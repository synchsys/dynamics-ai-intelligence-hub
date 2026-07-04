# CRM Assistant

A conversational assistant over the generic CRM domain (#63). It answers
questions **grounded in Dataverse data**, keeps conversation history, and logs
every prompt/response for governance. It is the read-only, grounded foundation
that #64 (guarded action tools) and #65 (cited RAG answers) build on.

## Flow

```
question ─► CrmRetriever.context(question)         # pull relevant CRM records
        ─► prompts.render("crm_qa", context, question)   # system carries context (#59)
        ─► [system, ...history, user]              # multi-turn conversation
        ─► AIClient.chat(...)                       # Azure OpenAI (#58)
        ─► PromptLogger.log_request/response        # governance (ai.prompt_log)
        ─► AssistantAnswer(text, context)
```

## Components (`src/ai/assistant/`)

- **`CrmAssistant`** — the conversation loop. Each `ask()` retrieves fresh
  context, renders the `crm_qa` prompt with it, appends the turn to history, and
  logs the exchange. `reset()` clears history.
- **`CrmRetriever`** (Protocol) + **`DataverseCrmRetriever`** — turn CRM records
  into a context block. The Dataverse implementation reads a configured set of
  `EntityView`s (entity set + fields) and formats a bounded number of rows per
  view. Relevance is deliberately simple; **Epic 9 RAG (#65)** slots a
  retrieval-and-citation implementation in behind the same `CrmRetriever`
  contract.

## Grounding contract

The `crm_qa` prompt instructs the model to answer **only** from the supplied
context and to say when it doesn't know — never to invent records or figures.
This mirrors the deterministic reject-don't-guess rule elsewhere (ADR-0008).
Verified live: asked which accounts are in a city, it lists exactly the matching
accounts; asked for data not in context (a revenue forecast), it declines rather
than fabricating (`scripts/ai/verify_assistant.py`).

## Governance

Prompt and response are logged to the `racy_airequest` / `racy_airesponse`
Dataverse tables via `ai.prompt_log.DataversePromptLogger` — the same
capability used by the Paddock free-text intake (#230). Logging is wired in from
the start, not bolted on (Epic 11 consolidates policy over it).

## Actions & approval (#64)

Beyond answering, the assistant can *act* through the #61 tool layer
(`src/ai/crm_tools.py`), built for safety:

- **`lookup_records`** — a read tool; executes immediately against Dataverse.
- **`create_followup_activity`** — a **guarded write**. Invoking it never writes
  to Dataverse; it **stages** a `PendingWrite` in an `ApprovalBroker` and returns
  a "pending approval" result. The record is created only when a human calls
  `broker.approve(action_id)` (or discarded via `reject`). Every staged /
  approved / rejected action is recorded in the broker's audit trail.

`build_crm_tools(read_gw, write_gw)` assembles both tools + the broker into a
`ToolRegistry` for `run_tools`. Because the write tool is side-effect-free until
approved, the model can plan and "request" an action within the tool loop while
the actual mutation stays behind the human gate — the concrete case of
human-in-the-loop (#80). Verified live (`scripts/ai/verify_actions.py`): the
follow-up is blocked before approval and created only after.

## RAG grounding (#65)

The assistant can be given an optional **knowledge source** — the Epic 9 RAG
assistant (#25) — for cited, permission-aware answers to knowledge questions:

```
ask(question)
  ─► knowledge.ask(question, roles)     # RAG: permission-aware, cited
        ─► grounded?  ── yes ──► return the cited answer (grounded_in="knowledge")
        └─ no ─► fall back to CRM-data answer (grounded_in="crm")
```

The knowledge source is a structural **`KnowledgeSource` Protocol** (`ask(question,
roles) -> GroundedAnswer`), so `ai` does not import `rag` (which depends on `ai`)
— the `RagAssistant` is injected and duck-types the contract, avoiding a
dependency cycle. The caller's `roles` are forwarded so RAG enforces access at
retrieval time. `AssistantAnswer` now carries `citations` and `grounded_in`
(`"knowledge"` or `"crm"`).

**Routing:** RAG is tried first; if it grounds (finds relevant, permitted
sources) its cited answer is returned, otherwise the assistant falls back to the
Dataverse-data path — so knowledge questions get cited answers and CRM questions
still work when the knowledge base has nothing relevant. Verified live
(`scripts/ai/verify_assistant_rag.py`): a DRS question is answered from RAG with a
citation; an accounts question falls back to Dataverse.

## Testing

The model, retriever, logger, gateways, and knowledge source are all injected, so
the assistant and tools are unit-tested hermetically (grounded answer, history,
reset, logging; read executes, write blocked until approved, approve/reject audit
trail; RAG-grounded vs CRM-fallback routing). Live smoke tests
(`scripts/ai/verify_assistant.py`, `verify_actions.py`, `verify_assistant_rag.py`)
exercise the full paths against Azure OpenAI + Dataverse and clean up after
themselves.
