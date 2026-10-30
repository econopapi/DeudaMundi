#!/usr/bin/env python3
"""Step-5/H3 evidence: PyPI release history for the 37 runtime distributions.

Requested in plan.md after the plan commit and before running the H3 test.
Records one JSON per distribution with the query receipt (URL, UTC instant,
HTTP status, body SHA-256), the version dates needed for the 12m/24m windows
and nothing else (no owner data, no description bodies).

Run from the repository root:
    python research/dependencies/maintenance/analysis/collect_pypi.py
"""

import csv
import datetime as dt
import hashlib
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "attributions" / "source-repos.csv"
OUT = HERE / "pypi-evidence"
START_24 = "2024-10-30T00:00:00Z"
START_12 = "2025-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"


def fetch(name):
    url = f"https://pypi.org/pypi/{name}/json"
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "DeudaMundi-research/step5 (github.com/econopapi/DeudaMundi)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            status = r.status
    except Exception as e:  # noqa: BLE001 — evidence file records the failure
        body, status = b"", None
        error = repr(e)
    else:
        error = None
    receipt = {
        "url": url,
        "method": "GET",
        "consulted_at_utc": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "http_status": status,
        "error": error,
        "body_sha256": hashlib.sha256(body).hexdigest() if body else None,
        "body_bytes": len(body),
    }
    if not body:
        return {"distribution": name, "unavailable": True, "request": receipt}
    data = json.loads(body)
    versions = {}
    for version, files in (data.get("releases") or {}).items():
        dates = [f.get("upload_time_iso_8601") or f.get("upload_time")
                 for f in files if f.get("upload_time")]
        if dates:
            versions[version] = min(dates)  # earliest upload of that version
    return {
        "distribution": name,
        "unavailable": False,
        "request": receipt,
        "total_versions": data.get("info", {}).get("version") and len(versions),
        "latest_version_at_query": data.get("info", {}).get("version"),
        "versions_published_at": versions,
    }


def in_window(date, start):
    return date is not None and start <= date < END


def main():
    OUT.mkdir(exist_ok=True)
    with SOURCE.open(newline="", encoding="utf-8") as f:
        dists = []
        seen = set()
        for row in csv.DictReader(f):
            name = row["name"]
            if name in seen:
                continue
            seen.add(name)
            dists.append(name)
    assert len(dists) == 37, f"expected 37 dists, got {len(dists)}"
    summary = []
    for i, name in enumerate(dists):
        path = OUT / f"{name}.json"
        data = fetch(name)
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                        encoding="utf-8")
        rec = {"distribution": name,
               "unavailable": data["unavailable"],
               "published_12m": False,
               "published_24m": False,
               "latest_before_cut":
                   None if data["unavailable"] else data.get("latest_version_at_query")}
        if not data["unavailable"]:
            for date in data["versions_published_at"].values():
                rec["published_12m"] |= in_window(date, START_12)
                rec["published_24m"] |= in_window(date, START_24)
        summary.append(rec)
        print(f"[{i + 1}/{len(dists)}] {name:22s} 12m={rec['published_12m']} "
              f"24m={rec['published_24m']}")
        time.sleep(1.0)
    (OUT / "h3-summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for r in summary if not r["unavailable"])
    print(f"done: {ok}/{len(dists)} distributions archived")


if __name__ == "__main__":
    main()
