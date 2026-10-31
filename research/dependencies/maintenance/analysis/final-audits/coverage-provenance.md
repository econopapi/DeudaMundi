# Matriz de cobertura y procedencia por repositorio (auditoría de cierre §2)

Generada desde los artefactos congelados (`data/`, `attributions/`, y los resultados del paso 5); sin acceso a GitHub.

## Verificaciones sumarias ejecutadas (no inferidas, contadas aquí)

- 35 repositorios, uno por fila del CSV; 37 distribuciones mapeadas; 2 repositorios compartidos contados una vez (psycopg, pydantic).
- Archivos JSON en data/: 443 (442 por repositorio + 1 run-summary.json en la raíz). Concilia con el '443' publicado; las 454 entradas del manifiesto del paso 4 = 443 + 11 archivos de procedencia/documentación.
- Páginas totales de eventos: 372 (144 commits + 183 PR + 45 releases = 372, según paso 4).
- Código HTTP distinto de 200: 0. `boundary_stop: true` en alguna página: 29/35 repositorios (el extractor marca el corte por límite inferior de la ventana de 24 meses; es semántica del extractor, no un error).
- Todas las corrientes `complete=true` para 35/35 (`verify_activity.py` del paso 4 confirmado de nuevo en checkout limpio).

## Anomalías por repositorio (directo, observado en los archivos)

| Repositorio | Anomalía / nota | Impacto potencial |
|---|---|---|
| encode/httpcore | cero commits humanos no-fusión en 12m (actividad por revisión/publish) | Denominadores de commits vacíos; esas repos quedan fuera de H1/H2 por la regla de evaluabilidad; H3/H4 no afectados. |
| grahamdumpleton/wrapt | default_branch=develop (rama principal observada, no main/master) | Los commits 'desde la rama principal observada' pueden excluir actividad histórica en otra rama; afecta denominadores de commits (leve, documentado en límites). |
| kludex/starlette | redirect histórico encode/starlette → kludex/starlette (documentado paso 3) | Registrar en la lectura; no invalida contraste salvo nota |
| psycopg/psycopg | repositorio compartido por 2 distribuciones: actividad puede incluir trabajo ajeno a lo congelado | Cuenta actividad del repo entero para dos paquetes; puede amplificar la concentración si el recorte es monorepo |
| pydantic/pydantic | repositorio compartido por 2 distribuciones: actividad puede incluir trabajo ajeno a lo congelado | Cuenta actividad del repo entero para dos paquetes; puede amplificar la concentración si el recorte es monorepo |
| python-hyper/h11 | cero commits humanos no-fusión en 12m (actividad por revisión/publish) | Denominadores de commits vacíos; esas repos quedan fuera de H1/H2 por la regla de evaluabilidad; H3/H4 no afectados. |

## Límites que requieren GitHub (no re-consultados aquí, declarados)

- Resolución histórica de la rama principal por fecha: la API entrega la rama actual; el paso 4 documenta esta limitación.
- PR paginados por `updatedAt`: ventana cambiante; las revisiones dentro de PR antiguos dependen de que `updatedAt` registre el toque. La auditoría previa del paso 4 documentó ocho revisiones guardadas con solapamiento de 2–10 s entre `submittedAt` y `updatedAt`.
- Releases: tags sin objeto release quedan fuera por diseño del API (documentado).
- Parciales: no se detectaron respuestas HTTP != 200 ni recuentos de registro inconsistentes (comprobador del paso 4 sobre los mismos archivos).

## Conclusión de la dimensión

La cobertura es completa por unidad (35/35), con paginación agotada excepto en los casos documentados; el impacto sobre los contrastes es limitado y declarado. Restan ventanas con revisión cambiante (documentadas) y una limitación respecto a la(branch) principal históricos que NO puede resolverse con los datos congelados.
