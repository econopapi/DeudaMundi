# Límites de alcance y de evidencia (Paso 6)

**Fecha:** 2 de noviembre de 2026. Este documento complementa las limitaciones
persistentes del dictamen de cierre del Paso 5
(`../analysis/final-audits/dictamen.md` §Limitaciones) sin reemplazarlas. Los
límites del Paso 5 siguen vigentes **íntegros**.

## 1. Límites estructurales de los datos (heredados del Paso 5)

1. **Rama principal por fecha**: los commits se extrajeron de la rama principal
   observada; la historia por ramas de cada repositorio no está reconstruida.
2. **Ventana de PR por `updatedAt`**: la descubribilidad de PR depende de su
   fecha de actualización; no hay foto transaccional completa.
3. **Tags sin objeto release**: los tags de Git sin release de GitHub quedan
   fuera de la métrica de releases por diseño del API.
4. **Cobertura ≠ completitud absoluta**: «35/35 + eventos completos» certifica
   la extracción bajo sus reglas, no que GitHub entregue todo el histórico.
5. **Alias no fusionados**: una misma persona puede operar varias cuentas sin
   ser detectada (y una cuenta puede corresponder a varias personas o a una
   automatización).
6. **Compartimiento de datos**: el origen se apoya en recibos HTTP fechados;
   re-consultar GitHub hoy no añade nada sobre el pasado y sí introduce
   desviación temporal.
7. **Automatización no declarada**: la regla de bots (`type=Bot` o sufijo
   `[bot]`) no detecta todas las automatizaciones. Tres patrones quedaron
   documentados sin recategorizar (`claude`, `sqla-tester`,
   `invalid-email-address`, ver `../analysis/audits.md`): cualquier lectura
   literal de «quién hace el trabajo» en esos repositorios está contaminada.
8. **Repositorios compartidos** (`psycopg/psycopg-binary`,
   `pydantic/pydantic-core`): su actividad puede incluir trabajo ajeno a la
   distribución instalada.
9. **Corte exclusivo**: `2026-10-30T00:00:00Z`. Nada de lo observado después
   modifica los resultados; nada de las ventanas puede leerse como estado
   actual.

## 2. Límites de la evidencia cualitativa (nuevos en este paso)

1. **Posterioridad temporal**: la documentación pública se consultó el
   02-11-2026 (y los artefactos congelados de PyPI/atribución, el 30-10-2026).
   Las páginas web pueden haber cambiado respecto al estado histórico del corte
   (p. ej. un README editado tras la ventana). Cada fuente lleva fecha de
   consulta y commit/versión cuando la URL lo permite; **no se presenta ninguna
   fuente posterior al corte como representativa del 30-10-2026**.
2. **Disponibilidad selectiva de la documentación**: lo que un proyecto
   documenta (gobernanza, financiación, sucesión) depende de sus costumbres.
   La ausencia de un `GOVERNANCE.md` **no** prueba ausencia de gobernanza; solo
   prueba ausencia de documento público localizado (así se codifica: E4 con la
   búsqueda registrada).
3. **Documentación ≠ práctica**: un proceso de release escrito (E1) no demuestra
   que se siga en cada release; un rol nombrado no demuestra su ejercicio. Los
   expedientes separan siempre el plano documental (C2/C3) del observable
   (C1/C4).
4. **Cuentas ≠ personas**: todo lo que la evidencia permite nombrar son cuentas
   y roles públicos. No se resuelve la identidad personal detrás de las cuentas
   y no se recogen datos personales innecesarios.
5. **Financiación solo declarada**: se registra patrocinio o afiliación cuando
   el proyecto o la cuenta lo declara públicamente (E1). **No** se infieren
   salarios, dedicación, presupuestos ni porcentaje de trabajo remunerado. La
   ausencia de declaración de financiación (E4) no significa ausencia de
   financiación.
6. **Trabajo no observable (C8)**: soporte, coordinación privada, respuesta a
   incidentes de seguridad no pública, triage no registrado, docencia y
   mantenimiento emocional de comunidades **existen como categoría** pero no son
   medibles con estas fuentes. Toda conclusión de «quién mantiene» queda
   acotada al trabajo visible en las fuentes públicas consultadas.
7. **Sensibilidad de afirmaciones sobre actores**: las lecturas sobre
   gobernanza o incentivos de proyectos concretos están sometidas a revisión
   factual (`factual-review.md`) antes de publicarse; la ausencia de respuesta
   de un mantenedor no se interpretará como confirmación.

## 3. Límites de inferencia (qué no hace este paso)

- No infiere **causalidad** entre organización y métricas.
- No infiere **riesgo**, probabilidad de fallo, «bus factor» ni abandono. Una
  ventana sin releases o una cuota top-1 alta **no** son diagnósticos.
- No infiere **remuneración** ni valor económico: no se calculan costos
  salariales, externalidades ni valor de las dependencias (para el marco
  económico ver `literature.md`, que solo aporta contexto teórico).
- No reclasifica **automatización** no declarada ni fusiona alias.
- No extrapola al **ecosistema Python**: la unidad es el caso DeudaMundi; la
  cohorte comparativa queda diferida
  (`deferred-comparative-cohort.md`).
- No atribuye **responsabilidad formal**: «mantiene» en este estudio significa
  «actividad observable y roles documentados», no obligación legal ni
  compromiso de continuidad.

## 4. Límites de verificación de este paso

- Las verificaciones del Paso 5 se **conservan** (reproducción byte-idéntica ya
  auditada); este paso no re-ejecuta el análisis para no tocar derivados
  congelados y solo verifica hashes y consistencia en solo lectura.
- Hallazgo registrado H-01 (`status-matrix.md`): el manifiesto
  `maintenance/SHA256SUMS` tiene una entrada desactualizada para `README.md`
  (documentación, no datos); reproduce 453/454, no 454/454.
- Las fuentes web de este paso se recuperaron con las herramientas disponibles
  (fetch público); los endpoints que exigen autenticación o que no existen
  quedan como E4 con la URL intentada.
