"""Live smoke test for the function-calling tool layer (#61).

Registers the two sample tools (pure ``add`` + a real Dataverse ``count_records``)
and drives ``gpt-5-mini`` through the tool loop, asserting it selects the right
tool with valid arguments and reaches the right answer.
Run: python scripts/ai/verify_tools.py
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
    from ai import AIClient, AzureOpenAIConfig
    from ai.tools import ToolRegistry, add_tool, record_count_tool, run_tools
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig

    dv = DataverseClient(DataverseConfig.from_env())
    registry = ToolRegistry()
    registry.register(add_tool())
    registry.register(record_count_tool(dv))
    client = AIClient(AzureOpenAIConfig.from_env())

    ok = True

    r1 = run_tools(client, [{"role": "user", "content": "What is 21 + 21? Use the add tool."}], registry)
    called_add = any(c.name == "add" and c.ok for c in r1.calls)
    print(f"add    -> {r1.content.strip()!r}  (tool used: {called_add})")
    ok &= called_add and "42" in r1.content

    r2 = run_tools(
        client,
        [{"role": "user", "content": "How many rows are in racy_sessionresults for session 9165? "
          "Use count_records with OData filter 'racy_sessionkey eq 9165'."}],
        registry,
    )
    counted = next((c for c in r2.calls if c.name == "count_records" and c.ok), None)
    print(f"count  -> {r2.content.strip()[:120]!r}  (tool used: {counted is not None})")
    ok &= counted is not None and "19" in r2.content

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
