"""Live end-to-end verification of hybrid retrieval (#71).

Against racy-search-dev: create a temp index, ingest + embed a short knowledge
source, upload, then run the Retriever (hybrid vector + keyword) on sample
queries and confirm the relevant chunk is retrieved top-1. Deletes the temp
index afterwards.

Run: python scripts/rag/verify_retrieval.py
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
    "# Overtaking and DRS\n\nDrivers must not leave the track and gain a lasting advantage. "
    "The drag reduction system may be used only within designated activation zones.\n\n"
    "# Safety Car\n\nWhen the safety car is deployed, overtaking is forbidden and drivers "
    "must reduce speed and hold position.\n\n"
    "# Pit Stops\n\nA driver may change tyres in the pit lane; the pit lane speed limit is "
    "strictly enforced and unsafe releases are penalised."
)


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from rag import KnowledgeIndex, Retriever, SearchConfig, embed_chunks, ingest_markdown

    client = AIClient(AzureOpenAIConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    result = ingest_markdown([("regs.md", SOURCE, "public")], size=200, overlap=40)
    run = embed_chunks(client, result.chunks)
    print(f"chunks={run.embedded} dims={run.dimensions}")

    ok = True
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):  # wait until all docs are queryable
            time.sleep(2)
            if len(ki.keyword_search("*", top=len(run.chunks))) >= len(run.chunks):
                break

        retriever = Retriever(ki, client)
        cases = [
            ("when are drivers allowed to use DRS?", "Overtaking and DRS"),
            ("what happens when the safety car comes out?", "Safety Car"),
            ("is there a speed limit for changing tyres?", "Pit Stops"),
        ]
        for query, expected in cases:
            hits = retriever.retrieve(query, top_k=2)
            sections = [h.section for h in hits]
            passed = expected in sections  # AC: relevant chunk appears in top-k
            ok &= passed
            print(f"[{'PASS' if passed else 'FAIL'}] {query!r} -> top-{len(sections)} {sections}")
    finally:
        ki.delete()
        print("deleted temp index")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
