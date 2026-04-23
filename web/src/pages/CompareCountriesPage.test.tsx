import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { CompareCountriesPage } from "./CompareCountriesPage";

const mockFetchGlobeData = jest.fn();
const mockFetchCountriesCompare = jest.fn();

jest.mock("../services/deudamundiApi", () => ({
  fetchGlobeData: () => mockFetchGlobeData(),
  fetchCountriesCompare: (iso3: string[]) => mockFetchCountriesCompare(iso3),
}));

jest.mock("../components/country/CountryComparisonChart", () => ({
  CountryComparisonChart: () => <div>Historical comparison: debt stock and debt/GDP</div>,
}));

describe("CompareCountriesPage", () => {
  beforeEach(() => {
    mockFetchGlobeData.mockReset();
    mockFetchCountriesCompare.mockReset();
  });

  it("loads comparison from countries query param", async () => {
    mockFetchGlobeData.mockResolvedValue({
      item_count: 2,
      items: [
        {
          iso3: "ARG",
          name_en: "Argentina",
          region: "Latin America & Caribbean",
          latest_year: 2024,
          total_external_debt_usd: 1,
          debt_per_capita_usd: 1,
          debt_pct_gdp: 1,
        },
        {
          iso3: "USA",
          name_en: "United States",
          region: "North America",
          latest_year: 2024,
          total_external_debt_usd: 1,
          debt_per_capita_usd: 1,
          debt_pct_gdp: 1,
        },
      ],
    });

    mockFetchCountriesCompare.mockResolvedValue({
      requested_iso3: ["ARG", "USA"],
      missing_iso3: [],
      item_count: 2,
      items: [
        {
          detail: {
            iso3: "ARG",
            iso2: "AR",
            name_es: "Argentina",
            name_en: "Argentina",
            region: "Latin America & Caribbean",
            subregion: "South America",
            population: 46000000,
            capital: "Buenos Aires",
            latest_year: 2024,
            total_external_debt_usd: 100,
            debt_per_capita_usd: 10,
            debt_pct_gdp: 40,
            gdp_usd: 200,
            source: "wb_ids_dt_dod_dect_cd",
            debt_concept: "external_debt_bop",
            data_source: "World Bank IDS DT.DOD.DECT.CD",
            equivalences: [],
          },
          history: [
            {
              year: 2024,
              total_external_debt_usd: 100,
              debt_per_capita_usd: 10,
              debt_pct_gdp: 40,
              gdp_usd: 200,
              source: "wb_ids_dt_dod_dect_cd",
            },
          ],
        },
        {
          detail: {
            iso3: "USA",
            iso2: "US",
            name_es: "Estados Unidos",
            name_en: "United States",
            region: "North America",
            subregion: "North America",
            population: 340000000,
            capital: "Washington, D.C.",
            latest_year: 2024,
            total_external_debt_usd: 999,
            debt_per_capita_usd: 10,
            debt_pct_gdp: 90,
            gdp_usd: 2000,
            source: "wb_ids_dt_dod_dect_cd",
            debt_concept: "external_debt_bop",
            data_source: "World Bank IDS DT.DOD.DECT.CD",
            equivalences: [],
          },
          history: [
            {
              year: 2024,
              total_external_debt_usd: 999,
              debt_per_capita_usd: 10,
              debt_pct_gdp: 90,
              gdp_usd: 2000,
              source: "wb_ids_dt_dod_dect_cd",
            },
          ],
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={["/compare?countries=arg,usa"]}>
        <Routes>
          <Route path="/compare" element={<CompareCountriesPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Comparación entre países")).toBeInTheDocument();
    expect(await screen.findByText("Historical comparison: debt stock and debt/GDP")).toBeInTheDocument();
    expect(await screen.findByRole("link", { name: "Argentina (ARG)" })).toBeInTheDocument();
    expect(await screen.findByText("Trazabilidad de datos")).toBeInTheDocument();
    expect((await screen.findAllByText(/DT\.DOD\.DECT\.CD/)).length).toBeGreaterThan(0);
    expect(mockFetchCountriesCompare).toHaveBeenCalledWith(["ARG", "USA"]);
  });
});
