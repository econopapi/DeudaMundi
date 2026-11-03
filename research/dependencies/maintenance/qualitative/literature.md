# Marco conceptual y bibliografía crítica (Fase 4)

**Fecha de consulta de las fuentes:** 2 de noviembre de 2026. **Regla de uso:**
las obras se emplean como **marco interpretativo**, nunca como extrapolar del
ecosistema al caso DeudaMundi. No se calcula valor económico, costo salarial ni
externalidades: las cifras que se transcriben son reproducción literal de sus
fuentes y **no** se aplican al caso. Toda conexión con DeudaMundi va marcada
como inferencia (E3).

**Convención de recuperación:** E1a = texto completo recuperado; E1b =
resumen/página oficial recuperada, texto completo no recuperado; E1c = extractos
localizados por búsqueda (usar con cautela antes de citar literalmente);
E4 = no recuperable.

## 1. Census III of Free and Open Source Software (Nagle, Powell, Zitomer & Wheeler, LF/OpenSSF/LISH, 2024)

- **Referencia:** *Census III of Free and Open Source Software – Application
  Libraries*, The Linux Foundation & OpenSSF con LISH (Harvard), diciembre 2024,
  DOI `10.70828/JRPB8299`. Página oficial:
  <https://www.linuxfoundation.org/research/census-iii> (E1b; PDF completo no
  recuperado, ≈183 págs.; hallazgos contrastados contra la nota de prensa
  oficial de OpenSSF, 04-12-2024).
- **Pregunta / marco:** qué paquetes FOSS son más usados como bibliotecas de
  aplicación y qué patrones de uso y seguridad presentan; el FOSS como
  infraestructura cuya «salud» exige identificar los componentes de los que
  dependen las organizaciones.
- **Método y unidad:** cuantitativo agregado; «over 12 million observations of
  FOSS libraries in production applications at more than ten thousand
  companies» (datos anonimizados de cuatro firmas SCA: Black Duck, FOSSA, Snyk,
  Sonatype). Unidad: paquete FOSS en producción empresarial (datos de 2023).
- **Hallazgos pertinentes:** (a) «Much of the most widely used FOSS is
  developed by only a handful of contributors» (hallazgo clave de la nota de
  prensa); (b) creciente prevalencia de paquetes Python; (c) persistencia de
  software legado; (d) la dependencia de cuentas individuales conecta el
  mantenimiento con decisiones de seguridad de terceros.
- **Limitaciones para DeudaMundi:** es un censo de **uso** (demanda), no de
  trabajo de mantenimiento; no identifica mantenedores ni financiación; sesgo
  hacia clientes de las firmas SCA; agregado ecosistémico que **no** se
  extrapola a un caso único. Sirve como contexto de escala, no como dato.
- **Afirmación del artículo que contextualiza:** «La mayor parte del software
  ampliamente usado está desarrollado por un puñado de contribuidores» es
  concordante con las cuotas top-1 observadas en este caso (§041 del borrador),
  **sin** que el Census III valide esas cuotas ni viceversa: son fuentes
  independientes con unidades distintas (E3).

## 2. Nadia Eghbal, *Working in Public* (Stripe Press, 2020)

- **Referencia:** Eghbal, Nadia (2020). *Working in Public: The Making and
  Maintenance of Open Source Software*. Stripe Press, 256 págs.
  <https://press.stripe.com/working-in-public> (E1b; texto completo no
  recuperado, monografía de pago; la autora figura también como Nadia
  Asparouhova).
- **Pregunta / marco:** cómo evolucionó el desarrollo OSS hacia «operadores
  individuales» cuyo código consumen millones; el libro sitúa explícitamente
  «the maintenance costs of production that software incurs for its developers»
  y «the costs of production that endure through an application's lifetime».
- **Método y unidad:** cualitativo-divulgativo basado en «hundreds of developer
  interviews» y análisis de plataformas; unidad: proyectos de GitHub y sus
  roles (mantenedores, contribuidores, usuarios).
- **Hallazgos pertinentes:** (a) separación entre **costo marginal de
  reproducción** (copiar el código) y **costos persistentes de mantenimiento**
  que duran la vida de la aplicación; (b) «Open source communities are
  increasingly centered around the work of individual developers rather than
  teams», con «often unseen solo operators who write and publish the code that
  millions of users rely on every day».
- **Limitaciones:** ensayo divulgativo sin muestreo ni datos replicables;
  universo GitHub/anglofono anterior a 2020; sus tipologías de proyectos son
  heurísticas, no categorías validadas. **No** permite concluir nada sobre los
  seis casos; aporta vocabulario analítico (E3).
- **Afirmación del artículo que respalda:** el puente argumental de §061
  («una biblioteca puede instalarse en segundos… mientras conservarla útil
  exige revisar cambios, responder problemas, publicar versiones») es la tesis
  del libro, citada como marco y **no** como resultado propio.

## 3. Cailean Osborne — financiación de Open Source

- **Referencia principal (texto completo recuperado, E1a):** Osborne, Cailean
  (2024). *Public-private funding models in open source software development: A
  case study on scikit-learn*. arXiv:2404.06484v5.
  <https://arxiv.org/html/2404.06484v5>.
- **Pregunta / marco:** cómo evalúan los desarrolladores OSS el financiamiento
  gubernamental frente a otras fuentes; sostenibilidad, free-riding y
  gobernanza que protege la autonomía de la comunidad.
- **Método y unidad:** estudio de caso único cualitativo con métodos mixtos
  (documentos + 25 entrevistas semiestructuradas 2021–2023 + notas de campo);
  unidad: scikit-learn y su financiación mixta (Inria, consorcio empresarial,
  microdonaciones, GSoC, subvención pública francesa).
- **Hallazgos pertinentes (citas verificadas del texto):** (a) «The major part
  of the labour [in the project] is based on benevolance of people working in
  their free time and not asking to get paid»; además del desarrollo, «Community
  animation is a huge part» del trabajo; (b) dependencias infra-mantenidas:
  «OpenBLAS … only maintained by two people … They are the foundations; they
  are the infrastructure»; (c) las contribuciones de empresas no patrocinadoras
  «create more work for the maintainers»; (d) los mantenedores insistieron en
  «the need to allocate sufficient funding to maintenance» y en proteger el
  consenso frente a los financiadores: «Overall, it's good to have a
  panaché» (fuentes mixtas).
- **Limitaciones:** caso singular (biblioteca de primer nivel con respaldo
  institucional); estudio de un proyecto **aguas arriba**, no del grafo de una
  aplicación aguas abajo; su sección de amenazas a la validez limita la
  transferibilidad. Sus cifras financieras **no** se trasladan al caso.
- **Afirmación del artículo que contextualiza:** §053/§061 («recursos por
  mantenerlo», «quién lo paga») queda como pregunta abierta; Osborne aporta el
  contraste de que la financiación existente tiende a financiar novedades y que
  sostener exige decisiones explícitas de financiar el **mantenimiento** (E3).

Obras complementarias del mismo autor (E1c, abstracts): *A Toolkit for
Measuring the Impacts of Public Funding on OSS* (arXiv:2411.06027) — medir
impacto exige considerar etapa de vida, estructura social y objetivos de
financiación —; *Why Companies "Democratise" Artificial Intelligence*
(arXiv:2409.17876) — incentivos comerciales detrás de donar/mantener OSS.

## 4. Yochai Benkler, «Coase's Penguin, or, Linux and the Nature of the Firm» (2002)

- **Referencia:** *The Yale Law Journal*, vol. 112 (2002), p. 369 ss.
  <https://yalelawjournal.org/article/coases-penguin-or-linux-and-the-nature-of-the-firm>
  (E1b: abstract íntegro recuperado; PDF completo no recuperado).
- **Pregunta / marco:** extiende la teoría de la firma de Coase para describir
  un tercer modo de producción —*commons-based peer production*— distinto de la
  firma y del mercado: miles de personas colaboran «where no one "owns" the
  software in the traditional sense».
- **Método y unidad:** teórico-conceptual con casos ilustrativos; unidad: modos
  de organización de la producción de información.
- **Argumentos pertinentes:** (a) la coordinación sin propiedad ni precios
  reduce los costos de transacción de selección de tareas y colaboradores;
  (b) ventaja en «information opportunity cost» al asignar mejor el capital
  humano; (c) estos modelos usan «a variety of technological and social
  strategies to overcome the collective action problems usually solved … by
  property and contract».
- **Limitaciones:** escrito antes de GitHub y de los gestores de paquetes
  modernos; es teoría, no evidencia; «bien compartido / acción colectiva»
  aplicado al mantenimiento de dependencias es **inferencia E3**, no hallazgo
  del texto para este contexto.
- **Afirmación del artículo que contextualiza:** el encuadre de §061 (software
  como recurso compartido cuya conservación no la resuelve el mercado de la
  copia) recibe de Benkler su lente teórica; el artículo debe presentarlo como
  marco, sin atribuir a Benkler afirmaciones sobre este caso.

## 5. Lerner & Tirole — economía del código compartido (2002 / 2005)

- **Referencias:** Lerner, J. & Tirole, J. (2005). «The Economics of Technology
  Sharing: Open Source and Beyond», *Journal of Economic Perspectives* 19(2):
  99–120, DOI `10.1257/0895330054048678`; y Lerner, J. & Tirole, J. (2002).
  «Some Simple Economics of Open Source», *The Journal of Industrial
  Economics* 50(2): 197–234, DOI `10.1111/1467-6451.00174`. (E1b: abstracts
  recuperados; textos completos no recuperados — paywalls/PDF no legibles —;
  matices de sección vía E1c.)
- **Pregunta / marco:** por qué programadores y empresas invierten en software
  que no controlan propietariamente; marcos de *career concerns* (señalización
  profesional, reputación) y de organización industrial (licencias, estrategia).
- **Método y unidad:** revisión teórica con modelos formales y análisis
  empírico de licencias; unidad: contribuidores, proyectos y empresas.
- **Argumentos pertinentes:** (a) el contribuidor afronta «an opportunity cost
  of time» frente a beneficios no pecuniarios (señalización, reconocimiento);
  (b) para empresas, OSS reduce riesgos de *hold-up* («no future price increase
  after adopting a technology») y *patent thickets*; (c) los marcos explican
  estructura y roles del proyecto, no el trabajo continuo de mantenimiento;
  (d) los propios autores advierten que el futuro del proceso «remain[s]
  somewhat difficult to predict with 'off-the-shelf' economic models».
- **Limitaciones:** principios de los 2000 (kernel, Apache, licencias); no
  aborda gestores de paquetes ni carga post-publicación; los incentivos
  tipificados **no** pueden atribuirse a los mantenedores concretos sin
  evidencia del caso (E3).
- **Afirmación del artículo que contextualiza:** la sección de incentivos del
  artículo («quién lo paga», trabajo visible e invisible) puede apoyarse en
  estos marcos como **hipótesis interpretativas**, etiquetadas como tales, sin
  atribuir motivaciones a las cuentas observadas.

## 6. Hoffmann, Nagle & Zhou, «The Value of Open Source Software» (HBS WP 24-038, 2024)

- **Referencia:** Harvard Business School Working Paper 24-038 (enero 2024),
  DOI SSRN `10.2139/ssrn.4693148`.
  <https://www.hbs.edu/faculty/Pages/item.aspx?num=65230> (E1b: abstract
  recuperado; PDF completo no recuperado).
- **Pregunta / marco:** cómo valorar un producto no pecuniario; el OSS como
  «a global public good», distinguiendo valor del lado de la oferta (costo de
  recrear el software) y del lado de la demanda (valor de reemplazo por firma).
- **Método y unidad:** estimación de valoración con dos fuentes globales
  (Census II y BuiltWith); unidad: paquetes OSS ampliamente usados y firmas
  usuarias.
- **Hallazgos pertinentes (reproducidos literalmente del abstract):** (a) «96%
  of the demand-side value is created by only 5% of OSS developers»; (b) «The
  top six programming languages in our sample comprise 84% of the demand-side
  value of OSS»; (c) el documento reporta valores agregados de oferta (4,15 mil
  millones USD) y demanda (8,8 billones USD) y que las firmas gastarían 3,5
  veces más sin OSS. **Estas cifras no se recalculan ni se aplican a
  DeudaMundi** (prohibición del protocolo).
- **Limitaciones:** working paper no revisado por pares en la versión
  consultada; valoración agregada que no observa mantenimiento, horas ni
  gobernanza; su lógica de «recrear una vez» **subestima por construcción** el
  trabajo persistente de mantenimiento (E3: crítica del investigador).
- **Afirmación del artículo que contextualiza:** sirve para el puente
  «reproducir es barato / mantener es costoso» de §061 y para mostrar que la
  concentración de creación de valor documentada en el ecosistema **es
  compatible** con las cuotas observadas aquí, sin validarlas (E3).

## 7. Discusión económica del caso (síntesis conceptual, sin cálculos)

1. **Costos marginales de reproducción ≈ 0.** Copiar e instalar una
   distribución Python no cuesta apreciablemente nada al usuario (Benkler:
   reducción de costos de transacción; Hoffmann et al.: distinción
   oferta/demanda; Eghbal: reproducción barata). DeudaMundi instala 37
   distribuciones en segundos; la foto del Paso 1 documenta ese resultado, no
   su costo.
2. **Costos persistentes de mantenimiento.** Revisar cambios, responder
   problemas, publicar versiones y decidir rumbo son costos que duran la vida
   de la dependencia (Eghbal; Osborne: «allocate sufficient funding to
   maintenance»). Los flujos de eventos del Paso 5 (commits, PR, revisiones,
   releases) son **huellas observables** de parte de ese trabajo, no su
   medición (E3).
3. **Provisión de un bien compartido.** Las dependencias son
   infraestructura común de muchas aplicaciones (Benkler; Census III;
   Osborne: «They are the foundations; they are the infrastructure»). La
   coordinación sin contrato ni jerarquía se sostiene en estrategias
   tecnológicas y sociales (revisión por pares, automatización de releases,
   acuerdos de contribución) — visibles en los expedientes como procesos
   documentados (E1/E2), sin concluir sobre su suficiencia.
4. **Incentivos.** Señalización profesional y reputación (Lerner & Tirole),
   autonomía y financiación mixta (Osborne), motivación intrínseca (Eghbal).
   Son marcos; **ninguna motivación se atribuye a las cuentas observadas** sin
   declaración propia (E3/E4).
5. **Coordinación entre actores.** Usuarios aguas abajo (como DeudaMundi),
   contribuidores ocasionales, integradores, publicadores de versiones y
   financiadores son roles distintos — la misma separación que imponen los
   cuatro flujos de eventos y los roles de H4.
6. **Sostenibilidad organizacional.** Los casos cualitativos muestran modelos
   distintos (organización fundacional, cuenta individual, empresa/consorcio);
   la literatura indica que la mezcla de fuentes y el financiamiento explícito
   del mantenimiento son variables centrales (Osborne), **sin** que este estudio
   pueda evaluar la sostenibilidad futura de ningún proyecto.

## 8. Referencia no recuperable

- Protocolo de investigación en Notion
  (<https://app.notion.com/p/409d8d49cd6481cc873fe4ddc7c93745>): requiere
  autenticación; **E4**. Las lecturas priorizadas se tomaron de la lista del
  propio encargo; si el protocolo interno contiene notas de lectura adicionales,
  deberán incorporarse como documento interno citado, no como fuente pública.
