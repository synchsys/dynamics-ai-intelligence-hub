# Dataverse solutions

Source-controlled home for the **unmanaged solution** that packages the racy_
schema (#6 / #233). The exported solution `.zip` and its unpacked source live
here so schema changes are reviewable in PRs.

## Convention

- **Publisher:** `Racy` — customization prefix **`racy`** (option-value prefix
  `72000`). Created by `scripts/dataverse/create_racy_schema.py`.
- **Solution:** `RacyCRM` (unmanaged), containing:
  - the CRM alternate keys added to the standard tables (`account`, `contact`,
    `knowledgearticle`) — ADR-0005;
  - the custom CRM tables (`racy_lead`, `racy_opportunity`, `racy_case`,
    `racy_product`) and AI-logging tables (`racy_airequest`, `racy_airesponse`);
  - the F1 (`racy_session`, `racy_driver`, …) and Paddock (`racy_league`, …)
    tables, as the single dev solution.
- **Layout:**
  - `RacyCRM.zip` — the exported unmanaged solution (do not hand-edit).
  - `RacyCRM/` — `pac solution unpack` output (source-friendly; diff this in PRs).

## Provision the schema (metadata)

Tables, columns, and alternate keys are created by the provisioning script
(reused across environments; idempotent):

```bash
set -a && source .env && set +a
python scripts/dataverse/create_racy_schema.py --only all            # dry run
python scripts/dataverse/create_racy_schema.py --only all --apply    # create
```

`--only crm` provisions just the CRM slice (standard-table alt keys + the four
custom CRM tables).

## Package & export the solution (ALM, #6 / #233)

The solution container + component selection is a maker-portal / `pac` step:

```bash
pac auth create --url https://racy-dev.crm11.dynamics.com
# In the maker portal: create the RacyCRM unmanaged solution, add the tables above
# (they already exist from the script), Publish all customizations. Then:
pac solution export --name RacyCRM --path dataverse/solutions/RacyCRM.zip --managed false
pac solution unpack --zipfile dataverse/solutions/RacyCRM.zip --folder dataverse/solutions/RacyCRM
```

Commit both `RacyCRM.zip` and the unpacked `RacyCRM/` folder. Re-export + re-unpack
on schema changes so the diff is visible in review.

## Why script + solution (not one or the other)

The **script** provisions metadata repeatably and hermetically (no click-ops for
tables/columns/keys); the **solution** is the ALM boundary Dataverse uses to
move customizations between environments and the deliverable #6/#233 asks for.
They compose: script creates, solution packages.
