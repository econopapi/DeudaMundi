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
