type GlobeLegendProps = {
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
  selectedBand?: "all" | "low" | "mid" | "high";
  onBandChange?: (band: "all" | "low" | "mid" | "high") => void;
  mode?: "debt_pct_gdp" | "total_external_debt_usd_log";
  availableCountries?: number;
  totalCountries?: number;
};

const BAND_OPTIONS: Array<{ key: "all" | "low" | "mid" | "high"; label: string }> = [
  { key: "all", label: "All" },
  { key: "low", label: "Low" },
  { key: "mid", label: "Medium" },
  { key: "high", label: "High" },
];

export function GlobeLegend({
  minDebtPctGdp,
  maxDebtPctGdp,
  selectedBand = "all",
  onBandChange,
  mode = "debt_pct_gdp",
  availableCountries,
  totalCountries,
}: GlobeLegendProps) {
  const isRatioMode = mode === "debt_pct_gdp";
  const leftLabel = isRatioMode ? `${minDebtPctGdp.toFixed(1)}%` : `${Math.pow(10, minDebtPctGdp).toExponential(1)} USD`;
  const rightLabel = isRatioMode ? `${maxDebtPctGdp.toFixed(1)}%` : `${Math.pow(10, maxDebtPctGdp).toExponential(1)} USD`;

  return (
    <aside className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300 shadow-lg backdrop-blur">
      <p className="mb-2 font-semibold text-slate-100">
        {isRatioMode ? "Debt % GDP intensity" : "Debt intensity (fallback: total debt)"}
      </p>
      <div className="mb-2 h-3 w-40 rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500" />
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>

      {typeof availableCountries === "number" && typeof totalCountries === "number" && (
        <p className="mt-2 text-[11px] text-slate-400">
          Data coverage: {availableCountries}/{totalCountries} countries
        </p>
      )}

      <div className="mt-3 flex flex-wrap gap-2">
        {BAND_OPTIONS.map((option) => {
          const isActive = selectedBand === option.key;

          return (
            <button
              key={option.key}
              type="button"
              aria-pressed={isActive}
              onClick={() => onBandChange?.(option.key)}
              className={`rounded-md border px-2 py-1 text-[11px] transition ${
                isActive
                  ? "border-sky-400 bg-sky-500/20 text-sky-200"
                  : "border-slate-700 bg-slate-950/40 text-slate-300 hover:border-slate-500"
              }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </aside>
  );
}
