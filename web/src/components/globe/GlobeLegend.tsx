type GlobeLegendProps = {
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
  selectedBand?: "all" | "low" | "mid" | "high";
  onBandChange?: (band: "all" | "low" | "mid" | "high") => void;
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
}: GlobeLegendProps) {
  return (
    <aside className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300 shadow-lg backdrop-blur">
      <p className="mb-2 font-semibold text-slate-100">Debt % GDP intensity</p>
      <div className="mb-2 h-3 w-40 rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500" />
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>{minDebtPctGdp.toFixed(1)}%</span>
        <span>{maxDebtPctGdp.toFixed(1)}%</span>
      </div>

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
