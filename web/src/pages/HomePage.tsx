import { Suspense, lazy, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { AppHeader } from "../components/AppHeader";
import { CountryTooltip } from "../components/globe/CountryTooltip";
import { GlobeLegend } from "../components/globe/GlobeLegend";
import { fetchGlobeData } from "../services/deudamundiApi";
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

function getDebtRange(points: GlobeDataPoint[]): { min: number; max: number } {
  const values = points
    .map((point) => point.debt_pct_gdp)
    .filter((value): value is number => value !== null && Number.isFinite(value));

  if (values.length === 0) {
    return { min: 0, max: 100 };
  }

  return {
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

function filterPointsByDebtBand(points: GlobeDataPoint[], debtBand: DebtBand, min: number, max: number): GlobeDataPoint[] {
  if (debtBand === "all" || max <= min) {
    return points;
  }

  const oneThird = (max - min) / 3;
  const lowLimit = min + oneThird;
  const midLimit = min + oneThird * 2;

  return points.filter((point) => {
    const value = point.debt_pct_gdp;
    if (value === null || !Number.isFinite(value)) {
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
  const [searchParams, setSearchParams] = useSearchParams();
  const [points, setPoints] = useState<GlobeDataPoint[]>([]);
  const [debtBand, setDebtBand] = useState<DebtBand>("all");
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "ready">("idle");

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

  const debtRange = useMemo(() => getDebtRange(points), [points]);
  const filteredPoints = useMemo(
    () => filterPointsByDebtBand(points, debtBand, debtRange.min, debtRange.max),
    [points, debtBand, debtRange.max, debtRange.min],
  );

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <AppHeader
        title="DeudaMundi · Global Debt Atlas"
        subtitle="Fase 2 MVP: globo 3D interactivo con intensidad por deuda/PIB y navegación por país."
      />

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
            <Suspense
              fallback={
                <div className="flex h-[560px] items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-300">
                  Loading 3D globe module...
                </div>
              }
            >
              <GlobeScene points={filteredPoints} />
            </Suspense>
            <div className="pointer-events-none absolute left-4 top-4">
              <CountryTooltip />
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <GlobeLegend
              minDebtPctGdp={debtRange.min}
              maxDebtPctGdp={debtRange.max}
              selectedBand={debtBand}
              onBandChange={setDebtBand}
            />
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300">
              <p className="font-semibold text-slate-100">Interaction</p>
              <ul className="mt-2 list-disc space-y-1 pl-4">
                <li>Drag to rotate the globe.</li>
                <li>Scroll to zoom in/out.</li>
                <li>Hover a marker to inspect debt metrics.</li>
                <li>Click a marker to open country detail.</li>
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
