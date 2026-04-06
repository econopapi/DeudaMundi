import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { t, trRegion } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";
import type { CountryDetailResponse } from "../../types/api";
import { MetricCounter } from "./MetricCounter";

type CountryHeroProps = {
  country: CountryDetailResponse;
};

export function CountryHero({ country }: CountryHeroProps) {
  const locale = useLocaleStore((state) => state.locale);
  const hasMissingCoreRatios = country.debt_pct_gdp === null || country.debt_per_capita_usd === null;

  return (
    <section className="glass-panel rounded-2xl p-5 md:p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="mono-meta text-xs uppercase tracking-[0.18em] text-[#a594f9]">{t(locale, "countryProfile")}</p>
          <h2 className="display-title mt-2 text-2xl font-bold text-[#f5f4f0] md:text-3xl">{country.name_en}</h2>
          <p className="mt-1 text-sm text-[#888680]">{country.name_es}</p>
        </div>

        <div className="flex flex-wrap gap-2 text-xs text-[#c8c7c2]">
          <span className="rounded-full border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1">ISO3: {country.iso3}</span>
          <span className="rounded-full border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1">ISO2: {country.iso2}</span>
          <span className="rounded-full border border-[#3b4252] bg-[#0d1017]/80 px-3 py-1">
            {t(locale, "region")}: {country.region ? trRegion(locale, country.region) : t(locale, "notAvailable")}
          </span>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCounter label={t(locale, "debtLabel")} value={country.total_external_debt_usd} formatter={formatUsdCompact} />
        <MetricCounter label={t(locale, "debtPerCapitaLabel")} value={country.debt_per_capita_usd} formatter={formatUsdCompact} />
        <MetricCounter label={t(locale, "debtToGdpLabel")} value={country.debt_pct_gdp} formatter={formatPercentage} />
        <MetricCounter label={t(locale, "latestYear")} value={country.latest_year} formatter={(value) => (value ? String(Math.round(value)) : "N/A")} />
      </div>

      {hasMissingCoreRatios && (
        <p className="mt-4 text-xs text-amber-300">
          {t(locale, "missingRatios")}
        </p>
      )}
    </section>
  );
}
