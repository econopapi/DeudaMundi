import { useMemo, useState } from "react";

import { formatPercentage, formatUsdCompact } from "../../lib/formatters";
import { t } from "../../lib/translations";
import { useLocaleStore } from "../../store/localeStore";
import type { CountryDetailResponse } from "../../types/api";

type ShareCardActionsProps = {
  country: CountryDetailResponse;
};

function buildShareText(country: CountryDetailResponse, locale: "en" | "es"): string {
  const debtPerCapita = formatUsdCompact(country.debt_per_capita_usd);
  const debtPct = formatPercentage(country.debt_pct_gdp);

  if (locale === "es") {
    return `${country.name_en} (${country.iso3}) · Deuda per cápita: ${debtPerCapita} · Deuda/PIB: ${debtPct}. Explora: ${window.location.href}`;
  }

  return `${country.name_en} (${country.iso3}) · Debt per capita: ${debtPerCapita} · Debt/GDP: ${debtPct}. Explore: ${window.location.href}`;
}

function drawShareCard(country: CountryDetailResponse, locale: "en" | "es"): string {
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
  context.fillText(locale === "es" ? "Atlas de Deuda Pública" : "Public Debt Atlas", 72, 100);

  context.fillStyle = "#f8fafc";
  context.font = "700 64px Epilogue, Inter, system-ui, sans-serif";
  context.fillText(country.name_en, 72, 200);

  context.fillStyle = "#94a3b8";
  context.font = "500 32px Outfit, Inter, system-ui, sans-serif";
  context.fillText(`ISO3 ${country.iso3} · ${locale === "es" ? "Último año" : "Latest year"} ${country.latest_year ?? "N/A"}`, 72, 250);

  context.fillStyle = "#e2e8f0";
  context.font = "600 42px Outfit, Inter, system-ui, sans-serif";
  context.fillText(`${locale === "es" ? "Deuda pública externa" : "Public external debt"}: ${formatUsdCompact(country.total_external_debt_usd)}`, 72, 355);
  context.fillText(`${locale === "es" ? "Deuda per cápita" : "Debt per capita"}: ${formatUsdCompact(country.debt_per_capita_usd)}`, 72, 425);
  context.fillText(`${locale === "es" ? "Deuda / PIB" : "Debt / GDP"}: ${formatPercentage(country.debt_pct_gdp)}`, 72, 495);

  context.fillStyle = "#38bdf8";
  context.font = "500 24px Inter, system-ui, sans-serif";
  context.fillText("deudamundi.dlimon.net", 72, 560);

  return canvas.toDataURL("image/png");
}

export function ShareCardActions({ country }: ShareCardActionsProps) {
  const locale = useLocaleStore((state) => state.locale);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const shareText = useMemo(() => buildShareText(country, locale), [country, locale]);

  const handleDownloadCard = () => {
    try {
      const image = drawShareCard(country, locale);
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
