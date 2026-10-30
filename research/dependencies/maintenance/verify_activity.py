#!/usr/bin/env python3
"""Check step-4 coverage and derive descriptive event counts without interpretation."""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SOURCE = HERE.parent / "attributions" / "source-repos.csv"
SOURCE_SHA = "f1d2884a5907652236848be559f168a535eb898e4ef2db14e57e352472fea12c"
START_24 = "2024-10-30T00:00:00Z"
START_12 = "2025-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def page_files(folder):
    return sorted(folder.glob("[0-9][0-9][0-9][0-9][0-9].json"))


def pages(folder):
    files = page_files(folder)
    if not files:
        raise ValueError(f"No pages: {folder}")
    if [f.name for f in files] != [f"{i:05d}.json" for i in range(1, len(files) + 1)]:
        raise ValueError(f"Page gap: {folder}")
    result = [load(f) for f in files]
    for i, page in enumerate(result):
        if page["complete"] != (i == len(result) - 1):
            raise ValueError(f"Incorrect completion flag: {files[i]}")
        request = page["request"]
        if request["http_status"] != 200 or len(request["body_sha256"]) != 64:
            raise ValueError(f"Bad request receipt: {files[i]}")
        if page["response_records"] != len(page["records"]):
            raise ValueError(f"Page count mismatch: {files[i]}")
        if i < len(result) - 1 and not page["next_cursor"]:
            raise ValueError(f"Missing pagination cursor: {files[i]}")
    return result


def records(folder):
    return [r for p in pages(folder) for r in p["records"]]


def unique(items, key, label):
    ids = [item[key] for item in items]
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError(f"Missing or duplicate {label}")


def within(date, start):
    return bool(date and start <= date < END)


def breakdown(items, date_key, start):
    selected = [item for item in items if within(item.get(date_key), start)]
    return {"events": len(selected),
            "bot": sum(bool((item.get("author") or {}).get("bot")) for item in selected),
            "unattributed": sum(item.get("author") is None for item in selected)}


def verify_repo(repo):
    folder = DATA / repo.replace("/", "__")
    meta = load(folder / "repository.json")
    coverage = load(folder / "coverage.json")
    if meta["full_name"].lower() != repo.lower() or coverage["repo"] != repo or not coverage["complete"]:
        raise ValueError(f"Metadata or coverage incomplete: {repo}")
    commits = records(folder / "commits")
    prs = records(folder / "prs")
    releases = records(folder / "releases")
    if pages(folder / "releases")[-1]["response_records"] == 100:
        raise ValueError(f"Release pagination not exhausted: {repo}")
    unique(commits, "sha", f"commit SHA in {repo}")
    unique(prs, "number", f"PR number in {repo}")
    unique(releases, "id", f"release id in {repo}")
    # A page before the boundary may contain post-cutoff updates. The PR list is
    # a current view, so these do not become events until timestamps pass the cut.
    reviews = []
    for pr in prs:
        if pr["date"] < START_24:
            continue
        these = pr["reviews"][:]
        if pr["reviews_next_cursor"]:
            these.extend(records(folder / "reviews-extra" / str(pr["number"])))
        if len(these) != pr["review_total"]:
            raise ValueError(f"Missing reviews: {repo} PR {pr['number']} ({len(these)}/{pr['review_total']})")
        unique(these, "id", f"review id in {repo} PR {pr['number']}")
        for review in these:
            if review["state"] in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}:
                reviews.append(review)
    merged = [p for p in prs if p["merged_at"]]
    published = [r for r in releases if not r["draft"]]
    result = {"repo": repo, "repository_id": meta["id"], "archived": meta["archived"],
              "fork": meta["fork"], "default_branch": meta["default_branch"],
              "commit_pages": len(page_files(folder / "commits")),
              "pr_pages": len(page_files(folder / "prs")),
              "release_pages": len(page_files(folder / "releases")),
              "review_extra_pages": sum(1 for _ in (folder / "reviews-extra").glob("*/*.json"))}
    for period, start in (("12m", START_12), ("24m", START_24)):
        for kind, events, date_key in (("commits", commits, "date"), ("merged_prs", merged, "merged_at"),
                                       ("reviews", reviews, "date"), ("releases", published, "date")):
            for key, value in breakdown(events, date_key, start).items():
                result[f"{period}_{kind}_{key}"] = value
    for kind, metric in (("commits", "commits"), ("prs", "merged_prs"),
                         ("reviews", "reviews"), ("releases", "releases")):
        if coverage["streams"][kind]["records_24m"] != result[f"24m_{metric}_events"]:
            raise ValueError(f"Coverage count mismatch: {repo}/{kind}")
    return result


def main():
    global DATA
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=HERE / "coverage-descriptive.csv")
    args = parser.parse_args()
    DATA = args.data
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source attribution hash changed")
    with SOURCE.open(newline="", encoding="utf-8") as f:
        repos = sorted({r["repo_owner"] + "/" + r["repo_name"] for r in csv.DictReader(f)})
    if len(repos) != 35:
        raise ValueError(f"Expected 35 repos, got {len(repos)}")
    rows = [verify_repo(repo) for repo in repos]
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS: 35/35 repositories, four event types, two windows; wrote {path.name}")
    for metric in ("commit_pages", "pr_pages", "release_pages", "review_extra_pages"):
        print(f"{metric}: {sum(r[metric] for r in rows)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
