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

**Model the CRM domain on native Dataverse standard tables where they exist**,
and add custom `racy_` tables for what the target environment doesn't provide.

> **Amendment (Option B, after #6 discovery).** The original decision assumed all
> 12 standard tables exist. In practice `racy-dev` is a **plain Dataverse
> environment** — it has the base tables (`account`, `contact`,
> `activitypointer`, `knowledgearticle`, `annotation`, `audit`) but **not** the
> Dynamics 365 Sales/Customer Service tables (`lead`, `opportunity`, `product`,
> `incident`), which only appear once those first-party apps are installed.
> Rather than install those apps (heavier, licensing-dependent, hundreds of
> tables for a data-model + AI showcase), we **model the four missing entities as
> custom `racy_` tables**. See the environment check in `create_racy_schema.py`.

| Domain entity | Dataverse table | Kind |
|---|---|---|
| Account | `account` | standard |
| Contact | `contact` | standard |
| Activity | `activitypointer` (+ task/phonecall/email…) | standard |
| Knowledge Article | `knowledgearticle` | standard |
| Document | `annotation` (Note+attachment) / SharePoint | standard |
| Audit Event | `audit` | standard (platform) |
| Lead | `racy_lead` | **custom** *(Sales app not installed)* |
| Opportunity | `racy_opportunity` | **custom** *(Sales)* |
| Case | `racy_case` | **custom** *(Customer Service)* |
| Product | `racy_product` | **custom** *(Sales)* |
| AI Request | `racy_airequest` | **custom** |
| AI Response | `racy_airesponse` | **custom** |

The custom CRM tables follow the **flat-table** pattern (ADR-0009 / the Paddock
tables): cross-entity references are carried as *code columns*
(`racy_accountnumber`, `racy_contactcode`, …), and native lookups / N:N are
model-driven-app enrichment (#11/#12), not created by the provisioning script.
The `racy_` prefix stays reserved for the genuinely custom (these CRM entities +
AI-logging here; F1 sample data and the Paddock game elsewhere).

## Consequences

- **Positive:** idiomatic Dynamics 365 — standard tables bring relationships,
  security roles, auditing, activities, and BPFs for free; reads as real-world
  architecture in the portfolio; the assistant already queries native tables
  (e.g. `accounts`). Less to build and maintain.
- **Upsert:** standard tables carry a GUID primary key; where the pipeline
  upserts (seeding, integration) it uses a **defined alternate key** on a natural
  business identifier — added to the standard tables (`account.accountnumber`,
  `contact.emailaddress1`) and native on the custom ones (`racy_leadcode`,
  `racy_opportunitycode`, `racy_casecode`, `racy_productnumber`). The AI tables
  use `racy_requestcode`. (`knowledgearticle` gets **no** alt key —
  `articlepublicnumber` exceeds Dataverse's 1700-byte alt-key index limit, and KB
  content is indexed for RAG in Azure AI Search, not upserted here.)
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
