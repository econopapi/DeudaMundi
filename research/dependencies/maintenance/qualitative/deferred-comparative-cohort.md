# Recomendación — cohorte comparativa de otros backends (diferida)

**Fecha:** 2 de noviembre de 2026. **Estado:** recomendación explícita de
**diferir** la comparación con otros backends Python (FastAPI, Flask, Django) a
una investigación posterior. Este documento registra la decisión de alcance y
las condiciones que exigiría su propio subprotocolo. **No se ejecuta ninguna
comparación en este paso y no se presentan cifras de adopción ni similitud**:
no existen datos congelados que las sostengan.

## 1. Pregunta diferida

La línea complementaria del protocolo de Notion pregunta, en esencia: **¿hasta
qué punto las dependencias de ejecución y sus patrones de mantenimiento en
DeudaMundi son compartidos por otros backends Python públicos (FastAPI, Flask,
Django)?** Queda **diferida íntegra**, incluida su fase de recolección. El
artículo la conserva como pregunta abierta (bloques §54–§56 del borrador 2735),
sin prometer resultados ni calendario.

## 2. Por qué se difiere (motivos registrados)

1. **Universo no definido.** «Un backend FastAPI/Flask/Django público» no es una
   unidad de muestreo: un repo público no representa una aplicación desplegada,
   una empresa usuaria ni una instalación (el propio artículo ya lo advierte).
   Sin criterios de búsqueda y elegibilidad, cualquier denominador sería
   arbitrario.
2. **Riesgo de extrapolación indebida.** Este estudio es un **caso único
   descriptivo**. Mezclar una cohorte sin su propio diseño convertiría las
   proporciones congeladas de DeudaMundi en estimaciones del ecosistema, algo
   que el plan del Paso 5 prohíbe explícitamente.
3. **Coste metodológico propio.** La atribución paquete→repositorio, la
   congelación de entornos y la extracción de actividad (pasos 1–4) tienen
   reglas, verificaciones y manifiestos que deberían replicarse por cohorte;
   improvisarlos sobre la marcha contaminaría la trazabilidad ya auditada.
4. **Prioridad del protocolo.** El encargo del Paso 6 exige cerrar la lectura
   cualitativa y la preparación editorial; la cohorte es una extensión
   declarada «módulo separado» desde el plan preregistrado («Lo que estos datos
   no permiten afirmar», punto final).

## 3. Cambio de alcance que debe registrarse (cuando se retome)

- **Ampliación de la pregunta** de «un caso» a «comparación entre aplicaciones»:
  unidad de análisis nueva (aplicación/backend público), no repositorio.
- **Nuevo preregistro obligatorio** antes de recolectar datos: criterios de
  búsqueda y elegibilidad, fuentes de repositorios candidatos, muestreo,
  denominadores, reglas de bots/no atribuidos idénticas o justificadas,
  ventanas temporales (nuevo corte: **no** reutilizar el corte 2026-10-30 para
  afirmar sobre otras aplicaciones), y métricas de similitud definidas de
  antemano.
- **Separación editorial estricta:** los resultados de la cohorte deben
  publicarse como módulo aparte (artículo o sección con su propia marca), nunca
  fundidos con las cifras de DeudaMundi en los mismos denominadores.
- **Enmienda al protocolo de Notion** con fecha: la pregunta queda «diferida a
  estudio posterior», no «respondida».

## 4. Condiciones que exigiría su propio subprotocolo (checklist mínimo)

1. Definición operacional de «aplicación/backend público comparable» y de la
   fuente de repositorios (p. ej. criterios de búsqueda reproducibles), con
   lista congelada y hash.
2. Congelación del entorno por cohorte (equivalente al Paso 1) o justificación
   formal de una fuente alternativa de dependencias (p. ej. archivos de lock
   publicados), con sus propios límites declarados.
3. Atribución paquete→repositorio con el mismo rigor del Paso 3 (recibos,
   redirecciones, repos compartidos).
4. Extracción de actividad con las mismas definiciones de evento, bot y
   evaluabilidad, con sus propios manifiestos SHA-256 y cobertura declarada.
5. Plan de análisis preregistrado con denominadores mínimos y hipótesis
   propias; prohibido «ver los datos y luego elegir umbral».
6. Consideración explícita de la **dependencia estadística entre muestras**
   (aplicaciones que comparten dependencias no son observaciones
   independientes).
7. Revisión factual y de riesgo de estigmatización: comparar «mantenimiento»
   entre proyectos puede leerse como ranking de calidad; el subprotocolo debe
   fijar reglas de redacción para no atribuir responsabilidad a cuentas.
8. Presupuesto de API y verificación independiente equivalentes a los del
   Paso 5.

## 5. Efecto sobre la publicación actual

Ninguno: el artículo puede cerrarse como estudio de caso único sin la cohorte,
siempre que la frase «no es una estimación de todo Python» permanezca visible y
la cohorte aparezca solo como pregunta abierta diferida (texto ya propuesto en
`editorial-handoff.md`).
