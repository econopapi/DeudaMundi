import type { CountryDetailResponse, CountryHistoryItem } from "../types/api";

const SOURCE_TO_INDICATORS: Record<string, string[]> = {
  wb_ids_dt_dod_dect_cd: ["DT.DOD.DECT.CD", "NY.GDP.MKTP.CD", "SP.POP.TOTL"],
  wb_qeds_dt_dod_dect_cd_ar_us: ["DT.DOD.DECT.CD.AR.US", "NY.GDP.MKTP.CD", "SP.POP.TOTL"],
  imf_dm_proxy_ggxwdg: ["GGXWDG_NGDP", "NGDPD", "SP.POP.TOTL"],
};

function unique(values: Array<string | null | undefined>): string[] {
  return [...new Set(values.filter((value): value is string => Boolean(value && value.trim())))];
}

function inferSourceCodes(detail: CountryDetailResponse, history: CountryHistoryItem[]): string[] {
  if (history.length === 0) {
    return detail.source ? [detail.source] : [];
  }

  const preferredYear = detail.latest_year ?? history[0]?.year;
  const rowsForLatestYear = history.filter((item) => item.year === preferredYear);
  const latestRows = rowsForLatestYear.length > 0 ? rowsForLatestYear : [history[0]];
  const codes = unique(latestRows.map((item) => item.source));

  if (codes.length > 0) {
    return codes;
  }

  return detail.source ? [detail.source] : [];
}

export type CountryProvenance = {
  dataSource: string | null;
  debtConcept: string | null;
  sourceCodes: string[];
  indicators: string[];
  dataVintage: string | null;
};

export function buildCountryProvenance(
  detail: CountryDetailResponse,
  history: CountryHistoryItem[],
): CountryProvenance {
  const sourceCodes = inferSourceCodes(detail, history);
  const indicators = unique(
    sourceCodes.flatMap((sourceCode) => SOURCE_TO_INDICATORS[sourceCode] ?? [sourceCode]),
  );

  return {
    dataSource: detail.data_source ?? null,
    debtConcept: detail.debt_concept ?? null,
    sourceCodes,
    indicators,
    dataVintage: detail.data_vintage ?? null,
  };
}
