window.__epb = {};
(function(){
  'use strict';
  var LIGHT = {"bg":"#f4f4f8","surface":"#ffffff","text":"#1f2230","muted":"#676b7e","border":"#e6e7ef","accent":"#5f58d8","soft":"#ebe9ff","grid":"rgba(31,34,48,0.06)","warm":"#956100","cyan":"#0f4ea5"};
  var DARK = {"bg":"#090b14","surface":"#0b0d17","text":"#e8ebf7","muted":"#9ea5bf","border":"#1f2437","accent":"#7b70ff","soft":"#251d53","grid":"rgba(232,235,251,0.07)","warm":"#ffd272","cyan":"#55d6ff"};
  function tok(t){ return (t==='dark') ? DARK : LIGHT; }
  function axes(c){
    return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
             tickfont:{color:c.muted,size:11}, automargin:true };
  }
  function lay(c){
    return { paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
      font:{color:c.text, family:"-\u002dapple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial"},
      xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
      hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
        font:{color:c.text, size:12}} };
  }

function tok(t){ return (t==='dark') ? DARK : LIGHT; }
function axes(c){
  return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
           tickfont:{color:c.muted,size:11}, automargin:true };
}
function lay(c){
  return { paper_bgcolor:c.surface, plot_bgcolor:c.surface,
    font:{color:c.text},
    xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
    hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
      font:{color:c.text, size:12}} };
}

window.__epb['f1'] = function(d, tname, chartEl){
  var c = tok(tname);
  var colors = { h:c.accent, b:c.warm, u:c.muted };
  var names = { h:'Actores con cuenta (no bots)', b:'Bots declarados', u:'Sin cuenta vinculada' };
  var show = { h:[true,true,true,true], b:[true,true,true,true], u:[true,true,true,true] };
  var traces = ['h','b','u'].map(function(k){
    var my = d.rows.filter(function(r){ return r.k===k; });
    return { type:'bar', orientation:'h', name:names[k],
      x:my.map(function(r){ return r.n; }),
      y:my.map(function(r){ return r.label; }),
      marker:{color:colors[k]},
      customdata:my.map(function(r){ return [r.total, r.humans, r.bots, r.unatt]; }),
      hovertemplate:'%{y}<br>%{x} eventos (' + names[k] + ')<br>' +
        'Total del flujo: %{customdata[0]}<br>' +
        'Con cuenta: %{customdata[1]} - Bots: %{customdata[2]} - Sin cuenta: %{customdata[3]}' +
        '<extra></extra>' };
  });
  var L = lay(c);
  L.barmode='stack';
  L.yaxis.autorange='reversed';
  L.legend={orientation:'h', font:{color:c.muted, size:11}, traceorder:'normal'};
  return Plotly.react(chartEl, traces, L, {displayModeBar:false, responsive:true});
};


function tok(t){ return (t==='dark') ? DARK : LIGHT; }
function axes(c){
  return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
           tickfont:{color:c.muted,size:11}, automargin:true };
}
function lay(c){
  return { paper_bgcolor:c.surface, plot_bgcolor:c.surface,
    font:{color:c.text},
    xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
    hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
      font:{color:c.text, size:12}} };
}

window.__epb['f2'] = function(d, tname, chartEl){
  var c = tok(tname);
  var names = { h:'Con cuenta (no bots)', b:'Bots declarados', u:'Sin cuenta vinculada' };
  var traces = ['h','b','u'].map(function(k, ki){
    var my = d.rows.filter(function(r){ return r.k===k; });
    return { type:'bar', orientation:'h', name:names[k],
      x:my.map(function(r){ return r.n; }),
      y:my.map(function(r){ return r.repo; }),
      marker:{color:(k==='h'?c.accent:(k==='b'?c.warm:c.muted))},
      customdata: my.map(function(r){ return [r.humans, r.bots, r.unatt,
                                              r.prs, r.prs_bots, r.rel, r.rel_bots]; }),
      hovertemplate:'<b>%{y}</b><br>' + names[k] + ': %{x} commits no-fusion' +
        '<br>Commits con cuenta: %{customdata[0]} - Bots: %{customdata[1]} - Sin cuenta: %{customdata[2]}' +
        '<br>PR fusionados en 12m: %{customdata[3]} (bots: %{customdata[4]})' +
        '<br>Releases 12m: %{customdata[5]} (bots: %{customdata[6]})<extra></extra>' };
  });
  var L = lay(c);
  L.barmode='stack';
  L.yaxis.autorange='reversed';
  L.xaxis.title={text:'commits no-fusion en la ventana de 12 meses (eventos)', font:{color:c.muted, size:11}};
  L.legend={orientation:'h', font:{color:c.muted, size:11}};
  return Plotly.react(chartEl, traces, L, {displayModeBar:false, responsive:true});
};


function tok(t){ return (t==='dark') ? DARK : LIGHT; }
function axes(c){
  return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
           tickfont:{color:c.muted,size:11}, automargin:true };
}
function lay(c){
  return { paper_bgcolor:c.surface, plot_bgcolor:c.surface,
    font:{color:c.text},
    xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
    hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
      font:{color:c.text, size:12}} };
}

window.__epb['f3'] = function(d, tname, chartEl){
  var c = tok(tname);
  function build(wname, vis){
    var rows = d.rows.filter(function(r){ return r.window===wname; });
    return { type:'scatter', mode:'markers+text', x:[], y:[], text:[],
             textposition:'top center', textfont:{size:10, color:c.muted},
             marker:{size:9, color:c.accent, line:{color:c.border,width:1}},
             name:wname, visible:vis,
             hovertemplate:'<b>%{text}</b> (' + wname + ')' +
               '<br>Cuota commits: %{x}' +
               '<br>Cuota PR fusionados: %{y}' +
               '<br>%{customdata}<extra></extra>',
             customdata: rows.map(function(r){ return r.tip; }),
             x: rows.map(function(r){ return r.c_commit; }),
             y: rows.map(function(r){ return r.c_pr; }),
             text: rows.map(function(r){ return r.repo_label; }) };
  }
  var traces = [build('12m', true), build('24m', false)];
  var L = lay(c);
  L.shapes = [{ type:'line', x0:0, x1:1, y0:0, y1:1, line:{color:c.border, width:1} }].concat(
    [0.5, 0.75].map(function(v){ return { type:'line', x0:v, x1:v, y0:0, y1:1.02, yref:'paper',
      line:{color:c.muted, width:1, dash:'dot'} }; }));
  L.xaxis.range=[0,1.02]; L.yaxis.range=[0,1.02];
  L.xaxis.title={text:'cuota top-1 por commits no-fusion (0-1)', font:{color:c.muted,size:11}};
  L.yaxis.title={text:'cuota top-1 por PR fusionados a rama principal (0-1)', font:{color:c.muted,size:11}};
  L.showlegend=false;
  L.updatemenus=[{ type:'buttons', direction:'right', x:0, y:1.12, xanchor:'left', yanchor:'top',
    bgcolor:c.surface, bordercolor:c.border, font:{color:c.text, size:11},
    active:0, activebgcolor:c.accent, activecolor:'#ffffff',
    buttons:[
      { label:'12 meses', method:'restyle', args:[['visible','visible'],[true, false]] },
      { label:'24 meses', method:'restyle', args:[['visible','visible'],[false, true]] }
    ]}];
  L.annotations=[{x:0.94, y:0.06, xref:'x', yref:'y', text:'misma cuota', showarrow:false,
    font:{color:c.muted, size:10}}];
  return Plotly.react(chartEl, traces, L, {displayModeBar:false, responsive:true});
};


function tok(t){ return (t==='dark') ? DARK : LIGHT; }
function axes(c){
  return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
           tickfont:{color:c.muted,size:11}, automargin:true };
}
function lay(c){
  return { paper_bgcolor:c.surface, plot_bgcolor:c.surface,
    font:{color:c.text},
    xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
    hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
      font:{color:c.text, size:12}} };
}

window.__epb['f4'] = function(d, tname, chartEl){
  var c = tok(tname);
  var traces = d.repos.map(function(rp, i){
    var y12 = d.series[rp]['12m'], y24 = d.series[rp]['24m'];
    var over = (y12 > 0.5 && y24 > 0.5);
    return { type:'scatter', mode:'lines+markers', x:[0, 1], y:[y12, y24],
      name:rp, showlegend:false,
      line:{width: over ? 2 : 1.2, color:c.accent, opacity: over ? 0.85 : 0.4},
      marker:{size:6, color:c.accent},
      hovertemplate:'<b>' + rp + '</b><br>' +
        '12m: ' + y12 + ' | 24m: ' + y24 + '<extra></extra>' };
  });
  var L = lay(c);
  L.shapes = [0.5, 0.75].map(function(v){ return { type:'line', x0:0, x1:1, y0:v, y1:v,
    yref:'paper', line:{color:c.muted, width:1, dash:'dot'} }; });
  L.xaxis.range=[-0.15,1.15]; L.xaxis.tickvals=[0,1]; L.xaxis.ticktext=['12 meses','24 meses'];
  L.xaxis.title={text:'ventana', font:{color:c.muted, size:11}};
  L.yaxis.title={text:'cuota top-1 por commits no-fusion (0-1)', font:{color:c.muted, size:11}};
  L.showlegend=false;
  return Plotly.react(chartEl, traces, L, {displayModeBar:false, responsive:true});
};


function tok(t){ return (t==='dark') ? DARK : LIGHT; }
function axes(c){
  return { gridcolor:c.grid, zerolinecolor:c.grid, linecolor:c.border,
           tickfont:{color:c.muted,size:11}, automargin:true };
}
function lay(c){
  return { paper_bgcolor:c.surface, plot_bgcolor:c.surface,
    font:{color:c.text},
    xaxis:axes(c), yaxis:axes(c), margin:{t:8,r:10,b:4,l:10},
    hoverlabel:{bgcolor:c.surface, bordercolor:c.border,
      font:{color:c.text, size:12}} };
}

window.__epb['f5'] = function(d, tname, chartEl){
  var c = tok(tname);
  var names = { h:'Con cuenta (no bots)', b:'Bots declarados', u:'Sin cuenta vinculada' };
  var traces = ['b','h','u'].map(function(k){
    var my = d.rows.filter(function(r){ return r.k===k; });
    return { type:'bar', orientation:'h', name:names[k],
      x: my.map(function(r){ return k==='b' ? r.bot_share :
          (k==='h' ? r.humans_share : r.unatt_share); }),
      y: my.map(function(r){ return r.label; }),
      marker:{color:(k==='b'?c.warm:(k==='h'?c.accent:c.muted))},
      customdata: my.map(function(r){ return [r.total, r.bots, r.humans, r.unatt]; }),
      hovertemplate:'%{y}<br>' + names[k] + ': %{x}% de eventos' +
        '<br>Totales: %{customdata[0]} eventos; bots %{customdata[1]}; ' +
        'con cuenta %{customdata[2]}; sin cuenta %{customdata[3]}<extra></extra>' };
  });
  var L = lay(c);
  L.barmode='stack'; L.bargap=0.35;
  L.xaxis.range=[0,100];
  L.xaxis.ticksuffix='%';
  L.xaxis.title={text:'porcentaje de los eventos del flujo', font:{color:c.muted, size:11}};
  L.legend={orientation:'h', font:{color:c.muted, size:11}};
  return Plotly.react(chartEl, traces, L, {displayModeBar:false, responsive:true});
};

}());