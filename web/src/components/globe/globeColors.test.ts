import { getDebtColor, percentile, COLOR_SCALE_CAP_PERCENTILE } from "./globeColors";

describe("getDebtColor", () => {
  it("returns fallback for non-finite values", () => {
    expect(getDebtColor(NaN, 0, 100)).toBe("#94a3b8");
    expect(getDebtColor(Infinity, 0, 100)).toBe("#94a3b8");
  });

  it("returns fallback when max <= min", () => {
    expect(getDebtColor(50, 100, 100)).toBe("#94a3b8");
    expect(getDebtColor(50, 200, 100)).toBe("#94a3b8");
  });

  it("returns green-ish for low values", () => {
    const color = getDebtColor(0, 0, 100);
    // Should be the start of the green ramp: rgb(16, 185, 129)
    expect(color).toBe("rgb(16, 185, 129)");
  });

  it("returns red-ish for high values", () => {
    const color = getDebtColor(100, 0, 100);
    // Should be the end of the red ramp: rgb(225, 29, 72)
    expect(color).toBe("rgb(225, 29, 72)");
  });

  it("clamps values above max to red end", () => {
    // Values above the scale max should produce the same color as max
    expect(getDebtColor(500, 0, 100)).toBe(getDebtColor(100, 0, 100));
  });
});

describe("percentile", () => {
  it("returns 0 for empty array", () => {
    expect(percentile([], 0.5)).toBe(0);
  });

  it("returns the single element for a 1-element array", () => {
    expect(percentile([42], 0.5)).toBe(42);
    expect(percentile([42], 0)).toBe(42);
    expect(percentile([42], 1)).toBe(42);
  });

  it("returns min at p=0 and max at p=1", () => {
    const values = [10, 20, 30, 40, 50];
    expect(percentile(values, 0)).toBe(10);
    expect(percentile(values, 1)).toBe(50);
  });

  it("computes median at p=0.5", () => {
    expect(percentile([1, 2, 3, 4, 5], 0.5)).toBe(3);
    expect(percentile([10, 20, 30, 40], 0.5)).toBe(25);
  });

  it("interpolates between adjacent values", () => {
    // p=0.25 of [0, 100] → idx=0.25, lo=0(0), hi=1(100) → 0 + 100*0.25 = 25
    expect(percentile([0, 100], 0.25)).toBe(25);
    expect(percentile([0, 100], 0.75)).toBe(75);
  });

  it("handles unsorted input", () => {
    expect(percentile([50, 10, 30, 20, 40], 0.5)).toBe(30);
  });

  it("caps outliers at P95 for realistic debt data", () => {
    // Simulate: 90 countries at 50%, 5 at 150%, 4 at 300%, 1 at 4000%
    const values = [
      ...Array(90).fill(50),
      ...Array(5).fill(150),
      ...Array(4).fill(300),
      4000,
    ];
    const p95 = percentile(values, 0.95);
    // P95 should be around 300 (not 4000)
    expect(p95).toBeLessThanOrEqual(300);
    expect(p95).toBeGreaterThanOrEqual(150);
  });
});

describe("COLOR_SCALE_CAP_PERCENTILE", () => {
  it("is 0.95", () => {
    expect(COLOR_SCALE_CAP_PERCENTILE).toBe(0.95);
  });
});
