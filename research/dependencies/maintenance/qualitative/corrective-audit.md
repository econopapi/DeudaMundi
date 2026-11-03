# Auditoría correctiva y cierre científico definitivo (Paso 6.1)

**Fecha:** 3 de noviembre de 2026 UTC. **Rama:**
`research/deudamundi-dependencies`. **HEAD verificado antes de empezar:**
`3c096f79e4aa1becf231b6b837989bc593797fa6` = referencia del encargo; sin
commits posteriores en el remoto (`git fetch` + comparación). **Árbol de
trabajo:** limpio al inicio. **Alcance:** corrección del paquete cualitativo y
documental; **no** se reabrió el Paso 5, **no** se tocaron los 443 JSON
congelados, resultados H1–H4, inventario, grafo ni atribuciones, **no** se
modificó WordPress 2735, `main` ni `dev`, **no** se contactó con mantenedores.

## Fuente de autoridad

Los contrastes se recontaron **exclusivamente** desde los artefactos canónicos:
`analysis/results/hypotheses.json`, `repo-metrics.csv`, `actor-shares.csv`,
`h3-test.csv`, `analysis/final-audits/traceability-h1h4.csv` y
`analysis/final-audits/dictamen.md`. Ninguna cifra se tomó de memoria ni de
resúmenes previos. El texto del artículo 2735 se leyó íntegro el 2026-11-03
vía `wp-json/wp/v2/posts/2735` **con la contraseña del post facilitada por el
autor** (solo lectura; el contenido no se versiona en este repositorio).

## Matriz de observaciones (Fase 1)

| ID | Observación | Archivos | Severidad | Evidencia | Corrección propuesta | Criterio de aceptación |
|---|---|---|---|---|---|---|
| O-01 | El conteo de coincidencias de H4 está mal: «6 de 12 (aprox.)» coinciden y «seis de los casos/ventanas los tres roles coinciden» (C39) | `synthesis.md` §4.5; `claim-ledger.csv` C39 | **Crítica** | `hypotheses.json` H4: 12 m 18 incluidos / 16 con revisión evaluable / **10 coinciden** / 6 divergen; 24 m 25/24/**18**/6 | Recontar, corregir textos y C39, adoptar la conclusión corregida | Conteos idénticos a `hypotheses.json`; C39 reescrita; sin generalizaciones incompatibles |
| O-02 | La sensibilidad 24 m de H4 está mal descrita («los seis divergentes se mantienen») | `synthesis.md` §4.1 | Alta | En 24 m `typing_extensions` **coincide** (tops `JelleZijlstra`) y entra `laurent-laporte-pro/deprecated` (`claude` top de commits) | Corregir la frase y las identidades | Identidades verificadas contra `hypotheses.json` |
| O-03 | No se distinguen los planos que mide H4; la publicación se mezcla con los tres roles | `synthesis.md` §4.2; `cases/psycopg-psycopg.md` §F; `cases/kludex-starlette.md` §C; `protocol.md` | Alta | H4 solo contrasta autoría/integración/revisión; la publicación es un cuarto plano (plan del Paso 5) | Declarar los tres planos + el cuarto (publicación) fuera de H4 | Afirmaciones de «quién publica» sin apoyo en H4 |
| O-04 | «Permanece desconocido» aplana grados distintos de conocimiento; se sugiere que no se sabe quién mantiene | `limitations.md`; `synthesis.md` §0.5/§6.4 | **Crítica** | Los expedientes identifican responsables declarados, roles y procesos (E1/E2) | Marco A/B/C/D + distinciones ausencia de evidencia / evidencia de ausencia / no observable | Texto que comunica «parte documentada y observable reconstruida», no fracaso de identificación |
| O-05 | «Sucesión formal desconocida en cinco de seis» sin soporte; transferencia histórica ≠ sucesión futura | `evidence/index.md`; casos §B/§E; `factual-review.md` | Alta | Starlette: transferencia administrativa 2025-09 (histórica); ningún caso documenta relevo futuro; SQLAlchemy tiene procesos documentados (Gerrit) sin protocolo de sucesión | Clasificación 1–5 por caso; eliminar el conteo 5/6 | Clasificación coherente en los seis expedientes y en el ledger (C49) |
| O-06 | Riesgo de leer los 6 casos como gobernanza de los 35 repos o muestra representativa | `synthesis.md`; `editorial-handoff.md` | Media | 35 repos cuantitativos vs 6 casos por regla mecánica (plan, Aclaración 3) | Separación explícita 35/6 en introducción, síntesis, límites y conclusión | Frase de alcance en §0, handoff §3.3 (C50) y conclusiones |
| O-07 | «Financiación declarada en cuatro de seis» sin unidad de conteo; SQLAlchemy y Alembic comparten estructura | `synthesis.md` §0.4/§6.1; `editorial-handoff.md` §3.2 | Media | `FUNDING.yml` idéntico en sqlalchemy/alembic; psycopg/starlette/idna/typing_extensions en casos §D | Canales documentados + unidad explícita (4 unidades de caso = 3 estructuras) + diferencias de categoría | C48 con denominador; sin porcentajes de prevalencia |
| O-08 | C45 afirma exhaustividad del registro sin prueba | `claim-ledger.csv` C45 | Alta | El artículo protegido no se había comparado fila a fila | **Opción A**: matriz de cobertura real sobre el texto íntegro | `coverage-matrix.csv` con toda afirmación mapeada y trazas resueltas (C46–C52) |
| O-09 | Literatura: citas literales no verificables contra el material recuperado | `literature.md` | Media | Revisión 2026-11-03: Osborne E1a re-verificado cita por cita; Hoffmann y Census III verificados; Eghbal 2 de 5 citas no verificables; Benkler/Lerner–Tirole sin fuente de las citas | Mantener solo citas verificadas; el resto a paráfrasis con nivel real | Sin citas sin fuente; tabla de recuperación por obra |
| O-10 | Comandos de reproducción con `cd` encadenados y frágiles | `qualitative/README.md` | Media | Comandos rompen al cambiar de directorio | Comandos desde la raíz + `verify_readonly.sh` | Script pasa en checkout limpio |
| O-11 | H-01: `maintenance/SHA256SUMS` reproduce 453/454 | `maintenance/SHA256SUMS`; `status-matrix.md` | Alta (documental) | Entrada `README.md` = `8188c665…` vs archivo real `81e9affe…`; causa `eaee185` post-`1363af8` | Actualizar **solo** esa entrada (excepción autorizada) y documentar | 454/454 OK; diff de una línea; 453 hashes idénticos |

### Discrepancias con el dictamen externo (comprobadas, no asumidas)

1. La afirmación literal **«los roles rara vez coinciden» no existe** ni en el
   artículo 2735 (§053, texto íntegro leído el 2026-11-03) ni en el paquete
   cualitativo. El defecto real (O-01) es distinto pero del mismo signo: el
   paquete **subestimaba las coincidencias** («6 de 12 aprox.» / «seis de los
   casos/ventanas») frente a las 10 de 16 reales. Se corrigió el defecto real y
   se deja constancia de la discrepancia.
2. El error de la sensibilidad 24 m de H4 (O-02) **no** constaba en el dictamen
   externo; se detectó en esta auditoría al recontar `hypotheses.json`.
3. El resto de observaciones del dictamen externo (H4/C39, grados de
   conocimiento, sucesión, alcance, financiación, C45, literatura, H-01,
   comandos) se comprobaron contra los archivos canónicos y **son correctas**.

## Recontos verificados (Fase 10)

| Contraste | Valor verificado (canónico) | Estado |
|---|---|---|
| H1 12 m | 22 evaluables, 15 cuotas numéricas > 50 %, FastAPI inconcluso (regla de bots), 14 concluyentes | ✓ `hypotheses.json` H1_summary |
| H1 24 m | 28 / 19 / 0 / 19 | ✓ |
| H2 12 m | 6 cambios de categoría de 18 evaluables (24 m: 10 de 25) | ✓ recontado |
| H3 | 4 repos: psycopg, certifi, httpx, tzlocal (PyPI + 0 releases + actividad) | ✓ `h3-test.csv` |
| H4 12 m | 18 incluidos; 16 con revisión evaluable; 10 coincidencias de los tres líderes; 6 divergencias (fastapi, pyjwt, click, typing_extensions, sqlalchemy, python-dotenv) | ✓ recontado + identidades |
| H4 24 m | 25 incluidos; 24 evaluables; 18 coincidencias; 6 divergencias (fastapi, pyjwt, deprecated, click, sqlalchemy, python-dotenv) | ✓ recontado + identidades |
| Revisión crudas vs pares | 2,610/10,543 (24.8 %) ≠ 1,638/5,756 (28.5 %): unidades separadas | ✓ sin mezclar |
| Bots declarados | 21.3 % commits / 16.8 % PR / 24.8 % revisiones / 28.5 % pares / 39.3 % releases | ✓ |
| Squash-mirror | uvicorn, typing_extensions, starlette, redis-py: commits sin merges = PR fusionados (web-flow); no es validación doble (C16) | ✓ sin cambios (ya correcto) |
| Automatización no declarada | `claude`, `sqla-tester`, `invalid-email-address` sin reclasificar | ✓ |
| Casos | 6 expedientes sin extrapolación; alcance 35 vs 6 declarado | ✓ |

## Hallazgo H-01 — reparación (excepción controlada)

1. **Diferencia exacta:** `maintenance/SHA256SUMS` declaraba
   `8188c66599b8f20e8ee1a1065de19b122bb34768e8ab3851ad4616ead1f6f1fa  README.md`;
   el archivo versionado tiene
   `81e9affe5f2427299f19c27c185115605dd54fcc64fb55446338ea10166265b6`.
2. **Archivo válido:** `maintenance/README.md` es documentación de navegación
   del Paso 4 (sin datos científicos); su contenido actual es coherente y ya
   verificado en el checkout `e02ad67` del dictamen.
3. **Causa (Git):** el README se editó en `eaee185` (2026-10-30, «align README
   wording with final WP integration path») **después** de escribirse el
   manifiesto en `1363af8`, sin refrescar la entrada.
4. **Corrección:** solo la línea de `README.md` en `maintenance/SHA256SUMS`
   (diff de una línea en el commit). **Hash anterior:** `8188c665…f6f1fa`.
   **Hash nuevo:** `81e9affe…265b6`. **Fecha:** 2026-11-03. **Motivo:**
   alinear el manifiesto con el documento ya versionado (hallazgo H-01).
5. **Verificación:** `sha256sum -c maintenance/SHA256SUMS` → **454/454 OK**.
6. **Datos intactos:** los 453 hashes restantes no se tocaron; los 443 JSON de
   actividad y todos los artefactos del Paso 4/5 siguen verificando
   (`verify_readonly.sh` comprueba además que no hay modificaciones sin
   commitear en rutas congeladas). H-01 queda registrado como anomalía
   documental **detectada y corregida**.

## Propuesta de actualización del protocolo de Notion (Fase 9)

**No se modificó el protocolo.** No existe conexión MCP autenticada ni
autorizada contra Notion en esta ejecución (comprobado con
`list_mcp_resources`: sin recursos); la página requiere autenticación. Texto
propuesto para cuando el autor aplique el cambio:

> **Estado del protocolo (propuesta, 2026-11-03):**
> - Pasos 1–5 completados y auditados (dictamen de cierre 30-10-2026).
> - Paso 6 cualitativo completado y auditado (auditoría correctiva 03-11-2026;
>   `qualitative/corrective-audit.md`).
> - Revisión factual externa: pendiente o recomendada (mensajes redactados,
>   **no** enviados; no condición universal de publicación).
> - Edición final e integración de las cinco figuras: pendientes.
> - Cohorte comparativa de otros backends: **diferida expresamente** a un
>   estudio posterior con subprotocolo propio.
> - Resultado científico: **estudio de caso** con alcance delimitado (35
>   repositorios medidos; 6 leídos en profundidad; sin extrapolar al ecosistema).

## Tabla de cierre (hallazgo → evidencia → corrección → verificación)

| Hallazgo | Evidencia original | Corrección | Archivos afectados | Verificación | Estado |
|---|---|---|---|---|---|
| O-01 H4/C39: conteos de coincidencia erróneos («6 de 12 aprox.», «seis de los casos/ventanas») | `hypotheses.json` H4: 12 m 18/16/**10**/6; 24 m 25/24/**18**/6 | Conteos reales + conclusión corregida mandada + planos distinguidos | `synthesis.md` §0.2/§4.2/§4.5/§4.6; `claim-ledger.csv` C13/C39; `editorial-handoff.md` §3.3/§7; `protocol.md`; `status-matrix.md` | Recontado de `hypotheses.json` (10+6=16 y 18+6=24) | **Corregido** |
| O-02 sensibilidad 24 m de H4 («los seis divergentes se mantienen») | `hypotheses.json` 24 m: `typing_extensions` coincide; `deprecated` diverge | Frase reescrita con los dos cambios de conjunto | `synthesis.md` §4.1 | Identidades verificadas una a una | **Corregido** |
| O-03 planos de H4 (publicación fuera del contraste) | Plan del Paso 5: H4 = commits vs `merged_by` vs pares de revisión | Sección «Planos» en la síntesis; ajuste en psycopg/starlette; nota editorial | `synthesis.md` §4.2; `cases/psycopg-psycopg.md` §F; `cases/kludex-starlette.md` §C; `protocol.md`; `editorial-handoff.md` §3.3 | Ninguna afirmación de cuatro roles queda atribuida a H4 | **Corregido** |
| O-04 grados de conocimiento («Permanece desconocido») | Expedientes con responsables/roles/procesos documentados (E1/E2) | Marco A/B/C/D + ausencia de evidencia / evidencia de ausencia / no observable | `limitations.md` §2.5; `synthesis.md` §0.5/§6.4; `editorial-handoff.md` §7 | Redacción que no presenta el estudio como fracaso de identificación | **Corregido** |
| O-05 sucesión vs transferencia; «5 de 6» sin soporte | Starlette = transferencia histórica 2025-09; SQLAlchemy = Gerrit documentado; ningún relevo futuro en 6/6 | Clasificación 1–5 por caso; conteo 5/6 eliminado; C49 | `evidence/index.md`; 6 casos §B/§E; `factual-review.md`; `claim-ledger.csv` C49 | Ningún caso presenta la transferencia como sucesión futura | **Corregido** |
| O-06 alcance 35 vs 6 | Plan, Aclaración 3 (selección mecánica) | Frase de alcance en introducción/síntesis/handoff; C50 | `synthesis.md` §0; `editorial-handoff.md` §3.3; `claim-ledger.csv` C50 | Sin afirmaciones de gobernanza de los 35 ni muestra representativa | **Corregido** |
| O-07 financiación «4 de 6» | `FUNDING.yml` compartido sqlalchemy/alembic; casos §D | Canales por categoría + unidad de conteo (4 unidades = 3 estructuras); C48 | `synthesis.md` §0.4/§6.1; `editorial-handoff.md` §3.2; `claim-ledger.csv` C48 | Sin porcentajes de prevalencia; remuneración no demostrada declarada | **Corregido** |
| O-08 C45 exhaustividad sin prueba | Artículo protegido sin comparación fila a fila | **Opción A**: `coverage-matrix.csv` sobre el texto íntegro (lectura autorizada 2026-11-03); C46–C52 para afirmaciones sin traza | `claim-ledger.csv` C45–C52; `coverage-matrix.csv` | 31 filas de cobertura; todo ID referenciado existe | **Corregido (cobertura demostrada)** |
| O-09 literatura (citas sin fuente verificable) | Relectura 2026-11-03: Osborne verificado; Hoffmann verificado; Census III verificado (PDF localizado); 2 citas Eghbal y las de Benkler/Lerner–Tirole no verificables | Citas verificadas conservadas; el resto a paráfrasis; tabla de recuperación real por obra | `literature.md`; `claim-ledger.csv` C42 | Sin citas textuales sin fuente | **Corregido** |
| O-10 comandos de reproducción frágiles | `cd` encadenados que rompen al cambiar de directorio | Comandos desde la raíz + `verify_readonly.sh` (solo lectura) | `qualitative/README.md`; `qualitative/verify_readonly.sh` | Script PASS en este checkout | **Corregido** |
| O-11 / H-01 manifiesto del Paso 4 (453/454) | Entrada `README.md` `8188c665…` vs archivo `81e9affe…`; causa `eaee185` | Solo esa entrada actualizada (excepción autorizada), con diff de 1 línea | `maintenance/SHA256SUMS`; `status-matrix.md`; `limitations.md` §4 | `sha256sum -c` → 454/454; 453 hashes idénticos | **Corregido** |
| Discrepancia dictamen: «los roles rara vez coinciden» | Búsqueda literal en artículo y paquete: **ausente** | Se documenta la discrepancia; se corrige el defecto real (O-01) | este documento | Búsqueda reproducible (`grep`) | **Documentado** |
| Cuatro casos squash (uvicorn, typing_extensions, starlette, redis-py) | `audits.md` §verificación 01-11-2026; C16 | Sin cambios necesarios (ya correctos); se refuerza la advertencia en §4.5/§4.6 y fig3 | `synthesis.md` (refuerzo) | Commits sin merges = PR fusionados (web-flow) | **Verificado, sin discrepancia** |
| Límites del Paso 5 heredados | `dictamen.md` §Limitaciones | Se conservan íntegros; se clasifican como límites normales, no defectos | `limitations.md` §1 | Sin cambios | **Verificado** |

## Estado editorial derivado

1. **WordPress 2735:** sin cambios (solo dos lecturas autorizadas). Quedan por
   ejecutar: sustituciones de `editorial-handoff.md` §3, integración de
   `fig1.json`…`fig5.json` y checklist §4.4.
2. **Revisión factual:** mensajes redactados y **no** enviados; recomendada,
   no condición universal de publicación (`factual-review.md`).
3. **Notion:** propuesta lista (arriba); sin conexión autenticada en esta
   ejecución.
4. **Redacción definitiva:** `editorial-handoff.md` §7 (respuesta central,
   H1–H4, límites A–D, gobernanza/financiación, puente económico, preguntas
   abiertas y conclusión).

## Trazabilidad de decisiones

- No se re-ejecutó `analyze_activity.py` ni se consultó GitHub para sustituir
  datos congelados: los recontos son solo lectura sobre artefactos versionados.
- No se reclasificó automatización no declarada; no se identificaron personas
  detrás de cuentas; no se infirieron riesgos, abandono, bus factor ni
  remuneración.
- La lectura del artículo usó la contraseña del post **facilitada por el
  autor** y se limitó a GET; ni el contenido ni la contraseña se versionan.
- Los commits de esta auditoría son atómicos y temáticos en la misma rama; no
  se fusiona con `main` ni `dev` ni se publica nada.
