// Consolidated observability: one dashboard + baseline alerts over ingestion,
// agents, and HTTP telemetry (#29 / 11.D). Conforms to
// docs/architecture/observability-standard.md. Scoped to the App Insights
// component (workspace-based) so queries span all sources.

@description('Resource id of the App Insights component all telemetry flows to.')
param appInsightsId string

@description('Location.')
param location string = resourceGroup().location

@description('Optional Action Group id for alert notifications (email/SMS/webhook). Empty = alerts evaluate without notifying.')
param actionGroupId string = ''

var actions = empty(actionGroupId) ? [] : [actionGroupId]

// --- Dashboard: one workbook over ingestion + agents + HTTP -----------------

resource workbook 'Microsoft.Insights/workbooks@2022-04-01' = {
  name: guid(resourceGroup().id, 'observability-workbook')
  location: location
  kind: 'shared'
  properties: {
    displayName: 'Observability — ingestion, agents & HTTP'
    category: 'workbook'
    sourceId: appInsightsId
    serializedData: string({
      version: 'Notebook/1.0'
      items: [
        {
          type: 1
          content: { json: '# Dynamics AI Intelligence Hub — Observability\nIngestion (#21), agent runs (#78), and HTTP endpoints against the one standard (observability-standard.md).' }
        }
        {
          type: 3
          content: {
            version: 'KqlItem/1.0'
            query: 'AppRequests\n| summarize total=count(), failures=countif(Success == false), p95_ms=percentile(DurationMs, 95) by Name, bin(TimeGenerated, 15m)\n| order by TimeGenerated desc'
            size: 0
            title: 'HTTP requests — volume, failures, p95 latency'
            queryType: 0
            resourceType: 'microsoft.insights/components'
          }
        }
        {
          type: 3
          content: {
            version: 'KqlItem/1.0'
            query: 'AppTraces\n| where Message startswith "metric ingestion."\n| parse Message with "metric " name "=" value:real " " *\n| summarize sum(value) by name, bin(TimeGenerated, 1h)'
            size: 0
            title: 'Ingestion metrics (records / duration / failures)'
            queryType: 0
            resourceType: 'microsoft.insights/components'
          }
        }
        {
          type: 3
          content: {
            version: 'KqlItem/1.0'
            query: 'AppTraces\n| where Message startswith "event agent.step"\n| parse Message with * "\'run_id\': \'" run_id "\'" *\n| summarize steps=count() by run_id\n| order by steps desc'
            size: 0
            title: 'Agent workflow runs (steps per run_id)'
            queryType: 0
            resourceType: 'microsoft.insights/components'
          }
        }
      ]
    })
  }
}

// --- Baseline alerts (scheduled log-query rules) ----------------------------

resource failureAlert 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: 'racy-alert-http-failures'
  location: location
  properties: {
    displayName: 'HTTP function failures'
    description: 'Any HTTP function invocation returning a failure result.'
    severity: 2
    enabled: true
    scopes: [appInsightsId]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT15M'
    criteria: {
      allOf: [
        {
          query: 'AppRequests | where Success == false'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    autoMitigate: true
    actions: { actionGroups: actions }
  }
}

resource ingestionFailureAlert 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: 'racy-alert-ingestion-failures'
  location: location
  properties: {
    displayName: 'Ingestion run failures'
    description: 'A scheduled ingestion run emitted the ingestion.failures signal.'
    severity: 1
    enabled: true
    scopes: [appInsightsId]
    evaluationFrequency: 'PT1H'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          query: 'AppTraces | where Message startswith "metric ingestion.failures"'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    autoMitigate: true
    actions: { actionGroups: actions }
  }
}

resource latencyAlert 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: 'racy-alert-http-latency'
  location: location
  properties: {
    displayName: 'HTTP p95 latency high'
    description: 'p95 request latency over 5s in a 15-minute window.'
    severity: 3
    enabled: true
    scopes: [appInsightsId]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT15M'
    criteria: {
      allOf: [
        {
          query: 'AppRequests | summarize p95=percentile(DurationMs, 95)'
          timeAggregation: 'Maximum'
          metricMeasureColumn: 'p95'
          operator: 'GreaterThan'
          threshold: 5000
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    autoMitigate: true
    actions: { actionGroups: actions }
  }
}

output workbookId string = workbook.id
