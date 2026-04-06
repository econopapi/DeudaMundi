import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { CountryHero } from "../components/country/CountryHero";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { fetchCountryDetail } from "../services/deudamundiApi";
import type { CountryDetailResponse } from "../types/api";

export function CountryDetailPage() {
  const { iso3 = "" } = useParams();
  const [country, setCountry] = useState<CountryDetailResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "error" | "ready">("loading");

  useEffect(() => {
    let cancelled = false;

    async function loadCountry() {
      setStatus("loading");
      try {
        const response = await fetchCountryDetail(iso3);
        if (!cancelled) {
          setCountry(response);
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

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-8">
      <header className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-semibold text-slate-100 md:text-3xl">Country detail · {iso3.toUpperCase()}</h1>
        <p className="mt-2 text-sm text-slate-400">Vista inicial del país conectada a GET /api/v1/countries/{"{iso3}"}.</p>
      </header>

      <Link to="/" className="text-sm text-sky-300 hover:text-sky-200">
        ← Back to globe
      </Link>

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

          <section className="grid gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-6 md:grid-cols-2">
            <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
              <h2 className="text-sm font-semibold text-slate-300">Debt metrics</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                <li>Total debt: {formatUsdCompact(country.total_external_debt_usd)}</li>
                <li>Debt per capita: {formatUsdCompact(country.debt_per_capita_usd)}</li>
                <li>Debt / GDP: {formatPercentage(country.debt_pct_gdp)}</li>
                <li>GDP: {formatUsdCompact(country.gdp_usd)}</li>
                <li>Latest year: {country.latest_year ?? "N/A"}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
              <h2 className="text-sm font-semibold text-slate-300">Country info</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-200">
                <li>Name (EN): {country.name_en}</li>
                <li>Name (ES): {country.name_es}</li>
                <li>ISO2: {country.iso2}</li>
                <li>Region: {country.region ?? "N/A"}</li>
                <li>Subregion: {country.subregion ?? "N/A"}</li>
                <li>Population: {country.population?.toLocaleString("en-US") ?? "N/A"}</li>
                <li>Capital: {country.capital ?? "N/A"}</li>
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
