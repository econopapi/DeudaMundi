import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { CountryHero } from "../components/country/CountryHero";
import { CountryHistoryChart } from "../components/country/CountryHistoryChart";
import { ShareCardActions } from "../components/country/ShareCardActions";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { t } from "../lib/translations";
import { fetchCountryDetail, fetchCountryGovernments, fetchCountryHistory } from "../services/deudamundiApi";
import { useLocaleStore } from "../store/localeStore";
import type {
  CountryDetailResponse,
  CountryGovernmentItem,
  CountryHistoryItem,
} from "../types/api";

function formatMetricWithAvailability(value: number | null, formatter: (input: number | null) => string): string {
  if (value === null || Number.isNaN(value)) {
    return "Not available from source";
  }

  return formatter(value);
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

    const title = `${country.name_en} debt profile · DeudaMundi`;
    const description = `${country.name_en} (${country.iso3}) debt profile: total debt ${formatUsdCompact(
      country.total_external_debt_usd,
    )}, debt per capita ${formatUsdCompact(country.debt_per_capita_usd)}, debt/GDP ${formatPercentage(country.debt_pct_gdp)}.`;

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
  }, [country]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-8">
      <header className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-semibold text-slate-100 md:text-3xl">
          {t(locale, "countryDetailPrefix")} · {iso3.toUpperCase()}
        </h1>
        <p className="mt-2 text-sm text-slate-400">Vista inicial del país conectada a GET /api/v1/countries/{"{iso3}"}.</p>
      </header>

      <div className="flex flex-wrap items-center gap-4 text-sm">
        <LanguageSwitcher />
        <Link to="/" className="text-sky-300 hover:text-sky-200">
          ← {t(locale, "backToGlobe")}
        </Link>
        <Link to="/rankings" className="text-sky-300 hover:text-sky-200">
          {t(locale, "viewRankings")} →
        </Link>
      </div>

      {status === "loading" && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 text-sm text-slate-300">
          Loading country metrics...
        </section>
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-6 text-sm text-rose-200">
          Could not load country detail for `{iso3.toUpperCase()}`.
        </section>
      )}

      {status === "ready" && country && (
        <>
          <CountryHero country={country} />

          <ShareCardActions country={country} />

          <CountryHistoryChart historyItems={historyItems} governments={governments} />

          <section className="grid gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 md:grid-cols-2">
            <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
              <h2 className="text-sm font-semibold text-slate-300">Debt metrics</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                <li>Total debt: {formatMetricWithAvailability(country.total_external_debt_usd, formatUsdCompact)}</li>
                <li>Debt per capita: {formatMetricWithAvailability(country.debt_per_capita_usd, formatUsdCompact)}</li>
                <li>Debt / GDP: {formatMetricWithAvailability(country.debt_pct_gdp, formatPercentage)}</li>
                <li>GDP: {formatMetricWithAvailability(country.gdp_usd, formatUsdCompact)}</li>
                <li>Latest year: {country.latest_year ?? "Not available from source"}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
              <h2 className="text-sm font-semibold text-slate-300">Country info</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                <li>Name (EN): {country.name_en}</li>
                <li>Name (ES): {country.name_es}</li>
                <li>ISO2: {country.iso2}</li>
                <li>Region: {country.region ?? "Not available from source"}</li>
                <li>Subregion: {country.subregion ?? "Not available from source"}</li>
                <li>Population: {country.population?.toLocaleString("en-US") ?? "Not available from source"}</li>
                <li>Capital: {country.capital ?? "Not available from source"}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4 md:col-span-2">
              <h2 className="text-sm font-semibold text-slate-300">Emotional equivalences</h2>
              {country.equivalences.length === 0 ? (
                <p className="mt-3 text-sm text-slate-400">No equivalences available.</p>
              ) : (
                <ul className="mt-3 grid gap-3 md:grid-cols-2">
                  {country.equivalences.map((equivalence) => (
                    <li key={equivalence.label} className="rounded-lg border border-slate-700 p-3 text-sm">
                      <p className="font-medium text-slate-200">{equivalence.label}</p>
                      <p className="text-slate-100">{equivalence.value.toLocaleString("en-US")}</p>
                      <p className="mt-1 text-xs text-slate-400">{equivalence.description}</p>
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
