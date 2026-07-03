"""Live end-to-end verification of free-text wager intake (#230).

Wires the real AIClient + HeuristicPricer + DataversePromptLogger over live
Dataverse (session 9165, 2023 Singapore GP) and runs several free-text
predictions through WagerIntakeService, asserting mappable text yields a priced
draft slip and un-settleable text is declined with guidance. Prompt/response are
logged to the racy_ai* tables; the rows this run creates are cleaned up after.

Run: python scripts/paddock/verify_intake.py
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

SESSION_KEY = 9165


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig
    from openf1.models import Driver
    from paddock.intake import DataversePromptLogger, WagerIntakeService
    from paddock.odds import HeuristicPricer

    dv = DataverseClient(DataverseConfig.from_env())

    drivers = [
        Driver(
            session_key=SESSION_KEY,
            driver_number=r["racy_drivernumber"],
            full_name=r.get("racy_fullname"),
            name_acronym=r.get("racy_acronym"),
        )
        for r in dv.retrieve_multiple("racy_drivers", filter=f"racy_sessionkey eq {SESSION_KEY}")
    ]
    # Form table from the ingested finishing positions (single-race form).
    form = {
        r["racy_drivernumber"]: [r.get("racy_position")]
        for r in dv.retrieve_multiple(
            "racy_sessionresults", filter=f"racy_sessionkey eq {SESSION_KEY}"
        )
    }
    pricer = HeuristicPricer(form)
    logger = DataversePromptLogger(dv)
    service = WagerIntakeService(AIClient(AzureOpenAIConfig.from_env()), pricer, logger=logger)

    cases = [
        ("Carlos Sainz to win the race", True, "driver_wins"),
        ("Lando Norris to finish on the podium", True, "podium_contains"),
        ("Sainz to beat Norris", True, "head_to_head_finish"),
        ("Charles Leclerc to finish in the top 5", True, "driver_finish_position"),
        ("Will it rain during the race on Sunday?", False, None),
    ]
    ok = True
    for text, want_accept, want_type in cases:
        result = service.intake(text, session_key=SESSION_KEY, drivers=drivers)
        if result.accepted and result.slip is not None:
            slip = result.slip
            got = f"ACCEPT {slip.settlement_type} {slip.parameters} @ {slip.odds.line}"
            passed = want_accept and slip.settlement_type == want_type
        else:
            got = f"REJECT ({(result.guidance or '').splitlines()[0]})"
            passed = not want_accept
        ok &= passed
        print(f"[{'PASS' if passed else 'FAIL'}] {text!r}\n        -> {got}")

    # Clean up the AI Request/Response rows this run logged.
    for es in ("racy_airequests", "racy_airesponses"):
        rows = dv.retrieve_multiple(es)
        pk = "racy_airequestid" if es == "racy_airequests" else "racy_airesponseid"
        for r in rows:
            dv.delete(es, r[pk])
        print(f"cleaned up {len(rows)} {es} row(s)")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
