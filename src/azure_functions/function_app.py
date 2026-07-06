"""Azure Functions app — Python v2 programming model (#10).

The single serverless app that ingestion (#20), the GenAI assistant, and the
agent workflow will all extend. Bindings only — the logic lives in
``handlers.py`` so it can be unit-tested without the Functions host. Run locally
with ``func start`` and deploy per ``README`` / ADR-0004.
"""

import json
from datetime import UTC, datetime

import azure.functions as func

from azure_functions.handlers import health_payload, run_scheduled_ingestion

app = func.FunctionApp()


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP health check — returns 200 with a small status payload."""
    return func.HttpResponse(json.dumps(health_payload()), mimetype="application/json")


@app.timer_trigger(schedule="0 0 * * * *", arg_name="timer", run_on_startup=False)
def scheduled_ingestion(timer: func.TimerRequest) -> None:
    """Hourly timer — placeholder for OpenF1 ingestion (#20)."""
    run_scheduled_ingestion(datetime.now(UTC))
