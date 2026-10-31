# Cronología metodológica (§3)

Orden verificado con `git log` (husos horarios del autor, -06:00 en el historial local). Clasificaciones exigidas por el protocolo de cierre. Sin fechas inventadas: cada línea se deriva del historial real de commits y del contenido de los diffs.

| Commit | Fecha | Contenido | Clasificación | Impacto |
|---|---|---|---|---|
| f72d157 | 2026-10-30 | Paso 1: entorno congelado (fotografía de 41 distribuciones, manifiesto | Regla/dato definido antes de todo el análisis de actividad | Base del universo; sin decisiones de análisis. |
| 5277ba2 | 2026-10-30 | Paso 2 endurecido (grafo) | Regla/dato | Grafo de exposición usado por H3/lectura profunda. |
| 823ecc4 / 104cdc1 / c129e4e | 2026-10-30 | Paso 3: atribución documental 37→35 y verificación | Regla/dato | Mapa de repositorios y compartidos (una sola cuenta por repo). |
| f68a511 | 2026-10-30 | Subprotocolo del paso 4 (ventanas, streams, bots, recibos) | Regla definida ANTES de la recolección (preregistrada, verificable por orden de commits) | Recolecta ocurrir después (5bc37e7 10:07). Sin cambios de reglas en la extracción. |
| 5bc37e7 | 2026-10-30 | Recolección de los 443 JSON | Ejecución de regla | Datos congelados; sin análisis de cuotas. |
| 1363af8 | 2026-10-30 | Auditoría de calidad del paso 4 (agotar releases) | Corrección de implementación de la regla de extracción (post-recolección, pre-análisis) | Añade 3 páginas de releases; totales de eventos sin cambio (documentado). |
| 65b8d02 | 2026-10-30 | Plan del paso 5 (H1–H4, umbrales 30/10/5, denominadores, unidades) | Reglas definidas antes de los contrastes versionados | Limitación honesta: el historial Git no puede demostrar ausencia de impresiones de terminal previas; los consecutivos versionados sí. Regla de H4 definida aquí sin precisar 'pares totales vs revisor top' (precisada después; ver 99617fb). |
| c57005f | 2026-10-30 | Aclaración 1: observabilidad del rol de revisión (≥5 pares) | Aclaración registrada después del plan, antes de los primeros resultados versionados | No precisó total vs top; lacimal implementación inicial usó el conteo del revisor top (defecto corregido en 99617fb). |
| e56114d | 2026-10-30 | Aclaración 2-3: continuidad + variante con bots + selección de casos | Aclaración registrada después del plan, antes de los primeros resultados versionados | La definición de 'variante con bots' no fijó unidades: se corrigió en 99617fb (misma unidad que la métrica principal). |
| 9334d39 | 2026-10-30 | Selección mecánica de 6 casos (solo grafo del paso 2) | Aplicación de regla del protocolo | No depende de métricas de actividad. |
| 9750be8 | 2026-10-30 | Primer análisis versionado y evidencia PyPI | Ejecución de reglas | Primera versión de resultados con un error real de implementación (den del commits incluía bots) y clasificaciones provisionales; conservado para trazabilidad. |
| 7b6dc3b … eb03582 | 2026-10-30 | Figuras, plugin puente y publicación en borrador (WordPress) | Producto editorial/visual | No cambia reglas o umbrales; incluye la reversión byte-idéntica del borrador y el v0.1.x del plugin. |
| 99617fb | 2026-10-30 | Correcciones de rigor (denominador de commits, variante bots unidades, flag congelada, H4 total-pair, porcentajes de bots, botones fig3) | Corrección de implementación + modificación metodológica posterior (la aplicación a 'pares totales' en H4) | Anexa tabla antes/después en esta misma carpeta (traceability). El resultado de H1/H2 queda en los mismos umbrales; H4 gana 3 evaluables en 24m sin cambios de divergencias. |
| e02ad67 | 2026-10-30 | Verificaciones funcionales + payloads + checkout limpio | Verificación | Sin cambios metodológicos. |

## Preguntas del auditor respondidas

1. **Cuándo se definieron H1–H4:** commit `65b8d02` (2026-10-30 11:43), documento versionado en la rama; predates la mayoría de las ejecuciones de script que resultan en resultados versionados (`9750be8` 11:58).
2. **Cuándo se congelaron los datos:** `5bc37e7` (10:07) con la auditoría `1363af8` (10:18); todo PREVIO al plan del paso 5.
3. **Primeros contrastes:** `9750be8` (11:58) — la versión conservada incluye una implementación con un error real documentado; se conserva como evidencia y no se reescribe de forma silenciosa.
4. **Modificaciones de denominadores/umbrales:** NINGUNA. Los umbrales 30/10/5 no cambiaron; los denominadores fueron corregidos para referirse a las definiciones del plan (99617fb, corrección de implementación).
5. **Modificaciones posteriores a los resultados:** (a) correcciones de implementación (tabla de commits 99617fb); (b) UNA modificación metodológica posterior reconocida: la operativa de evaluabilidad del rol de revisión se definió como 'total de pares' en 99617fb (antes quedó ambigua en la aclaración c57005f y se implementó 'revisor top'). Impacto documentado (3 repos 24m pasan a evaluables, divergencias no cambian); (c) el resto son verificaciones, documentación y producto editorial.

## Advertencias de capacidad del historial

- La anterioridad del plan es demostrable frente a los RESULTADOS VERSIONADOS, no frente a impresiones de terminal tempranas que no persisten. No se afirma 'preregistrado' con significado más fuerte que esto.
- Las Aclaraciones 1–3 son modificaciones al plan registradas con commits DISTINCTOS del plan original; su ventana temporal es clara.
- No hay commits que alteren el dataset congelado después de 1363af8 (verificado con `git log -- maintenance/data` en el checkout).

### Commits que tocaron `maintenance/data/`: ['1363af8', '5bc37e7']