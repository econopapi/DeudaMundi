Cómo incorporar las figuras interactivas al borrador de WordPress (post 2735)
=============================================================================
Estado: método investigado y materializado; **requiere verificación en un
borrador de trabajo** antes de aplicarlo al post real. Nada aquí activa el
viejo plugin de Plotly ni publica nada.

Contexto verificado
-------------------
- El sitio (econopapi.com) es WordPress.com con plan capaz de plugins: en la
  raíz REST (/wp-json) aparecen namespaces wpcom/v2, jetpack/v4,
  code-block-pro/v1, astra/v1, etc. Para instalar plugins en WP.com hace falta
  ese nivel de plan (el tema Econopapi WP ya es un tema hijo con bloques
  propios).
- El borrador 2735 (copia local: outputs/borrador-deudamundi-wordpress.html de
  la sesión del 30-10) ya renderiza un bloque interativo `graphdraw/diagram`
  con sus propios scripts: es la prueba de que los mecanismos que un plugin
  o bloque encolado controlan funcionan en el sitio.
- La(editor)ーバ de scripts en contenido de post depende de la capacidad
  `unfiltered_html` (disponible a administradores en sites con plan de
  plugins). No se pudo verificar por API en esta sesión porque no hay
  credenciales; por eso el paso 1 abajo es obligatorio.

Vías evaluadas (procedencia: investigación WordPress.com + REST del sitio,
2026-10-30; sin dependencia del plugin viejo de Plotly)
------------------------------------------------------
A. **Bloque "HTML personalizado" con fragmento inline** (vía primaria a
   probar). Ventajas: cero plugins nuevos, el HTML autocontenido lleva
   fuentes+datos+JS, y el alto/tema quedan gestionados dentro (claro/oscuro,
   móvil). Riesgo: WP.com puede eliminar <script> en el contenido; el paso 1
   lo decide en 5 minutos. Los fragmentos listos están en este directorio
   (fig{N}-*-fragmento-wp.html; ~250 KB cada uno).

B. **Servidor propio: iframe** al VPS de DeudaMundi (Caddy ya sirve el
   dominio; docker-compose.prod.yml). Se subiría figures/figN-*.html a una
   carpeta estática y se embebería:
     <figure>
       <iframe src="https://deudamundi.{dominio}/research/figures/fig1-...html"
               title="..." loading="lazy" style="width:100%;height:480px;
               border:0" sandbox="allow-scripts></iframe>
     </figure>
   Ventajas: immune a la eliminación de scripts; URL de primera parte;
   la autoriaqueda del tema no puede romper el CSS interno. Desventajas:
   requiere subir/deploy manual (un Make target o rsync) y mantener las
   figuras sincronizadas con el commit versionado.

C. **plugins nuevos tipo GraphDraw** (encolar plotly.min.js + payload JSON).
   Consistente con el sitio (GraphDraw hace esto con Mermaid), pero añade
   código a mantener; solo vale la pena si A y B fallan. No se creó.

D. **El plugin viejo de Plotly**: NO activado, NO evaluado; sin acceso de
   administrador no se puede inspeccionar (nombre exacto, versión de Plotly
   que carga, soporte WCAG, peso). Antes de considerar reactivarlo, revisar
   en wp-admin > Plugins: fecha de última actualización, versión de
   plotly.js que encola (debe ser ≥ 2.x para responsive/interacciones),
   tamaño, y si acepta datos inline sin CDN externo. Criterio sugerido: si
   encola Plotly < 2.x o requiere subida de CSV insegura, descartarlo y usar
   la vía A/B.

Procedimiento de verificación (en un borrador de trabajo nuevo)
---------------------------------------------------------------
1. Crear borrador nuevo, pegar y guardar el contenido de
   `prueba-script-wp-fragmento.html` en un bloque "HTML personalizado",
   reproducir con "Vista previa" y comprobar: aparece el texto "PLOTLY OK EN
   WORDPRESS" con una gráfica mínima.
   - Si aparece: la vía A está disponible; seguir el paso 2.
   - Si el bloque desaparece o queda texto plano: la vía A queda descartada;
     recordar qué camino tomar (paso 5).
2. Copiar el contenido completo de cada figN-*fragmento-wp.html* y pegarlo en
   su propio bloque HTML personalizado, en el orden deseado del artículo.
3. Comprobar en la vista previa (escritorio y móvil, y con el modo claro y
   oscuro del sitio):
   - Las 5 figuras pintan y sus tooltips muestran unidades y denominadores.
   - El claro/oscuro cambia con el sitio (media query del sistema).
   - La tabla accesible desplegable funciona.
4. Registrar en esta misma carpeta qué método funcionó (archivo
   resultado-incorporacion.txt) y el hash SHA-256 de cada fragmento pegado
   (los hashes de los archivos fuente están en ../SHA256SUMS).
5. Si la vía A no funcionó: usar la vía B (iframe), declarando el origen de
   los cinco HTML (commit de esta rama) en el atributo title del iframe y
   anotando fecha de deploy en el README.

Advertencias
------------
- Cada fragmento incluye <script src="https://cdn.plot.ly/...">: si el sitio
  endurece CSP o drawlots ante CDN, en su lugar corresponde la vía B.
- El contenido de este directorio no debe pegarse directo al post 2735 sin el
  paso de verificación 1-3; está pensado para un borrador de prueba.
- Los fragmentos generan su tema según el sistema del lector; el toggle
  'claro/oscuro' sirve para comparar a mano sería una decisión editorial
  visible, eliminna se sabría del tema del artículo.
