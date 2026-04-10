import { t } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";

type GlobeLegendProps = {
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
  selectedBand?: "all" | "low" | "mid" | "high";
  onBandChange?: (band: "all" | "low" | "mid" | "high") => void;
  mode?: "debt_pct_gdp" | "total_external_debt_usd_log";
  availableCountries?: number;
  totalCountries?: number;
};

const BAND_OPTIONS: Array<{ key: "all" | "low" | "mid" | "high"; labelKey: "all" | "low" | "medium" | "high" }> = [
  { key: "all", labelKey: "all" },
  { key: "low", labelKey: "low" },
  { key: "mid", labelKey: "medium" },
  { key: "high", labelKey: "high" },
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
  const locale = useLocaleStore((state) => state.locale);
  const isRatioMode = mode === "debt_pct_gdp";
  const leftLabel = isRatioMode ? `${minDebtPctGdp.toFixed(1)}%` : `${Math.pow(10, minDebtPctGdp).toExponential(1)} USD`;
  const rightLabel = isRatioMode ? `${maxDebtPctGdp.toFixed(1)}%` : `${Math.pow(10, maxDebtPctGdp).toExponential(1)} USD`;

  return (
    <aside className="glass-panel rounded-xl p-4 text-xs text-[#c8c7c2] shadow-lg">
      <p className="mb-2 font-semibold text-[#f5f4f0]">
        {isRatioMode ? t(locale, "debtIntensityTitle") : t(locale, "debtIntensityFallbackTitle")}
      </p>
      <div className="mb-2 h-3 w-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500" />
      <div className="mono-meta flex items-center justify-between text-[11px] text-[#888680]">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>

      {typeof availableCountries === "number" && typeof totalCountries === "number" && (
        <p className="mt-2 text-[11px] text-[#888680]">
          {t(locale, "dataCoverage")}: {availableCountries}/{totalCountries}
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
                  ? "border-[#7c6af5] bg-[#7c6af5]/20 text-[#ede9fe]"
                  : "border-[#3b4252] bg-[#0d1017]/70 text-[#c8c7c2] hover:border-[#6d7280]"
              }`}
            >
              {t(locale, option.labelKey)}
            </button>
          );
        })}
      </div>
    </aside>
  );
}
