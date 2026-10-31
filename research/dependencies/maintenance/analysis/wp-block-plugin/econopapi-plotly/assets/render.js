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
      sec.__token = (sec.__token || 0) + 1;
      var token = sec.__token;
      var ok = function(){
        if (token !== sec.__token) return;
        sec.dataset.rendered = String(t);
      };
      var fail = function(msg){
        if (token !== sec.__token) return;
        sec.dataset.rendered = '';
        sec.classList.add('econopapi-plotly-error');
        el.textContent = 'El gráfico interactivo no pudo renderizarse (' + msg + '). ' +
          'La tabla de datos accesible, más abajo, conserva los valores.';
      };
      if (!def || !el) { fail('figura desconocida'); return; }
      if (!window.__epb || typeof window.__epb[def.builder] !== 'function') { fail('definiciones no cargadas'); return; }
      sec.dataset.rendered = 'pending';
      sec.classList.remove('econopapi-plotly-error');
      try {
        if (!window.Plotly) { fail('Plotly no cargó; revisa la conexión o el filtro del CDN'); return; }
        var result = window.__epb[def.builder](def.data, t, el);
        if (result && typeof result.then === 'function') {
          result.then(ok, function(e){ fail(e && (e.message || e)); });
        } else { ok(); }
      } catch (e) { fail(e && (e.message || e)); }
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
