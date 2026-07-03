"""Authenticated Dataverse Web API client.

Wraps the Epic 2 :class:`~api.client.RestClient` (inheriting its
retry/backoff/logging) and injects a bearer token per request via
:class:`~dataverse.auth.TokenProvider`. Exposes typed CRUD, upsert-by-alternate
-key and ``$batch`` bulk-write methods over the generic CRM entities.

This is the single governed persistence layer imported by OpenF1 (4.4), FastF1
(5.5) and AI request/response logging (8.x).
"""

import json
import re
import time
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any

from azure.core.credentials import TokenCredential

from api.client import RestClient
from api.exceptions import ApiStatusError
from dataverse.auth import TokenProvider
from dataverse.config import DataverseConfig
from dataverse.exceptions import (
    DataverseBatchError,
    DataverseError,
    DataverseNotFoundError,
)
from shared.logging import get_logger

_ENTITY_ID_RE = re.compile(r"\(([0-9a-fA-F-]{36})\)")
_BATCH_ERROR_RE = re.compile(r"HTTP/1\.1 (4\d\d|5\d\d)")


class DataverseClient:
    """Typed client for the Dataverse Web API."""

    def __init__(
        self,
        config: DataverseConfig,
        *,
        credential: TokenCredential | None = None,
        rest: RestClient | None = None,
        timeout: float = 30.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._log = get_logger("dataverse.client")
        self._tokens = TokenProvider(config, credential=credential)
        self._rest = rest or RestClient(config.api_base, timeout=timeout, sleep=sleep)

    # -- headers ------------------------------------------------------------

    def _headers(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._tokens.token()}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }
        if extra:
            headers.update(extra)
        return headers

    # -- CRUD ---------------------------------------------------------------

    def create(self, entity_set: str, data: Mapping[str, Any]) -> str:
        """Create a record; return its GUID (parsed from the ``OData-EntityId`` header)."""
        with self._translate(entity_set):
            resp = self._rest.post(f"/{entity_set}", json=dict(data), headers=self._headers())
        entity_id = resp.headers.get("OData-EntityId", "")
        match = _ENTITY_ID_RE.search(entity_id)
        if not match:
            raise DataverseError(f"create({entity_set}) returned no entity id")
        return match.group(1)

    def retrieve(
        self, entity_set: str, record_id: str, *, select: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Retrieve a single record by id."""
        params = {"$select": ",".join(select)} if select else None
        with self._translate(entity_set, record_id):
            resp = self._rest.get(
                f"/{entity_set}({record_id})", params=params, headers=self._headers()
            )
        return dict(resp.json())

    def retrieve_multiple(
        self,
        entity_set: str,
        *,
        filter: str | None = None,
        select: Sequence[str] | None = None,
        top: int | None = None,
        max_pages: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieve records, transparently following ``@odata.nextLink`` pagination."""
        params: dict[str, str] = {}
        if filter:
            params["$filter"] = filter
        if select:
            params["$select"] = ",".join(select)
        if top:
            params["$top"] = str(top)

        results: list[dict[str, Any]] = []
        path: str | None = f"/{entity_set}"
        pages = 0
        with self._translate(entity_set):
            while path and pages < max_pages:
                # params only apply to the first request; nextLink carries its own query
                resp = self._rest.get(
                    path, params=params if pages == 0 else None, headers=self._headers()
                )
                payload = resp.json()
                results.extend(payload.get("value", []))
                path = payload.get("@odata.nextLink")
                pages += 1
        return results

    def update(self, entity_set: str, record_id: str, data: Mapping[str, Any]) -> None:
        """Update (PATCH) an existing record."""
        with self._translate(entity_set, record_id):
            self._rest.request(
                "PATCH", f"/{entity_set}({record_id})", json=dict(data), headers=self._headers()
            )

    def delete(self, entity_set: str, record_id: str) -> None:
        """Delete a record."""
        with self._translate(entity_set, record_id):
            self._rest.request("DELETE", f"/{entity_set}({record_id})", headers=self._headers())

    def upsert(self, entity_set: str, alternate_key: str, data: Mapping[str, Any]) -> None:
        """Upsert by alternate key, e.g. ``alternate_key="ref_code='ABC'"``.

        Dataverse PATCH to an alternate-key URL creates the record if absent and
        updates it otherwise.
        """
        with self._translate(entity_set):
            self._rest.request(
                "PATCH", f"/{entity_set}({alternate_key})", json=dict(data), headers=self._headers()
            )

    # -- batch --------------------------------------------------------------

    def batch_create(self, entity_set: str, records: Sequence[Mapping[str, Any]]) -> None:
        """Create many records in a single ``$batch`` changeset (bulk write).

        Raises :class:`DataverseBatchError` if any inner operation reports a
        4xx/5xx status.
        """
        if not records:
            return
        batch_id = f"batch_{uuid.uuid4().hex}"
        changeset_id = f"changeset_{uuid.uuid4().hex}"
        body = self._build_batch(entity_set, records, batch_id, changeset_id)
        headers = self._headers({"Content-Type": f"multipart/mixed; boundary={batch_id}"})
        with self._translate(entity_set):
            resp = self._rest.post("/$batch", content=body, headers=headers)
        if _BATCH_ERROR_RE.search(resp.text):
            raise DataverseBatchError(f"$batch to {entity_set} reported failed operation(s)")

    def _build_batch(
        self,
        entity_set: str,
        records: Sequence[Mapping[str, Any]],
        batch_id: str,
        changeset_id: str,
    ) -> str:
        lines = [f"--{batch_id}", f"Content-Type: multipart/mixed; boundary={changeset_id}", ""]
        for index, record in enumerate(records, start=1):
            lines += [
                f"--{changeset_id}",
                "Content-Type: application/http",
                "Content-Transfer-Encoding: binary",
                f"Content-ID: {index}",
                "",
                f"POST {self._config.api_base}/{entity_set} HTTP/1.1",
                "Content-Type: application/json",
                "",
                json.dumps(dict(record)),
                "",
            ]
        lines += [f"--{changeset_id}--", f"--{batch_id}--", ""]
        return "\r\n".join(lines)

    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None:
        """Upsert several records by alternate key in one **atomic** ``$batch`` changeset.

        Each operation is ``(entity_set, alternate_key, data)``. A changeset is
        all-or-nothing, so this is the mechanism for multi-record transactions
        that must not partially apply — e.g. the confirm-and-lock debit (#228).
        """
        if not operations:
            return
        batch_id = f"batch_{uuid.uuid4().hex}"
        changeset_id = f"changeset_{uuid.uuid4().hex}"
        lines = [f"--{batch_id}", f"Content-Type: multipart/mixed; boundary={changeset_id}", ""]
        for index, (entity_set, alt_key, data) in enumerate(operations, start=1):
            lines += [
                f"--{changeset_id}",
                "Content-Type: application/http",
                "Content-Transfer-Encoding: binary",
                f"Content-ID: {index}",
                "",
                f"PATCH {self._config.api_base}/{entity_set}({alt_key}) HTTP/1.1",
                "Content-Type: application/json",
                "",
                json.dumps(dict(data)),
                "",
            ]
        lines += [f"--{changeset_id}--", f"--{batch_id}--", ""]
        headers = self._headers({"Content-Type": f"multipart/mixed; boundary={batch_id}"})
        with self._translate("$batch"):
            resp = self._rest.post("/$batch", content="\r\n".join(lines), headers=headers)
        if _BATCH_ERROR_RE.search(resp.text):
            raise DataverseBatchError("$batch upsert reported failed operation(s)")

    # -- lifecycle + error translation -------------------------------------

    def close(self) -> None:
        self._rest.close()

    def __enter__(self) -> "DataverseClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def _translate(self, entity_set: str, record_id: str = "") -> Iterator[None]:
        """Map :class:`ApiStatusError` from the REST layer to the Dataverse error model."""
        try:
            yield
        except ApiStatusError as exc:
            target = f"{entity_set}({record_id})" if record_id else entity_set
            if exc.status_code == 404:
                raise DataverseNotFoundError(f"{target} not found") from exc
            raise DataverseError(f"Dataverse {target} error {exc.status_code}: {exc.body}") from exc
