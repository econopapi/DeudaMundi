# Paso 6 — protocolo de lectura y clasificación cualitativa

**Estado:** protocolo de análisis cualitativo **registrado antes de producir las
interpretaciones finales** de los seis casos. Se redacta el 2 de noviembre de
2026, **después** del análisis cuantitativo del Paso 5 (cerrado con dictamen
`../analysis/final-audits/dictamen.md`, 30-10-2026) y **no constituye un
preregistro original**: los criterios de clasificación son posteriores a la
observación de las métricas congeladas y así se declara en todo el paquete.

Este documento no cambia nada del Paso 5: ni ventanas, ni umbrales, ni
unidades, ni evaluabilidad, ni reglas de bots, ni resultados de H1–H4. Los
datos congelados (443 JSON de `../data/`, inventario, grafo, atribuciones) se
leen **en solo lectura**.

## Pregunta guía

**¿Qué puede saberse sobre quién realiza, coordina y publica el mantenimiento
de las dependencias Python de DeudaMundi, y hasta dónde alcanza la evidencia?**

La unidad de análisis es el **repositorio atribuido** (seis casos fijados
mecánicamente en `../analysis/plan.md`, Aclaración 3), no la persona. Donde la
documentación identifica solo cuentas, el análisis se detiene en las cuentas.

## Fuentes admitidas

1. **Artefactos congelados del estudio** (autoridad primaria para hechos
   cuantitativos): `../../graph/`, `../../attributions/`, `../data/`,
   `../analysis/results/`, `../analysis/final-audits/`, `../analysis/pypi-evidence/`.
   Cualquier cifra citada en este paso proviene de aquí y conserva su
   denominador original.
2. **Documentación pública de los proyectos** (README, GOVERNANCE,
   CONTRIBUTING, SECURITY, docs de release, páginas de patrocinio, metadatos
   PyPI congelados en `../../attributions/pypi-evidence/`).
3. **Literatura académica y de organismos** priorizada por el protocolo de
   Notion (ver `literature.md`).
4. **Fuentes web recuperadas durante este paso**: siempre con **fecha de
   consulta** y, cuando la URL lo permite, **commit o versión**. Se consultan
   a partir del **2 de noviembre de 2026**, es decir, **después** del corte
   exclusivo `2026-10-30T00:00:00Z`. **Ninguna fuente recuperada ahora
   representa necesariamente el estado histórico del 30 de octubre de 2026**;
   cada entrada del índice de evidencia lo anota. Si una fuente permite fijar
   un commit anterior al corte (p. ej. archivo versionado), se cita el commit
   y se marca como documento histórico fechado por su propio contenido.

## Categorías de contenido (qué se clasifica)

Cada fragmento de evidencia se clasifica en **una o varias** de estas
categorías. La clasificación evita mezclar planos que las métricas mantienen
distintos:

| Código | Categoría | Qué cubre | Qué NO cubre |
|---|---|---|---|
| C1 | Actividad observable en GitHub | Commits, PR, revisiones, releases, issues públicas con definición operacional del Paso 4 | Trabajo no registrado en GitHub |
| C2 | Mantenimiento formalmente documentado | Roles y responsabilidades declarados en documentación oficial del proyecto (p. ej. equipo de mantenedores listado, proceso de release escrito) | La ejecución real de esas responsabilidades |
| C3 | Gobernanza y autoridad de decisión | Quién puede aceptar cambios, publicar versiones, definir rumbo; políticas de contribución; mecanismos de sucesión | La práctica efectiva no documentada |
| C4 | Desarrollo, revisión, integración y publicación | Flujo de trabajo observable por roles de evento (autoría, revisión, integración `merged_by`, publicación) | La calidad o el esfuerzo de cada rol |
| C5 | Financiación y patrocinio declarados | Patrocinio público (GitHub Sponsors, fundaciones, empleadores **declarados por el propio proyecto o cuenta**) | Salarios, presupuestos, dedicación, porcentaje de trabajo remunerado |
| C6 | Continuidad organizacional y sucesión | Transferencias de responsabilidad documentadas, cambios de propiedad del repositorio o del paquete, relevo de roles | Predicción de continuidad futura |
| C7 | Evidencia desconocida o no verificable | Lo que las fuentes consultadas no permiten establecer | — (es la categoría residual honesta) |
| C8 | Trabajo no observable en fuentes públicas | Soporte, coordinación privada, seguridad no pública, docencia, triage no registrado: se **documenta su existencia como límite**, sin estimarlo | Cualquier cuantificación de ese trabajo |

## Niveles de evidencia (código obligatorio en cada afirmación)

- **E1 — Documental directa:** política institucional, documentación oficial
  del proyecto, roles públicos declarados o declaraciones verificables del
  propio proyecto/cuenta. Cita literal o referencia exacta.
- **E2 — Observación técnica:** registros de GitHub, PyPI, workflows, commits,
  PR y releases con definición operacional (incluye los artefactos congelados
  del estudio). El hecho es el registro, no su interpretación.
- **E3 — Inferencia contextual:** interpretación razonada del analista.
  **Nunca equivale a un hecho demostrado**; se redacta como lectura y se
  acompaña de la evidencia E1/E2 que la motiva y de la contraevidencia conocida.
- **E4 — Desconocido:** ausencia de información suficiente. Se registra la
  búsqueda realizada (qué se consultó y qué no apareció) para que el vacío sea
  reproducible.

Reglas de uso:

- Ninguna conclusión destacada del artículo puede apoyarse **solo** en E3.
- Toda afirmación sobre una organización o cuenta concreta requiere E1 o E2.
- Las lecturas E3 se marcan explícitamente en el texto con fórmulas del tipo
  «esto sugiere…, pero la evidencia disponible no permite afirmarlo».
- E4 no se rellena con plausibilidad: si no hay evidencia, se declara.

## Reglas de atribución (límites no negociables de este paso)

1. **Una cuenta GitHub no equivale necesariamente a una persona.** No se
   identifican personas detrás de cuentas; no se recogen datos personales
   innecesarios; solo roles públicos de proyecto.
2. **No se reclasifica retrospectivamente automatización no declarada.**
   `claude`, `sqla-tester` e `invalid-email-address` conservan su
   clasificación congelada; se citan como **patrones documentados** que
   condicionan la lectura (ver `../analysis/audits.md`).
3. **No se infieren causalidad, riesgo, abandono, bus factor, remuneración ni
   responsabilidad formal.** Poca actividad observable no demuestra abandono;
   mucha actividad no demuestra organización.
4. **No se mezclan observaciones posteriores al corte con eventos de las
   ventanas congeladas.** Los hechos web posteriores al 30-10-2026 se marcan
   como «observado el 02-11-2026» y solo contextualizan; no alteran ningún
   resultado H1–H4.
5. Los rankings de eventos del Paso 5 **no se convierten en atribuciones de
   responsabilidad**; se leen como distribución de eventos por cuenta.

## Procedimiento de lectura por caso

Para cada uno de los seis casos (`sqlalchemy/sqlalchemy`, `sqlalchemy/alembic`,
`python/typing_extensions`, `kjd/idna`, `psycopg/psycopg`, `kludex/starlette`):

1. **A. Identificación y relación con DeudaMundi:** desde artefactos congelados
   (`distribution-map.csv`, `graph/nodes.csv`, `graph/paths.txt`,
   `source-repos.csv`): distribución instalada, versión congelada, carácter
   directo/transitivo, rutas desde la raíz, alcance real de la atribución
   paquete→repositorio (incluidos repositorios compartidos y redirecciones).
2. **B. Organización y gobernanza (C2/C3):** propietarios públicos, políticas
   de contribución, mantenedores nombrados **cuando exista evidencia E1**,
   procedimientos de aceptación de cambios, seguridad, publicación de
   versiones y mecanismos conocidos de sucesión.
3. **C. Roles observables (C1/C4):** relacionar el expediente con las métricas
   congeladas (`repo-metrics.csv`, `actor-shares.csv`, `audit-packs.json`,
   `traceability-h1h4.csv`), distinguiendo autoría, revisión, integración,
   publicación y automatización. Sin convertir rankings en responsabilidad.
4. **D. Incentivos y financiación (C5):** fundaciones, empresas, patrocinio,
   proyectos asociados o financiación **declarada**. Prohibido inferir
   salarios, presupuestos o porcentajes de trabajo remunerado.
5. **E. Continuidad y límites (C6):** señales documentadas de coordinación,
   transferencias de responsabilidad, estabilidad o cambios organizacionales.
   Sin deducir abandono de poca actividad.
6. **F. Contraste (C7/C8):** qué confirma, contradice o matiza el análisis
   cuantitativo; **evidencia que debilite la interpretación atractiva**
   (contraejemplo obligatorio).
7. **G. Fuentes:** URL exacta, tipo de documento, fecha de consulta, commit o
   versión cuando exista, fragmento verificable y nivel de evidencia (E1–E4).

## Triangulación con H1–H4

La triangulación (ver `synthesis.md`) **no recalcula** hipótesis: confronta la
evidencia cualitativa con los resultados descriptivos congelados, con los
valores de referencia fijados por el dictamen (H1 12m: 22 evaluables / 15
cuotas numéricas > 50 % / FastAPI inconcluso / 14 conclusivos; H2 12m: 6
cambios de categoría de 18 evaluables; H3: psycopg, certifi, httpx, tzlocal;
H4 12m: 18 repos incluidos, 16 con revisión evaluable, 6 divergencias y 10
coincidencias entre autoría, integración y revisión). Para cada hipótesis se
separa: (1) resultado descriptivo congelado; (2) interpretación permitida; (3)
interpretación **no** permitida; (4) contexto cualitativo; (5) contraejemplo o
límite; (6) redacción editorial recomendada con fuentes. La sensibilidad de 24
meses y la distinción revisiones crudas / pares únicos revisor–PR se
conservan. **Planos:** H4 contrasta autoría, integración y revisión; la
publicación de versiones es un cuarto plano que H4 **no** incorpora y la
responsabilidad organizacional no la mide ningún contraste (ver `synthesis.md`
§4.2 y `limitations.md` §2.5 para los grados de conocimiento A–D).

## Destino de cada interpretación

Toda afirmación destinada al artículo pasa antes por `claim-ledger.csv`
(identificador, texto propuesto, nivel de evidencia, fuente exacta, artefacto
cuantitativo relacionado, estado de verificación y destino editorial). Ninguna
cifra, afirmación sobre organización o conclusión destacada se publica sin
entrada verificable en el registro. La cobertura se comprueba por sección del
artículo con `coverage-matrix.csv` (matriz artículo ↔ registro), no por la
mera existencia del registro.

## Relación con los demás artefactos del paso

| Archivo | Contenido |
|---|---|
| `cases/` | Seis expedientes (A–G) por repositorio |
| `evidence/` | Índice de fuentes y procedencia (fechas de consulta, commits) |
| `synthesis.md` | Triangulación H1–H4 y respuesta científica integrada |
| `claim-ledger.csv` | Registro trazable de afirmaciones |
| `literature.md` | Marco conceptual y bibliografía crítica |
| `limitations.md` | Límites de alcance y evidencia |
| `editorial-handoff.md` | Propuesta de edición para WordPress y especificación de figuras |
| `factual-review.md` | Preguntas y mensajes propuestos para revisión externa |
| `deferred-comparative-cohort.md` | Recomendación de diferir la cohorte de otros backends |
| `status-matrix.md` | Matriz Fase 0 (completado / pendiente / requiere decisión editorial) |
| `README.md` | Guía de navegación y reproducción |
