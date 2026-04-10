import { buildShareCardChartSeries } from "./shareCardChart";

describe("buildShareCardChartSeries", () => {
  it("prioritizes debt_stock_usd and sorts by year", () => {
    const series = buildShareCardChartSeries([
      {
        year: 2022,
        debt_stock_usd: 200,
        total_external_debt_usd: 100,
        debt_per_capita_usd: null,
        debt_pct_gdp: 44.2,
        gdp_usd: null,
        source: "test",
      },
      {
        year: 2021,
        total_external_debt_usd: 90,
        debt_per_capita_usd: null,
        debt_pct_gdp: 40.5,
        gdp_usd: null,
        source: "test",
      },
    ]);

    expect(series).toEqual([
      { year: 2021, debtStockUsd: 90, debtPctGdp: 40.5 },
      { year: 2022, debtStockUsd: 200, debtPctGdp: 44.2 },
    ]);
  });

  it("returns only the most recent points when maxPoints is exceeded", () => {
    const history = Array.from({ length: 6 }, (_, index) => ({
      year: 2019 + index,
      total_external_debt_usd: 100 + index,
      debt_per_capita_usd: null,
      debt_pct_gdp: 20 + index,
      gdp_usd: null,
      source: "test",
    }));

    const series = buildShareCardChartSeries(history, 3);

    expect(series).toEqual([
      { year: 2022, debtStockUsd: 103, debtPctGdp: 23 },
      { year: 2023, debtStockUsd: 104, debtPctGdp: 24 },
      { year: 2024, debtStockUsd: 105, debtPctGdp: 25 },
    ]);
  });

  it("keeps null debt-to-gdp values while preserving stock points", () => {
    const series = buildShareCardChartSeries([
      {
        year: 2024,
        total_external_debt_usd: 120,
        debt_per_capita_usd: null,
        debt_pct_gdp: null,
        gdp_usd: null,
        source: "test",
      },
    ]);

    expect(series).toEqual([{ year: 2024, debtStockUsd: 120, debtPctGdp: null }]);
  });
});
