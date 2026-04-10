import { AuthorCredits } from "./AuthorCredits";

export function AppFooter() {
  return (
    <footer className="border-t border-[#2a2f3a] bg-[#0b0f1b]/70">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-end sm:justify-between sm:px-6">
        <p className="text-xs text-[#888680]">DeudaMundi · Atlas de Deuda Externa</p>
        <AuthorCredits compact className="text-left sm:text-right" />
      </div>
    </footer>
  );
}
