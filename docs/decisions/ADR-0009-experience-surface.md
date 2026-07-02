# ADR-0009: Experience surface and business-logic placement

## Status

Proposed

> Supersedes the placeholder "ADR-0007 (experience surface)" referenced in
> earlier drafts of the Dynamics/Dataverse technical documentation. ADR-0007 is
> reserved for the agent-orchestration framework decision (Epic 10, spike 10.1);
> the experience-surface + business-logic-placement decision is recorded here as
> ADR-0009. Grounded in `docs/architecture/dynamics-dataverse.md` §6–§7.

## Context

The solution needs (a) a human experience surface for the CRM domain and the
Paddock Club predictions game, and (b) a clear, consistent rule for **where
business logic lives** — Dataverse (plug-in / business rule / Power Automate)
vs the Azure back end (Functions). Getting placement wrong risks non-atomic
money-like operations, untestable logic, or logic hidden in low-code that the
portfolio can't showcase or audit.

## Decision

**Experience surface:** the primary surface is a **native model-driven app**
(Dynamics 365) over Dataverse, with the sitemap areas in the tech doc §6
(Command Centre, Race Data, CRM Workspace, Paddock Club, AI Studio,
Governance). A custom page / PCF surface is **not** adopted for Tier A; it is
retained as a future option only if a specific interaction cannot be expressed
in native forms/views. Rationale: maximises out-of-the-box audit, security and
rollup behaviour, and keeps the build focused on the AI/data architecture
rather than bespoke UI.

**Business-logic placement** follows this rule of thumb — *deterministic,
transactional, must-be-atomic → plug-in or Azure Function; orchestration /
notification → Power Automate; simple field behaviour → business rule*:

| Logic | Placement | Why |
|---|---|---|
| Confirm-and-lock wager (freeze odds, debit wallet, enforce deadline) | Synchronous **plug-in** (or tightly-scoped function) | Must be atomic and guarded; races the deadline; no partial debit |
| Settlement grading + payout | **Azure Function** (timer) | Deterministic, testable, idempotent; heavy read of F1 data; belongs off-platform |
| Odds pricing | **Azure Function** | Reuses ingested history / the ML model; not a Dataverse concern |
| Hide/lock form controls after lock | **Business rule** | Pure UI behaviour |
| "Race Event locked" notifications | **Power Automate** | Orchestration/notification, not core state |
| AI request/response logging | **Azure Function** via Web API | The caller owns the log write |

**Constraint:** a synchronous plug-in is an acceptable home for the lock
transaction because plug-in requests are exempt from the service-protection
request-count limit — but its execution time still counts against the
triggering request's budget, so it must stay lean (see tech doc §9.3).

## Options Considered

1. **Native model-driven app + the placement rule above (CHOSEN)** — best
   audit/security/rollup for free; clear, defensible logic boundaries.
2. Custom page / canvas / PCF front end — more UI control, but more bespoke
   code to build and secure, and less out-of-the-box governance. Deferred.
3. All logic in Power Automate / low-code — fast to prototype, but non-atomic
   for the money-like lock/settle operations and weaker to test/showcase.
   Rejected for the transactional core.

## Consequences

**Positive:** consistent, auditable logic boundaries; the atomic lock and the
idempotent settlement live where they can be tested; native app gives
leaderboard rollups and audit views with no custom code.

**Negative:** a synchronous plug-in introduces a small amount of C#/Dataverse
SDK surface (the only non-Python component); the experience-surface choice
should be revisited if a required interaction outgrows native forms.

## Follow-up Actions

- [ ] Confirm the plug-in vs tightly-scoped-function choice for the lock
      transaction when building 12.PA-5
- [ ] Record the chosen lock implementation in 12.PA-5's Definition of Done
