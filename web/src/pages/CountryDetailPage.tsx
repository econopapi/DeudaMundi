import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { CountryHero } from "../components/country/CountryHero";
import { CountryHistoryChart } from "../components/country/CountryHistoryChart";
import { ShareCardActions } from "../components/country/ShareCardActions";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { LoadingPanel } from "../components/ui/LoadingPanel";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { t, trRegion } from "../lib/translations";
import { fetchCountryDetail, fetchCountryGovernments, fetchCountryHistory } from "../services/deudamundiApi";
import { useLocaleStore } from "../store/localeStore";
import type {
  CountryDetailResponse,
  CountryGovernmentItem,
  CountryHistoryItem,
} from "../types/api";

function formatMetricWithAvailability(value: number | null, formatter: (input: number | null) => string): string {
  if (value === null || Number.isNaN(value)) {
    return "__NOT_AVAILABLE__";
  }

  return formatter(value);
}

function getDebtStock(country: CountryDetailResponse): number | null {
  return country.debt_stock_usd ?? country.total_external_debt_usd;
}

export function CountryDetailPage() {
  const { iso3 = "" } = useParams();
  const locale = useLocaleStore((state) => state.locale);
  const [country, setCountry] = useState<CountryDetailResponse | null>(null);
  const [historyItems, setHistoryItems] = useState<CountryHistoryItem[]>([]);
  const [governments, setGovernments] = useState<CountryGovernmentItem[]>([]);
  const [status, setStatus] = useState<"loading" | "error" | "ready">("loading");

  useEffect(() => {
    let cancelled = false;

    async function loadCountry() {
      setStatus("loading");
      try {
        const [detail, history, governmentsResponse] = await Promise.all([
          fetchCountryDetail(iso3),
          fetchCountryHistory(iso3),
          fetchCountryGovernments(iso3),
        ]);

        if (!cancelled) {
          setCountry(detail);
          setHistoryItems(history.items);
          setGovernments(governmentsResponse.items);
          setStatus("ready");
        }
      } catch {
        if (!cancelled) {
          setStatus("error");
        }
      }
    }

    if (iso3) {
      void loadCountry();
    }

    return () => {
      cancelled = true;
    };
  }, [iso3]);

  useEffect(() => {
    if (!country) {
      return;
    }

    const title = `${country.name_en} · ${t(locale, "shareTitlePrefix")} · DeudaMundi`;
    const debtStock = getDebtStock(country);
    const description = `${country.name_en} (${country.iso3}) ${t(locale, "shareTitlePrefix")}: ${t(locale, "debtLabel").toLowerCase()} ${formatUsdCompact(
      debtStock,
    )}, ${t(locale, "debtPerCapitaLabel").toLowerCase()} ${formatUsdCompact(country.debt_per_capita_usd)}, ${t(locale, "debtToGdpLabel").toLowerCase()} ${formatPercentage(country.debt_pct_gdp)}.`;

    document.title = title;

    const upsertMeta = (selector: string, attributeName: "property" | "name", attributeValue: string, content: string) => {
      let element = document.head.querySelector(selector) as HTMLMetaElement | null;
      if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attributeName, attributeValue);
        document.head.appendChild(element);
      }

      element.setAttribute("content", content);
    };

    upsertMeta('meta[property="og:title"]', "property", "og:title", title);
    upsertMeta('meta[property="og:description"]', "property", "og:description", description);
    upsertMeta('meta[name="twitter:card"]', "name", "twitter:card", "summary_large_image");
    upsertMeta('meta[name="twitter:title"]', "name", "twitter:title", title);
    upsertMeta('meta[name="twitter:description"]', "name", "twitter:description", description);
  }, [country, locale]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-8">
      <header className="border-b border-[#2a2f3a] pb-4">
        <h1 className="display-title text-2xl font-semibold text-[#f5f4f0] md:text-3xl">
          {t(locale, "countryDetailPrefix")} · {iso3.toUpperCase()}
        </h1>
        <p className="mt-2 text-sm text-[#888680]">{t(locale, "countryIntro")}</p>
      </header>

      <div className="flex flex-wrap items-center gap-4 text-sm">
        <LanguageSwitcher />
        <Link to="/" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
          ← {t(locale, "backToGlobe")}
        </Link>
        <Link to="/rankings" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
          {t(locale, "viewRankings")} →
        </Link>
      </div>

      {status === "loading" && (
        <LoadingPanel message={`${t(locale, "loadingCountryMetrics")}...`} detail={`/api/v1/countries/${iso3.toUpperCase()}`} />
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-6 text-sm text-rose-200">
          {t(locale, "errorCountry")} `{iso3.toUpperCase()}`.
        </section>
      )}

      {status === "ready" && country && (
        <>
          <CountryHero country={country} />

          <ShareCardActions country={country} />

          <CountryHistoryChart historyItems={historyItems} governments={governments} />

          <section className="glass-panel grid gap-4 rounded-2xl p-6 md:grid-cols-2">
            <article className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4">
              <h2 className="text-sm font-semibold text-[#c8c7c2]">{t(locale, "debtMetrics")}</h2>
              <ul className="mt-3 space-y-2 text-sm text-[#f5f4f0]">
                <li>{t(locale, "debtLabel")}: {formatMetricWithAvailability(getDebtStock(country), formatUsdCompact).replace("__NOT_AVAILABLE__", t(locale, "notAvailable"))}</li>
                <li>{t(locale, "debtPerCapitaLabel")}: {formatMetricWithAvailability(country.debt_per_capita_usd, formatUsdCompact).replace("__NOT_AVAILABLE__", t(locale, "notAvailable"))}</li>
                <li>{t(locale, "debtToGdpLabel")}: {formatMetricWithAvailability(country.debt_pct_gdp, formatPercentage).replace("__NOT_AVAILABLE__", t(locale, "notAvailable"))}</li>
                <li>GDP: {formatMetricWithAvailability(country.gdp_usd, formatUsdCompact).replace("__NOT_AVAILABLE__", t(locale, "notAvailable"))}</li>
                <li>{t(locale, "latestYear")}: {country.latest_year ?? t(locale, "notAvailable")}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4">
              <h2 className="text-sm font-semibold text-[#c8c7c2]">{t(locale, "countryInfo")}</h2>
              <ul className="mt-3 space-y-2 text-sm text-[#f5f4f0]">
                <li>Name (EN): {country.name_en}</li>
                <li>Name (ES): {country.name_es}</li>
                <li>ISO2: {country.iso2}</li>
                <li>{t(locale, "region")}: {country.region ? trRegion(locale, country.region) : t(locale, "notAvailable")}</li>
                <li>Subregion: {country.subregion ?? t(locale, "notAvailable")}</li>
                <li>Population: {country.population?.toLocaleString(locale === "es" ? "es-MX" : "en-US") ?? t(locale, "notAvailable")}</li>
                <li>Capital: {country.capital ?? t(locale, "notAvailable")}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4 md:col-span-2">
              <h2 className="text-sm font-semibold text-[#c8c7c2]">{t(locale, "emotionalEquivalences")}</h2>
              {country.equivalences.length === 0 ? (
                <p className="mt-3 text-sm text-[#888680]">{t(locale, "noEquivalences")}</p>
              ) : (
                <ul className="mt-3 grid gap-3 md:grid-cols-2">
                  {country.equivalences.map((equivalence) => (
                    <li key={equivalence.label} className="rounded-lg border border-[#3b4252] p-3 text-sm">
                      <p className="font-medium text-[#f5f4f0]">{equivalence.label}</p>
                      <p className="text-[#c8c7c2]">{equivalence.value.toLocaleString(locale === "es" ? "es-MX" : "en-US")}</p>
                      <p className="mt-1 text-xs text-[#888680]">{equivalence.description}</p>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          </section>
        </>
      )}
    </main>
  );
}
