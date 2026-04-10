import { extent, max, scaleLinear } from "d3";
import { useMemo } from "react";

import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { t } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";
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

type GovernmentLabelLayout = {
  key: string;
  x: number;
  y: number;
  text: string;
};

const CHART_WIDTH = 960;
const CHART_HEIGHT = 340;
const MARGIN = {
  top: 24,
  right: 24,
  bottom: 34,
  left: 72,
};

const AVG_CHAR_PX = 5.8;
const LABEL_SIDE_PADDING = 8;
const LABEL_LANES_Y_OFFSETS = [14, 24, 34];
const LABEL_LANE_GAP = 8;

function estimateTextWidth(text: string): number {
  return text.length * AVG_CHAR_PX;
}

function truncateTextToWidth(text: string, maxWidth: number): string {
  if (maxWidth <= 0) {
    return "";
  }

  if (estimateTextWidth(text) <= maxWidth) {
    return text;
  }

  const ellipsis = "…";
  const available = Math.max(0, maxWidth - estimateTextWidth(ellipsis));
  const chars = Math.max(0, Math.floor(available / AVG_CHAR_PX));
  if (chars === 0) {
    return ellipsis;
  }

  return `${text.slice(0, chars)}${ellipsis}`;
}

function buildGovernmentLabels(
  governmentIntervals: GovernmentInterval[],
  xScale: (year: number) => number,
): GovernmentLabelLayout[] {
  const laneEnds = LABEL_LANES_Y_OFFSETS.map(() => Number.NEGATIVE_INFINITY);
  const result: GovernmentLabelLayout[] = [];

  governmentIntervals.forEach((gov, index) => {
    const xStart = xScale(gov.startYear);
    const xEnd = xScale(gov.endYear);
    const bandWidth = Math.max(2, xEnd - xStart);
    const maxLabelWidth = Math.max(0, bandWidth - LABEL_SIDE_PADDING);
    if (maxLabelWidth < 10) {
      return;
    }

    const text = truncateTextToWidth(gov.leaderName, maxLabelWidth);
    if (!text) {
      return;
    }

    const effectiveWidth = estimateTextWidth(text);
    const laneIndex = laneEnds.findIndex((laneEnd) => laneEnd + LABEL_LANE_GAP <= xStart);
    if (laneIndex === -1) {
      return;
    }

    laneEnds[laneIndex] = xStart + effectiveWidth;
    result.push({
      key: `${gov.leaderName}-${gov.startYear}-${index}`,
      x: xStart + 4,
      y: MARGIN.top + LABEL_LANES_Y_OFFSETS[laneIndex],
      text,
    });
  });

  return result;
}

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

function isFiniteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function buildLinePath(
  points: Array<{ year: number; debtPctGdp: number | null }>,
  xScale: (year: number) => number,
  yScale: (value: number) => number,
): string {
  let path = "";
  let started = false;

  points.forEach((point) => {
    if (!isFiniteNumber(point.debtPctGdp)) {
      started = false;
      return;
    }

    path += `${started ? "L" : "M"}${xScale(point.year)},${yScale(point.debtPctGdp)} `;
    started = true;
  });

  return path.trim();
}

export function CountryHistoryChart({ historyItems, governments }: CountryHistoryChartProps) {
  const locale = useLocaleStore((state) => state.locale);
  const sortedHistory = useMemo(() => {
    return [...historyItems].sort((a, b) => a.year - b.year);
  }, [historyItems]);

  const chartData = useMemo(() => {
    return sortedHistory
      .filter((item) => item.total_external_debt_usd !== null)
      .map((item) => ({
        year: item.year,
        debtUsd: item.total_external_debt_usd ?? 0,
        debtPctGdp: item.debt_pct_gdp,
      }));
  }, [sortedHistory]);

  if (chartData.length === 0) {
    return (
      <section className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4 text-sm text-[#888680]">
        {t(locale, "noHistoricalSeries")}
      </section>
    );
  }

  const [minYear, maxYear] = extent(chartData, (d) => d.year) as [number, number];
  const maxDebtUsd = max(chartData, (d) => d.debtUsd) ?? 0;
  const pctValues = chartData.map((point) => point.debtPctGdp).filter(isFiniteNumber);
  const hasPctSeries = pctValues.length > 0;

  const x = scaleLinear()
    .domain([minYear, maxYear])
    .range([MARGIN.left, CHART_WIDTH - MARGIN.right]);

  const y = scaleLinear()
    .domain([0, maxDebtUsd])
    .nice()
    .range([CHART_HEIGHT - MARGIN.bottom, MARGIN.top]);

  const pctMin = hasPctSeries ? Math.min(...pctValues) : 0;
  const pctMax = hasPctSeries ? Math.max(...pctValues) : 1;
  const safePctMax = pctMin === pctMax ? pctMax + 1 : pctMax;
  const yPct = scaleLinear()
    .domain([pctMin, safePctMax])
    .nice()
    .range([CHART_HEIGHT - MARGIN.bottom, MARGIN.top]);

  const linePath = chartData
    .map((point, index) => `${index === 0 ? "M" : "L"}${x(point.year)},${y(point.debtUsd)}`)
    .join(" ");
  const pctPath = hasPctSeries ? buildLinePath(chartData, x, yPct) : "";

  const areaPath = [
    `M${x(chartData[0].year)},${y(0)}`,
    ...chartData.map((point) => `L${x(point.year)},${y(point.debtUsd)}`),
    `L${x(chartData[chartData.length - 1].year)},${y(0)}`,
    "Z",
  ].join(" ");

  const yTickValues = y.ticks(4);
  const yPctTickValues = hasPctSeries ? yPct.ticks(4) : [];
  const xTickValues = x.ticks(6).map((tick) => Math.round(tick));

  const governmentIntervals = buildGovernmentIntervals(governments, minYear, maxYear);
  const governmentLabels = buildGovernmentLabels(governmentIntervals, x);

  return (
    <section className="rounded-xl border border-[#3b4252] bg-[#0d1017]/70 p-4">
      <header className="mb-3 flex flex-col gap-1">
        <h3 className="text-sm font-semibold text-[#f5f4f0]">{t(locale, "historicalDebtTitle")}</h3>
        <p className="text-xs text-[#888680]">{t(locale, "historicalDebtSubtitle")}</p>
        <div className="mt-1 flex flex-wrap gap-4 text-[11px] text-[#94a3b8]">
          <span className="inline-flex items-center gap-2">
            <span className="h-0.5 w-6 bg-[#22d3ee]" />
            {t(locale, "debtLabel")}
          </span>
          <span className="inline-flex items-center gap-2">
            <span className="h-0.5 w-6 border-t border-dashed border-[#f59e0b]" />
            {t(locale, "debtToGdpLabel")}
          </span>
        </div>
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
              </g>
            );
          })}

          {governmentLabels.map((label) => (
            <text key={label.key} x={label.x} y={label.y} fontSize={10} fill="#93c5fd">
              {label.text}
            </text>
          ))}

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

          {yPctTickValues.map((tick) => (
            <text key={`y-right-${tick}`} x={CHART_WIDTH - MARGIN.right + 8} y={yPct(tick) + 4} textAnchor="start" fontSize={11} fill="#94a3b8">
              {formatPercentage(tick)}
            </text>
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
          {pctPath && <path d={pctPath} fill="none" stroke="#f59e0b" strokeWidth={1.8} strokeDasharray="6 4" />}

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
