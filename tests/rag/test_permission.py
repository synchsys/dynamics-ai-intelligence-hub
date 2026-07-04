"""Tests for permission-aware retrieval — role->tags, filters, two-user trimming."""

import re
from collections.abc import Sequence
from typing import Any

from rag import AccessPolicy, Retriever

POLICY = AccessPolicy()


# --- role -> allowed tags ---------------------------------------------------


def test_guest_gets_public_only() -> None:
    assert POLICY.allowed_tags(["guest"]) == {"public"}


def test_employee_gets_public_and_internal() -> None:
    assert POLICY.allowed_tags(["employee"]) == {"public", "internal"}


def test_manager_gets_all_levels() -> None:
    assert POLICY.allowed_tags(["manager"]) == {"public", "internal", "confidential"}


def test_highest_role_wins_across_multiple() -> None:
    assert POLICY.allowed_tags(["guest", "manager"]) == {"public", "internal", "confidential"}


def test_unknown_role_grants_nothing() -> None:
    assert POLICY.allowed_tags(["intruder"]) == set()
    assert POLICY.allowed_tags([]) == set()


def test_role_matching_is_case_insensitive() -> None:
    assert POLICY.allowed_tags(["  Manager "]) == {"public", "internal", "confidential"}


# --- filter construction ----------------------------------------------------


def test_filter_uses_search_in_with_sorted_tags() -> None:
    assert POLICY.filter_for(["employee"]) == "search.in(access_tag, 'internal,public', ',')"


def test_filter_denies_all_for_unknown_role() -> None:
    assert POLICY.filter_for(["intruder"]) == "access_tag eq '__no_access__'"


def test_custom_policy_mapping() -> None:
    policy = AccessPolicy(role_access={"vip": "confidential"})
    assert policy.allowed_tags(["vip"]) == {"public", "internal", "confidential"}
    assert policy.allowed_tags(["guest"]) == set()  # not in custom map


# --- two-user enforcement (filter-respecting fake index) --------------------

DOCS: list[dict[str, Any]] = [
    {"id": "1", "content": "public notice", "source": "s", "section": None, "access_tag": "public"},
    {
        "id": "2",
        "content": "internal memo",
        "source": "s",
        "section": None,
        "access_tag": "internal",
    },
    {
        "id": "3",
        "content": "secret plan",
        "source": "s",
        "section": None,
        "access_tag": "confidential",
    },
]


class FilterRespectingIndex:
    """A fake index that enforces the OData security filter, like the real service."""

    def hybrid_search(
        self,
        query_text: str,
        vector: Sequence[float],
        *,
        top: int = 5,
        access_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        allowed = self._allowed(access_filter)
        return [d for d in DOCS if d["access_tag"] in allowed][:top]

    @staticmethod
    def _allowed(filter_str: str | None) -> set[str]:
        if not filter_str:
            return {d["access_tag"] for d in DOCS}
        match = re.search(r"search\.in\(access_tag, '([^']*)', ','\)", filter_str)
        return set(match.group(1).split(",")) if match else set()


class StubEmbedder:
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]


def _retriever() -> Retriever:
    return Retriever(FilterRespectingIndex(), StubEmbedder())  # type: ignore[arg-type]


def test_guest_cannot_retrieve_internal_or_confidential() -> None:
    tags = {c.access_tag for c in _retriever().retrieve_for("q", ["guest"])}
    assert tags == {"public"}


def test_manager_retrieves_everything() -> None:
    tags = {c.access_tag for c in _retriever().retrieve_for("q", ["manager"])}
    assert tags == {"public", "internal", "confidential"}


def test_restricted_user_provably_cannot_see_what_authorised_can() -> None:
    guest_ids = {c.id for c in _retriever().retrieve_for("q", ["guest"])}
    manager_ids = {c.id for c in _retriever().retrieve_for("q", ["manager"])}
    confidential_id = "3"
    assert confidential_id in manager_ids
    assert confidential_id not in guest_ids  # the core security guarantee


def test_unknown_role_retrieves_nothing() -> None:
    assert _retriever().retrieve_for("q", ["intruder"]) == []
