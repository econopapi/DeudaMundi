import { t } from "../lib/translations";
import { useLocaleStore } from "../store/localeStore";

export function LanguageSwitcher() {
  const locale = useLocaleStore((state) => state.locale);
  const setLocale = useLocaleStore((state) => state.setLocale);

  return (
    <div className="flex items-center gap-2 text-xs text-slate-300">
      <label htmlFor="locale" className="font-semibold uppercase tracking-wide text-slate-400">
        {t(locale, "languageLabel")}
      </label>
      <select
        id="locale"
        value={locale}
        onChange={(event) => setLocale(event.target.value as "en" | "es")}
        className="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-slate-100"
      >
        <option value="en">EN</option>
        <option value="es">ES</option>
      </select>
    </div>
  );
}
