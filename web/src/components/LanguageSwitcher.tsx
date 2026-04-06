import { t } from "../lib/translations";
import { useLocaleStore } from "../store/localeStore";

export function LanguageSwitcher() {
  const locale = useLocaleStore((state) => state.locale);
  const setLocale = useLocaleStore((state) => state.setLocale);

  return (
    <div className="flex items-center gap-2 text-xs text-[#c8c7c2]">
      <label htmlFor="locale" className="mono-meta font-semibold uppercase tracking-wide text-[#888680]">
        {t(locale, "languageLabel")}
      </label>
      <select
        id="locale"
        value={locale}
        onChange={(event) => setLocale(event.target.value as "en" | "es")}
        className="rounded-md border border-[#3b4252] bg-[#0d1017] px-2 py-1 text-xs text-[#f5f4f0] focus:border-[#7c6af5] focus:outline-none"
      >
        <option value="es">ES</option>
        <option value="en">EN</option>
      </select>
    </div>
  );
}
