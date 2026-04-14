import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { CountryTooltip } from "../components/globe/CountryTooltip";
import { GlobeLegend } from "../components/globe/GlobeLegend";
import { LoadingPanel } from "../components/ui/LoadingPanel";
import { formatPercentage, formatUsdCompact } from "../lib/formatters";
import { HOME_REGION_OPTIONS, isHomeRegion } from "../lib/regions";
import { t, trRegion } from "../lib/translations";
import { isWebGlAvailable } from "../lib/webgl";
import { fetchGlobeData } from "../services/deudamundiApi";
import { useGlobeStore } from "../store/globeStore";
import { useLocaleStore } from "../store/localeStore";
import type { GlobeDataPoint } from "../types/api";
import { percentile, COLOR_SCALE_CAP_PERCENTILE } from "../components/globe/globeColors";

const GlobeScene = lazy(async () => import("../components/globe/GlobeScene").then((mod) => ({ default: mod.GlobeScene })));

type DebtBand = "all" | "low" | "mid" | "high";

type IntensityMode = "debt_pct_gdp" | "total_external_debt_usd_log";

type IntensityMeta = {
  min: number;
  max: number;
  mode: IntensityMode;
  availableCount: number;
  totalCount: number;
};

const LATAM_REGION = "Latin America & Caribbean";
const MAX_COMPARE_SUGGESTIONS = 5;
const PROJECT_DOCUMENTATION_URL = "https://econopapi.com/proyectos/deudamundi";
const SOURCE_CODE_URL = "https://github.com/econopapi/DeudaMundi";
const PREFERRED_COMPARE_PAIRS: ReadonlyArray<readonly [string, string]> = [
  ["MEX", "BRA"],
  ["BRA", "ARG"],
  ["URY", "ARG"],
  ["USA", "JPN"],
  ["USA", "GBR"],
];

type CompareSuggestion = {
  href: string;
  label: string;
};

function getIntensityValue(point: GlobeDataPoint, mode: IntensityMode): number | null {
  if (mode === "debt_pct_gdp") {
    const ratio = point.debt_pct_gdp;
    return ratio !== null && Number.isFinite(ratio) ? ratio : null;
  }

  const totalDebt = point.debt_stock_usd ?? point.total_external_debt_usd;
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
      max: percentile(ratioValues, COLOR_SCALE_CAP_PERCENTILE),
      mode: "debt_pct_gdp",
      availableCount: ratioValues.length,
      totalCount: points.length,
    };
  }

  const debtValues = points
    .map((point) => point.debt_stock_usd ?? point.total_external_debt_usd)
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

export function buildSuggestedComparePairs(points: GlobeDataPoint[]): CompareSuggestion[] {
  const debtPoints = points
    .map((point) => ({
      ...point,
      debtValue: point.debt_stock_usd ?? point.total_external_debt_usd,
    }))
    .filter(
      (point): point is GlobeDataPoint & { debtValue: number } =>
        point.debtValue !== null && Number.isFinite(point.debtValue) && point.debtValue > 0,
    );

  if (debtPoints.length < 2) {
    return [];
  }

  const byIso3 = new Map(debtPoints.map((point) => [point.iso3, point]));
  const suggestions: CompareSuggestion[] = [];
  const seenPairs = new Set<string>();

  const addPair = (leftIso3: string, rightIso3: string) => {
    if (leftIso3 === rightIso3 || suggestions.length >= MAX_COMPARE_SUGGESTIONS) {
      return;
    }

    const left = byIso3.get(leftIso3);
    const right = byIso3.get(rightIso3);
    if (!left || !right) {
      return;
    }

    const dedupeKey = [left.iso3, right.iso3].sort().join("-");
    if (seenPairs.has(dedupeKey)) {
      return;
    }

    seenPairs.add(dedupeKey);
    const params = new URLSearchParams({ countries: `${left.iso3},${right.iso3}` });
    suggestions.push({
      href: `/compare?${params.toString()}`,
      label: `${left.name_en} vs ${right.name_en}`,
    });
  };

  for (const [leftIso3, rightIso3] of PREFERRED_COMPARE_PAIRS) {
    addPair(leftIso3, rightIso3);
  }

  const latamPoints = debtPoints
    .filter((point) => point.region === LATAM_REGION)
    .sort((a, b) => b.debtValue - a.debtValue);

  for (let i = 0; i < latamPoints.length; i += 1) {
    for (let j = i + 1; j < latamPoints.length; j += 1) {
      addPair(latamPoints[i].iso3, latamPoints[j].iso3);
      if (suggestions.length >= MAX_COMPARE_SUGGESTIONS) {
        break;
      }
    }
    if (suggestions.length >= MAX_COMPARE_SUGGESTIONS) {
      break;
    }
  }

  const globalPoints = [...debtPoints].sort((a, b) => b.debtValue - a.debtValue);
  for (let i = 1; i < globalPoints.length; i += 1) {
    addPair(globalPoints[0].iso3, globalPoints[i].iso3);
    if (suggestions.length >= MAX_COMPARE_SUGGESTIONS) {
      break;
    }
  }

  return suggestions;
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
  const region = isHomeRegion(regionFromUrl) ? regionFromUrl : "";

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
  const topDebtPairs = useMemo(() => buildSuggestedComparePairs(points), [points]);
  const highlightedIso3Set = useMemo(() => new Set(filteredPoints.map((point) => point.iso3)), [filteredPoints]);

  useEffect(() => {
    setHoveredCountry(null);
  }, [debtBand, region, setHoveredCountry]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <AppHeader
        title={t(locale, "homeTitle")}
        subtitle={t(locale, "homeSubtitle")}
        actions={(
          <>
            <a
              href={PROJECT_DOCUMENTATION_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center rounded-lg border border-[#7c6af5] bg-[#7c6af5]/20 px-4 py-2 text-sm font-medium text-[#f5f4f0] transition hover:bg-[#7c6af5]/30"
            >
              {t(locale, "homeCtaPrimary")}
            </a>
            <a
              href={SOURCE_CODE_URL}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-[#a594f9] transition hover:text-[#c4b9fa]"
            >
              {t(locale, "homeCtaSecondary")} →
            </a>
          </>
        )}
      />

      {status === "loading" && (
        <LoadingPanel
          message={`${t(locale, "loadingGlobeData")}${region ? ` (${trRegion(locale, region)})` : ""}...`}
          detail="/api/v1/globe-data"
        />
      )}

      {status === "error" && (
        <section className="rounded-xl border border-rose-900/70 bg-rose-950/40 p-8 text-sm text-rose-200">
          {t(locale, "errorGlobeData")}
        </section>
      )}

      {status === "ready" && (
        <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_420px]">
          <div className="relative min-w-0">
            {!webGlAvailable ? (
              <div className="glass-panel rounded-2xl p-4">
                <p className="text-sm font-semibold text-[#f5f4f0]">{t(locale, "webglFallbackTitle")}</p>
                <p className="mt-1 text-xs text-[#888680]">{t(locale, "webglFallbackSubtitle")}</p>

                <div className="mt-4 overflow-auto">
                  <table className="w-full border-collapse text-xs">
                    <thead className="text-left uppercase tracking-wide text-[#888680]">
                      <tr>
                        <th className="px-2 py-2">{t(locale, "country")}</th>
                        <th className="px-2 py-2">{t(locale, "debtLabel")}</th>
                        <th className="px-2 py-2">{t(locale, "debtToGdpLabel")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {points.slice(0, 20).map((point) => (
                        <tr key={point.iso3} className="border-t border-[#2a2f3a] text-[#f5f4f0]">
                          <td className="px-2 py-2">
                            <Link className="text-[#a594f9] hover:text-[#c4b9fa]" to={`/country/${point.iso3.toLowerCase()}`}>
                              {point.name_en} ({point.iso3})
                            </Link>
                          </td>
                          <td className="px-2 py-2">{formatUsdCompact(point.debt_stock_usd ?? point.total_external_debt_usd)}</td>
                          <td className="px-2 py-2">{formatPercentage(point.debt_pct_gdp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <Suspense
                fallback={
                  <LoadingPanel
                    message={`${t(locale, "loadingGlobeModule")}...`}
                    className="h-[380px] sm:h-[460px] md:h-[520px] lg:h-[560px]"
                  />
                }
              >
                <GlobeScene
                  points={points}
                  selectedBand={debtBand}
                  highlightedIso3Set={highlightedIso3Set}
                  selectedRegion={region || undefined}
                  autoRotateEnabled={!region}
                />
              </Suspense>
            )}
            <div className="pointer-events-none absolute left-4 top-4">
              <CountryTooltip />
            </div>
          </div>

          <div className="flex w-full flex-col gap-3 lg:w-[420px]">
            <section className="glass-panel rounded-xl p-4">
              <div className="mb-4 flex items-center justify-between gap-3 text-sm">
                <LanguageSwitcher />
                <Link to="/rankings" className="font-medium text-[#a594f9] hover:text-[#c4b9fa]">
                  {t(locale, "viewGlobalRankings")} →
                </Link>
              </div>

              <label
                htmlFor="region-filter"
                className="mono-meta mb-2 block text-xs font-semibold uppercase tracking-wide text-[#c8c7c2]"
              >
                {t(locale, "regionFilter")}
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
                className="w-full rounded-lg border border-[#3b4252] bg-[#0d1017] px-3 py-2 text-sm text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
              >
                <option value="">{t(locale, "allRegions")}</option>
                {HOME_REGION_OPTIONS.map((regionOption) => (
                  <option key={regionOption} value={regionOption}>
                    {trRegion(locale, regionOption)}
                  </option>
                ))}
              </select>
            </section>

            <section className="relative overflow-hidden rounded-xl border border-[#4f46e5]/40 bg-gradient-to-br from-[#1a103d] via-[#151b3b] to-[#0d1017] p-4 shadow-[0_18px_50px_-30px_rgba(124,106,245,0.8)]">
              <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-[#7c6af5]/20 blur-2xl" />
              <div className="pointer-events-none absolute -bottom-10 -left-8 h-28 w-28 rounded-full bg-[#22d3ee]/15 blur-2xl" />

              <p className="relative mono-meta text-[11px] uppercase tracking-[0.2em] text-[#c4b9fa]">{t(locale, "compareCta")}</p>
              <h3 className="relative mt-1 text-base font-semibold text-[#f5f4f0]">{t(locale, "compareTitle")}</h3>
              <p className="relative mt-1 text-xs leading-relaxed text-[#c8c7c2]">{t(locale, "compareSubtitle")}</p>

              <Link
                to="/compare"
                className="relative mt-3 inline-flex w-full items-center justify-center rounded-lg border border-[#7c6af5] bg-[#7c6af5]/25 px-3 py-2 text-sm font-medium text-[#f5f4f0] transition hover:bg-[#7c6af5]/35"
              >
                {t(locale, "compareRun")} →
              </Link>

              {topDebtPairs.length > 0 && (
                <div className="relative mt-3 flex flex-wrap gap-2">
                  {topDebtPairs.map((pair) => (
                    <Link
                      key={pair.href}
                      to={pair.href}
                      className="whitespace-nowrap rounded-full border border-[#3b4252] bg-[#0b0f1c]/75 px-3 py-1 text-[11px] text-[#e5e7eb] hover:border-[#7c6af5]"
                    >
                      {pair.label}
                    </Link>
                  ))}
                </div>
              )}
            </section>

            <GlobeLegend
              minDebtPctGdp={intensityMeta.min}
              maxDebtPctGdp={intensityMeta.max}
              selectedBand={debtBand}
              onBandChange={setDebtBand}
              mode={intensityMeta.mode}
              availableCountries={intensityMeta.availableCount}
              totalCountries={intensityMeta.totalCount}
            />
            <div className="glass-panel rounded-xl p-4 text-xs text-[#c8c7c2]">
              <p className="font-semibold text-[#f5f4f0]">{t(locale, "interactionTitle")}</p>
              <ul className="mt-2 list-disc space-y-1 pl-4">
                <li>{t(locale, "interactionDrag")}</li>
                <li>{t(locale, "interactionZoom")}</li>
                <li>{t(locale, "interactionHover")}</li>
                <li>{t(locale, "interactionClick")}</li>
                <li>{t(locale, "interactionBand")}</li>
              </ul>
              <p className="mt-3 text-[11px] text-[#888680]">{t(locale, "visibleCountries")}: {points.length}</p>
              <p className="mt-1 text-[11px] text-[#888680]">{t(locale, "highlightedCountries")}: {filteredPoints.length}</p>
              {debtBand !== "all" && filteredPoints.length === 0 && (
                <p className="mt-2 text-[11px] text-amber-300">{t(locale, "noCountriesBand")}</p>
              )}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
