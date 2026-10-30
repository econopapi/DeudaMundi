# Paso 4: actividad pública observable en los repositorios atribuidos

**Estado:** extracción descriptiva completada para los 35 repositorios únicos vinculados a las 37 dependencias de ejecución de la foto de DeudaMundi. No identifica por sí sola a las personas mantenedoras ni mide riesgo, esfuerzo, remuneración o responsabilidad formal. La rama de investigación sigue separada de `main` y `dev`.

## Procedencia y alcance

- Universo: `../attributions/source-repos.csv` del paso 3, commit `c129e4edd21db956ba6cb68f918d104d5aeac9cc`, SHA-256 `f1d2884a5907652236848be559f168a535eb898e4ef2db14e57e352472fea12c`. Dos repositorios compartidos se cuentan una vez cada uno.
- Corte exclusivo UTC: `2026-10-30T00:00:00Z`. Ventana principal: 12 meses desde `2025-10-30T00:00:00Z`; sensibilidad: 24 meses desde `2024-10-30T00:00:00Z`. Los eventos del día de consulta quedan fuera.
- Definiciones y ajuste del método: [`protocol.md`](protocol.md). REST con API version `2026-03-10` para repositorios, commits y releases; GraphQL para PR y revisiones en páginas de hasta 100. No se truncó el volumen de FastAPI.
- Extracción y auditoría de paginación: 407 solicitudes efectivas, 144 páginas de commits, 183 de PR, 45 de releases y 35 de metadatos. Ningún PR necesitó páginas extra de revisiones. Primera respuesta archivada: `2026-10-30T15:50:42Z`; última: `2026-10-30T16:15:14Z`. Tres páginas finales de releases se añadieron en la auditoría sin cambiar los conteos de las ventanas.
- Preservación: `data/` contiene 443 JSON normalizados, **12,584,931 bytes de contenido**. Cada página conserva URL o variables de consulta, instante UTC, código HTTP, conteo de registros, hash SHA-256 del cuerpo recibido y, si aplica, costo GraphQL. No se archivaron cuerpos completos de PR ni correos de commit. El hash del cuerpo sirve como recibo de la consulta; sin el cuerpo original no permite reconstruirlo ni verificarlo de forma independiente.

## Resultados descriptivos de cobertura

`coverage-descriptive.csv` contiene una fila por repositorio y columnas separadas por tipo de evento, periodo, bot y actor no atribuible. El verificador confirmó 35/35 repositorios y paginación completa de los cuatro tipos. Totales de eventos, **sin sumar los tipos entre sí**:

| Ventana | Commits de rama principal | PR fusionados | Revisiones | Releases de GitHub |
| --- | ---: | ---: | ---: | ---: |
| 12 meses | 7,014 | 3,981 | 10,543 | 356 |
| 24 meses | 12,593 | 6,545 | 18,025 | 594 |

Estas cifras son eventos públicos bajo las reglas fijadas, no personas únicas ni una muestra aleatoria del ecosistema Python. La cobertura completa permite describir **este caso congelado**; la extrapolación a otros backends requiere la cohorte complementaria prevista en el protocolo general. Cuatro repositorios tienen cero releases de GitHub en la ventana de 24 meses, lo que no prueba ausencia de versiones publicadas por otros mecanismos.

## Reproducción y verificación

Desde la raíz del repositorio:

```sh
python research/dependencies/maintenance/verify_activity.py
cd research/dependencies/maintenance
sha256sum -c SHA256SUMS
```

Para volver a consultar GitHub, se requiere Python 3.12+, `gh` autenticado y acceso a la API. El colector verifica primero el hash del CSV de atribuciones. En una copia limpia, ejecutar desde la raíz:

```sh
python research/dependencies/maintenance/collect_activity.py --pilot
python research/dependencies/maintenance/collect_activity.py
```

Los directorios `data/<owner>__<repo>/` guardan páginas numeradas. Una ejecución interrumpida conserva páginas completas y retoma desde la última página guardada. Los repositorios ya completos se saltan sin red; la repetición sobre esta evidencia dejó todos los JSON byte idénticos. Una nueva consulta en otra fecha podría diferir por cambios en GitHub y **no** debe sobrescribir la foto publicada sin versionar una nueva extracción.

## Verificación ejecutada

- Verificador independiente: 35/35 repositorios, cuatro corrientes, dos ventanas, sin IDs duplicados ni páginas faltantes; releases paginados hasta una página con menos de 100 registros; `coverage-descriptive.csv` byte idéntico en dos corridas.
- Repetición del colector sobre la foto completa, sin token ni red: exit 0; tras la auditoría, el hash agregado de `data/` es `45536bba7e4ea330a6c409b38478c26af6536b34742c2204128702894bf95d94`.
- Prueba negativa en copia temporal: retirar `fastapi__fastapi/prs/00002.json` produjo exit 1 con `Page gap`; los originales quedaron intactos.
- `SHA256SUMS` cubre los archivos publicados de este directorio y la tabla fuente del paso 3. Su comprobación se ejecuta desde este directorio.

## Límites que acompañan cualquier publicación

GitHub presenta un estado actual, no una foto histórica perfecta al corte: `updatedAt`, rama principal y atribuciones de cuentas pueden cambiar mientras se pagina. El colector filtra por fecha de cada evento y detecta IDs duplicados, pero no puede demostrar que nunca hubo un movimiento de PR entre páginas durante la consulta. Las revisiones se descubren a través de PR actualizados en la ventana; si GitHub no actualizara `updatedAt` por una revisión, podría faltar. Los commits se recorren desde la rama principal observada al consultar, no desde una referencia histórica inmutable del día de corte. Releases de GitHub excluyen tags sin objeto release. La clasificación de bots usa el tipo de cuenta o el sufijo `[bot]` y puede omitir automatizaciones no declaradas.

No hay análisis de concentración, HHI, «bus factor», calidad de revisión, riesgo o quién mantiene cada repositorio en este paso. El material de demostración para el blog y el video está en [`editorial-evidence.md`](editorial-evidence.md).

La [auditoría de aptitud analítica](quality-audit.md) mapea las preguntas del protocolo a los datos disponibles y registra los controles pendientes antes de sacar conclusiones.

**Paso 5 (30 de octubre de 2026):** el análisis descriptivo vive en [`analysis/`](analysis/), con el plan preregistrado (`analysis/plan.md`), los contrastes H1–H4 con sensibilidad 12/24 meses, evidencia PyPI para H3, auditoría manual de 24 repositorios con segunda implementación independiente, bitácora en `analysis/audits.md`, cinco figuras interactivas con identidad visual Econopapi (`analysis/figures/`) y su integración verificada como borrador en WordPress (sin publicar) a través de `analysis/wp-snippets/`. Verificación reproducible y hashes en `analysis/verification.txt` y `analysis/SHA256SUMS`.
