#!/usr/bin/env python3
"""Create the `racy_` OpenF1 tables in Dataverse via the Web API metadata endpoints.

Provisions the custom publisher (prefix ``racy``) and the core F1 settlement
tables — sessions, drivers, session_result, starting_grid, laps, pit — with
their columns and idempotent **alternate keys**. Logical/collection names match
``src/openf1/mapping.py`` so persistence (#19) writes upsert cleanly.

Auth reuses the project's `.env` (client-credentials via ``azure-identity``),
exactly like the Dataverse integration test.

USAGE
-----
    set -a && source .env && set +a
    python scripts/dataverse/create_racy_schema.py            # DRY RUN (prints plan)
    python scripts/dataverse/create_racy_schema.py --apply    # actually create

Idempotent: existing publisher/tables/columns/keys are detected and skipped, so
it's safe to re-run. Alternate-key creation is processed asynchronously by the
platform. Scope: the six int-keyed settlement tables (clean alt keys). The
datetime-keyed tables (position, weather, stints) can be added the same way
once you decide their key strategy (DateTime alternate keys need care).

NOTE: this is a pragmatic provisioning script; proper solution packaging /
managed export is story #233. Review before running against a shared env.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field

import httpx
from azure.identity import ClientSecretCredential

LANG = 1033
PREFIX = "racy"
PUBLISHER_UNIQUE = "racypublisher"
PUBLISHER_OPTVALUE_PREFIX = 72000  # option-value prefix for the publisher (10000–99999)


# --- schema definition (mirrors src/openf1/mapping.py) ----------------------


@dataclass
class Column:
    schema: str  # e.g. racy_SessionKey  (logical name -> racy_sessionkey)
    kind: str  # int | decimal | bool | string | datetime
    display: str


@dataclass
class Table:
    schema: str  # racy_Session   (logical -> racy_session)
    display: str
    display_plural: str
    entity_set: str  # collection name used by the data API (matches mapping.py)
    columns: list[Column]
    alt_key: list[str]  # column schema names forming the alternate key
    primary_name: str = "racy_Name"
    ownership: str = "OrganizationOwned"  # or "UserOwned" for player-scoped tables


SCHEMA: list[Table] = [
    Table(
        "racy_Session",
        "Racy Session",
        "Racy Sessions",
        "racy_sessions",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_MeetingKey", "int", "Meeting Key"),
            Column("racy_SessionName", "string", "Session Name"),
            Column("racy_SessionType", "string", "Session Type"),
            Column("racy_DateStart", "datetime", "Date Start"),
            Column("racy_DateEnd", "datetime", "Date End"),
            Column("racy_Year", "int", "Year"),
        ],
        alt_key=["racy_SessionKey"],
    ),
    Table(
        "racy_Driver",
        "Racy Driver",
        "Racy Drivers",
        "racy_drivers",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_DriverNumber", "int", "Driver Number"),
            Column("racy_FullName", "string", "Full Name"),
            Column("racy_Acronym", "string", "Acronym"),
            Column("racy_TeamName", "string", "Team Name"),
        ],
        alt_key=["racy_SessionKey", "racy_DriverNumber"],
    ),
    Table(
        "racy_SessionResult",
        "Racy Session Result",
        "Racy Session Results",
        "racy_sessionresults",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_DriverNumber", "int", "Driver Number"),
            Column("racy_Position", "int", "Position"),
            Column("racy_Dnf", "bool", "DNF"),
            Column("racy_Dns", "bool", "DNS"),
            Column("racy_Dsq", "bool", "DSQ"),
            Column("racy_GapToLeader", "decimal", "Gap To Leader"),
            Column("racy_NumberOfLaps", "int", "Number Of Laps"),
        ],
        alt_key=["racy_SessionKey", "racy_DriverNumber"],
    ),
    Table(
        "racy_StartingGrid",
        "Racy Starting Grid",
        "Racy Starting Grids",
        "racy_startinggrids",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_DriverNumber", "int", "Driver Number"),
            Column("racy_GridPosition", "int", "Grid Position"),
        ],
        alt_key=["racy_SessionKey", "racy_DriverNumber"],
    ),
    Table(
        "racy_Lap",
        "Racy Lap",
        "Racy Laps",
        "racy_laps",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_DriverNumber", "int", "Driver Number"),
            Column("racy_LapNumber", "int", "Lap Number"),
            Column("racy_LapDuration", "decimal", "Lap Duration"),
        ],
        alt_key=["racy_SessionKey", "racy_DriverNumber", "racy_LapNumber"],
    ),
    Table(
        "racy_PitStop",
        "Racy Pit Stop",
        "Racy Pit Stops",
        "racy_pitstops",
        [
            Column("racy_SessionKey", "int", "Session Key"),
            Column("racy_DriverNumber", "int", "Driver Number"),
            Column("racy_LapNumber", "int", "Lap Number"),
            Column("racy_PitDuration", "decimal", "Pit Duration"),
        ],
        alt_key=["racy_SessionKey", "racy_DriverNumber", "racy_LapNumber"],
    ),
]


# --- Paddock Club wager tables (story #225) ---------------------------------
# Flat tables (scalar columns + alternate keys) so the wager loop can persist.
# Cross-table references are carried as code/key columns (racy_playercode,
# racy_sessionkey, ...). Native lookups, the Wallet-balance rollup, choice
# columns and the Wager-Slip BPF are model-driven-app enrichment added with the
# app stories (#11/#12) — not required for the settlement engine to read/write.
# Player / Wallet / Wager Slip are UserOwned per the security model (#13, tech
# doc §5); reference/event tables are OrganizationOwned.

PADDOCK: list[Table] = [
    Table("racy_League", "Racy League", "Racy Leagues", "racy_leagues",
          [Column("racy_LeagueCode", "string", "League Code"),
           Column("racy_Commissioner", "string", "Commissioner")],
          alt_key=["racy_LeagueCode"]),
    Table("racy_Season", "Racy Season", "Racy Seasons", "racy_seasons",
          [Column("racy_SeasonCode", "string", "Season Code"),
           Column("racy_LeagueCode", "string", "League Code"),
           Column("racy_Year", "int", "Year")],
          alt_key=["racy_SeasonCode"]),
    Table("racy_RaceEvent", "Racy Race Event", "Racy Race Events", "racy_raceevents",
          [Column("racy_SessionKey", "int", "Session Key"),
           Column("racy_MeetingKey", "int", "Meeting Key"),
           Column("racy_SeasonCode", "string", "Season Code"),
           Column("racy_Status", "string", "Status"),  # Open / Locked / Settled
           Column("racy_LockDeadline", "datetime", "Lock Deadline")],
          alt_key=["racy_SessionKey"]),
    Table("racy_Player", "Racy Player", "Racy Players", "racy_players",
          [Column("racy_PlayerCode", "string", "Player Code"),
           Column("racy_DisplayName", "string", "Display Name"),
           Column("racy_SystemUserId", "string", "System User Id")],
          alt_key=["racy_PlayerCode"], ownership="UserOwned"),
    Table("racy_Wallet", "Racy Wallet", "Racy Wallets", "racy_wallets",
          [Column("racy_PlayerCode", "string", "Player Code"),
           Column("racy_Balance", "decimal", "Balance"),
           Column("racy_StartingStake", "decimal", "Starting Stake")],
          alt_key=["racy_PlayerCode"], ownership="UserOwned"),
    Table("racy_SettlementType", "Racy Settlement Type", "Racy Settlement Types",
          "racy_settlementtypes",
          [Column("racy_Code", "string", "Code"),
           Column("racy_Label", "string", "Label"),
           Column("racy_Parameters", "string", "Parameters"),
           Column("racy_Tier", "string", "Tier")],
          alt_key=["racy_Code"]),
    Table("racy_WagerSlip", "Racy Wager Slip", "Racy Wager Slips", "racy_wagerslips",
          [Column("racy_SlipCode", "string", "Slip Code"),
           Column("racy_SessionKey", "int", "Session Key"),
           Column("racy_PlayerCode", "string", "Player Code"),
           Column("racy_SettlementTypeCode", "string", "Settlement Type Code"),
           Column("racy_RestatedText", "string", "Restated Prediction"),
           Column("racy_Parameters", "memo", "Parameters (JSON)"),
           Column("racy_FrozenOdds", "decimal", "Frozen Odds"),
           Column("racy_Stake", "decimal", "Stake"),
           Column("racy_Status", "string", "Status")],  # Draft/Locked/Won/Lost/Void
          alt_key=["racy_SlipCode"], ownership="UserOwned"),
    Table("racy_Settlement", "Racy Settlement", "Racy Settlements", "racy_settlements",
          [Column("racy_SlipCode", "string", "Slip Code"),
           Column("racy_Result", "string", "Result"),  # Won/Lost/Void
           Column("racy_Payout", "decimal", "Payout"),
           Column("racy_GradedOn", "datetime", "Graded On"),
           Column("racy_DataSnapshot", "string", "Data Snapshot Ref")],
          alt_key=["racy_SlipCode"]),
]


# --- AI governance tables (story #230, Epic 8 prompt/response logging) -------
# Every LLM call in a feature epic logs its prompt + response here (governance is
# implemented in the feature epic, not deferred to Epic 11). Request and response
# are paired by racy_RequestCode; the response carries the parsed decision so the
# intake pipeline's behaviour is auditable end to end.

AI: list[Table] = [
    Table("racy_AiRequest", "Racy AI Request", "Racy AI Requests", "racy_airequests",
          [Column("racy_RequestCode", "string", "Request Code"),
           Column("racy_Purpose", "string", "Purpose"),  # e.g. wager-intake
           Column("racy_Model", "string", "Model"),
           Column("racy_Prompt", "memo", "Prompt")],
          alt_key=["racy_RequestCode"]),
    Table("racy_AiResponse", "Racy AI Response", "Racy AI Responses", "racy_airesponses",
          [Column("racy_RequestCode", "string", "Request Code"),
           Column("racy_RawOutput", "memo", "Raw Output"),
           Column("racy_Decision", "string", "Decision"),  # propose / decline / error
           Column("racy_SettlementTypeCode", "string", "Settlement Type Code"),
           Column("racy_Ok", "bool", "Ok"),
           Column("racy_Error", "memo", "Error")],
          alt_key=["racy_RequestCode"]),
]


# --- helpers ----------------------------------------------------------------


def _label(text: str) -> dict:
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [
            {
                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                "Label": text,
                "LanguageCode": LANG,
            }
        ],
    }


def _attr_payload(col: Column, *, is_primary: bool = False) -> dict:
    common = {
        "SchemaName": col.schema,
        "RequiredLevel": {"Value": "None"},
        "DisplayName": _label(col.display),
    }
    if is_primary or col.kind == "string":
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            **common,
            "MaxLength": 250,
            "FormatName": {"Value": "Text"},
            **({"IsPrimaryName": True} if is_primary else {}),
        }
    if col.kind == "int":
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
            **common,
            "Format": "None",
            "MinValue": -2147483648,
            "MaxValue": 2147483647,
        }
    if col.kind == "decimal":
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
            **common,
            "Precision": 3,
            "MinValue": -100000.0,
            "MaxValue": 1000000.0,
        }
    if col.kind == "bool":
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
            **common,
            "OptionSet": {
                "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
                "TrueOption": {"Value": 1, "Label": _label("Yes")},
                "FalseOption": {"Value": 0, "Label": _label("No")},
            },
        }
    if col.kind == "datetime":
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
            **common,
            "Format": "DateAndTime",
        }
    if col.kind == "memo":  # multi-line text, e.g. JSON parameters
        return {
            "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
            **common,
            "MaxLength": 4000,
            "Format": "Text",
        }
    raise ValueError(f"unknown column kind: {col.kind}")


def _logical(schema_name: str) -> str:
    return schema_name.lower()


@dataclass
class Client:
    http: httpx.Client
    apply: bool
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    def _get_json(self, path: str) -> dict:
        r = self.http.get(path)
        r.raise_for_status()
        return r.json()

    def exists(self, path: str) -> bool:
        r = self.http.get(path)
        if r.status_code == 200:
            return True
        if r.status_code == 404:
            return False
        r.raise_for_status()
        return False

    def post(self, path: str, body: dict, *, label: str) -> None:
        if not self.apply:
            print(f"  [dry-run] would create {label}")
            self.created.append(label)
            return
        r = self.http.post(path, json=body)
        if r.status_code >= 300:
            raise RuntimeError(f"create {label} failed: HTTP {r.status_code}\n{r.text[:600]}")
        print(f"  created {label}")
        self.created.append(label)


def ensure_publisher(c: Client) -> None:
    found = c._get_json(
        f"/publishers?$filter=customizationprefix eq '{PREFIX}'&$select=publisherid"
    )
    if found.get("value"):
        print(f"publisher '{PREFIX}' exists — skip")
        c.skipped.append(f"publisher:{PREFIX}")
        return
    c.post(
        "/publishers",
        {
            "uniquename": PUBLISHER_UNIQUE,
            "friendlyname": "Racy",
            "customizationprefix": PREFIX,
            "customizationoptionvalueprefix": PUBLISHER_OPTVALUE_PREFIX,
        },
        label=f"publisher '{PREFIX}'",
    )


def ensure_table(c: Client, t: Table) -> None:
    logical = _logical(t.schema)
    if c.exists(f"/EntityDefinitions(LogicalName='{logical}')?$select=LogicalName"):
        print(f"table {logical} exists — skip create")
        c.skipped.append(f"table:{logical}")
    else:
        body = {
            "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
            "SchemaName": t.schema,
            "DisplayName": _label(t.display),
            "DisplayCollectionName": _label(t.display_plural),
            "EntitySetName": t.entity_set,
            "OwnershipType": t.ownership,
            "HasActivities": False,
            "HasNotes": False,
            "Attributes": [
                _attr_payload(Column(t.primary_name, "string", "Name"), is_primary=True)
            ],
        }
        c.post("/EntityDefinitions", body, label=f"table {logical}")

    # columns
    for col in t.columns:
        col_logical = _logical(col.schema)
        if c.exists(
            f"/EntityDefinitions(LogicalName='{logical}')/Attributes(LogicalName='{col_logical}')?$select=LogicalName"
        ):
            c.skipped.append(f"column:{logical}.{col_logical}")
            continue
        c.post(
            f"/EntityDefinitions(LogicalName='{logical}')/Attributes",
            _attr_payload(col),
            label=f"column {logical}.{col_logical}",
        )

    # alternate key
    key_schema = f"{t.schema}_AK"
    key_logical = _logical(key_schema)
    keys = (
        c._get_json(f"/EntityDefinitions(LogicalName='{logical}')/Keys?$select=SchemaName")
        if c.apply or c.exists(f"/EntityDefinitions(LogicalName='{logical}')?$select=LogicalName")
        else {"value": []}
    )
    if any(k.get("SchemaName") == key_schema for k in keys.get("value", [])):
        c.skipped.append(f"altkey:{logical}")
    else:
        c.post(
            f"/EntityDefinitions(LogicalName='{logical}')/Keys",
            {
                "@odata.type": "Microsoft.Dynamics.CRM.EntityKeyMetadata",
                "SchemaName": key_schema,
                "DisplayName": _label(f"{t.display} Key"),
                "KeyAttributes": [_logical(s) for s in t.alt_key],
            },
            label=f"alternate key {key_logical} ({', '.join(_logical(s) for s in t.alt_key)})",
        )


def build_client(apply: bool) -> Client:
    url = os.environ.get("DATAVERSE_URL", "").rstrip("/")
    tenant = os.environ.get("AZURE_TENANT_ID", "")
    client_id = os.environ.get("AZURE_CLIENT_ID", "")
    secret = os.environ.get("AZURE_CLIENT_SECRET", "")
    if not all([url, tenant, client_id, secret]):
        sys.exit(
            "Missing DATAVERSE_URL / AZURE_* env vars — `set -a && source .env && set +a` first."
        )
    token = ClientSecretCredential(tenant, client_id, secret).get_token(f"{url}/.default").token
    http = httpx.Client(
        base_url=f"{url}/api/data/v9.2",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Consistency": "Strong",
        },
        timeout=60.0,
    )
    return Client(http=http, apply=apply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create racy_ Dataverse schema (OpenF1 + Paddock).")
    parser.add_argument("--apply", action="store_true", help="actually create (default: dry run)")
    parser.add_argument(
        "--only",
        choices=["f1", "paddock", "ai", "all"],
        default="all",
        help="which table set to provision (default: all)",
    )
    args = parser.parse_args()

    tables: list[Table] = []
    if args.only in ("f1", "all"):
        tables += SCHEMA
    if args.only in ("paddock", "all"):
        tables += PADDOCK
    if args.only in ("ai", "all"):
        tables += AI

    c = build_client(args.apply)
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== racy_ schema provisioning ({mode}, set={args.only}) ===")
    ensure_publisher(c)
    for table in tables:
        print(f"table: {_logical(table.schema)}")
        ensure_table(c, table)
    print(
        f"\n{mode} complete — created/planned: {len(c.created)}, skipped(existing): {len(c.skipped)}"
    )
    if not args.apply:
        print("Re-run with --apply to create these in Dataverse.")


if __name__ == "__main__":
    main()
