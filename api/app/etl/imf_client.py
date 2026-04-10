from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

IMF_DATAMAPPER_BASE_URL = "https://www.imf.org/external/datamapper/api/v1"
IMF_GENERAL_GOV_DEBT_TO_GDP = "GGXWDG_NGDP"
IMF_NOMINAL_GDP_USD_BILLIONS = "NGDPD"


class ImfDataMapperClient:
    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_general_government_debt_to_gdp(self) -> dict[tuple[str, int], float]:
        return self._fetch_indicator(IMF_GENERAL_GOV_DEBT_TO_GDP)

    def fetch_nominal_gdp_usd_billions(self) -> dict[tuple[str, int], float]:
        return self._fetch_indicator(IMF_NOMINAL_GDP_USD_BILLIONS)

    def _fetch_indicator(self, indicator: str) -> dict[tuple[str, int], float]:
        url = f"{IMF_DATAMAPPER_BASE_URL}/{indicator}"
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()

        values = payload.get("values", {}) if isinstance(payload, dict) else {}
        indicator_payload = values.get(indicator, {}) if isinstance(values, dict) else {}

        current_year = datetime.now(tz=UTC).year
        normalized: dict[tuple[str, int], float] = {}

        for iso3, year_map in indicator_payload.items():
            iso3_normalized = str(iso3 or "").strip().upper()
            if len(iso3_normalized) != 3 or not isinstance(year_map, dict):
                continue

            for year_raw, value_raw in year_map.items():
                try:
                    year = int(str(year_raw))
                    value = float(value_raw)
                except (TypeError, ValueError):
                    continue

                if year >= current_year:
                    # Skip IMF current-year nowcasts/projections to keep the API historical.
                    continue

                normalized[(iso3_normalized, year)] = value

        return normalized
