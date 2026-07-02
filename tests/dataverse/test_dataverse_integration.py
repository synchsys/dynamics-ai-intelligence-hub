"""Integration test against a real Dataverse environment.

Skipped unless ``RUN_DATAVERSE_INTEGRATION=1`` and the Dataverse env vars are
set (see ``.env.example``). Proves the client end to end by creating and then
deleting a ``contact`` (a built-in Dataverse table, so it does not depend on
Epic 3 custom entities).
"""

import os

import pytest

from dataverse import DataverseClient, DataverseConfig

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_DATAVERSE_INTEGRATION") != "1",
    reason="set RUN_DATAVERSE_INTEGRATION=1 (+ Dataverse env vars) to run",
)


def test_create_retrieve_delete_contact() -> None:
    with DataverseClient(DataverseConfig.from_env()) as client:
        record_id = client.create(
            "contacts", {"lastname": "IntegrationTest", "firstname": "Claude"}
        )
        try:
            fetched = client.retrieve("contacts", record_id, select=["lastname"])
            assert fetched["lastname"] == "IntegrationTest"
        finally:
            client.delete("contacts", record_id)
