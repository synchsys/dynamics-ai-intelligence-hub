# Dataverse environment setup (service principal auth)

> One-time provisioning to connect this solution to a real Dataverse
> environment. These steps happen in **your** Azure / Power Platform tenant —
> they can't be scripted from this repo. Grounded in Microsoft Learn.
> Design of record: [ADR-0003](../decisions/ADR-0003-dataverse-auth.md)
> (service principal now → Managed Identity later).

## Goal

Produce four values for a local, git-ignored **`.env`** (see `.env.example`):

```dotenv
DATAVERSE_URL=https://<org>.crm.dynamics.com
AZURE_TENANT_ID=<directory (tenant) id>
AZURE_CLIENT_ID=<application (client) id>
AZURE_CLIENT_SECRET=<client secret value>
```

The client uses the OAuth 2.0 **client-credentials** flow (`azure-identity`
`ClientSecretCredential`); the token scope is `${DATAVERSE_URL}/.default`.

## Step 1 — Register an Entra app + client secret

[Entra admin center](https://entra.microsoft.com) → **Entra ID → App
registrations → New registration**.

1. Name it, e.g. `dynamics-ai-intelligence-hub-svc`.
2. Supported account types → **Accounts in this organizational directory only**.
   Redirect URI: leave blank (not needed for client-credentials).
3. **Register**. From **Overview**, copy **Directory (tenant) ID** →
   `AZURE_TENANT_ID` and **Application (client) ID** → `AZURE_CLIENT_ID`.
4. **Certificates & secrets → New client secret** → copy the **Value**
   immediately → `AZURE_CLIENT_SECRET`. (It's shown only once.)

## Step 2 — A Dataverse environment

[Power Platform admin center](https://admin.powerplatform.microsoft.com) →
**Environments**. Use an existing dev environment **with a Dataverse database**,
or create one (a **Developer**-type environment is free). Copy its **Environment
URL** (`https://<org>.crm.dynamics.com`) → `DATAVERSE_URL`.

## Step 3 — Custom security role + application user (least privilege)

The application user **must** be assigned a **custom** security role (a default
role can't be assigned to an application user), and per ADR-0003 it must never
be System Administrator.

1. In the environment → **Settings → Security → Security roles → New role**
   (e.g. `AI Service — least privilege`). Grant **Create / Read / Write** (and
   **Delete** only where required) on the tables it touches:
   - For the **#5** integration test: the standard **Contact** table (it
     creates and deletes a contact).
   - For **#19** later: the `racy_*` F1 tables, once story #6 creates them.

   *Quick dev shortcut:* the built-in **System Customizer** role covers Contact,
   but a purpose-built role is the governed, portfolio-correct choice.
2. **Settings → Users + permissions → Application users → New app user →
   + Add app** → select your registration → choose a **Business unit** → assign
   the custom role → **Create**.

## Step 4 — Wire it up and run the guarded integration tests

```bash
cp .env.example .env               # then fill in the four values
set -a && source .env && set +a    # export them into the shell...
export RUN_DATAVERSE_INTEGRATION=1 # ...the integration tests read os.environ, not .env

.venv/bin/python -m pytest tests/dataverse/test_dataverse_integration.py -v
```

A green run verifies the live Dataverse client (#5). **#19's** integration test
additionally needs the `racy_*` F1 tables (story #6), so it stays skipped until
that schema exists.

## Fast-path alternative (dev only)

```bash
pac admin create-service-principal --environment <environment-id>
```

This creates the Entra app **and** the Dataverse application user in one step —
but it grants a broad, Power-Platform-Administrator-style identity with no
least-privilege scoping. Fine for a throwaway spike; not the governed setup
ADR-0003 describes.

## Notes

- **Never commit secrets.** `.env` and `.claude/settings.local.json` are
  git-ignored. Production secrets move to Key Vault + Managed Identity in
  Epic 11 (#11.C).
- The application user draws from a **shared tenant request pool**; pace bulk
  backfills (see `docs/architecture/dynamics-dataverse.md` §9.3).

## References (Microsoft Learn)

- Register an app with Microsoft Entra ID / create a service principal.
- Power Platform admin center — manage application users.
- Use the Dataverse Web API (client-credentials, `$batch`).
