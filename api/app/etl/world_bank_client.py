from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.worldbank.org/v2"
DEBT_INDICATOR = "DT.DOD.DECT.CD"


class WorldBankClient:
    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_countries(self) -> list[dict[str, Any]]:
        data = self._paginate("/country", params={"format": "json", "per_page": 500})
        return [item for item in data if isinstance(item, dict)]

    def fetch_external_debt(self) -> list[dict[str, Any]]:
        data = self._paginate(
            f"/country/all/indicator/{DEBT_INDICATOR}",
            params={"format": "json", "per_page": 20000},
        )
        return [item for item in data if isinstance(item, dict)]

    def _paginate(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        page = 1

        with httpx.Client(base_url=BASE_URL, timeout=self.timeout_seconds) as client:
            while True:
                response = client.get(path, params={**params, "page": page})
                response.raise_for_status()
                payload = response.json()

                meta = payload[0] if payload and isinstance(payload[0], dict) else {}
                data = payload[1] if len(payload) > 1 and isinstance(payload[1], list) else []
                results.extend(data)

                if page >= int(meta.get("pages", page)):
                    break
                page += 1

        return results
