# Generic CRM — schema notes

Companion to the [ERD](../diagrams/crm-erd.md) and [ADR-0005](../decisions/ADR-0005-crm-schema.md).
The CRM domain is modelled on **native Dataverse standard tables**; only AI
Request / AI Response are custom (`racy_`). This note pins the keys,
relationships, cascade behaviour, and the AI↔CRM link so #6 can create/configure
tables without further design.

## Entities & keys

| Entity | Table | Primary name | Alternate key (upsert) |
|---|---|---|---|
| Account | `account` | `name` | `accountnumber` |
| Contact | `contact` | `fullname` | `emailaddress1` |
| Lead | `lead` | `subject` | `racy_leadcode` *(added)* |
| Opportunity | `opportunity` | `name` | `racy_opportunitycode` *(added)* |
| Case | `incident` | `title` | `ticketnumber` *(system)* |
| Activity | `activitypointer` | `subject` | — *(system-generated)* |
| Product | `product` | `name` | `productnumber` |
| Knowledge Article | `knowledgearticle` | `title` | `articlepublicnumber` |
| Document | `annotation` | `subject` | — *(system-generated)* |
| Audit Event | `audit` | — | — *(read-only platform log)* |
| AI Request | `racy_airequest` | `racy_requestcode` | `racy_requestcode` |
| AI Response | `racy_airesponse` | `racy_requestcode` | `racy_requestcode` |

**Alternate keys** exist because standard tables key on a GUID `PK`, but the
ingestion/seeding pipeline upserts by a *business-natural* identifier (see the
upsert-by-alt-key pattern already used for the `racy_` F1 tables). Two —
`racy_leadcode`, `racy_opportunitycode` — must be **added** to the standard
tables (they ship with no business-natural unique key). Activity, Document, and
Audit Event are created by the system / not upserted, so they need none.

## Relationships & cascade behaviour

| From → To | Type | Lookup | Cascade (delete) |
|---|---|---|---|
| Account → Contact | 1:N | `contact.parentcustomerid` | Remove Link (reparent, don't cascade-delete) |
| Account → Opportunity | 1:N | `opportunity.parentaccountid` | Remove Link |
| Account → Case | 1:N | `incident.customerid` | Cascade *(close/delete cases with account)* |
| Contact → Opportunity | 1:N | `opportunity.parentcontactid` | Remove Link |
| Contact → Case | 1:N | `incident.primarycontactid` | Remove Link |
| Lead → Opportunity | 1:0..1 | `opportunity.originatingleadid` | Remove Link *(set on qualify)* |
| Opportunity ↔ Product | N:N | opportunity line items (`opportunityproduct`) | line items deleted with opportunity |
| Case ↔ Knowledge Article | N:N | article associations | Remove Link |
| * → Activity | 1:N | `activitypointer.regardingobjectid` | Cascade *(activities deleted with parent)* |
| * → Document | 1:N | `annotation.objectid` | Cascade |
| * → Audit Event | 1:N | `audit.objectid` | n/a *(immutable log)* |
| SystemUser → AI Request | 1:N | `racy_airequest.racy_userid` | Restrict |
| * → AI Request | 1:N | `racy_airequest.racy_regardingid` | Remove Link |
| AI Request → AI Response | 1:1 | paired by `racy_requestcode` | Cascade |

Cascade choices favour **Remove Link** for reference relationships (deleting an
account shouldn't silently delete its contacts) and **Cascade** for owned child
records (activities/documents/line items belong to their parent). These are
Dataverse relationship-behaviour defaults to confirm at build time (#6).

## Polymorphic ("regarding") lookups

Four entities attach to *many* parent types via a single polymorphic lookup —
the ERD draws representative edges only:

- **Activity** `regardingobjectid` → Account, Contact, Lead, Opportunity, Case
  (any activity-enabled table).
- **Document** (`annotation`) `objectid` → the record the note/attachment hangs
  off (most tables).
- **Audit Event** `objectid` → the audited record; `userid` → the acting
  SystemUser.
- **AI Request** `racy_regardingid` → the CRM record the model acted on.

In Dataverse these are `PartyList`/`Customer`/`Regarding` polymorphic lookups
(or a `Customer` lookup limited to Account+Contact, as on `incident.customerid`).

## AI Request / AI Response ↔ CRM

The governance link (#69, [ai-logging.md](ai-logging.md)):

- **AI Request** records *who asked, what, and against which record*:
  `racy_purpose`, `racy_model`, `racy_prompt`, `racy_userid` (acting user), and
  `racy_regardingid` (the CRM record acted on).
- **AI Response** records *what came back*: `racy_rawoutput`, `racy_decision`,
  `racy_ok`, `racy_tokens`, `racy_latencyms`.
- The two are **paired 1:1 by `racy_requestcode`** — the alternate key on both —
  so a request and its response upsert independently yet join cleanly.

**Implementation note:** the current `racy_ai*` tables (created by
`create_racy_schema.py`) are **flat** — `racy_userid` is a string and
`racy_regardingid` is not yet present. Modelling them here as lookups is the
*design target*; native lookups + the regarding link are app-enrichment for the
model-driven app (#11/#12) / an Epic 11 hardening step, not required for the
logger to read/write. This mirrors the flat-table approach ADR-0009 took for the
Paddock tables.

## What this drives

- **#6** — create the two `racy_leadcode`/`racy_opportunitycode` alternate keys
  and confirm relationship behaviours; the `racy_ai*` tables already exist.
- **#14** — seed sample Accounts/Contacts/Leads/Opportunities/Cases via
  upsert-by-alternate-key.
- **#13** — security roles build on standard-table privileges (and the
  least-privilege agent-write role, #294).
