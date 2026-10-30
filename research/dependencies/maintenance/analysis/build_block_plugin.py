#!/usr/bin/env python3
"""Build the WordPress block plugin 'econopapi-plotly' from the step-5 figures.

Reads analysis/results/figure-meta.json + the figure builder code defined in
make_figures.py and writes a self-contained plugin under
analysis/wp-block-plugin/econopapi-plotly/ plus a zip ready for upload:

  - dynamic block econopapi/plotly-figure (attribute: figure)
  - server side renders kicker/title/subtitle/footer + accessible table + noscript
  - client renders the chart into a per-instance container (unique ids)
  - plotly.min.js from the pinned CDN; fonts and definitions bundled locally
  - light/dark via prefers-color-scheme + site dark markers (html.dark / data-theme)

Role of this plugin: NOT to replace GraphDraw (the static graph block stays);
it only renders the step-5 Plotly figures as native Gutenberg blocks.
"""

import json
import textwrap
import zipfile
from pathlib import Path

import make_figures

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PLUGIN_DIR = HERE / "wp-block-plugin" / "econopapi-plotly"
FONTS = Path("/tmp/opencode/fonts")

BUILDER_MAP = {1: "f1", 2: "f2", 3: "f3", 4: "f4", 5: "f5"}


def builder_sources():
    return {
        BUILDER_MAP[n]: getattr(make_figures, f"JS_F{n}")
        for n in (1, 2, 3, 4, 5)
    }


def defs_js(meta):
    defs = {}
    for m in meta:
        key = BUILDER_MAP[int(m["id"][3])]
        defs[m["id"]] = {
            "builder": key,
            "title": m["title"], "kicker": m["kicker"],
            "subtitle": m["subtitle"], "alt": m["alt"],
            "provenance_extra": m["provenance_extra"],
            "table_head": m["table_head"], "table_body": m["table_body"],
            "data": m["data"],
        }
    return "window.ECONOPAPI_PLOTLY_DEFS = " + json.dumps(
        defs, ensure_ascii=False, separators=(",", ":")) + ";"


RENDER_JS = textwrap.dedent("""\
(function(){
  'use strict';
  function theme(){
    var h = document.documentElement;
    if (h.dataset.theme==='dark' || h.classList.contains('dark')) return 'dark';
    if (h.dataset.theme==='light') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function paint(){
    var t = theme();
    document.querySelectorAll('.econopapi-plotly[data-figure]').forEach(function(sec){
      if (sec.dataset.rendered === t) return;
      var defs = window.ECONOPAPI_PLOTLY_DEFS || {};
      var def = defs[sec.dataset.figure];
      var el = sec.querySelector('.econ-chart');
      if (!def || !el || typeof window.__epb[def.builder] !== 'function') return;
      sec.dataset.rendered = String(t);
      try { window.__epb[def.builder](def.data, t, el); } catch (e) {
        sec.classList.add('econopapi-plotly-error');
        el.textContent = 'La grafica no pudo renderizarse: ' + e.message;
      }
    });
  }
  function boot(){
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', paint);
    } else { paint(); }
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) { mq.addEventListener('change', paint); }
    else if (mq.addListener) { mq.addListener(paint); }
    var obs = new MutationObserver(paint);
    obs.observe(document.documentElement, { attributes: true,
      attributeFilter: ['data-theme', 'class'] });
  }
  boot();
})();
""")


STYLE_CSS = textwrap.dedent("""\
@font-face { font-family:'Montserrat'; src:url('fonts/Montserrat-Bold-sub.otf') format('opentype');
  font-weight:700; font-style:normal; font-display:swap; }
@font-face { font-family:'Source Sans Pro'; src:url('fonts/SourceSansPro-Regular-sub.otf') format('opentype');
  font-weight:400; font-style:normal; font-display:swap; }
@font-face { font-family:'Source Sans Pro'; src:url('fonts/SourceSansPro-Bold-sub.otf') format('opentype');
  font-weight:700; font-style:normal; font-display:swap; }
.econopapi-plotly { color-scheme: light dark;
  --bg:#f4f4f8; --surface:#ffffff; --text:#1f2230; --muted:#676b7e;
  --border:#e6e7ef; --accent:#5f58d8; --soft:#ebe9ff; --grid:rgba(31,34,48,0.08); }
@media (prefers-color-scheme: dark) {
  html.dark .econopapi-plotly, html[data-theme="dark"] .econopapi-plotly,
  .econopapi-plotly[data-theme="dark"] {
    --bg:#090b14; --surface:#0b0d17; --text:#e8ebf7; --muted:#9ea5bf;
    --border:#1f2437; --accent:#7b70ff; --soft:#251d53; --grid:rgba(232,235,251,0.07); } }
@media (prefers-color-scheme: light) {
  .econopapi-plotly { --bg:#f4f4f8; --surface:#ffffff; --text:#1f2230; --muted:#676b7e;
    --border:#e6e7ef; --accent:#5f58d8; --soft:#ebe9ff; --grid:rgba(31,34,48,0.08); } }
html.dark .econopapi-plotly, html[data-theme="dark"] .econopapi-plotly,
.econopapi-plotly[data-theme="dark"] { --bg:#090b14; --surface:#0b0d17; --text:#e8ebf7;
  --muted:#9ea5bf; --border:#1f2437; --accent:#7b70ff; --soft:#251d53;
  --grid:rgba(232,235,251,0.07); }
.econopapi-plotly { margin:2rem 0; padding:18px; background:var(--bg);
  color:var(--text); border:1px solid var(--border); border-radius:16px;
  font-family:"Source Sans Pro", -apple-system, BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  font-size:14px; line-height:1.5; max-width:1080px; margin-inline:auto; }
.econopapi-plotly .figu { display:flex; flex-wrap:wrap; gap:8px; align-items:baseline; }
.econopapi-plotly .figkicker { font-size:11px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--accent); font-weight:700; }
.econopapi-plotly h2.figu-title { font-family:"Montserrat","Source Sans Pro",sans-serif;
  font-size:19px; margin:0; line-height:1.2; letter-spacing:-.025em; }
.econopapi-plotly .accent-dot { color:var(--accent); }
.econopapi-plotly .figu-sub { font-size:12.5px; color:var(--muted); margin:6px 0 10px; line-height:1.45; }
.econopapi-plotly .enu { border:1px solid var(--border); background:var(--surface);
  border-radius:.4rem; padding:8px 4px 2px; margin:0; }
.econopapi-plotly .enu > div { width:100%; height:100%; }
.econopapi-plotly .figu-footer { font-size:11px; color:var(--muted); margin-top:10px;
  border-top:1px solid var(--border); padding-top:8px; line-height:1.55; }
.econopapi-plotly .figu-footer strong { color:var(--text); }
.econopapi-plotly .figu-footer a { color:var(--accent); border-bottom:1px solid var(--border);
  text-decoration:none; }
.econopapi-plotly details.datatables { margin-top:10px; font-size:12px; }
.econopapi-plotly details.datatables summary { cursor:pointer; color:var(--muted); }
.econopapi-plotly table.data { border-collapse:collapse; width:100%; margin:6px 0; }
.econopapi-plotly table.data th, .econopapi-plotly table.data td {
  border:1px solid var(--border); padding:4px 7px; text-align:left;
  font-variant-numeric:tabular-nums; }
.econopapi-plotly table.data th { background:var(--soft); color:var(--muted);
  font-size:11px; font-weight:600; }
.econopapi-plotly-error .econ-chart { border:1px dashed var(--border); color:var(--muted);
  padding:18px; font-size:12px; }
@media (max-width:640px){ .econopapi-plotly { padding:12px; } h2.figu-title { font-size:16px; }
  .econopapi-plotly { overflow-x:hidden; } }
""")


PHP_PLUGIN = textwrap.dedent(r'''
<?php
/**
 * Plugin Name: Econopapi Plotly Charts
 * Description: Bloque dinámico econopapi/plotly-figure para las figuras interactivas del paso 5 (caso DeudaMundi). El bloque guarda solo la elección de figura; el render y los datos viven en el plugin, y las fuentes/Plotly se encolan una sola vez por página. No modifie el bloque GraphDraw ni el plugin viejo wp-plotly.
 * Version: 0.1.0
 * Author: Daniel Limón — Econopapi
 * Text Domain: econopapi-plotly
 */
defined('ABSPATH') || exit;

define('ECONOPAPI_PLOTLY_VERSION', '0.1.0');
define('ECONOPAPI_PLOTLY_PLOTLY_URL', 'https://cdn.plot.ly/plotly-2.35.2.min.js'); /* filterable */

require_once __DIR__ . '/assets/defs-meta.php';

function econopapi_plotly_assets(): void {
    wp_register_script('plotly-2-35-2', apply_filters('econopapi_plotly_script_url', ECONOPAPI_PLOTLY_PLOTLY_URL), array(), '2.35.2', true);
    wp_register_script('econopapi-plotly-defs', plugins_url('assets/definitions.js', __FILE__), array(), ECONOPAPI_PLOTLY_VERSION, true);
    wp_register_script('econopapi-plotly-builders', plugins_url('assets/builders.js', __FILE__), array(), ECONOPAPI_PLOTLY_VERSION, true);
    wp_register_script('econopapi-plotly-render', plugins_url('assets/render.js', __FILE__), array('plotly-2-35-2', 'econopapi-plotly-defs', 'econopapi-plotly-builders'), ECONOPAPI_PLOTLY_VERSION, true);
    wp_register_style('econopapi-plotly-style', plugins_url('assets/style.css', __FILE__), array(), ECONOPAPI_PLOTLY_VERSION);
}
add_action('init', 'econopapi_plotly_assets');

function econopapi_plotly_editor_assets(): void {
    wp_register_script('econopapi-plotly-editor', plugins_url('assets/editor.js', __FILE__), array('wp-blocks', 'wp-block-editor', 'wp-components', 'wp-element', 'wp-server-side-render', 'wp-i18n'), ECONOPAPI_PLOTLY_VERSION, true);
    wp_register_style('econopapi-plotly-editor-style', plugins_url('assets/style.css', __FILE__), array(), ECONOPAPI_PLOTLY_VERSION);
    wp_enqueue_script('econopapi-plotly-editor');
    wp_enqueue_style('econopapi-plotly-editor-style');
}
add_action('enqueue_block_editor_assets', 'econopapi_plotly_editor_assets');

function econopapi_plotly_render(array $attributes = array()): string {
    $figure = isset($attributes['figure']) ? (string) $attributes['figure'] : 'fig1';
    $defs = econopapi_plotly_defs();
    if (!isset($defs[$figure])) { return ''; }
    $d = $defs[$figure];
    $uid = 'econopapi-plotly-' . esc_attr($figure) . '-' . wp_unique_id();
    wp_enqueue_script('plotly-2-35-2');
    wp_enqueue_script('econopapi-plotly-defs');
    wp_enqueue_script('econopapi-plotly-builders');
    wp_enqueue_script('econopapi-plotly-render');
    wp_enqueue_style('econopapi-plotly-style');

    ob_start(); ?>
<section class="econopapi-plotly" id="<?php echo esc_attr($uid); ?>" data-figure="<?php echo esc_attr($figure); ?>" role="figure" aria-label="<?php echo esc_attr(wp_strip_all_tags($d['alt'])); ?>">
  <div class="figu">
    <div class="figkicker"><?php echo esc_html($d['kicker']); ?></div>
    <h2 class="figu-title"><?php echo esc_html($d['title']); ?><span class="accent-dot">.</span></h2>
  </div>
  <p class="figu-sub"><?php echo wp_kses_post($d['subtitle']); ?></p>
  <div class="enu">
    <div class="econ-chart" data-figure="<?php echo esc_attr($figure); ?>" aria-hidden="false"></div>
  </div>
  <noscript>
    <p class="epi-note">El gráfico interactivo necesita JavaScript; abajo queda la tabla accesible equivalente.</p>
  </noscript>
  <figcaption class="figu-footer">
    <strong>Fuente:</strong> extracción congelada del 30-10-2026 (<a href="https://github.com/econopapi/DeudaMundi/commit/1363af84d5089ca4260645012dcb34ccc93d4c6c">commit 1363af84</a> · <a href="https://github.com/econopapi/DeudaMundi/tree/research/deudamundi-dependencies/research/dependencies/maintenance/analysis">plan preregistrado del paso 5</a>).
    <?php echo wp_kses_post($d['provenance_extra']); ?> Unidad: eventos públicos observados; los cuatro flujos no se suman entre sí.
    <strong>La figura correspondiente a la ventana congelada del 30-10-2026; los números de la rama de investigación son la evidencia.</strong>
  </figcaption>
  <details class="datatables">
    <summary>Tabla de datos (accesible)</summary>
    <table class="data">
      <thead><tr><?php echo wp_kses_post($d['table_head']); ?></tr></thead>
      <tbody><?php echo wp_kses_post($d['table_body']); ?></tbody>
    </table>
  </details>
</section>
<?php
    return (string) ob_get_clean();
}

add_action('init', function (): void {
    register_block_type('econopapi/plotly-figure', array(
        'api_version'        => 2,
        'title'              => 'Econopapi Plotly Figure',
        'category'           => 'media',
        'attributes'         => array('figure' => array('type' => 'string', 'default' => 'fig1')),
        'render_callback'    => 'econopapi_plotly_render',
        'editor_script_handles' => array('econopapi-plotly-editor'),
        'editor_style_handles'  => array('econopapi-plotly-editor-style'),
    ));
});
''')


EDITOR_JS = textwrap.dedent(r"""
(function (wp) {
  var el = wp.element.createElement;
  var registerBlockType = wp.blocks.registerBlockType;
  var SSR = wp.serverSideRender;
  var Select = wp.components.SelectControl;
  var InspectorControls = wp.blockEditor.InspectorControls;
  var PanelBody = wp.components.PanelBody;
  registerBlockType('econopapi/plotly-figure', {
    title: 'Econopapi Plotly Figure',
    icon: 'chart-bar',
    category: 'media',
    supports: { html: false },
    attributes: { figure: { type: 'string', default: 'fig1' } },
    edit: function (props) {
      return el(wp.element.Fragment, {},
        el(InspectorControls, {},
          el(PanelBody, { title: 'Figura del paso 5', initialOpen: true },
            el(Select, {
              label: 'Figura',
              value: props.attributes.figure,
              onChange: function (v) { props.setAttributes({ figure: v }); },
              options: [
                { value: 'fig1', label: 'fig1 — Actividad por tipo de evento y ventana' },
                { value: 'fig2', label: 'fig2 — Actividad por repositorio (commits/bots)' },
                { value: 'fig3', label: 'fig3 — Cuota top-1: commits vs PR fusionados' },
                { value: 'fig4', label: 'fig4 — Sensibilidad 12 / 24 meses' },
                { value: 'fig5', label: 'fig5 — Participación de bots por flujo' },
              ],
            }))),
        el('div', { className: 'econopapi-plotly-edit' },
          el(wp.serverSideRender, {
            block: 'econopapi/plotly-figure',
            attributes: { figure: props.attributes.figure },
          })));
    },
    save: function () { return null; },
  });
})(window.wp);
""")


DEFS_META_PHP_TEMPLATE = r'''<?php
/** Generado por build_block_plugin.py desde los artefactos del paso 5. */
defined('ABSPATH') || exit;

function econopapi_plotly_defs(): array {
    return {defs};
}
'''


def main():
    meta = json.loads((RESULTS / "figure-meta.json").read_text(encoding="utf-8"))
    assets = PLUGIN_DIR / "assets"
    fonts = PLUGIN_DIR / "assets" / "fonts"
    for p in (assets, fonts):
        p.mkdir(parents=True, exist_ok=True)
    # PHP (no leading whitespace: anything before <?php is output at activation)
    php_code = PHP_PLUGIN.lstrip("\n")
    assert php_code.startswith("<?php"), "plugin PHP must start with the open tag"
    (PLUGIN_DIR / "econopapi-plotly.php").write_text(php_code, encoding="utf-8")
    defs_php = DEFS_META_PHP_TEMPLATE.replace("{defs}", _php_array(meta)).lstrip("\n")
    assert defs_php.startswith("<?php")
    (assets / "defs-meta.php").write_text(defs_php, encoding="utf-8")
    # JS
    (assets / "definitions.js").write_text(defs_js(meta), encoding="utf-8")
    srcs = builder_sources()
    light = json.dumps(make_figures.T["light"], separators=(",", ":"))
    dark = json.dumps(make_figures.T["dark"], separators=(",", ":"))
    head = textwrap.dedent(f"""\
    window.__epb = {{}};
    (function(){{
      'use strict';
      var LIGHT = {light};
      var DARK = {dark};
      function tok(t){{ return (t==='dark') ? DARK : LIGHT; }}
      function axes(c){{
        return {{ gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
                 tickfont:{{color:c.muted,size:11}}, automargin:true }};
      }}
      function lay(c){{
        return {{ paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
          font:{{color:c.text, family:"-\\u002dapple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial"}},
          xaxis:axes(c), yaxis:axes(c), margin:{{t:8,r:10,b:4,l:10}},
          hoverlabel:{{bgcolor:c.surface, bordercolor:c.border,
            font:{{color:c.text, size:12}}}} }};
      }}
    """)
    body = []
    for key, code in srcs.items():
        adapted = code.replace(
            "window.__build = function(d, tname){",
            "window.__epb['" + key + "'] = function(d, tname, chartEl){", 1)
        adapted = adapted.replace("Plotly.react('chart',", "Plotly.react(chartEl,", 1)
        body.append(adapted)
    builders = head + "\n".join(body) + "\n}());"
    (assets / "builders.js").write_text(builders, encoding="utf-8")
    (assets / "render.js").write_text(RENDER_JS, encoding="utf-8")
    (assets / "editor.js").write_text(EDITOR_JS, encoding="utf-8")
    (assets / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    # fonts
    for f in ("Montserrat-Bold-sub.otf", "SourceSansPro-Regular-sub.otf",
              "SourceSansPro-Bold-sub.otf"):
        (fonts / f).write_bytes((FONTS / f).read_bytes())
    for f in ("FONTS-LICENSE-Montserrat-OFL.txt", "FONTS-LICENSE-SourceSansPro-OFL.txt"):
        name = "LICENSE-" + f.split("FONTS-LICENSE-")[1]
        (fonts / name).write_text((HERE / "figures" / f).read_text(encoding="utf-8"),
                                  encoding="utf-8")
    # zip
    zpath = PLUGIN_DIR.parent / "econopapi-plotly.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(PLUGIN_DIR.rglob("*")):
            if p.is_file():
                z.write(p, "econopapi-plotly/" + str(p.relative_to(PLUGIN_DIR)))
    print("plugin build ok:", PLUGIN_DIR)
    print("zip:", zpath, zpath.stat().st_size, "bytes")


def _php_array(meta):
    import re
    items = []
    for m in meta:
        key = BUILDER_MAP[int(m["id"][3])]
        d = {
            "title": m["title"], "kicker": m["kicker"],
            "subtitle": m["subtitle"], "alt": m["alt"],
            "provenance_extra": m["provenance_extra"],
            "table_head": m["table_head"], "table_body": m["table_body"],
            "builder": key,
        }
        items.append("'" + m["id"] + "' => " + _php_export(d))
    return "array(\n    " + ",\n    ".join(items) + "\n)"


def _php_export(v):
    import re
    if isinstance(v, dict):
        inner = ", ".join("'" + k + "' => " + _php_export(x) for k, x in v.items())
        return "array(" + inner + ")"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    s = s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return "'" + s + "'"


if __name__ == "__main__":
    main()
