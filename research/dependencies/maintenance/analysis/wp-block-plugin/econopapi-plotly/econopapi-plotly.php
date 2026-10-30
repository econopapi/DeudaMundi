
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
