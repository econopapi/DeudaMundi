function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

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
