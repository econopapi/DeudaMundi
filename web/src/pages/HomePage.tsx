import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { CountryTooltip } from "../components/globe/CountryTooltip";
import { GlobeLegend } from "../components/globe/GlobeLegend";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { t } from "../lib/translations";
import { isWebGlAvailable } from "../lib/webgl";
import { fetchGlobeData } from "../services/deudamundiApi";
import { useGlobeStore } from "../store/globeStore";
import { useLocaleStore } from "../store/localeStore";
import type { GlobeDataPoint } from "../types/api";

const GlobeScene = lazy(async () => import("../components/globe/GlobeScene").then((mod) => ({ default: mod.GlobeScene })));

const REGION_OPTIONS = [
  { value: "", label: "All regions" },
  { value: "East Asia & Pacific", label: "East Asia & Pacific" },
  { value: "Europe & Central Asia", label: "Europe & Central Asia" },
  { value: "Latin America & Caribbean", label: "Latin America & Caribbean" },
  { value: "Middle East & North Africa", label: "Middle East & North Africa" },
  { value: "North America", label: "North America" },
  { value: "South Asia", label: "South Asia" },
  { value: "Sub-Saharan Africa", label: "Sub-Saharan Africa" },
];

type DebtBand = "all" | "low" | "mid" | "high";

type IntensityMode = "debt_pct_gdp" | "total_external_debt_usd_log";

type IntensityMeta = {
  min: number;
  max: number;
  mode: IntensityMode;
  availableCount: number;
  totalCount: number;
};

function getIntensityValue(point: GlobeDataPoint, mode: IntensityMode): number | null {
  if (mode === "debt_pct_gdp") {
    const ratio = point.debt_pct_gdp;
    return ratio !== null && Number.isFinite(ratio) ? ratio : null;
  }

  const totalDebt = point.total_external_debt_usd;
  if (totalDebt === null || !Number.isFinite(totalDebt) || totalDebt <= 0) {
    return null;
  }

  return Math.log10(totalDebt);
}

function getIntensityMeta(points: GlobeDataPoint[]): IntensityMeta {
  const ratioValues = points
    .map((point) => point.debt_pct_gdp)
    .filter((value): value is number => value !== null && Number.isFinite(value));

  if (ratioValues.length > 0) {
    return {
      min: Math.min(...ratioValues),
      max: Math.max(...ratioValues),
      mode: "debt_pct_gdp",
      availableCount: ratioValues.length,
      totalCount: points.length,
    };
  }

  const debtValues = points
    .map((point) => point.total_external_debt_usd)
    .filter((value): value is number => value !== null && Number.isFinite(value) && value > 0)
    .map((value) => Math.log10(value));

  if (debtValues.length === 0) {
    return {
      min: 0,
      max: 1,
      mode: "debt_pct_gdp",
      availableCount: 0,
      totalCount: points.length,
    };
  }

  return {
    min: Math.min(...debtValues),
    max: Math.max(...debtValues),
    mode: "total_external_debt_usd_log",
    availableCount: debtValues.length,
    totalCount: points.length,
  };
}

function filterPointsByDebtBand(points: GlobeDataPoint[], debtBand: DebtBand, intensityMeta: IntensityMeta): GlobeDataPoint[] {
  const { min, max, mode } = intensityMeta;

  if (debtBand === "all" || max <= min) {
    return points;
  }

  const oneThird = (max - min) / 3;
  const lowLimit = min + oneThird;
  const midLimit = min + oneThird * 2;

  return points.filter((point) => {
    const value = getIntensityValue(point, mode);
    if (value === null) {
      return false;
    }

    if (debtBand === "low") {
      return value <= lowLimit;
    }

    if (debtBand === "mid") {
      return value > lowLimit && value <= midLimit;
    }

    return value > midLimit;
  });
}

export function HomePage() {
  const setHoveredCountry = useGlobeStore((state) => state.setHoveredCountry);
  const locale = useLocaleStore((state) => state.locale);
  const [searchParams, setSearchParams] = useSearchParams();
  const [points, setPoints] = useState<GlobeDataPoint[]>([]);
  const [debtBand, setDebtBand] = useState<DebtBand>("all");
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "ready">("idle");
  const webGlAvailable = useMemo(() => isWebGlAvailable(), []);

  const regionFromUrl = searchParams.get("region") ?? "";
  const region = REGION_OPTIONS.some((option) => option.value === regionFromUrl) ? regionFromUrl : "";

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setStatus("loading");
      try {
        const response = await fetchGlobeData(region || undefined);
        if (!cancelled) {
          setPoints(response.items);
          setStatus("ready");
        }
      } catch (error) {
        if (!cancelled) {
          setStatus("error");
        }
      }
    }

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [region]);

  const intensityMeta = useMemo(() => getIntensityMeta(points), [points]);
  const filteredPoints = useMemo(
    () => filterPointsByDebtBand(points, debtBand, intensityMeta),
    [points, debtBand, intensityMeta],
  );

  useEffect(() => {
    setHoveredCountry(null);
  }, [debtBand, region, setHoveredCountry]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <AppHeader
        title={t(locale, "homeTitle")}
        subtitle={t(locale, "homeSubtitle")}
      />

      <div className="flex items-center justify-between text-sm">
        <LanguageSwitcher />
        <Link to="/rankings" className="text-sky-300 hover:text-sky-200">
          {t(locale, "viewGlobalRankings")} →
        </Link>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
        <label htmlFor="region-filter" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-300">
          Region filter
        </label>
        <select
          id="region-filter"
          name="region"
          value={region}
          onChange={(event) => {
            const value = event.target.value;
            const nextParams = new URLSearchParams(searchParams);

            if (value) {
              nextParams.set("region", value);
            } else {
              nextParams.delete("region");
            }

            setSearchParams(nextParams);
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none"
        >
          {REGION_OPTIONS.map((option) => (
            <option key={option.value || "all"} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </section>

      {status === "loading" && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-8 text-sm text-slate-300">
          Loading globe data from API{region ? ` for ${region}` : ""}...
        </section>
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900 bg-rose-950/40 p-8 text-sm text-rose-200">
          Could not load data from `GET /api/v1/globe-data`. Please verify backend availability.
        </section>
      )}

      {status === "ready" && (
        <section className="grid gap-4 lg:grid-cols-[1fr_auto]">
          <div className="relative">
            {!webGlAvailable ? (
              <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                <p className="text-sm font-semibold text-slate-200">{t(locale, "webglFallbackTitle")}</p>
                <p className="mt-1 text-xs text-slate-400">{t(locale, "webglFallbackSubtitle")}</p>

                <div className="mt-4 overflow-auto">
                  <table className="w-full border-collapse text-xs">
                    <thead className="text-left uppercase tracking-wide text-slate-400">
                      <tr>
                        <th className="px-2 py-2">Country</th>
                        <th className="px-2 py-2">Debt</th>
                        <th className="px-2 py-2">Debt / GDP</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPoints.slice(0, 20).map((point) => (
                        <tr key={point.iso3} className="border-t border-slate-800 text-slate-200">
                          <td className="px-2 py-2">
                            <Link className="text-sky-300 hover:text-sky-200" to={`/country/${point.iso3.toLowerCase()}`}>
                              {point.name_en} ({point.iso3})
                            </Link>
                          </td>
                          <td className="px-2 py-2">{formatUsdCompact(point.total_external_debt_usd)}</td>
                          <td className="px-2 py-2">{formatPercentage(point.debt_pct_gdp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : filteredPoints.length === 0 ? (
              <div className="flex h-[560px] items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 px-6 text-center text-sm text-slate-300">
                No countries match the current debt band filter.
              </div>
            ) : (
              <Suspense
                fallback={
                  <div className="flex h-[560px] items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-300">
                    Loading 3D globe module...
                  </div>
                }
              >
                <GlobeScene points={filteredPoints} />
              </Suspense>
            )}
            <div className="pointer-events-none absolute left-4 top-4">
              <CountryTooltip />
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <GlobeLegend
              minDebtPctGdp={intensityMeta.min}
              maxDebtPctGdp={intensityMeta.max}
              selectedBand={debtBand}
              onBandChange={setDebtBand}
              mode={intensityMeta.mode}
              availableCountries={intensityMeta.availableCount}
              totalCountries={intensityMeta.totalCount}
            />
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300">
              <p className="font-semibold text-slate-100">Interaction</p>
              <ul className="mt-2 list-disc space-y-1 pl-4">
                <li>Drag to rotate the globe.</li>
                <li>Scroll to zoom in/out.</li>
                <li>Hover a country area to inspect debt metrics.</li>
                <li>Click a country area to open detail.</li>
                <li>Use legend presets to focus low, medium, or high debt bands.</li>
              </ul>
              <p className="mt-3 text-[11px] text-slate-400">Visible countries: {filteredPoints.length}</p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
