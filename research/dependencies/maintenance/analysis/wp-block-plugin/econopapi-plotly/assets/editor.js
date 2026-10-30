
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
