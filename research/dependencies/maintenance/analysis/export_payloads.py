#!/usr/bin/env python3
"""Export the step-5 figures as Econopapi Plotly manifests (schema v1, figures v2).

Presentation derivative requested by the external peer-review dictamen of
2026-11-01 (§5): the five figures are restated around questions and built
EXCLUSIVELY from frozen published results (`results/*.json|csv` and
`figures/fig*-data.json`, all read-only inputs). No frozen data, plan,
hypotheses or preregistered denominators are modified here. The original
fig3 scatter remains as technical supplement in
`figures/fig3-concentracion-commits-vs-pr.html`.

Every export re-runs crosschecks against the frozen sources and the exact
numbers quoted by the dictamen (§2, §3, §5); any mismatch aborts the export
before a single file is written. The only editable outputs are
`results/plotly-embed/fig{1..5}.json` and `index.json`; the historical
`post-2735-*.json` upload archive is never touched.

Run from the repository root:
    python research/dependencies/maintenance/analysis/export_payloads.py
"""

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
OUT = RESULTS / "plotly-embed"

REPOSITORY = "https://github.com/econopapi/DeudaMundi"
SOURCE_COMMIT = "1363af84d5089ca4260645012dcb34ccc93d4c6c"
CUT_UTC = "2026-10-30T00:00:00Z"
ANALYSIS_PATH = "research/dependencies/maintenance/analysis/export_payloads.py"
METHODOLOGY_PATH = "research/dependencies/maintenance/analysis/plan.md"

WINDOWS = ("12m", "24m")
WINDOW_LABELS = {"12m": "12 meses", "24m": "24 meses"}

ACTOR_NAMES = {
    "h": "Con cuenta (no bots)",
    "b": "Bots declarados",
    "u": "Sin cuenta vinculada",
}
# Paleta funcional (no cosmética): el tema del sitio fija fondos, tipografía y
# colorway, pero el colorway no puede expresar "mismo actor = mismo color" a
# través del conmutador 12/24 (las trazas ocultas consumirían índices
# distintos y la leyenda mentiría al cambiar de ventana). Estos tres colores
# son estables entre ventanas y figuras, con contraste >=3:1 (WCAG 1.4.11)
# sobre superficie clara (#f6f7fb) y oscura, y distinguibles en deuteranopía;
# nunca son la única codificación (nombre en leyenda + posición + tabla).
ACTOR_COLORS = {"h": "#5B87B5", "b": "#C07800", "u": "#7C7C81"}
NEUTRAL = "#8A8A8F"            # conectores/umbrales/casos Δ=0: gris neutro funcional
WARN = "#B3453C"               # aspa de caso inconcluso (regla de bots)

# Categorías preregistradas de concentración (plan.md / hypotheses.json).
CAT_LABELS = {"<=50%": "≤50 %", "50-75%": ">50–75 %", ">75%": ">75 %"}

# Flujos de events (units NOT comparable between flows; never summed).
FLOWS = {
    "commits": ("Commits rama principal", ("commits_nonmerge", "commit_merges")),
    "prs": ("PR fusionados (toda base)", ("merged_prs_main", "merged_prs_other_base")),
    "reviews_raw": ("Revisiones de PR (crudas)", ("reviews_raw",)),
    "review_pairs": ("Pares únicos revisor–PR", ("review_pairs",)),
    "releases": ("Releases de GitHub", ("releases",)),
}
FIG1_FLOWS = ("commits", "prs", "reviews_raw", "releases")
FIG5_FLOWS = ("commits", "prs", "reviews_raw", "review_pairs", "releases")
# Etiquetas congeladas en figures/fig1-data.json y fig5-data.json (4 flujos).
FROZEN_FLOW_LABELS = {
    "commits": "Commits rama principal",
    "prs": "PR fusionados (toda base)",
    "reviews_raw": "Revisiones de PR",
    "releases": "Releases de GitHub",
}

# Cifras textuales del dictamen externo (2026-11-01) usadas como contraste.
EXPECTED_TOTALS = {
    ("commits", "12m"): 7014, ("prs", "12m"): 3981,
    ("reviews_raw", "12m"): 10543, ("releases", "12m"): 356,
    ("commits", "24m"): 12593, ("prs", "24m"): 6545,
    ("reviews_raw", "24m"): 18025, ("releases", "24m"): 594,
}
EXPECTED_BOT_PCT_12M = {
    "commits": 21.3, "prs": 16.8, "reviews_raw": 24.8,
    "review_pairs": 28.5, "releases": 39.3,
}
EXPECTED_BOT_PCT_24M_PAIRS = 18.7   # 1757/9380
EXPECTED_H1 = {
    "12m": {"evaluable": 22, "numeric_over_50": 15, "inconclusive": 1,
            "conclusive_over_50": 14, "inconclusive_repos": ["fastapi/fastapi"]},
    "24m": {"evaluable": 28, "numeric_over_50": 19, "inconclusive": 0,
            "conclusive_over_50": 19, "inconclusive_repos": []},
}
EXPECTED_H2 = {"12m": {"rows": 18, "changed": 6}, "24m": {"rows": 25, "changed": 10}}
EXPECTED_DELTA_EXAMPLES_12M = {   # dictamen §5 fig3 (pp, dos decimales)
    "grahamdumpleton/wrapt": 65.67,
    "agronholm/apscheduler": 57.17,
    "sqlalchemy/sqlalchemy": 50.09,
    "jpadilla/pyjwt": 44.54,
    "agronholm/anyio": 26.34,
}
EXPECTED_TIES = {   # audits.md, verificación fechada 01-11-2026
    ("kludex/uvicorn", "12m"),
    ("python/typing_extensions", "12m"),
    ("python/typing_extensions", "24m"),
    ("redis/redis-py", "12m"),
}
FIG2_CROP_N = 15  # recorte de presentación predefinido (no selección estadística)
ZERO_COMMIT_REPOS_12M = ["encode/httpcore", "python-hyper/h11"]


def fmt_int(value):
    return f"{int(value):,}"


def analysis_commit():
    """Identify the analysis snapshot when exporting from a Git checkout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=HERE, check=True, capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def load_frozen():
    """Read every frozen source (read-only) used by the figures v2."""
    overview = json.loads((RESULTS / "overview-totals.json").read_text(encoding="utf-8"))
    hypotheses = json.loads((RESULTS / "hypotheses.json").read_text(encoding="utf-8"))
    metrics = {}
    with (RESULTS / "repo-metrics.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            metrics[(row["repo"], row["window_end"])] = row
    continuity = {}
    with (RESULTS / "continuity.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            continuity[(row["repo"], row["window"])] = row
    frozen = {
        f"fig{i}": json.loads((FIGURES / f"fig{i}-data.json").read_text(encoding="utf-8"))
        for i in range(1, 6)
    }
    return overview, hypotheses, metrics, continuity, frozen


def flow_totals(overview, flow, window):
    """Aggregate overview-totals components into one flow's counts."""
    events = bots = unatt = 0
    for component in FLOWS[flow][1]:
        part = overview[window][component]
        events += part["events"]
        bots += part["bots"]
        unatt += part["unattributed"]
    humans = events - bots - unatt
    assert humans >= 0, (flow, window)
    return {"events": events, "humans": humans, "bots": bots, "unatt": unatt}


def category(share):
    """Preregistered concentration category (plan.md boundaries)."""
    if share <= 0.5:
        return "≤50 %"
    if share <= 0.75:
        return ">50–75 %"
    return ">75 %"


def short_label(repo):
    return repo.split("/", 1)[1]


# ---------------------------------------------------------------------------
# Crosschecks: the export aborts if any frozen number or dictamen quote fails.
# ---------------------------------------------------------------------------

def crosscheck(overview, hypotheses, metrics, frozen):
    passed = []

    # 1) Totales por flujo y ventana == tabla §2 del dictamen.
    for (flow, window), expected in EXPECTED_TOTALS.items():
        actual = flow_totals(overview, flow, window)["events"]
        assert actual == expected, (flow, window, actual, expected)
    passed.append("totales por flujo/ventana == dictamen §2 (7,014/3,981/10,543/356 · 12,593/6,545/18,025/594)")

    # 2) % de bots 12m == §5 fig5 del dictamen (crudas y pares por separado).
    for flow, expected in EXPECTED_BOT_PCT_12M.items():
        totals = flow_totals(overview, flow, "12m")
        actual = round(100 * totals["bots"] / totals["events"], 1)
        assert actual == expected, (flow, actual, expected)
    pairs24 = flow_totals(overview, "review_pairs", "24m")
    assert round(100 * pairs24["bots"] / pairs24["events"], 1) == EXPECTED_BOT_PCT_24M_PAIRS
    passed.append("% bots 12m == dictamen (21.3/16.8/24.8/28.5/39.3) y pares 24m == 18.7; revisiones crudas ≠ pares únicos")

    # 3) overview-totals == figures/fig1-data.json y fig5-data.json (congelados).
    for window in WINDOWS:
        for flow in FIG1_FLOWS:
            totals = flow_totals(overview, flow, window)
            label = f"{FROZEN_FLOW_LABELS[flow]} · {window}"
            rows = [r for r in frozen["fig1"]["rows"] if r["label"] == label]
            by_key = {r["k"]: r for r in rows}
            assert by_key["h"]["n"] == totals["humans"], (flow, window)
            assert by_key["b"]["n"] == totals["bots"], (flow, window)
            assert by_key["u"]["n"] == totals["unatt"], (flow, window)
            assert by_key["h"]["total"] == totals["events"], (flow, window)
            for key, field in (("b", "bot_share"), ("h", "humans_share"), ("u", "unatt_share")):
                share = 100 * (totals["bots"] if key == "b" else
                               totals["humans"] if key == "h" else totals["unatt"]) / totals["events"]
                label5 = f"{FROZEN_FLOW_LABELS[flow]} - {window}"
                row5 = [r for r in frozen["fig5"]["rows"]
                        if r["label"] == label5 and r["k"] == key]
                assert row5 and abs(row5[0][field] - share) <= 0.05, (flow, window, key)
    passed.append("overview-totals.json reconcilia con fig1-data.json y fig5-data.json (conteos y % ±0.05)")

    # 4) repo-metrics: consistencia interna y totales globales == overview.
    for window in WINDOWS:
        sums = {"nonmerge": 0, "merge": 0, "prs_main": 0, "prs_other": 0,
                "reviews_raw": 0, "pairs": 0, "releases": 0}
        for (repo, w), row in metrics.items():
            if w != window:
                continue
            nonmerge = int(row["commits_nonmerge"])
            assert nonmerge == int(row["commits_human"]) + int(row["commits_bot"]) + int(row["commits_unattrib"]), (repo, w)
            sums["nonmerge"] += nonmerge
            sums["merge"] += int(row["commits_merge"])
            sums["prs_main"] += int(row["merged_prs_main"])
            sums["prs_other"] += int(row["merged_prs_other_base"])
            sums["reviews_raw"] += int(row["reviews_raw"])
            sums["pairs"] += int(row["review_pairs"])
            sums["releases"] += int(row["releases_all"])
        assert sums["nonmerge"] == overview[window]["commits_nonmerge"]["events"], window
        assert sums["merge"] == overview[window]["commit_merges"]["events"], window
        assert sums["prs_main"] == overview[window]["merged_prs_main"]["events"], window
        assert sums["prs_other"] == overview[window]["merged_prs_other_base"]["events"], window
        assert sums["reviews_raw"] == overview[window]["reviews_raw"]["events"], window
        assert sums["pairs"] == overview[window]["review_pairs"]["events"], window
        assert sums["releases"] == overview[window]["releases"]["events"], window
    passed.append("repo-metrics.csv (70 filas) suma exactamente overview-totals.json en ambos ventanas; h+b+u == nonmerge fila a fila")

    # 5) H1: resúmenes, evaluabilidad y regla de inconclusos == dictamen §3.
    for window in WINDOWS:
        summary = hypotheses["windows"][window]["H1_summary"]
        rows = hypotheses["windows"][window]["H1"]
        expected = EXPECTED_H1[window]
        assert summary["evaluable"] == expected["evaluable"] == len(rows), window
        assert summary["numeric_over_50"] == expected["numeric_over_50"], window
        assert summary["inconclusive"] == expected["inconclusive"], window
        assert summary["conclusive_over_50"] == expected["conclusive_over_50"], window
        assert summary["inconclusive_repos"] == expected["inconclusive_repos"], window
        for row in rows:
            metric = metrics[(row["repo"], window)]
            den = int(metric["commits_nonmerge"]) - int(metric["commits_bot"])
            assert den == row["den_nonmerge"] >= 30, (row["repo"], window)
            assert row["top1"] == metric["cmt_top1"], (row["repo"], window)
            assert round(float(metric["cmt_top1_share"]), 4) == round(row["share"], 4), (row["repo"], window)
    assert {r["repo"] for r in hypotheses["windows"]["12m"]["H1"]} <= \
           {r["repo"] for r in hypotheses["windows"]["24m"]["H1"]}
    passed.append("H1: 22 evaluables/15 >50%/1 inconcluso (fastapi)/14 conclusivos en 12m; 28/19/0/19 en 24m; denominadores y top-1 == repo-metrics.csv")

    # 6) H2: filas, cambios de categoría y ejemplos de delta del dictamen §5.
    ties = set()
    deltas = {}
    for window in WINDOWS:
        rows = hypotheses["windows"][window]["H2"]
        assert len(rows) == EXPECTED_H2[window]["rows"], window
        assert sum(1 for r in rows if r["changed"]) == EXPECTED_H2[window]["changed"], window
        for row in rows:
            metric = metrics[(row["repo"], window)]
            assert round(float(metric["cmt_top1_share"]), 4) == round(row["commit_share"], 4), row["repo"]
            assert round(float(metric["pr_top1_share"]), 4) == round(row["pr_share"], 4), row["repo"]
            assert row["commit_cat"] in CAT_LABELS and row["pr_cat"] in CAT_LABELS, row
            assert CAT_LABELS[row["commit_cat"]] == category(row["commit_share"]), row
            assert CAT_LABELS[row["pr_cat"]] == category(row["pr_share"]), row
            delta = round(100 * (row["commit_share"] - row["pr_share"]), 2)
            deltas[(row["repo"], window)] = delta
            if metric["cmt_top1_share"] == metric["pr_top1_share"]:
                ties.add((row["repo"], window))
    for repo, expected in EXPECTED_DELTA_EXAMPLES_12M.items():
        assert deltas[(repo, "12m")] == expected, (repo, deltas[(repo, "12m")], expected)
    assert ties == EXPECTED_TIES, ties
    passed.append("H2: 6/18 cambios de categoría en 12m y 10/25 en 24m; categorías == fronteras preregistradas; deltas del dictamen reproducidos (wrapt +65.67, APScheduler +57.17, SQLAlchemy +50.09, PyJWT +44.54, AnyIO +26.34)")
    passed.append("coincidencias exactas de cuota top-1 == los 4 casos auditados (espejo squash, audits.md 01-11-2026): uvicorn 12m, typing_extensions 12m/24m, redis-py 12m")

    # 7) fig2-data.json (congelado) == repo-metrics 12m repositorio a repositorio.
    fig2 = {}
    for r in frozen["fig2"]["rows"]:
        fig2.setdefault(r["repo"], {})[r["k"]] = r
    assert len(fig2) == 35, len(fig2)
    for repo, parts in fig2.items():
        metric = metrics[(repo, "12m")]
        assert parts["h"]["humans"] == int(metric["commits_human"]), repo
        assert parts["b"]["bots"] == int(metric["commits_bot"]), repo
        assert parts["u"]["unatt"] == int(metric["commits_unattrib"]), repo
        assert int(parts["h"]["prs"]) == int(metric["merged_prs_all"]), repo
        assert int(parts["h"]["rel"]) == int(metric["releases_all"]), repo
    zeros12 = sorted(repo for (repo, w), m in metrics.items()
                     if w == "12m" and int(m["commits_all"]) == 0)
    assert zeros12 == ZERO_COMMIT_REPOS_12M, zeros12
    passed.append("fig2-data.json == repo-metrics.csv 12m (35 repos); ceros de 12m: encode/httpcore y python-hyper/h11; 24m: ninguno")

    # 8) fig3-data.json (congelado) == H2; fig4-data.json == H1.
    fig3 = {}
    for r in frozen["fig3"]["rows"]:
        fig3[(r["window"], r["repo_label"])] = r
    h2_rows = {(w, short_label(r["repo"])): r
               for w in WINDOWS for r in hypotheses["windows"][w]["H2"]}
    assert set(fig3) == set(h2_rows), (len(fig3), len(h2_rows))
    for key, frozen_row in fig3.items():
        row = h2_rows[key]
        assert abs(frozen_row["c_commit"] - row["commit_share"]) < 1e-9, key
        assert abs(frozen_row["c_pr"] - row["pr_share"]) < 1e-9, key
    series = frozen["fig4"]["series"]
    assert set(series) == {r["repo"] for r in hypotheses["windows"]["12m"]["H1"]}
    for window in WINDOWS:
        shares = {r["repo"]: r["share"] for r in hypotheses["windows"][window]["H1"]}
        for repo, values in series.items():
            if repo in shares:
                assert abs(values[window] - shares[repo]) <= 0.0011, (repo, window)
    passed.append("fig3-data.json == H2 (43 filas) y fig4-data.json == H1 12m (22 repos, ±0.001 por redondeo a 3 decimales)")
    return passed


# ---------------------------------------------------------------------------
# Figure builders (dictamen §5). Each returns (figure, caption, columns, rows).
# ---------------------------------------------------------------------------

def column(key, label, kind="string", unit=None):
    result = {"key": key, "label": label, "type": kind}
    if unit is not None:
        result["unit"] = unit
    return result


def axis_categories(labels):
    return {"categoryorder": "array", "categoryarray": list(labels)}


def window_buttons(visible_map, extra_layout=None):
    buttons = []
    for index, window in enumerate(WINDOWS):
        args = [{"visible": visible_map[window]}]
        if extra_layout and window in extra_layout:
            args.append(extra_layout[window])
        buttons.append({
            "label": WINDOW_LABELS[window],
            "method": "update" if len(args) > 1 else "restyle",
            "args": args,
        })
    return [{
        "type": "buttons", "direction": "right",
        "x": 0, "y": 1.07, "xanchor": "left", "yanchor": "bottom",
        "active": 0, "buttons": buttons,
    }]


def legend_bottom():
    return {"orientation": "h", "x": 0, "y": -0.14, "xanchor": "left", "yanchor": "top"}


def build_fig1(overview):
    """§5 fig1 — «¿Cuánta actividad pública observamos?» cifras grandes."""
    flows = [FLOWS[key][0] for key in FIG1_FLOWS]
    y_labels = list(flows)
    traces = []
    for window in WINDOWS:
        totals = [flow_totals(overview, flow, window) for flow in FIG1_FLOWS]
        traces.append({
            "type": "bar", "orientation": "h", "name": WINDOW_LABELS[window],
            "x": [t["events"] for t in totals],
            "y": y_labels,
            "text": [fmt_int(t["events"]) for t in totals],
            "textposition": "outside",
            "textfont": {"size": 13},
            "customdata": [[t["humans"], t["bots"], t["unatt"]] for t in totals],
            "hovertemplate": (
                "<b>%{y}</b> · " + WINDOW_LABELS[window] + "<br>"
                "Total: %{x:,} eventos<br>"
                "Con cuenta (no bots): %{customdata[0]:,}<br>"
                "Bots declarados: %{customdata[1]:,}<br>"
                "Sin cuenta vinculada: %{customdata[2]:,}"
                "<extra></extra>"
            ),
        })
    biggest = max(flow_totals(overview, flow, window)["events"]
                  for flow in FIG1_FLOWS for window in WINDOWS)
    figure = {
        "data": traces,
        "layout": {
            "barmode": "group", "bargap": 0.3, "bargroupgap": 0.06,
            "xaxis": {
                "title": {"text": "eventos observados en la ventana (unidades no comparables entre flujos: no se suman)"},
                "range": [0, biggest * 1.28],
                "zeroline": False,
            },
            "yaxis": dict({"autorange": "reversed"}, **axis_categories(y_labels)),
            "legend": legend_bottom(),
            "margin": {"l": 8, "r": 16, "t": 16, "b": 72},
        },
    }
    columns = [
        column("flow", "Flujo"),
        column("window", "Ventana"),
        column("events", "Eventos totales", "number", "eventos"),
        column("humans", "Con cuenta (no bots)", "number", "eventos"),
        column("bots", "Bots declarados", "number", "eventos"),
        column("unattributed", "Sin cuenta vinculada", "number", "eventos"),
    ]
    rows = []
    for flow in FIG1_FLOWS:
        for window in WINDOWS:
            totals = flow_totals(overview, flow, window)
            rows.append({
                "flow": FLOWS[flow][0], "window": WINDOW_LABELS[window],
                "events": totals["events"], "humans": totals["humans"],
                "bots": totals["bots"], "unattributed": totals["unatt"],
            })
    caption = ("Totales por flujo y ventana con su composición por tipo de cuenta "
               "(8 filas). Los cuatro flujos cuentan unidades distintas: no se suman.")
    return figure, caption, columns, rows


def build_fig2(metrics, continuity, hypotheses):
    """§5 fig2 — ranking por commits no automatizados, conmutador 12/24."""
    repos = sorted({repo for (repo, window) in metrics if window == "12m"})
    assert len(repos) == 35, len(repos)
    labels = {repo: short_label(repo) for repo in repos}
    assert len(set(labels.values())) == 35

    def nonbot(window, repo):
        row = metrics[(repo, window)]
        return int(row["commits_human"]) + int(row["commits_unattrib"])

    order = sorted(repos, key=lambda r: (-nonbot("12m", r), r))
    crop = order[:FIG2_CROP_N]
    h1 = {w: {r["repo"] for r in hypotheses["windows"][w]["H1"]} for w in WINDOWS}
    y_labels = [labels[repo] for repo in crop]

    biggest = 0
    traces = []
    for window in WINDOWS:
        per = {repo: {
            "h": int(metrics[(repo, window)]["commits_human"]),
            "b": int(metrics[(repo, window)]["commits_bot"]),
            "u": int(metrics[(repo, window)]["commits_unattrib"]),
        } for repo in crop}
        totals = {repo: per[repo]["h"] + per[repo]["b"] + per[repo]["u"] for repo in crop}
        biggest = max(biggest, max(totals.values()))
        for key in ("h", "b", "u"):
            traces.append({
                "type": "bar", "orientation": "h",
                "name": ACTOR_NAMES[key], "legendgroup": key,
                "marker": {"color": ACTOR_COLORS[key]},
                "x": [per[repo][key] for repo in crop],
                "y": y_labels,
                "customdata": [
                    [totals[repo], per[repo]["h"], per[repo]["b"], per[repo]["u"],
                     int(continuity[(repo, window)]["commits_months_all"]),
                     "sí" if repo in h1[window] else "no"]
                    for repo in crop
                ],
                "hovertemplate": (
                    "<b>%{y}</b> · " + WINDOW_LABELS[window] + "<br>"
                    + ACTOR_NAMES[key] + ": %{x:,} commits sin merges<br>"
                    "Total sin merges: %{customdata[0]:,} (con cuenta %{customdata[1]:,} · "
                    "bots %{customdata[2]:,} · sin cuenta %{customdata[3]:,})<br>"
                    "Meses con commits: %{customdata[4]} · Evaluable H1: %{customdata[5]}"
                    "<extra></extra>"
                ),
                "visible": window == "12m",
            })
        traces.append({
            "type": "scatter", "mode": "text", "showlegend": False,
            "x": [totals[repo] for repo in crop],
            "y": y_labels,
            "text": [fmt_int(totals[repo]) for repo in crop],
            "textposition": "middle right",
            "textfont": {"size": 10},
            "hoverinfo": "skip",
            "visible": window == "12m",
        })
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack", "bargap": 0.28,
            "xaxis": {
                "title": {"text": "commits de rama principal sin merges en la ventana activa (eventos)"},
                "range": [0, biggest * 1.25],
                "zeroline": False,
            },
            "yaxis": dict({"autorange": "reversed", "tickfont": {"size": 11}},
                          **axis_categories(y_labels)),
            "legend": legend_bottom(),
            "updatemenus": window_buttons({
                "12m": [True, True, True, True, False, False, False, False],
                "24m": [False, False, False, False, True, True, True, True],
            }),
            "margin": {"l": 8, "r": 48, "t": 64, "b": 96},
        },
    }
    columns = [
        column("repository", "Repositorio"),
        column("window", "Ventana"),
        column("commits_nonmerge", "Commits sin merges", "number", "commits"),
        column("humans", "Con cuenta (no bots)", "number", "commits"),
        column("bots", "Bots declarados", "number", "commits"),
        column("unattributed", "Sin cuenta vinculada", "number", "commits"),
        column("den_h1", "Denominador H1 (no-bot)", "number", "commits"),
        column("evaluable_h1", "Evaluable H1 (≥30 no-bot)", "boolean"),
        column("months", "Meses con commits", "number", "meses"),
        column("last_nonbot", "Último commit no-bot", "string", "UTC ISO 8601"),
    ]
    rows = []
    for repo in sorted(repos):
        for window in WINDOWS:
            metric = metrics[(repo, window)]
            cont = continuity[(repo, window)]
            last = cont["commits_last_nobot"] or None
            rows.append({
                "repository": repo, "window": WINDOW_LABELS[window],
                "commits_nonmerge": int(metric["commits_nonmerge"]),
                "humans": int(metric["commits_human"]),
                "bots": int(metric["commits_bot"]),
                "unattributed": int(metric["commits_unattrib"]),
                "den_h1": nonbot(window, repo),
                "evaluable_h1": repo in h1[window],
                "months": int(cont["commits_months_all"]),
                "last_nonbot": last,
            })
    caption = ("Los 35 repositorios en ambas ventanas (70 filas), incluidos los de "
               "actividad cero y los que no alcanzan el umbral H1. El gráfico recorta "
               "a los 15 repositorios con más commits no automatizados en 12 m "
               "(recorte de presentación predefinido, idéntico en ambas ventanas).")
    return figure, caption, columns, rows


def build_fig3(hypotheses, metrics):
    """§5 fig3 — barras divergentes de delta_pp (H2 sigue por categorías)."""
    per_window = {}
    for window in WINDOWS:
        entries = []
        for row in hypotheses["windows"][window]["H2"]:
            metric = metrics[(row["repo"], window)]
            delta = round(100 * (row["commit_share"] - row["pr_share"]), 2)
            entries.append({
                "repo": row["repo"], "label": short_label(row["repo"]),
                "delta": delta,
                "c_share": round(row["commit_share"] * 100, 2),
                "p_share": round(row["pr_share"] * 100, 2),
                "c_top": metric["cmt_top1"], "c_num": int(metric["cmt_top1_count"]),
                "c_den": int(metric["commits_human"]),
                "c_pct": f"{row['commit_share'] * 100:.2f} %",
                "p_top": metric["pr_top1"], "p_num": int(metric["pr_top1_count"]),
                "p_den": int(metric["merged_prs_main_human"]),
                "p_pct": f"{row['pr_share'] * 100:.2f} %",
                "c_cat": CAT_LABELS[row["commit_cat"]],
                "p_cat": CAT_LABELS[row["pr_cat"]],
                "changed": bool(row["changed"]),
                "tie": metric["cmt_top1_share"] == metric["pr_top1_share"],
            })
        entries.sort(key=lambda e: (-e["delta"], e["repo"]))
        per_window[window] = entries

    traces = []
    layout_menus = {}
    for window in WINDOWS:
        entries = per_window[window]
        y_labels = [e["label"] for e in entries]
        customdata = [
            [e["c_top"], e["c_num"], e["c_den"], e["c_pct"],
             e["p_top"], e["p_num"], e["p_den"], e["p_pct"],
             e["repo"], e["c_cat"], e["p_cat"],
             " · H2: cambia de categoría" if e["changed"] else ""]
            for e in entries
        ]
        traces.append({
            "type": "bar", "orientation": "h", "showlegend": False,
            "x": [e["delta"] for e in entries],
            "y": y_labels,
            "text": [f"{e['delta']:+.2f}" if e["delta"] != 0 else "" for e in entries],
            "textposition": "outside",
            "textfont": {"size": 10},
            "customdata": customdata,
            "hovertemplate": (
                "<b>%{customdata[8]}</b> · " + WINDOW_LABELS[window] + "<br>"
                "Δ = %{x:+.2f} pp (descriptivo editorial)<br>"
                "Commits: %{customdata[0]} — %{customdata[1]} de %{customdata[2]} no-bot "
                "(%{customdata[3]})<br>"
                "PR a rama principal: %{customdata[4]} — %{customdata[5]} de "
                "%{customdata[6]} no-bot (%{customdata[7]})<br>"
                "Categorías: %{customdata[9]} → %{customdata[10]}%{customdata[11]}"
                "<extra></extra>"
            ),
            "visible": window == "12m",
        })
        ties = [e for e in entries if e["delta"] == 0]
        traces.append({
            "type": "scatter", "mode": "markers",
            "name": "Δ = 0 · cuotas idénticas (espejo squash, ver audits.md)",
            "legendgroup": "tie",
            "x": [0] * len(ties),
            "y": [e["label"] for e in ties],
            "marker": {"symbol": "diamond-open", "size": 11,
                       "color": NEUTRAL, "line": {"color": NEUTRAL, "width": 2}},
            "customdata": [[e["repo"]] for e in ties],
            "hovertemplate": (
                "<b>%{customdata[0]}</b> · " + WINDOW_LABELS[window] + "<br>"
                "Δ = 0.00 pp: cuotas top-1 idénticas en commits y PR.<br>"
                "Espejo 1:1 por materialización squash de los PR (web-flow): "
                "no son dos medidas independientes (audits.md, 01-11-2026)."
                "<extra></extra>"
            ),
            "visible": window == "12m",
        })
        layout_menus[window] = {"yaxis.categoryarray": y_labels}
    max_abs = max(abs(e["delta"]) for entries in per_window.values() for e in entries)
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack", "bargap": 0.34,
            "xaxis": {
                "title": {"text": "cuota top-1 commits − cuota top-1 PR (puntos porcentuales)"},
                "range": [-max_abs * 1.3, max_abs * 1.3],
                "zeroline": True, "zerolinewidth": 2,
            },
            "yaxis": dict({"autorange": "reversed", "tickfont": {"size": 11}},
                          **axis_categories(layout_menus["12m"]["yaxis.categoryarray"])),
            "legend": legend_bottom(),
            "updatemenus": window_buttons(
                {"12m": [True, True, False, False], "24m": [False, False, True, True]},
                layout_menus,
            ),
            "margin": {"l": 8, "r": 56, "t": 64, "b": 96},
        },
    }
    columns = [
        column("repository", "Repositorio"),
        column("window", "Ventana"),
        column("commit_share", "Cuota commits", "number", "%"),
        column("commit_top", "Cuenta top commits"),
        column("commit_num", "Commits de la cuenta top", "number", "commits"),
        column("commit_den", "Denominador commits (no-bot)", "number", "commits"),
        column("pr_share", "Cuota PR", "number", "%"),
        column("pr_top", "Cuenta top PR"),
        column("pr_num", "PR de la cuenta top", "number", "PR"),
        column("pr_den", "Denominador PR (no-bot, rama principal)", "number", "PR"),
        column("commit_cat", "Categoría commits (preregistrada)"),
        column("pr_cat", "Categoría PR (preregistrada)"),
        column("changed", "H2: cambia de categoría", "boolean"),
        column("delta_pp", "Δ commits − PR (análisis descriptivo editorial)", "number", "pp"),
        column("tie", "Coincidencia exacta (espejo squash)", "boolean"),
    ]
    rows = []
    for window in WINDOWS:
        for e in sorted(per_window[window], key=lambda e: e["repo"]):
            rows.append({
                "repository": e["repo"], "window": WINDOW_LABELS[window],
                "commit_share": e["c_share"],
                "commit_top": e["c_top"], "commit_num": e["c_num"], "commit_den": e["c_den"],
                "pr_share": e["p_share"],
                "pr_top": e["p_top"], "pr_num": e["p_num"], "pr_den": e["p_den"],
                "commit_cat": e["c_cat"], "pr_cat": e["p_cat"],
                "changed": e["changed"], "delta_pp": e["delta"], "tie": e["tie"],
            })
    caption = ("Repos evaluables en H2 con ambas cuotas, numeradores, denominadores, "
               "identidades top y categorías preregistradas (43 filas: 18 en 12 m + 25 en 24 m). "
               "Δ en pp: análisis descriptivo editorial; H2 se evalúa por categorías.")
    return figure, caption, columns, rows


def build_fig4(hypotheses, metrics, frozen_fig4):
    """§5 fig4 — dumbbell de sensibilidad 12/24 con estados y umbrales."""
    rows12 = {r["repo"]: r for r in hypotheses["windows"]["12m"]["H1"]}
    rows24 = {r["repo"]: r for r in hypotheses["windows"]["24m"]["H1"]}
    repos = sorted(rows24, key=lambda r: (-rows24[r]["share"], r))
    labels = {repo: short_label(repo) for repo in repos}
    y_labels = [labels[repo] for repo in repos]

    def point(window, repo, row):
        metric = metrics[(repo, window)]
        status = ("inconcluso (regla de bots)" if row["inconclusive"] else "evaluable")
        return [WINDOW_LABELS[window], row["top1"], int(metric["cmt_top1_count"]),
                row["den_nonmerge"],
                ("Estado: " + status) if row["inconclusive"]
                else ("Categoría: " + category(row["share"])), repo]

    circle = [(repo, rows12[repo]) for repo in repos
              if repo in rows12 and not rows12[repo]["inconclusive"]]
    inconclusive = [(repo, rows12[repo]) for repo in repos
                    if repo in rows12 and rows12[repo]["inconclusive"]]
    squares = [(repo, rows24[repo]) for repo in repos]
    traces = [
        {
            "type": "scatter", "mode": "markers", "name": "12 meses (círculo)",
            "x": [round(row["share"] * 100, 4) for _, row in circle],
            "y": [labels[repo] for repo, _ in circle],
            "marker": {"symbol": "circle", "size": 9},
            "customdata": [point("12m", repo, row) for repo, row in circle],
            "hovertemplate": (
                "<b>%{customdata[5]}</b> · %{customdata[0]}<br>"
                "Cuota top-1: %{x:.2f} %<br>"
                "Cuenta: %{customdata[1]} — %{customdata[2]} de %{customdata[3]} "
                "commits no-bot<br>%{customdata[4]}<extra></extra>"
            ),
        },
        {
            "type": "scatter", "mode": "markers",
            "name": "12 meses · inconcluso (regla de bots)",
            "x": [round(row["share"] * 100, 4) for _, row in inconclusive],
            "y": [labels[repo] for repo, _ in inconclusive],
            "marker": {"symbol": "x-thin", "size": 14, "color": WARN,
                       "line": {"color": WARN, "width": 2.5}},
            "customdata": [point("12m", repo, row) for repo, row in inconclusive],
            "hovertemplate": (
                "<b>%{customdata[5]}</b> · %{customdata[0]}<br>"
                "Cuota top-1 numérica: %{x:.2f} % — %{customdata[4]}<br>"
                "Cuenta: %{customdata[1]} — %{customdata[2]} de %{customdata[3]} "
                "commits no-bot<extra></extra>"
            ),
        },
        {
            "type": "scatter", "mode": "markers", "name": "24 meses (cuadrado)",
            "x": [round(row["share"] * 100, 4) for _, row in squares],
            "y": [labels[repo] for repo, _ in squares],
            "marker": {"symbol": "square", "size": 8.5},
            "customdata": [point("24m", repo, row) for repo, row in squares],
            "hovertemplate": (
                "<b>%{customdata[5]}</b> · %{customdata[0]}<br>"
                "Cuota top-1: %{x:.2f} %<br>"
                "Cuenta: %{customdata[1]} — %{customdata[2]} de %{customdata[3]} "
                "commits no-bot<br>%{customdata[4]}<extra></extra>"
            ),
        },
    ]
    shapes = []
    for repo in repos:
        if repo in rows12:
            shapes.append({
                "type": "line", "layer": "below",
                "x0": round(rows12[repo]["share"] * 100, 4),
                "x1": round(rows24[repo]["share"] * 100, 4),
                "y0": labels[repo], "y1": labels[repo],
                "xref": "x", "yref": "y",
                "line": {"color": "rgba(138,138,143,0.65)", "width": 1.6},
            })
    for value in (50, 75):
        shapes.append({
            "type": "line", "layer": "below",
            "x0": value, "x1": value, "y0": 0, "y1": 1,
            "xref": "x", "yref": "paper",
            "line": {"color": "rgba(138,138,143,0.9)", "width": 1.3, "dash": "dot"},
        })
    figure = {
        "data": traces,
        "layout": {
            "xaxis": {
                "title": {"text": "cuota top-1 de commits sin merges no automatizados (%)"},
                "range": [0, 100], "ticksuffix": "%", "zeroline": False,
            },
            "yaxis": dict({"autorange": "reversed", "tickfont": {"size": 11}},
                          **axis_categories(y_labels)),
            "shapes": shapes,
            "annotations": [
                {"x": value, "y": 1.012, "xref": "x", "yref": "paper",
                 "text": f"{value} %", "showarrow": False, "font": {"size": 10}}
                for value in (50, 75)
            ],
            "legend": legend_bottom(),
            "margin": {"l": 8, "r": 24, "t": 40, "b": 96},
        },
    }
    columns = [
        column("repository", "Repositorio"),
        column("share_12m", "Cuota 12 m", "number", "%"),
        column("top_12m", "Cuenta top 12 m"),
        column("num_12m", "Commits top 12 m", "number", "commits"),
        column("den_12m", "Denominador 12 m (no-bot)", "number", "commits"),
        column("state_12m", "Estado 12 m"),
        column("cat_12m", "Categoría 12 m (preregistrada)"),
        column("share_24m", "Cuota 24 m", "number", "%"),
        column("top_24m", "Cuenta top 24 m"),
        column("num_24m", "Commits top 24 m", "number", "commits"),
        column("den_24m", "Denominador 24 m (no-bot)", "number", "commits"),
        column("state_24m", "Estado 24 m"),
        column("cat_24m", "Categoría 24 m (preregistrada)"),
        column("delta_pp", "Cambio 24 m − 12 m (descriptivo editorial)", "number", "pp"),
    ]
    rows = []
    for repo in repos:
        row24 = rows24[repo]
        row12 = rows12.get(repo)
        metric24 = metrics[(repo, "24m")]
        state12 = None
        if row12 is None:
            state12 = "no evaluable (<30 commits no-bot)"
        elif row12["inconclusive"]:
            state12 = "inconcluso (regla de bots)"
        else:
            state12 = "evaluable"
        delta = (round(100 * (row24["share"] - row12["share"]), 2)
                 if row12 is not None else None)
        rows.append({
            "repository": repo,
            "share_12m": round(row12["share"] * 100, 2) if row12 else None,
            "top_12m": row12["top1"] if row12 else None,
            "num_12m": int(metrics[(repo, "12m")]["cmt_top1_count"]) if row12 else None,
            "den_12m": row12["den_nonmerge"] if row12 else None,
            "state_12m": state12,
            "cat_12m": category(row12["share"]) if row12 else None,
            "share_24m": round(row24["share"] * 100, 2),
            "top_24m": row24["top1"],
            "num_24m": int(metric24["cmt_top1_count"]),
            "den_24m": row24["den_nonmerge"],
            "state_24m": "inconcluso (regla de bots)" if row24["inconclusive"] else "evaluable",
            "cat_24m": category(row24["share"]),
            "delta_pp": delta,
        })
    # fig4-data.json congelado debe seguir coincidiendo (serie 12m/24m).
    series = frozen_fig4["series"]
    for repo in series:
        assert abs(series[repo]["24m"] - rows24[repo]["share"]) <= 0.0011, repo
        if repo in rows12:
            assert abs(series[repo]["12m"] - rows12[repo]["share"]) <= 0.0011, repo
    caption = ("28 repositorios evaluables en 24 m (orden por cuota 24 m), con estado, "
               "identidad top-1 y denominadores por ventana; 6 repos no evaluables en "
               "12 m quedan con cuota 12 m vacía (—).")
    return figure, caption, columns, rows


def build_fig5(overview):
    """§5 fig5 — composición 100 % por flujo, crudas y pares separados."""
    spacers = ["\u00a0", "\u2007", "\u2002", "\u205f"]
    y_labels = []
    bars = []  # (label, flow, window)
    for index, flow in enumerate(FIG5_FLOWS):
        if index:
            y_labels.append(spacers[index - 1])
        for window in WINDOWS:
            label = f"{FLOWS[flow][0]} · {window[:2]} m"
            y_labels.append(label)
            bars.append((label, flow, window))
    totals = {(flow, window): flow_totals(overview, flow, window)
              for _, flow, window in bars}
    traces = []
    for key, field in (("b", "bots"), ("h", "humans"), ("u", "unatt")):
        shares, counts = [], []
        for label, flow, window in bars:
            t = totals[(flow, window)]
            shares.append(100 * t[field] / t["events"])
            counts.append([t[field], t["events"]])
        traces.append({
            "type": "bar", "orientation": "h",
            "name": ACTOR_NAMES[key], "legendgroup": key,
            "marker": {"color": ACTOR_COLORS[key]},
            "x": shares,
            "y": [label for label, _, _ in bars],
            "customdata": counts,
            "hovertemplate": (
                "<b>%{y}</b><br>" + ACTOR_NAMES[key] + ": %{x:.1f} % · "
                "%{customdata[0]:,} de %{customdata[1]:,} eventos<extra></extra>"
            ),
        })
    annotations = []
    for label, flow, window in bars:
        t = totals[(flow, window)]
        annotations.append({
            "x": 101.5, "y": label, "xref": "x", "yref": "y",
            "text": f"bots {100 * t['bots'] / t['events']:.1f} %",
            "showarrow": False, "xanchor": "left", "font": {"size": 10.5},
        })
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack", "bargap": 0.32,
            "xaxis": {
                "title": {"text": "% de los eventos de su propio flujo y ventana (cada barra = 100 %; unidades no comparables entre flujos)"},
                "range": [0, 134], "tickvals": [0, 25, 50, 75, 100],
                "ticksuffix": "%", "zeroline": False,
            },
            "yaxis": dict({"autorange": "reversed", "tickfont": {"size": 11}},
                          **axis_categories(y_labels)),
            "annotations": annotations,
            "legend": legend_bottom(),
            "margin": {"l": 8, "r": 8, "t": 16, "b": 96},
        },
    }
    columns = [
        column("flow", "Flujo"),
        column("window", "Ventana"),
        column("events", "Eventos totales", "number", "eventos"),
        column("humans", "Con cuenta (no bots)", "number", "eventos"),
        column("bots", "Bots declarados", "number", "eventos"),
        column("unattributed", "Sin cuenta vinculada", "number", "eventos"),
        column("pct_bots", "% bots declarados", "number", "%"),
        column("pct_humans", "% con cuenta (no bots)", "number", "%"),
        column("pct_unatt", "% sin cuenta vinculada", "number", "%"),
    ]
    rows = []
    for flow in FIG5_FLOWS:
        for window in WINDOWS:
            t = flow_totals(overview, flow, window)
            rows.append({
                "flow": FLOWS[flow][0], "window": WINDOW_LABELS[window],
                "events": t["events"], "humans": t["humans"],
                "bots": t["bots"], "unattributed": t["unatt"],
                "pct_bots": round(100 * t["bots"] / t["events"], 1),
                "pct_humans": round(100 * t["humans"] / t["events"], 1),
                "pct_unatt": round(100 * t["unatt"] / t["events"], 1),
            })
    caption = ("Conteos y porcentajes exactos por flujo y ventana (10 filas). "
               "«Revisiones de PR (crudas)» y «Pares únicos revisor–PR» son unidades "
               "distintas: no intercambiarlas ni sumarlas entre flujos.")
    return figure, caption, columns, rows


# ---------------------------------------------------------------------------
# Manifest assembly and validation (port of the theme block's PHP rules).
# ---------------------------------------------------------------------------

FIGMETA = {
    "fig1": {
        "kicker": "ACTIVIDAD OBSERVABLE",
        "title": "¿Cuánta actividad pública observamos?",
        "description": (
            "Eventos públicos registrados en los 35 repositorios atribuidos de esta "
            "instalación, por flujo y ventana (12 y 24 meses hasta el corte exclusivo "
            "2026-10-30T00:00:00Z). Cada flujo cuenta unidades de observación "
            "distintas y no se suman entre sí. Cifras exactas junto a cada barra; la "
            "composición por tipo de cuenta está en la figura 5 y en la tabla."),
        "alt": (
            "Barras horizontales agrupadas de los cuatro flujos de eventos (commits de "
            "rama principal, PR fusionados, revisiones de PR y releases de GitHub) en "
            "dos ventanas (12 y 24 meses), con el total exacto etiquetado junto a cada "
            "barra."),
        "unit": "eventos públicos observados por flujo (unidades no comparables entre flujos)",
        "note": (
            "No sumar flujos: unidades de observación distintas. Cobertura auditada "
            "35/35 repositorios. Fuente: results/overview-totals.json; corte UTC "
            f"exclusivo {CUT_UTC}."),
    },
    "fig2": {
        "kicker": "35 REPOSITORIOS",
        "title": "¿Qué repositorios registraron más commits?",
        "description": (
            "Commits de rama principal sin merges por repositorio, ordenados por "
            "commits no automatizados (cuentas no marcadas como bot, incluidos los "
            "eventos sin cuenta vinculada) y partidos en tres componentes. Recorte de "
            "presentación predefinido: los 15 repositorios con más commits no "
            "automatizados en 12 meses, idénticos en ambas ventanas para poder "
            "comparar; los 35 repositorios —incluidos los de actividad cero o bajo el "
            "umbral— están en la tabla con meses de actividad y último evento no-bot. "
            "El volumen de commits no mide concentración, importancia ni calidad."),
        "alt": (
            "Barras horizontales apiladas por repositorio con tres componentes "
            "(cuentas no identificadas como bots, bots declarados y eventos sin cuenta "
            "vinculada), ordenadas por commits no automatizados, con conmutador entre "
            "ventanas de 12 y 24 meses y el total etiquetado al final de cada barra."),
        "unit": "commits de rama principal sin merges (eventos)",
        "note": (
            "Conmutador 12/24 meses. En 12 m, 2 repositorios registran cero commits de "
            "rama principal (encode/httpcore, python-hyper/h11); en 24 m, ninguno. "
            "Evaluable H1: ≥30 commits no-bot sin merges en la ventana. Fuente: "
            f"results/repo-metrics.csv + results/continuity.csv; corte UTC exclusivo {CUT_UTC}."),
    },
    "fig3": {
        "kicker": "CONCENTRACION (H1/H2)",
        "title": "¿Dónde se concentra más la autoría de commits que la de PR?",
        "description": (
            "Diferencia en puntos porcentuales (pp) entre la cuota top-1 por commits "
            "sin merges no automatizados y la cuota top-1 por PR fusionados a rama "
            "principal, por repositorio evaluable en ambas métricas (18 en 12 m; 25 en "
            "24 m; umbrales preregistrados: ≥30 commits no-bot y ≥10 PR no-bot). "
            "Positivo: más concentración en la autoría de commits; negativo: más "
            "concentración en la autoría de PR. H2 se sigue evaluando con las "
            "categorías preregistradas (≤50 %, >50–75 %, >75 %): 6 de 18 repositorios "
            "cambian de categoría en 12 m y 10 de 25 en 24 m; el delta en pp es "
            "análisis descriptivo editorial y no reemplaza ese contraste. Los 4 casos "
            "con Δ = 0 (rombo gris) son coincidencias exactas por espejo squash —cada "
            "PR fusionado materializa un commit atribuido a la misma autoría—: no son "
            "dos medidas independientes (audits.md, 01-11-2026). Las cuentas "
            "observadas no son necesariamente personas ni mantenedores formales."),
        "alt": (
            "Barras horizontales divergentes centradas en cero por repositorio: hacia "
            "la derecha, más concentración en commits que en PR; hacia la izquierda, "
            "más concentración en PR; valores en puntos porcentuales, con conmutador "
            "entre ventanas de 12 y 24 meses y marcadores de rombo para los cuatro "
            "casos de diferencia cero."),
        "unit": "puntos porcentuales (pp) de diferencia entre cuotas top-1 — análisis descriptivo editorial",
        "note": (
            "Tooltip y tabla: ambas cuotas con numerador y denominador, identidades "
            "top por separado y categorías preregistradas. El scatter original "
            "permanece como suplemento técnico en "
            "figures/fig3-concentracion-commits-vs-pr.html. Fuente: "
            f"results/hypotheses.json (H2) + results/repo-metrics.csv; corte UTC exclusivo {CUT_UTC}."),
    },
    "fig4": {
        "kicker": "SENSIBILIDAD 12/24",
        "title": "¿Cambia la concentración cuando observamos 24 meses?",
        "description": (
            "Cuota top-1 de commits sin merges no automatizados por repositorio, en la "
            "ventana de 12 meses frente a la de 24 (mismo corte exclusivo). 28 "
            "repositorios evaluables en 24 m (≥30 commits no-bot); 22 también en 12 m "
            "— los 6 restantes solo tienen punto de 24 m. H1 en 12 m: 22 evaluables, "
            "15 cuotas numéricas >50 %, 1 inconcluso por la regla preregistrada de "
            "bots (fastapi/fastapi, aspa roja) y 14 conclusivos >50 %; en 24 m: 28 "
            "evaluables, 19 >50 %, 0 inconclusos. Los movimientos entre ventanas son "
            "sensibilidad temporal con reglas fijas, no series mensuales ni tendencias "
            "causales; la cuota no mide «bus factor», riesgo ni abandono, y las "
            "cuentas observadas no son necesariamente personas."),
        "alt": (
            "Gráfico de mancuernas: cada repositorio muestra un punto con la cuota "
            "top-1 de commits en 12 meses (círculo) y otro en 24 meses (cuadrado), "
            "unidos por un conector gris, sobre un eje de 0 a 100 por ciento con "
            "umbrales punteados en 50 y 75 por ciento; el caso inconcluso por la regla "
            "de bots se marca con aspa roja."),
        "unit": "cuota top-1 (% de commits sin merges no automatizados)",
        "note": (
            "Líneas punteadas: umbrales de categoría 50 % y 75 % (preregistrados). Sin "
            "punto en 12 m: no evaluable en esa ventana (<30 commits no-bot); la tabla "
            "lista denominadores, identidades y estado. Fuente: results/hypotheses.json "
            f"(H1); corte UTC exclusivo {CUT_UTC}."),
    },
    "fig5": {
        "kicker": "AUTOMATIZACION",
        "title": "¿Cuánto de lo registrado corresponde a bots declarados?",
        "description": (
            "Composición porcentual de cada flujo de eventos según el tipo de cuenta: "
            "con cuenta no marcada como bot, bot declarado (type=Bot o sufijo [bot] en "
            "la extracción congelada) y sin cuenta vinculada. Cada barra suma 100 % de "
            "su propio flujo y ventana: los porcentajes no son comparables entre "
            "flujos ni se suman. «Revisiones de PR (crudas)» cuenta cada envío de "
            "revisión; «Pares únicos revisor–PR» cuenta una vez por revisor y PR: no "
            "intercambiarlas. Los bots declarados pueden subestimar la automatización "
            "real: hay cuentas type=User con patrones probablemente automatizados no "
            "declarados (ver audits.md). Las cuentas no son necesariamente personas."),
        "alt": (
            "Barras horizontales apiladas al cien por ciento, una por cada combinación "
            "de flujo de eventos (commits, PR fusionados, revisiones crudas, pares "
            "únicos revisor-PR y releases) y ventana (12 y 24 meses), divididas en "
            "bots declarados, cuentas no marcadas como bot y eventos sin cuenta "
            "vinculada, con el porcentaje de bots anotado al final de cada barra."),
        "unit": "% de los eventos del propio flujo y ventana de cada barra",
        "note": (
            "Anotación al final de cada barra: % de bots declarados (12 m: commits "
            "21.3 %, PR 16.8 %, revisiones crudas 24.8 %, pares únicos 28.5 %, "
            "releases 39.3 %). Conteos exactos en la tabla. Fuente: "
            f"results/overview-totals.json; corte UTC exclusivo {CUT_UTC}."),
    },
}


def make_manifest(fig_id, figure, caption, columns, rows, generated_at, commit):
    meta = dict(FIGMETA[fig_id])
    analysis = {"repository": REPOSITORY, "path": ANALYSIS_PATH}
    methodology_ref = commit or "research/deudamundi-dependencies"
    if commit:
        analysis["commit"] = commit
    source_file = {
        "fig1": "overview-totals.json",
        "fig2": "repo-metrics.csv",
        "fig3": "hypotheses.json",
        "fig4": "hypotheses.json",
        "fig5": "overview-totals.json",
    }[fig_id]
    return {
        "schemaVersion": 1,
        "meta": {
            "title": meta["title"],
            "kicker": meta["kicker"],
            "description": meta["description"],
            "alt": meta["alt"],
            "unit": meta["unit"],
            "sources": [{
                "label": (
                    "Cálculos propios con datos públicos de GitHub; "
                    "extracción congelada del 30-10-2026 (443 JSON, 35 repositorios)"
                ),
                "url": f"{REPOSITORY}/commit/{SOURCE_COMMIT}",
            }],
            "methodology": {
                "label": "Plan preregistrado del paso 5",
                "url": f"{REPOSITORY}/blob/{methodology_ref}/{METHODOLOGY_PATH}",
            },
            "analysis": analysis,
            "generatedAt": generated_at,
            "note": f"{meta['note']} Datos derivados de results/{source_file}.",
        },
        "figure": figure,
        "config": {"displayModeBar": False},
        "table": {"caption": caption, "columns": columns, "rows": rows},
    }


def validate_manifest(manifest):
    """Local port of the theme block rules (plotly-figure.php) + strict JSON."""
    assert manifest["schemaVersion"] == 1
    meta = manifest["meta"]
    for field in ("title", "alt"):
        assert isinstance(meta.get(field), str) and meta[field], field
    assert isinstance(meta.get("sources"), list) and meta["sources"]
    for source in meta["sources"]:
        assert isinstance(source.get("label"), str) and source["label"]
    figure = manifest["figure"]
    assert isinstance(figure.get("data"), list) and figure["data"]
    assert isinstance(figure.get("layout"), dict)
    if "frames" in figure:
        assert isinstance(figure["frames"], list)
    assert isinstance(manifest.get("config", {}), dict)
    table = manifest["table"]
    assert isinstance(table.get("columns"), list) and table["columns"]
    assert isinstance(table.get("rows"), list)
    keys = []
    for item in table["columns"]:
        assert isinstance(item.get("key"), str) and item["key"]
        assert isinstance(item.get("label"), str) and item["label"]
        assert item.get("type", "string") in {
            "string", "number", "boolean", "date", "datetime"}
        keys.append(item["key"])
    assert len(keys) == len(set(keys))
    for row in table["rows"]:
        assert isinstance(row, dict)
        assert set(row) == set(keys)
        for value in row.values():
            assert value is None or isinstance(value, (str, int, float, bool))
            if isinstance(value, float):
                assert value == value and abs(value) != float("inf")
    encoded = json.dumps(manifest, ensure_ascii=False, allow_nan=False)
    assert len(encoded.encode("utf-8")) <= 5 * 1024 * 1024
    return encoded


def main():
    overview, hypotheses, metrics, continuity, frozen = load_frozen()
    print("Contrastes contra datos congelados y cifras del dictamen:")
    for line in crosscheck(overview, hypotheses, metrics, frozen):
        print(f"  PASS · {line}")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = analysis_commit()
    builds = {
        "fig1": lambda: build_fig1(overview),
        "fig2": lambda: build_fig2(metrics, continuity, hypotheses),
        "fig3": lambda: build_fig3(hypotheses, metrics),
        "fig4": lambda: build_fig4(hypotheses, metrics, frozen["fig4"]),
        "fig5": lambda: build_fig5(overview),
    }
    OUT.mkdir(exist_ok=True)
    index = []
    for fig_id in ("fig1", "fig2", "fig3", "fig4", "fig5"):
        figure, caption, columns, rows = builds[fig_id]()
        manifest = make_manifest(fig_id, figure, caption, columns, rows,
                                 generated_at, commit)
        encoded = validate_manifest(manifest)
        filename = f"{fig_id}.json"
        (OUT / filename).write_text(encoded + "\n", encoding="utf-8")
        index.append({
            "figure": fig_id,
            "file": filename,
            "title": FIGMETA[fig_id]["title"],
            "sha256": hashlib.sha256((encoded + "\n").encode("utf-8")).hexdigest(),
        })
    (OUT / "index.json").write_text(
        json.dumps({"schemaVersion": 1, "figures": index},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifiestos Econopapi v1 (figuras v2, dictamen §5): {len(index)} -> {OUT}")
    for item in index:
        print(f"  {item['figure']}: {item['file']} ({item['sha256'][:12]}…) «{item['title']}»")


if __name__ == "__main__":
    main()
