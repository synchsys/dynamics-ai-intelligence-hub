# Infrastructure (Bicep)

Infrastructure-as-Code for the Azure resources (#89). **Bicep** is the primary
tool ([ADR-0002](../docs/decisions/ADR-0002-iac-tool.md)); the `terraform/` tree
is a retired placeholder.

## Layout

```
bicep/
  main.bicep                 # Managed Identity + Key Vault (inline) + modules
                             # + data-plane role assignments
  modules/
    app-insights.bicep       # workspace-based App Insights (#29/#78/#82)
    storage.bicep            # Function App backing storage
    function-app.bicep       # Flex Consumption Function App (ADR-0004)
environments/
  dev.bicepparam             # rg-racy-ai-dev / uksouth parameter values
```

The Managed Identity (#127) and RBAC Key Vault (#34) are declared **inline** in
`main.bicep` rather than as modules: the role assignments need their resource
ids at the start of the deployment (a Bicep constraint on `guid()`-derived
role-assignment names), which module outputs don't satisfy.

`main.bicep` also grants the Managed Identity its data-plane roles on the
**pre-existing** Azure OpenAI + AI Search accounts and on the Key Vault
(Cognitive Services OpenAI User, Search Index Data Reader, Key Vault Secrets
User) — mirroring the roles created during the manual bootstrap.

## Use

```bash
# lint / compile
az bicep build --file bicep/main.bicep

# preview against the live environment (never skip before a real apply)
az deployment group what-if -g rg-racy-ai-dev \
  -f bicep/main.bicep -p environments/dev.bicepparam

# apply
az deployment group create -g rg-racy-ai-dev \
  -f bicep/main.bicep -p environments/dev.bicepparam
```

The dev resources were first stood up imperatively with `az`; this codifies them
so the environment is reproducible. Because ARM deployments are declarative and
idempotent, re-applying against the already-provisioned dev RG converges rather
than duplicates (role assignments use deterministic `guid()` names). Secrets are
never in these templates — the Function App resolves them at runtime from Key
Vault via the Managed Identity (`KEY_VAULT_URL` + `AZURE_CLIENT_ID`).

CI-driven deployment is #88 / #180.
