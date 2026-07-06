"""Azure Functions app — Python v2 programming model (#10).

The single serverless app that ingestion (#20), the GenAI assistant, and the
agent workflow will all extend. Bindings only — the logic lives in
``handlers.py`` so it can be unit-tested without the Functions host. Run locally
with ``func start`` and deploy per ``README`` / ADR-0004.
"""

import json
from datetime import UTC, datetime

import azure.functions as func

from azure_functions.handlers import health_payload
from azure_functions.inference import handle_predict, load_served_model
from azure_functions.ingestion import ingest_from_env

app = func.FunctionApp()


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP health check — returns 200 with a small status payload."""
    return func.HttpResponse(json.dumps(health_payload()), mimetype="application/json")


@app.route(route="predict", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def predict(req: func.HttpRequest) -> func.HttpResponse:
    """HTTP inference — predict lap time from a lap-feature record (#57)."""
    status, payload = handle_predict(req.get_json(), model=load_served_model())
    return func.HttpResponse(json.dumps(payload), status_code=status, mimetype="application/json")


@app.timer_trigger(schedule="0 0 * * * *", arg_name="timer", run_on_startup=False)
def scheduled_ingestion(timer: func.TimerRequest) -> None:
    """Hourly timer — runs the OpenF1 → Dataverse pipeline (#20)."""
    ingest_from_env(datetime.now(UTC))
