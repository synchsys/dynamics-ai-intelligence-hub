// Key Vault + Managed Identity access for production secrets (#28).
//
// Provisions an RBAC-mode Key Vault and grants a principal (the Function App's
// managed identity) least-privilege read access to secrets. Deploy with:
//   az deployment group create -g <rg> -f infrastructure/bicep/keyvault.bicep \
//     -p name=<kv-name> secretsUserPrincipalId=<function-app-mi-object-id>

@description('Key Vault name (globally unique).')
param name string

@description('Location for the vault.')
param location string = resourceGroup().location

@description('Object id of the principal (Function App managed identity) granted secret read.')
param secretsUserPrincipalId string

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true // RBAC, not access policies — least-privilege via roles
    enableSoftDelete: true
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
  }
}

// Built-in "Key Vault Secrets User" — read secret values only (no management).
var secretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'

resource secretsUserGrant 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, secretsUserPrincipalId, secretsUserRoleId)
  scope: vault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', secretsUserRoleId)
    principalId: secretsUserPrincipalId
    principalType: 'ServicePrincipal'
  }
}

@description('Set this as KEY_VAULT_URL in the app settings so SecretResolver reads from the vault.')
output vaultUri string = vault.properties.vaultUri
