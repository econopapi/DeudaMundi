# Paso 4 — bitácora para artículo y tomas de video

Este documento registra cómo mostrar el procedimiento después de la recolección. Es una guía de evidencia, no un guion ni una interpretación de quién mantiene cada proyecto.

## Decisiones que deben quedar visibles

1. **Universo fijado:** `source-repos.csv` del paso 3 vincula 37 distribuciones de ejecución con 35 repositorios únicos. Los dos repositorios compartidos se consultan una sola vez. No mezclar este universo con la futura cohorte de otros backends Python.
2. **Ventanas fijadas antes de los conteos:** corte UTC exclusivo de 2026-10-30; periodos de 12 y 24 meses en `protocol.md`.
3. **Unidad de observación:** evento público de GitHub, con commits, PR fusionados, revisiones y releases en columnas distintas. Un actor observado en un evento no se convierte automáticamente en «mantenedor».
4. **Ajuste operativo documentado:** el primer sondeo de FastAPI mostró 100 PR actualizados en diez días. El protocolo conserva REST para commits/releases y utiliza GraphQL para obtener PR con sus revisiones en lotes de 100. El piloto de cuatro repositorios midió el costo antes de recorrer los 35.
5. **Límites:** actividad fuera de GitHub, trabajo no publicado, identidades no vinculadas y automatización no declarada no se pueden reconstruir con esta extracción. Los tags sin release de GitHub no son releases en esta métrica.

## Toma de terminal reproducible, sin grabar toda la extracción

Desde la raíz del repositorio, en la rama `research/deudamundi-dependencies`:

```sh
git log --oneline --max-count=5
sha256sum research/dependencies/attributions/source-repos.csv
sed -n '1,90p' research/dependencies/maintenance/protocol.md
python research/dependencies/maintenance/verify_activity.py
sha256sum -c research/dependencies/maintenance/SHA256SUMS
```

Para mostrar una página de evidencia sin exponer el token de GitHub ni el cuerpo de un PR, usar un extracto local:

```sh
python -c 'import json; p="research/dependencies/maintenance/data/fastapi__fastapi/prs/00001.json"; d=json.load(open(p)); print({"consulta":d["request"]["url"],"fecha_utc":d["request"]["consulted_at_utc"],"registros":d["response_records"],"sha256_respuesta":d["request"]["body_sha256"]})'
```

La consulta en vivo, si se quiere grabar, puede reproducirse en un directorio temporal con `--repo sqlalchemy/mako --output /tmp/deudamundi-maintenance-demo`. Requiere `gh` autenticado y acceso a GitHub; el video debe identificar que es una nueva consulta, no la evidencia fechada de la extracción original.

## Material para el blog y el video largo

- Captura real: commit del protocolo previo, hash de `source-repos.csv`, comando de verificación y manifiesto de hashes.
- Diagrama conceptual: 37 paquetes → 35 repositorios → cuatro corrientes de eventos → dos ventanas temporales. Etiquetar los dos repositorios compartidos sin duplicar su actividad.
- Hacer de la operación de datos un segmento metodológico: mostrar el contador final de páginas, archivos y bytes del directorio de evidencia, seguido de una ampliación de una sola página. Explicar que el volumen procede de paginar la actividad pública de 35 repositorios y que cada página tiene fecha y hash de la respuesta. Dar los números finales solo después del verificador; distinguir bytes reales de tamaño en disco.
- Mostrar la corrección de calidad como escena breve: la primera regla detenía releases al ver una página antigua llena; la auditoría exigió agotar el endpoint y añadió tres páginas. No alteró los conteos de las ventanas. Es una demostración concreta de por qué «cobertura 35/35» necesita controles de evento además del contador de repositorios.
- Transición visual propuesta para el video: terminal de extracción breve → mosaico de páginas normalizadas → indicador de cobertura 35/35 → una fila verificable. El montaje puede combinar capturas reales con ilustraciones; las ilustraciones deben rotularse como representación conceptual.
- Captura de una fila de `coverage-descriptive.csv`, mostrando columnas y denominadores sin concluir sobre personas.
- Nota editorial: explicar por qué un censo de este caso describe DeudaMundi y no permite estimar automáticamente todo el ecosistema Python. La cohorte de otros backends es un estudio complementario.
- Conservar enlaces a los commits de cada paso y a la página del protocolo en Notion como material de referencia. No usar capturas de perfiles individuales como prueba de responsabilidad formal.

## Registro de ejecución

- **Rama:** `research/deudamundi-dependencies`; el hash del commit de publicación se obtiene con `git log` y se enlaza desde Notion (un archivo no puede contener el hash de su propio commit).
- **Fecha de las respuestas preservadas:** `2026-10-30T15:50:42Z` a `2026-10-30T16:15:14Z`, incluida la auditoría posterior de paginación de releases.
- **Escala final:** 35/35 repositorios; 407 solicitudes efectivas; 144 páginas de commits, 183 de PR, 45 de releases, 35 de metadatos; 443 archivos JSON normalizados; 12,584,931 bytes de contenido. `du -sh` puede mostrar otra cifra por bloques del sistema de archivos.
- **Comprobación:** `verify_activity.py` pasó para cuatro tipos y dos ventanas. La repetición del colector sobre los datos completos fue byte idéntica y no requirió red. La prueba negativa retiró una página en una copia temporal y produjo `Page gap` con exit 1.
- **Fallo o reanudación:** no hubo fallos en la corrida completa. El piloto previo cubrió cuatro repositorios y la corrida completa reutilizó esas páginas. La auditoría añadió tres páginas finales de releases porque detenerse ante una página antigua llena no demostraba agotamiento; contenían cero eventos dentro de las ventanas y los totales quedaron iguales.
- **Cambio de método:** GraphQL agrupó PR y revisiones después del sondeo de volumen de FastAPI; quedó registrado en `protocol.md` antes de la extracción de eventos.
- **Manifiesto:** `SHA256SUMS` cubre el conjunto publicado; consultar el commit de cierre en el historial de la rama.
