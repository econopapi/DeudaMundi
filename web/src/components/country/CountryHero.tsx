import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import type { CountryDetailResponse } from "../../types/api";
import { MetricCounter } from "./MetricCounter";

type CountryHeroProps = {
  country: CountryDetailResponse;
};

export function CountryHero({ country }: CountryHeroProps) {
  const hasMissingCoreRatios = country.debt_pct_gdp === null || country.debt_per_capita_usd === null;

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 md:p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-sky-300">Country profile</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-100 md:text-3xl">{country.name_en}</h2>
          <p className="mt-1 text-sm text-slate-400">{country.name_es}</p>
        </div>

        <div className="flex flex-wrap gap-2 text-xs text-slate-300">
          <span className="rounded-full border border-slate-700 bg-slate-950/50 px-3 py-1">ISO3: {country.iso3}</span>
          <span className="rounded-full border border-slate-700 bg-slate-950/50 px-3 py-1">ISO2: {country.iso2}</span>
          <span className="rounded-full border border-slate-700 bg-slate-950/50 px-3 py-1">
            Region: {country.region ?? "Not available"}
          </span>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCounter label="Total debt" value={country.total_external_debt_usd} formatter={formatUsdCompact} />
        <MetricCounter label="Debt per capita" value={country.debt_per_capita_usd} formatter={formatUsdCompact} />
        <MetricCounter label="Debt / GDP" value={country.debt_pct_gdp} formatter={formatPercentage} />
        <MetricCounter label="Latest year" value={country.latest_year} formatter={(value) => (value ? String(Math.round(value)) : "N/A")} />
      </div>

      {hasMissingCoreRatios && (
        <p className="mt-4 text-xs text-amber-300">
          Some ratio indicators are currently unavailable in the source dataset for the latest year.
        </p>
      )}
    </section>
  );
}
