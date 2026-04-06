type GlobeLegendProps = {
  minDebtPctGdp: number;
  maxDebtPctGdp: number;
};

export function GlobeLegend({ minDebtPctGdp, maxDebtPctGdp }: GlobeLegendProps) {
  return (
    <aside className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-xs text-slate-300 shadow-lg backdrop-blur">
      <p className="mb-2 font-semibold text-slate-100">Debt % GDP intensity</p>
      <div className="mb-2 h-3 w-40 rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-500" />
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>{minDebtPctGdp.toFixed(1)}%</span>
        <span>{maxDebtPctGdp.toFixed(1)}%</span>
      </div>
    </aside>
  );
}
