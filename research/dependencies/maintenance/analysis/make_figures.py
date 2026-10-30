#!/usr/bin/env python3
"""Build the step-5 interactive figures (Plotly, self-contained HTML).

Reads results/repo-metrics.csv, results/overview-totals.json,
results/hypotheses.json, results/h3-test.csv and results/distribution-map.csv
(produced by analyze_activity.py) and writes:

  figures/figN-*.html                 five self-contained interactive figures
  figures/figN-data.json              the exact data each figure plots
  wp-snippets/figN-gutenberg.html     WordPress paste-ready custom HTML (iframe)
  wp-snippets/README.txt              the embedding procedure to test first

Visual identity: Econopapi design tokens (light/dark), singular page variant,
reconstructed 2026-10-23 (kit v0.4). Rules: unidades, ventanas y denominadores
visibles; texto en espanol; cada figura lleva tabla accesible y texto
alternativo; la procedencia fechada se imprime en la pagina.
"""

import base64
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGS = HERE / "figures"
WP = HERE / "wp-snippets"

PLOTLY_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"
GENERATED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
BRANCH_REF = "research/deudamundi-dependencies"

# Econopapi tokens: manual oficial en
# /home/econopapi/Projects/econopapi-video-studio/docs/brand/ECONOPAPI_BRAND_KIT_LIGHT_DARK_v04/
# (guía HTML v0.4; variante singular para piezas dentro de artículos del blog:
# dark #070b17 con acento #6d65ff; núcleo light #5f58d8). Gris de estado (warm)
# = status-dev-text #956100/#ffd272; cian = profile-accent-secondary.
T = {
    "light": {"bg": "#f4f4f8", "surface": "#ffffff", "text": "#1f2230",
              "muted": "#676b7e", "border": "#e6e7ef", "accent": "#5f58d8",
              "soft": "#ebe9ff", "grid": "rgba(31,34,48,0.06)",
              "warm": "#956100", "cyan": "#0f4ea5"},
    "dark": {"bg": "#090b14", "surface": "#0b0d17", "text": "#e8ebf7",
             "muted": "#9ea5bf", "border": "#1f2437", "accent": "#7b70ff",
             "soft": "#251d53", "grid": "rgba(232,235,251,0.07)",
             "warm": "#ffd272", "cyan": "#55d6ff"},
}
PAGE_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body.figpage { margin:0; padding:16px; background:var(--bg); color:var(--text);
  font-family:"Source Sans Pro",-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
  font-size:14px; line-height:1.5; }
figure.fig { margin:0; max-width:1080px; }
.figu { display:flex; flex-wrap:wrap; gap:8px; align-items:baseline; margin-bottom:4px; }
.figkicker { font-size:11px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--accent); font-weight:700; }
h2.figu-title { font-family:"Montserrat","Source Sans Pro",sans-serif;
  font-size:19px; margin:0; line-height:1.2; letter-spacing:-.025em; }
.accent-dot { color:var(--accent); }
.figu-sub { font-size:12.5px; color:var(--muted); margin:6px 0 10px; line-height:1.45; }
.figu-sub code { font-family:Menlo,Consolas,Monaco,monospace; font-size:11px; }
.figu-footer { font-size:11px; color:var(--muted); margin-top:10px;
  border-top:1px solid var(--border); padding-top:8px; line-height:1.55; }
.figu-footer strong { color:var(--text); }
.figu-footer a { color:var(--accent); text-decoration:none; border-bottom:1px solid var(--border); }
.theme-toggle { font:inherit; font-size:11px; margin-left:auto; align-self:center;
  padding:3px 9px; border:1px solid var(--border); background:var(--surface);
  color:var(--muted); border-radius:6px; cursor:pointer; }
.chartwrap { background:var(--surface); border:1px solid var(--border);
  border-radius:16px; padding:6px 4px 2px; }
details.datatables { margin-top:10px; font-size:12px; }
details.datatables summary { cursor:pointer; color:var(--muted); font-size:12px; }
table.data { border-collapse:collapse; width:100%; margin-top:6px; }
table.data th, table.data td { border:1px solid var(--border); padding:4px 7px;
  text-align:left; font-variant-numeric:tabular-nums; }
table.data th { background:var(--soft); color:var(--muted);
  font-size:11px; font-weight:600; }
@media (max-width:640px){ body.figpage{padding:10px;} h2.figu-title{font-size:16px;}
  html,body{overflow-x:hidden;} }
"""
PAGE_JS = """
(function(){
  var root=document.documentElement;
  var btn=document.getElementById('themeBtn');
  function theme(){
    if(root.dataset.theme==='dark') return 'dark';
    if(root.dataset.theme==='light') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  }
  function apply(){
    var t=theme();
    root.dataset.theme=t;
    window.__build(window.__chartData, t);
  }
  if(btn){ btn.addEventListener('click', function(){
    var cur=theme(); root.dataset.theme = (cur==='dark')?'light':'dark'; apply(); }); }
  var mq=window.matchMedia('(prefers-color-scheme: dark)');
  if(mq.addEventListener){ mq.addEventListener('change', apply); }
  else if(mq.addListener){ mq.addListener(apply); }
  apply();
})();
"""


TEMPLATE = """<!doctype html>
<html lang="es" data-theme="">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="{plotly_url}"></script>
{font_css}
<style>
:root {{ --bg:{tlight[bg]}; --surface:{tlight[surface]}; --text:{tlight[text]};
        --muted:{tlight[muted]}; --border:{tlight[border]}; --accent:{tlight[accent]};
        --soft:{tlight[soft]}; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:{tdark[bg]}; --surface:{tdark[surface]};
          --text:{tdark[text]}; --muted:{tdark[muted]}; --border:{tdark[border]};
          --accent:{tdark[accent]}; --soft:{tdark[soft]}; }}
}}
html[data-theme="dark"] {{ --bg:{tdark[bg]}; --surface:{tdark[surface]};
  --text:{tdark[text]}; --muted:{tdark[muted]}; --border:{tdark[border]};
  --accent:{tdark[accent]}; --soft:{tdark[soft]}; }}
html[data-theme="light"] {{ --bg:{tlight[bg]}; --surface:{tlight[surface]};
  --text:{tlight[text]}; --muted:{tlight[muted]}; --border:{tlight[border]};
  --accent:{tlight[accent]}; --soft:{tlight[soft]}; }}
{page_css}
</style>
</head>
<body class="figpage" data-provenance="{generated}">
<figure class="fig">
  <div class="figu">
    <div class="figkicker">{kicker}</div>
    <h2 class="figu-title">{title}<span class="accent-dot">.</span></h2>
    <button class="theme-toggle" id="themeBtn" type="button"
      aria-label="Cambiar entre modo claro y oscuro">claro/oscuro</button>
  </div>
  <p class="figu-sub">{subtitle}</p>
  <div class="chartwrap" role="img" aria-label="{alt}">
    <div id="chart" style="width:100%;height:{height}px;"></div>
  </div>
  <figcaption class="figu-footer">
    <strong>Fuente:</strong> extracción congelada del 30-10-2026
    (<a href="https://github.com/econopapi/DeudaMundi/commit/1363af84d5089ca4260645012dcb34ccc93d4c6c">commit 1363af84</a> ·
    <a href="https://github.com/econopapi/DeudaMundi/tree/{branch}/research/dependencies/maintenance/analysis">plan preregistrado del paso 5</a>).
    {provenance_extra} Figura generada {generated}. Unidad: eventos públicos observados; los cuatro flujos no se suman entre sí.
  </figcaption>
  <details class="datatables">
    <summary>Tabla de datos (accesible)</summary>
    <table class="data">
      <thead><tr>{table_head}</tr></thead>
      <tbody>{table_body}</tbody>
    </table>
  </details>
</figure>
<script>
const LIGHT = {light_json};
const DARK = {dark_json};
</script>
<script>
window.__chartData = {data_json};
{builder}
</script>
<script>{page_js}</script>
</body>
</html>
"""


FONT_DIR = Path("/tmp/opencode/fonts")


def font_and_css(html):
    """Extract the two <style> blocks (fonts + page CSS) from a full page."""
    styles = re.findall(r"<style>.*?</style>", html, re.S)
    return "\n".join(styles)


def scope_for_wp(fragment):
    """WP-scoped variant: CSS vars and body selectors anchored to .econofigw
    so the fragment works inside an article where there is no <body>. The
    fragment is wrapped in the scoped container explicitly (the original
    <body> tags do not survive the fragment extraction)."""
    s = fragment
    s = s.replace("body.figpage", ".econofigw")
    s = re.sub(r"(?<!\[)html\[data-theme", ".econofigw[data-theme", s)
    s = s.replace(":root { color-scheme: light dark; }",
                  ".econofigw { color-scheme: light dark; }")
    s = s.replace('<body class="figpage"', '<div class="econofigw"')
    s = s.replace("</body>", "</div>")
    if '<div class="econofigw"' not in s:
        s = ('<div class="econofigw">\n' + s.rstrip() + "\n</div>")
    return s


def font_css():
    """Base64 @font-face for the two brand families (subsets; OFL licenses
    kept in the brand kit; see figures/FONTS-NOTICE.txt)."""
    parts = []
    for fam, weight, fname in (
            ("Montserrat", 700, "Montserrat-Bold-sub.otf"),
            ("Source Sans Pro", 400, "SourceSansPro-Regular-sub.otf"),
            ("Source Sans Pro", 700, "SourceSansPro-Bold-sub.otf")):
        b64 = base64.b64encode((FONT_DIR / fname).read_bytes()).decode()
        parts.append(
            f"@font-face {{ font-family:'{fam}'; src:"
            f"data:font/opentype;base64,{b64} format('opentype');"
            f" font-weight:{weight}; font-style:normal; font-display:swap; }}")
    return "<style>" + "\n".join(parts) + "</style>"


def render(idx, slug, title, kicker, subtitle, alt, provenance_extra, height,
           data, builder_code, table_head, table_body):
    FIGS.mkdir(exist_ok=True)
    (FIGS / f"fig{idx}-data.json").write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    html = TEMPLATE.format(
        title=title, kicker=kicker, subtitle=subtitle, alt=alt,
        plotly_url=PLOTLY_URL, generated=GENERATED, branch=BRANCH_REF,
        provenance_extra=provenance_extra, height=height,
        font_css=font_css(),
        tlight=T["light"], tdark=T["dark"], page_css=PAGE_CSS, page_js=PAGE_JS,
        light_json=json.dumps(T["light"], separators=(",", ":")),
        dark_json=json.dumps(T["dark"], separators=(",", ":")),
        data_json=json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        builder=builder_code, table_head=table_head, table_body=table_body)
    (FIGS / f"fig{idx}-{slug}.html").write_text(html, encoding="utf-8")

    # WordPress fragment: everything a "Custom HTML" block may accept
    # (no <html>/<head>/<body>; styles + data + scripts inline).
    body = html.split("<body", 1)[1].split(">", 1)[1]
    body = body.rsplit("</body>", 1)[0]
    wpdir = HERE / "wp-snippets"
    wpdir.mkdir(exist_ok=True)
    fragment = ("<script src=\"" + PLOTLY_URL + "\"></script>\n"
                + font_and_css(html) + "\n" + body)
    (wpdir / f"fig{idx}-{slug}-fragmento-wp.html").write_text(
        fragment, encoding="utf-8")
    scoped = scope_for_wp(fragment)
    (wpdir / f"fig{idx}-{slug}-wp-scoped.html").write_text(
        scoped, encoding="utf-8")
    FIGURE_META.append({
        "id": f"fig{idx}", "slug": slug, "title": title, "kicker": kicker,
        "subtitle": subtitle, "alt": alt, "provenance_extra": provenance_extra,
        "table_head": table_head, "table_body": table_body,
        "data": json.loads((FIGS / f"fig{idx}-data.json").read_text(encoding="utf-8")),
    })
    print(f"fig{idx}: ok")


FIGURE_META = []


# --------------------------------------------------------------- data helpers

def overview():
    return json.loads((RESULTS / "overview-totals.json").read_text(encoding="utf-8"))


def pct(x):
    return round(100 * x, 1)


def load_csv(name):
    with (RESULTS / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def overview():
    return json.loads((RESULTS / "overview-totals.json").read_text(encoding="utf-8"))


def stream_rows(w):
    """(label, split dict) per stream for figures 1 and 5, from repo-metrics.csv."""
    rows = [r for r in load_csv("repo-metrics.csv") if r["window_end"] == w]
    def agg(k):
        return sum(int(r[k]) for r in rows)
    out = [
        ("Commits rama principal", {"events": agg("commits_all"),
                                    "bots": agg("commits_bot"),
                                    "unattributed": agg("commits_unattrib")}),
        ("PR fusionados (toda base)", {"events": agg("merged_prs_all"),
                                       "bots": agg("merged_prs_bot"),
                                       "unattributed": agg("merged_prs_unattrib")}),
        ("Revisiones de PR", {"events": agg("reviews_raw"),
                              "bots": agg("reviews_raw_bot"),
                              "unattributed": agg("reviews_raw_unattrib")}),
        ("Releases de GitHub", {"events": agg("releases_all"),
                                "bots": agg("releases_bot"),
                                "unattributed": agg("releases_unattrib")}),
    ]
    pairs = agg("review_pairs")
    return out, pairs


BASE_JS = """
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
"""

JS_F1 = BASE_JS + """
window.__build = function(d, tname){
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
  return Plotly.react('chart', traces, L, {displayModeBar:false, responsive:true});
};
"""


def fig1():
    data = {"rows": []}
    for w in ("12m", "24m"):
        rows, pairs = stream_rows(w)
        for label, s in rows:
            total = s["events"]
            bots, unatt = s["bots"], s["unattributed"]
            data["rows"] += [
                {"label": f"{label} · {w}", "k": "h", "n": total - bots - unatt,
                 "total": total, "humans": total - bots - unatt, "bots": bots, "unatt": unatt},
                {"label": f"{label} · {w}", "k": "b", "n": bots, "total": total,
                 "humans": total - bots - unatt, "bots": bots, "unatt": unatt},
                {"label": f"{label} · {w}", "k": "u", "n": unatt, "total": total,
                 "humans": total - bots - unatt, "bots": bots, "unatt": unatt},
            ]
    table_head = "<th>Flujo · ventana</th><th>Eventos totales</th><th>Con cuenta (no bots)</th><th>Bots declarados</th><th>Sin cuenta vinculada</th>"
    body = []
    for label in ("Commits rama principal", "PR fusionados (toda base)",
                  "Revisiones de PR", "Releases de GitHub"):
        for w in ("12m", "24m"):
            part = [r for r in data["rows"] if r["label"].startswith(label) and r["label"].endswith(w)]
            if not part:
                continue
            body.append(f"<tr><td>{label} · {w}</td><td>{part[0]['total']}</td>"
                        f"<td>{part[0]['humans']}</td><td>{part[0]['bots']}</td>"
                        f"<td>{part[0]['unatt']}</td></tr>")
    alt = ("Barras apiladas horizontales de los cuatro tipos de evento publico en dos ventanas, "
           "partidas en actores con cuenta, bots declarados y actores sin cuenta vinculada.")
    sub = ("Eventos públicos por tipo en los 35 repositorios atribuidos; cortes y ventanas "
           "fijados antes de recolectar (ventana abierta, exclusiva). Cada barra parte la "
           "actividad en <b>actores con cuenta</b>, <b>bots declarados</b> y <b>sin cuenta "
           "vinculada</b>. Los cuatro flujos se cuentan por separado y no se suman entre sí.")
    figname = "fig1"
    render(1, "eventos-por-flujo", "Actividad pública por tipo de evento y ventana",
           "PASO 5 · ACTIVIDAD OBSERVABLE", sub, alt,
           "Datos derivados de <code>results/overview-totals.json</code>.", 460,
           data, JS_F1, table_head, "\n".join(body))


JS_F2 = BASE_JS + """
window.__build = function(d, tname){
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
  return Plotly.react('chart', traces, L, {displayModeBar:false, responsive:true});
};
"""


def fig2():
    rows = [r for r in load_csv("repo-metrics.csv") if r["window_end"] == "12m"]
    rows.sort(key=lambda r: int(r["commits_nonmerge"]))
    data = {"rows": []}
    for r in rows:
        hu, b, u = int(r["commits_human"]), int(r["commits_bot"]), int(r["commits_unattrib"])
        base = {"humans": hu, "bots": b, "unatt": u, "prs": r["merged_prs_all"],
                "prs_bots": r["merged_prs_bot"], "rel": r["releases_all"],
                "rel_bots": r["releases_bot"]}
        for k, n in (("h", hu), ("b", b), ("u", u)):
            row = dict(base); row.update({"repo": r["repo"], "k": k, "n": n})
            data["rows"].append(row)
    table_head = ("<th>Repositorio</th><th>Commits no-fusion 12m</th><th>Con cuenta</th>"
                  "<th>Bots</th><th>Sin cuenta</th><th>PR fusionados</th><th>Releases</th>")
    body = []
    for r in rows:
        body.append(f"<tr><td>{r['repo']}</td><td>{r['commits_nonmerge']}</td>"
                    f"<td>{r['commits_human']}</td><td>{r['commits_bot']}</td>"
                    f"<td>{r['commits_unattrib']}</td><td>{r['merged_prs_all']}</td>"
                    f"<td>{r['releases_all']}</td></tr>")
    alt = ("Una barra apilada horizontal por repositorio: commits sin fusionar de 12 meses "
           "partidos en actores con cuenta, bots declarados y actores sin cuenta; el punto "
           "de cada barra anota tambien PR fusionados y releases de ese repositorio.")
    sub = ("Commits de la rama principal registrada, excluidos los commits de fusion, en la "
           "ventana de 12 meses para los 35 repositorios. La unidad es el <b>evento</b> "
           "(un commit publico), no horas de trabajo ni esfuerzo. Los PR fusionados que "
           "muestra el comportamiento incluyen todas las ramas base.")
    render(2, "repos-commits", "Actividad por repositorio: commits, bots y actores sin cuenta",
           "PASO 5 - 35 REPOSITORIOS", sub, alt,
           "Datos derivados de <code>results/repo-metrics.csv</code> (ventana 12m).", 780,
           data, JS_F2, table_head, "\n".join(body))
JS_F3 = BASE_JS + """
window.__build = function(d, tname){
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
  return Plotly.react('chart', traces, L, {displayModeBar:false, responsive:true});
};
"""


def fig3():
    hyp = json.loads((RESULTS / "hypotheses.json").read_text(encoding="utf-8"))
    rows = []
    data = {"rows": []}
    met = {(r["repo"], r["window_end"]): r for r in load_csv("repo-metrics.csv")}
    for w in ("12m", "24m"):
        for r in hyp["windows"][w]["H2"]:
            mr = met[(r["repo"], w)]
            data["rows"].append({
                "window": w, "repo_label": r["repo"].split("/")[1],
                "c_commit": r["commit_share"], "c_pr": r["pr_share"],
                "tip": (f"Top commits: {mr['cmt_top1']} ({mr['cmt_top1_count']} de "
                        f"{int(mr['commits_human']) + int(mr['commits_unattrib'])} no-bot) | "
                        f"Top PR: {mr['pr_top1']} ({mr['pr_top1_count']})")})
    table_head = ("<th>Repositorio · ventana</th><th>Cuota commits</th><th>Categoría</th>"
                  "<th>Cuota PR</th><th>Categoría</th>")
    body = []
    met2 = {(r["repo"], r["window_end"]): r for r in load_csv("repo-metrics.csv")}
    for w in ("12m", "24m"):
        for r in hyp["windows"][w]["H2"]:
            body.append(f"<tr><td>{r['repo']} · {w}</td><td>{r['commit_share']}</td>"
                        f"<td>{r['commit_cat']}</td><td>{r['pr_share']}</td>"
                        f"<td>{r['pr_cat']}</td></tr>")
    alt = ("Diagrama de dispersion: cada punto es un repositorio evaluable en ambas "
           "metricas, con la cuota del actor principal por commits (eje x) frente a la "
           "cuota por PR fusionados a rama principal (eje y), para la ventana elegida.")
    sub = ("Solo repositorios con denominadores minimos preregistrados (>=30 commits y >=10 PR "
           "fusionados a rama principal, no bots). La diagonal marca cuotas iguales; "
           "las bandas verticales son las categorias del protocolo. El color de punto es fiel "
           "al tema; pasa el cursor para ver el numerador exacto.")
    render(3, "concentracion-commits-vs-pr", "Un actor principal: cuota por commits frente a PR fusionados",
           "PASO 5 - CONCENTRACION (H1/H2)", sub, alt,
           "Datos derivados de <code>results/hypotheses.json</code> (12 y 24 meses).", 640,
           data, JS_F3, table_head, "\n".join(body))
JS_F4 = BASE_JS + """
window.__build = function(d, tname){
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
  return Plotly.react('chart', traces, L, {displayModeBar:false, responsive:true});
};
"""


def fig4():
    hyp = json.loads((RESULTS / "hypotheses.json").read_text(encoding="utf-8"))
    series = {}
    for w in ("12m", "24m"):
        for r in hyp["windows"][w]["H1"]:
            if r["share"] is None or not r["share"]:
                continue
            s = series.setdefault(r["repo"], {})
            s[w] = round(r["share"], 3)
    evaluable = [repo for repo, s in series.items() if "12m" in s and "24m" in s]
    evaluable.sort(key=lambda x: -sum(series[x].values()))
    parsed = {r: series[r] for r in evaluable}
    table_head = "<th>Repositorio</th><th>Cuota 12m</th><th>Cuota 24m</th>"
    body = "\n".join(f"<tr><td>{r}</td><td>{parsed[r]['12m']}</td>"
                     f"<td>{parsed[r]['24m']}</td></tr>" for r in evaluable)
    alt = ("Grafico de pendientes: para cada repositorio evaluable en ambas ventanas, una "
           "linea con la cuota del actor humano principal por commits en 12 y en 24 meses.")
    sub = ("Cambios de la cuota del actor principal entre ventanas con las mismas reglas "
           "preregistradas. Las lineas horizontales punteadas marcan 0.50 y 0.75. La "
           "estabilidad de cuota no es estabilidad de riesgo: es un cambio de denominador.")
    render(4, "sensibilidad-ventanas", "Sensibilidad: cuota del actor principal entre ventanas",
           "PASO 5 - SENSIBILIDAD 12/24", sub, alt,
           "Datos derivados de <code>results/hypotheses.json</code>.", 640,
           {"repos": evaluable, "series": parsed}, JS_F4, table_head, body)
JS_F5 = BASE_JS + """
window.__build = function(d, tname){
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
  return Plotly.react('chart', traces, L, {displayModeBar:false, responsive:true});
};
"""


def fig5():
    data = {"rows": []}
    for w in ("12m", "24m"):
        rows, pairs = stream_rows(w)
        for label, s in rows:
            total = s["events"]
            b, u, hu = s["bots"], s["unattributed"], total - s["bots"] - s["unattributed"]
            if total == 0:
                continue
            data["rows"] += [
                {"label": f"{label} - {w}", "k": "b", "bot_share": pct(b / total),
                 "humans_share": pct(hu / total), "unatt_share": pct(u / total),
                 "total": total, "bots": b, "humans": hu, "unatt": u},
                {"label": f"{label} - {w}", "k": "h", "bot_share": pct(b / total),
                 "humans_share": pct(hu / total), "unatt_share": pct(u / total),
                 "total": total, "bots": b, "humans": hu, "unatt": u},
                {"label": f"{label} - {w}", "k": "u", "bot_share": pct(b / total),
                 "humans_share": pct(hu / total), "unatt_share": pct(u / total),
                 "total": total, "bots": b, "humans": hu, "unatt": u},
            ]
    table_head = ("<th>Flujo - ventana</th><th>Eventos</th><th>Bots declarados</th>"
                  "<th>Con cuenta</th><th>Sin cuenta</th><th>% bots</th>")
    body = []
    for label in ("Commits rama principal", "PR fusionados (toda base)",
                  "Revisiones de PR", "Releases de GitHub"):
        for w in ("12m", "24m"):
            part = [r for r in data["rows"]
                    if r["label"].startswith(label) and r["label"].endswith(w)]
            if not part:
                continue
            t = part[0]
            body.append(f"<tr><td>{label} - {w}</td><td>{t['total']}</td><td>{t['bots']}</td>"
                        f"<td>{t['humans']}</td><td>{t['unatt']}</td>"
                        f"<td>{t['bot_share']}%</td></tr>")
    alt = ("Porcentaje de eventos automatizados declaradamente, de actores con cuenta y de "
           "actores sin cuenta, por tipo de evento y ventana, en barras apiladas al 100 %.")
    sub = ("La misma composicion de la figura 1 expresada en participacion porcentual. "
           "La deteccion de bots es la del paso 4 (type=Bot o sufijo [bot]); no capta "
           "automatizacion no declarada, que la auditoria registro aparte.")
    render(5, "bots-por-flujo", "Participacion de bots declarados por tipo de evento",
           "PASO 5 - AUTOMATIZACION", sub, alt,
           "Datos derivados de <code>results/overview-totals.json</code>.", 460,
           data, JS_F5, table_head, "\n".join(body))


def main():
    (RESULTS / "figure-meta.json").write_text("[]", encoding="utf-8")  # reset
    FIGURE_META.clear()
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    (RESULTS / "figure-meta.json").write_text(
        json.dumps(FIGURE_META, indent=1, ensure_ascii=False), encoding="utf-8")
    print("figures done")


if __name__ == "__main__":
    main()
