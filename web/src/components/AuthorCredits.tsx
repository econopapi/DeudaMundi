import authorLogo from "../assets/author-logo.svg";

type AuthorCreditsProps = {
  compact?: boolean;
  className?: string;
};

export function AuthorCredits({ compact = false, className = "" }: AuthorCreditsProps) {
  const details = (
    <>
      {!compact && <p className="mono-meta text-xs font-semibold uppercase tracking-wide text-[#c8c7c2]">Info del autor</p>}
      <a
        href="https://econopapi.com"
        target="_blank"
        rel="noreferrer"
        className={`${compact ? "" : "mt-1"} block text-sm font-semibold text-[#f5f4f0] hover:text-[#c4b9fa]`}
      >
        Daniel Limon
      </a>
      <a
        href="mailto:dani@dlimon.net"
        className="mt-1 block text-sm text-[#a594f9] hover:text-[#c4b9fa]"
      >
        dani@dlimon.net
      </a>
    </>
  );

  if (compact) {
    return <section className={className}>{details}</section>;
  }

  return (
    <section className={className}>
      <div className="flex items-center gap-3">
        <a
          href="https://econopapi.com"
          target="_blank"
          rel="noreferrer"
          aria-label="Perfil de Daniel Limon en econopapi.com"
          className="shrink-0"
        >
          <img
            src={authorLogo}
            alt="Logo de Daniel Limon"
            className="h-14 w-14 rounded-md border border-[#2a2f3a] bg-[#0a0e18] p-1"
            loading="lazy"
          />
        </a>
        <div className="min-w-0">{details}</div>
      </div>
    </section>
  );
}
