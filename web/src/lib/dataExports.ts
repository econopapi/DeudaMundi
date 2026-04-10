import { utils, write } from "xlsx";

import { buildLeaderLabel } from "./governmentLabels";
import type {
  CountryCompareItem,
  CountryDetailResponse,
  CountryGovernmentItem,
  CountryHistoryItem,
} from "../types/api";

type ExportValue = string | number | null;
export type ExportRow = Record<string, ExportValue>;

export type ExportSheet = {
  name: string;
  rows: ExportRow[];
};

export type ComparePdfCountrySeries = {
  iso3: string;
  name_en: string;
  region: string | null;
  latestYear: number | null;
  latestDebtStockUsd: number | null;
  latestDebtPctGdp: number | null;
  stockSeries: Array<number | null>;
  pctSeries: Array<number | null>;
};

export type ComparePdfReportData = {
  years: number[];
  countries: ComparePdfCountrySeries[];
};

export type CountryPdfReportData = {
  iso3: string;
  name_en: string;
  region: string | null;
  latestYear: number | null;
  latestDebtStockUsd: number | null;
  latestDebtPctGdp: number | null;
  years: number[];
  stockSeries: Array<number | null>;
  pctSeries: Array<number | null>;
};

type PdfReportCopy = {
  title: string;
  chartTitle: string;
  sourceText: string;
};

const REPORT_COLORS = [
  "#38bdf8",
  "#a78bfa",
  "#22c55e",
  "#f59e0b",
  "#f97316",
];

const PROJECT_URL = "deudamundi.econopapi.com";

function normalizeCell(value: ExportValue): string | number {
  if (value === null || value === undefined) {
    return "";
  }
  return value;
}

function normalizeRows(rows: ExportRow[]): Array<Record<string, string | number>> {
  return rows.map((row) => {
    const normalized: Record<string, string | number> = {};
    Object.entries(row).forEach(([key, value]) => {
      normalized[key] = normalizeCell(value);
    });
    return normalized;
  });
}

export function rowsToCsv(rows: ExportRow[]): string {
  if (rows.length === 0) {
    return "";
  }

  const headers = Object.keys(rows[0]);
  const escaped = (value: ExportValue): string => {
    const normalized = String(normalizeCell(value));
    const needsQuotes = /[",\n]/.test(normalized);
    const safe = normalized.replace(/"/g, '""');
    return needsQuotes ? `"${safe}"` : safe;
  };

  const lines = [headers.join(",")];
  rows.forEach((row) => {
    lines.push(headers.map((header) => escaped(row[header] ?? null)).join(","));
  });

  return `${lines.join("\n")}\n`;
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
}

export function downloadCsvFile(filename: string, rows: ExportRow[]): void {
  const csvText = rowsToCsv(rows);
  const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
  downloadBlob(blob, filename);
}

export function downloadXlsxFile(filename: string, sheets: ExportSheet[]): void {
  const workbook = utils.book_new();

  sheets.forEach((sheet) => {
    const ws = utils.json_to_sheet(normalizeRows(sheet.rows));
    utils.book_append_sheet(workbook, ws, sheet.name.slice(0, 31));
  });

  const output = write(workbook, { bookType: "xlsx", type: "array" });
  const blob = new Blob([output], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
  downloadBlob(blob, filename);
}

export function buildCountryLatestExportRows(country: CountryDetailResponse): ExportRow[] {
  return [
    {
      iso3: country.iso3,
      name_en: country.name_en,
      name_es: country.name_es,
      region: country.region,
      subregion: country.subregion,
      latest_year: country.latest_year,
      total_external_debt_usd: country.debt_stock_usd ?? country.total_external_debt_usd,
      debt_per_capita_usd: country.debt_per_capita_usd,
      debt_pct_gdp: country.debt_pct_gdp,
      gdp_usd: country.gdp_usd,
    },
  ];
}

export function buildCountryHistoryExportRows(country: CountryDetailResponse, historyItems: CountryHistoryItem[]): ExportRow[] {
  return historyItems.map((item) => ({
    iso3: country.iso3,
    name_en: country.name_en,
    year: item.year,
    total_external_debt_usd: item.debt_stock_usd ?? item.total_external_debt_usd,
    debt_per_capita_usd: item.debt_per_capita_usd,
    debt_pct_gdp: item.debt_pct_gdp,
    gdp_usd: item.gdp_usd,
    source: item.source,
  }));
}

export function buildCompareLatestExportRows(items: CountryCompareItem[]): ExportRow[] {
  return items.map((item) => ({
    iso3: item.detail.iso3,
    name_en: item.detail.name_en,
    region: item.detail.region,
    latest_year: item.detail.latest_year,
    total_external_debt_usd: item.detail.debt_stock_usd ?? item.detail.total_external_debt_usd,
    debt_per_capita_usd: item.detail.debt_per_capita_usd,
    debt_pct_gdp: item.detail.debt_pct_gdp,
    gdp_usd: item.detail.gdp_usd,
  }));
}

export function buildCompareHistoryExportRows(items: CountryCompareItem[]): ExportRow[] {
  const rows: ExportRow[] = [];

  items.forEach((item) => {
    item.history.forEach((historyRow) => {
      rows.push({
        iso3: item.detail.iso3,
        name_en: item.detail.name_en,
        year: historyRow.year,
        total_external_debt_usd: historyRow.debt_stock_usd ?? historyRow.total_external_debt_usd,
        debt_per_capita_usd: historyRow.debt_per_capita_usd,
        debt_pct_gdp: historyRow.debt_pct_gdp,
        gdp_usd: historyRow.gdp_usd,
        source: historyRow.source,
      });
    });
  });

  return rows;
}

function getHistoryDebtStock(item: CountryHistoryItem): number | null {
  return item.debt_stock_usd ?? item.total_external_debt_usd;
}

function hexToRgb(hex: string): [number, number, number] {
  const normalized = hex.replace("#", "");
  const value = Number.parseInt(normalized, 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

function formatUsdCompactByLocale(value: number | null, locale: "en" | "es"): string {
  if (value === null || Number.isNaN(value)) {
    return locale === "es" ? "N/D" : "N/A";
  }

  return new Intl.NumberFormat(locale === "es" ? "es-MX" : "en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatUsdCompactChartLikeWeb(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercentageByLocale(value: number | null, locale: "en" | "es"): string {
  if (value === null || Number.isNaN(value)) {
    return locale === "es" ? "N/D" : "N/A";
  }

  return `${new Intl.NumberFormat(locale === "es" ? "es-MX" : "en-US", {
    maximumFractionDigits: 2,
  }).format(value)}%`;
}

function buildLinearTicks(minValue: number, maxValue: number, count: number): number[] {
  if (count <= 1) {
    return [minValue];
  }

  const range = maxValue - minValue;
  if (!Number.isFinite(range) || range <= 0) {
    return Array.from({ length: count }, () => minValue);
  }

  return Array.from({ length: count }, (_, index) => minValue + (range * index) / (count - 1));
}

function buildTickIndices(totalPoints: number, maxTicks: number): number[] {
  if (totalPoints <= 0) {
    return [];
  }
  if (totalPoints === 1) {
    return [0];
  }

  const tickCount = Math.min(maxTicks, totalPoints);
  const indices = new Set<number>();
  for (let i = 0; i < tickCount; i += 1) {
    const rawIndex = Math.round((i * (totalPoints - 1)) / (tickCount - 1));
    indices.add(rawIndex);
  }

  return Array.from(indices).sort((a, b) => a - b);
}

export function buildComparePdfReportData(items: CountryCompareItem[]): ComparePdfReportData {
  const years = Array.from(
    new Set(
      items.flatMap((item) => item.history.map((historyItem) => historyItem.year).filter((year) => Number.isFinite(year))),
    ),
  ).sort((left, right) => left - right);

  const countries: ComparePdfCountrySeries[] = items.map((item) => {
    const byYear = new Map<number, CountryHistoryItem>();
    item.history.forEach((historyItem) => {
      byYear.set(historyItem.year, historyItem);
    });

    return {
      iso3: item.detail.iso3,
      name_en: item.detail.name_en,
      region: item.detail.region,
      latestYear: item.detail.latest_year,
      latestDebtStockUsd: item.detail.debt_stock_usd ?? item.detail.total_external_debt_usd,
      latestDebtPctGdp: item.detail.debt_pct_gdp,
      stockSeries: years.map((year) => {
        const point = byYear.get(year);
        return point ? getHistoryDebtStock(point) : null;
      }),
      pctSeries: years.map((year) => {
        const point = byYear.get(year);
        return point?.debt_pct_gdp ?? null;
      }),
    };
  });

  return { years, countries };
}

export function buildCountryPdfReportData(country: CountryDetailResponse, historyItems: CountryHistoryItem[]): CountryPdfReportData {
  const orderedHistory = [...historyItems].sort((left, right) => left.year - right.year);

  return {
    iso3: country.iso3,
    name_en: country.name_en,
    region: country.region,
    latestYear: country.latest_year,
    latestDebtStockUsd: country.debt_stock_usd ?? country.total_external_debt_usd,
    latestDebtPctGdp: country.debt_pct_gdp,
    years: orderedHistory.map((item) => item.year),
    stockSeries: orderedHistory.map((item) => getHistoryDebtStock(item)),
    pctSeries: orderedHistory.map((item) => item.debt_pct_gdp),
  };
}

async function downloadCountriesPdfReport(
  filename: string,
  items: CountryCompareItem[],
  locale: "en" | "es",
  copy: PdfReportCopy,
  governmentsByIso3?: Record<string, CountryGovernmentItem[]>,
): Promise<void> {
  if (items.length === 0) {
    return;
  }

  const report = buildComparePdfReportData(items);
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ orientation: "landscape", unit: "pt", format: "a4" });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  doc.setFillColor(13, 16, 23);
  doc.rect(0, 0, pageWidth, pageHeight, "F");

  doc.setFillColor(15, 23, 42);
  doc.roundedRect(18, 18, pageWidth - 36, pageHeight - 36, 14, 14, "F");

  doc.setTextColor(125, 211, 252);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.text(
    locale === "es" ? "DeudaMundi · Atlas de Deuda Externa" : "DeudaMundi · External Debt Atlas",
    32,
    40,
  );

  doc.setTextColor(248, 250, 252);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.text(copy.title, 32, 66);

  doc.setTextColor(148, 163, 184);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(
    locale === "es"
      ? `Generado el ${new Date().toLocaleDateString("es-MX")}`
      : `Generated on ${new Date().toLocaleDateString("en-US")}`,
    32,
    84,
  );

  const cardsPerRow = Math.min(3, report.countries.length);
  const rowCount = Math.ceil(report.countries.length / cardsPerRow);
  const cardGap = 10;
  const cardsStartX = 32;
  const cardsStartY = 96;
  const cardHeight = 58;
  const cardsWidth = pageWidth - 64;
  const cardWidth = (cardsWidth - cardGap * (cardsPerRow - 1)) / cardsPerRow;

  report.countries.forEach((country, index) => {
    const row = Math.floor(index / cardsPerRow);
    const col = index % cardsPerRow;
    const x = cardsStartX + col * (cardWidth + cardGap);
    const y = cardsStartY + row * (cardHeight + cardGap);
    const [r, g, b] = hexToRgb(REPORT_COLORS[index % REPORT_COLORS.length]);

    doc.setFillColor(11, 18, 32);
    doc.roundedRect(x, y, cardWidth, cardHeight, 8, 8, "F");
    doc.setDrawColor(r, g, b);
    doc.setLineWidth(2);
    doc.line(x + 10, y + 10, x + 34, y + 10);

    doc.setTextColor(226, 232, 240);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(`${country.name_en} (${country.iso3})`, x + 40, y + 14, {
      maxWidth: cardWidth - 48,
    });

    doc.setTextColor(148, 163, 184);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(
      `${locale === "es" ? "Stock" : "Stock"}: ${formatUsdCompactByLocale(country.latestDebtStockUsd, locale)}`,
      x + 10,
      y + 31,
    );
    doc.text(
      `${locale === "es" ? "Deuda/PIB" : "Debt/GDP"}: ${formatPercentageByLocale(country.latestDebtPctGdp, locale)}`,
      x + 10,
      y + 46,
    );
  });

  const singleCountryIso3 = report.countries.length === 1 ? report.countries[0].iso3 : null;
  const recentGovernments = singleCountryIso3
    ? buildPdfRecentGovernmentsSummary(governmentsByIso3?.[singleCountryIso3] ?? [], locale)
    : "";
  const recentGovernmentsBlockHeight = recentGovernments ? 22 : 0;

  if (recentGovernments) {
    const governmentsY = cardsStartY + rowCount * (cardHeight + cardGap) + 22;
    doc.setTextColor(148, 163, 184);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(locale === "es" ? "Gobiernos recientes:" : "Recent governments:", cardsStartX, governmentsY);

    doc.setTextColor(226, 232, 240);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.text(recentGovernments, cardsStartX + 86, governmentsY);
  }

  const chartContainerX = 32;
  const chartContainerY = cardsStartY + rowCount * (cardHeight + cardGap) + 12 + recentGovernmentsBlockHeight;
  const chartContainerWidth = pageWidth - 64;
  const chartContainerHeight = pageHeight - chartContainerY - 38;
  doc.setFillColor(9, 14, 26);
  doc.roundedRect(chartContainerX, chartContainerY, chartContainerWidth, chartContainerHeight, 10, 10, "F");

  doc.setTextColor(203, 213, 225);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.text(copy.chartTitle, chartContainerX + 14, chartContainerY + 18);

  const plotX = chartContainerX + 16;
  const plotY = chartContainerY + 34;
  const plotWidth = chartContainerWidth - 32;
  const plotHeight = chartContainerHeight - 54;

  const allStockValues = report.countries.flatMap((country) =>
    country.stockSeries.filter((value): value is number => value !== null && Number.isFinite(value)),
  );
  const allPctValues = report.countries.flatMap((country) =>
    country.pctSeries.filter((value): value is number => value !== null && Number.isFinite(value)),
  );

  if (report.years.length < 2 || allStockValues.length < 2) {
    doc.setTextColor(148, 163, 184);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    doc.text(locale === "es" ? "Sin datos históricos suficientes" : "Not enough historical data", plotX, plotY + 32);
    doc.save(filename);
    return;
  }

  const minStock = 0;
  const maxStock = Math.max(...allStockValues);
  const stockRange = Math.max(maxStock - minStock, 1);

  const minPct = allPctValues.length > 0 ? Math.min(...allPctValues) : 0;
  const maxPct = allPctValues.length > 0 ? Math.max(...allPctValues) : 1;
  const pctRange = maxPct - minPct || Math.max(maxPct, 1);

  const xFor = (index: number) =>
    report.years.length === 1 ? plotX + plotWidth / 2 : plotX + (index / (report.years.length - 1)) * plotWidth;
  const yForStock = (value: number) => plotY + (1 - (value - minStock) / stockRange) * plotHeight;
  const yForPct = (value: number) => plotY + (1 - (value - minPct) / pctRange) * plotHeight;

  const stockTicks = buildLinearTicks(minStock, maxStock, 4);
  const pctTicks = allPctValues.length > 0 ? buildLinearTicks(minPct, maxPct, 4) : [];
  const xTickIndices = buildTickIndices(report.years.length, 6);

  doc.setDrawColor(71, 85, 105);
  doc.setLineWidth(0.7);
  stockTicks.forEach((tick) => {
    const y = yForStock(tick);
    doc.line(plotX, y, plotX + plotWidth, y);
  });

  doc.setDrawColor(148, 163, 184);
  doc.setLineWidth(0.9);
  doc.line(plotX, plotY, plotX, plotY + plotHeight);
  doc.line(plotX + plotWidth, plotY, plotX + plotWidth, plotY + plotHeight);
  doc.line(plotX, plotY + plotHeight, plotX + plotWidth, plotY + plotHeight);

  report.countries.forEach((country, index) => {
    const [r, g, b] = hexToRgb(REPORT_COLORS[index % REPORT_COLORS.length]);

    doc.setDrawColor(r, g, b);
    doc.setLineWidth(1.8);
    doc.setLineDashPattern([], 0);

    let prevStockIndex: number | null = null;
    country.stockSeries.forEach((value, seriesIndex) => {
      if (value === null) {
        prevStockIndex = null;
        return;
      }

      if (prevStockIndex !== null) {
        const prevValue = country.stockSeries[prevStockIndex];
        if (prevValue !== null) {
          doc.line(xFor(prevStockIndex), yForStock(prevValue), xFor(seriesIndex), yForStock(value));
        }
      }

      doc.setFillColor(r, g, b);
      doc.circle(xFor(seriesIndex), yForStock(value), 1.4, "F");
      prevStockIndex = seriesIndex;
    });

    doc.setLineDashPattern([4, 3], 0);
    doc.setLineWidth(1.4);
    let prevPctIndex: number | null = null;
    country.pctSeries.forEach((value, seriesIndex) => {
      if (value === null) {
        prevPctIndex = null;
        return;
      }

      if (prevPctIndex !== null) {
        const prevValue = country.pctSeries[prevPctIndex];
        if (prevValue !== null) {
          doc.line(xFor(prevPctIndex), yForPct(prevValue), xFor(seriesIndex), yForPct(value));
        }
      }
      prevPctIndex = seriesIndex;
    });
    doc.setLineDashPattern([], 0);
  });

  doc.setTextColor(148, 163, 184);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);

  stockTicks.forEach((tick) => {
    doc.setTextColor(125, 211, 252);
    doc.text(formatUsdCompactChartLikeWeb(tick), plotX, yForStock(tick) - 4);
  });

  if (allPctValues.length > 0) {
    pctTicks.forEach((tick) => {
      doc.setTextColor(196, 181, 253);
      doc.text(formatPercentageByLocale(tick, locale), plotX + plotWidth - 44, yForPct(tick) - 4);
    });
  }

  doc.setTextColor(148, 163, 184);
  xTickIndices.forEach((tickIndex) => {
    const tickX = xFor(tickIndex);
    doc.line(tickX, plotY + plotHeight, tickX, plotY + plotHeight + 4);
    doc.text(String(report.years[tickIndex]), tickX - 8, plotY + plotHeight + 14);
  });

  doc.setTextColor(136, 134, 128);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.text(copy.sourceText, chartContainerX + 14, chartContainerY + chartContainerHeight + 15);
  doc.setTextColor(136, 134, 128);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(10);
  doc.text(PROJECT_URL, pageWidth - 32, chartContainerY + chartContainerHeight + 15, {
    align: "right",
  });

  doc.save(filename);
}

function parseYearFromDate(value: string | null): number {
  if (!value) {
    return 0;
  }

  const year = Number.parseInt(value.slice(0, 4), 10);
  return Number.isFinite(year) ? year : 0;
}

function truncateTextByLength(value: string, maxLength: number): string {
  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, Math.max(0, maxLength - 1))}…`;
}

export function buildPdfRecentGovernmentsSummary(
  governments: CountryGovernmentItem[],
  locale: "en" | "es",
): string {
  if (governments.length === 0) {
    return "";
  }

  const seen = new Set<string>();
  const names = governments
    .slice()
    .sort((a, b) => parseYearFromDate(b.start_date) - parseYearFromDate(a.start_date))
    .map((gov) =>
      buildLeaderLabel(gov.leader_name, locale === "es" ? 150 : 120, {
        locale,
      }),
    )
    .filter((label) => {
      if (!label || seen.has(label)) {
        return false;
      }
      seen.add(label);
      return true;
    });

  if (names.length === 0) {
    return "";
  }

  const maxItems = 4;
  const selected = names.slice(0, maxItems);
  const remaining = names.length - selected.length;
  const suffix = remaining > 0 ? ` +${remaining}` : "";
  return truncateTextByLength(`${selected.join(" · ")}${suffix}`, 120);
}

export async function downloadComparePdfReport(
  filename: string,
  items: CountryCompareItem[],
  locale: "en" | "es",
): Promise<void> {
  await downloadCountriesPdfReport(filename, items, locale, {
    title: locale === "es" ? "Reporte de comparación entre países" : "Country comparison report",
    chartTitle:
      locale === "es"
        ? "Comparación histórica (línea sólida: USD, línea punteada: %PIB)"
        : "Historical comparison (solid line: USD, dashed line: %GDP)",
    sourceText:
      locale === "es"
        ? "Fuente: DeudaMundi API · GET /api/v1/countries/compare"
        : "Source: DeudaMundi API · GET /api/v1/countries/compare",
  });
}

export async function downloadCountryPdfReport(
  filename: string,
  country: CountryDetailResponse,
  historyItems: CountryHistoryItem[],
  governments: CountryGovernmentItem[],
  locale: "en" | "es",
): Promise<void> {
  const compareItems: CountryCompareItem[] = [
    {
      detail: country,
      history: historyItems,
    },
  ];

  await downloadCountriesPdfReport(filename, compareItems, locale, {
    title: locale === "es" ? `Reporte de país: ${country.name_en}` : `Country report: ${country.name_en}`,
    chartTitle:
      locale === "es"
        ? "Evolución histórica (línea sólida: USD, línea punteada: %PIB)"
        : "Historical trajectory (solid line: USD, dashed line: %GDP)",
    sourceText:
      locale === "es"
        ? `Fuente: DeudaMundi API · GET /api/v1/countries/${country.iso3.toLowerCase()}`
        : `Source: DeudaMundi API · GET /api/v1/countries/${country.iso3.toLowerCase()}`,
  }, {
    [country.iso3]: governments,
  });
}
