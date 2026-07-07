# Generic CRM — schema notes

Companion to the [ERD](../diagrams/crm-erd.md) and [ADR-0005](../decisions/ADR-0005-crm-schema.md).
The CRM domain is modelled on **native Dataverse standard tables**; only AI
Request / AI Response are custom (`racy_`). This note pins the keys,
relationships, cascade behaviour, and the AI↔CRM link so #6 can create/configure
tables without further design.

## Entities & keys

> **Environment note (ADR-0005 Option B):** `racy-dev` is a plain Dataverse
> environment without the Dynamics 365 Sales/Customer Service apps, so `lead`,
> `opportunity`, `product`, and `incident` (Case) **don't exist as standard
> tables**. They're modelled as custom `racy_` tables (flat, reference-by-code).
> The rest are native standard tables.

| Entity | Table | Kind | Alternate key (upsert) |
|---|---|---|---|
| Account | `account` | standard | `accountnumber` *(added)* |
| Contact | `contact` | standard | `emailaddress1` *(added)* |
| Knowledge Article | `knowledgearticle` | standard | `articlepublicnumber` *(added)* |
| Activity | `activitypointer` | standard | — *(system-generated)* |
| Document | `annotation` | standard | — *(system-generated)* |
| Audit Event | `audit` | standard | — *(read-only platform log)* |
| Lead | `racy_lead` | custom | `racy_leadcode` |
| Opportunity | `racy_opportunity` | custom | `racy_opportunitycode` |
| Case | `racy_case` | custom | `racy_casecode` |
| Product | `racy_product` | custom | `racy_productnumber` |
| AI Request | `racy_airequest` | custom | `racy_requestcode` |
| AI Response | `racy_airesponse` | custom | `racy_requestcode` |

**Alternate keys** let the pipeline upsert by a *business-natural* identifier
(the pattern the `racy_` F1 tables already use). On the standard tables the key
is **added** (via `create_racy_schema.py --only crm`) on an existing column; on
the custom tables it's native. Activity, Document, and Audit Event are
system-created / not upserted, so they need none.

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
records (activities/documents/line items belong to their parent).

**Implementation (ADR-0005 Option B):** the table above is the *logical* design.
Because Lead/Opportunity/Case/Product are custom **flat** `racy_` tables, their
relationships are physically carried as **reference-code columns**
(`racy_opportunity.racy_accountnumber` → `account.accountnumber`,
`racy_case.racy_contactcode` → a contact code, `racy_opportunity.racy_leadcode`
→ `racy_lead`, etc.) rather than native lookups. Opportunity↔Product and
Case↔Knowledge Article (N:N) are likewise deferred. Native lookups, cascade
behaviours, and N:N are **model-driven-app enrichment (#11/#12)** — the ERD
relationships remain the target for that work.

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

- **#6** — `create_racy_schema.py --only crm` adds the alternate keys to the
  standard tables (account/contact/knowledgearticle) and creates the four custom
  `racy_` CRM tables; then a maker-portal/`pac` pass packages everything into an
  unmanaged solution exported to `dataverse/solutions/` (with #233).
- **#14** — seed sample Accounts/Contacts + `racy_lead`/`racy_opportunity`/
  `racy_case`/`racy_product` via upsert-by-alternate-key.
- **#13** — security roles build on standard-table privileges + the custom-table
  privileges (and the least-privilege agent-write role, #294).
