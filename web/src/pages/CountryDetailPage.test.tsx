import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { CountryDetailPage } from "./CountryDetailPage";

const mockFetchCountryDetail = jest.fn();
const mockFetchCountryHistory = jest.fn();
const mockFetchCountryGovernments = jest.fn();

jest.mock("../services/deudamundiApi", () => ({
  fetchCountryDetail: (iso3: string) => mockFetchCountryDetail(iso3),
  fetchCountryHistory: (iso3: string) => mockFetchCountryHistory(iso3),
  fetchCountryGovernments: (iso3: string) => mockFetchCountryGovernments(iso3),
}));

jest.mock("../components/country/CountryHistoryChart", () => ({
  CountryHistoryChart: () => <div>Evolución histórica del stock de deuda externa (USD)</div>,
}));

describe("CountryDetailPage", () => {
  beforeEach(() => {
    mockFetchCountryDetail.mockReset();
    mockFetchCountryHistory.mockReset();
    mockFetchCountryGovernments.mockReset();
  });

  it("renders country hero and core sections", async () => {
    mockFetchCountryDetail.mockResolvedValue({
      iso3: "ARG",
      iso2: "AR",
      name_es: "Argentina",
      name_en: "Argentina",
      region: "Latin America & Caribbean",
      subregion: "South America",
      population: 46000000,
      capital: "Buenos Aires",
      latest_year: 2023,
      total_external_debt_usd: 1000000000,
      debt_per_capita_usd: 20000,
      debt_pct_gdp: 40.3,
      gdp_usd: 2500000000,
      equivalences: [],
    });

    mockFetchCountryHistory.mockResolvedValue({
      iso3: "ARG",
      items: [
        {
          year: 2022,
          total_external_debt_usd: 900000000,
          debt_per_capita_usd: 18000,
          debt_pct_gdp: 39.2,
          gdp_usd: 2400000000,
          source: "worldbank",
        },
        {
          year: 2023,
          total_external_debt_usd: 1000000000,
          debt_per_capita_usd: 20000,
          debt_pct_gdp: 40.3,
          gdp_usd: 2500000000,
          source: "worldbank",
        },
      ],
    });

    mockFetchCountryGovernments.mockResolvedValue({
      iso3: "ARG",
      items: [
        {
          leader_name: "Leader Test",
          party: null,
          start_date: "2020-01-01",
          end_date: null,
          political_lean: null,
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={["/country/arg"]}>
        <Routes>
          <Route path="/country/:iso3" element={<CountryDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

  expect(await screen.findByText("Perfil del país")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Argentina" })).toBeInTheDocument();
  expect(screen.getByText("Evolución histórica del stock de deuda externa (USD)")).toBeInTheDocument();
  expect(screen.getByText("Métricas de deuda externa")).toBeInTheDocument();
  expect(screen.getByText("Equivalencias emocionales")).toBeInTheDocument();
    expect(mockFetchCountryDetail).toHaveBeenCalledWith("arg");
    expect(mockFetchCountryHistory).toHaveBeenCalledWith("arg");
    expect(mockFetchCountryGovernments).toHaveBeenCalledWith("arg");
  });

  it("shows source-unavailable messaging for null metrics", async () => {
    mockFetchCountryDetail.mockResolvedValue({
      iso3: "MEX",
      iso2: "MX",
      name_es: "México",
      name_en: "Mexico",
      region: "Latin America & Caribbean",
      subregion: "Latin America & Caribbean (excluding high income)",
      population: null,
      capital: "Mexico City",
      latest_year: 2024,
      total_external_debt_usd: 591255026725,
      debt_per_capita_usd: null,
      debt_pct_gdp: null,
      gdp_usd: null,
      equivalences: [],
    });

    mockFetchCountryHistory.mockResolvedValue({
      iso3: "MEX",
      items: [],
    });

    mockFetchCountryGovernments.mockResolvedValue({
      iso3: "MEX",
      items: [],
    });

    render(
      <MemoryRouter initialEntries={["/country/mex"]}>
        <Routes>
          <Route path="/country/:iso3" element={<CountryDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Perfil del país")).toBeInTheDocument();
    expect(screen.getByText("Algunos indicadores de razón no están disponibles actualmente en la fuente para el último año.")).toBeInTheDocument();
    expect(screen.getAllByText(/No disponible en la fuente/i).length).toBeGreaterThan(0);
  });
});
