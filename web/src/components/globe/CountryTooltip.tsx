import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { t } from "../../lib/translations";
import { useGlobeStore } from "../../store/globeStore";
import { useLocaleStore } from "../../store/localeStore";

export function CountryTooltip() {
  const hoveredCountry = useGlobeStore((state) => state.hoveredCountry);
  const locale = useLocaleStore((state) => state.locale);

  if (!hoveredCountry) {
    return null;
  }

  return (
    <div className="glass-panel rounded-xl p-4 text-sm text-[#c8c7c2] shadow-xl">
      <p className="font-semibold text-[#f5f4f0]">{hoveredCountry.name}</p>
      <div className="mt-2 space-y-1 text-xs text-[#c8c7c2]">
        <p>ISO3: {hoveredCountry.iso3}</p>
        <p>{t(locale, "debtLabel")}: {formatUsdCompact(hoveredCountry.debtTotalUsd)}</p>
        <p>{t(locale, "debtToGdpLabel")}: {formatPercentage(hoveredCountry.debtPctGdp)}</p>
      </div>
    </div>
  );
}
