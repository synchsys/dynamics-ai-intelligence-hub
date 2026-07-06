# ADR-0003: Dataverse authentication approach

## Status

Accepted

## Context

The Python Dataverse client (`src/dataverse`, story #5) must authenticate to
the Dataverse Web API to perform CRUD, upsert and `$batch` operations. Options
for a server-to-server (no interactive user) integration:

1. **Service principal via client-credentials** — an Entra ID app registration
   with a client secret, added as a Dataverse *application user*.
2. **Managed Identity** — an Azure-managed identity assigned to the hosting
   compute (Functions/App Service), with no secret to store.
3. **Interactive / delegated user auth** — not appropriate for automated
   ingestion and logging pipelines.

Local development has no Azure-managed compute, so Managed Identity is not
available there. Production (Epic 11) will run on Azure and should avoid stored
secrets.

## Decision

Use the **client-credentials flow with a service principal now**, via
`azure-identity`'s `ClientSecretCredential`. Credentials are loaded from the
environment (`.env` locally, CI secrets / Key Vault in deployment) and never
committed.

The credential is **injected** into `TokenProvider`, so migrating to Managed
Identity later is a one-line change — swap `ClientSecretCredential` for
`ManagedIdentityCredential` (or `DefaultAzureCredential`, which resolves to a
managed identity in Azure and to environment/developer credentials locally) with
no change to `DataverseClient`.

Token scope is `${DATAVERSE_URL}/.default`.

## Consequences

- **Positive:** works locally and in CI immediately; standard Microsoft-aligned
  approach; clean, secret-free path to Managed Identity in production.
- **Negative:** a client secret exists and must be rotated and protected until
  the Managed Identity migration lands.

## Follow-up

- Epic 11 (#11.C): move production secrets to Key Vault + Managed Identity;
  this ADR may be superseded/updated then.
- The application user must be granted a least-privilege security role in the
  Dataverse environment.

## Update — production identity (Epic 11 / #28)

The Managed Identity migration path is now implemented as a shared capability:

- **`shared.credentials.azure_credential()`** returns `DefaultAzureCredential` —
  a **managed identity** when deployed to Azure, and dev credentials (the
  service-principal env vars, or `az login`) locally. Services obtain their Entra
  credential from this rather than constructing a `ClientSecretCredential`, so
  **no client secret appears in production code or config**.
- **`shared.credentials.SecretResolver`** reads any residual secret (e.g. the
  Azure AI Search admin key) from **Key Vault** when `KEY_VAULT_URL` is set, and
  from the environment (`.env`) in local dev. Key Vault + the identity grant are
  provisioned by `infrastructure/bicep/keyvault.bicep`.

**Net:** production authenticates to Dataverse (and Azure OpenAI) via Managed
Identity with no stored client secret; the service-principal client secret is a
**local-development** convenience only, resolved through the same abstraction.
See `docs/security/secrets-and-identity.md`.
