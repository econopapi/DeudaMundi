import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { RankingsPage } from "./RankingsPage";

const mockFetchRankings = jest.fn();

jest.mock("../services/deudamundiApi", () => ({
  fetchRankings: (metric: string, region?: string, limit?: number) => mockFetchRankings(metric, region, limit),
}));

describe("RankingsPage", () => {
  beforeEach(() => {
    mockFetchRankings.mockReset();
  });

  it("loads and renders ranking rows", async () => {
    mockFetchRankings.mockResolvedValue({
      metric: "absolute",
      region: null,
      limit: 20,
      items: [
        {
          rank: 1,
          iso3: "MEX",
          name_en: "Mexico",
          region: "Latin America & Caribbean",
          value: 591255026725,
          latest_year: 2024,
        },
      ],
    });

    render(
      <MemoryRouter initialEntries={["/rankings"]}>
        <Routes>
          <Route path="/rankings" element={<RankingsPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText("Mexico (MEX)")).toBeInTheDocument();
    expect(mockFetchRankings).toHaveBeenCalledWith("absolute", undefined, 20);
  });

  it("updates metric filter", async () => {
    const user = userEvent.setup();

    mockFetchRankings.mockResolvedValue({
      metric: "absolute",
      region: null,
      limit: 20,
      items: [],
    });

    render(
      <MemoryRouter initialEntries={["/rankings"]}>
        <Routes>
          <Route path="/rankings" element={<RankingsPage />} />
        </Routes>
      </MemoryRouter>,
    );

  const metricSelect = await screen.findByLabelText("Métrica");
    await user.selectOptions(metricSelect, "pct_gdp");

    expect(mockFetchRankings).toHaveBeenCalledWith("pct_gdp", undefined, 20);
  });
});
