# Paso 6 — investigación cualitativa y preparación del cierre científico

**Estado:** completado y auditado (auditoría correctiva de cierre,
2026-11-03, ver `corrective-audit.md`) con reservas editoriales (ver
`status-matrix.md`). Rama `research/deudamundi-dependencies`. Trabajo original
del 2 de noviembre de 2026 sobre el HEAD `761a947` (commit de referencia del
encargo) **sin tocar** ningún artefacto congelado de los Pasos 1–5; la única
excepción autorizada —la entrada de `README.md` en `maintenance/SHA256SUMS`,
hallazgo H-01— quedó corregida y documentada el 2026-11-03.

Este directorio responde a la pregunta del estudio —**¿qué puede saberse sobre
quién realiza, coordina y publica el mantenimiento de las dependencias Python
de DeudaMundi, y hasta dónde alcanza la evidencia?**— con la lectura cualitativa
de los seis casos fijados mecánicamente en el Paso 5, la triangulación de
H1–H4, el marco económico y la preparación editorial. **No** es una nueva
investigación cuantitativa: no recalcula hipótesis, no cambia ventanas,
umbrales, unidades, evaluabilidad ni reglas de bots.

## Navegación

| Archivo | Contenido | Fase del encargo |
|---|---|---|
| [`protocol.md`](protocol.md) | Protocolo de lectura, categorías (C1–C8) y niveles de evidencia (E1–E4). **Posterior al análisis cuantitativo; no es preregistro original** | Fase 1 |
| [`status-matrix.md`](status-matrix.md) | Control de integridad (Fase 0), hallazgo H-01 y matriz completado/pendiente/decisión editorial | Fase 0 |
| [`cases/`](cases/) | Seis expedientes A–G | Fase 2 |
| [`synthesis.md`](synthesis.md) | Triangulación de H1–H4 (permitido / no permitido / contexto / contraejemplo / redacción) y síntesis por niveles de evidencia | Fases 3 y 5 |
| [`literature.md`](literature.md) | Marco económico y bibliografía crítica (Census III, Eghbal, Osborne, Benkler, Lerner–Tirole, Hoffmann–Nagle–Zhou) | Fase 4 |
| [`claim-ledger.csv`](claim-ledger.csv) | Registro trazable de afirmaciones (52 entradas) con nivel de evidencia, fuente y destino editorial | Fase 5 |
| [`coverage-matrix.csv`](coverage-matrix.csv) | Matriz de cobertura artículo 2735 ↔ registro de afirmaciones (Opción A, Fase 6) | Fase 6 |
| [`corrective-audit.md`](corrective-audit.md) | Auditoría correctiva de cierre: hallazgos, correcciones y verificación | Fase 10 |
| [`editorial-handoff.md`](editorial-handoff.md) | Propuesta de edición para la entrada 2735, especificación de figuras y ruta de publicación | Fase 6 |
| [`editorial-production-notes.md`](editorial-production-notes.md) | Notas de producción y escaletas retiradas del artículo (conservadas aquí) | Fase 6 |
| [`factual-review.md`](factual-review.md) | Afirmaciones sensibles y mensajes propuestos de revisión factual (**sin enviar**) | Fase 7 |
| [`limitations.md`](limitations.md) | Límites de alcance, evidencia e inferencia | Fase 8 |
| [`deferred-comparative-cohort.md`](deferred-comparative-cohort.md) | Recomendación de diferir la cohorte de otros backends | Decisión de alcance |
| [`evidence/`](evidence/index.md) | Índice de fuentes y procedencia (+ anexos crudos en `evidence/raw/`) | Todas |
| `SHA256SUMS` / `verification.txt` / `verify_readonly.sh` | Integridad de **este** directorio y verificación de solo lectura desde la raíz | Fase 8 |

## Casos (selección mecánica del Paso 5, sin sustituir)

1. [`cases/sqlalchemy-sqlalchemy.md`](cases/sqlalchemy-sqlalchemy.md)
2. [`cases/sqlalchemy-alembic.md`](cases/sqlalchemy-alembic.md)
3. [`cases/python-typing_extensions.md`](cases/python-typing_extensions.md)
4. [`cases/kjd-idna.md`](cases/kjd-idna.md)
5. [`cases/psycopg-psycopg.md`](cases/psycopg-psycopg.md)
6. [`cases/kludex-starlette.md`](cases/kludex-starlette.md) (redirección
   `encode/starlette` → `Kludex/starlette` documentada)

## Reproducción y verificación (checkout limpio)

Todos los comandos se ejecutan **desde la raíz del repositorio** (rutas
explícitas; no hay encadenamientos de `cd`):

```sh
# Verificación completa de solo lectura (recomendada): manifiestos de los
# Pasos 4, 5 y 6, cinco manifiestos Plotly, claim-ledger y coverage-matrix
# (integridad referencial: CSV válido, IDs existentes), referencias internas
# y datos congelados intactos. Los fallos se diagnostican paso a paso.
sh research/dependencies/maintenance/qualitative/verify_readonly.sh

# Comprobaciones individuales equivalentes:
python research/dependencies/maintenance/verify_activity.py                  # PASS 35/35
( cd research/dependencies/maintenance && sha256sum -c SHA256SUMS )          # 454/454 (H-01 corregido 2026-11-03)
( cd research/dependencies/maintenance/analysis && sha256sum -c SHA256SUMS ) # todos OK
( cd research/dependencies/maintenance/qualitative && sha256sum -c SHA256SUMS )
python3 -c "import csv; r=list(csv.DictReader(open('research/dependencies/maintenance/qualitative/claim-ledger.csv'))); print(len(r),'afirmaciones,',len(r[0]),'columnas')"
```

- **Sin rutas absolutas ni credenciales:** todo el paquete usa rutas relativas
  al repositorio; la lectura del artículo 2735 requirió la contraseña del post
  **facilitada por el autor** y su contenido **no** se versiona aquí.
- **Alcance de la validación automática:** `verify_readonly.sh` certifica
  integridad de hashes, validez de CSV, integridad referencial de los IDs y
  enlaces internos. **No** demuestra cobertura semántica exhaustiva del
  artículo: esa cobertura (`coverage-matrix.csv`) es una **revisión manual
  documentada**, con su alcance declarado en `claim-ledger.csv` C45.
- **Fuentes web:** consultadas el 2026-11-02 (posteriores al corte
  `2026-10-30T00:00:00Z`); cada una lleva URL, fecha y, cuando aplica, commit
  fijado. No representan necesariamente el estado del corte.
- **No se re-ejecutó** el análisis del Paso 5 para no tocar derivados
  congelados; su reproducción byte-idéntica ya está auditada en
  `../analysis/final-audits/dictamen.md`.

## Reglas que este paso no rompe (resumen)

1. Los 443 JSON, inventario, grafo, atribuciones y resultados cuantitativos:
   intactos (verificado en `verification.txt`).
2. H1–H4 no se recalculan; sus valores de referencia se citan literalmente.
3. Cuentas ≠ personas; sin causalidad, riesgo, abandono, bus factor ni
   remuneración; sin reclasificar automatización; sin mezclar post-corte con
   ventanas.
4. Sin cambios en WordPress, sin publicar, sin contactar mantenedores.
5. Toda afirmación del artículo pasa por `claim-ledger.csv`; las sensibles,
   por `factual-review.md`.
