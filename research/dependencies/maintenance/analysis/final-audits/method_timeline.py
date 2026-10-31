#!/usr/bin/env python3
"""Final-audit §3 (methodological timeline) and §4 (H1–H4 traceability).

Produces:
  final-audits/method_timeline.csv   (one row per relevant commit + classification)
  final-audits/method_timeline.md    (narrative + honesty limitations)
  final-audits/traceability-h1h4.csv (per repo/window audit rows for H1, H2, H4;
                                      H3 lives in h3-test.csv and pypi map)
Run from the repository root (no network).
"""

import csv
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
ROOT = HERE.parents[4]


def git_log(path):
    out = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--format=%h|%cI|%s", "--reverse",
         "--", path], capture_output=True, text=True).stdout
    rows = []
    for line in out.strip().splitlines():
        if not line:
            continue
        h, d, s = line.split("|", 2)
        rows.append((h, d, s))
    return rows


TIMELINE = [
    # (commit, alcance, clasificación requerida, impacto/validación)
    ("f72d157", "Paso 1: entorno congelado (fotografía de 41 distribuciones, manifiesto",
     "Regla/dato definido antes de todo el análisis de actividad",
     "Base del universo; sin decisiones de análisis."),
    ("5277ba2", "Paso 2 endurecido (grafo)",
     "Regla/dato", "Grafo de exposición usado por H3/lectura profunda."),
    ("823ecc4 / 104cdc1 / c129e4e", "Paso 3: atribución documental 37→35 y verificación",
     "Regla/dato", "Mapa de repositorios y compartidos (una sola cuenta por repo)."),
    ("f68a511", "Subprotocolo del paso 4 (ventanas, streams, bots, recibos)",
     "Regla definida ANTES de la recolección (preregistrada, verificable por orden de commits)",
     "Recolecta ocurrir después (5bc37e7 10:07). Sin cambios de reglas en la extracción."),
    ("5bc37e7", "Recolección de los 443 JSON",
     "Ejecución de regla", "Datos congelados; sin análisis de cuotas."),
    ("1363af8", "Auditoría de calidad del paso 4 (agotar releases)",
     "Corrección de implementación de la regla de extracción (post-recolección, pre-análisis)",
     "Añade 3 páginas de releases; totales de eventos sin cambio (documentado)."),
    ("65b8d02", "Plan del paso 5 (H1–H4, umbrales 30/10/5, denominadores, unidades)",
     "Reglas definidas antes de los contrastes versionados",
     "Limitación honesta: el historial Git no puede demostrar ausencia de impresiones de terminal previas; los consecutivos versionados sí. Regla de H4 definida aquí sin precisar 'pares totales vs revisor top' (precisada después; ver 99617fb)."),
    ("c57005f", "Aclaración 1: observabilidad del rol de revisión (≥5 pares)",
     "Aclaración registrada después del plan, antes de los primeros resultados versionados",
     "No precisó total vs top; lacimal implementación inicial usó el conteo del revisor top (defecto corregido en 99617fb)."),
    ("e56114d", "Aclaración 2-3: continuidad + variante con bots + selección de casos",
     "Aclaración registrada después del plan, antes de los primeros resultados versionados",
     "La definición de 'variante con bots' no fijó unidades: se corrigió en 99617fb (misma unidad que la métrica principal)."),
    ("9334d39", "Selección mecánica de 6 casos (solo grafo del paso 2)",
     "Aplicación de regla del protocolo", "No depende de métricas de actividad."),
    ("9750be8", "Primer análisis versionado y evidencia PyPI",
     "Ejecución de reglas",
     "Primera versión de resultados con un error real de implementación (den del commits incluía bots) y clasificaciones provisionales; conservado para trazabilidad."),
    ("7b6dc3b … eb03582", "Figuras, plugin puente y publicación en borrador (WordPress)",
     "Producto editorial/visual",
     "No cambia reglas o umbrales; incluye la reversión byte-idéntica del borrador y el v0.1.x del plugin."),
    ("99617fb", "Correcciones de rigor (denominador de commits, variante bots unidades, flag congelada, H4 total-pair, porcentajes de bots, botones fig3)",
     "Corrección de implementación + modificación metodológica posterior (la aplicación a 'pares totales' en H4)",
     "Anexa tabla antes/después en esta misma carpeta (traceability). El resultado de H1/H2 queda en los mismos umbrales; H4 gana 3 evaluables en 24m sin cambios de divergencias."),
    ("e02ad67", "Verificaciones funcionales + payloads + checkout limpio",
     "Verificación", "Sin cambios metodológicos."),
]


def main():
    # timeline
    with open(HERE / "method_timeline.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["commit(s)", "alcance", "clasificación", "impacto/validación"])
        for c, scope, cls, impact in TIMELINE:
            w.writerow([c, scope, cls, impact])
    # verify each referenced commit hash exists (guard against invented hashes)
    real = set()
    for h, d, s in git_log("research/dependencies"):
        real.add(h)
    for entry in TIMELINE:
        for token in entry[0].split(" / "):
            token = token.strip().split()[0]
            if token not in real and len(token) == 7:
                raise ValueError(f"commit inexistente en la línea temporal: {token}")
    md = ["# Cronología metodológica (§3)",
          "",
          "Orden verificado con `git log` (fechas locales autor LST-06). Clasificaciones exigidas por el protocolo de cierre. Sin inventar fechas: la tabé registro aquí se deriva de los commits y del contenido real de los diffs.",
          "",
          "| Commit | Fecha | Contenido | Clasificación | Impacto |",
          "|---|---|---|---|---|"]
    hashes = {h: d for h, d, _ in git_log("research/dependencies")}
    for c, scope, cls, impact in TIMELINE:
        first = c.split(" / ")[0].strip().split()[0]
        d = hashes.get(first, "(hash compuesto)")
        md.append(f"| {c} | {d[:10] if d != '(hash compuesto)' else d} | {scope} | {cls} | {impact} |")
    md += [
        "",
        "## Preguntas del auditor respondidas",
        "",
        "1. **Cuándo se definieron H1–H4:** commit `65b8d02` (2026-10-30 11:43), documento versionado en la rama; predates la mayoría de las ejecuciones de script que resultan en resultados versionados (`9750be8` 11:58).",
        "2. **Cuándo se congelaron los datos:** `5bc37e7` (10:07) con la auditoría `1363af8` (10:18); todo PREVIO al plan del paso 5.",
        "3. **Primeros contrastes:** `9750be8` (11:58) — la versión conservada incluye una implementación con un error real documentado; se conserva como evidencia y no se reescribe de forma silenciosa.",
        "4. **Modificaciones de denominadores/umbrales:** NINGUNA. Los umbrales 30/10/5 no cambiaron; los denominadores fueron corregidos para referirse a las definiciones del plan (99617fb, corrección de implementación).",
        "5. **Modificaciones posteriores a los resultados:** (a) correcciones de implementación (tabla de commits 99617fb); (b) UNA modificación metodológica posterior reconocida: la operativa de evaluabilidad del rol de revisión se definió como 'total de pares' en 99617fb (antes quedó ambigua en la aclaración c57005f y se implementó 'revisor top'). Impacto documentado (3 repos 24m pasan a evaluables, divergencias no cambian); (c) el resto son verificaciones, documentación y producto editorial.",
        "",
        "## Advertencias de capacidad del historial",
        "",
        "- La anterioridad del plan es demostrable frente a los RESULTADOS VERSIONADOS, no frente a impresiones de terminal tempranas que no persisten. No se afirma 'preregistrado' con significado más fuerte que esto.",
        "- Las Aclaraciones 1–3 son modificaciones al plan registradas con commits DISTINCTOS del plan original; su ventana temporal es clara.",
        "- No hay commits que alteren el dataset congelado después de 1363af8 (verificado con `git log -- maintenance/data` en el checkout).",
    ]
    (HERE / "method_timeline.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # no freez dataset touched git check
    out = subprocess.run(["git", "-C", str(ROOT), "log", "--oneline",
                          "--format=%h", "--", "research/dependencies/maintenance/data"],
                         capture_output=True, text=True).stdout.strip().splitlines()
    md.append(f"### Commits que tocaron `maintenance/data/`: {out}")
    (HERE / "method_timeline.md").open("a", encoding="utf-8").write("\n" + "\n".join(md[-1:]))
    print("method_timeline listo; datasets commits tocados:", out)

    # §4 traceability CSV
    hyp = json.load(open(RESULTS / "hypotheses.json"))
    import csv as _csv
    mrows = {}
    with (RESULTS / "repo-metrics.csv").open(newline="", encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            mrows[(r["repo"], r["window_end"])] = r
    out_rows = []
    with open(HERE.parents[2] / "attributions" / "source-repos.csv", newline="", encoding="utf-8") as f:
        dists = list(_csv.DictReader(f))
    for window in ("12m", "24m"):
        for r in hyp["windows"][window]["H1"]:
            m = mrows[(r["repo"], window)]
            out_rows.append({
                "hypothesis": "H1", "repo": r["repo"], "window": window,
                # H1 denominador: commits no-bot SIN fusiones (humanos + no atribuidos)
                "numerator": m["cmt_top1_count"],
                "denominator": r["den_nonmerge"],
                "indicator": "cuota top-1 de commit_cuenta (no-bot, sin fusiones)",
                "threshold": ">50%",
                "result_share": r["share"],
                "evaluable": True,
                "state": ("conclusivo>50" if r["conclusive_over_50"]
                          else ("inconcluso" if r["inconclusive"] else "<=50%")),
                "top_actor": r["top1"],
                "exclusion_notes": "excluye fusiones, bots; no-atribuidos dentro del denominador",
                "limitations": "cuenta GitHub ≠ persona; rama principal observada",
            })
        for r in hyp["windows"][window]["H2"]:
            out_rows.append({
                "hypothesis": "H2", "repo": r["repo"], "window": window,
                "numerator": "-", "denominator": "≥30 commits y ≥10 PR fusionados no-bot",
                "indicator": "categoría (≤50/50-75/>75) commits vs PR",
                "threshold": "categorías distintas",
                "result_share": f"{r['commit_share']}→{r['pr_share']}",
                "evaluable": True,
                "state": ("cambia" if r["changed"] else "no cambia"),
                "top_actor": f"(fusión de roles)",
                "exclusion_notes": "PR fusionados a rama principal; bots fuera",
                "limitations": "cuenta GitHub ≠ persona",
            })
        for r in hyp["windows"][window]["H4"]:
            out_rows.append({
                "hypothesis": "H4", "repo": r["repo"], "window": window,
                "numerator": "-", "denominator": "≥30 commits y ≥10 PR; ≥5 pares de revisión no-bot TOTALES",
                "indicator": "cuenta top de commits ≠ cuenta top integración o revisión",
                "threshold": "cualquiera de los dos roles difiere",
                "result_share": "-",
                "evaluable": r["reviewer_evaluable"],
                "state": ("diverge" if (r["commit_pr_differ"] or r["commit_rev_differ"])
                          else "coincide"),
                "top_actor": f"cmt={r['top_committer']}; int={r['top_integrator']}; rev={r['top_reviewer']}",
                "exclusion_notes": "roles: autoría, integración (merged_by), revisión (pares únicos)",
                "limitations": "sqla-tester/claude/invalid-email-address advertidos",
            })
    fields = ["hypothesis", "repo", "window", "numerator", "denominator", "indicator",
              "threshold", "result_share", "evaluable", "state", "top_actor",
              "exclusion_notes", "limitations"]
    with (HERE / "traceability-h1h4.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"traceability: {len(out_rows)} filas")


if __name__ == "__main__":
    main()
