"""Live verification of the four core agents (#76).

Runs each agent against the real model (and Dataverse for the researcher):
planner produces steps, researcher uses a tool to find a fact, reviewer returns a
verdict, reporter writes a report. No writes; nothing to clean up.

Run: python scripts/agents/verify_core_agents.py
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env()
    from agents import Planner, Reporter, Researcher, Reviewer
    from ai import AIClient, AzureOpenAIConfig
    from ai.tools import ToolRegistry, record_count_tool
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig

    client = AIClient(AzureOpenAIConfig.from_env())
    dv = DataverseClient(DataverseConfig.from_env())

    plan = Planner().plan(client, "Report how many drivers finished the 2023 Singapore GP (session 9165)")
    print(f"planner -> {len(plan.steps)} step(s): {plan.steps}")

    registry = ToolRegistry()
    registry.register(record_count_tool(dv))
    findings = Researcher(registry=registry).research(
        client,
        "How many session result rows exist for session 9165? Use count_records with filter racy_sessionkey eq 9165.",
    )
    print(f"researcher -> {findings.strip()[:120]}")

    review = Reviewer().review(client, findings, goal="state the number of session-9165 results")
    print(f"reviewer -> approved={review.approved} summary={review.summary!r}")

    report = Reporter().report(client, f"Goal: session 9165 result count\nFindings: {findings}\nReview: {review.summary}")
    print(f"reporter -> {report.strip()[:120]}")

    ok = bool(plan.steps) and "19" in findings and isinstance(review.approved, bool) and len(report) > 0
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
