import type { ReactNode } from "react";

import { AuthorCredits } from "./AuthorCredits";

type AppHeaderProps = {
  title: string;
  subtitle: string;
  actions?: ReactNode;
};

export function AppHeader({ title, subtitle, actions }: AppHeaderProps) {
  return (
    <header className="grid gap-4 border-b border-[#2a2f3a] pb-6 lg:grid-cols-[1fr_340px] lg:items-start">
      <div>
        <h1 className="display-title text-3xl font-extrabold tracking-tight text-[#f5f4f0] md:text-4xl">{title}</h1>
        <p className="mt-2 max-w-3xl text-sm text-[#888680] md:text-base">{subtitle}</p>
        {actions ? <div className="mt-4 flex flex-wrap items-center gap-3">{actions}</div> : null}
      </div>
      <AuthorCredits className="glass-panel rounded-xl px-4 py-3" />
    </header>
  );
}
