# Grounded generation with citations

The answer side of the RAG pipeline (#73): turn retrieved chunks into an answer
that **cites its sources**, so a reader can verify the answer is grounded rather
than hallucinated.

## Flow

```
question + retrieved chunks (#71)
  ─► as_context(chunks)                       # sources tagged [id]
  ─► structured_output(_RawAnswer)            # {answer, citations: [id, ...]} (#60)
  ─► resolve citations against retrieved ids  # drop unknown, dedupe
  ─► CitedAnswer(answer, [Citation(id, source, section), ...])
```

## Citation format

A `CitedAnswer` is the `answer` text plus a list of `Citation`s. Each citation
carries:

- **`id`** — the retrieved chunk's id (the Azure AI Search document key), the
  stable handle for the exact chunk.
- **`source`** + **`section`** — the human-readable provenance a UI shows
  (e.g. *regs.md · Overtaking*).

`is_grounded` is true when at least one citation survived resolution.

## The trust guarantee

The model is prompted to answer **only** from the numbered sources and to cite
the ids it used. Returned citations are then **resolved against the retrieved
chunk ids**: any id the model invents (not in the retrieved set) is discarded,
and duplicates are collapsed (order-preserved). So every citation on a
`CitedAnswer` provably maps to a real chunk the caller was allowed to retrieve
(#72) — a hallucinated source cannot appear in the output.

When no chunks are retrieved, generation short-circuits to a plain "no sources"
answer with no citations and **no model call** — it never answers from model
memory.

## Testing

Unit tests (injected fake SDK) cover: citations resolve to retrieved chunks, a
hallucinated id is dropped, duplicates are deduped, the context/ids reach the
prompt, empty-citations ⇒ not grounded, and no-chunks ⇒ ungrounded answer with
no model call. Live-verified end to end (`scripts/rag/verify_generation.py`): a
DRS question returns a grounded answer citing the DRS chunk; an off-topic
question is declined with no citations.
