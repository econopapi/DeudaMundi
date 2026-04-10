import type { Locale } from "../store/localeStore";
import type { EquivalenceItem } from "../types/api";

type EquivalencePresentationMeta = {
  icon: string;
  title: Record<Locale, string>;
  description: Record<Locale, string>;
  accentClassName: string;
};

export type PresentedEquivalence = {
  label: string;
  value: number;
  icon: string;
  title: string;
  description: string;
  accentClassName: string;
};

const EQUIVALENCE_META: Record<string, EquivalencePresentationMeta> = {
  hospitales_publicos: {
    icon: "🏥",
    title: {
      es: "Hospitales públicos potenciales",
      en: "Potential public hospitals",
    },
    description: {
      es: "Infraestructura hospitalaria aproximada que podría financiarse con un monto equivalente.",
      en: "Estimated hospital infrastructure that could be funded with an equivalent amount.",
    },
    accentClassName: "from-[#38bdf8]/20 to-[#38bdf8]/5 border-[#38bdf8]/40",
  },
  anios_salario_docente: {
    icon: "📚",
    title: {
      es: "Años de salario docente",
      en: "Teacher salary years",
    },
    description: {
      es: "Referencia estimada en años de remuneración docente para dimensionar magnitud fiscal.",
      en: "Estimated teacher-compensation years used as an intuitive fiscal scale reference.",
    },
    accentClassName: "from-[#a78bfa]/20 to-[#a78bfa]/5 border-[#a78bfa]/40",
  },
  salarios_minimos_anuales: {
    icon: "👷",
    title: {
      es: "Salarios mínimos anuales",
      en: "Annual minimum wages",
    },
    description: {
      es: "Cantidad equivalente de salarios mínimos anuales bajo una referencia global simplificada.",
      en: "Equivalent annual minimum wages using a simplified global benchmark.",
    },
    accentClassName: "from-[#22c55e]/20 to-[#22c55e]/5 border-[#22c55e]/40",
  },
};

function fallbackTitle(label: string): string {
  return label
    .split("_")
    .filter((chunk) => chunk.length > 0)
    .map((chunk) => `${chunk.charAt(0).toUpperCase()}${chunk.slice(1)}`)
    .join(" ");
}

export function presentEquivalences(items: EquivalenceItem[], locale: Locale): PresentedEquivalence[] {
  return items.map((item) => {
    const meta = EQUIVALENCE_META[item.label];

    if (!meta) {
      return {
        label: item.label,
        value: item.value,
        icon: "💡",
        title: fallbackTitle(item.label),
        description: item.description,
        accentClassName: "from-[#3b4252]/20 to-[#3b4252]/5 border-[#3b4252]/50",
      };
    }

    return {
      label: item.label,
      value: item.value,
      icon: meta.icon,
      title: meta.title[locale],
      description: meta.description[locale],
      accentClassName: meta.accentClassName,
    };
  });
}