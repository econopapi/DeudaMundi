import { extent, max, min, scaleLinear } from "d3";
import { useMemo } from "react";

import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { t } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";
import type { CountryCompareItem } from "../../types/api";

type CountryComparisonChartProps = {
  countries: CountryCompareItem[];
};

type SeriesPoint = {
  year: number;
  debtUsd: number | null;
  debtPctGdp: number | null;
};

type CountrySeries = {
  iso3: string;
  name: string;
  color: string;
  points: SeriesPoint[];
};

const CHART_WIDTH = 1040;
const CHART_HEIGHT = 380;
const MARGIN = {
  top: 24,
  right: 76,
  bottom: 38,
  left: 88,
};

const SERIES_COLORS = ["#22d3ee", "#f59e0b", "#a78bfa", "#34d399", "#f472b6", "#60a5fa"];

function isFiniteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function buildLinePath(
  points: SeriesPoint[],
  xScale: (year: number) => number,
  yScale: (value: number) => number,
  accessor: (point: SeriesPoint) => number | null,
): string {
  let path = "";
  let activeSegment = false;

  points.forEach((point) => {
    const value = accessor(point);
    if (!isFiniteNumber(value)) {
      activeSegment = false;
      return;
    }

    const command = activeSegment ? "L" : "M";
    path += `${command}${xScale(point.year)},${yScale(value)} `;
    activeSegment = true;
  });

  return path.trim();
}

export function CountryComparisonChart({ countries }: CountryComparisonChartProps) {
  const locale = useLocaleStore((state) => state.locale);

  const series = useMemo<CountrySeries[]>(() => {
    return countries.map((country, index) => {
      const points = [...country.history]
        .sort((a, b) => a.year - b.year)
        .map((item) => ({
          year: item.year,
          debtUsd: item.debt_stock_usd ?? item.total_external_debt_usd,
          debtPctGdp: item.debt_pct_gdp,
        }));

      return {
        iso3: country.detail.iso3,
        name: country.detail.name_en,
        color: SERIES_COLORS[index % SERIES_COLORS.length],
        points,
      };
    });
  }, [countries]);

  const allPoints = series.flatMap((country) => country.points);
  if (allPoints.length === 0) {
    return (
      <section className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4 text-sm text-[#888680]">
        {t(locale, "noHistoricalSeries")}
      </section>
    );
  }

  const yearDomain = extent(allPoints, (point) => point.year) as [number, number];
  const maxDebtUsd = max(allPoints, (point) => (isFiniteNumber(point.debtUsd) ? point.debtUsd : null)) ?? 0;
  const pctValues = allPoints.map((point) => point.debtPctGdp).filter(isFiniteNumber);

  const pctMin = (pctValues.length > 0 ? min(pctValues) : null) ?? 0;
  const pctMax = (pctValues.length > 0 ? max(pctValues) : null) ?? 1;
  const safePctMax = pctMin === pctMax ? pctMax + 1 : pctMax;
  const hasPctSeries = pctValues.length > 0;

  const x = scaleLinear()
    .domain(yearDomain)
    .range([MARGIN.left, CHART_WIDTH - MARGIN.right]);

  const yDebt = scaleLinear()
    .domain([0, maxDebtUsd])
    .nice()
    .range([CHART_HEIGHT - MARGIN.bottom, MARGIN.top]);

  const yPct = scaleLinear()
    .domain([pctMin, safePctMax])
    .nice()
    .range([CHART_HEIGHT - MARGIN.bottom, MARGIN.top]);

  const yDebtTicks = yDebt.ticks(4);
  const yPctTicks = hasPctSeries ? yPct.ticks(4) : [];
  const xTicks = x.ticks(7).map((tick) => Math.round(tick));

  return (
    <section className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4">
      <header className="mb-3 flex flex-col gap-1">
        <h3 className="text-sm font-semibold text-[#f5f4f0]">{t(locale, "compareChartTitle")}</h3>
        <p className="text-xs text-[#888680]">{t(locale, "compareChartSubtitle")}</p>
      </header>

      <div className="mb-3 flex flex-wrap gap-3 text-xs text-[#c8c7c2]">
        {series.map((countrySeries) => (
          <span key={countrySeries.iso3} className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: countrySeries.color }} />
            {countrySeries.name} ({countrySeries.iso3})
          </span>
        ))}
      </div>

      <div className="mb-3 flex flex-wrap gap-4 text-xs text-[#94a3b8]">
        <span className="inline-flex items-center gap-2">
          <span className="h-0.5 w-6 bg-[#f5f4f0]" />
          {t(locale, "debtLabel")}
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-0.5 w-6 border-t border-dashed border-[#f5f4f0]" />
          {t(locale, "debtToGdpLabel")}
        </span>
      </div>

      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="min-w-[860px]" role="img" aria-label="Countries comparison chart">
          {yDebtTicks.map((tick) => (
            <g key={`y-debt-${tick}`}>
              <line
                x1={MARGIN.left}
                y1={yDebt(tick)}
                x2={CHART_WIDTH - MARGIN.right}
                y2={yDebt(tick)}
                stroke="rgba(148, 163, 184, 0.2)"
                strokeDasharray="4 4"
              />
              <text x={MARGIN.left - 10} y={yDebt(tick) + 4} textAnchor="end" fontSize={11} fill="#94a3b8">
                {formatUsdCompact(tick)}
              </text>
            </g>
          ))}

          {yPctTicks.map((tick) => (
            <g key={`y-pct-${tick}`}>
              <text x={CHART_WIDTH - MARGIN.right + 10} y={yPct(tick) + 4} textAnchor="start" fontSize={11} fill="#94a3b8">
                {formatPercentage(tick)}
              </text>
            </g>
          ))}

          {xTicks.map((tick) => (
            <g key={`x-${tick}`}>
              <line
                x1={x(tick)}
                y1={CHART_HEIGHT - MARGIN.bottom}
                x2={x(tick)}
                y2={CHART_HEIGHT - MARGIN.bottom + 6}
                stroke="rgba(148, 163, 184, 0.4)"
              />
              <text x={x(tick)} y={CHART_HEIGHT - MARGIN.bottom + 20} textAnchor="middle" fontSize={11} fill="#94a3b8">
                {tick}
              </text>
            </g>
          ))}

          {series.map((countrySeries) => {
            const debtPath = buildLinePath(countrySeries.points, x, yDebt, (point) => point.debtUsd);
            const pctPath = buildLinePath(countrySeries.points, x, yPct, (point) => point.debtPctGdp);

            return (
              <g key={`series-${countrySeries.iso3}`}>
                {debtPath && <path d={debtPath} fill="none" stroke={countrySeries.color} strokeWidth={2.5} />}
                {pctPath && (
                  <path
                    d={pctPath}
                    fill="none"
                    stroke={countrySeries.color}
                    strokeWidth={1.8}
                    strokeDasharray="6 4"
                    opacity={0.9}
                  />
                )}
              </g>
            );
          })}

          <line
            x1={MARGIN.left}
            y1={CHART_HEIGHT - MARGIN.bottom}
            x2={CHART_WIDTH - MARGIN.right}
            y2={CHART_HEIGHT - MARGIN.bottom}
            stroke="rgba(148, 163, 184, 0.6)"
          />
          <line
            x1={MARGIN.left}
            y1={MARGIN.top}
            x2={MARGIN.left}
            y2={CHART_HEIGHT - MARGIN.bottom}
            stroke="rgba(148, 163, 184, 0.6)"
          />
          <line
            x1={CHART_WIDTH - MARGIN.right}
            y1={MARGIN.top}
            x2={CHART_WIDTH - MARGIN.right}
            y2={CHART_HEIGHT - MARGIN.bottom}
            stroke="rgba(148, 163, 184, 0.6)"
          />
        </svg>
      </div>
    </section>
  );
}
