from app.schemas.country import EquivalenceItem

# Valores de referencia globales iniciales (MVP). En fase posterior se harán por país/año.
DEFAULT_HOSPITAL_COST_USD = 150_000_000
DEFAULT_TEACHER_ANNUAL_SALARY_USD = 12_000
DEFAULT_MIN_WAGE_ANNUAL_USD = 3_600


def build_equivalences(total_external_debt_usd: float | None) -> list[EquivalenceItem]:
    if not total_external_debt_usd or total_external_debt_usd <= 0:
        return []

    hospitals = total_external_debt_usd / DEFAULT_HOSPITAL_COST_USD
    teacher_years = total_external_debt_usd / DEFAULT_TEACHER_ANNUAL_SALARY_USD
    minimum_wages = total_external_debt_usd / DEFAULT_MIN_WAGE_ANNUAL_USD

    return [
        EquivalenceItem(
            label="hospitales_publicos",
            value=round(hospitals, 2),
            description="Hospitales públicos aproximados que podrían financiarse.",
        ),
        EquivalenceItem(
            label="anios_salario_docente",
            value=round(teacher_years, 2),
            description="Años de salario docente (referencia global estimada).",
        ),
        EquivalenceItem(
            label="salarios_minimos_anuales",
            value=round(minimum_wages, 2),
            description="Cantidad equivalente de salarios mínimos anuales.",
        ),
    ]
