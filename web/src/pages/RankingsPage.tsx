import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { t } from "../lib/translations";
import { fetchRankings } from "../services/deudamundiApi";
import { useLocaleStore } from "../store/localeStore";
import type { RankingItem, RankingMetric } from "../types/api";
import { LanguageSwitcher } from "../components/LanguageSwitcher";

const METRIC_OPTIONS: Array<{ value: RankingMetric; label: string }> = [
  { value: "absolute", label: "Total external debt" },
  { value: "pct_gdp", label: "Debt / GDP" },
  { value: "per_capita", label: "Debt per capita" },
];

const REGION_OPTIONS = [
  "East Asia & Pacific",
  "Europe & Central Asia",
  "Latin America & Caribbean",
  "Middle East, North Africa, Afghanistan & Pakistan",
  "North America",
  "South Asia",
  "Sub-Saharan Africa",
];

function formatRankingValue(metric: RankingMetric, value: number | null): string {
  if (metric === "pct_gdp") {
    return formatPercentage(value);
  }

  return formatUsdCompact(value);
}

export function RankingsPage() {
  const locale = useLocaleStore((state) => state.locale);
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<RankingItem[]>([]);
  const [status, setStatus] = useState<"loading" | "error" | "ready">("loading");

  const metricParam = searchParams.get("metric") as RankingMetric | null;
  const metric = METRIC_OPTIONS.some((option) => option.value === metricParam) ? metricParam! : "absolute";
  const region = searchParams.get("region") ?? "";
  const query = searchParams.get("q") ?? "";

  useEffect(() => {
    let cancelled = false;

    async function loadRankings() {
      setStatus("loading");
      try {
        const response = await fetchRankings(metric, region || undefined, 20);
        if (!cancelled) {
          setItems(response.items);
          setStatus("ready");
        }
      } catch {
        if (!cancelled) {
          setStatus("error");
        }
      }
    }

    void loadRankings();

    return () => {
      cancelled = true;
    };
  }, [metric, region]);

  const filteredItems = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return items;
    }

    return items.filter((item) => {
      return item.name_en.toLowerCase().includes(normalized) || item.iso3.toLowerCase().includes(normalized);
    });
  }, [items, query]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <AppHeader
        title={t(locale, "rankingsTitle")}
        subtitle={t(locale, "rankingsSubtitle")}
      />

      <div className="flex items-center justify-between text-sm">
        <LanguageSwitcher />
        <Link to="/" className="text-sky-300 hover:text-sky-200">
          ← {t(locale, "backToGlobe")}
        </Link>
      </div>

      <section className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/70 p-4 md:grid-cols-3">
        <div>
          <label htmlFor="metric-filter" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-300">
            Metric
          </label>
          <select
            id="metric-filter"
            value={metric}
            onChange={(event) => {
              const next = new URLSearchParams(searchParams);
              next.set("metric", event.target.value);
              setSearchParams(next);
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
          >
            {METRIC_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="region-filter" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-300">
            Region
          </label>
          <select
            id="region-filter"
            value={region}
            onChange={(event) => {
              const next = new URLSearchParams(searchParams);
              if (event.target.value) {
                next.set("region", event.target.value);
              } else {
                next.delete("region");
              }
              setSearchParams(next);
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
          >
            <option value="">All regions</option>
            {REGION_OPTIONS.map((regionOption) => (
              <option key={regionOption} value={regionOption}>
                {regionOption}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="country-search" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-300">
            Country search
          </label>
          <input
            id="country-search"
            list="countries-list"
            value={query}
            onChange={(event) => {
              const next = new URLSearchParams(searchParams);
              if (event.target.value.trim()) {
                next.set("q", event.target.value);
              } else {
                next.delete("q");
              }
              setSearchParams(next);
            }}
            placeholder="Type country or ISO3"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
          />
          <datalist id="countries-list">
            {items.map((item) => (
              <option key={item.iso3} value={item.name_en} />
            ))}
          </datalist>
        </div>
      </section>

      {status === "loading" && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-8 text-sm text-slate-300">Loading rankings…</section>
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-8 text-sm text-rose-200">
          Could not load rankings from `GET /api/v1/rankings`.
        </section>
      )}

      {status === "ready" && (
        <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/70">
          {filteredItems.length === 0 ? (
            <p className="p-6 text-sm text-slate-300">No countries found for the selected filters and metric.</p>
          ) : (
            <table className="w-full border-collapse text-sm">
              <thead className="bg-slate-950/60 text-left text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="px-4 py-3">Rank</th>
                  <th className="px-4 py-3">Country</th>
                  <th className="px-4 py-3">Region</th>
                  <th className="px-4 py-3">Value</th>
                  <th className="px-4 py-3">Year</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr key={`${item.iso3}-${item.rank}`} className="border-t border-slate-800 text-slate-200">
                    <td className="px-4 py-3 font-semibold">#{item.rank}</td>
                    <td className="px-4 py-3">
                      <Link className="text-sky-300 hover:text-sky-200" to={`/country/${item.iso3.toLowerCase()}`}>
                        {item.name_en} ({item.iso3})
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{item.region ?? "Not available"}</td>
                    <td className="px-4 py-3">{formatRankingValue(metric, item.value)}</td>
                    <td className="px-4 py-3 text-slate-300">{item.latest_year ?? "N/A"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </main>
  );
}
