# ADR-0008: Odds generation and free-text wager settlement contract

## Status

Proposed

> Source: Paddock Club artefact pack v0.4.2. Adopted into the backlog by the
> rework of 2026-07-02; remains Proposed until the Paddock Club schema
> (12.PA-1) and settlement registry (12.PA-2) land.

## Context

The Paddock Club punter experience accepts free-text predictions rather than a
fixed market catalogue. Two problems must be solved safely: (1) pricing
arbitrary predictions, and (2) grading them deterministically from ingested
data at the end of the race. An LLM can plausibly price and restate a
prediction, but must never be trusted to decide whether a bet paid out — that
would be ungrounded and non-reproducible. Free text also risks producing
unsettleable bets that can never be graded.

## Decision

1. Free text is mapped, at slip-creation time, onto a Settlement Type from an
   enumerable Settlement Capability Registry, using LLM function calling with
   structured output. The registry is sized to what ingestion supports and
   grows with it.
2. Each Settlement Type has a deterministic grading function that reads
   ingested data — no LLM involvement at settlement.
3. **Settlement source of truth is OpenF1 for Tier A.** Its `session_result`,
   `starting_grid`, `laps` and dedicated `/pit` endpoints grade all Tier-A
   types (1–12) via a single lightweight REST-ingested path. A type may only
   take a heavier source (e.g. FastF1) when OpenF1 genuinely cannot ground it:
   `driver_crash` (type 15) needs FastF1's results `Status`, and
   `safety_car_deployed` (type 13) is best grounded on FastF1's coded
   `track_status` stream rather than fuzzy `race_control` text (the OpenF1
   parse remains a fallback). Such multi-source types are **Tier B**, are
   flagged FastF1-dependent, and **VOID** when the source is missing or
   ambiguous rather than inferring. Punters get the deterministic `driver_dnf`
   (type 7, OpenF1) in Tier A. The same registry types grade **qualifying**
   sessions unchanged (pole, reach-Q3, quali head-to-head) by pointing at a
   qualifying session key — no new grading code.
4. If free text cannot be mapped to a registry type (or a driver cannot be
   resolved), the request is **REJECTED WITH GUIDANCE** listing supported
   prediction kinds. No silent accept; no manual-review queue in Tier A.
5. Odds are generated v1 by a recent-form heuristic and v2 by the Epic 7
   probability model; both write the same odds field, flagged by source. Odds
   and the settlement spec are **FROZEN** onto the slip at lock time.
6. Settlement is **VOID-ON-MISSING-DATA**: if required ingested facts are
   absent or ambiguous, the slip is voided and the stake refunded — never
   graded on a guess.
7. Settlement is **IDEMPOTENT**: re-running after an upstream data correction
   (revised lap times, post-race disqualification) must reconcile to the
   correct result without double-paying.
8. **Virtual credits only.** No real currency, deposit, cash-out, or betting
   terminology anywhere in the app or documentation.

## Options Considered

1. Fixed market catalogue (no free text) — simplest to settle, but loses the
   LLM/structured-output/function-calling showcase and the engagement hook.
   Rejected as the primary design; retained as the fallback shape.
2. Free text priced AND graded by the LLM — richest UX, but ungrounded,
   non-reproducible settlement. Rejected on safety and portfolio-integrity
   grounds.
3. Free text → structured spec (LLM), graded by code (**CHOSEN**) — keeps the
   AI showcase where it is trustworthy (intake) and keeps grading
   deterministic and auditable.

## Consequences

**Positive:** strong structured-output + function-calling deliverable; grading
is testable and reproducible; ingestion correctness gains real consequence; a
clean "we know where not to trust the model" governance story for the
Responsible AI assessment (11.B).

**Negative:** intake must handle mapping failures gracefully; the registry and
ingestion coverage are coupled and must be versioned together; settlement
statefulness (idempotency, void) is the first real business logic in the
project and needs careful tests; multi-source types (FastF1 for `driver_crash`)
add a heavier, slower settlement path and a second data dependency, so they are
deliberately isolated to Tier B.

## Follow-up Actions

- [ ] Seed the Settlement Type registry (types 1–12) as reference data (12.PA-2)
- [ ] Add the settlement-completeness acceptance criterion to Epic 4 ingestion
      (entry list + `session_result` must be present to settle)
- [ ] Record the virtual-credits framing in the Responsible AI note (11.B)
- [ ] Log the FastF1 / Ergast–jolpica dependency risk before Tier-B types 13/15
