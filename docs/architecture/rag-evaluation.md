# RAG evaluation

Measuring RAG quality rather than assuming it (#74). An evaluation set of
questions with expected sources, scored on retrieval and answer quality, so
weaknesses are surfaced rather than left undetected.

## Method

- **Eval set** (`rag.evaluation.dataset`): ≥ 12 `EvalCase`s, each a question + the
  section it should be answered from + keywords a relevant answer should contain +
  the caller roles. It targets a small F1 sporting-regulations corpus (one section
  per topic), shipped alongside so the eval is reproducible.
- **Metrics** (`rag.evaluation.evaluator`):
  - **Retrieval hit rate** — fraction of questions where retrieval surfaced the
    expected section (recall@k at the section level).
  - **Groundedness** — fraction of answers that cite at least one source.
  - **Relevance** — rule-based: the answer contains every expected keyword
    (deterministic and cheap; an LLM-judge could replace this later).
- **Runner** — `evaluate(run, cases)` scores each case through an injected
  `RunQuery` callable, so it is pure and unit-tested; `make_rag_run(retriever,
  client)` adapts the live retrieve → generate pipeline into that callable.
- **Live run** — `scripts/rag/run_evaluation.py` ingests the corpus into a temp
  index and evaluates the default set end to end.

## Results (live, 12 questions)

| Metric | Score |
|--------|-------|
| Retrieval hit rate | **1.00** |
| Groundedness | **0.92** |
| Relevance | **0.92** |

Retrieval surfaced the correct section for every question — hybrid search over a
small, well-sectioned corpus is strong. Two weaknesses surfaced:

- *"What penalties can stewards impose?"* — retrieved and grounded, but the answer
  paraphrased ("time penalties, grid drops…") without the literal keyword the
  rule-based check expected. This is a **metric limitation** (keyword matching is
  brittle) more than an answer fault — a reason to move to an LLM-judge for
  relevance.
- *"When is the fastest-lap point awarded?"* — relevant and correct, but the model
  did not return a citation on that run, so it scored ungrounded. A prompting/
  determinism weakness worth watching.

## Interpreting weaknesses

The value is the **weak-case list**, not just the aggregate: it points at whether
to fix ingestion/chunking, retrieval, the generation prompt, or the metric
itself. Here, hit rate is saturated (the corpus is small and clean), so the
signal to improve is in groundedness/relevance and the metric quality, not
retrieval.

## Limitations

- Rule-based relevance under-scores correct-but-paraphrased answers; an LLM-judge
  would be fairer (future work).
- The corpus is small, so retrieval hit rate is optimistic versus a large,
  overlapping knowledge base.
- Scores vary slightly run to run with model non-determinism.
