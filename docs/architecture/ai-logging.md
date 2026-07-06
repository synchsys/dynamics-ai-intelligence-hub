# AI Prompt/Response Logging

The Epic 8 governance capability (#69): **every LLM call in a feature logs its
prompt and the model's response** to two paired Dataverse tables. Governance is
wired in at the `ai` layer (`src/ai/prompt_log.py`) and reused by the CRM
assistant (#63), the RAG assistant (#25), and the Paddock free-text intake
(#230) — it is not bolted on later by Epic 11.

## Flow

```
feature ─► logger.log_request(code, purpose, model, prompt, user_id)   # who asked, what, which model
        ─► <LLM call>                                                  # timed with time.perf_counter()
        ─► logger.log_response(code, raw_output, decision, ok, error,  # what came back
                               tokens, latency_ms)                     # cost + performance signals
```

`request_code` is a per-call correlation id (`uuid4().hex` by default, injectable
in tests). It is the alternate key on **both** tables, so a request row and its
response row are paired 1:1 by `racy_requestcode`.

## Interfaces (`src/ai/prompt_log.py`)

- **`PromptLogger`** (Protocol) — `log_request` / `log_response`. Callers depend
  on this, so features stay testable with an in-memory fake.
- **`NullLogger`** — records nothing, never raises. Default for tests and
  offline runs.
- **`DataversePromptLogger`** — the live adapter. Upserts to `racy_airequests`
  and `racy_airesponses` via a `SupportsUpsert` Dataverse client (keyed on
  `racy_requestcode`).

`ai.client.usage_tokens(response)` extracts `response.usage.total_tokens` from an
SDK completion (returns `None` when the SDK reported no usage), so callers can
pass `tokens=` without reaching into the SDK response shape themselves.

All fields beyond the request core (`user_id`, `tokens`, `latency_ms`,
`settlement_type`, `error`) are **optional** — each caller logs what it has. No
secret values are ever logged; prompts and raw outputs are business content, not
credentials.

## Schema

Provisioned by `scripts/dataverse/create_racy_schema.py`.

### `racy_AiRequest` — who asked, and what

| Column | Type | Meaning |
|---|---|---|
| `racy_RequestCode` | string | Correlation id (alternate key) |
| `racy_Purpose` | string | `wager-intake` / `crm-assistant` / `rag-assistant` |
| `racy_Model` | string | Deployment name the call targeted |
| `racy_Prompt` | memo | The user prompt / question |
| `racy_UserId` | string | Acting user — who asked (#69) |

### `racy_AiResponse` — what came back

| Column | Type | Meaning |
|---|---|---|
| `racy_RequestCode` | string | Correlation id (pairs to the request) |
| `racy_RawOutput` | memo | The model's raw output |
| `racy_Decision` | string | `propose` / `decline` / `answer` / `answer-rag` / `error` |
| `racy_SettlementTypeCode` | string | Intake settlement type, when applicable |
| `racy_Ok` | bool | Whether the call produced a usable result |
| `racy_Error` | memo | Failure detail when `Ok` is false |
| `racy_Tokens` | int | Total tokens — cost signal (#69) |
| `racy_LatencyMs` | int | End-to-end latency in ms — performance signal (#69) |

## Observability signals (#69)

- **`user_id`** — attributes each AI call to the acting user (assistant caller /
  intake player), so requests are auditable per person.
- **`tokens`** — total tokens for the completion, for cost tracking. Captured on
  the CRM assistant path via `usage_tokens(response)`. The RAG assistant does not
  yet surface usage (it returns a `CitedAnswer`, not the raw response), so its
  `tokens` are unset — a future enhancement can thread usage through
  `generate_answer`.
- **`latency_ms`** — wall-clock time from just after `log_request` to the
  `log_response` call, measured with `time.perf_counter()` and rounded to one
  decimal place on write. Every response path (success, decline, mapping
  failure, parse error) records a latency.

## Callers

| Feature | Module | `purpose` | Records |
|---|---|---|---|
| Wager intake (#230) | `paddock.intake.service` | `wager-intake` | user_id, latency on all four response paths |
| CRM assistant (#63) | `ai.assistant.service` | `crm-assistant` | user_id, tokens (CRM path), latency |
| RAG assistant (#25) | `rag.assistant` | `rag-assistant` | latency |

Epic 11 (Security & Governance) defines *policy* over this data (retention,
access, redaction review) — it does not re-implement the logging.
