# Secrets & identity

How the solution authenticates and where secrets live (#28, Epic 11). The rule:
**local dev uses `.env`; production uses Key Vault + Managed Identity, with no
secret in source or app config.**

## Identity

`shared.credentials.azure_credential()` returns `DefaultAzureCredential`, which
resolves to:

- a **Managed Identity** when running in Azure (Functions, App Service) — no
  secret involved; the platform issues tokens to the identity, and
- **developer credentials** locally — the service-principal env vars
  (`AZURE_TENANT_ID`/`AZURE_CLIENT_ID`/`AZURE_CLIENT_SECRET`) or `az login`.

Services use this instead of a hard-coded `ClientSecretCredential`, so the same
code runs secret-free in production and with a dev SP locally.

## Secrets

`shared.credentials.SecretResolver.resolve(name)`:

- **Production** — when `KEY_VAULT_URL` is set, reads from **Key Vault** (via the
  managed identity), mapping `A_B` → the `A-B` secret name.
- **Dev** — reads from the environment (`.env`).

The only secret that must live in Key Vault is the **Azure AI Search admin key**
(Search has no data-plane Managed Identity in this setup); Dataverse and Azure
OpenAI use Managed Identity directly, so they need no stored secret in production.

## Provisioning

`infrastructure/bicep/keyvault.bicep` creates an RBAC-mode Key Vault and grants
the Function App's managed identity the **Key Vault Secrets User** role
(least-privilege, read-only). Its `vaultUri` output becomes the `KEY_VAULT_URL`
app setting.

```bash
az deployment group create -g rg-racy-ai-dev -f infrastructure/bicep/keyvault.bicep \
  -p name=racy-kv-dev secretsUserPrincipalId=<function-app-mi-object-id>
# then, one-off, load the Search key:
az keyvault secret set --vault-name racy-kv-dev --name AZURE-SEARCH-KEY --value <key>
```

## Local vs production

| | Dev (local) | Production (Azure) |
|-|-------------|--------------------|
| Entra credential | SP env vars / `az login` | **Managed Identity** |
| Dataverse / Azure OpenAI | SP client secret in `.env` | **Managed Identity** (no secret) |
| Search admin key | `.env` | **Key Vault** reference |
| Secret store | `.env` (git-ignored) | **Key Vault** |

## Standing action

The dev secrets currently in `.env` (Dataverse client secret, Search admin key)
were exposed during development and the repo is public — **rotate them** and, for
anything beyond local dev, move to the Key Vault + Managed Identity path above.
