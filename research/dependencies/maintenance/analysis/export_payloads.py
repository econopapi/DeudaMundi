#!/usr/bin/env python3
"""Export the step-5 figures as Econopapi Plotly manifests (schema v1).

Reads results/figure-meta.json produced by make_figures.py and writes one
uploadable manifest per figure plus index.json into results/plotly-embed/.
The figure definitions are native Plotly data/layout objects; visual identity
(light/dark palette, fonts, grids and hovers) remains the theme block's job.

Run from the repository root:
    python research/dependencies/maintenance/analysis/export_payloads.py
"""

import hashlib
import html
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = RESULTS / "plotly-embed"

REPOSITORY = "https://github.com/econopapi/DeudaMundi"
SOURCE_COMMIT = "1363af84d5089ca4260645012dcb34ccc93d4c6c"
CUT_UTC = "2026-10-30T00:00:00Z"
ANALYSIS_PATH = "research/dependencies/maintenance/analysis/export_payloads.py"
METHODOLOGY_PATH = "research/dependencies/maintenance/analysis/plan.md"

ACTOR_NAMES = {
    "h": "Con cuenta (no bots)",
    "b": "Bots declarados",
    "u": "Sin cuenta vinculada",
}
UNITS = {
    "fig1": "eventos públicos observados",
    "fig2": "eventos (commits no fusionados)",
    "fig3": "proporción (0–1)",
    "fig4": "proporción (0–1)",
    "fig5": "porcentaje de eventos del flujo",
}


def analysis_commit():
    """Identify the analysis snapshot when exporting from a Git checkout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def plain_text(value):
    """Metadata is escaped by PHP, so remove presentational HTML from old meta."""
    return html.unescape(re.sub(r"<[^>]+>", "", value))


def rows_by(rows, key):
    """Keep the first occurrence of each category in the original plot order."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row[key], row)
    return grouped


def column(key, label, kind="string", unit=None):
    result = {"key": key, "label": label, "type": kind}
    if unit is not None:
        result["unit"] = unit
    return result


def event_columns(first_key, first_label):
    return [
        column(first_key, first_label),
        column("events", "Eventos totales", "number", "eventos"),
        column("humans", "Con cuenta (no bots)", "number", "eventos"),
        column("bots", "Bots declarados", "number", "eventos"),
        column("unattributed", "Sin cuenta vinculada", "number", "eventos"),
    ]


def build_fig1(data):
    traces = []
    for key in ("h", "b", "u"):
        selected = [row for row in data["rows"] if row["k"] == key]
        traces.append({
            "type": "bar",
            "orientation": "h",
            "name": ACTOR_NAMES[key],
            "x": [row["n"] for row in selected],
            "y": [row["label"] for row in selected],
            "customdata": [
                [row["total"], row["humans"], row["bots"], row["unatt"]]
                for row in selected
            ],
            "hovertemplate": (
                "%{y}<br>%{x} eventos (" + ACTOR_NAMES[key] + ")<br>"
                "Total del flujo: %{customdata[0]}<br>"
                "Con cuenta: %{customdata[1]} · Bots: %{customdata[2]} · "
                "Sin cuenta: %{customdata[3]}<extra></extra>"
            ),
        })
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack",
            "xaxis": {"title": {"text": "eventos públicos"}},
            "yaxis": {"autorange": "reversed"},
            "legend": {"orientation": "h", "traceorder": "normal"},
        },
    }
    columns = event_columns("flow_window", "Flujo · ventana")
    rows = [
        {
            "flow_window": label,
            "events": row["total"],
            "humans": row["humans"],
            "bots": row["bots"],
            "unattributed": row["unatt"],
        }
        for label, row in rows_by(data["rows"], "label").items()
    ]
    return figure, columns, rows


def build_fig2(data):
    traces = []
    for key in ("h", "b", "u"):
        selected = [row for row in data["rows"] if row["k"] == key]
        traces.append({
            "type": "bar",
            "orientation": "h",
            "name": ACTOR_NAMES[key],
            "x": [row["n"] for row in selected],
            "y": [row["repo"] for row in selected],
            "customdata": [
                [
                    row["humans"], row["bots"], row["unatt"],
                    int(row["prs"]), int(row["prs_bots"]),
                    int(row["rel"]), int(row["rel_bots"]),
                ]
                for row in selected
            ],
            "hovertemplate": (
                "<b>%{y}</b><br>" + ACTOR_NAMES[key] +
                ": %{x} commits no fusionados<br>"
                "Commits con cuenta: %{customdata[0]} · Bots: %{customdata[1]} · "
                "Sin cuenta: %{customdata[2]}<br>"
                "PR fusionados en 12 m: %{customdata[3]} (bots: %{customdata[4]})<br>"
                "Releases 12 m: %{customdata[5]} (bots: %{customdata[6]})"
                "<extra></extra>"
            ),
        })
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack",
            "xaxis": {
                "title": {"text": "commits no fusionados en 12 meses (eventos)"},
            },
            "yaxis": {"autorange": "reversed"},
            "legend": {"orientation": "h"},
        },
    }
    columns = [
        column("repository", "Repositorio"),
        column("commits", "Commits no fusionados (12 m)", "number", "commits"),
        column("humans", "Con cuenta (no bots)", "number", "commits"),
        column("bots", "Bots declarados", "number", "commits"),
        column("unattributed", "Sin cuenta vinculada", "number", "commits"),
        column("merged_prs", "PR fusionados (12 m)", "number", "PR"),
        column("releases", "Releases (12 m)", "number", "releases"),
    ]
    rows = []
    for repo, row in rows_by(data["rows"], "repo").items():
        commits = row["humans"] + row["bots"] + row["unatt"]
        rows.append({
            "repository": repo,
            "commits": commits,
            "humans": row["humans"],
            "bots": row["bots"],
            "unattributed": row["unatt"],
            "merged_prs": int(row["prs"]),
            "releases": int(row["rel"]),
        })
    return figure, columns, rows


def build_fig3(data, hypotheses):
    traces = []
    for window, visible in (("12m", True), ("24m", False)):
        selected = [row for row in data["rows"] if row["window"] == window]
        traces.append({
            "type": "scatter",
            "mode": "markers+text",
            "name": window,
            "visible": visible,
            "x": [row["c_commit"] for row in selected],
            "y": [row["c_pr"] for row in selected],
            "text": [row["repo_label"] for row in selected],
            "textposition": "top center",
            "marker": {"size": 9},
            "customdata": [row["tip"] for row in selected],
            "hovertemplate": (
                "<b>%{text}</b> (" + window + ")<br>"
                "Cuota commits: %{x:.4f}<br>"
                "Cuota PR fusionados: %{y:.4f}<br>"
                "%{customdata}<extra></extra>"
            ),
        })
    figure = {
        "data": traces,
        "layout": {
            "showlegend": False,
            "xaxis": {
                "range": [0, 1.02],
                "title": {"text": "cuota top-1 por commits no fusionados (0–1)"},
            },
            "yaxis": {
                "range": [0, 1.02],
                "title": {"text": "cuota top-1 por PR a rama principal (0–1)"},
            },
            "shapes": [
                {"type": "line", "x0": 0, "x1": 1, "y0": 0, "y1": 1},
            ] + [
                {
                    "type": "line", "x0": value, "x1": value,
                    "y0": 0, "y1": 1.02, "yref": "paper",
                    "line": {"dash": "dot"},
                }
                for value in (0.5, 0.75)
            ],
            "updatemenus": [{
                "type": "buttons",
                "direction": "right",
                "x": 0,
                "y": 1.12,
                "xanchor": "left",
                "yanchor": "top",
                "active": 0,
                "buttons": [
                    {
                        "label": "12 meses",
                        "method": "restyle",
                        "args": [{"visible": [True, False]}],
                    },
                    {
                        "label": "24 meses",
                        "method": "restyle",
                        "args": [{"visible": [False, True]}],
                    },
                ],
            }],
            "annotations": [{
                "x": 0.94,
                "y": 0.06,
                "xref": "x",
                "yref": "y",
                "text": "misma cuota",
                "showarrow": False,
            }],
        },
    }
    columns = [
        column("repository_window", "Repositorio · ventana"),
        column("commit_share", "Cuota commits", "number", "proporción (0–1)"),
        column("commit_category", "Categoría commits"),
        column("pr_share", "Cuota PR", "number", "proporción (0–1)"),
        column("pr_category", "Categoría PR"),
    ]
    rows = []
    for window in ("12m", "24m"):
        for row in hypotheses["windows"][window]["H2"]:
            rows.append({
                "repository_window": f"{row['repo']} · {window}",
                "commit_share": row["commit_share"],
                "commit_category": row["commit_cat"],
                "pr_share": row["pr_share"],
                "pr_category": row["pr_cat"],
            })
    return figure, columns, rows


def build_fig4(data):
    traces = []
    for repo in data["repos"]:
        series = data["series"][repo]
        over = series["12m"] > 0.5 and series["24m"] > 0.5
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "name": repo,
            "showlegend": False,
            "x": [0, 1],
            "y": [series["12m"], series["24m"]],
            "customdata": ["12 meses", "24 meses"],
            "line": {"width": 2 if over else 1.2},
            "marker": {"size": 6},
            "opacity": 0.85 if over else 0.4,
            "hovertemplate": (
                "<b>" + repo + "</b><br>%{customdata}: %{y:.3f}<extra></extra>"
            ),
        })
    figure = {
        "data": traces,
        "layout": {
            "showlegend": False,
            "xaxis": {
                "range": [-0.15, 1.15],
                "tickvals": [0, 1],
                "ticktext": ["12 meses", "24 meses"],
                "title": {"text": "ventana"},
            },
            "yaxis": {
                "range": [0, 1.02],
                "title": {"text": "cuota top-1 por commits no fusionados (0–1)"},
            },
            "shapes": [
                {
                    "type": "line", "x0": 0, "x1": 1,
                    "y0": value, "y1": value, "yref": "y",
                    "line": {"dash": "dot"},
                }
                for value in (0.5, 0.75)
            ],
        },
    }
    columns = [
        column("repository", "Repositorio"),
        column("share_12m", "Cuota 12 m", "number", "proporción (0–1)"),
        column("share_24m", "Cuota 24 m", "number", "proporción (0–1)"),
    ]
    rows = [
        {
            "repository": repo,
            "share_12m": data["series"][repo]["12m"],
            "share_24m": data["series"][repo]["24m"],
        }
        for repo in data["repos"]
    ]
    return figure, columns, rows


def build_fig5(data):
    share_keys = {"b": "bot_share", "h": "humans_share", "u": "unatt_share"}
    traces = []
    for key in ("b", "h", "u"):
        selected = [row for row in data["rows"] if row["k"] == key]
        traces.append({
            "type": "bar",
            "orientation": "h",
            "name": ACTOR_NAMES[key],
            "x": [row[share_keys[key]] for row in selected],
            "y": [row["label"] for row in selected],
            "customdata": [
                [row["total"], row["bots"], row["humans"], row["unatt"]]
                for row in selected
            ],
            "hovertemplate": (
                "%{y}<br>" + ACTOR_NAMES[key] + ": %{x:.1f}% de eventos<br>"
                "Totales: %{customdata[0]} eventos; bots %{customdata[1]}; "
                "con cuenta %{customdata[2]}; sin cuenta %{customdata[3]}"
                "<extra></extra>"
            ),
        })
    figure = {
        "data": traces,
        "layout": {
            "barmode": "stack",
            "bargap": 0.35,
            "xaxis": {
                "range": [0, 100],
                "ticksuffix": "%",
                "title": {"text": "porcentaje de los eventos del flujo"},
            },
            "yaxis": {"autorange": "reversed"},
            "legend": {"orientation": "h"},
        },
    }
    columns = event_columns("flow_window", "Flujo · ventana") + [
        column("bot_share", "% bots", "number", "%"),
        column("humans_share", "% con cuenta", "number", "%"),
        column("unattributed_share", "% sin cuenta", "number", "%"),
    ]
    rows = [
        {
            "flow_window": label,
            "events": row["total"],
            "humans": row["humans"],
            "bots": row["bots"],
            "unattributed": row["unatt"],
            "bot_share": row["bot_share"],
            "humans_share": row["humans_share"],
            "unattributed_share": row["unatt_share"],
        }
        for label, row in rows_by(data["rows"], "label").items()
    ]
    return figure, columns, rows


def make_manifest(meta, figure, columns, rows, generated_at, commit):
    analysis = {"repository": REPOSITORY, "path": ANALYSIS_PATH}
    methodology_ref = commit or "research/deudamundi-dependencies"
    if commit:
        analysis["commit"] = commit
    metadata = {
        "title": meta["title"],
        "kicker": meta["kicker"],
        "description": plain_text(meta["subtitle"]),
        "alt": plain_text(meta["alt"]),
        "unit": UNITS[meta["id"]],
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
    }
    source_file = {
        "fig1": "overview-totals.json",
        "fig2": "repo-metrics.csv",
        "fig3": "hypotheses.json",
        "fig4": "hypotheses.json",
        "fig5": "overview-totals.json",
    }[meta["id"]]
    metadata["note"] = (
        f"Corte UTC exclusivo: {CUT_UTC}. Datos derivados de results/{source_file}."
    )
    return {
        "schemaVersion": 1,
        "meta": metadata,
        "figure": figure,
        "config": {"displayModeBar": False},
        "table": {
            "caption": "Datos representados en la figura",
            "columns": columns,
            "rows": rows,
        },
    }


def validate_manifest(manifest):
    """Fail locally instead of uploading a manifest the block must reject."""
    assert manifest["schemaVersion"] == 1
    assert manifest["meta"]["title"] and manifest["meta"]["alt"]
    assert any(source.get("label") for source in manifest["meta"]["sources"])
    assert isinstance(manifest["figure"]["data"], list)
    assert isinstance(manifest["figure"]["layout"], dict)
    columns = manifest["table"]["columns"]
    keys = [item["key"] for item in columns]
    assert len(keys) == len(set(keys))
    assert all(item.get("label") for item in columns)
    assert all(item.get("type", "string") in {
        "string", "number", "boolean", "date", "datetime",
    } for item in columns)
    for row in manifest["table"]["rows"]:
        assert set(row) == set(keys)
        assert all(value is None or isinstance(value, (str, int, float, bool))
                   for value in row.values())
    encoded = json.dumps(manifest, ensure_ascii=False, allow_nan=False)
    assert len(encoded.encode("utf-8")) <= 5 * 1024 * 1024


def main():
    metadata = json.loads((RESULTS / "figure-meta.json").read_text(encoding="utf-8"))
    hypotheses = json.loads((RESULTS / "hypotheses.json").read_text(encoding="utf-8"))
    builders = {
        "fig1": lambda data: build_fig1(data),
        "fig2": lambda data: build_fig2(data),
        "fig3": lambda data: build_fig3(data, hypotheses),
        "fig4": lambda data: build_fig4(data),
        "fig5": lambda data: build_fig5(data),
    }
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = analysis_commit()
    OUT.mkdir(exist_ok=True)
    index = []
    for meta in metadata:
        figure, columns, rows = builders[meta["id"]](meta["data"])
        manifest = make_manifest(meta, figure, columns, rows, generated_at, commit)
        validate_manifest(manifest)
        content = json.dumps(
            manifest, ensure_ascii=False, allow_nan=False, indent=2,
        ) + "\n"
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        filename = f"{meta['id']}.json"
        (OUT / filename).write_text(content, encoding="utf-8")
        index.append({
            "figure": meta["id"],
            "file": filename,
            "title": meta["title"],
            "sha256": digest,
        })
    (OUT / "index.json").write_text(
        json.dumps(
            {"schemaVersion": 1, "figures": index},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"manifiestos Econopapi v1: {len(index)} figuras -> {OUT}")
    for item in index:
        print(f"  {item['figure']}: {item['file']} ({item['sha256'][:12]}…)")


if __name__ == "__main__":
    main()
