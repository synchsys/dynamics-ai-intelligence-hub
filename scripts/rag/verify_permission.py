"""Live verification of permission-aware retrieval (#72).

Seeds a temp index with public / internal / confidential chunks, then retrieves
the same query as a guest and as a manager and confirms the guest provably
cannot see the internal/confidential chunks the manager can. Deletes the temp
index afterwards.

Run: python scripts/rag/verify_permission.py
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
    from rag import (
        Document,
        KnowledgeIndex,
        Retriever,
        SearchConfig,
        embed_chunks,
        ingest,
    )

    client = AIClient(AzureOpenAIConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    docs = [
        Document("policies.md", "The staff canteen opens at 8am.", access_tag="public", section="Canteen"),
        Document("policies.md", "Internal only: the Q4 reorg plan affects the sales team.", access_tag="internal", section="Reorg"),
        Document("policies.md", "Confidential: acquisition target is Globex, offer 40M.", access_tag="confidential", section="M&A"),
    ]
    run = embed_chunks(client, ingest(docs).chunks)
    print(f"chunks={run.embedded} dims={run.dimensions}")

    ok = True
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):
            time.sleep(2)
            if len(ki.keyword_search("*", top=3)) >= 3:
                break

        retriever = Retriever(ki, client)
        query = "what do we know about the company plans?"
        guest = {c.access_tag for c in retriever.retrieve_for(query, ["guest"], top_k=5)}
        manager = {c.access_tag for c in retriever.retrieve_for(query, ["manager"], top_k=5)}
        intruder = retriever.retrieve_for(query, ["intruder"], top_k=5)

        print(f"guest sees:    {sorted(guest)}")
        print(f"manager sees:  {sorted(manager)}")
        print(f"intruder sees: {len(intruder)} chunks")
        ok = (
            guest == {"public"}
            and "confidential" in manager
            and "internal" in manager
            and intruder == []
        )
    finally:
        ki.delete()
        print("deleted temp index")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
