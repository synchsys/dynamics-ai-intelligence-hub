"""Tests for synthetic CRM seeding (#14) — deterministic generators + seeder."""

from collections.abc import Mapping, Sequence
from typing import Any

from dataverse.seed import CrmSeeder, SeedVolume, generate
from dataverse.seed.seeder import build_ops


class FakeDV:
    """Records batch_upsert calls; satisfies SupportsBatchUpsert."""

    def __init__(self) -> None:
        self.batches: list[list[tuple[str, str, Mapping[str, Any]]]] = []
        self.ops: list[tuple[str, str, Mapping[str, Any]]] = []

    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None:
        batch = list(operations)
        self.batches.append(batch)
        self.ops.extend(batch)


# --- generators -------------------------------------------------------------


def test_generate_is_deterministic() -> None:
    assert generate(seed=1) == generate(seed=1)
    assert generate(seed=1) != generate(seed=2)


def test_default_volume_counts() -> None:
    data, vol = generate(seed=0), SeedVolume()
    assert len(data.accounts) == vol.accounts
    assert len(data.contacts) == vol.contacts
    assert len(data.activities) == vol.activities


def test_references_are_valid() -> None:
    data = generate(seed=3)
    account_numbers = {a.number for a in data.accounts}
    emails = {c.email for c in data.contacts}
    lead_codes = {lead.code for lead in data.leads}
    assert all(c.account_number in account_numbers for c in data.contacts)
    assert all(lead.account_number in account_numbers for lead in data.leads)
    assert all(o.contact_email in emails for o in data.opportunities)
    assert all(o.lead_code in lead_codes for o in data.opportunities)


def test_data_is_client_agnostic() -> None:
    data = generate(seed=0)
    assert all(c.email.endswith("@example.invalid") for c in data.contacts)


def test_volume_scaled() -> None:
    assert SeedVolume.scaled(0.5).accounts == 10
    assert SeedVolume.scaled(2).total == SeedVolume().total * 2
    assert SeedVolume.scaled(0.001).accounts == 1  # floor of 1


def test_opportunity_leadcode_blank_when_no_leads() -> None:
    data = generate(SeedVolume(leads=0, opportunities=5), seed=0)
    assert data.opportunities and all(o.lead_code == "" for o in data.opportunities)


# --- build_ops --------------------------------------------------------------


def test_build_ops_entity_sets_and_links() -> None:
    ops = build_ops(generate(seed=0))
    assert set(ops) == {"accounts", "contacts", "leads", "opportunities", "cases", "activities"}
    # contact links to its account via the lookup bind
    assert any("parentcustomerid_account@odata.bind" in data for _, _, data in ops["contacts"])
    # activities bind to both account- and contact-regarding (data alternates)
    binds = {k for _, _, data in ops["activities"] for k in data if k.endswith("@odata.bind")}
    assert binds == {
        "regardingobjectid_account_task@odata.bind",
        "regardingobjectid_contact_task@odata.bind",
    }
    assert ops["accounts"][0][0] == "accounts" and ops["leads"][0][0] == "racy_leads"


# --- seeder -----------------------------------------------------------------


def test_seed_populates_all_entities_over_threshold() -> None:
    dv = FakeDV()
    summary = CrmSeeder(dv).seed(seed=0)
    assert set(summary.counts) == {
        "accounts",
        "contacts",
        "leads",
        "opportunities",
        "cases",
        "activities",
    }
    assert summary.total_records >= 200  # AC: >= 200 records
    assert summary.updates == 60  # AC: >= 50 audit-generating updates


def test_seed_is_idempotent() -> None:
    a, b = FakeDV(), FakeDV()
    CrmSeeder(a).seed(seed=7)
    CrmSeeder(b).seed(seed=7)
    assert a.ops == b.ops  # same seed -> identical upserts, no duplicates


def test_updates_can_be_skipped() -> None:
    dv = FakeDV()
    summary = CrmSeeder(dv).seed(seed=0, apply_updates=False)
    assert summary.updates == 0


def test_update_count_exercises_all_entity_spillover() -> None:
    # default volume: 20 accounts + 30 cases + 40 leads = 90 updatable.
    # 15 breaks in accounts, 30 in cases, 60 in leads, 500 caps at all 90.
    for update_count, expected in [(15, 15), (30, 30), (60, 60), (500, 90)]:
        dv = FakeDV()
        summary = CrmSeeder(dv).seed(seed=0, update_count=update_count)
        assert summary.updates == expected


def test_upsert_is_chunked_by_batch_size() -> None:
    dv = FakeDV()
    CrmSeeder(dv, batch_size=5).seed(
        SeedVolume(accounts=12, contacts=0, leads=0, opportunities=0, cases=0, activities=0),
        seed=0,
        apply_updates=False,
    )
    account_batches = [b for b in dv.batches if b and b[0][0] == "accounts"]
    assert [len(b) for b in account_batches] == [5, 5, 2]  # 12 rows -> 5+5+2
