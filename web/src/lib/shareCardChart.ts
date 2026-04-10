import type { CountryHistoryItem } from "../types/api";

export type ShareCardChartPoint = {
  year: number;
  debtStockUsd: number;
  debtPctGdp: number | null;
};

function getDebtStock(item: CountryHistoryItem): number | null {
  return item.debt_stock_usd ?? item.total_external_debt_usd;
}

export function buildShareCardChartSeries(
  historyItems: CountryHistoryItem[],
  maxPoints = 18,
): ShareCardChartPoint[] {
  const ordered = historyItems
    .map((item) => ({
      year: item.year,
      debtStockUsd: getDebtStock(item),
      debtPctGdp: Number.isFinite(item.debt_pct_gdp) ? item.debt_pct_gdp : null,
    }))
    .filter(
      (item): item is ShareCardChartPoint =>
        Number.isFinite(item.year) && item.debtStockUsd !== null && Number.isFinite(item.debtStockUsd),
    )
    .sort((left, right) => left.year - right.year);

  if (ordered.length <= maxPoints) {
    return ordered;
  }

  return ordered.slice(ordered.length - maxPoints);
}
