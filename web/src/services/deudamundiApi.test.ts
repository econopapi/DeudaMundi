import { fetchCountryDetail, fetchCountryGovernments, fetchCountryHistory, fetchGlobeData } from "./deudamundiApi";

describe("deudamundiApi", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("calls globe-data endpoint", async () => {
    const mockResponse = {
      item_count: 1,
      items: [
        {
          iso3: "ARG",
          name_en: "Argentina",
          region: "Latin America",
          latest_year: 2023,
          total_external_debt_usd: 100,
          debt_per_capita_usd: 10,
          debt_pct_gdp: 50,
        },
      ],
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const result = await fetchGlobeData();

    expect(global.fetch).toHaveBeenCalledWith("https://deudamundi.dlimon.net/api/v1/globe-data");
    expect(result.items).toHaveLength(1);
  });

  it("calls globe-data endpoint with region query param", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ item_count: 0, items: [] }),
    } as Response);

    await fetchGlobeData("Latin America & Caribbean");

    expect(global.fetch).toHaveBeenCalledWith(
      "https://deudamundi.dlimon.net/api/v1/globe-data?region=Latin+America+%26+Caribbean",
    );
  });

  it("calls country detail endpoint with uppercase iso3", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        iso3: "ARG",
        iso2: "AR",
        name_es: "Argentina",
        name_en: "Argentina",
        region: "Latin America",
        subregion: "South America",
        population: 100,
        capital: "Buenos Aires",
        latest_year: 2023,
        total_external_debt_usd: 100,
        debt_per_capita_usd: 20,
        debt_pct_gdp: 45,
        gdp_usd: 200,
        equivalences: [],
      }),
    } as Response);

    const result = await fetchCountryDetail("arg");

    expect(global.fetch).toHaveBeenCalledWith("https://deudamundi.dlimon.net/api/v1/countries/ARG");
    expect(result.iso3).toBe("ARG");
  });

  it("calls country history endpoint", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ iso3: "ARG", items: [] }),
    } as Response);

    const result = await fetchCountryHistory("arg");

    expect(global.fetch).toHaveBeenCalledWith("https://deudamundi.dlimon.net/api/v1/countries/ARG/history");
    expect(result.iso3).toBe("ARG");
  });

  it("calls country governments endpoint", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ iso3: "ARG", items: [] }),
    } as Response);

    const result = await fetchCountryGovernments("arg");

    expect(global.fetch).toHaveBeenCalledWith("https://deudamundi.dlimon.net/api/v1/countries/ARG/governments");
    expect(result.iso3).toBe("ARG");
  });
});
