# Dictamen final — auditoría metodológica y científica de cierre (Paso 5)

**Fecha:** 30 de octubre de 2026 UTC. **Checkout auditado:** `e02ad67…` (rama
`research/deudamundi-dependencies`). Sin acceso a GitHub; sin modificaciones al
dataset congelado; reglas del plan no renegociadas.

## Comandos ejecutados durante ESTA auditoría (con resultados)

| Comando | Resultado |
|---|---|
| `maintenance/verify_activity.py` | PASS 35/35; 144/183/45 páginas; 2 ventanas |
| `sha256sum -c maintenance/SHA256SUMS` | 454/454 OK (idéntico en checkout limpio) |
| `maintenance/analysis/analyze_activity.py` | PASS; cross-check vs `coverage-descriptive.csv`: 0 discrepancias |
| `maintenance/analysis/verify_contrasts.py` | PASS (recálculo independiente: variante bots por unidad, H4 por pares totales, resumen H1) |
| `final-audits/coverage_matrix.py` | matriz por repositorio: 35 filas; 443 JSON (372 páginas + 70 + 1); 0 HTTP≠200; `boundary_stop` en 29/35 (semántica del extractor) |
| `final-audits/method_timeline.py` | 14 hitos clasificados; commits que tocaron `data/`: `1363af8`, `5bc37e7` (443/454 exactos) |
| `final-audits/manual_sample_audit.py` | 8 repos estratificados; **0 discrepancias**; spot-checks: `claude` 36 no-fusión en 12m (38 con fusiones; publicado 36 ✓), `sqla-tester` 96 pares (publicado 96 ✓), `invalid-email-address` 0 en 12m / 462 en 24m |
| reconciliación de % bots (tercera vía) | OK: 1,495/7,014 = 21.3 % commits; 670/3,981 = 16.8 % PR; 2,610/10,543 = 24.8 % revisiones crudas; 1,638/5,756 = 28.5 % pares; 140/356 = 39.3 % releases |
| reconstrucción en checkout limpio | análisis, contrastes, figuras y plugin: sin red; ZIP byte-idéntico (`2becba85…`) |
| pruebas funcionales del render | 5 bloques + instancia duplicada; repintado por cambio de tema; clics reales en botones 12/24; móvil 390 px; sin CDN (fallback con tabla); sin JS (verificación por HTML servido; el flag headless no se honró, anotado) |

## Dictamen por dimensión (§8)

| Dimensión | Estado | Fundamento y condiciones |
|---|---|---|
| Integridad y completitud del dataset | **APROBADO CON LIMITACIONES** | Recibos y manifiestos verificables; límites registrados que no se pueden resolver con los datos congelados (rama principal histórica, paginación por `updatedAt`, tags sin release). Ninguno alterna un denominador publicado. |
| Integridad temporal del preregistro | **APROBADO CON LIMITACIONES** | Orden demostrable por commits: plan (65b8d02) antes de los resultados versionados (9750be8); tres aclaraciones con commit propio; data/ intacta después de 1363af8. La ausencia de impresiones de terminal previas NO es demostrable con Git (advertencia registrada). Los cambios post-análisis (unidades de la variante bots, aplicación de 'pares totales' en H4, clasificación por flag) quedan clasificados como correcciones de implementación/modificación metodológica documentada con tabla antes/después. |
| Reproducibilidad computacional | **APROBADO** | Re-ejecución completa en checkout limpio sin red: byte-idéntica (verificación cruzada incluida). |
| Consistencia de contrastes | **APROBADO CON LIMITACIONES** | H1 12m reconciliada fila a fila (22 evaluables / 15 cuotas numéricas >50 % / fastapi inconcluso / 14 conclusivos) y 24m (28/19/0/19) en `traceability-h1h4.csv`; H2 y H4 reconciliadas; los porcentajes de bots concilian por tercera vía. |
| Independencia de verificaciones | **APROBADO CON LIMITACIONES** | Tres implementaciones comparten dataset congelado y definiciones del plan: la 'independencia' es aritmética/lógica sobre los mismos datos de origen, no una fuente de datos nueva. Recibos HTTP por página = única evidencia de origen. Declarado en cada artefacto. |
| Validez de constructo | **APROBADO CON LIMITACIONES** | Matriz completa en `construct-validity.md` (constructo → indicador → permitido → no permitido). Las métricas no sustituyen identificación formal de mantenedores ni evaluación de riesgo. |
| Alcance de las conclusiones | **APROBADO CON LIMITACIONES** | Descriptivas del congelado; sin inferencia sobre el ecosistema u otros backends; las hipótesis económicas/organizacionales plausibles no se tratan como resultados. |
| Preparación científica para publicación | **APROBADO CON LIMITACIONES** | El pipeline y los entregables de investigación están listos. La publicación del artículo requiere además (fuera del paso 5): lectura profunda de los 6 casos seleccionados en el plan y revisión factual con los actores. |

**NO APROBADO:** ninguno. **PENDIENTE:** ninguno para el cierre del análisis.
Fuera del paso 5 (no deciden el cierre): ajuste fino del modo light y del
bloque genérico del tema, lectura cualitativa y revisión factual previas a
titulares.

## Hallazgos con impacto

1. Ninguno adicional que altere contrastes (los defectos previos ya corregidos
   quedan documentados con tabla antes/después en la ronda de rigor de 99617fb).
2. Matices de conteo cuantificados en esta auditoría (sin cambio de resultados):
   `claude` = 36 no-fusión (38 totales incl. 2 fusiones); `invalid-email-address`
   en fastapi = 0 (12m) / 462 (24m). Actualizados en `audits.md`.
3. Un defecto de estilo con frase corrupta en la matriz de cobertura se corrigió
   aquí mismo (registrado; los demás documentos se revisaron y quedaron limpios).

## Limitaciones persistentes (no resolubles con datos congelados)

1. Rama principal por fecha (necesitaría la historia de ramas de cada repositorio).
2. Ventana de PR por `updatedAt` (sin foto transaccional).
3. Tags sin objeto release (fuera de la métrica por diseño del API).
4. Cobertura por unidad ≠ completitud absoluta de todos los eventos históricos.
5. Alias no fusionados (una persona puede estar en varias cuentas sin ser detectada).
6. Compartimiento de datos: el 'verificado' de origen se apoya en recibos; re-consultar GitHub no añade nada tras esta auditoría, pero sí en un ciclo futuro con cortes nuevos de fecha.

## Conclusión

Con los datos congelados y las verificaciones ejecutadas: **el Paso 5 puede
cerrarse metodológicamente (APROBADO CON LIMITACIONES)**, con sus fronteras
declaradas (caso congelado, cuentas GitHub, sin ecosistema). La lectura profunda
de los seis casos, la revisión factual y la cohorte de otros backends son pasos
separados del protocolo y no bloquean este cierre; sí bloquean titulares y la
publicación final del artículo.
