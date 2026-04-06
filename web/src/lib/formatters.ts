const compactCurrencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 2,
});

const decimalFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
});

export function formatUsdCompact(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "N/A";
  }

  return compactCurrencyFormatter.format(value);
}

export function formatPercentage(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "N/A";
  }

  return `${decimalFormatter.format(value)}%`;
}
