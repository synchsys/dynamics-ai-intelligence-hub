"""Seed synthetic CRM data into Dataverse, idempotently (#14).

Maps the generated records to Dataverse upsert operations and writes them via the
client's atomic ``$batch`` (chunked). Idempotent — every record has a stable
alternate-key code, so re-running upserts the same rows rather than duplicating.
A controlled set of field updates is re-upserted afterwards so **auditing**
produces a usable history. Logic is client-injected and unit-tested; the live
entrypoint is ``scripts/dataverse/seed_crm.py``.

Links: contacts → account via the ``parentcustomerid`` lookup; activities (task)
→ their regarding record via the polymorphic lookup; the custom flat tables
(lead/opportunity/case) carry references as code columns (ADR-0005).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from dataverse.seed.generators import SeedData, SeedVolume, generate
from shared.logging import get_logger

_logger = get_logger("dataverse.seed")

Op = tuple[str, str, dict[str, Any]]


class SupportsBatchUpsert(Protocol):
    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None: ...


@dataclass
class SeedSummary:
    counts: dict[str, int] = field(default_factory=dict)
    updates: int = 0

    @property
    def total_records(self) -> int:
        return sum(self.counts.values())


def _account_ref(number: str) -> str:
    return f"/accounts(accountnumber='{number}')"


def _contact_ref(email: str) -> str:
    return f"/contacts(emailaddress1='{email}')"


def _regarding_bind(activity_type: str, ref: str) -> dict[str, str]:
    """The polymorphic-lookup @odata.bind for a task's regarding record."""
    if activity_type == "account":
        return {"regardingobjectid_account_task@odata.bind": _account_ref(ref)}
    return {"regardingobjectid_contact_task@odata.bind": _contact_ref(ref)}


def build_ops(data: SeedData) -> dict[str, list[Op]]:
    """Map generated records to per-entity Dataverse upsert operations."""
    return {
        "accounts": [
            (
                "accounts",
                f"accountnumber='{a.number}'",
                {
                    "name": a.name,
                    "accountnumber": a.number,
                    "address1_city": a.city,
                    "telephone1": a.phone,
                },
            )
            for a in data.accounts
        ],
        "contacts": [
            (
                "contacts",
                f"emailaddress1='{c.email}'",
                {
                    "firstname": c.first,
                    "lastname": c.last,
                    "emailaddress1": c.email,
                    "address1_city": c.city,
                    "parentcustomerid_account@odata.bind": _account_ref(c.account_number),
                },
            )
            for c in data.contacts
        ],
        "leads": [
            (
                "racy_leads",
                f"racy_leadcode='{lead.code}'",
                {
                    "racy_name": lead.code,
                    "racy_leadcode": lead.code,
                    "racy_subject": lead.subject,
                    "racy_statuscode": lead.status,
                    "racy_accountnumber": lead.account_number,
                    "racy_contactcode": lead.contact_email,
                },
            )
            for lead in data.leads
        ],
        "opportunities": [
            (
                "racy_opportunities",
                f"racy_opportunitycode='{o.code}'",
                {
                    "racy_name": o.code,
                    "racy_opportunitycode": o.code,
                    "racy_accountnumber": o.account_number,
                    "racy_contactcode": o.contact_email,
                    "racy_leadcode": o.lead_code,
                    "racy_estimatedvalue": o.estimated_value,
                    "racy_statuscode": o.status,
                },
            )
            for o in data.opportunities
        ],
        "cases": [
            (
                "racy_cases",
                f"racy_casecode='{c.code}'",
                {
                    "racy_name": c.code,
                    "racy_casecode": c.code,
                    "racy_title": c.title,
                    "racy_accountnumber": c.account_number,
                    "racy_contactcode": c.contact_email,
                    "racy_prioritycode": c.priority,
                    "racy_statuscode": c.status,
                },
            )
            for c in data.cases
        ],
        "activities": [
            (
                "tasks",
                f"racy_taskcode='{t.code}'",
                {
                    "subject": t.subject,
                    "racy_taskcode": t.code,
                    **_regarding_bind(t.regarding_type, t.regarding_ref),
                },
            )
            for t in data.activities
        ],
    }


class CrmSeeder:
    """Idempotently seeds synthetic CRM data via the Dataverse ``$batch`` upsert."""

    def __init__(self, dataverse: SupportsBatchUpsert, *, batch_size: int = 100) -> None:
        self._dv = dataverse
        self._batch_size = batch_size

    def _upsert(self, ops: Sequence[Op]) -> None:
        for i in range(0, len(ops), self._batch_size):
            self._dv.batch_upsert(ops[i : i + self._batch_size])

    def seed(
        self,
        volume: SeedVolume | None = None,
        *,
        seed: int = 0,
        update_count: int = 60,
        apply_updates: bool = True,
    ) -> SeedSummary:
        """Generate + upsert the dataset, then re-upsert a subset for audit history."""
        data = generate(volume, seed=seed)
        summary = SeedSummary()
        for name, ops in build_ops(data).items():
            self._upsert(ops)
            summary.counts[name] = len(ops)
            _logger.info("seed %s: upserted %d", name, len(ops))
        if apply_updates:
            summary.updates = self._apply_updates(data, update_count)
            _logger.info("seed updates: %d records re-upserted for audit history", summary.updates)
        return summary

    def _apply_updates(self, data: SeedData, n: int) -> int:
        """Re-upsert up to ``n`` records with one changed field each (audit history)."""
        ops: list[Op] = []
        for a in data.accounts:
            if len(ops) >= n:
                break
            ops.append(("accounts", f"accountnumber='{a.number}'", {"telephone1": f"{a.phone}-U"}))
        for c in data.cases:
            if len(ops) >= n:
                break
            ops.append(("racy_cases", f"racy_casecode='{c.code}'", {"racy_statuscode": "Resolved"}))
        for lead in data.leads:
            if len(ops) >= n:
                break
            ops.append(
                ("racy_leads", f"racy_leadcode='{lead.code}'", {"racy_statuscode": "Contacted"})
            )
        self._upsert(ops)
        return len(ops)
