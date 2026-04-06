import { useEffect, useMemo, useState } from "react";

type MetricCounterProps = {
  label: string;
  value: number | null;
  formatter: (value: number | null) => string;
  durationMs?: number;
};

function useAnimatedNumber(target: number | null, durationMs: number): number | null {
  const [displayValue, setDisplayValue] = useState<number | null>(target);

  useEffect(() => {
    if (target === null || Number.isNaN(target)) {
      setDisplayValue(null);
      return;
    }

    const steps = 30;
  const stepDuration = Math.max(1, Math.floor(durationMs / steps));
    const startValue = 0;
    let currentStep = 0;

    setDisplayValue(startValue);

    const intervalId = window.setInterval(() => {
      currentStep += 1;
      const progress = Math.min(1, currentStep / steps);
      const nextValue = startValue + (target - startValue) * progress;
      setDisplayValue(nextValue);

      if (progress >= 1) {
        window.clearInterval(intervalId);
      }
    }, stepDuration);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [durationMs, target]);

  return displayValue;
}

export function MetricCounter({ label, value, formatter, durationMs = 900 }: MetricCounterProps) {
  const animatedValue = useAnimatedNumber(value, durationMs);

  const formattedValue = useMemo(() => {
    if (value === null) {
      return formatter(null);
    }

    if (animatedValue === null) {
      return formatter(null);
    }

    return formatter(animatedValue);
  }, [animatedValue, formatter, value]);

  return (
    <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-2 text-xl font-semibold text-slate-100 md:text-2xl">{formattedValue}</p>
    </article>
  );
}
