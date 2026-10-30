#!/usr/bin/env python3
"""Independent manual-audit pack for step-5 trigger repos.

Second, deliberately simple recomputation (no share_table reuse) that prints,
for each audited repository and window, the evidence a human auditor needs:
event counts, actor tables with login/id/type, base_ref split, PyPI last
publication for the repo's distributions, and sample raw records for the top
actors. Output goes to results/audit-packs.json (and stdout).

Usage:
    python research/dependencies/maintenance/analysis/audit_manual.py [repo ...]
Without arguments it audits the preregistered trigger set (plan.md): H1/H2/H3/H4
triggers, the max-exposure repository, and the seed-42 sample.
"""

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAINT = HERE.parent
DATA = MAINT / "data"
RESULTS = HERE / "results"
START_12 = "2025-10-30T00:00:00Z"
START_24 = "2024-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def pages_records(folder):
    out = []
    for f in sorted(Path(folder).glob("0*.json")):
        out.extend(load(f)["records"])
    return out


def actor_desc(a):
    if a is None:
        return {"kind": "unattributed"}
    return {"login": a.get("login"), "id": a.get("id"),
            "type": a.get("type"), "bot_flag": a.get("bot"),
            "kind": "bot" if a.get("bot") else "human"}


def window_of(d, start):
    return d is not None and start <= d < END


def audit_repo(repo, start, pname):
    folder = DATA / repo.replace("/", "__")
    meta = load(folder / "repository.json")
    dbranch = meta["default_branch"]
    commits = [c for c in pages_records(folder / "commits") if window_of(c["date"], start)]
    prs_all = pages_records(folder / "prs")
    merged = [p for p in prs_all if p.get("merged_at") and window_of(p["merged_at"], start)]
    rels = [r for r in pages_records(folder / "releases")
            if not r["draft"] and window_of(r["date"], start)]
    reviews = [dict(r, pr_number=p["number"]) for p in prs_all for r in p["reviews"]
               if window_of(r.get("date"), start)
               and r["state"] in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}]
    packs = {
        "repo": repo, "window": pname,
        "default_branch": dbranch,
        "counts": {
            "commits_in": len(commits),
            "commits_merge": sum(1 for c in commits if c["parent_count"] > 1),
            "commits_nonmerge_nonbot":
                sum(1 for c in commits if c["parent_count"] <= 1
                    and c.get("author") and not c["author"].get("bot")),
            "commits_nonmerge_unattrib":
                sum(1 for c in commits if c["parent_count"] <= 1
                    and c.get("author") is None),
            "merged_prs_in": len(merged),
            "merged_prs_main": sum(1 for p in merged if p["base_ref"] == dbranch),
            "merged_prs_other_base": sum(1 for p in merged if p["base_ref"] != dbranch),
            "reviews_in": len(reviews),
            "releases_in": len(rels),
            "releases_bot": sum(1 for r in rels if (r.get("author") or {}).get("bot")),
        },
        "base_refs_other": sorted({p["base_ref"] for p in merged
                                   if p["base_ref"] != dbranch}),
    }
    # actor tables (human only, non-merge commits)
    def table(items, keyf):
        c = Counter()
        ids = {}
        types = {}
        for it in items:
            a = keyf(it)
            if a is None or a.get("bot"):
                continue
            login = a.get("login") or ""
            c[login.lower()] += 1
            ids[login.lower()] = a.get("id")
            types[login.lower()] = a.get("type")
        return [{"login": next((l for l in types if l == k), k),
                 "id": ids.get(k), "type": types.get(k), "count": n}
                for k, n in c.most_common(6)]

    human_nonmerge = [c for c in commits
                      if c["parent_count"] <= 1 and c.get("author")
                      and not c["author"].get("bot")]
    packs["top_committers_nonmerge"] = table(human_nonmerge, lambda c: c.get("author"))
    packs["top_pr_authors_main"] = table(
        [p for p in merged if p["base_ref"] == dbranch], lambda p: p.get("author"))
    packs["top_integrators_main"] = table(
        [p for p in merged if p["base_ref"] == dbranch], lambda p: p.get("merged_by"))
    packs["top_reviewers_pairs"] = []
    pairs = {}
    for r in reviews:
        a = r.get("author")
        if a is None or a.get("bot"):
            continue
        pairs.setdefault((a.get("login") or "").lower(), set()).add(r["pr_number"])
    for login, prs in sorted(pairs.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:6]:
        picks = [r for r in reviews if (r.get("author") or {}).get("login", "").lower() == login]
        packs["top_reviewers_pairs"].append({
            "login": picks[0]["author"]["login"], "id": picks[0]["author"]["id"],
            "type": picks[0]["author"]["type"],
            "pr_count": len(prs)})
    packs["top_release_authors"] = table(rels, lambda r: r.get("author"))
    # raw samples of the top actor (first commit record for each of top 3 actors)
    samples = []
    for entry in packs["top_committers_nonmerge"][:3]:
        for c in human_nonmerge:
            if (c.get("author") or {}).get("login", "").lower() == entry["login"].lower():
                samples.append(c)
                entry["sample_commit"] = {"sha": c["sha"], "date": c["date"],
                                          "parents": c["parent_count"],
                                          "committer": (c.get("committer") or {}).get("login")}
                break
    packs["sample_commits"] = samples
    # release details (for repos with few releases)
    packs["releases_detail"] = [
        {"tag": r.get("tag_name"), "date": r["date"], "author": actor_desc(r.get("author")),
         "prerelease": r.get("prerelease")} for r in rels[:12]]
    return packs


def trigger_repos():
    trig = set()
    hyp = load(RESULTS / "hypotheses.json")
    for w in hyp["windows"].values():
        for r in w["H1"]:
            if r["over_50"] or (r["share"] or 0) > 0.85:
                trig.add(r["repo"])
        for r in w["H2"]:
            if r["changed"]:
                trig.add(r["repo"])
        for r in w["H4"]:
            if r["commit_rev_differ"]:
                trig.add(r["repo"])
    h3 = {}
    for r in csv.DictReader(open(RESULTS / "h3-test.csv")):
        if r["qualifies"] == "True":
            trig.add(r["repo"])
            h3[r["repo"]] = True
    # max exposure repo (paths_from_root max in graph nodes.csv)
    best, bestn = None, -1
    for n in csv.DictReader(open(MAINT.parent / "graph" / "nodes.csv")):
        if n["category"].startswith("runtime"):
            nv = int(n["paths_from_root"])
            if nv > bestn:
                best, bestn = n["name"], nv
    distmap = {r["distribution"]: r["repo"]
               for r in csv.DictReader(open(RESULTS / "distribution-map.csv"))}
    trig.add(distmap[best])
    with open(MAINT.parent / "attributions" / "source-repos.csv", newline="", encoding="utf-8") as f:
        repos = sorted({r["repo_owner"] + "/" + r["repo_name"] for r in csv.DictReader(f)})
    import random
    random.seed(42)
    idx = random.sample(range(35), 3)
    seeded = {repos[i] for i in idx}
    return sorted(trig | seeded), seeded, {"exposure_repo": distmap[best],
                                           "max_paths": bestn}


def main():
    args = sys.argv[1:]
    if args:
        targets = args
        seeded = {}
        extra = {}
    else:
        targets, seeded, extra = trigger_repos()
    packs = []
    for repo in targets:
        for pname, start in (("12m", START_12), ("24m", START_24)):
            packs.append(audit_repo(repo, start, pname))
    out = RESULTS / "audit-packs.json"
    out.write_text(json.dumps({
        "generated_by": "audit_manual.py",
        "targets": targets, "seed42_sample": sorted(seeded), "extra": extra,
        "packs": packs}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"PASS: audit pack for {len(targets)} repos x 2 windows -> {out.name}")
    for t in targets:
        print(" audited:", t)


if __name__ == "__main__":
    main()
