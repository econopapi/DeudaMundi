# Notas editoriales y de producción (extraídas del borrador 2735)

**Propósito:** conservar, fuera del artículo público, las notas de producción
que en el borrador de WordPress (entrada 2735, leída el 2026-11-02) aparecen
mezcladas con el texto de lectores. La propuesta editorial
(`editorial-handoff.md`) las **retira del artículo** y las mantiene aquí. Las
escaletas de video se preservan igualmente.

## 1. Nota editorial de estado (bloque §001 del borrador)

> Nota editorial — borrador de trabajo, 1 de noviembre de 2026. Los pasos
> técnicos 1–5 están documentados y el análisis cuantitativo se presenta con
> los límites del protocolo. Se retiraron las visualizaciones preliminares para
> rediseñarlas; cinco avisos indican su lugar y propósito. Siguen pendientes la
> lectura cualitativa de los seis casos, la revisión factual y la edición final
> de las notas de producción. Este artículo continúa protegido mientras se
> prepara la publicación definitiva.

*Destino:* reemplazar por una nota breve solo si el artículo se publica todavía
como «libreta abierta»; en caso contrario, retirarla. Tras el Paso 6, la
lectura cualitativa **ya no** está pendiente; lo están la revisión factual y la
autorización de publicación.

## 2. Nota de producción — captura real del Paso 1 (bloque §012)

> Nota de producción — captura real: mostrar la rama y el commit de la foto, el
> manifiesto api/pyproject.toml, la versión de Python y una pequeña porción
> legible de pip-inspect.json. Ocultar rutas, tokens o datos personales si
> aparecen. Una toma hecha ahora debe rotularse como lectura posterior del
> artefacto congelado, no como grabación del día en que se creó la imagen.

## 3. Nota de producción — Paso 3 (bloque §023)

> Nota de producción — captura real: enseñar una fila de source-repos.csv junto
> con sus dos metadatos de procedencia y la URL final del repositorio. Para el
> video, un par de paquetes que comparten repo explica visualmente por qué 37
> no se convierten en 37 repositorios. Evitar mostrar la portada de un perfil
> individual como «prueba» de que esa persona sostiene el proyecto.

## 4. Nota de producción — la extracción como escena (bloque §027)

> Nota de producción — la extracción como escena: conservar una toma corta del
> verificador y del manifiesto de hashes, una vista de las carpetas de páginas y
> una ampliación de un JSON que muestre fecha, consulta y número de registros
> sin exponer credenciales. Una consulta nueva en pantalla se debe presentar
> como demostración posterior, porque GitHub puede haber cambiado desde la
> extracción del 30 de octubre. Una animación puede visualizar «35 repositorios
> → cuatro corrientes → dos ventanas», pero los números deben venir de la tabla
> versionada.

## 5. Nota de producción — gráfico y terminal, Paso 2 (final del bloque §019)

> Nota de producción — gráfico y terminal: animar una sola ruta comprobada
> «DeudaMundi → dependencia directa → dependencia transitiva» y luego revelar
> una segunda ruta hacia el mismo paquete. Contrastar esa animación conceptual
> con una captura real de nodes.csv, edges.csv y el diagrama Mermaid. No inventar
> flechas para hacer más vistosa la escena.

## 6. Escaletas de video (sección «Del texto maestro al video largo…», §069–§073)

- **Video largo (§071):** «Escaleta: abrir con DeudaMundi funcionando; revelar
  la foto, una ruta del grafo, la atribución de repositorio y la escala de la
  extracción. Combinar las capturas reales señaladas en cada paso con una
  animación conceptual rotulada. Reservar los casos humanos y la interpretación
  económica para después del análisis y la revisión factual.»
- **Shorts (§073):** «Escaleta: posibles piezas sobre dependencia directa frente
  a transitiva, sobre por qué un commit no basta para identificar a un
  mantenedor y, si los resultados lo permiten, sobre el costo invisible de
  mantener software reutilizado. Elegir y escribir los guiones después de
  estabilizar el artículo.»
- Tras el Paso 6: la lectura cualitativa existe y puede alimentar los casos
  humanos; **la revisión factual sigue siendo requisito previo** para nombrar
  actores en video.

## 7. Nota editorial final (bloque §074)

> Nota editorial final — material por reunir: capturas de la API en
> funcionamiento, manifiesto e inventario congelado, una ruta real del grafo,
> un ejemplo de dos paquetes en un repositorio, verificación del conjunto de
> datos y una fila de la tabla descriptiva. Guardar para cada toma el
> archivo/commit fuente, fecha, afirmación que respalda y si es evidencia
> original, lectura posterior o ilustración conceptual. La portada de este
> borrador es una metáfora visual; el diagrama de cuatro pasos sí usa conteos
> versionados.

## 8. Reglas de producción permanentes (de `../editorial-evidence.md`)

- Toda captura actual se rotula como **lectura posterior** del artefacto
  congelado.
- Las ilustraciones se rotulan como **representación conceptual**.
- Los números siempre proceden de tablas versionadas, no de pantallas.
- No usar capturas de perfiles individuales como prueba de responsabilidad.
