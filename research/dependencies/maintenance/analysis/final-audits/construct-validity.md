# Validez de constructo y alcance científico (§7) — Paso 5

Pregunta editorial: **¿Quién mantiene el software del que depende una aplicación Python?**

## Matriz constructo → indicador disponible → afirmación permitida → afirmación NO justificada

| Constructo | Indicadores disponibles (datos congelados) | Afirmación PERMITIDA con esta evidencia | Afirmación NO justificada (separación explícita) |
|---|---|---|---|
| **Actividad observable** | commits de rama principal (con/sin fusiones, bots, no atribuidos), PR fusionados, revisiones (pares), releases (12/24 m; 35 repos; recibos por página) | Los eventos públicos congelados y sus totales por repositorio/ventana, desglosados por cuentas y clases de actor | Actividad total del proyecto (fuera de GitHub: triage, soporte, coordinación privada, enseñanza); horas de trabajo |
| **Concentración de contribuciones** | cuota top-1/top-2, HHI por métrica y ventana, con denominadores explícitos (≥30/≥10/≥5 preregistrados) | Distribución observable de ciertos eventos entre cuentas, por repo y ventana; categorías del protocolo; sensibilidad 12/24 | "Un actor concentra el mantenimiento" sin matriz; contraste de una cuota con probabilidad de fallo o riesgo |
| **Actividad de revisión** | pares únicos (revisor, PR) con estados del API y bots separados | Quiénes revisan más por repo y ventana (cuentas); evaluabilidad ≥5 pares | Calidad de revisión, diligencia, autoridad de decisión (no se capturan) |
| **Automatización** | bots clasificados por campo congelado `bot` (type=Bot/sufijo [bot]); bots/total por flujo, y variantes con misma unidad | Participación observable de automatización declarada por evento, ventana y repo | Automatización NO declarada está ella caracterizada sólo con advertencias (claude, sqla-tester, invalid-email-address); un release por bot no excusa trabajo humano previo |
| **Continuidad histórica** | meses con actividad por flujo, última fecha observable, cadencia de releases | Continuidad observable de la ventana (1–24 meses) | Cese/abandono; salud del proyecto; ningún "sin release = abandonado" (H3 rebatió cada atajo) |
| **Identificación de mantenedores** | cuentas top por rol (committer, integrador, revisor, publicador) y advertencias específicas | Cuentas con MAYOR actividad observable por rol y ventana | Identidad de mantenedores FORMALES (roles, permisos, gobernanza); personas tras las cuentas (alias posibles sin fusionar) |
| **Responsabilidad efectiva del mantenimiento** | ningún indicador directo disponible | — | Cualquier asignación de responsabilidad de mantenimiento eficaz a cuentas específicas |
| **Sostenibilidad / riesgo futuro** | ningún indicador directo (no se construyó, por plan) | — | Riesgo de DeudaMundi, "bus factor", probabilidad de abandono: la presentación debe referirse sólo a "concentración observable de contribuciones" |
| **Atribución del paquete al repo** | paso 3: URL congelada + PyPI + resolución GitHub (`verified`) | El repo de origen documental cada dist; 37→35 (dos compartidos) | Origen bit del wheel de un artefacto (sin reconstruir) y no demostrado a nivel de archivo |
| **Publicaciones** | evidencia PyPI (37 dists con recibos) vs releases GitHub | versiones publicadas en PyPI por ventana; publicaciones sin release de GitHub (4 repos, H3) | Autoría de cada upload; release por cuenta del publicador como "trabajo hecho por esa cuenta" |
| **Respuesta editorial** | ninguno: no hay resultado que nombre responsables | Diagnóstico *a quién preguntar* siguientes pasos: lectura cualitativa de los 6 casos seleccionados y revisión factual | "Está mantenido por X" — la investigación sigue abierta por diseño del protocolo |

## Separación de alcance

1. **Describe este congelado:** 35 repositorios, 2 ventanas, 4 flujos; no describe el ecosistema Python ni otros backends (cohorte complementaria aparte, plan definido en el protocolo Notion).
2. **Cuentas ≠ personas:** cuenta ≠ persona; una persona puede estar detrás de varias cuentas y viceversa. Ninguna aproximación de alias se realiza aquí sin nota.
3. **Las hipótesis H1–H4 son descriptivas del caso**(umbral editorial), no validan un mecanismo causal y no son probabilidad de riesgo económico u organizativo.
4. **Hipótesis económicas/organizaciónales plausibles pero no demostradas aquí** (candidatas para investigación futura, requerirían los módulos aún no levantados):
   - la concentración observada de contribuciones coexiste con sostenibilidad reportada (psycopg, certifi, hg, etc.) – requeriría cohortes y gobernanza documentada;
   - la automatización en releases (39.3 %) guarda relación con modo de financiación de actividades de seguridad – requiere fuentes institucionales;
   - la retención del parto del trabajo depende del rol de quien recibe finanzas – lectura cualitativa pendiente.

Estas hipótesis explicativas NO se tratan como resultados del paso 5.
