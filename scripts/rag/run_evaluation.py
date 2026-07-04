"""Run the RAG evaluation against the live pipeline (#74).

Ingests the default eval corpus into a temp index, then evaluates the default
question set end to end (retrieve -> generate), reporting hit rate, groundedness,
relevance, and any weak cases. Deletes the temp index afterwards.

Run: python scripts/rag/run_evaluation.py
"""

import dataclasses
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from rag import KnowledgeIndex, Retriever, SearchConfig, embed_chunks, ingest_markdown
    from rag.evaluation import DEFAULT_EVAL_SET, evaluate, make_rag_run, merged_corpus

    client = AIClient(AzureOpenAIConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    run = embed_chunks(client, ingest_markdown(merged_corpus(), size=400, overlap=60).chunks)
    print(f"indexed {run.embedded} chunk(s)")

    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(20):
            time.sleep(2)
            if len(ki.keyword_search("*", top=run.embedded)) >= run.embedded:
                break

        report = evaluate(make_rag_run(Retriever(ki, client), client), DEFAULT_EVAL_SET)
        print("\n" + report.summary())
        for weak in report.weaknesses:
            print(
                f"  WEAK: {weak.case.question!r} "
                f"(hit={weak.hit} grounded={weak.grounded} relevant={weak.relevant})"
            )
    finally:
        ki.delete()
        print("deleted temp index")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
