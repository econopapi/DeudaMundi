const AVG_CHAR_PX = 5.8;

export const GOVERNMENT_LABEL_MAX_WIDTH = 120;

type LeaderLabelOptions = {
  locale?: "en" | "es";
};

export function estimateTextWidth(text: string): number {
  return text.length * AVG_CHAR_PX;
}

export function truncateTextToWidth(text: string, maxWidth: number): string {
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

export function compactLeaderName(fullName: string): string {
  const normalized = fullName.trim().replace(/\s+/g, " ");
  if (!normalized || /^Q\d+$/i.test(normalized)) {
    return "";
  }

  const tokens = normalized.split(" ");
  if (tokens.length <= 2) {
    return normalized;
  }

  return `${tokens[0]} ${tokens[tokens.length - 1]}`;
}

function normalizeName(fullName: string): string {
  const normalized = fullName.trim().replace(/\s+/g, " ");
  if (/^Q\d+$/i.test(normalized)) {
    return "";
  }

  return normalized;
}

function buildSpanishLeaderLabel(fullName: string, maxWidth: number): string {
  const normalized = normalizeName(fullName);
  if (!normalized) {
    return "";
  }

  if (estimateTextWidth(normalized) <= maxWidth) {
    return normalized;
  }

  const tokens = normalized.split(" ");
  if (tokens.length >= 3) {
    const firstAndLastTwo = `${tokens[0]} ${tokens.slice(-2).join(" ")}`;
    if (estimateTextWidth(firstAndLastTwo) <= maxWidth) {
      return firstAndLastTwo;
    }

    return truncateTextToWidth(firstAndLastTwo, maxWidth);
  }

  return truncateTextToWidth(normalized, maxWidth);
}

export function buildLeaderLabel(
  fullName: string,
  maxWidth: number = GOVERNMENT_LABEL_MAX_WIDTH,
  options: LeaderLabelOptions = {},
): string {
  if (options.locale === "es") {
    return buildSpanishLeaderLabel(fullName, maxWidth);
  }

  const compact = compactLeaderName(fullName);
  if (estimateTextWidth(compact) <= maxWidth) {
    return compact;
  }

  return truncateTextToWidth(compact, maxWidth);
}
