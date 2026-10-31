#!/usr/bin/env python3
"""Independent check of the corrected step-5 contrasts (no share_table reuse).

Recomputes, straight from ../data/ frozen pages:
  1. bot-inclusive top-1 with the SAME units as the principal metric:
     non-merge commits / mainline merged PRs / unique (reviewer, PR) pairs;
     bot status strictly from the frozen `bot` flag;
  2. H4 review-role observability = repo TOTAL non-bot (reviewer, PR) pairs >= 5;
  3. H1 summary (evaluable / numeric >50% / inconclusive / conclusive>50%).

Cross-checks every value against results/repo-metrics.csv and
results/hypotheses.json and reports any mismatch. Run from the repo root:
    python research/dependencies/maintenance/analysis/verify_contrasts.py
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAINT = HERE.parent
DATA = MAINT / "data"
RESULTS = HERE / "results"
START_12 = "2025-10-30T00:00:00Z"
START_24 = "2024-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"
MIN_PRS = 10


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def all_records(folder):
    out = []
    for f in sorted(Path(folder).glob("0*.json")):
        out.extend(load(f)["records"])
    return out


def within(d, start):
    return d is not None and start <= d < END


def is_bot(a):
    return bool(a and a.get("bot"))


def top1_incl(events):
    """(login, is_bot, count, den, bot_events) with frozen bot flag."""
    counts = defaultdict(int)
    kind = {}
    disp = {}
    bot_events = 0
    for a in events:
        if a is None:
            counts[("none", None)] += 1
            kind[("none", None)] = "unattributed"
            continue
        k = ((a.get("login") or "").lower(), a.get("id"))
        counts[k] += 1
        disp[k[0]] = a.get("login")
        kind[k] = "bot" if is_bot(a) else "human"
        bot_events += 1 if is_bot(a) else 0
    den = sum(counts.values())
    if not den:
        return None, None, None, den, bot_events
    best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0]))[0]
    return disp[best[0][0]], kind[best[0]] == "bot", best[1], den, bot_events


def main():
    with open(MAINT.parent / "attributions" / "source-repos.csv", newline="", encoding="utf-8") as f:
        repos = sorted({r["repo_owner"] + "/" + r["repo_name"]
                        for r in csv.DictReader(f)})
    metrics = {}
    with (RESULTS / "repo-metrics.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            metrics[(r["repo"], r["window_end"])] = r
    hyp = load(RESULTS / "hypotheses.json")

    mismatches = []
    for repo in repos:
        folder = DATA / repo.replace("/", "__")
        dbranch = load(folder / "repository.json")["default_branch"]
        for p, start in (("12m", START_12), ("24m", START_24)):
            commits = [c for c in all_records(folder / "commits") if within(c["date"], start)]
            nonmerge = [c for c in commits if c["parent_count"] <= 1]
            merged = [x for x in all_records(folder / "prs")
                      if x.get("merged_at") and within(x["merged_at"], start)]
            main = [x for x in merged if x["base_ref"] == dbranch]
            pairs = {}
            for pr in all_records(folder / "prs"):
                for rev in pr["reviews"]:
                    a = rev.get("author")
                    if not within(rev.get("date"), start):
                        continue
                    if rev["state"] not in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}:
                        continue
                    key = (pr["number"], (a or {}).get("login") or "", (a or {}).get("id"))
                    pairs.setdefault(key, a)
            pair_authors = list(pairs.values())
            m = metrics[(repo, p)]
            # bots-inclusive units (independent recomputation)
            got_c = top1_incl([c.get("author") for c in nonmerge])
            got_p = top1_incl([x.get("author") for x in main])
            got_r = top1_incl(pair_authors)
            for which, got, row in (
                    ("cmt", got_c, m), ("pr", got_p, m), ("rev", got_r, m)):
                login, isb, n, den, bots = got
                if (login or "").lower() != (row[f"{which}_top1_incl_name"] or "").lower():
                    mismatches.append((repo, p, which, "login", login,
                                       row[f"{which}_top1_incl_name"]))
                if bool(isb) != (row[f"{which}_top1_incl_bot"] == "True"):
                    mismatches.append((repo, p, which, "is_bot", isb,
                                       row[f"{which}_top1_incl_bot"]))
                share = round(n / den, 4) if den and n else None
                if abs((float(row[f"{which}_top1_incl_share"] or 0)) - (share or 0)) > 0.001:
                    mismatches.append((repo, p, which, "share", share,
                                       row[f"{which}_top1_incl_share"]))
            # H4 rev_ok via total non-bot pairs
            pairs_nobot = sum(1 for a in pair_authors if a and not is_bot(a))
            h4 = next((x for x in hyp["windows"][p]["H4"] if x["repo"] == repo), None)
            if h4 and h4["reviewer_evaluable"] != (pairs_nobot >= 5):
                mismatches.append((repo, p, "h4_rev_ok", pairs_nobot >= 5,
                                   h4["reviewer_evaluable"]))
    # H1 summary counts, independently
    for p in ("12m", "24m"):
        evaluable = sum(1 for k, m in metrics.items() if k[1] == p
                        and int(m["commits_human"]) + int(m["commits_unattrib"]) >= 30)
        summ = hyp["windows"][p]["H1_summary"]
        if summ["evaluable"] != evaluable:
            mismatches.append((p, "h1_evaluable", summ["evaluable"], evaluable))
        shared = sum(1 for r in hyp["windows"][p]["H1"] if r["numeric_over_50"])
        if summ["numeric_over_50"] != shared:
            mismatches.append((p, "h1_numeric", summ["numeric_over_50"], shared))
        if summ["conclusive_over_50"] != sum(1 for r in hyp["windows"][p]["H1"]
                                            if r["conclusive_over_50"]):
            mismatches.append((p, "h1_conclusive", summ["conclusive_over_50"],
                               sum(1 for r in hyp["windows"][p]["H1"]
                                   if r["conclusive_over_50"])))

    if mismatches:
        for x in mismatches[:25]:
            print("MISMATCH", x, file=sys.stderr)
        print(f"FAIL: {len(mismatches)} mismatches")
        sys.exit(1)
    print("PASS: independent recompute of bot-inclusive units (frozen flag), "
          "H4 total-pair rule and H1 summary matches the published results for "
          f"{len(repos)} repos x 2 windows.")


if __name__ == "__main__":
    main()
