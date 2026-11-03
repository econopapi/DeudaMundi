# Handoff editorial — propuesta de edición para WordPress 2735 y especificación de figuras

**Paso 6 · 2 de noviembre de 2026. NO SE HA REALIZADO NINGÚN CAMBIO EN
WORDPRESS.** Este documento entrega (1) una propuesta de edición del artículo,
(2) la especificación de integración de las cinco figuras v2, (3) las pruebas
que debe ejecutar el agente responsable del tema y (4) la ruta de publicación
con sus bloqueos.

## 1. Estado de la entrada 2735 (lectura autorizada 2026-11-02)

- **Mecanismo:** API REST `wp-json/wp/v2/posts/2735` con la contraseña del post
  facilitada por el autor. Solo lectura.
- **Metadatos:** `status: publish`, `protected: true`, `modified:
  2026-11-01T06:40:31`, 22 revisiones, categoría «Uncategorized», portada
  `deudamundi-dependencias-portada.jpg`, tema Astra.
- **Estructura interna:** 74 bloques (1 nota editorial, 23 secciones
  H2/H3, 40 párrafos, 2 figuras fijas existentes con sus `figcaption`, 5 avisos
  «Gráfico pendiente», 4 notas de producción, 2 escaletas de video, 1 nota
  final).
- **Los cinco marcadores pendientes** (sustituir por bloques
  `econopapi/plotly-figure`):

| Marcador en el artículo (bloque) | Texto actual | Figura v2 |
|---|---|---|
| §031 | «Gráfico pendiente — Figura 1: Escala de la actividad pública observada…» | `fig1.json` |
| §033 | «Gráfico pendiente — Figura 2: Actividad de commits por repositorio…» | `fig2.json` |
| §044 | «Gráfico pendiente — Figura 3: ¿Se concentra más la autoría de commits que la de PR?…» | `fig3.json` |
| §047 | «Gráfico pendiente — Figura 4: Sensibilidad de la concentración entre 12 y 24 meses…» | `fig4.json` |
| §039 | «Gráfico pendiente — Figura 5: Participación de automatización declarada por tipo de evento…» | `fig5.json` |

## 2. Correspondencia sección–afirmación–figura

| Sección (bloques) | Contenido | Claims | Figura |
|---|---|---|---|
| Introducción §002–§006 | Pregunta y escalas | C01–C04, C50 | — |
| Pasos 1–4 §009–§027 | Método verificable | C01–C05 | figuras fijas existentes (grafo) |
| «Qué podemos afirmar ya» §029–§033 | Universo y totales | C06, C02 | **fig1, fig2** |
| Roles §036–§039 | Flujos y bots | C14, C15 | **fig5** |
| Concentración §041–§044 | H1–H2 | C07, C09, C10, C16 | **fig3** |
| Sensibilidad §046–§047 | 24 meses | C08 | **fig4** |
| H3 §049 | PyPI sin releases | C11, C12, C30 | — |
| H4 §051 | Divergencia de roles | C13, C17, C18, C39 | — |
| Gobernanza §053 | **Cualitativa (ver §3.2)** | C19–C38, C48, C49 | — |
| Cohorte §055–§056 | Pregunta diferida | C43 | — |
| Límites §058–§059 | Qué no mide | C40 + C8 | — |
| Economía §060–§061 | Puente conceptual | C41, C42 | — |
| Auditoría §063–§065 | Reproducción y lecturas | C05, C41, C42 | — |
| Conclusión §067–§068 | Cierre | síntesis | — |

## 3. Cambios propuestos

### 3.1 Notas de producción → fuera del artículo

Retirar del artículo los bloques §001 (nota editorial de estado), §012, §023,
§027 (notas de captura), §069–§073 (sección de video/shorts) y §074 (nota
final). **Ya están conservadas** en
[`editorial-production-notes.md`](editorial-production-notes.md) con su texto
íntegro. Sustituir §001 por una nota mínima para lectores:

> *Esta investigación es un estudio de caso único: describe una instalación
> concreta de DeudaMundi con datos congelados al 30 de octubre de 2026. No es
> una estimación del ecosistema Python.*

### 3.2 Sustitución del bloque §053 («Gobernanza, patrocinio y el trabajo que GitHub no enseña»)

Retirar el texto «Lectura cualitativa pendiente…» (ya no lo está) e insertar,
con selección —no seis fichas enciclopédicas—:

> **Gobernanza, patrocinio y el trabajo que GitHub no enseña**
>
> Las métricas anteriores cuentan eventos; para saber quién coordina y publica
> hay que leer la documentación de los proyectos. Revisamos en profundidad seis
> casos elegidos por regla mecánica antes de ver sus métricas. El resultado no
> es un retrato de personas —las cuentas de GitHub no son personas— sino un
> mapa de cómo se organiza el mantenimiento.
>
> Los seis proyectos documentan **procesos**: SQLAlchemy integra cambios por
> una instancia propia de revisión y firma sus releases; typing_extensions
> exige el acuerdo de contribución de la Python Software Foundation y publica
> con candidaturas y aprobación manual; idna publica automáticamente releases
> firmados con Sigstore; psycopg documenta paso a paso cómo publica en PyPI sin
> crear releases de GitHub — el mismo patrón que medimos en H3. Donde la
> actividad parecía «ausente» aparecen, pues, procedimientos escritos.
>
> También hay **modelos organizativos distintos**: una organización fundacional
> (typing_extensions, bajo la org `python`), organizaciones de proyecto con
> roles nombrados (SQLAlchemy declara públicamente dos mantenedores para todos
> sus proyectos; psycopg nombra un responsable técnico y otro de operaciones,
> cuyas funciones incluyen triage y coordinación: trabajo que ningún commit
> registra), una cuenta individual con procesos automatizados (idna) y un
> proyecto cuya administración se transfirió de una organización a una cuenta
> personal en 2025 (starlette, antes `encode/starlette`; una transferencia
> histórica documentada, no un procedimiento de sucesión futura), con la
> licencia conservando al titular histórico. La atribución de un paquete a un
> repositorio, por tanto, **no es estable en el tiempo**: hay que fecharla.
>
> Sobre **financiación**, solo cabe decir lo que los proyectos declaran. Los
> canales documentados: para el conjunto SQLAlchemy/Alembic, patrocinio de
> organización (GitHub Sponsors), Patreon y una suscripción de Tidelift —una
> sola estructura que cubre dos de los seis casos estudiados—; para psycopg, un
> programa de patrocinio del proyecto con tiers corporativos y patrocinio de la
> cuenta del responsable técnico; para starlette, patrocinio de la cuenta
> titular. Cuatro de las seis unidades de caso declaran algún canal, pero son
> solo tres estructuras distintas: ese «cuatro de seis» no es una tasa de
> financiación entre organizaciones independientes. En idna solo consta una
> afiliación declarada de la cuenta (no una financiación) y en typing_extensions
> no se localizó declaración alguna. Que no haya declaración pública no
> significa que no haya recursos; y donde la hay, no sabemos cuánto ni a qué
> dedicación corresponden —la remuneración efectiva no está demostrada en
> ningún caso.
>
> Una advertencia que el Paso 5 ya dejó escrita: parte de la revisión y de la
> publicación observable pertenece a **automatización no declarada** como bot
> (la cuenta `sqla-tester` de los proyectos SQLAlchemy; un patrón compatible
> con un agente automatizado en otro repositorio). Las cifras identifican
> cuentas y eventos; estas páginas identifican procesos. La pregunta por las
> personas —quién decide, quién responde, quién puede dejar de estar— sigue
> exigiendo otra clase de pruebas, empezando por preguntarles.

### 3.3 Refuerzos puntuales (párrafos existentes que se conservan con adiciones)

- **§042–§043 (H2):** añadir tras el ejemplo de wrapt: *«Advertencia
  verificada: en cuatro repositorios (uvicorn, typing_extensions, starlette,
  redis-py) cada PR fusionado materializa exactamente un commit vía squash,
  por lo que ambas cuotas cuentan el mismo trabajo dos veces y su coincidencia
  no es confirmación independiente.»* (claim C16). Aclarar también el
  constructo: *«H2 compara la autoría de commits con la autoría de PR
  fusionados; no dice quién integra los cambios —eso se observa en H4, con la
  cuenta que fusiona—.»* (C09).
- **§051 (H4):** añadir: *«En SQLAlchemy el contraste se apoya en el rol de
  integración porque la cuenta que encabeza la revisión es la del pipeline de
  CI del proyecto (sqla-tester), no una persona revisando.»* (C17). Añadir
  además, para equilibrar el matiz: *«En otros repositorios la autoría, la
  integración y la revisión sí tienen la misma cuenta principal: en 10 de los
  16 repositorios con los tres roles evaluables (12 meses). La distribución
  depende de la actividad observada, y esa coincidencia no demuestra por sí
  sola responsabilidad formal ni mantenimiento unipersonal.»* (C39). H4
  contrasta tres planos (autoría, integración, revisión): **no** incorpora la
  publicación de versiones; cualquier frase sobre «quién publica» se apoya en
  la documentación y en `repo-metrics.csv`, no en H4.
- **§002–§006 (introducción):** añadir una frase de alcance: *«Este artículo
  describe una instalación concreta: 35 repositorios medidos en sus eventos
  públicos y seis de ellos leídos en profundidad, elegidos por una regla fija
  antes de ver sus métricas.»* (C50). La separación 35 (cuantitativo) / 6
  (cualitativo) debe resultar inequívoca desde la introducción.
- **§055–§056 (cohorte):** añadir la frase de cierre: *«Esta comparación queda
  formalmente diferida a un estudio posterior con su propio protocolo y
  denominador; no forma parte de estos resultados.»* (C43).
- **§058–§059 (límites):** añadir el trabajo no observable (C8): *«Tampoco
  vemos el soporte, la coordinación privada, la respuesta a incidentes no
  públicos ni el triage que no deja registro: los propios proyectos lo nombran
  como parte del mantenimiento.»*
- **§060–§061 (economía):** el puente se conserva y se cierra con la
  distinción que aporta la literatura (Eghbal; Hoffmann et al.): reproducir es
  casi gratuito, reponer tiene precio de mercado, pero **mantener** es un costo
  persistente que ninguna de esas dos magnitudes captura — y que este estudio
  describe en sus huellas, sin valorarlo económicamente (C41).
- **§065 (lecturas):** sustituir «quedan en la agenda» por la ficha ya
  incorporada de cada obra (C41–C42), con enlaces a
  `qualitative/literature.md` en el repositorio.
- **§067–§068 (conclusión):** añadir: *«La lectura cualitativa completó el
  mapa: procesos documentados en los seis proyectos, modelos organizativos
  distintos y financiación declarada solo donde existe declaración. La
  frontera final no es de datos sino de método: decidir quién mantiene algo
  exige evidencia documental y, cuando se nombra a alguien, la oportunidad de
  corregir los hechos.»*

### 3.4 Lo que NO se cambia

Ninguna cifra congelada ni denominador (7,014 / 3,981 / 10,543 / 356; cuotas
H1–H4; porcentajes de bots con su distinción crudos/pares). Ninguna definición
de ventana, umbral o evaluabilidad. La advertencia «las cuentas no son
personas» se conserva en §037.

## 4. Especificación de integración de figuras v2

### 4.1 Fuente canónica

Subir **`analysis/results/plotly-embed/fig1.json` … `fig5.json`** (un archivo
por bloque `econopapi/plotly-figure`, campo «Fuente de la figura»). No subir el
HTML autocontenido ni `index.json` (este solo cataloga y fija hashes,
verificados 5/5 el 2026-11-02). **No usar** los `post-2735-fig*.json`
(archivo histórico).

### 4.2 Contrato de metadatos del visor — estado y propuesta

Los manifiestos `schemaVersion: 1` incluyen `meta` con: `title`, `kicker`,
`description`, `alt`, `unit`, `sources[]`, `methodology`, `analysis`
(repositorio, ruta, commit), `generatedAt`, `note`, más `figure`, `config` y
`table` (caption + columnas). **Falta una guía explícita de interpretación.**
Propuesta (metadato editorial; **no** modifica resultados):

- Añadir al esquema del visor un campo **`meta.howtoread`** (nombre normalizado
  sugerido; si el componente adopta otro, actualizar esta sección): array de
  2–4 frases imperativas de lectura.
- Validación de esquema exigible: `schemaVersion`, `meta.{title, alt, unit,
  sources, methodology, analysis.commit}`, `table.caption` presentes;
  `meta.howtoread` presente (obligatorio tras la adopción); coherencia de
  `meta.analysis.commit` con el commit real del exportador.

### 4.3 Textos `howtoread` propuestos por figura

- **fig1 (escala de la actividad):** «Cada barra es un tipo de evento distinto;
  las columnas comparan 12 y 24 meses. No sumes barras: commits, PR,
  revisiones y releases son unidades diferentes. Los segmentos separan cuentas
  sin marca de bot, bots declarados y eventos sin cuenta vinculada.»
- **fig2 (commits por repositorio):** «Ranking recortado a los 15 repositorios
  con más commits no automatizados en 12 meses; usa el conmutador 12/24. El
  orden describe volumen de eventos, no calidad ni riesgo: un repositorio con
  pocos commits puede ser perfectamente mantenible.»
- **fig3 (Δ de concentración):** «Cada barra es la diferencia en puntos
  porcentuales entre la cuota de la cuenta principal por commits y por PR.
  Derecha: más concentración en commits; izquierda: más en PR; cerca de cero:
  similar. Los rombos marcan los cuatro casos donde ambas cuotas cuentan el
  mismo trabajo (fusión squash): ahí la diferencia cero no es confirmación.»
- **fig4 (sensibilidad 12/24):** «Cada repositorio muestra su cuota en 12
  (círculo) y 24 meses (cuadrado); las líneas punteadas marcan los umbrales
  50 % y 75 %. Las ventanas se solapan: las diferencias no son tendencias. Sin
  punto en 12 m: actividad insuficiente para esa ventana, no ausencia de
  mantenimiento.»
- **fig5 (automatización declarada):** «Cada barra suma el 100 % de su propio
  flujo y ventana; no compares alturas entre barras. «Revisiones crudas» y
  «pares únicos revisor–PR» son unidades distintas y se muestran separadas a
  propósito.»

### 4.4 Pruebas obligatorias del agente del tema (checklist)

1. Render en **escritorio y móvil (390 px)** de los cinco bloques.
2. **Tema claro y oscuro** (incluido el repintado al cambiar de tema).
3. **Accesibilidad:** `meta.alt` como texto alternativo real; tabla de datos
   asociada y navegable por teclado; contraste AA en ambos temas.
4. **Tablas alternativas:** los cinco `table` visibles/expandibles sin JS.
5. **Cero errores JavaScript** en consola; funcionamiento con CDN caído
   (fallback a tabla).
6. **Fidelidad:** cada cifra y etiqueta del gráfico coincide con
   `meta.note`/`table` y con las cifras del artículo (ver §2); denominadores
   visibles.
7. Los conmutadores 12/24 (fig2, fig3, fig4) funcionan con clic real en móvil.
8. Los archivos `post-2735-fig*.json` **no** se reutilizan.

## 5. Ruta de publicación verificable

1. Revisión factual (opcional pero recomendada para §053 y el caso starlette):
   mensajes en `factual-review.md`; plazo 7–14 días; sin respuesta → redacción
   atenuada ya preparada.
2. Aplicar §3 (sustituciones) en la entrada 2735; retirar notas a
   `editorial-production-notes.md`.
3. Instalar/verificar el bloque `econopapi/plotly-figure` (el plugin fue
   retirado de la rama por decisión del autor; su historia queda en Git) y
   subir `fig1.json`…`fig5.json`.
4. Ejecutar el checklist §4.4 en staging (la entrada sigue protegida).
5. El **autor** decide retirar la protección y publicar (fecha, categorías,
   portada); este paso queda fuera de la agencia técnica.

## 6. Bloqueos restantes (lista explícita)

| # | Bloqueo | Quién lo resuelve |
|---|---|---|
| 1 | Autorización de publicación y desbloqueo de la entrada | Autor |
| 2 | Envío y gestión de la revisión factual | Autor (mensajes ya redactados) |
| 3 | Integración física de figuras y pruebas de tema | Agente del tema / autor |
| 4 | Instalación del plugin de bloque en producción | Autor (requiere acceso al sitio) |
| 5 | ~~Decisión sobre H-01 (hash de `README.md` en el manifiesto del Paso 4)~~ | **Resuelto en la auditoría correctiva 2026-11-03**: entrada refrescada tras verificar y documentar H-01 (`corrective-audit.md`) |
| 6 | Notas de lectura del protocolo de Notion (no recuperables sin autenticación) | Autor, si quiere incorporarlas |

## 7. Redacción definitiva recomendada (post-auditoría 2026-11-03)

Texto listo para integrar; sustituye cualquier borrador anterior y respeta
cuentas ≠ personas y el alcance de caso único.

- **Respuesta central.** «¿Quién mantiene el software del que depende
  DeudaMundi? Puede saberse, con precisión fechada y auditable, quién aparece
  como autor, quién integra, quién revisa y quién publica en los repositorios
  de origen, y qué declaran esos proyectos sobre sus roles, procesos y
  recursos. Hasta ahí llega la evidencia pública: lo que no puede verse —el
  trabajo que no deja registro, la identidad detrás de las cuentas, las horas,
  los sueldos ni el futuro— queda explícitamente fuera.»
- **H1.** «En 14 de los 22 repositorios con actividad suficiente, una sola
  cuenta firmó más de la mitad de los commits no automatizados del año al
  corte (12 m); en 24 m, 19 de 28. La cifra describe eventos por cuenta, no
  personas, ni riesgo, ni bus factor.»
- **H2.** «Medir por commits o por PR fusionados cambia la categoría de
  concentración en 6 de los 18 repositorios comparables (12 m): la autoría de
  commits se concentra más que la de PR (en 13 de 18 la cuota por commits es
  mayor; en 2 mayor por PR; en 3 iguales). Esto compara **autorías**, no quién
  integra los cambios: la integración se observa en H4. Donde la fusión es
  squash, ambas métricas cuentan el mismo trabajo dos veces; y donde la entrada
  de cambios pasa por herramientas externas a GitHub (Gerrit), la métrica de
  PR observa un canal secundario.»
- **H3.** «Cuatro repositorios publicaron en PyPI durante el año observado sin
  crear un solo GitHub Release (psycopg, certifi, httpx, tzlocal): “sin
  releases” no significa “sin mantenimiento” —tampoco lo contrario—; significa
  que hay que mirar en otro lugar.»
- **H4.** «En algunos repositorios, la autoría, integración y revisión tienen
  cuentas principales distintas; en otros coinciden. La distribución depende
  de la actividad observada, y esa coincidencia no demuestra por sí sola
  responsabilidad formal ni mantenimiento unipersonal. Concretamente, en 6 de
  los 16 repositorios con los tres roles evaluables las cuentas principales
  difieren —en 5 de los 6 solo difiere una cuenta; solo en SQLAlchemy las tres
  son distintas— y en 10 coinciden las tres (12 m).»
- **Límites.** «El estudio reconstruyó una parte documentada y observable del
  mantenimiento: responsables declarados, roles públicos y actividad medida.
  No determina la relación cuenta–persona, el esfuerzo real ni la remuneración
  (información no determinada), y no estima sostenibilidad, abandono ni riesgo
  futuros (preguntas fuera del alcance).»
- **Gobernanza y financiación.** «Los seis proyectos documentan procesos —
  revisión en Gerrit, pipelines de release firmados, roles nombrados— y uno
  documenta además una transferencia histórica de administración (starlette,
  2025); ninguno documenta un procedimiento de relevo futuro. Sobre dinero,
  solo lo declarado: tres estructuras distintas de patrocinio en cuatro de las
  seis unidades de caso, sin que la declaración demuestre remuneración ni
  dedicación.»
- **Puente económico.** «Reproducir una biblioteca cuesta casi nada; mantenerla
  cuesta trabajo persistente que ninguna de estas magnitudes captura. Este
  estudio describe sus huellas públicas, sin valorarlas económicamente.»
- **Preguntas abiertas.** «La identidad detrás de las cuentas, el trabajo que
  no deja registro, la sostenibilidad económica de cada proyecto y la cohorte
  comparativa de otros backends (diferida) quedan como agenda, no como
  resultados.»
- **Conclusión.** «Una investigación concluida no es la que responde todas las
  preguntas, sino la que responde rigurosamente las delimitadas por su método,
  declara sus límites y deja una agenda coherente. Aquí: sabemos quién escribe,
  integra, revisa y publica —y qué se declara sobre quién coordina y financia—
  en las dependencias Python de esta aplicación; no sabemos —y no lo
  fingimos— cuánto vale ese trabajo ni cuánto durará.»
