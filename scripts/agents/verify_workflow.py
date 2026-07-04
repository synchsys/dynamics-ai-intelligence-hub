"""Live verification of the multi-agent workflow (#26 / #124).

Seeds a temp knowledge index, wires a RAG-backed researcher (search_knowledge +
Dataverse read + guarded write), and runs the full planner → researcher →
reviewer → reporter workflow on a sample goal against Azure OpenAI + Azure AI
Search + Dataverse. Prints the trace and report; any write stays staged pending
approval. Deletes the temp index afterwards.

Run: python scripts/agents/verify_workflow.py
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


KNOWLEDGE = (
    "# DRS\n\nThe drag reduction system may be used only within designated activation zones, "
    "and only when a driver is within one second of the car ahead."
)


def main() -> int:
    _load_env()
    from agents import MultiAgentWorkflow, Researcher, knowledge_search_tool
    from ai import AIClient, AzureOpenAIConfig, build_crm_tools
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig
    from rag import (
        KnowledgeIndex,
        RagAssistant,
        Retriever,
        SearchConfig,
        embed_chunks,
        ingest_markdown,
    )

    client = AIClient(AzureOpenAIConfig.from_env())
    dv = DataverseClient(DataverseConfig.from_env())
    config = dataclasses.replace(SearchConfig.from_env(), index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    run = embed_chunks(client, ingest_markdown([("regs.md", KNOWLEDGE, "public")]).chunks)

    ok = False
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)
        for _ in range(15):
            time.sleep(2)
            if ki.keyword_search("*", top=1):
                break

        rag = RagAssistant(Retriever(ki, client), client)
        tools = build_crm_tools(dv, dv)  # lookup_records + guarded create_followup_activity
        tools.registry.register(knowledge_search_tool(rag, roles=["employee"]))
        workflow = MultiAgentWorkflow(
            client,
            researcher=Researcher(registry=tools.registry),
            broker=tools.broker,
            on_event=lambda e: print(f"  · {e.step} [{e.agent}] {e.summary}"),
        )

        result = workflow.run(
            "Explain when DRS may be used, and draft a follow-up task to brief the team."
        )
        print("\n--- report ---")
        print(result.report.strip()[:400])
        print(f"\npending writes (blocked, awaiting approval): {len(result.pending_writes)}")

        agents_seen = {e.agent for e in result.trace}
        ok = (
            bool(result.plan.steps)
            and len(result.report) > 0
            and agents_seen == {"planner", "researcher", "reviewer", "reporter"}
        )
        print(
            f"all four agents ran: {agents_seen == {'planner', 'researcher', 'reviewer', 'reporter'}}"
        )
    finally:
        ki.delete()
        # Only clean up tasks if a staged write was ever approved (it isn't here).
        print("deleted temp index")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
