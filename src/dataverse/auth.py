"""Access-token acquisition for the Dataverse Web API.

Uses the OAuth 2.0 **client-credentials** flow via ``azure-identity``. Token
caching and refresh are handled by the credential; this wrapper just exposes a
bearer token for the configured scope and normalises failures to
:class:`DataverseAuthError`.

**ADR-0003:** a service principal (``ClientSecretCredential``) is used now; the
credential is injectable so the path to Managed Identity
(``DefaultAzureCredential`` / ``ManagedIdentityCredential``) is a one-line swap
with no changes to the client.
"""

from azure.core.credentials import TokenCredential
from azure.identity import ClientSecretCredential

from dataverse.config import DataverseConfig
from dataverse.exceptions import DataverseAuthError


class TokenProvider:
    """Provides bearer tokens for the Dataverse scope."""

    def __init__(self, config: DataverseConfig, credential: TokenCredential | None = None) -> None:
        self._scope = config.scope
        self._credential: TokenCredential = credential or ClientSecretCredential(
            tenant_id=config.tenant_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )

    def token(self) -> str:
        """Return a valid bearer token, refreshing via the credential as needed."""
        try:
            return self._credential.get_token(self._scope).token
        except Exception as exc:  # azure.core.exceptions.ClientAuthenticationError etc.
            raise DataverseAuthError(f"Failed to acquire Dataverse token: {exc}") from exc
