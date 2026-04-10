import {
  buildComparePdfReportData,
  buildCompareHistoryExportRows,
  buildCompareLatestExportRows,
  buildCountryPdfReportData,
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

  it("builds aligned yearly series for PDF compare report", () => {
    const compareItems: CountryCompareItem[] = [
      {
        detail: sampleCountry,
        history: [
          {
            year: 2022,
            total_external_debt_usd: 850,
            debt_per_capita_usd: 18,
            debt_pct_gdp: 43,
            gdp_usd: 1800,
            source: "worldbank",
          },
          {
            year: 2024,
            total_external_debt_usd: 1000,
            debt_per_capita_usd: 20,
            debt_pct_gdp: 45,
            gdp_usd: 2000,
            source: "worldbank",
          },
        ],
      },
    ];

    const report = buildComparePdfReportData(compareItems);

    expect(report.years).toEqual([2022, 2024]);
    expect(report.countries[0].stockSeries).toEqual([850, 1000]);
    expect(report.countries[0].pctSeries).toEqual([43, 45]);
  });

  it("builds country PDF report series sorted by year", () => {
    const report = buildCountryPdfReportData(sampleCountry, [
      {
        year: 2024,
        total_external_debt_usd: 1000,
        debt_per_capita_usd: 20,
        debt_pct_gdp: 45,
        gdp_usd: 2000,
        source: "worldbank",
      },
      {
        year: 2022,
        total_external_debt_usd: 850,
        debt_per_capita_usd: 18,
        debt_pct_gdp: 43,
        gdp_usd: 1800,
        source: "worldbank",
      },
    ]);

    expect(report.iso3).toBe("ARG");
    expect(report.years).toEqual([2022, 2024]);
    expect(report.stockSeries).toEqual([850, 1000]);
    expect(report.pctSeries).toEqual([43, 45]);
  });
});
