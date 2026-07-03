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

## Testing

The model, retriever, and logger are all injected, so the assistant is
unit-tested hermetically (grounded answer, history carried forward, reset,
logging). A live smoke test (`scripts/ai/verify_assistant.py`) exercises the
full path against Azure OpenAI + Dataverse and cleans up after itself.
