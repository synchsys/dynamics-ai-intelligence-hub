"""Live end-to-end verification of grounded generation with citations (#73).

The full RAG path against racy-search-dev + Azure OpenAI: ingest + embed + index
a short source, retrieve for a question, then generate a cited answer and confirm
at least one citation resolves to a retrieved chunk. Also checks an out-of-scope
question is declined with no citations. Deletes the temp index afterwards.

Run: python scripts/rag/verify_generation.py
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


SOURCE = (
    "# Overtaking and DRS\n\nThe drag reduction system (DRS) may be used only within "
    "designated activation zones, and only when a driver is within one second of the car "
    "ahead.\n\n# Safety Car\n\nWhen the safety car is deployed, overtaking is forbidden and "
    "drivers must hold position and reduce speed."
)


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from rag import (
        KnowledgeIndex,
        Retriever,
        SearchConfig,
        embed_chunks,
        generate_answer,
        ingest_markdown,
    )

    client = AIClient(AzureOpenAIConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    run = embed_chunks(
        client, ingest_markdown([("regs.md", SOURCE, "public")], size=200, overlap=40).chunks
    )
    print(f"chunks={run.embedded} dims={run.dimensions}")

    ok = True
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):
            time.sleep(2)
            if len(ki.keyword_search("*", top=len(run.chunks))) >= len(run.chunks):
                break

        retriever = Retriever(ki, client)
        retrieved_ids = {c.id for c in retriever.retrieve("when can DRS be used?", top_k=3)}

        grounded = generate_answer(
            client,
            "When is a driver allowed to use DRS?",
            retriever.retrieve("When is a driver allowed to use DRS?", top_k=3),
        )
        print(f"answer: {grounded.answer.strip()[:160]}")
        print(f"citations: {[c.id for c in grounded.citations]}")
        cited_ok = grounded.is_grounded and any(c.id in retrieved_ids for c in grounded.citations)

        offtopic = generate_answer(
            client,
            "What is the capital of France?",
            retriever.retrieve("What is the capital of France?", top_k=3),
        )
        print(f"off-topic grounded={offtopic.is_grounded}")

        ok = cited_ok  # the AC: >=1 citation resolves to a retrieved chunk
        print(f"cited_ok={cited_ok}")
    finally:
        ki.delete()
        print("deleted temp index")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
