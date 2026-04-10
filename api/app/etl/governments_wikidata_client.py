from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from time import perf_counter

import httpx

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_USER_AGENT = "DeudaMundiBot/1.0 (https://deudamundi.econopapi.com)"
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WikidataGovernmentPeriod:
    iso3: str
    leader_name: str
    start_date: date
    end_date: date | None
    role: str


def _chunked(values: list[str], chunk_size: int) -> list[list[str]]:
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def _parse_wikidata_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None

    normalized = str(raw_value).strip()
    if len(normalized) < 10:
        return None

    try:
        return date.fromisoformat(normalized[:10])
    except ValueError:
        return None


def _dedupe_periods(periods: list[WikidataGovernmentPeriod]) -> list[WikidataGovernmentPeriod]:
    by_key: dict[tuple[str, str, date, str], WikidataGovernmentPeriod] = {}

    for period in periods:
        key = (period.iso3, period.leader_name, period.start_date, period.role)
        previous = by_key.get(key)

        if previous is None:
            by_key[key] = period
            continue

        # Keep the row that has an explicit end date when duplicates exist.
        if previous.end_date is None and period.end_date is not None:
            by_key[key] = period

    return sorted(by_key.values(), key=lambda row: (row.iso3, row.start_date, row.leader_name))


def select_preferred_role_periods(periods: list[WikidataGovernmentPeriod]) -> list[WikidataGovernmentPeriod]:
    by_iso3: dict[str, dict[str, list[WikidataGovernmentPeriod]]] = {}

    for period in periods:
        by_iso3.setdefault(period.iso3, {}).setdefault(period.role, []).append(period)

    selected: list[WikidataGovernmentPeriod] = []
    for iso3, role_map in by_iso3.items():
        role_p6 = sorted(role_map.get("p6", []), key=lambda row: (row.start_date, row.leader_name))
        role_p35 = sorted(role_map.get("p35", []), key=lambda row: (row.start_date, row.leader_name))

        # Prefer heads of government when there is enough timeline depth; fallback to head of state.
        if len(role_p6) >= 2:
            selected.extend(role_p6)
            continue

        if len(role_p35) > len(role_p6):
            selected.extend(role_p35)
            continue

        selected.extend(role_p6 or role_p35)

    return _dedupe_periods(selected)


class WikidataGovernmentsClient:
    def __init__(
        self,
        timeout_seconds: float = 30.0,
        chunk_size: int = 25,
        max_duration_seconds: float = 180.0,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.chunk_size = max(1, chunk_size)
        self.max_duration_seconds = max(10.0, max_duration_seconds)

    def fetch_periods(self, iso3_codes: set[str], min_start_year: int = 1990) -> list[WikidataGovernmentPeriod]:
        normalized_iso3 = sorted({code.strip().upper() for code in iso3_codes if len(code.strip()) == 3})
        if not normalized_iso3:
            return []

        chunks = _chunked(normalized_iso3, self.chunk_size)
        started_at = perf_counter()
        rows: list[WikidataGovernmentPeriod] = []
        with httpx.Client(timeout=self.timeout_seconds, headers={"User-Agent": WIKIDATA_USER_AGENT}) as client:
            for index, chunk in enumerate(chunks, start=1):
                elapsed = perf_counter() - started_at
                if elapsed > self.max_duration_seconds:
                    raise TimeoutError(
                        "Wikidata governments ETL exceeded maximum duration "
                        f"({self.max_duration_seconds:.0f}s)"
                    )

                logger.info(
                    "Wikidata governments chunk %s/%s started (iso3=%s, elapsed=%.1fs)",
                    index,
                    len(chunks),
                    len(chunk),
                    elapsed,
                )
                query = self._build_query(chunk, min_start_year=min_start_year)
                try:
                    response = client.get(
                        WIKIDATA_SPARQL_URL,
                        params={"query": query, "format": "json"},
                        headers={"Accept": "application/sparql-results+json"},
                    )
                except httpx.TimeoutException as exc:
                    raise TimeoutError(
                        f"Wikidata chunk timed out after {self.timeout_seconds:.0f}s"
                    ) from exc

                response.raise_for_status()
                payload = response.json()
                parsed_rows = self._parse_payload(payload)
                rows.extend(parsed_rows)
                logger.info(
                    "Wikidata governments chunk %s/%s completed (rows=%s, total_rows=%s)",
                    index,
                    len(chunks),
                    len(parsed_rows),
                    len(rows),
                )

        selected_rows = select_preferred_role_periods(rows)
        logger.info(
            "Wikidata governments fetch completed (raw_rows=%s, selected_rows=%s, countries=%s, elapsed=%.1fs)",
            len(rows),
            len(selected_rows),
            len(normalized_iso3),
            perf_counter() - started_at,
        )
        return selected_rows

    def _build_query(self, iso3_codes: list[str], min_start_year: int) -> str:
        values_clause = " ".join(f'"{iso3}"' for iso3 in iso3_codes)

        return f"""
SELECT ?iso3 ?leaderLabel ?start ?end ?role WHERE {{
  VALUES ?iso3 {{ {values_clause} }}
  ?country wdt:P298 ?iso3 .

  {{
    ?country p:P6 ?statement .
    ?statement ps:P6 ?leader .
    BIND("p6" AS ?role)
  }}
  UNION
  {{
    ?country p:P35 ?statement .
    ?statement ps:P35 ?leader .
    BIND("p35" AS ?role)
  }}

  ?statement pq:P580 ?start .
  OPTIONAL {{ ?statement pq:P582 ?end . }}
  FILTER(YEAR(?start) >= {min_start_year})

  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?iso3 ?start
""".strip()

    def _parse_payload(self, payload: dict) -> list[WikidataGovernmentPeriod]:
        rows: list[WikidataGovernmentPeriod] = []
        bindings = payload.get("results", {}).get("bindings", []) if isinstance(payload, dict) else []

        for binding in bindings:
            if not isinstance(binding, dict):
                continue

            iso3 = str(binding.get("iso3", {}).get("value", "")).strip().upper()
            leader_name = str(binding.get("leaderLabel", {}).get("value", "")).strip()
            role = str(binding.get("role", {}).get("value", "")).strip().lower()
            start_date = _parse_wikidata_date(binding.get("start", {}).get("value"))
            end_date = _parse_wikidata_date(binding.get("end", {}).get("value"))

            if len(iso3) != 3 or not leader_name or start_date is None or role not in {"p6", "p35"}:
                continue

            rows.append(
                WikidataGovernmentPeriod(
                    iso3=iso3,
                    leader_name=leader_name,
                    start_date=start_date,
                    end_date=end_date,
                    role=role,
                )
            )

        return rows
