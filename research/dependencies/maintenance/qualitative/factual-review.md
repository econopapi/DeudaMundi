# Revisión factual — afirmaciones sensibles y mensajes propuestos

**Paso 6 · 2 de noviembre de 2026. Estado: NINGÚN MENSAJE ENVIADO.** Este
documento identifica las afirmaciones del estudio que involucran a responsables
o gobernanza de proyectos concretos y prepara, para cada una, un mensaje de
revisión factual limitado a esa afirmación, con sus fuentes y preguntas
verificables. El envío (si procede) es una **decisión editorial del autor**.

**Reglas aplicadas:** (a) solo se revisan afirmaciones sobre proyectos/actores
concretos, no las cifras agregadas del caso; (b) la **ausencia de respuesta no
se interpretará como confirmación** — sin respuesta, la afirmación se publicará
en su forma atenuada ya propuesta, o no se publicará; (c) se distingue entre
afirmaciones publicables con evidencia suficiente, afirmaciones que merecen una
oportunidad de corrección factual y afirmaciones que deben atenuarse o
retirarse; (d) la revisión externa es **recomendada** —cortesía y oportunidad
de corrección—, **no condición universal de publicación**: las afirmaciones
clase A (hechos públicos con fuente citable) se publican con su evidencia sin
depender de respuestas de terceros.

**Matiz de sucesión (auditoría 2026-11-03):** donde los mensajes preguntan por
«governance or succession», la distinción operativa es entre **transferencia
histórica documentada** (starlette, 2025-09), **roles/procesos formales
documentados** (los seis, en distinto grado) y **procedimiento de relevo
futuro** (no localizado en ninguno; `claim-ledger.csv` C49). La ausencia de
`GOVERNANCE.md` no se presenta como ausencia de gobernanza.

## Clasificación general

| Clase | Criterio | Afirmaciones |
|---|---|---|
| **A — publicables con evidencia documental suficiente** | Hechos E1/E2 con fuente citable, sin atribución de intención ni de identidad personal | C01–C18 (metodología y cifras), C20–C27, C29–C30, C32–C34, C37–C44 |
| **B — con oportunidad de corrección factual** | Afirmaciones E1/E2 que describen roles, decisiones o conflictos de proyectos concretos y cuya redacción puede afectar a personas/organizaciones identificables | C19, C21, C28, C31, C35, C36 |
| **C — atenuar o retirar** | Sin evidencia suficiente o con riesgo de implicar identidad, intención o remuneración | Cualquier forma de «abandono», «bus factor», «riesgo»; la atribución de «get paid by Tidelift» (libraries.io); la identificación de cuentas con personas; la lectura de `claude` como agente concreto sin declaración propia |

## 1. `kludex/starlette` (antes `encode/starlette`) — prioridad ALTA

**Afirmaciones (C35, C36, C37):** transferencia de la administración de
starlette/uvicorn de la organización `encode` a la cuenta personal `Kludex`
(sept. 2025) por acuerdo público; debate posterior sobre el modelo de propiedad
(issue #3180, cerrada y bloqueada el mismo día); pregunta de una tercera cuenta
sobre si quedaba un único mantenedor (sin respuesta registrada); roles
nombrados autor/mantenedor en PyPI y `CITATION.cff`; licencia con titular
histórico Encode OSS Ltd.

**Clase:** B (oportunidad de corrección). La mención de un hilo cerrado y
bloqueado, y de una pregunta sin respuesta, es factual pero sensible.

**Mensaje propuesto (NO enviado; redactar al destinatario elegido por el autor:
mantenedor actual y/o organización encode):**

> As part of a single-case study on dependency maintenance (frozen data from
> 2026-10-30; article draft in Spanish), we describe Starlette's public
> documentation as follows and would like to give you the opportunity to
> correct any factual error before publication:
>
> 1. Administration of `encode/starlette` and `encode/uvicorn` was transferred
>    to the personal account `Kludex` in September 2025 (Discussion #2997:
>    "this only changes the official administration of the projects").
> 2. In March 2026, issue #3180 proposed reconsidering the project ownership
>    model; it was closed as not planned and locked the same day.
> 3. Package metadata names Tom Christie as author and Marcelo Trylesinski as
>    maintainer; `LICENSE.md` retains "Copyright © 2018, Encode OSS Ltd".
> 4. Our metrics (not a statement about people) show the `Kludex` account
>    leading commits, merged PRs, reviews and releases in the 12 months to
>    2026-10-30.
>
> Questions: (a) Is point 1 accurate and reasonably worded? (b) Is there a
> documented governance or succession model we should cite instead of / in
> addition to point 2? (c) Are the roles in point 3 current? (d) Anything you
> would like qualified or removed?

**Redacción si no hay respuesta:** mantener 1, 3 y 4 (E1/E2 citados); el punto 2
se publicaría solo como «hubo un debate público sobre el modelo de propiedad,
resuelto sin cambios», sin describir el bloqueo del hilo, o se retirará.

## 2. `sqlalchemy/sqlalchemy` y `sqlalchemy/alembic` — prioridad MEDIA

**Afirmaciones (C19, C21):** declaración pública de que dos cuentas son
mantenedoras de todos los proyectos de la organización; releases materializadas
por `sqla-tester` tras subidas manuales a PyPI; revisión/integración vía Gerrit
(C20, clase A).

**Clase:** B. Las citas son textuales y públicas, pero nombran roles.

**Mensaje propuesto (NO enviado; destinatario sugerido: canales oficiales de la
organización `sqlalchemy`, p. ej. la Discussion #11553 o contacto público del
proyecto):**

> In our case study we quote your public statements: Discussion #11553
> ("myself and @CaselIT are the maintainers of every project under the
> 'sqlalchemy' organization") and Discussion #13324 ("mike pushes the tar.gz
> to pypi and makes the GitHub release that starts the pipeline"), plus the
> development guide ("Pull requests for code changes are never merged
> directly"). We report GitHub-event metrics per account (not per person) and
> explicitly warn that `sqla-tester` is CI automation, not a reviewer.
> Questions: (a) Are these quotes still accurate descriptions of your
> governance? (b) Is there a public governance or succession document we should
> cite? (c) Any correction to how we describe your release process?

**Redacción si no respuesta:** publicable como está (citas E1/E2, sin
identificar personas); sin añadir nada sobre intenciones o disponibilidad.

## 3. `psycopg/psycopg` — prioridad MEDIA

**Afirmaciones (C31, C32, C33):** dos cargos nombrados en la web oficial
(Technical Lead / Operations Lead) con funciones que incluyen triage y
coordinación; patrocinio declarado (personal, organización y tiers corporativos
con `BACKERS.yaml`); propiedad registrada del paquete PyPI (`piro`) distinta de
la cuenta con más eventos (`dvarrazzo`).

**Clase:** B (los cargos nombrados) + A (financiación declarada, propiedad de
paquete). C33 se redacta sin identificar cuentas entre sí.

**Mensaje propuesto (NO enviado; destinatario sugerido: contacto de
psycopg.org / sponsors):**

> Our study reports, from your official site, two named roles (Technical Lead:
> "creator and primary maintainer of Psycopg 2 and Psycopg 3"; Operations
> Lead: coordination, release support, issue triage, documentation oversight)
> and your public sponsorship pages. We do not estimate funding amounts,
> salaries or time dedication. Questions: (a) Are these roles current and
> correctly described? (b) Is there a governance/succession document to cite?
> (c) Would you qualify how we describe the release process (tags + PyPI, no
> GitHub Releases)?

**Redacción si no respuesta:** publicable (E1 con fecha de consulta), sin
comentar la estructura de financiación más allá de lo declarado.

## 4. `kjd/idna` — prioridad MEDIA-BAJA

**Afirmación (C28):** tensión documental entre la autors singular del
`pyproject.toml` y la autodescripción «maintained by a team of volunteers»
(`SECURITY.md`).

**Clase:** B leve. La tensión es entre dos documentos públicos; se publica como
tal, sin resolverla.

**Mensaje propuesto (NO enviado):**

> We report both facts verbatim: `pyproject.toml` lists a single author entry
> and `SECURITY.md` says the project "is maintained by a team of volunteers who
> work on a best effort basis". We present the tension without resolving it.
> Questions: (a) Is there a public list of maintainers you would like us to
> cite? (b) Any correction to our wording?

## 5. `python/typing_extensions` — prioridad BAJA

**Afirmaciones (C24, C25):** seis cuentas con roles de Owner/Maintainer en
PyPI (hecho E2 congelado); ausencia de declaración pública de financiación del
proyecto (ausencia documentada E2/E4).

**Clase:** A/B. La ausencia de financiación **declarada** no debe leerse como
ausencia de fondos; la redacción ya lo advierte.

**Mensaje propuesto (NO enviado):** opcional, solo si se cita el proyecto por
su financiación: confirmar que «no hay declaración pública localizada» es
correcto y que el proyecto no desea añadir nada.

## 6. Automatización no declarada (`claude`, `sqla-tester`, `invalid-email-address`) — prioridad ALTA (manejo interno)

**Afirmación (C15/C17):** patrones de automatización no declarada documentados
en `../analysis/audits.md`. **No se contactará a las cuentas** (el encargo lo
prohíbe y una pregunta sobre «¿eres un bot?» es innecesaria). Manejo editorial:

- `sqla-tester`: describir como «la cuenta que materializa el pipeline de CI y
  releases de SQLAlchemy (documentado públicamente)», nunca como revisora.
- `claude`: «patrón compatible con automatización no declarada» (E3 explícita);
  prohibido afirmar qué agente es ni quién lo opera.
- `invalid-email-address`: «cuenta materializadora de GitHub cuando el commit
  no tiene correo vinculable» (definición del plan), sin más atribución.
- **Clase C:** cualquier frase que convierta estos patrones en acusación o en
  identidad queda prohibida.

## 7. Procedimiento de envío (para el agente/humano que lo ejecute)

1. El autor elige canal y destinatario por proyecto (issue pública, email de
   seguridad/mantenimiento, o discusión existente).
2. Se envía **solo** el mensaje de la sección correspondiente, sin adjuntar
   resultados no publicados ni datos de otros proyectos.
3. Plazo sugerido: 7–14 días naturales; **sin** recordatorios automáticos.
4. Las respuestas se incorporan como fuentes fechadas (E1) con su agradecimiento
   en el artículo; las correcciones factuales se aplican al texto y al
   `claim-ledger.csv` (nueva versión del registro, sin borrar la anterior).
5. Sin respuesta: se aplica la redacción alternativa indicada y se deja
   constancia de la consulta sin respuesta, **sin** interpretarla como
   confirmación ni como negativa.
