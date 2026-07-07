"""Deterministic, fully synthetic CRM record generators (#14).

No external data library and no real people/companies/domains: names come from
curated word lists, emails use the reserved ``.invalid`` TLD. Everything is
driven by a seeded :class:`random.Random`, so the same ``seed`` always yields the
same data — which makes both the tests deterministic and the seed run idempotent
(stable alternate-key codes → upsert, never duplicate).

Records are plain dataclasses carrying their **alternate-key value** (the code)
and the cross-entity **references** (by code); mapping to Dataverse payloads is
the seeder's job, keeping these generators I/O-free and unit-testable.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

# Curated, obviously-synthetic vocab (client-agnostic).
_ADJ = ["Apex", "Nimbus", "Vertex", "Quanta", "Lumina", "Cobalt", "Zephyr", "Orbit", "Halcyon"]
_NOUN = ["Systems", "Dynamics", "Labs", "Industries", "Networks", "Analytics", "Robotics", "Group"]
_FIRST = [
    "Ada",
    "Bruno",
    "Cora",
    "Devon",
    "Elena",
    "Farid",
    "Gita",
    "Hugo",
    "Ines",
    "Jonas",
    "Kira",
    "Liam",
    "Mara",
    "Noor",
    "Otto",
    "Priya",
    "Quinn",
    "Rosa",
    "Sami",
    "Tara",
]
_LAST = [
    "Ackerman",
    "Boone",
    "Castellano",
    "Dupont",
    "Everett",
    "Falk",
    "Gough",
    "Ibarra",
    "Jansson",
    "Kowalski",
    "Lindqvist",
    "Moreau",
    "Novak",
    "Oduya",
    "Petrov",
    "Renner",
]
_CITY = ["Cork", "Dublin", "Galway", "Limerick", "Sligo", "Ennis", "Tralee", "Kilkenny"]
_LEAD_STATUS = ["New", "Contacted", "Qualified", "Disqualified"]
_OPP_STATUS = ["Open", "Won", "Lost"]
_CASE_PRIORITY = ["Low", "Normal", "High"]
_CASE_STATUS = ["Active", "On Hold", "Resolved"]
_SUBJECTS = [
    "Renewal enquiry",
    "Onboarding help",
    "Pricing question",
    "Integration support",
    "Outage report",
    "Feature request",
    "Contract review",
    "Training session",
]


@dataclass
class SeedVolume:
    """How many of each entity to generate (defaults total ~230 records)."""

    accounts: int = 20
    contacts: int = 60
    leads: int = 40
    opportunities: int = 40
    cases: int = 30
    activities: int = 40

    @classmethod
    def scaled(cls, multiplier: float) -> SeedVolume:
        base = cls()
        return cls(
            accounts=max(1, round(base.accounts * multiplier)),
            contacts=max(1, round(base.contacts * multiplier)),
            leads=max(1, round(base.leads * multiplier)),
            opportunities=max(1, round(base.opportunities * multiplier)),
            cases=max(1, round(base.cases * multiplier)),
            activities=max(1, round(base.activities * multiplier)),
        )

    @property
    def total(self) -> int:
        return (
            self.accounts
            + self.contacts
            + self.leads
            + self.opportunities
            + self.cases
            + self.activities
        )


@dataclass(frozen=True)
class Account:
    number: str  # alt key -> accountnumber
    name: str
    city: str
    phone: str


@dataclass(frozen=True)
class Contact:
    email: str  # alt key -> emailaddress1
    first: str
    last: str
    city: str
    account_number: str  # ref -> account


@dataclass(frozen=True)
class Lead:
    code: str  # alt key -> racy_leadcode
    subject: str
    status: str
    account_number: str
    contact_email: str


@dataclass(frozen=True)
class Opportunity:
    code: str
    account_number: str
    contact_email: str
    lead_code: str
    estimated_value: float
    status: str


@dataclass(frozen=True)
class Case:
    code: str
    title: str
    account_number: str
    contact_email: str
    priority: str
    status: str


@dataclass(frozen=True)
class Activity:
    code: str  # alt key -> racy_taskcode
    subject: str
    regarding_type: str  # "account" | "contact"
    regarding_ref: str  # accountnumber or contact email
    status: str


@dataclass
class SeedData:
    accounts: list[Account] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    leads: list[Lead] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    cases: list[Case] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)


def generate(volume: SeedVolume | None = None, *, seed: int = 0) -> SeedData:
    """Generate a fully-linked, deterministic synthetic CRM dataset."""
    vol = volume or SeedVolume()
    rng = random.Random(seed)

    accounts = [
        Account(
            number=f"ACC-{i:04d}",
            name=f"{rng.choice(_ADJ)} {rng.choice(_NOUN)} {i:04d}",
            city=rng.choice(_CITY),
            phone=f"+353-1-{rng.randint(1000000, 9999999)}",
        )
        for i in range(1, vol.accounts + 1)
    ]

    contacts = []
    for i in range(1, vol.contacts + 1):
        first, last = rng.choice(_FIRST), rng.choice(_LAST)
        contacts.append(
            Contact(
                email=f"{first.lower()}.{last.lower()}.{i}@example.invalid",
                first=first,
                last=last,
                city=rng.choice(_CITY),
                account_number=accounts[(i - 1) % len(accounts)].number,
            )
        )

    def _acc(i: int) -> str:
        return accounts[i % len(accounts)].number

    def _con(i: int) -> str:
        return contacts[i % len(contacts)].email

    leads = [
        Lead(
            code=f"LEAD-{i:04d}",
            subject=rng.choice(_SUBJECTS),
            status=rng.choice(_LEAD_STATUS),
            account_number=_acc(i),
            contact_email=_con(i),
        )
        for i in range(1, vol.leads + 1)
    ]

    opportunities = [
        Opportunity(
            code=f"OPP-{i:04d}",
            account_number=_acc(i),
            contact_email=_con(i),
            lead_code=leads[(i - 1) % len(leads)].code if leads else "",
            estimated_value=round(rng.uniform(5_000, 250_000), 2),
            status=rng.choice(_OPP_STATUS),
        )
        for i in range(1, vol.opportunities + 1)
    ]

    cases = [
        Case(
            code=f"CASE-{i:04d}",
            title=rng.choice(_SUBJECTS),
            account_number=_acc(i),
            contact_email=_con(i),
            priority=rng.choice(_CASE_PRIORITY),
            status=rng.choice(_CASE_STATUS),
        )
        for i in range(1, vol.cases + 1)
    ]

    activities = [
        Activity(
            code=f"TASK-{i:04d}",
            subject=rng.choice(_SUBJECTS),
            regarding_type="account" if i % 2 else "contact",
            regarding_ref=_acc(i) if i % 2 else _con(i),
            status=rng.choice(["Open", "Completed"]),
        )
        for i in range(1, vol.activities + 1)
    ]

    return SeedData(accounts, contacts, leads, opportunities, cases, activities)
