#!/usr/bin/env python3
"""Export the step-5 figures as portable JSON payloads (canonical contract).

This is the ONLY output bridge between versioned research results and any
renderer (the econopapi theme block, future viewers). Deterministic: reading
results/figure-meta.json produced by make_figures.py, it writes one file per
figure plus index.json into results/plotly-embed/, and nothing else. No fonts,
no plotly, no WordPress code. The history of the previous WordPress bridge
(wp-block-plugin/, wp-snippets/, removed at the author's request on 2026-10-31)
remains auditable in Git.

Contract for a plotly block:
  payload = {
    "figure", "attributes": {figure}, …
    "meta": {kicker, title, subtitle, alt, provenance_extra,
             table_head, table_body},
    "data": {...},        # the same object the figures/figN HTML renders
    "source": {branch, cut_utc, results_dir}
  }

Run from the repository root:
    python research/dependencies/maintenance/analysis/export_payloads.py
"""

import json
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = RESULTS / "plotly-embed"


def main():
    meta = json.loads((RESULTS / "figure-meta.json").read_text(encoding="utf-8"))
    keys_by_id = {}
    for m in meta:
        keys_by_id[m["id"]] = None
    OUT.mkdir(exist_ok=True)
    index = []
    for m in meta:
        payload = {
            "figure": m["id"],
            "attributes": {"figure": m["id"]},
            "meta": {
                "kicker": m["kicker"], "title": m["title"],
                "subtitle": m["subtitle"], "alt": m["alt"],
                "provenance_extra": m["provenance_extra"],
                "table_head": m["table_head"], "table_body": m["table_body"],
            },
            # the renderer (theme block) implements the chart type; the payload
            # is data-only by design decision of 2026-10-31
            "chart_hint": {
                "1": "hbar-4streams-by-window",
                "2": "hbar-35repos-stacked-commits",
                "3": "scatter-with-updatemenu-12/24",
                "4": "slope-12-24",
                "5": "hbar-pct-bots",
            }[m["id"][3]],
            "data": m["data"],
            "source": {
                "branch": "research/deudamundi-dependencies",
                "cut_utc": "2026-10-30T00:00:00Z",
                "results": "maintenance/analysis/results",
                "note": "regenerable without network from the 443 frozen JSONs "
                        "via analyze_activity.py + make_figures.py",
            },
        }
        h = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        payload["sha256_payload"] = h
        (OUT / (m["id"] + ".json")).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        index.append({"figure": m["id"], "file": m["id"] + ".json",
                      "title": m["title"], "sha256_payload": h})
    (OUT / "index.json").write_text(
        json.dumps({"figures": index,
                    "contract_version": 1,
                    "brand": "Econopapi (tokens por tema en el bloque)",
                    },
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"payloads: {len(index)} figuras -> {OUT}")
    for e in index:
        print(f"  {e['figure']}: {e['file']} ({e['sha256_payload'][:12]}…)")


if __name__ == "__main__":
    main()
