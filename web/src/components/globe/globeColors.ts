function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/**
 * Compute the value at a given percentile (0–1) from an unsorted array.
 * Uses linear interpolation between adjacent ranks.
 */
export function percentile(values: number[], p: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  if (sorted.length === 1) return sorted[0];
  const idx = p * (sorted.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
}

/**
 * Default percentile used to cap the color-scale maximum so that
 * extreme outliers (financial centres with >500 % debt/GDP) don't
 * crush the visual distribution of the rest of the globe.
 */
export const COLOR_SCALE_CAP_PERCENTILE = 0.95;

export function getDebtColor(value: number, min: number, max: number): string {
  if (!Number.isFinite(value) || max <= min) {
    return "#94a3b8";
  }

  const t = clamp((value - min) / (max - min), 0, 1);

  if (t < 0.5) {
    const localT = t / 0.5;
    const r = Math.round(lerp(16, 251, localT));
    const g = Math.round(lerp(185, 191, localT));
    const b = Math.round(lerp(129, 36, localT));
    return `rgb(${r}, ${g}, ${b})`;
  }

  const localT = (t - 0.5) / 0.5;
  const r = Math.round(lerp(251, 225, localT));
  const g = Math.round(lerp(191, 29, localT));
  const b = Math.round(lerp(36, 72, localT));
  return `rgb(${r}, ${g}, ${b})`;
}
