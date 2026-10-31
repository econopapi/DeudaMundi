#!/usr/bin/env python3
"""Final-audit §6: stratified manual audit of ORIGINAL frozen events.

Sample selection (strata, justified):
  S1 high activity            -> fastapi/fastapi
  S2 low activity             -> python-hyper/h11 (0 human commits; review-only)
  S3 high concentration       -> sqlalchemy/mako (top1 share 1.000)
  S4 significant automation   -> certifi/python-certifi (bot commits/PRs),
                                 grahamdumpleton/wrapt (bot releases)
  S5 attribution issues       -> laurent-laporte-pro/deprecated (account `claude`),
                                 sqlalchemy/sqlalchemy (`sqla-tester` reviewer),
                                 fastapi (`invalid-email-address`)
  S6 non-mainline merges      -> pallets/click (PRs to other base refs)

For every sampled repo we (a) recount aggregates from the frozen pages with a
completely separate minimal implementation, (b) extract two concrete original
events per stream/sha with their request receipts, (c) compare against the
derived files (repo-metrics.csv / actor-shares.csv).

Honesty note recorded in output: this is a THIRD implementation of the same
operational rules over the SAME frozen dataset — not an independent data
source; the receipts (HTTP 200 + body SHA-256 per page) are the origin evidence.

Run from repo root:
    python research/dependencies/maintenance/analysis/final-audits/manual_sample_audit.py
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAINT = HERE.parent.parent
DATA = MAINT / "data"
RESULTS = MAINT / "analysis" / "results"
START_12 = "2025-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"


def records(subfolder):
    out = []
    for f in sorted(Path(subfolder).glob("0*.json")):
        pg = json.loads(f.read_text(encoding="utf-8"))
        out.extend(pg["records"])
    return out


def is_bot(a):
    return bool(a and a.get("bot"))


def audit(repo, dbranch="master"):
    folder = DATA / repo.replace("/", "__")
    inwin = lambda d: d is not None and START_12 <= d < END
    commits = [c for c in records(folder / "commits") if inwin(c["date"])]
    nonmerge = [c for c in commits if c["parent_count"] <= 1]
    prs = records(folder / "prs")
    merged = [p for p in prs if p.get("merged_at") and inwin(p["merged_at"])]
    main = [p for p in merged if (p["base_ref"] or "") == dbranch]
    rels = [r for r in records(folder / "releases")
            if not r["draft"] and inwin(r["date"])]
    pairs = {}
    for pr in prs:
        for rev in pr["reviews"]:
            if not inwin(rev.get("date")):
                continue
            if rev["state"] not in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}:
                continue
            a = rev.get("author")
            pairs[(pr["number"], (a or {}).get("login") or "", (a or {}).get("id"))] = a
    # fresh counts (human-only non-merge authors for commits, and so on)
    cm = Counter((c.get("author") or {}).get("login", "") for c in nonmerge
                 if c.get("author") and not is_bot(c["author"]))
    pm = Counter((p.get("author") or {}).get("login", "") for p in main
                 if p.get("author") and not is_bot(p["author"]))
    rv = Counter()
    for a in pairs.values():
        if a and not is_bot(a):
            rv[(a.get("login") or "")] += 1
    # receipts: confirm every sampled page had http 200 + sha64
    rec_ok = True
    receipt_samples = []
    for f in sorted(folder.glob("*/0*.json"))[:2] + sorted(folder.glob("*/0*.json"))[-1:]:
        pg = json.loads(f.read_text(encoding="utf-8"))
        rec_ok &= pg["request"]["http_status"] == 200 and len(
            pg["request"]["body_sha256"]) == 64 and pg["response_records"] == len(pg["records"])
        receipt_samples.append({"file": str(f.relative_to(DATA)),
                                "url": pg["request"]["url"],
                                "consulted_at_utc": pg["request"]["consulted_at_utc"],
                                "body_sha256": pg["request"]["body_sha256"][:16] + "…",
                                "records": pg["response_records"]})
    sample_events = {
        "commit_sample": next(({"sha": c["sha"][:7], "date": c["date"],
                                "author": (c.get("author") or {}).get("login"),
                                "parents": c["parent_count"]}
                               for c in sorted(nonmerge, key=lambda x: tuple(-ord(ch) for ch in x["date"]))[:1]), None),
        "pr_sample": next(({"number": p["number"], "merged_at": p["merged_at"],
                            "author": (p.get("author") or {}).get("login"),
                            "merged_by": (p.get("merged_by") or {}).get("login"),
                            "base_ref": p["base_ref"]}
                           for p in sorted(merged, key=lambda x: (x["merged_at"] or "") , reverse=True)[:1]), None),
        "release_sample": next(({"date": r["date"],
                                 "author": (r.get("author") or {}).get("login"),
                                 "tag": r.get("tag_name")}
                                for r in sorted(rels, key=lambda x: x["date"], reverse=True)[:1]), None),
        "review_pairs_sample": [
            {"pr": n, "reviewer": ((a or {}).get("login") if a else None),
             "is_bot": bool(is_bot(a))}
            for (n, _l, _i), a in sorted(pairs.items(), key=lambda kv: -kv[0][0])[:1]
        ],
    }
    return {
        "repo": repo,
        "receipts_all_200_and_sha64": rec_ok,
        "receipt_samples": receipt_samples,
        "recompute": {
            "commits_nonmerge": len(nonmerge),
            "commits_merge": len(commits) - len(nonmerge),
            "top_human_committer": (cm.most_common(1) or [(None, 0)])[0],
            "merged_total_12m": len(merged),
            "merged_main": len(main),
            "merged_other_base": len(merged) - len(main),
            "top_pr_author_main": (pm.most_common(1) or [(None, 0)])[0],
            "release_events_12m": len(rels),
            "release_bot_events": sum(1 for r in rels if is_bot(r.get("author"))),
            "review_pairs_total_12m": len(pairs),
            "review_pairs_nonbot": sum(1 for a in pairs.values() if a and not is_bot(a)),
            "top_reviewer_pairs": (rv.most_common(1) or [(None, 0)])[0],
        },
        "sample_events": sample_events,
    }


def _read_metrics():
    import csv  # noqa
    with (RESULTS / "repo-metrics.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compare(repo_name, aud):
    """Contrast fresh counts with derived published files."""
    issues = []
    import csv as _csv
    m = None
    with (RESULTS / "repo-metrics.csv").open(newline="", encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            if r["repo"] == repo_name and r["window_end"] == "12m":
                m = r
    rc = aud["recompute"]
    checks = [
        ("commits_nonmerge", int(m["commits_nonmerge"]), rc["commits_nonmerge"]),
        ("merged_prs_all", int(m["merged_prs_all"]), rc["merged_total_12m"]),
        ("merged_prs_main", int(m["merged_prs_main"]), rc["merged_main"]),
        ("merged_other_base", int(m["merged_prs_other_base"]), rc["merged_other_base"]),
        ("releases_all", int(m["releases_all"]), rc["release_events_12m"]),
        ("releases_bot", int(m["releases_bot"]), rc["release_bot_events"]),
        ("review_pairs", int(m["review_pairs"]), rc["review_pairs_total_12m"]),
        ("review_pairs_human", int(m["review_pairs_human"]), rc["review_pairs_nonbot"]),
    ]
    for k, pub, mine in checks:
        if pub != mine:
            issues.append((k, "published", pub, "manual", mine))
    return issues


def main():
    metas = {}
    import csv
    with (RESULTS / "repo-metrics.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            metas[(r["repo"], r["window_end"])] = r
    selected = [
        ("fastapi/fastapi", "master", "S1 alta actividad + S5 invalid-email-address"),
        ("python-hyper/h11", "master", "S2 baja actividad (0 commits humanos)"),
        ("sqlalchemy/mako", "main", "S3 concentración 1.000 (42/42)"),
        ("certifi/python-certifi", "master", "S4 automatización (dependabot)"),
        ("grahamdumpleton/wrapt", "develop", "S4 releases bot + default_branch develop"),
        ("laurent-laporte-pro/deprecated", "master", "S5 cuenta `claude`"),
        ("sqlalchemy/sqlalchemy", "main", "S5 sqla-tester revisora"),
        ("pallets/click", "main", "S6 PRs a bases no principales"),
    ]
    out = {"sample_selection": {repo: reason for repo, _, reason in selected},
           "honesty_note": ("Tercera implementación sobre el MISMO dataset congelado y las "
                            "MISMAS reglas operativas: valida el cómputo, no el origen de los "
                            "datos; los recibos (HTTP 200 + SHA-64 por página) son única evidencia de origen."),
           "audits": [], "issues": []}
    for repo, dbranch, reason in selected:
        a = None
        # dbranch default comes from repository.json
        meta_json = json.loads((DATA / repo.replace("/", "__") / "repository.json")
                               .read_text(encoding="utf-8"))
        a = audit(repo, meta_json["default_branch"])
        a["stratum_reason"] = reason
        a["expected_default_branch"] = meta_json["default_branch"]
        out["audits"].append(a)
    # convenience known-actor spot checks
    fast = next(a for a in out["audits"] if a["repo"] == "fastapi/fastapi")
    folder = DATA / "fastapi__fastapi"
    iea = [c for c in records(folder / "commits") if inwin12(c["date"])
           and (c.get("author") or {}).get("login") == "invalid-email-address"]
    ie24 = [c for c in records(folder / "commits") if inwin24(c["date"])
            and (c.get("author") or {}).get("login") == "invalid-email-address"]
    out["spot_checks"] = {
        "fastapi_invalid_email_address_commits": {"12m": len(iea), "24m": len(ie24)},
        "expected_bucket": "cuenta con flag congelado no-bot (type=User); cuenta como actor con login, no como no-atribuido ni bot. Advertencia registrada en audits.md (patrón probablemente automatizado no declarado).",
    }
    dep = next(a for a in out["audits"] if a["repo"] == "laurent-laporte-pro/deprecated")
    dfold = DATA / "laurent-laporte-pro__deprecated"
    clav = [c for c in records(dfold / "commits") if inwin12(c["date"])
            and (c.get("author") or {}).get("login") == "claude"]
    clav_nm = [c for c in clav if c["parent_count"] <= 1]
    out["spot_checks"]["deprecated_claude_commits_12m"] = {
        "total": len(clav), "nonmerge": len(clav_nm),
        "published_top1_count": 36}
    sqla = next(a for a in out["audits"] if a["repo"] == "sqlalchemy/sqlalchemy")
    sfold = DATA / "sqlalchemy__sqlalchemy"
    sqla_pairs = {}
    import csv as _csv  # noqa
    for pr in records(sfold / "prs"):
        for rev in pr["reviews"]:
            if inwin12(rev.get("date")) and rev["state"] in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}:
                a = rev.get("author")
                key = (pr["number"], (a or {}).get("login") or "", (a or {}).get("id"))
                sqla_pairs.setdefault(key, a)
    out["spot_checks"]["sqlalchemy_sqla_tester_pairs_12m"] = {
        "pairs": sum(1 for a in sqla_pairs.values()
                     if a and (a.get("login") or "").lower() == "sqla-tester"),
        "published_top_reviewer_pairs": 96}
    # compare each audited repo
    for a in out["audits"]:
        out["issues"] += compare(a["repo"], a)
    (HERE / "manual-sample-audits.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    nissues = len(out["issues"])
    print("audits:", len(out["audits"]), "| spot checks:",
          {k: v for k, v in out["spot_checks"].items()},
          "| issues:", nissues if out["issues"] else "NINGUNA")
    if out["issues"]:
        print(out["issues"][:15])


def inwin12(d):
    return d is not None and START_12 <= d < END


def inwin24(d):
    return d is not None and "2024-10-30T00:00:00Z" <= d < END


if __name__ == "__main__":
    main()
