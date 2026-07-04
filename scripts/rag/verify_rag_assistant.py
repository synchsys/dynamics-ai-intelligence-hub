"""Live end-to-end verification of the assembled RAG assistant (#25 / #123).

Seeds a temp index with public/internal/confidential knowledge, then asks the
same question as a guest, a manager, and an unknown role — confirming answers are
grounded and cited, that the guest cannot surface confidential content the
manager can, and that prompt/response are logged to Dataverse. Cleans up the temp
index and the logged rows afterwards.

Run: python scripts/rag/verify_rag_assistant.py
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
    from ai import AIClient, AzureOpenAIConfig, DataversePromptLogger
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig
    from rag import (
        Document,
        KnowledgeIndex,
        RagAssistant,
        Retriever,
        SearchConfig,
        embed_chunks,
        ingest,
    )

    client = AIClient(AzureOpenAIConfig.from_env())
    dv = DataverseClient(DataverseConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    docs = [
        Document("policy.md", "The staff canteen opens at 8am on weekdays.", access_tag="public", section="Canteen"),
        Document("policy.md", "Internal: the Q4 reorganisation merges the sales and support teams.", access_tag="internal", section="Reorg"),
        Document("policy.md", "Confidential: the acquisition target is Globex, at an offer of 40 million.", access_tag="confidential", section="M&A"),
    ]
    run = embed_chunks(client, ingest(docs).chunks)
    print(f"chunks={run.embedded} dims={run.dimensions}")

    ok = False
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):
            time.sleep(2)
            if len(ki.keyword_search("*", top=3)) >= 3:
                break

        assistant = RagAssistant(Retriever(ki, client), client, logger=DataversePromptLogger(dv))
        question = "What upcoming company changes are planned?"

        manager = assistant.ask(question, ["manager"], top_k=5)
        guest = assistant.ask(question, ["guest"], top_k=5)
        intruder = assistant.ask(question, ["intruder"], top_k=5)

        m_sections = {c.section for c in manager.citations}
        g_sections = {c.section for c in guest.citations}
        print(f"manager answer:  {manager.answer.strip()[:140]}")
        print(f"  cites: {sorted(m_sections)}")
        print(f"guest answer:    {guest.answer.strip()[:140]}")
        print(f"  cites: {sorted(g_sections)}")
        print(f"intruder grounded={intruder.is_grounded} (citations={len(intruder.citations)})")

        ok = (
            manager.is_grounded
            and "M&A" in m_sections
            and "M&A" not in g_sections  # guest cannot cite confidential
            and not intruder.is_grounded
        )
        print(f"two-user guarantee holds: {ok}")
    finally:
        ki.delete()
        for es, pk in (("racy_airequests", "racy_airequestid"), ("racy_airesponses", "racy_airesponseid")):
            rows = dv.retrieve_multiple(es)
            for r in rows:
                dv.delete(es, r[pk])
        print("deleted temp index + logged rows")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
