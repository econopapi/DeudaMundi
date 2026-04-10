import { buildSuggestedComparePairs } from "./HomePage";
import type { GlobeDataPoint } from "../types/api";

function makePoint(input: Partial<GlobeDataPoint> & Pick<GlobeDataPoint, "iso3" | "name_en">): GlobeDataPoint {
  return {
    iso3: input.iso3,
    name_en: input.name_en,
    region: input.region ?? null,
    latest_year: input.latest_year ?? 2024,
    total_external_debt_usd: input.total_external_debt_usd ?? 100,
    debt_per_capita_usd: input.debt_per_capita_usd ?? null,
    debt_pct_gdp: input.debt_pct_gdp ?? null,
    debt_stock_usd: input.debt_stock_usd,
  };
}

describe("buildSuggestedComparePairs", () => {
  it("prioritizes the configured LATAM and developed pairs", () => {
    const points: GlobeDataPoint[] = [
      makePoint({ iso3: "USA", name_en: "United States", region: "North America", total_external_debt_usd: 1000 }),
      makePoint({ iso3: "JPN", name_en: "Japan", region: "East Asia & Pacific", total_external_debt_usd: 920 }),
      makePoint({ iso3: "GBR", name_en: "United Kingdom", region: "Europe & Central Asia", total_external_debt_usd: 800 }),
      makePoint({ iso3: "MEX", name_en: "Mexico", region: "Latin America & Caribbean", total_external_debt_usd: 600 }),
      makePoint({ iso3: "BRA", name_en: "Brazil", region: "Latin America & Caribbean", total_external_debt_usd: 700 }),
      makePoint({ iso3: "ARG", name_en: "Argentina", region: "Latin America & Caribbean", total_external_debt_usd: 500 }),
      makePoint({ iso3: "URY", name_en: "Uruguay", region: "Latin America & Caribbean", total_external_debt_usd: 300 }),
      makePoint({ iso3: "COL", name_en: "Colombia", region: "Latin America & Caribbean", total_external_debt_usd: 400 }),
    ];

    const suggestions = buildSuggestedComparePairs(points);

    expect(suggestions.map((item) => item.label)).toEqual([
      "Mexico vs Brazil",
      "Brazil vs Argentina",
      "Uruguay vs Argentina",
      "United States vs Japan",
      "United States vs United Kingdom",
    ]);
  });
});
