import { useEffect, useMemo, useState } from "react";

import { AppHeader } from "../components/AppHeader";
import { CountryTooltip } from "../components/globe/CountryTooltip";
import { GlobeLegend } from "../components/globe/GlobeLegend";
import { GlobeScene } from "../components/globe/GlobeScene";
import { fetchGlobeData } from "../services/deudamundiApi";
import type { GlobeDataPoint } from "../types/api";

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

export function HomePage() {
  const [points, setPoints] = useState<GlobeDataPoint[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "ready">("idle");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setStatus("loading");
      try {
        const response = await fetchGlobeData();
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
  }, []);

  const debtRange = useMemo(() => getDebtRange(points), [points]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <AppHeader
        title="DeudaMundi · Global Debt Atlas"
        subtitle="Fase 2 MVP: globo 3D interactivo con intensidad por deuda/PIB y navegación por país."
      />

      {status === "loading" && (
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-8 text-sm text-slate-300">
          Loading globe data from API...
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
            <GlobeScene points={points} />
            <div className="pointer-events-none absolute left-4 top-4">
              <CountryTooltip />
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <GlobeLegend minDebtPctGdp={debtRange.min} maxDebtPctGdp={debtRange.max} />
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300">
              <p className="font-semibold text-slate-100">Interaction</p>
              <ul className="mt-2 list-disc space-y-1 pl-4">
                <li>Drag to rotate the globe.</li>
                <li>Scroll to zoom in/out.</li>
                <li>Hover a marker to inspect debt metrics.</li>
                <li>Click a marker to open country detail.</li>
              </ul>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
