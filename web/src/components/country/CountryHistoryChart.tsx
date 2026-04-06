import { extent, max, scaleLinear } from "d3";
import { useMemo } from "react";

import { formatUsdCompact } from "../../lib/formatters";
import type { CountryGovernmentItem, CountryHistoryItem } from "../../types/api";

type CountryHistoryChartProps = {
  historyItems: CountryHistoryItem[];
  governments: CountryGovernmentItem[];
};

type GovernmentInterval = {
  leaderName: string;
  startYear: number;
  endYear: number;
};

const CHART_WIDTH = 960;
const CHART_HEIGHT = 340;
const MARGIN = {
  top: 24,
  right: 24,
  bottom: 34,
  left: 72,
};

function parseGovernmentYear(date: string | null): number | null {
  if (!date) {
    return null;
  }

  const parsedYear = Number(date.slice(0, 4));
  return Number.isFinite(parsedYear) ? parsedYear : null;
}

function buildGovernmentIntervals(
  governments: CountryGovernmentItem[],
  minYear: number,
  maxYear: number,
): GovernmentInterval[] {
  return governments
    .map((gov) => {
      const startYear = parseGovernmentYear(gov.start_date) ?? minYear;
      const endYear = parseGovernmentYear(gov.end_date) ?? maxYear;

      return {
        leaderName: gov.leader_name,
        startYear,
        endYear,
      };
    })
    .filter((gov) => gov.endYear >= minYear && gov.startYear <= maxYear)
    .sort((a, b) => a.startYear - b.startYear);
}

export function CountryHistoryChart({ historyItems, governments }: CountryHistoryChartProps) {
  const sortedHistory = useMemo(() => {
    return [...historyItems].sort((a, b) => a.year - b.year);
  }, [historyItems]);

  const chartData = useMemo(() => {
    return sortedHistory
      .filter((item) => item.total_external_debt_usd !== null)
      .map((item) => ({
        year: item.year,
        debtUsd: item.total_external_debt_usd ?? 0,
      }));
  }, [sortedHistory]);

  if (chartData.length === 0) {
    return (
      <section className="rounded-xl border border-slate-700 bg-slate-950/40 p-4 text-sm text-slate-400">
        No historical debt series available.
      </section>
    );
  }

  const [minYear, maxYear] = extent(chartData, (d) => d.year) as [number, number];
  const maxDebtUsd = max(chartData, (d) => d.debtUsd) ?? 0;

  const x = scaleLinear()
    .domain([minYear, maxYear])
    .range([MARGIN.left, CHART_WIDTH - MARGIN.right]);

  const y = scaleLinear()
    .domain([0, maxDebtUsd])
    .nice()
    .range([CHART_HEIGHT - MARGIN.bottom, MARGIN.top]);

  const linePath = chartData
    .map((point, index) => `${index === 0 ? "M" : "L"}${x(point.year)},${y(point.debtUsd)}`)
    .join(" ");

  const areaPath = [
    `M${x(chartData[0].year)},${y(0)}`,
    ...chartData.map((point) => `L${x(point.year)},${y(point.debtUsd)}`),
    `L${x(chartData[chartData.length - 1].year)},${y(0)}`,
    "Z",
  ].join(" ");

  const yTickValues = y.ticks(4);
  const xTickValues = x.ticks(6).map((tick) => Math.round(tick));

  const governmentIntervals = buildGovernmentIntervals(governments, minYear, maxYear);

  return (
    <section className="rounded-xl border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3 flex flex-col gap-1">
        <h3 className="text-sm font-semibold text-slate-200">Historical external debt (USD)</h3>
        <p className="text-xs text-slate-400">Line + area chart with government period overlay.</p>
      </header>

      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`} className="min-w-[760px]" role="img" aria-label="Country debt history chart">
          <rect x={0} y={0} width={CHART_WIDTH} height={CHART_HEIGHT} fill="transparent" />

          {governmentIntervals.map((gov, index) => {
            const xStart = x(Math.max(gov.startYear, minYear));
            const xEnd = x(Math.min(gov.endYear, maxYear));
            const width = Math.max(2, xEnd - xStart);

            return (
              <g key={`${gov.leaderName}-${gov.startYear}-${index}`}>
                <rect
                  x={xStart}
                  y={MARGIN.top}
                  width={width}
                  height={CHART_HEIGHT - MARGIN.top - MARGIN.bottom}
                  fill={index % 2 === 0 ? "rgba(14, 116, 144, 0.08)" : "rgba(37, 99, 235, 0.08)"}
                />
                {width > 44 && (
                  <text x={xStart + 4} y={MARGIN.top + 14} fontSize={10} fill="#93c5fd">
                    {gov.leaderName}
                  </text>
                )}
              </g>
            );
          })}

          {yTickValues.map((tick) => (
            <g key={`y-${tick}`}>
              <line
                x1={MARGIN.left}
                y1={y(tick)}
                x2={CHART_WIDTH - MARGIN.right}
                y2={y(tick)}
                stroke="rgba(148, 163, 184, 0.2)"
                strokeDasharray="4 4"
              />
              <text x={MARGIN.left - 8} y={y(tick) + 4} textAnchor="end" fontSize={11} fill="#94a3b8">
                {formatUsdCompact(tick)}
              </text>
            </g>
          ))}

          {xTickValues.map((tick) => (
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

          <path d={areaPath} fill="rgba(56, 189, 248, 0.16)" />
          <path d={linePath} fill="none" stroke="#22d3ee" strokeWidth={2.5} />

          {chartData.map((point) => (
            <circle key={`pt-${point.year}`} cx={x(point.year)} cy={y(point.debtUsd)} r={2.5} fill="#67e8f9" />
          ))}

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
        </svg>
      </div>
    </section>
  );
}
