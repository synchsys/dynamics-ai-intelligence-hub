"""Seed synthetic, client-agnostic CRM sample data into Dataverse (#14).

Idempotent (upsert by alternate key) and parameterised by volume; a controlled
set of updates generates audit history. Requires the CRM tables + alt keys from
`create_racy_schema.py --only crm --apply`.

Run:  set -a && source .env && set +a
      python scripts/dataverse/seed_crm.py            # dry run — counts only
      python scripts/dataverse/seed_crm.py --apply    # write to Dataverse
"""

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def main() -> int:
    p = argparse.ArgumentParser(description="Seed synthetic CRM data into Dataverse (#14).")
    p.add_argument("--apply", action="store_true", help="write to Dataverse (default: dry run)")
    p.add_argument("--seed", type=int, default=0, help="RNG seed (deterministic; default 0)")
    p.add_argument("--scale", type=float, default=1.0, help="volume multiplier (1.0 ~230 records)")
    p.add_argument("--update-count", type=int, default=60, help="records to update for audit")
    args = p.parse_args()

    from dataverse import DataverseClient, DataverseConfig
    from dataverse.seed import CrmSeeder, SeedVolume, generate

    vol = SeedVolume.scaled(args.scale)
    if not args.apply:
        d = generate(vol, seed=args.seed)
        print(
            f"[dry run] would seed {vol.total} records: accounts={len(d.accounts)}, "
            f"contacts={len(d.contacts)}, leads={len(d.leads)}, opportunities={len(d.opportunities)}, "
            f"cases={len(d.cases)}, activities={len(d.activities)} + up to {args.update_count} "
            f"updates for audit history.\nRe-run with --apply to write to Dataverse."
        )
        return 0

    seeder = CrmSeeder(DataverseClient(DataverseConfig.from_env()))
    summary = seeder.seed(vol, seed=args.seed, update_count=args.update_count)
    print(f"seeded {summary.total_records} records: {summary.counts}")
    print(f"applied {summary.updates} updates for audit history")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
