import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { CountryComparisonChart } from "../components/country/CountryComparisonChart";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import {
  buildCompareHistoryExportRows,
  buildCompareLatestExportRows,
  downloadComparePdfReport,
  downloadCsvFile,
  downloadXlsxFile,
} from "../lib/dataExports";
import { LoadingPanel } from "../components/ui/LoadingPanel";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { t, trRegion } from "../lib/translations";
import { fetchCountriesCompare, fetchGlobeData } from "../services/deudamundiApi";
import { useLocaleStore } from "../store/localeStore";
import type { CountriesCompareResponse, CountryDetailResponse } from "../types/api";

type CountriesLookupItem = {
  iso3: string;
  name_en: string;
  region: string | null;
};

const MAX_COMPARE_COUNTRIES = 5;

function parseCountriesParam(raw: string | null): string[] {
  if (!raw) {
    return [];
  }

  const seen = new Set<string>();
  return raw
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter((iso3) => {
      if (iso3.length !== 3 || seen.has(iso3)) {
        return false;
      }
      seen.add(iso3);
      return true;
    });
}

function getDebtStock(point: CountryDetailResponse): number | null {
  return point.debt_stock_usd ?? point.total_external_debt_usd;
}

export function CompareCountriesPage() {
  const locale = useLocaleStore((state) => state.locale);
  const [searchParams, setSearchParams] = useSearchParams();

  const countriesFromUrl = useMemo(() => {
    return parseCountriesParam(searchParams.get("countries"));
  }, [searchParams]);

  const [allCountries, setAllCountries] = useState<CountriesLookupItem[]>([]);
  const [lookupStatus, setLookupStatus] = useState<"loading" | "ready" | "error">("loading");

  const [selectedIso3, setSelectedIso3] = useState<string[]>(countriesFromUrl);
  const [countrySearch, setCountrySearch] = useState("");

  const [compareStatus, setCompareStatus] = useState<"idle" | "loading" | "error" | "ready">("idle");
  const [comparePayload, setComparePayload] = useState<CountriesCompareResponse | null>(null);

  useEffect(() => {
    setSelectedIso3(countriesFromUrl);
  }, [countriesFromUrl]);

  useEffect(() => {
    let cancelled = false;

    async function loadLookup() {
      setLookupStatus("loading");
      try {
        const response = await fetchGlobeData();
        if (!cancelled) {
          const sorted = [...response.items]
            .sort((a, b) => a.name_en.localeCompare(b.name_en))
            .map((item) => ({
              iso3: item.iso3,
              name_en: item.name_en,
              region: item.region,
            }));
          setAllCountries(sorted);
          setLookupStatus("ready");
        }
      } catch {
        if (!cancelled) {
          setLookupStatus("error");
        }
      }
    }

    void loadLookup();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadCompare() {
      if (countriesFromUrl.length < 2) {
        setComparePayload(null);
        setCompareStatus("idle");
        return;
      }

      setCompareStatus("loading");
      try {
        const payload = await fetchCountriesCompare(countriesFromUrl);
        if (!cancelled) {
          setComparePayload(payload);
          setCompareStatus("ready");
        }
      } catch {
        if (!cancelled) {
          setCompareStatus("error");
        }
      }
    }

    void loadCompare();

    return () => {
      cancelled = true;
    };
  }, [countriesFromUrl]);

  const suggestions = useMemo(() => {
    const query = countrySearch.trim().toLowerCase();
    const selectedSet = new Set(selectedIso3);

    return allCountries
      .filter((country) => {
        if (selectedSet.has(country.iso3)) {
          return false;
        }
        if (!query) {
          return true;
        }

        return country.name_en.toLowerCase().includes(query) || country.iso3.toLowerCase().includes(query);
      })
      .slice(0, 8);
  }, [allCountries, countrySearch, selectedIso3]);

  const canCompare = selectedIso3.length >= 2;

  const runCompare = () => {
    const next = new URLSearchParams(searchParams);
    if (selectedIso3.length > 0) {
      next.set("countries", selectedIso3.join(","));
    } else {
      next.delete("countries");
    }
    setSearchParams(next);
  };

  const handleExport = async (format: "csv" | "xlsx" | "pdf") => {
    if (!comparePayload || comparePayload.items.length === 0) {
      return;
    }

    const latestRows = buildCompareLatestExportRows(comparePayload.items);
    const historyRows = buildCompareHistoryExportRows(comparePayload.items);
    const fileTag = comparePayload.items.map((item) => item.detail.iso3.toLowerCase()).join("-");
    const baseFilename = `deudamundi-compare-${fileTag || "countries"}`;

    if (format === "csv") {
      downloadCsvFile(`${baseFilename}-history.csv`, historyRows);
      return;
    }

    if (format === "pdf") {
      await downloadComparePdfReport(`${baseFilename}-report.pdf`, comparePayload.items, locale);
      return;
    }

    downloadXlsxFile(`${baseFilename}.xlsx`, [
      { name: "latest", rows: latestRows },
      { name: "history", rows: historyRows },
    ]);
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <AppHeader title={t(locale, "compareTitle")} subtitle={t(locale, "compareSubtitle")} />

      <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
        <LanguageSwitcher />
        <div className="flex items-center gap-4">
          <Link to="/" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
            ← {t(locale, "backToGlobe")}
          </Link>
          <Link to="/rankings" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
            {t(locale, "viewRankings")} →
          </Link>
        </div>
      </div>

      <section className="glass-panel rounded-xl p-4">
        <h2 className="text-sm font-semibold text-[#f5f4f0]">{t(locale, "compareSelected")}</h2>
        <p className="mt-1 text-xs text-[#888680]">{t(locale, "compareHint")}</p>

        <div className="mt-3 flex flex-wrap gap-2">
          {selectedIso3.length === 0 ? (
            <span className="text-xs text-[#888680]">{t(locale, "noCountriesFilters")}</span>
          ) : (
            selectedIso3.map((iso3) => (
              <button
                key={iso3}
                type="button"
                onClick={() => {
                  setSelectedIso3((prev) => prev.filter((item) => item !== iso3));
                }}
                className="rounded-full border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1 text-xs text-[#f5f4f0]"
                aria-label={`${t(locale, "removeCountry")} ${iso3}`}
              >
                {iso3} ×
              </button>
            ))
          )}
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            value={countrySearch}
            onChange={(event) => {
              setCountrySearch(event.target.value);
            }}
            placeholder={t(locale, "compareSelectPlaceholder")}
            className="w-full rounded-lg border border-[#3b4252] bg-[#0d1017] px-3 py-2 text-sm text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={runCompare}
              disabled={!canCompare}
              className="rounded-md border border-[#7c6af5] bg-[#7c6af5]/20 px-3 py-2 text-xs text-[#ede9fe] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {t(locale, "compareRun")}
            </button>
            <button
              type="button"
              onClick={() => {
                setSelectedIso3([]);
                setCountrySearch("");
                const next = new URLSearchParams(searchParams);
                next.delete("countries");
                setSearchParams(next);
              }}
              className="rounded-md border border-[#3b4252] bg-[#0d1017]/80 px-3 py-2 text-xs text-[#f5f4f0]"
            >
              {t(locale, "compareReset")}
            </button>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-[#888680]">{t(locale, "exportCompareSubtitle")}</span>
          <button
            type="button"
            onClick={() => {
              void handleExport("csv");
            }}
            disabled={!comparePayload || comparePayload.items.length === 0}
            className="rounded-md border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1.5 text-xs text-[#f5f4f0] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t(locale, "exportCsv")}
          </button>
          <button
            type="button"
            onClick={() => {
              void handleExport("xlsx");
            }}
            disabled={!comparePayload || comparePayload.items.length === 0}
            className="rounded-md border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1.5 text-xs text-[#f5f4f0] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t(locale, "exportXlsx")}
          </button>
          <button
            type="button"
            onClick={() => {
              void handleExport("pdf");
            }}
            disabled={!comparePayload || comparePayload.items.length === 0}
            className="rounded-md border border-[#7c6af5] bg-[#7c6af5]/20 px-3 py-1.5 text-xs text-[#ede9fe] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t(locale, "exportPdf")}
          </button>
        </div>

        {!canCompare && (
          <p className="mt-2 text-xs text-amber-300">{t(locale, "compareNeedTwo")}</p>
        )}

        <ul className="mt-3 grid gap-2 md:grid-cols-2">
          {suggestions.map((suggestion) => (
            <li key={suggestion.iso3}>
              <button
                type="button"
                onClick={() => {
                  setSelectedIso3((prev) => {
                    if (prev.includes(suggestion.iso3) || prev.length >= MAX_COMPARE_COUNTRIES) {
                      return prev;
                    }
                    return [...prev, suggestion.iso3];
                  });
                  setCountrySearch("");
                }}
                className="w-full rounded-lg border border-[#2a2f3a] bg-[#0d1017]/70 px-3 py-2 text-left text-xs text-[#c8c7c2] hover:border-[#7c6af5] hover:text-[#f5f4f0]"
              >
                <span className="font-medium text-[#f5f4f0]">{suggestion.name_en}</span> ({suggestion.iso3})
                <span className="ml-2 text-[#888680]">{suggestion.region ? trRegion(locale, suggestion.region) : t(locale, "notAvailable")}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      {lookupStatus === "loading" && (
        <LoadingPanel message={`${t(locale, "loadingGlobeData")}...`} detail="/api/v1/globe-data" />
      )}

      {lookupStatus === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-6 text-sm text-rose-200">
          {t(locale, "errorGlobeData")}
        </section>
      )}

      {compareStatus === "loading" && (
        <LoadingPanel message={`${t(locale, "compareLoading")}...`} detail="/api/v1/countries/compare" />
      )}

      {compareStatus === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-6 text-sm text-rose-200">
          {t(locale, "compareError")}
        </section>
      )}

      {compareStatus === "ready" && comparePayload && (
        <>
          {comparePayload.missing_iso3.length > 0 && (
            <section className="rounded-xl border border-amber-800 bg-amber-950/30 p-4 text-xs text-amber-200">
              {t(locale, "compareMissing")}: {comparePayload.missing_iso3.join(", ")}
            </section>
          )}

          <CountryComparisonChart countries={comparePayload.items} />

          <section className="glass-panel overflow-x-auto rounded-xl">
            <table className="min-w-[680px] w-full border-collapse text-sm">
              <thead className="bg-[#0d1017]/70 text-left text-xs uppercase tracking-wide text-[#888680]">
                <tr>
                  <th className="px-4 py-3">{t(locale, "country")}</th>
                  <th className="px-4 py-3">{t(locale, "debtLabel")}</th>
                  <th className="px-4 py-3">{t(locale, "debtToGdpLabel")}</th>
                  <th className="px-4 py-3">{t(locale, "latestYear")}</th>
                </tr>
              </thead>
              <tbody>
                {comparePayload.items.map((item) => (
                  <tr key={item.detail.iso3} className="border-t border-[#2a2f3a] text-[#f5f4f0]">
                    <td className="px-4 py-3">
                      <Link className="text-[#a594f9] hover:text-[#c4b9fa]" to={`/country/${item.detail.iso3.toLowerCase()}`}>
                        {item.detail.name_en} ({item.detail.iso3})
                      </Link>
                    </td>
                    <td className="px-4 py-3">{formatUsdCompact(getDebtStock(item.detail))}</td>
                    <td className="px-4 py-3">{formatPercentage(item.detail.debt_pct_gdp)}</td>
                    <td className="px-4 py-3 text-[#c8c7c2]">{item.detail.latest_year ?? t(locale, "notAvailable")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </main>
  );
}
