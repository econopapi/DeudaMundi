import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { LoadingPanel } from "../components/ui/LoadingPanel";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { RANKINGS_REGION_OPTIONS, isRankingsRegion } from "../lib/regions";
import { t, trRegion } from "../lib/translations";
import { fetchRankings } from "../services/deudamundiApi";
import { useLocaleStore } from "../store/localeStore";
import type { RankingItem, RankingMetric } from "../types/api";
import { LanguageSwitcher } from "../components/LanguageSwitcher";

const METRIC_OPTIONS: Array<{ value: RankingMetric; labelKey: "metricAbsolute" | "metricPctGdp" | "metricPerCapita" }> = [
  { value: "absolute", labelKey: "metricAbsolute" },
  { value: "pct_gdp", labelKey: "metricPctGdp" },
  { value: "per_capita", labelKey: "metricPerCapita" },
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
  const regionFromUrl = searchParams.get("region") ?? "";
  const region = isRankingsRegion(regionFromUrl) ? regionFromUrl : "";
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
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <AppHeader
        title={t(locale, "rankingsTitle")}
        subtitle={t(locale, "rankingsSubtitle")}
      />

      <div className="flex items-center justify-between text-sm">
        <LanguageSwitcher />
        <Link to="/" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
          ← {t(locale, "backToGlobe")}
        </Link>
      </div>

      <section className="glass-panel grid gap-4 rounded-xl p-4 md:grid-cols-3">
        <div>
          <label htmlFor="metric-filter" className="mono-meta mb-2 block text-xs font-semibold uppercase tracking-wide text-[#c8c7c2]">
            {t(locale, "metricFilter")}
          </label>
          <select
            id="metric-filter"
            value={metric}
            onChange={(event) => {
              const next = new URLSearchParams(searchParams);
              next.set("metric", event.target.value);
              setSearchParams(next);
            }}
            className="w-full rounded-lg border border-[#3b4252] bg-[#0d1017] px-3 py-2 text-sm text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
          >
            {METRIC_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {t(locale, option.labelKey)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="region-filter" className="mono-meta mb-2 block text-xs font-semibold uppercase tracking-wide text-[#c8c7c2]">
            {t(locale, "region")}
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
            className="w-full rounded-lg border border-[#3b4252] bg-[#0d1017] px-3 py-2 text-sm text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
          >
            <option value="">{t(locale, "allRegions")}</option>
            {RANKINGS_REGION_OPTIONS.map((regionOption) => (
              <option key={regionOption} value={regionOption}>
                {trRegion(locale, regionOption)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="country-search" className="mono-meta mb-2 block text-xs font-semibold uppercase tracking-wide text-[#c8c7c2]">
            {t(locale, "countrySearch")}
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
            placeholder={t(locale, "countrySearchPlaceholder")}
            className="w-full rounded-lg border border-[#3b4252] bg-[#0d1017] px-3 py-2 text-sm text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
          />
          <datalist id="countries-list">
            {items.map((item) => (
              <option key={item.iso3} value={item.name_en} />
            ))}
          </datalist>
        </div>
      </section>

      {status === "loading" && (
        <LoadingPanel message={`${t(locale, "loadingRankings")}...`} detail="/api/v1/rankings" />
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-8 text-sm text-rose-200">
          {t(locale, "errorRankings")}
        </section>
      )}

      {status === "ready" && (
        <section className="glass-panel overflow-x-auto rounded-xl">
          {filteredItems.length === 0 ? (
            <p className="p-6 text-sm text-[#c8c7c2]">{t(locale, "noCountriesFilters")}</p>
          ) : (
            <table className="min-w-[720px] w-full border-collapse text-sm">
              <thead className="bg-[#0d1017]/70 text-left text-xs uppercase tracking-wide text-[#888680]">
                <tr>
                  <th className="px-4 py-3">{t(locale, "rank")}</th>
                  <th className="px-4 py-3">{t(locale, "country")}</th>
                  <th className="px-4 py-3">{t(locale, "region")}</th>
                  <th className="px-4 py-3">{t(locale, "value")}</th>
                  <th className="px-4 py-3">{t(locale, "year")}</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => (
                  <tr key={`${item.iso3}-${item.rank}`} className="border-t border-[#2a2f3a] text-[#f5f4f0]">
                    <td className="px-4 py-3 font-semibold">#{item.rank}</td>
                    <td className="px-4 py-3">
                      <Link className="text-[#a594f9] hover:text-[#c4b9fa]" to={`/country/${item.iso3.toLowerCase()}`}>
                        {item.name_en} ({item.iso3})
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-[#c8c7c2]">{item.region ? trRegion(locale, item.region) : t(locale, "notAvailable")}</td>
                    <td className="px-4 py-3">{formatRankingValue(metric, item.value)}</td>
                    <td className="px-4 py-3 text-[#c8c7c2]">{item.latest_year ?? t(locale, "notAvailable")}</td>
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
