import { useMemo, useState } from "react";

import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { buildShareCardChartSeries } from "../../lib/shareCardChart";
import { t } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";
import type { CountryDetailResponse, CountryHistoryItem } from "../../types/api";

type ShareCardActionsProps = {
  country: CountryDetailResponse;
  historyItems: CountryHistoryItem[];
};

function getDebtStock(country: CountryDetailResponse): number | null {
  return country.debt_stock_usd ?? country.total_external_debt_usd;
}

function buildShareText(country: CountryDetailResponse, locale: "en" | "es"): string {
  const debtPerCapita = formatUsdCompact(country.debt_per_capita_usd);
  const debtPct = formatPercentage(country.debt_pct_gdp);

  if (locale === "es") {
    return `${country.name_en} (${country.iso3}) · Deuda per cápita: ${debtPerCapita} · Deuda/PIB: ${debtPct}. Explora: ${window.location.href}`;
  }

  return `${country.name_en} (${country.iso3}) · Debt per capita: ${debtPerCapita} · Debt/GDP: ${debtPct}. Explore: ${window.location.href}`;
}

function drawMiniChart(
  context: CanvasRenderingContext2D,
  historyItems: CountryHistoryItem[],
  locale: "en" | "es",
) {
  const chartX = 640;
  const chartY = 168;
  const chartWidth = 500;
  const chartHeight = 332;
  const innerPadding = 24;
  const plotX = chartX + innerPadding;
  const plotY = chartY + innerPadding + 50;
  const plotWidth = chartWidth - innerPadding * 2;
  const plotHeight = chartHeight - innerPadding * 2 - 66;

  context.fillStyle = "#0b1220";
  context.fillRect(chartX, chartY, chartWidth, chartHeight);
  context.strokeStyle = "#1f2937";
  context.lineWidth = 1;
  context.strokeRect(chartX + 0.5, chartY + 0.5, chartWidth - 1, chartHeight - 1);

  context.fillStyle = "#93c5fd";
  context.font = "600 21px Outfit, Inter, system-ui, sans-serif";
  context.fillText(
    locale === "es" ? "Tendencia histórica (USD y % PIB)" : "Historical trend (USD and % GDP)",
    chartX + innerPadding,
    chartY + 30,
  );

  context.lineWidth = 3;
  context.strokeStyle = "#38bdf8";
  context.beginPath();
  context.moveTo(chartX + innerPadding, chartY + 48);
  context.lineTo(chartX + innerPadding + 24, chartY + 48);
  context.stroke();
  context.fillStyle = "#cbd5e1";
  context.font = "500 14px Outfit, Inter, system-ui, sans-serif";
  context.fillText(locale === "es" ? "Stock (USD)" : "Stock (USD)", chartX + innerPadding + 32, chartY + 53);

  context.setLineDash([7, 5]);
  context.strokeStyle = "#a78bfa";
  context.beginPath();
  context.moveTo(chartX + innerPadding + 130, chartY + 48);
  context.lineTo(chartX + innerPadding + 154, chartY + 48);
  context.stroke();
  context.setLineDash([]);
  context.fillText(locale === "es" ? "Deuda/PIB (%)" : "Debt/GDP (%)", chartX + innerPadding + 162, chartY + 53);

  for (let index = 0; index < 4; index += 1) {
    const gridY = plotY + (plotHeight / 3) * index;
    context.strokeStyle = "rgba(148, 163, 184, 0.2)";
    context.beginPath();
    context.moveTo(plotX, gridY);
    context.lineTo(plotX + plotWidth, gridY);
    context.stroke();
  }

  const series = buildShareCardChartSeries(historyItems);
  if (series.length < 2) {
    context.fillStyle = "#94a3b8";
    context.font = "500 20px Outfit, Inter, system-ui, sans-serif";
    context.fillText(t(locale, "noHistoricalSeries"), chartX + innerPadding, chartY + chartHeight / 2);
    return;
  }

  const values = series.map((item) => item.debtStockUsd);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue || Math.max(maxValue, 1);

  const xFor = (index: number) => plotX + (index / (series.length - 1)) * plotWidth;
  const yFor = (value: number) => plotY + (1 - (value - minValue) / range) * plotHeight;

  context.beginPath();
  context.moveTo(xFor(0), yFor(series[0].debtStockUsd));
  series.forEach((item, index) => {
    if (index === 0) {
      return;
    }
    context.lineTo(xFor(index), yFor(item.debtStockUsd));
  });
  context.lineTo(xFor(series.length - 1), plotY + plotHeight);
  context.lineTo(xFor(0), plotY + plotHeight);
  context.closePath();
  context.fillStyle = "rgba(56, 189, 248, 0.24)";
  context.fill();

  context.beginPath();
  context.moveTo(xFor(0), yFor(series[0].debtStockUsd));
  series.forEach((item, index) => {
    if (index === 0) {
      return;
    }
    context.lineTo(xFor(index), yFor(item.debtStockUsd));
  });
  context.strokeStyle = "#38bdf8";
  context.lineWidth = 4;
  context.stroke();

  const pctSeries = series.filter((item) => item.debtPctGdp !== null);
  if (pctSeries.length >= 2) {
    const pctValues = pctSeries.map((item) => item.debtPctGdp as number);
    const minPct = Math.min(...pctValues);
    const maxPct = Math.max(...pctValues);
    const pctRange = maxPct - minPct || Math.max(maxPct, 1);
    const yForPct = (value: number) => plotY + (1 - (value - minPct) / pctRange) * plotHeight;

    context.beginPath();
    let started = false;

    series.forEach((item, index) => {
      if (item.debtPctGdp === null) {
        started = false;
        return;
      }

      const x = xFor(index);
      const y = yForPct(item.debtPctGdp);

      if (!started) {
        context.moveTo(x, y);
        started = true;
        return;
      }

      context.lineTo(x, y);
    });

    context.setLineDash([8, 6]);
    context.strokeStyle = "#a78bfa";
    context.lineWidth = 3;
    context.stroke();
    context.setLineDash([]);

    const latestPct = [...series].reverse().find((item) => item.debtPctGdp !== null);
    if (latestPct) {
      const latestPctIndex = series.findIndex((item) => item.year === latestPct.year);
      const latestPctX = xFor(latestPctIndex);
      const latestPctY = yForPct(latestPct.debtPctGdp as number);

      context.beginPath();
      context.arc(latestPctX, latestPctY, 5, 0, Math.PI * 2);
      context.fillStyle = "#ddd6fe";
      context.fill();

      context.fillStyle = "#ddd6fe";
      context.textAlign = "right";
      context.font = "500 16px Outfit, Inter, system-ui, sans-serif";
      context.fillText(formatPercentage(latestPct.debtPctGdp as number), plotX + plotWidth, plotY - 8);
      context.textAlign = "left";
    }
  }

  const latest = series[series.length - 1];
  const latestX = xFor(series.length - 1);
  const latestY = yFor(latest.debtStockUsd);

  context.beginPath();
  context.arc(latestX, latestY, 6, 0, Math.PI * 2);
  context.fillStyle = "#f8fafc";
  context.fill();

  context.fillStyle = "#cbd5e1";
  context.font = "500 18px Outfit, Inter, system-ui, sans-serif";
  context.fillText(String(series[0].year), plotX, chartY + chartHeight - 18);
  context.fillStyle = "#7dd3fc";
  context.fillText(formatUsdCompact(latest.debtStockUsd), plotX, plotY + 2);
  context.textAlign = "right";
  context.fillStyle = "#cbd5e1";
  context.fillText(String(latest.year), plotX + plotWidth, chartY + chartHeight - 18);
  context.textAlign = "left";
}

function drawShareCard(country: CountryDetailResponse, historyItems: CountryHistoryItem[], locale: "en" | "es"): string {
  const canvas = document.createElement("canvas");
  canvas.width = 1200;
  canvas.height = 630;

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas context unavailable");
  }

  context.fillStyle = "#020617";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.fillStyle = "#0f172a";
  context.fillRect(36, 36, canvas.width - 72, canvas.height - 72);

  context.fillStyle = "#7dd3fc";
  context.font = "600 28px Outfit, Inter, system-ui, sans-serif";
  context.fillText(t(locale, "shareAtlasTitle"), 72, 100);

  context.fillStyle = "#f8fafc";
  context.font = "700 64px Epilogue, Inter, system-ui, sans-serif";
  context.fillText(country.name_en, 72, 200);

  context.fillStyle = "#94a3b8";
  context.font = "500 32px Outfit, Inter, system-ui, sans-serif";
  context.fillText(`ISO3 ${country.iso3} · ${locale === "es" ? "Último año" : "Latest year"} ${country.latest_year ?? "N/A"}`, 72, 250);

  context.fillStyle = "#e2e8f0";
  context.font = "600 35px Outfit, Inter, system-ui, sans-serif";
  context.fillText(`${t(locale, "debtLabel")}: ${formatUsdCompact(getDebtStock(country))}`, 72, 338);
  context.fillText(`${t(locale, "debtPerCapitaLabel")}: ${formatUsdCompact(country.debt_per_capita_usd)}`, 72, 398);
  context.fillText(`${t(locale, "debtToGdpLabel")}: ${formatPercentage(country.debt_pct_gdp)}`, 72, 458);

  drawMiniChart(context, historyItems, locale);

  context.fillStyle = "#38bdf8";
  context.font = "500 24px Inter, system-ui, sans-serif";
  context.fillText("deudamundi.econopapi.com", 72, 560);

  return canvas.toDataURL("image/png");
}

export function ShareCardActions({ country, historyItems }: ShareCardActionsProps) {
  const locale = useLocaleStore((state) => state.locale);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const shareText = useMemo(() => buildShareText(country, locale), [country, locale]);

  const handleDownloadCard = () => {
    try {
      const image = drawShareCard(country, historyItems, locale);
      const anchor = document.createElement("a");
      anchor.href = image;
      anchor.download = `deudamundi-${country.iso3.toLowerCase()}-share-card.png`;
      anchor.click();
      setStatusMessage(t(locale, "shareCardDownloaded"));
    } catch {
      setStatusMessage(t(locale, "shareCardError"));
    }
  };

  const handleShare = async () => {
    const sharePayload = {
      title: `${t(locale, "shareTitlePrefix")} · ${country.name_en}`,
      text: shareText,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(sharePayload);
        setStatusMessage(t(locale, "shareSuccess"));
        return;
      } catch {
        // User cancellation or browser-level share errors are handled by fallback.
      }
    }

    try {
      await navigator.clipboard.writeText(`${shareText}\n${window.location.href}`);
      setStatusMessage(t(locale, "shareCopied"));
    } catch {
      setStatusMessage(t(locale, "shareUnavailable"));
    }
  };

  return (
    <section className="glass-panel rounded-xl p-4">
      <h2 className="text-sm font-semibold text-[#f5f4f0]">{t(locale, "shareTitle")}</h2>
      <p className="mt-2 text-xs text-[#888680]">{t(locale, "shareSubtitle")}</p>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleDownloadCard}
          className="rounded-md border border-[#3b4252] bg-[#0d1017]/80 px-3 py-2 text-xs text-[#f5f4f0] hover:border-[#6d7280]"
        >
          {t(locale, "downloadShareCard")}
        </button>
        <button
          type="button"
          onClick={() => {
            void handleShare();
          }}
          className="rounded-md border border-[#7c6af5] bg-[#7c6af5]/20 px-3 py-2 text-xs text-[#ede9fe] hover:border-[#a594f9]"
        >
          {t(locale, "shareCountryProfile")}
        </button>
      </div>

      {statusMessage && <p className="mt-2 text-xs text-[#888680]">{statusMessage}</p>}
    </section>
  );
}
