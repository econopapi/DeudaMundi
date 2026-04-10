import { getLatestChartScrollLeft, isMobileViewport } from "./chartScroll";

describe("chartScroll helpers", () => {
  it("detects mobile viewport threshold", () => {
    expect(isMobileViewport(767)).toBe(true);
    expect(isMobileViewport(768)).toBe(false);
  });

  it("calculates rightmost scroll position", () => {
    expect(getLatestChartScrollLeft(1200, 800)).toBe(400);
    expect(getLatestChartScrollLeft(600, 800)).toBe(0);
  });
});
