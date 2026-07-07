"""Synthetic CRM sample-data seeding (#14).

Deterministic, client-agnostic generators (:mod:`generators`) plus a
:class:`~dataverse.seed.seeder.CrmSeeder` that upserts them via the Dataverse
client — idempotent by alternate key, with a controlled set of updates to
produce audit history. Live entrypoint: ``scripts/dataverse/seed_crm.py``.
"""

from dataverse.seed.generators import SeedData, SeedVolume, generate
from dataverse.seed.seeder import CrmSeeder, SeedSummary

__all__ = ["generate", "SeedData", "SeedVolume", "CrmSeeder", "SeedSummary"]
