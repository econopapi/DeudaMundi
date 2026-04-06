type AppHeaderProps = {
  title: string;
  subtitle: string;
};

export function AppHeader({ title, subtitle }: AppHeaderProps) {
  return (
    <header className="border-b border-slate-800 pb-6">
      <h1 className="text-3xl font-bold tracking-tight text-slate-100">{title}</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-400">{subtitle}</p>
    </header>
  );
}
