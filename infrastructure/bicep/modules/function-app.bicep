// Flex Consumption Function App (ADR-0004) — the serverless host for ingestion
// (#20), inference (#57), and the assistant/agent workloads. Runs as the
// user-assigned Managed Identity; deploy code from src/ with `func publish`.

@description('Function App name (globally unique).')
param name string

@description('Location.')
param location string = resourceGroup().location

@description('Resource id of the user-assigned Managed Identity the app runs as.')
param managedIdentityId string

@description('Backing storage account name.')
param storageAccountName string

@description('Application Insights connection string.')
param appInsightsConnectionString string

@description('App settings (config only — no secrets; secrets come from Key Vault via MI).')
param appSettings array = []

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${name}-plan'
  location: location
  sku: { name: 'FC1', tier: 'FlexConsumption' }
  kind: 'functionapp'
  properties: { reserved: true }
}

var deploymentContainer = 'app-package'

resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${storage.properties.primaryEndpoints.blob}${deploymentContainer}'
          authentication: {
            type: 'StorageAccountConnectionString'
            storageAccountConnectionStringName: 'AzureWebJobsStorage'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.12'
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 40
        instanceMemoryMB: 2048
      }
    }
    siteConfig: {
      appSettings: concat(
        [
          {
            name: 'AzureWebJobsStorage'
            value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storage.listKeys().keys[0].value}'
          }
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: appInsightsConnectionString
          }
        ],
        appSettings
      )
    }
  }
}

output id string = app.id
output defaultHostName string = app.properties.defaultHostName
