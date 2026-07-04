"""Live verification of the RAG-grounded CRM assistant (#65).

Wires a real RagAssistant (over a temp knowledge index) as the CRM assistant's
knowledge source, plus a Dataverse-backed CRM retriever over a seeded account.
Confirms: a knowledge question is answered from RAG with citations; a CRM-data
question (no knowledge match) falls back to Dataverse. Cleans up index, account,
and logged rows.

Run: python scripts/ai/verify_assistant_rag.py
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
    from ai.assistant import CrmAssistant, DataverseCrmRetriever, EntityView
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig
    from rag import KnowledgeIndex, RagAssistant, Retriever, SearchConfig, embed_chunks, ingest_markdown

    client = AIClient(AzureOpenAIConfig.from_env())
    dv = DataverseClient(DataverseConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    knowledge_src = "# DRS\n\nThe drag reduction system may be used only within designated activation zones."
    run = embed_chunks(client, ingest_markdown([("regs.md", knowledge_src, "public")]).chunks)
    account_id = dv.create("accounts", {"name": "Acme Corp", "address1_city": "Cork"})
    print(f"seeded {run.embedded} knowledge chunk(s) + 1 account")

    ok = False
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):
            time.sleep(2)
            if ki.keyword_search("*", top=1):
                break

        rag = RagAssistant(Retriever(ki, client), client)
        retriever = DataverseCrmRetriever(dv, [EntityView("accounts", "Accounts", ("name", "address1_city"))])
        assistant = CrmAssistant(
            client=client,
            retriever=retriever,
            knowledge=rag,
            roles=["employee"],
            logger=DataversePromptLogger(dv),
        )

        q1 = assistant.ask("When is a driver allowed to use DRS?")
        print(f"Q1 [{q1.grounded_in}] {q1.text.strip()[:120]}  citations={[c.source for c in q1.citations]}")

        q2 = assistant.ask("Which accounts are based in Cork?")
        print(f"Q2 [{q2.grounded_in}] {q2.text.strip()[:120]}")

        ok = (
            q1.grounded_in == "knowledge"
            and len(q1.citations) >= 1
            and q2.grounded_in == "crm"
            and "Acme" in q2.text
        )
        print(f"knowledge-then-crm routing holds: {ok}")
    finally:
        ki.delete()
        dv.delete("accounts", account_id)
        for es, pk in (("racy_airequests", "racy_airequestid"), ("racy_airesponses", "racy_airesponseid")):
            for r in dv.retrieve_multiple(es):
                dv.delete(es, r[pk])
        print("cleaned up index, account, logged rows")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
