#!/usr/bin/env python3
"""Step-5 descriptive analysis of the frozen step-4 activity data.

Recomputes every metric from the archived normalized pages in ../data/ (no
GitHub access, no live state), cross-checks totals against
../coverage-descriptive.csv and writes the derived tables in results/.

Rules preregistered in plan.md (commit 65b8d02 + clarification c57005f).

Run from the repository root:
    python research/dependencies/maintenance/analysis/analyze_activity.py
"""

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAINT = HERE.parent          # maintenance/
DATA = MAINT / "data"
SOURCE = MAINT.parent / "attributions" / "source-repos.csv"
GRAPH = MAINT.parent / "graph"
COVERAGE = MAINT / "coverage-descriptive.csv"
RESULTS = HERE / "results"

START_24 = "2024-10-30T00:00:00Z"
START_12 = "2025-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"
MIN_COMMITS = 30      # commit evaluability (plan.md)
MIN_PRS = 10          # merged-PR evaluability (plan.md); 20 as sensitivity
MIN_REVIEWERS = 5     # reviewer-role observability for H4 (clarification 1)

# ---------------------------------------------------------------- data loading


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def page_files(folder):
    return sorted(folder.glob("[0-9][0-9][0-9][0-9][0-9].json"))


def records(folder):
    out = []
    for f in page_files(folder):
        page = load(f)
        out.extend(page["records"])
    return out


def within(date, start):
    return bool(date and start <= date < END)


def actor(item, key="author"):
    return item.get(key)


def is_bot(a):
    return bool(a and a.get("bot"))


def actor_key(a):
    if a is None:
        return ("none", None)
    return ((a.get("login") or "").lower(), a.get("id"))


# --------------------------------------------------------------- per-repo data


def load_repo(repo):
    folder = DATA / repo.replace("/", "__")
    meta = load(folder / "repository.json")
    cover = load(folder / "coverage.json")
    assert cover["complete"]
    return {
        "repo": repo,
        "meta": meta,
        "commits": records(folder / "commits"),
        "prs": records(folder / "prs"),
        "releases": records(folder / "releases"),
    }


def reviews_of(prs):
    """Reviews in countable states, with their PR number (dedup pairs)."""
    out = []
    for pr in prs:
        for rev in pr["reviews"]:
            if rev["state"] in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}:
                r = dict(rev)
                r["pr_number"] = pr["number"]
                out.append(r)
    return out


def share_table(events, den, extra_categories=()):
    """Human top1/top2 + HHI. events: actor dicts or None, in-window.

    den: denominator (int, non-bot events incl. unattributed).
    Categories: each human actor is its own category; None -> 'unattributed'.
    """
def share_table(events, den):
    """Human top1/top2 + HHI over non-bot events. events: actor dicts | None.

    den: denominator (int, non-bot events incl. unattributed) — computed by
    the caller; bots are skipped here so that a bot never ranks.
    """
    counts = defaultdict(int)
    disp = {}
    for a in events:
        if a is None:
            counts[("none", None)] += 1
        elif is_bot(a):
            continue
        else:
            k = ((a.get("login") or "").lower(), a.get("id"))
            counts[k] += 1
            disp[k[0]] = a.get("login") or ""
    humans = {k: v for k, v in counts.items() if k[0] != "none"}
    unattrib = counts.get(("none", None), 0)
    ranked = sorted(humans.items(), key=lambda kv: (-kv[1], kv[0][0]))
    cats = [(disp[k[0]], v) for k, v in ranked]
    def hhi():
        total = den
        if not total:
            return None
        s = sum((v / total) ** 2 for _, v in cats)
        if unattrib:
            s += (unattrib / total) ** 2
        return round(s, 6)
    top1_share = round(cats[0][1] / den, 4) if cats and den else None
    top2_share = round((cats[0][1] + cats[1][1]) / den, 4) if len(cats) > 1 and den else None
    return {
        "top1_login": cats[0][0] if cats else None,
        "top1_id": ranked[0][0][1] if ranked else None,
        "top1_count": cats[0][1] if cats else 0,
        "top1_share": top1_share,
        "top2_share": top2_share,
        "hhi": hhi(),
        "distinct_humans": len(cats),
        "unattributed": unattrib,
        "unattributed_share": round(unattrib / den, 4) if den else None,
        "ranked": [(login, n, round(n / den, 4) if den else None)
                   for login, n in cats[:10]],
    }


def bucket(events_in):
    """Split events into bot/unattrib/human by author."""
    bot = sum(1 for a in events_in if is_bot(a))
    unattr = sum(1 for a in events_in if a is None)
    human = len(events_in) - bot - unattr
    return bot, unattr, human


def days_between(a, b):
    return round((datetime.fromisoformat(a.replace("Z", "+00:00"))
                  - datetime.fromisoformat(b.replace("Z", "+00:00"))).total_seconds() / 86400,
                 2)


# ------------------------------------------------------------------- analysis


def analyze_repo(data, start, pname):
    """Per-window metrics for one repo. pname = '12m' or '24m'."""
    end_cut = END
    res = {"repo": data["repo"], "window": pname,
           "start": start, "end": end_cut, "meta": data["meta"]}
    dbranch = data["meta"]["default_branch"]

    # --- commits
    commits = [c for c in data["commits"] if within(c["date"], start)]
    merges = [c for c in commits if c["parent_count"] > 1]
    nonmerge = [c for c in commits if c["parent_count"] <= 1]
    c_bot, c_unattr, c_human = bucket([c.get("author") for c in nonmerge])
    c_bot_m, c_unattr_m, c_human_m = bucket([c.get("author") for c in merges])
    # plan: non-bot denominator for commit concentration = human + unattributed
    den_c = c_unattr + c_human
    res.update({
        f"commits_all": len(commits),
        f"commits_merge": len(merges),
        f"commits_nonmerge": len(nonmerge),
        f"commits_bot": c_bot,
        f"commits_unattrib": c_unattr,
        f"commits_human": c_human,
        f"commits_bot_merge": c_bot_m,
        f"commits_unattrib_merge": c_unattr_m,
        f"commits_human_merge": c_human_m,
    })
    st = share_table([c.get("author") for c in nonmerge], den_c)
    res["commit_concentration"] = st
    # with merges (sensitivity): denominator = all in-window commits minus bot commits
    commit_bot_all = sum(1 for c in commits if is_bot(c.get("author")))
    st_merge = share_table([c.get("author") for c in commits],
                           len(commits) - commit_bot_all)
    res["commit_concentration_with_merge"] = st_merge

    # --- merged PRs (any base + default base)
    merged = [p for p in data["prs"] if p["merged_at"] and within(p["merged_at"], start)]
    m_main = [p for p in merged if (p["base_ref"] or "") == dbranch]
    m_other = [p for p in merged if (p["base_ref"] or "") != dbranch]
    # splits over ALL merged PRs (matches step-4 coverage-descriptive.csv semantics)
    bot, unattr, human = bucket([p.get("author") for p in merged])
    # splits over the default-branch subset (mainline concentration denominator)
    bot_main, unattr_main, human_main = bucket([p.get("author") for p in m_main])
    den_p = len(m_main) - bot_main
    res.update({
        f"merged_prs_all": len(merged),
        f"merged_prs_main": len(m_main),
        f"merged_prs_other_base": len(m_other),
        f"merged_prs_bot": bot,
        f"merged_prs_unattrib": unattr,
        f"merged_prs_human": human,
        f"merged_prs_main_bot": bot_main,
        f"merged_prs_main_unattrib": unattr_main,
        f"merged_prs_main_human": human_main,
    })
    res["pr_concentration"] = share_table([p.get("author") for p in m_main], den_p)
    # any-base sensitivity shares
    bot2, unattr2, human2 = bucket([p.get("author") for p in merged])
    res["pr_anybase_den_nonbot"] = len(merged) - bot2
    res["pr_anybase"] = share_table([p.get("author") for p in merged],
                                    len(merged) - bot2)

    # --- reviews (pairs)
    reviews = reviews_of(data["prs"])
    revs_in = [r for r in reviews if within(r["date"], start)]
    pairs = {}
    for r in revs_in:
        key = (r["pr_number"], actor_key(r.get("author")))
        pairs.setdefault(key, []).append(r)
    # classify pairs by author of the review record
    bots_pairs, unattr_pairs, human_pairs = 0, 0, 0
    human_actor_events = []
    for (n, ak), rs in pairs.items():
        a = rs[0].get("author")
        if a is None:
            unattr_pairs += 1
        elif is_bot(a):
            bots_pairs += 1
        else:
            human_pairs += 1
            human_actor_events.append(a)
    raw = len(revs_in)
    raw_bot = sum(1 for r in revs_in if is_bot(r.get("author")))
    raw_unattr = sum(1 for r in revs_in if r.get("author") is None)
    den_r = human_pairs + unattr_pairs
    res.update({
        f"reviews_raw": raw,
        f"reviews_raw_bot": raw_bot,
        f"reviews_raw_unattrib": raw_unattr,
        f"review_pairs": len(pairs),
        f"review_pairs_bot": bots_pairs,
        f"review_pairs_unattrib": unattr_pairs,
        f"review_pairs_human": human_pairs,
    })
    res["review_concentration"] = share_table(human_actor_events, den_r)

    # --- releases
    rels = [x for x in data["releases"]
            if not x["draft"] and within(x["date"], start)]
    rb, ru, rh = bucket([x.get("author") for x in rels])
    res.update({f"releases_all": len(rels), f"releases_bot": rb,
                f"releases_unattrib": ru, f"releases_human": rh})
    res["release_concentration"] = share_table(
        [x.get("author") for x in rels], len(rels) - rb)

    # --- continuity (plan Aclaración 2): months covered, last observable date
    def continuity(dates):
        months = sorted({d[:7] for d in dates})
        return {"months_covered": len(months), "last_event": max(dates) if dates else None}

    def continuity_nobot(dates, actors):
        kept = [d for d, a in zip(dates, actors) if not is_bot(a)]
        months = sorted({d[:7] for d in kept})
        return {"months_covered_nobot": len(months),
                "last_event_nobot": max(kept) if kept else None}

    c_all_dates = [c["date"] for c in commits]
    c_actors = [c.get("author") for c in commits]
    res["commits_continuity"] = {**continuity(c_all_dates),
                                 **continuity_nobot(c_all_dates, c_actors)}
    pr_dates = [p["merged_at"] for p in merged]
    pr_actors = [p.get("author") for p in merged]
    res["prs_continuity"] = {**continuity(pr_dates),
                             **continuity_nobot(pr_dates, pr_actors)}
    rev_dates = [r["date"] for r in revs_in]
    rev_actors = [r.get("author") for r in revs_in]
    res["reviews_continuity"] = {**continuity(rev_dates),
                                 **continuity_nobot(rev_dates, rev_actors)}
    rel_dates = [x["date"] for x in rels]
    rel_actors = [x.get("author") for x in rels]
    res["releases_continuity"] = {**continuity(rel_dates),
                                  **continuity_nobot(rel_dates, rel_actors)}
    sorted_rel = sorted(rel_dates, reverse=True)
    res["releases_cadence_days"] = (
        days_between(sorted_rel[0], sorted_rel[1]) if len(sorted_rel) >= 2 else None)

    # --- bot-included variant (plan Aclaración 2, CORRECTED): SAME units as
    # the principal metric — non-merge commits, mainline merged PRs, unique
    # (reviewer, PR) pairs — with every actor (bots and unattributed) in the
    # ranking and the denominator covering the whole unit.
    nm_actors = [c.get("author") for c in nonmerge]
    res["cmt_incl_bots"] = share_table_all(nm_actors, len(nonmerge))
    main_actors = [p.get("author") for p in m_main]
    res["pr_incl_bots"] = share_table_all(main_actors, len(m_main))
    pair_actors = [rs_pairs[0].get("author") for _k, rs_pairs in pairs.items()]
    res["rev_incl_bots"] = share_table_all(pair_actors, len(pairs))
    rel_actors_all = [x.get("author") for x in rels]
    res["rel_incl_bots"] = share_table_all(rel_actors_all, len(rels))

    # --- H4 roles
    res["top_integrator"] = top_by(
        [p for p in m_main if p.get("merged_by") and not is_bot(p["merged_by"])],
        lambda p: p["merged_by"])
    res["top_reviewer"] = (res["review_concentration"]["top1_login"],
                           res["review_concentration"]["top1_count"])
    return res


def share_table_all(events, den_all):
    """Variant INCLUDING bots, same units as the principal metric (plan.md
    Aclaración 2, corrected): the caller passes the SAME event set used by
    the principal concentration metric; only the bots join the ranking and
    the denominator covers all in-window events of that unit. Bot status is
    taken from the frozen `bot` flag, never inferred from the login suffix.
    Unattributed is its own category. top1 may be a bot; flag returned."""
    counts = defaultdict(int)
    disp = {}
    kind = {}
    bot_events = 0
    for a in events:
        if a is None:
            counts[("none", None)] += 1
            kind[("none", None)] = "unattributed"
            continue
        k = ((a.get("login") or "").lower(), a.get("id"))
        counts[k] += 1
        disp[k[0]] = a.get("login") or ""
        kind[k] = "bot" if is_bot(a) else "human"
        bot_events += 1 if is_bot(a) else 0
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0]))
    if not ranked or not den_all:
        return {"top1_incl": None, "top1_incl_is_bot": None,
                "top1_incl_share": None, "bot_share_incl": None}
    top_key = ranked[0][0]
    top_login = disp[top_key[0]]
    return {
        "top1_incl": top_login,
        "top1_incl_is_bot": kind[top_key] == "bot",
        "top1_incl_share": round(ranked[0][1] / den_all, 4),
        "bot_share_incl": round(bot_events / den_all, 4) if den_all else None,
    }


def top_by(items, getter):
    counts = defaultdict(int)
    for item in items:
        a = getter(item)
        if a and not is_bot(a):
            counts[(a.get("login") or "", a.get("id"))] += 1
    if not counts:
        return None
    login, n = max(counts.items(), key=lambda kv: (kv[1], kv[0][0]))
    return {"login": login[0], "id": login[1], "count": n}


def distinct_ids(items):
    ids = []
    for _login, oid in items:
        if oid is not None:
            ids.append(oid)
    return len(set(ids))


# --------------------------------------------------------------------- output


COLUMNS = [
    "repo", "window_end", "archived", "fork", "default_branch",
    "commits_all", "commits_merge", "commits_nonmerge", "commits_bot", "commits_unattrib",
    "commits_human", "commits_bot_merge", "commits_unattrib_merge", "commits_human_merge",
    "merged_prs_all", "merged_prs_main", "merged_prs_other_base", "merged_prs_bot",
    "merged_prs_unattrib", "merged_prs_human",
    "merged_prs_main_bot", "merged_prs_main_unattrib", "merged_prs_main_human",
    "reviews_raw", "reviews_raw_bot", "reviews_raw_unattrib",
    "review_pairs", "review_pairs_bot", "review_pairs_unattrib", "review_pairs_human",
    "releases_all", "releases_bot", "releases_unattrib", "releases_human",
    "cmt_top1", "cmt_top1_count", "cmt_top1_share", "cmt_top2_share",
    "cmt_merge_top1_share", "cmt_unattrib_share", "cmt_hhi", "cmt_humans",
    "cmt_evaluable", "pr_top1", "pr_top1_count", "pr_top1_share", "pr_top2_share",
    "pr_unattrib_share", "pr_hhi", "pr_humans", "pr_evaluable", "pr_evaluable20",
    "rev_top1", "rev_top1_count", "rev_top1_share", "rev_hhi", "rev_humans",
    "rel_top1", "rel_top1_count", "rel_top1_share", "rel_unattrib_share",
    "merged_other_base_nonbot", "any_base_pr_top1_share",
    "cmt_top1_incl_share", "cmt_top1_incl_name", "cmt_top1_incl_bot",
    "pr_top1_incl_share", "pr_top1_incl_name", "pr_top1_incl_bot",
    "rev_top1_incl_share", "rev_top1_incl_name", "rev_top1_incl_bot",
    "rel_top1_incl_share", "rel_top1_incl_name", "rel_top1_incl_bot",
    "cmt_months_all", "cmt_months_nobot", "cmt_last", "cmt_last_nobot",
    "pr_months_all", "pr_months_nobot", "pr_last", "pr_last_nobot",
    "rev_months_all", "rev_months_nobot", "rev_last", "rev_last_nobot",
    "rel_months_all", "rel_months_nobot", "rel_last", "rel_last_nobot",
    "rel_cadence_days",
]


def flatten(r):
    cc = r["commit_concentration"]
    cm = r["commit_concentration_with_merge"]
    pc = r["pr_concentration"]
    rc = r["review_concentration"]
    lc = r["release_concentration"]
    pr_any = r["pr_anybase"]
    cb = r["cmt_incl_bots"]
    pb = r["pr_incl_bots"]
    rb2 = r["rev_incl_bots"]
    lb = r["rel_incl_bots"]
    return {
        "repo": r["repo"],
        "window_end": r["window"],
        "archived": r["meta"]["archived"],
        "fork": r["meta"]["fork"],
        "default_branch": r["meta"]["default_branch"],
        "commits_all": r["commits_all"],
        "commits_merge": r["commits_merge"],
        "commits_nonmerge": r["commits_nonmerge"],
        "commits_bot": r["commits_bot"],
        "commits_unattrib": r["commits_unattrib"],
        "commits_human": r["commits_human"],
        "commits_bot_merge": r["commits_bot_merge"],
        "commits_unattrib_merge": r["commits_unattrib_merge"],
        "commits_human_merge": r["commits_human_merge"],
        "merged_prs_all": r["merged_prs_all"],
        "merged_prs_main": r["merged_prs_main"],
        "merged_prs_other_base": r["merged_prs_other_base"],
        "merged_prs_bot": r["merged_prs_bot"],
        "merged_prs_unattrib": r["merged_prs_unattrib"],
        "merged_prs_human": r["merged_prs_human"],
        "merged_prs_main_bot": r["merged_prs_main_bot"],
        "merged_prs_main_unattrib": r["merged_prs_main_unattrib"],
        "merged_prs_main_human": r["merged_prs_main_human"],
        "reviews_raw": r["reviews_raw"],
        "reviews_raw_bot": r["reviews_raw_bot"],
        "reviews_raw_unattrib": r["reviews_raw_unattrib"],
        "review_pairs": r["review_pairs"],
        "review_pairs_bot": r["review_pairs_bot"],
        "review_pairs_unattrib": r["review_pairs_unattrib"],
        "review_pairs_human": r["review_pairs_human"],
        "releases_all": r["releases_all"],
        "releases_bot": r["releases_bot"],
        "releases_unattrib": r["releases_unattrib"],
        "releases_human": r["releases_human"],
        "cmt_top1": cc["top1_login"],
        "cmt_top1_count": cc["top1_count"],
        "cmt_top1_share": cc["top1_share"],
        "cmt_top2_share": cc["top2_share"],
        "cmt_merge_top1_share": cm["top1_share"],
        "cmt_unattrib_share": cc["unattributed_share"],
        "cmt_hhi": cc["hhi"],
        "cmt_humans": cc["distinct_humans"],
        "cmt_evaluable": r["commits_human"] + r["commits_unattrib"] >= MIN_COMMITS,
        "pr_top1": pc["top1_login"],
        "pr_top1_count": pc["top1_count"],
        "pr_top1_share": pc["top1_share"],
        "pr_top2_share": pc["top2_share"],
        "pr_unattrib_share": pc["unattributed_share"],
        "pr_hhi": pc["hhi"],
        "pr_humans": pc["distinct_humans"],
        "pr_evaluable": r["merged_prs_main_human"] + r["merged_prs_main_unattrib"] >= MIN_PRS,
        "pr_evaluable20": r["merged_prs_main_human"] + r["merged_prs_main_unattrib"] >= 20,
        "rev_top1": rc["top1_login"],
        "rev_top1_count": rc["top1_count"],
        "rev_top1_share": rc["top1_share"],
        "rev_hhi": rc["hhi"],
        "rev_humans": rc["distinct_humans"],
        "rel_top1": lc["top1_login"],
        "rel_top1_count": lc["top1_count"],
        "rel_top1_share": lc["top1_share"],
        "rel_unattrib_share": lc["unattributed_share"],
        "merged_other_base_nonbot": r["merged_prs_other_base"],
        "any_base_pr_top1_share": pr_any["top1_share"],
        "cmt_top1_incl_share": cb["top1_incl_share"],
        "cmt_top1_incl_name": cb["top1_incl"],
        "cmt_top1_incl_bot": cb["top1_incl_is_bot"],
        "pr_top1_incl_share": pb["top1_incl_share"],
        "pr_top1_incl_name": pb["top1_incl"],
        "pr_top1_incl_bot": pb["top1_incl_is_bot"],
        "rev_top1_incl_share": rb2["top1_incl_share"],
        "rev_top1_incl_name": rb2["top1_incl"],
        "rev_top1_incl_bot": rb2["top1_incl_is_bot"],
        "rel_top1_incl_share": lb["top1_incl_share"],
        "rel_top1_incl_name": lb["top1_incl"],
        "rel_top1_incl_bot": lb["top1_incl_is_bot"],
        "cmt_months_all": r["commits_continuity"]["months_covered"],
        "cmt_months_nobot": r["commits_continuity"]["months_covered_nobot"],
        "cmt_last": r["commits_continuity"]["last_event"],
        "cmt_last_nobot": r["commits_continuity"]["last_event_nobot"],
        "pr_months_all": r["prs_continuity"]["months_covered"],
        "pr_months_nobot": r["prs_continuity"]["months_covered_nobot"],
        "pr_last": r["prs_continuity"]["last_event"],
        "pr_last_nobot": r["prs_continuity"]["last_event_nobot"],
        "rev_months_all": r["reviews_continuity"]["months_covered"],
        "rev_months_nobot": r["reviews_continuity"]["months_covered_nobot"],
        "rev_last": r["reviews_continuity"]["last_event"],
        "rev_last_nobot": r["reviews_continuity"]["last_event_nobot"],
        "rel_months_all": r["releases_continuity"]["months_covered"],
        "rel_months_nobot": r["releases_continuity"]["months_covered_nobot"],
        "rel_last": r["releases_continuity"]["last_event"],
        "rel_last_nobot": r["releases_continuity"]["last_event_nobot"],
        "rel_cadence_days": r["releases_cadence_days"],
    }


def category(share):
    if share is None:
        return None
    return "<=50%" if share <= 0.50 else ("50-75%" if share <= 0.75 else ">75%")


def write_csv(rows, path, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    RESULTS.mkdir(exist_ok=True)
    with SOURCE.open(newline="", encoding="utf-8") as f:
        dist_rows = list(csv.DictReader(f))
    repos = sorted({d["repo_owner"] + "/" + d["repo_name"] for d in dist_rows})
    assert len(repos) == 35, f"expected 35 repos, got {len(repos)}"

    data = {r: load_repo(r) for r in repos}

    # ---- per-repo metrics, both windows
    flat_rows = []
    raw_windows = {"12m": {}, "24m": {}}
    for repo in repos:
        for pname, start in (("12m", START_12), ("24m", START_24)):
            res = analyze_repo(data[repo], start, pname)
            res["window"] = pname
            raw_windows[pname][repo] = res
            flat_rows.append(flatten(res))

    # ---- cross-check vs coverage-descriptive.csv (independent verification)
    cov = {}
    with COVERAGE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cov[row["repo"]] = row
    checks = [
        ("commits_all", "commits_events"), ("commits_bot", "commits_bot"),
        ("commits_unattrib", "commits_unattributed"),
        ("merged_prs_all", "merged_prs_events"),
        ("merged_prs_bot", "merged_prs_bot"),
        ("merged_prs_unattrib", "merged_prs_unattributed"),
        ("reviews_raw", "reviews_events"),
        ("reviews_raw_bot", "reviews_bot"),
        ("reviews_raw_unattrib", "reviews_unattributed"),
        ("releases_all", "releases_events"),
        ("releases_bot", "releases_bot"),
        ("releases_unattrib", "releases_unattributed"),
    ]
    mismatches = []
    for repo, covrow in cov.items():
        for p, pre in (("12m", "12m"), ("24m", "24m")):
            mine = next(r for r in flat_rows
                        if r["repo"] == repo and r["window_end"] == p)
            for mine_col, cov_col in checks:
                if int(mine[mine_col]) != int(covrow[f"{pre}_{cov_col}"]):
                    mismatches.append((repo, p, mine_col,
                                       mine[mine_col], covrow[f"{pre}_{cov_col}"]))
    if mismatches:
        for m in mismatches[:20]:
            print("MISMATCH", m, file=sys.stderr)
        raise ValueError(f"{len(mismatches)} mismatches vs coverage-descriptive.csv")

    flat_fieldnames = COLUMNS
    write_csv(flat_rows, RESULTS / "repo-metrics.csv", flat_fieldnames)

    # ---- continuity CSV (plan Aclaración 2)
    cont_rows = []
    for repo in repos:
        for p in ("12m", "24m"):
            r = next(x for x in flat_rows
                     if x["repo"] == repo and x["window_end"] == p)
            cont_rows.append({
                "repo": repo, "window": p,
                "commits_months_all": r["cmt_months_all"],
                "commits_months_nobot": r["cmt_months_nobot"],
                "commits_last_all": r["cmt_last"],
                "commits_last_nobot": r["cmt_last_nobot"],
                "merged_prs_months_all": r["pr_months_all"],
                "merged_prs_months_nobot": r["pr_months_nobot"],
                "merged_prs_last_all": r["pr_last"],
                "merged_prs_last_nobot": r["pr_last_nobot"],
                "reviews_months_all": r["rev_months_all"],
                "reviews_months_nobot": r["rev_months_nobot"],
                "reviews_last_all": r["rev_last"],
                "reviews_last_nobot": r["rev_last_nobot"],
                "releases_months_all": r["rel_months_all"],
                "releases_months_nobot": r["rel_months_nobot"],
                "releases_last_all": r["rel_last"],
                "releases_last_nobot": r["rel_last_nobot"],
                "releases_cadence_days": r["rel_cadence_days"],
            })
    write_csv(cont_rows, RESULTS / "continuity.csv",
              ["repo", "window", "commits_months_all", "commits_months_nobot",
               "commits_last_all", "commits_last_nobot",
               "merged_prs_months_all", "merged_prs_months_nobot",
               "merged_prs_last_all", "merged_prs_last_nobot",
               "reviews_months_all", "reviews_months_nobot",
               "reviews_last_all", "reviews_last_nobot",
               "releases_months_all", "releases_months_nobot",
               "releases_last_all", "releases_last_nobot", "releases_cadence_days"])

    # ---- overview totals per window and stream
    overview = {}
    for p in ("12m", "24m"):
        rows = [r for r in flat_rows if r["window_end"] == p]
        overview[p] = {m: {
            "events": sum(r[k] for r in rows),
            "bots": sum(r[b] for r in rows) if b else 0,
            "unattributed": sum(r[u] for r in rows) if u else 0,
        } for m, k, b, u in (
            ("commits_nonmerge", "commits_nonmerge", "commits_bot", "commits_unattrib"),
            ("commit_merges", "commits_merge", "commits_bot_merge", "commits_unattrib_merge"),
            ("merged_prs_main", "merged_prs_main", "merged_prs_bot", "merged_prs_unattrib"),
            ("merged_prs_other_base", "merged_prs_other_base", None, None),
            ("review_pairs", "review_pairs", "review_pairs_bot", "review_pairs_unattrib"),
            ("reviews_raw", "reviews_raw", "reviews_raw_bot", "reviews_raw_unattrib"),
            ("releases", "releases_all", "releases_bot", "releases_unattrib"),
        )}
    (RESULTS / "overview-totals.json").write_text(
        json.dumps(overview, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- actor shares detail (per repo/window/metric) for top rows
    actors = []
    for p in ("12m", "24m"):
        for repo, res in raw_windows[p].items():
            for metric, key in (("commits", "commit_concentration"),
                                ("merged_prs_main", "pr_concentration"),
                                ("review_pairs", "review_concentration"),
                                ("releases", "release_concentration")):
                c = res[key]
                denom = (int(c["unattributed"] or 0) + (c["top1_count"] or 0)
                         ) if c["ranked"] is not None else 0
                for login, n, share in c["ranked"]:
                    actors.append({"repo": repo, "window": p, "metric": metric,
                                   "login": login, "count": n, "share": share})
    write_csv(actors, RESULTS / "actor-shares.csv",
              ["repo", "window", "metric", "login", "count", "share"])

    # ---- hypotheses
    hyp = {"generated_by": "analyze_activity.py",
           "rules": {"MIN_COMMITS": MIN_COMMITS, "MIN_PRS": MIN_PRS,
                     "MIN_REVIEWERS": MIN_REVIEWERS},
           "windows": {}}
    for p in ("12m", "24m"):
        rows = {r["repo"]: r for r in flat_rows if r["window_end"] == p}
        # H1 (all repos, per preregistered rule): evaluable / numeric >50% /
        # inconclusive / conclusive>50% are reported separately, no silent mix.
        rows_all = rows.values()
        evaluable_c = [r for r in rows_all if r["cmt_evaluable"]]
        h1 = []
        numer_over50 = 0
        conclusive_over50 = 0
        inconclusive_list = []
        for r in evaluable_c:
            by, ua = r["commits_bot"], r["commits_unattrib"]
            allc = r["commits_all"]
            numeric = (r["cmt_top1_share"] or 0) > 0.50
            inconclusive = (allc and ua / allc >= 0.20) or (allc and by / allc >= 0.50)
            conclusive = numeric and not inconclusive
            numer_over50 += numeric
            conclusive_over50 += conclusive
            if inconclusive:
                inconclusive_list.append(r["repo"])
            h1.append({"repo": r["repo"],
                       "top1": r["cmt_top1"], "share": r["cmt_top1_share"],
                       "with_merge_share": r["cmt_merge_top1_share"],
                       "with_bots_share": r["cmt_top1_incl_share"],
                       "with_bots_top1": r["cmt_top1_incl_name"],
                       "with_bots_top1_is_bot": r["cmt_top1_incl_bot"],
                       "den_nonmerge": r["commits_human"] + r["commits_unattrib"],
                       "unattrib_share": r["cmt_unattrib_share"],
                       "bot_share": round(by / allc, 4) if allc else None,
                       "numeric_over_50": numeric,
                       "inconclusive": inconclusive,
                       "conclusive_over_50": conclusive})
        # H2
        h2 = []
        for r in rows.values():
            if r["cmt_evaluable"] and r["pr_evaluable"]:
                ccat = category(r["cmt_top1_share"])
                pcat = category(r["pr_top1_share"])
                h2.append({"repo": r["repo"], "commit_cat": ccat,
                           "pr_cat": pcat, "changed": ccat != pcat,
                           "commit_share": r["cmt_top1_share"],
                           "commit_share_incl_bots": r["cmt_top1_incl_share"],
                           "pr_share": r["pr_top1_share"],
                           "pr_share_incl_bots": r["pr_top1_incl_share"]})
        # H4
        h4 = []
        for r in rows.values():
            if r["cmt_evaluable"] and r["pr_evaluable"]:
                rw = raw_windows[p][r["repo"]]
                integrator = rw["top_integrator"] or {}
                # plan.md (Aclaración 1, corrected): review role observable when
                # the repo's TOTAL non-bot (reviewer, PR) pairs >= 5, not the
                # top reviewer's count.
                rev_ok = int(r["review_pairs_human"]) >= MIN_REVIEWERS
                h4.append({
                    "repo": r["repo"],
                    "top_committer": r["cmt_top1"],
                    "top_integrator": integrator.get("login"),
                    "top_reviewer": r["rev_top1"] if rev_ok else None,
                    "reviewer_evaluable": rev_ok,
                    "commit_pr_differ": r["cmt_top1"] != integrator.get("login"),
                    "commit_rev_differ": bool(rev_ok) and r["cmt_top1"] != r["rev_top1"],
                })
        hyp["windows"][p] = {"H1": h1, "H2": h2, "H4": h4,
                             "H1_summary": {"evaluable": len(evaluable_c),
                                            "numeric_over_50": numer_over50,
                                            "inconclusive": len(inconclusive_list),
                                            "inconclusive_repos": inconclusive_list,
                                            "conclusive_over_50": conclusive_over50}}
    (RESULTS / "hypotheses.json").write_text(
        json.dumps(hyp, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- distribution map (37 dists -> 35 repos) with exposure
    graph_nodes = {}
    with (GRAPH / "nodes.csv").open(newline="", encoding="utf-8") as f:
        for n in csv.DictReader(f):
            graph_nodes[n["name"].strip().lower()] = n
    dist_map = []
    for d in dist_rows:
        node = graph_nodes.get(d["name"].strip().lower())
        dist_map.append({
            "distribution": d["name"],
            "frozen_version": d["frozen_version"],
            "category": d["category"],
            "repo": d["repo_owner"] + "/" + d["repo_name"],
            "is_direct": (node["is_direct"] if node else ""),
            "paths_from_root": (node["paths_from_root"] if node else ""),
            "hops_from_root": (node["hops_from_root"] if node else ""),
            "shared_repository": d["shared_repository"],
        })
    write_csv(dist_map, RESULTS / "distribution-map.csv",
              ["distribution", "frozen_version", "category", "repo", "is_direct",
               "paths_from_root", "hops_from_root", "shared_repository"])

    # ---- hypothesis H3 (repo-level; PyPI evidence collected per plan.md)
    pypi_path = HERE / "pypi-evidence" / "h3-summary.json"
    if pypi_path.exists():
        pypi = json.loads(pypi_path.read_text(encoding="utf-8"))
        pub_by_repo = defaultdict(list)
        for d in pypi:
            if d["unavailable"]:
                raise ValueError(f"H3 input unavailable: {d['distribution']}")
        with SOURCE.open(newline="", encoding="utf-8") as f:
            dist_to_repo = {r["name"]: r["repo_owner"] + "/" + r["repo_name"]
                            for r in csv.DictReader(f)}
        for d in pypi:
            pub_by_repo[dist_to_repo[d["distribution"]]].append(d)
        h3 = []
        for repo in repos:
            r12 = next(x for x in flat_rows
                       if x["repo"] == repo and x["window_end"] == "12m")
            dists = pub_by_repo[repo]
            pypi_12m = any(d["published_12m"] for d in dists)
            gh_rel = int(r12["releases_all"])
            activity = (int(r12["commits_human"]) > 0
                        or (int(r12["merged_prs_main"])
                            - int(r12["merged_prs_main_bot"])
                            - int(r12["merged_prs_main_unattrib"])) > 0
                        or int(r12["review_pairs_human"]) > 0)
            qualifies = (gh_rel == 0) and pypi_12m and activity
            h3.append({
                "repo": repo,
                "distributions": ";".join(d["distribution"] for d in dists),
                "github_releases_12m": gh_rel,
                "pypi_published_12m": pypi_12m,
                "observable_activity_12m": activity,
                "qualifies": qualifies,
                "activity_detail": {
                    "nonmerge_human_commits_12m": int(r12["commits_human"]),
                    "mainline_merged_nonbot_prs_12m":
                        int(r12["merged_prs_main"]) - int(r12["merged_prs_main_bot"])
                        - int(r12["merged_prs_main_unattrib"]),
                    "review_pairs_human_12m": int(r12["review_pairs_human"]),
                },
            })
        (RESULTS / "h3-test.csv").write_text(
            "repo,distributions,github_releases_12m,pypi_published_12m,"
            "observable_activity_12m,qualifies,activity_detail\n", encoding="utf-8")
        with (RESULTS / "h3-test.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(h3[0]), lineterminator="\n")
            w.writeheader()
            for row in h3:
                row_c = dict(row)
                row_c["activity_detail"] = json.dumps(row_c["activity_detail"],
                                                      ensure_ascii=False)
                w.writerow(row_c)
        nq = sum(1 for r in h3 if r["qualifies"])
        print(f"H3: {nq} repos qualify (PyPI publish, zero GitHub releases, "
              f"observable activity, 12m)")

    # ---- low-activity inventory
    low = []
    for p in ("12m", "24m"):
        for repo, res in raw_windows[p].items():
            cc = res["commit_concentration"]
            if cc["distinct_humans"] == 0 or (cc["top1_count"] + cc["unattributed"]) < MIN_COMMITS:
                den = cc["top1_count"] + cc["unattributed"]
                low.append({"repo": repo, "window": p,
                            "den_nonmerge_nonbot": den})
    write_csv(low, RESULTS / "low-activity.csv",
              ["repo", "window", "den_nonmerge_nonbot"])

    print("PASS: recomputed all four streams for two windows;")
    print("cross-check vs coverage-descriptive.csv: OK"
          if not mismatches else "cross-check FAILED")
    print(f"rows: {len(flat_rows)}; evaluability thresholds: "
          f"commits>={MIN_COMMITS}, merged-PRs>={MIN_PRS}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        raise
