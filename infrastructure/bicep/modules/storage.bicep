// Storage account backing the Function App (required by the Functions host).

@description('Storage account name (globally unique, 3-24 lowercase alphanumerics).')
@minLength(3)
@maxLength(24)
param name string

@description('Location.')
param location string = resourceGroup().location

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

output id string = storage.id
output name string = storage.name
