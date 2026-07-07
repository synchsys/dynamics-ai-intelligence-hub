# ADR-0005: Generic CRM schema approach

## Status

Accepted

## Context

The solution needs a client-agnostic CRM domain (#8) — Account, Contact, Lead,
Opportunity, Case, Activity, Product, Knowledge Article, Document, Audit Event —
plus AI-specific logging (AI Request, AI Response). Dataverse **already ships**
most of these as first-party standard tables with built-in relationships, forms,
views, security, auditing, and business logic. The question is whether to model
the CRM on those standard tables or to build parallel custom `racy_` tables.

This matters because everything downstream — sample-data seeding (#14),
security roles (#13), the CRM assistant/RAG retrieval, the model-driven app
(#11/#12) — reads and writes these tables.

## Decision

**Model the CRM domain on native Dataverse standard tables.** Add custom
`racy_` tables *only* for concepts Dataverse has no first-party equivalent for —
here, **AI Request / AI Response** (prompt/response governance logging, #69).

| Domain entity | Dataverse table | Kind |
|---|---|---|
| Account | `account` | standard |
| Contact | `contact` | standard |
| Lead | `lead` | standard |
| Opportunity | `opportunity` | standard |
| Case | `incident` | standard |
| Activity | `activitypointer` (+ task/phonecall/email…) | standard |
| Product | `product` | standard |
| Knowledge Article | `knowledgearticle` | standard |
| Document | `annotation` (Note+attachment) / SharePoint | standard |
| Audit Event | `audit` | standard (platform) |
| AI Request | `racy_airequest` | **custom** |
| AI Response | `racy_airesponse` | **custom** |

The `racy_` prefix is reserved for what is genuinely custom: the AI-logging
tables here, and — outside this ADR's CRM scope — the F1 sample-data and Paddock
Club game tables.

## Consequences

- **Positive:** idiomatic Dynamics 365 — standard tables bring relationships,
  security roles, auditing, activities, and BPFs for free; reads as real-world
  architecture in the portfolio; the assistant already queries native tables
  (e.g. `accounts`). Less to build and maintain.
- **Upsert:** standard tables carry a GUID primary key; where the pipeline
  upserts (seeding, integration) it uses a **defined alternate key** on a
  natural business identifier (e.g. `account.accountnumber`,
  `contact.emailaddress1`, `incident.ticketnumber`). The AI tables use
  `racy_requestcode`.
- **AI ↔ CRM link:** `racy_airequest` carries the acting user and an optional
  reference to the CRM record it acted on; `racy_airesponse` pairs 1:1 to its
  request by `racy_requestcode`. Detail in `crm-schema-notes.md`.
- **Negative / constraints:** standard tables have many system columns and
  behaviours we don't use; alternate keys must be *added* to standard tables
  (they don't ship with business-natural alt keys). Governance/audit still needs
  configuration (Epic 11), not just the presence of the `audit` table.

## Alternatives considered

- **All-custom `racy_` CRM tables** — rejected: non-idiomatic, high effort,
  forfeits built-in relationships/security/forms/activities, and misrepresents
  how a real Dynamics implementation is built.

## Notes

Design-only (#8): the ERD (`docs/diagrams/crm-erd.md`) and schema notes
(`docs/architecture/crm-schema-notes.md`) accompany this ADR and drive table
creation/configuration in #6. Only the `racy_ai*` tables are created by
`scripts/dataverse/create_racy_schema.py`; the standard tables already exist in
the environment.
