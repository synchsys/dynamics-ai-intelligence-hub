// Dev environment parameters for main.bicep (rg-racy-ai-dev, uksouth).
// Deploy: az deployment group create -g rg-racy-ai-dev \
//   -f infrastructure/bicep/main.bicep -p infrastructure/environments/dev.bicepparam
using '../bicep/main.bicep'

param appInsightsName = 'racy-appi-dev'
param keyVaultName = 'racy-kv-dev'
param managedIdentityName = 'racy-mi-dev'
param storageAccountName = 'racyfuncdevsa'
param functionAppName = 'racy-func-dev'
param openAiAccountName = 'racy-openai-dev'
param searchServiceName = 'racy-search-dev'

// Non-secret config the Function App needs. Secrets (Dataverse client secret,
// Search key) are NOT here — they resolve at runtime from Key Vault via the
// Managed Identity. KEY_VAULT_URL + AZURE_CLIENT_ID let DefaultAzureCredential
// and SecretResolver find them.
param functionAppSettings = [
  { name: 'KEY_VAULT_URL', value: 'https://racy-kv-dev.vault.azure.net/' }
  { name: 'AZURE_CLIENT_ID', value: 'ab309738-472b-4cdf-ae69-83f2a41b05e1' }
  { name: 'AZURE_OPENAI_ENDPOINT', value: 'https://racy-openai-dev.openai.azure.com/' }
  { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: 'gpt-5-mini' }
  { name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', value: 'text-embedding-3-small' }
  { name: 'AZURE_SEARCH_ENDPOINT', value: 'https://racy-search-dev.search.windows.net/' }
]
