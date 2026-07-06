// Dynamics AI Intelligence Hub — dev infrastructure (#89, ADR-0002).
//
// Codifies the resources first stood up by hand in rg-racy-ai-dev: App Insights,
// Key Vault, a user-assigned Managed Identity, storage, and a Flex Consumption
// Function App (ADR-0004), plus the data-plane role assignments that let the
// identity reach the pre-existing Azure OpenAI + AI Search accounts and the vault.
//
// The Managed Identity and Key Vault are top-level resources here (not modules)
// so their resource ids are known at the start of the deployment — a hard
// requirement for the deterministic guid() role-assignment names below.
//
// Deploy:  az deployment group create -g rg-racy-ai-dev \
//            -f infrastructure/bicep/main.bicep \
//            -p infrastructure/environments/dev.bicepparam
// Preview: add `--what-if` before applying against a live environment.

@description('Location for new resources.')
param location string = resourceGroup().location

@description('Application Insights component name.')
param appInsightsName string

@description('Key Vault name (globally unique).')
param keyVaultName string

@description('User-assigned Managed Identity name.')
param managedIdentityName string

@description('Storage account name (globally unique, 3-24 lowercase alphanumerics).')
param storageAccountName string

@description('Function App name (globally unique).')
param functionAppName string

@description('Name of the pre-existing Azure OpenAI (Cognitive Services) account.')
param openAiAccountName string

@description('Name of the pre-existing Azure AI Search service.')
param searchServiceName string

@description('Non-secret app settings for the Function App (endpoints, deployment names, etc.).')
param functionAppSettings array = []

// Built-in role definition ids (confirmed from the live dev grants).
var roles = {
  openAiUser: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
  searchIndexDataReader: '1407120a-92aa-4202-b7e9-c0e197c71c8f' // Search Index Data Reader
  keyVaultSecretsUser: '4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true // least-privilege via roles, not access policies
    enableSoftDelete: true
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
  }
}

module appInsights 'modules/app-insights.bicep' = {
  name: 'appInsights'
  params: { name: appInsightsName, location: location }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: { name: storageAccountName, location: location }
}

module functionApp 'modules/function-app.bicep' = {
  name: 'functionApp'
  params: {
    name: functionAppName
    location: location
    managedIdentityId: identity.id
    storageAccountName: storage.outputs.name
    appInsightsConnectionString: appInsights.outputs.connectionString
    appSettings: functionAppSettings
  }
}

// --- data-plane role assignments for the Managed Identity ------------------
// guid() names use resource ids (start-known); principalId is a runtime value,
// which is allowed for the principalId *property* (just not for the name).

resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: openAiAccountName
}

resource search 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: searchServiceName
}

resource openAiGrant 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openAi.id, identity.id, roles.openAiUser)
  scope: openAi
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.openAiUser)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource searchGrant 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, identity.id, roles.searchIndexDataReader)
  scope: search
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.searchIndexDataReader)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource keyVaultGrant 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, identity.id, roles.keyVaultSecretsUser)
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.keyVaultSecretsUser)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output appInsightsConnectionString string = appInsights.outputs.connectionString
output keyVaultUri string = keyVault.properties.vaultUri
output managedIdentityClientId string = identity.properties.clientId
output functionAppHostName string = functionApp.outputs.defaultHostName
