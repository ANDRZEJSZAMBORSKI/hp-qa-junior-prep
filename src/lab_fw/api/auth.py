"""Authentication helpers for lab_fw."""

from __future__ import annotations

from lab_fw.api.client import ApiClient
from lab_fw.core.errors import ApiError


def fetch_client_credentials_token(
    client: ApiClient,
    client_id: str,
    client_secret: str,
) -> str:
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    if response.status_code >= 400:
        raise ApiError(
            f"OAuth token request failed: HTTP {response.status_code}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise ApiError("OAuth token response is not valid JSON") from exc

    token = payload.get("access_token")
    if not token:
        raise ApiError("OAuth token response has no access_token")

    client.set_bearer_token(token)
    return token