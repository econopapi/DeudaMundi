import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { CountryDetailPage } from "./CountryDetailPage";

const mockFetchCountryDetail = jest.fn();

jest.mock("../services/deudamundiApi", () => ({
  fetchCountryDetail: (iso3: string) => mockFetchCountryDetail(iso3),
}));

describe("CountryDetailPage", () => {
  beforeEach(() => {
    mockFetchCountryDetail.mockReset();
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

    render(
      <MemoryRouter initialEntries={["/country/arg"]}>
        <Routes>
          <Route path="/country/:iso3" element={<CountryDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Country profile")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Argentina" })).toBeInTheDocument();
    expect(screen.getByText("Debt metrics")).toBeInTheDocument();
    expect(screen.getByText("Emotional equivalences")).toBeInTheDocument();
    expect(mockFetchCountryDetail).toHaveBeenCalledWith("arg");
  });
});
