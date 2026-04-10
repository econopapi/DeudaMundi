import {
  buildCompareHistoryExportRows,
  buildCompareLatestExportRows,
  buildCountryHistoryExportRows,
  buildCountryLatestExportRows,
  rowsToCsv,
} from "./dataExports";
import type { CountryCompareItem, CountryDetailResponse, CountryHistoryItem } from "../types/api";

const sampleCountry: CountryDetailResponse = {
  iso3: "ARG",
  iso2: "AR",
  name_es: "Argentina",
  name_en: "Argentina",
  region: "Latin America & Caribbean",
  subregion: "South America",
  population: 46000000,
  capital: "Buenos Aires",
  latest_year: 2024,
  total_external_debt_usd: 1000,
  debt_per_capita_usd: 20,
  debt_pct_gdp: 45,
  gdp_usd: 2000,
  equivalences: [],
};

const sampleHistory: CountryHistoryItem[] = [
  {
    year: 2023,
    total_external_debt_usd: 900,
    debt_per_capita_usd: 19,
    debt_pct_gdp: 44,
    gdp_usd: 1900,
    source: "worldbank",
  },
];

describe("dataExports", () => {
  it("builds country rows for latest and history export", () => {
    const latest = buildCountryLatestExportRows(sampleCountry);
    const history = buildCountryHistoryExportRows(sampleCountry, sampleHistory);

    expect(latest).toHaveLength(1);
    expect(latest[0].iso3).toBe("ARG");
    expect(history).toHaveLength(1);
    expect(history[0].year).toBe(2023);
  });

  it("builds compare rows and serializes csv", () => {
    const compareItems: CountryCompareItem[] = [
      {
        detail: sampleCountry,
        history: sampleHistory,
      },
    ];

    const latestRows = buildCompareLatestExportRows(compareItems);
    const historyRows = buildCompareHistoryExportRows(compareItems);

    expect(latestRows[0].iso3).toBe("ARG");
    expect(historyRows[0].source).toBe("worldbank");

    const csv = rowsToCsv(historyRows);
    expect(csv).toContain("iso3,name_en,year");
    expect(csv).toContain("ARG,Argentina,2023");
  });
});
