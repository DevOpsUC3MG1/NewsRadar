"""
Cliente HTTP para la API de NewsRadar.

Este módulo encapsula todas las llamadas a la API REST que necesita el demonio.
El demonio NO toca PostgreSQL ni MongoDB directamente: todo va por API.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class NewsRadarAPIError(Exception):
    """Error genérico de la API."""


class NewsRadarAPIClient:
    """Cliente asíncrono para la API de NewsRadar.

    Mantiene un token Bearer y reautentica automáticamente si caduca (401).
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        password: str,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_prefix = f"{self.base_url}/api/v1"
        self._email = email
        self._password = password
        self._token: str | None = None
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------ auth
    async def login(self) -> str:
        """Hace login y guarda el token. Devuelve el token."""
        resp = await self._client.post(
            f"{self.api_prefix}/auth/login",
            json={"email": self._email, "password": self._password},
        )
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"Login fallido ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        self._token = data["access_token"]
        logger.info("Login OK contra %s como %s", self.base_url, self._email)
        return self._token

    def _headers(self) -> dict[str, str]:
        if not self._token:
            raise NewsRadarAPIError("No hay token. Llama a login() primero.")
        return {"Authorization": f"Bearer {self._token}"}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: dict | None = None,
        retry_on_401: bool = True,
    ) -> httpx.Response:
        """Petición autenticada con reintento de login en 401."""
        url = f"{self.api_prefix}{path}"
        resp = await self._client.request(
            method,
            url,
            headers=self._headers(),
            json=json_body,
            params=params,
        )
        if resp.status_code == 401 and retry_on_401:
            logger.warning("401 en %s; relogin y reintento", path)
            await self.login()
            return await self._request(
                method, path,
                json_body=json_body, params=params, retry_on_401=False,
            )
        return resp

    # -------------------------------------------------------------- usuarios
    async def list_users(self) -> list[dict]:
        resp = await self._request("GET", "/users")
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"list_users fallo ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    async def get_user(self, user_id: int) -> dict:
        resp = await self._request("GET", f"/users/{user_id}")
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"get_user({user_id}) fallo ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    # --------------------------------------------------------------- alertas
    async def list_user_alerts(self, user_id: int) -> list[dict]:
        resp = await self._request("GET", f"/users/{user_id}/alerts")
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"list_user_alerts({user_id}) fallo ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    async def list_all_alerts(self) -> list[dict]:
        """Recorre todos los usuarios y devuelve sus alertas con user_id incluido."""
        users = await self.list_users()
        all_alerts: list[dict] = []
        for u in users:
            try:
                alerts = await self.list_user_alerts(u["id"])
                for a in alerts:
                    # aseguramos que cada alerta sabe a qué usuario pertenece
                    a.setdefault("user_id", u["id"])
                    a["_user_email"] = u["email"]
                    a["_user_first_name"] = u.get("first_name", "")
                    all_alerts.append(a)
            except NewsRadarAPIError as e:
                logger.error("No se pudieron leer alertas de user %s: %s", u["id"], e)
        return all_alerts

    # --------------------------------------------------------------- fuentes
    async def list_information_sources(self) -> list[dict]:
        resp = await self._request("GET", "/information-sources")
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"list_information_sources fallo ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        logger.info(
            "[DEBUG api] list_information_sources -> type=%s len=%s sample=%r",
            type(data).__name__,
            len(data) if hasattr(data, "__len__") else "?",
            (data[:2] if isinstance(data, list) else data),
        )
        return data

    async def list_source_channels(self, source_id: int) -> list[dict]:
        resp = await self._request(
            "GET", f"/information-sources/{source_id}/rss-channels"
        )
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"list_source_channels({source_id}) fallo "
                f"({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        logger.info(
            "[DEBUG api] list_source_channels(%s) -> type=%s len=%s sample=%r",
            source_id, type(data).__name__,
            len(data) if hasattr(data, "__len__") else "?",
            (data[:2] if isinstance(data, list) else data),
        )
        return data

    async def list_categories(self) -> list[dict]:
        resp = await self._request("GET", "/categories")
        if resp.status_code != 200:
            raise NewsRadarAPIError(
                f"list_categories fallo ({resp.status_code}): {resp.text}"
            )
        return resp.json()

    # ---------------------------------------------------------- notificaciones
    async def create_notification(
        self,
        user_id: int,
        alert_id: int,
        timestamp: datetime,
        metrics: list[dict],
    ) -> dict:
        """Crea una notificación en MongoDB vía API."""
        body = {
            "timestamp": timestamp.isoformat(),
            "metrics": metrics,
        }
        resp = await self._request(
            "POST",
            f"/users/{user_id}/alerts/{alert_id}/notifications",
            json_body=body,
        )
        if resp.status_code not in (200, 201):
            raise NewsRadarAPIError(
                f"create_notification fallo ({resp.status_code}): {resp.text}"
            )
        return resp.json()