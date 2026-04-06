import { useMemo, useState } from "react";

import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import type { CountryDetailResponse } from "../../types/api";

type ShareCardActionsProps = {
  country: CountryDetailResponse;
};

function buildShareText(country: CountryDetailResponse): string {
  const debtPerCapita = formatUsdCompact(country.debt_per_capita_usd);
  const debtPct = formatPercentage(country.debt_pct_gdp);

  return `${country.name_en} (${country.iso3}) · Debt per capita: ${debtPerCapita} · Debt/GDP: ${debtPct}. Explore: ${window.location.href}`;
}

function drawShareCard(country: CountryDetailResponse): string {
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
  context.font = "600 28px Inter, system-ui, sans-serif";
  context.fillText("Global Debt Atlas", 72, 100);

  context.fillStyle = "#f8fafc";
  context.font = "700 64px Inter, system-ui, sans-serif";
  context.fillText(country.name_en, 72, 200);

  context.fillStyle = "#94a3b8";
  context.font = "500 32px Inter, system-ui, sans-serif";
  context.fillText(`ISO3 ${country.iso3} · Latest year ${country.latest_year ?? "N/A"}`, 72, 250);

  context.fillStyle = "#e2e8f0";
  context.font = "600 44px Inter, system-ui, sans-serif";
  context.fillText(`Total external debt: ${formatUsdCompact(country.total_external_debt_usd)}`, 72, 355);
  context.fillText(`Debt per capita: ${formatUsdCompact(country.debt_per_capita_usd)}`, 72, 425);
  context.fillText(`Debt / GDP: ${formatPercentage(country.debt_pct_gdp)}`, 72, 495);

  context.fillStyle = "#38bdf8";
  context.font = "500 24px Inter, system-ui, sans-serif";
  context.fillText("deudamundi.dlimon.net", 72, 560);

  return canvas.toDataURL("image/png");
}

export function ShareCardActions({ country }: ShareCardActionsProps) {
  const [statusMessage, setStatusMessage] = useState<string>("");
  const shareText = useMemo(() => buildShareText(country), [country]);

  const handleDownloadCard = () => {
    try {
      const image = drawShareCard(country);
      const anchor = document.createElement("a");
      anchor.href = image;
      anchor.download = `deudamundi-${country.iso3.toLowerCase()}-share-card.png`;
      anchor.click();
      setStatusMessage("Share card downloaded.");
    } catch {
      setStatusMessage("Could not generate share card in this browser.");
    }
  };

  const handleShare = async () => {
    const sharePayload = {
      title: `Debt profile · ${country.name_en}`,
      text: shareText,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(sharePayload);
        setStatusMessage("Shared successfully.");
        return;
      } catch {
        // User cancellation or browser-level share errors are handled by fallback.
      }
    }

    try {
      await navigator.clipboard.writeText(`${shareText}\n${window.location.href}`);
      setStatusMessage("Share text copied to clipboard.");
    } catch {
      setStatusMessage("Share unavailable. Copy URL manually.");
    }
  };

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <h2 className="text-sm font-semibold text-slate-200">Share</h2>
      <p className="mt-2 text-xs text-slate-400">Generate a social card image or share this country profile link.</p>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleDownloadCard}
          className="rounded-md border border-slate-700 bg-slate-950/50 px-3 py-2 text-xs text-slate-100 hover:border-slate-500"
        >
          Download share card (PNG)
        </button>
        <button
          type="button"
          onClick={() => {
            void handleShare();
          }}
          className="rounded-md border border-sky-700 bg-sky-900/20 px-3 py-2 text-xs text-sky-100 hover:border-sky-500"
        >
          Share country profile
        </button>
      </div>

      {statusMessage && <p className="mt-2 text-xs text-slate-400">{statusMessage}</p>}
    </section>
  );
}
