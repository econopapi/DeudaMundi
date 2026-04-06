import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { useGlobeStore } from "../../store/globeStore";

export function CountryTooltip() {
  const hoveredCountry = useGlobeStore((state) => state.hoveredCountry);

  if (!hoveredCountry) {
    return null;
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950/90 p-4 text-sm text-slate-200 shadow-xl backdrop-blur">
      <p className="font-semibold text-slate-100">{hoveredCountry.name}</p>
      <div className="mt-2 space-y-1 text-xs text-slate-300">
        <p>ISO3: {hoveredCountry.iso3}</p>
        <p>Total debt: {formatUsdCompact(hoveredCountry.debtTotalUsd)}</p>
        <p>Debt / GDP: {formatPercentage(hoveredCountry.debtPctGdp)}</p>
      </div>
    </div>
  );
}
