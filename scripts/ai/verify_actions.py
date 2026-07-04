"""Live smoke test for guarded CRM action tools (#64).

Drives gpt-5-mini through the tool loop over live Dataverse: it looks up an
account, then requests a follow-up activity — which is *staged*, not executed.
The write only happens on explicit approval. Verifies the write is blocked
pre-approval and created post-approval, then cleans up.

Run: python scripts/ai/verify_actions.py
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
    from ai import AIClient, AzureOpenAIConfig, build_crm_tools
    from ai.tools import run_tools
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig

    dv = DataverseClient(DataverseConfig.from_env())
    account_id = dv.create("accounts", {"name": "Acme Corp", "address1_city": "Cork"})
    print(f"seeded account {account_id}")

    ok = True
    created_task_id: str | None = None
    try:
        tools = build_crm_tools(dv, dv)
        client = AIClient(AzureOpenAIConfig.from_env())

        result = run_tools(
            client,
            [
                {
                    "role": "user",
                    "content": (
                        "Look up the account named 'Acme Corp' in the accounts table "
                        "(filter name eq 'Acme Corp'), then create a follow-up activity "
                        "with subject 'Call Acme about renewal' regarding that account."
                    ),
                }
            ],
            tools.registry,
        )
        print(f"assistant: {result.content.strip()[:160]}")
        print(f"tool calls: {[(c.name, c.ok) for c in result.calls]}")

        pending = tools.broker.pending
        blocked = (
            len(dv.retrieve_multiple("tasks", filter="subject eq 'Call Acme about renewal'")) == 0
        )
        print(f"staged (awaiting approval): {[p.summary for p in pending]}")
        print(f"write blocked before approval: {blocked}")
        ok &= len(pending) == 1 and blocked

        # Human approves -> the write now executes.
        created_task_id = tools.broker.approve(pending[0].action_id)
        executed = (
            len(dv.retrieve_multiple("tasks", filter="subject eq 'Call Acme about renewal'")) == 1
        )
        print(f"write executed after approval: {executed}  (task {created_task_id})")
        ok &= executed
    finally:
        if created_task_id:
            dv.delete("tasks", created_task_id)
        dv.delete("accounts", account_id)
        print("cleaned up seeded account + task")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
