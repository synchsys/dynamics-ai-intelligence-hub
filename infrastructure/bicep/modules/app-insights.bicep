// Application Insights for observability (#29) — ingestion (#21) and agent
// telemetry (#78) emit here; the cost dashboard (#82) reads from it.

@description('Application Insights component name.')
param name string

@description('Location.')
param location string = resourceGroup().location

// Workspace-based App Insights is the current standard; back it with a
// Log Analytics workspace so KQL queries (agent-telemetry.md) work.
resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${name}-law'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource component 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

@description('Set as APPLICATIONINSIGHTS_CONNECTION_STRING on the Function App.')
output connectionString string = component.properties.ConnectionString
output id string = component.id
