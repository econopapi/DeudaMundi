type LoadingPanelProps = {
  message: string;
  detail?: string;
  className?: string;
};

export function LoadingPanel({ message, detail, className = "" }: LoadingPanelProps) {
  return (
    <section
      className={`rounded-2xl border border-[#2a2f3a] bg-[#11151f]/90 p-6 text-sm text-[#c8c7c2] transition-all duration-300 ${className}`.trim()}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-[#7c6af5]" aria-hidden="true" />
        <p className="font-medium text-[#f5f4f0]">{message}</p>
      </div>
      {detail && <p className="mt-2 text-xs text-[#888680]">{detail}</p>}
      <div className="mt-4 grid grid-cols-3 gap-2">
        <span className="h-2 rounded bg-[#1d2029] shimmer" />
        <span className="h-2 rounded bg-[#1d2029] shimmer" />
        <span className="h-2 rounded bg-[#1d2029] shimmer" />
      </div>
    </section>
  );
}
