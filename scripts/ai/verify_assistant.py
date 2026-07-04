"""Live smoke test for the CRM assistant (#63).

Seeds a few native Dataverse accounts, points the assistant at them, and checks
it answers a grounded question from that data and declines gracefully on an
unknown. Prompt/response are logged to the racy_ai* tables. All seeded accounts
and logged rows are cleaned up afterwards.

Run: python scripts/ai/verify_assistant.py
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
    from ai import AIClient, AzureOpenAIConfig, DataversePromptLogger
    from ai.assistant import CrmAssistant, DataverseCrmRetriever, EntityView
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig

    dv = DataverseClient(DataverseConfig.from_env())
    seeded = [
        dv.create("accounts", {"name": "Acme Corp", "address1_city": "Cork"}),
        dv.create("accounts", {"name": "Globex", "address1_city": "Dublin"}),
        dv.create("accounts", {"name": "Initech", "address1_city": "Cork"}),
    ]
    print(f"seeded {len(seeded)} accounts")

    ok = True
    try:
        retriever = DataverseCrmRetriever(
            dv, [EntityView("accounts", "Accounts", ("name", "address1_city"))]
        )
        assistant = CrmAssistant(
            client=AIClient(AzureOpenAIConfig.from_env()),
            retriever=retriever,
            logger=DataversePromptLogger(dv),
        )

        grounded = assistant.ask("Which accounts are based in Cork?")
        print(f"Q1 -> {grounded.text.strip()[:200]}")
        grounded_ok = "Acme" in grounded.text and "Initech" in grounded.text
        ok &= grounded_ok

        unknown = assistant.ask("What is our Q4 revenue forecast?")
        print(f"Q2 -> {unknown.text.strip()[:200]}")
        # Should not fabricate a figure; expect a graceful "don't have" style answer.
        declined = any(
            p in unknown.text.lower() for p in ("don't", "do not", "no ", "not have", "unable")
        )
        ok &= declined

        print(f"grounded={grounded_ok}  declined_unknown={declined}")
    finally:
        for es, rows_key in (
            ("racy_airequests", "racy_airequestid"),
            ("racy_airesponses", "racy_airesponseid"),
        ):
            rows = dv.retrieve_multiple(es)
            for r in rows:
                dv.delete(es, r[rows_key])
            print(f"cleaned up {len(rows)} {es} row(s)")
        for aid in seeded:
            dv.delete("accounts", aid)
        print(f"cleaned up {len(seeded)} accounts")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
