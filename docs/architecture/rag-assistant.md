# End-to-end RAG assistant

The headline Epic 9 deliverable (#25, feature #123): a single entrypoint that
answers a question for a specific caller, grounded in permitted knowledge and
cited to its sources. It composes the Epic 9 components — no new retrieval tech.

## API

```python
RagAssistant(retriever, client, policy=DEFAULT_POLICY, logger=...).ask(
    question: str, roles: Iterable[str], *, top_k: int = 5
) -> CitedAnswer
```

`CitedAnswer` = the answer text + resolved `Citation`s (`id`, `source`,
`section`) + `is_grounded`.

## Flow

```
ask(question, roles)
  ─► log_request                                   # governance (Epic 8)
  ─► retriever.retrieve_for(question, roles)       # hybrid (#71) + permission-aware (#72)
  ─► generate_answer(question, chunks)             # grounded + cited (#73)
  ─► log_response(ok = is_grounded)
  ─► CitedAnswer
```

The caller's Dataverse **role is enforced in retrieval**, before generation and
before the model sees anything — so the answer and its citations can only ever
draw on sources the caller is allowed to retrieve. Citations are resolved
against the retrieved set, so a model-invented source cannot appear.

## Access guarantee (verified with two users)

For the same question:

- a **manager** retrieves public + internal + confidential chunks and gets a
  grounded answer citing them;
- a **guest** retrieves only public chunks — if those don't answer the question
  the assistant says so and cites nothing; it **cannot** surface or cite the
  confidential content the manager can;
- an **unknown role** retrieves nothing (deny-by-default) and gets an ungrounded
  answer with no model call.

This is verified in unit tests (a filter-respecting fake index) and live
(`scripts/rag/verify_rag_assistant.py`) against Azure AI Search + Azure OpenAI,
with prompt/response logged to Dataverse.

## Limitations

- Retrieval relevance is only as good as the ingestion/chunking (#67) and the
  Free-tier index; there is no semantic reranker (needs a Basic+ Search tier).
- Role→access-tag mapping is the default `AccessPolicy`; Epic 11 (11.B) governs
  the real policy and its mapping to Dataverse security roles.
- Answers are single-turn; conversation memory (as in the CRM assistant, #63) is
  not part of this entrypoint.

## Next

This unblocks **#65** — grounding the CRM assistant with RAG: the CRM assistant
delegates knowledge questions to this RAG assistant behind its `CrmRetriever`
seam.
