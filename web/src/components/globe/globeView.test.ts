import { DEFAULT_GLOBE_VIEW, getGlobeViewForRegion } from "./globeView";

describe("getGlobeViewForRegion", () => {
  it("returns the configured focus for East Asia & Pacific", () => {
    expect(getGlobeViewForRegion("East Asia & Pacific")).toEqual({ lat: 21, lng: 126, altitude: 1.52 });
  });

  it("maps extended MENA label to the same focus", () => {
    expect(getGlobeViewForRegion("Middle East, North Africa, Afghanistan & Pakistan")).toEqual({ lat: 27, lng: 34, altitude: 1.56 });
  });

  it("returns default view when region is empty", () => {
    expect(getGlobeViewForRegion(undefined)).toEqual(DEFAULT_GLOBE_VIEW);
  });

  it("falls back to default view for unknown regions", () => {
    expect(getGlobeViewForRegion("Unknown Region")).toEqual(DEFAULT_GLOBE_VIEW);
  });
});
