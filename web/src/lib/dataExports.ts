import { utils, write } from "xlsx";

import type { CountryCompareItem, CountryDetailResponse, CountryHistoryItem } from "../types/api";

type ExportValue = string | number | null;
export type ExportRow = Record<string, ExportValue>;

export type ExportSheet = {
  name: string;
  rows: ExportRow[];
};

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
