"""HTTP API client for lab_fw."""

from __future__ import annotations

import logging

import httpx

from lab_fw.core.config import Settings, get_settings
from lab_fw.core.errors import ApiError

logger = logging.getLogger("lab_fw.api")


class ApiClient:
    def __init__(
                    self,
                    settings: Settings | None = None,
                    *,
                    transport: httpx.BaseTransport | None = None,
                ) -> None:
        self._settings = settings or get_settings()
        kwargs: dict = {
            "base_url": self._settings.base_url,
            "timeout": self._settings.timeout_s,
        }
        if transport is not None:
            kwargs["transport"] = transport
        self._client = httpx.Client(**kwargs)

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        logger.info("%s %s", method, path)
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiError(f"{method} {path} failed: {exc}") from exc
        return response

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ApiClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()