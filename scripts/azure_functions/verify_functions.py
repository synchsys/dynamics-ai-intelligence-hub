"""Live smoke test for the deployed Azure Functions app (#10 / #20).

Hits the deployed HTTP health endpoint and asserts a 200 + the expected status
payload — the deploy-time proof that the app started, imported the src/ package
tree, and is serving. Point it at the function app:

    FUNCTION_APP_URL=https://racy-func-dev.azurewebsites.net python \
        scripts/azure_functions/verify_functions.py

(Defaults to https://racy-func-dev.azurewebsites.net if FUNCTION_APP_URL unset.)
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import httpx  # noqa: E402

DEFAULT_URL = "https://racy-func-dev.azurewebsites.net"


def main() -> int:
    base = os.environ.get("FUNCTION_APP_URL", DEFAULT_URL).rstrip("/")
    url = f"{base}/api/health"
    print(f"GET {url}")

    response = httpx.get(url, timeout=30.0)
    print(f"status={response.status_code}  body={response.text}")
    response.raise_for_status()

    payload = response.json()
    assert payload.get("status") == "ok", f"unexpected health payload: {payload}"
    print(f"OK — {payload['service']} v{payload['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
