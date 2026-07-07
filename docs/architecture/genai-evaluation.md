# GenAI Output Evaluation

Quality evidence for the generative outputs — **summaries** and **assistant
answers** — measured against documented criteria rather than assumed (#66).
Harness lives in `src/ai/evaluation/`.

## Criteria

Each output is scored on two independent axes:

- **Groundedness** — does the output stay faithful to its **source** (no invented
  or contradicted facts)?
- **Relevance** — does the output actually address the **prompt**?

An output *passes* only if it is both grounded and relevant.

## Evaluation set (`dataset.py`)

A reproducible, labelled set of **13 cases** (≥10 required) mixing tasks —
summaries and answers over F1-session and CRM contexts — held as data so it is
deterministic and can grow. Each `GenAICase` carries its `source`, `prompt`, the
`output` under evaluation, the relevance `keywords`, and a `should_pass` flag.

Crucially the set includes **3 deliberately flawed** cases (`should_pass=False`)
— ungrounded (hallucinated facts), off-topic (misses the ask), or both — so the
harness is shown to *catch* weaknesses, not just rubber-stamp good output.

## Scoring — two interchangeable scorers

Both satisfy one `Scorer` contract (`score(case) -> (grounded, relevant)`), so
`evaluate()` is agnostic to which ran. **Choice recorded:** we ship *both* — a
deterministic rule scorer as the CI default, and an LLM-as-judge for a semantic
score at demo time.

| | `RuleScorer` (default, CI) | `LlmJudge` (live) |
|---|---|---|
| Groundedness | share of the output's content words present in the source ≥ 0.5 (**lexical proxy** — catches source-absent vocabulary; not semantic entailment) | model judges factual support against the source |
| Relevance | output contains every expected keyword | model judges whether it addresses the prompt |
| Determinism | yes (no network) | no (Azure OpenAI) |

The rule scorer's groundedness is an honest **lexical proxy**: it flags
hallucinations that introduce new vocabulary, but a faithful paraphrase using
synonyms could score low — that gap is exactly what `LlmJudge` closes.

## Results (rule scorer, default set)

```
n=13  groundedness=0.846  relevance=0.769  pass_rate=0.769  weaknesses=3
```

The harness flagged **exactly the 3 intentionally-flawed cases** and passed all
10 faithful ones:

| Case | grounded | relevant | Why flagged |
|---|---|---|---|
| `flaw-ungrounded` | ✗ | ✗ | summary of facts absent from the source |
| `flaw-offtopic` | ✓ | ✗ | on-source but doesn't answer the question |
| `flaw-both` | ✗ | ✗ | unrelated content |

`flaw-offtopic` is the instructive one — **grounded yet irrelevant** — showing
the two axes are scored independently.

## Known weaknesses & next steps

- Lexical groundedness under-scores faithful paraphrase and can't detect subtle
  contradiction — run `LlmJudge` for those; a future step is comparing the two
  scorers' agreement on the same set.
- The set is small and hand-authored; grow it from real assistant/summary
  outputs (and add adversarial cases) as the features evolve.

## Run it

```python
from ai.evaluation import evaluate, RuleScorer, LlmJudge
print(evaluate().summary())                    # rule-based (deterministic)
print(evaluate(LlmJudge(client)).summary())    # LLM-as-judge (live Azure OpenAI)
```
