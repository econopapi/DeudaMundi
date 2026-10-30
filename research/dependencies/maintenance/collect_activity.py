#!/usr/bin/env python3
"""Collect minimal public GitHub activity for step 4; never infer maintainers."""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parent / "attributions" / "source-repos.csv"
EXPECTED_SHA = "f1d2884a5907652236848be559f168a535eb898e4ef2db14e57e352472fea12c"
START = "2024-10-30T00:00:00Z"
END = "2026-10-30T00:00:00Z"
API_VERSION = "2026-03-10"
PILOT = {"fastapi/fastapi", "sqlalchemy/mako", "psycopg/psycopg", "kludex/starlette"}
ACTOR = "login __typename ... on User {databaseId} ... on Bot {databaseId} ... on Organization {databaseId}"
PR_QUERY = f"""query($owner:String!,$name:String!,$cursor:String) {{
  repository(owner:$owner,name:$name) {{
    pullRequests(first:100,after:$cursor,orderBy:{{field:UPDATED_AT,direction:DESC}},states:[OPEN,CLOSED,MERGED]) {{
      pageInfo {{hasNextPage endCursor}}
      nodes {{number updatedAt mergedAt baseRefName author {{{ACTOR}}} mergedBy {{{ACTOR}}}
        reviews(first:100) {{totalCount pageInfo {{hasNextPage endCursor}}
          nodes {{id submittedAt state author {{{ACTOR}}}}}}}
      }}
    }}
  }} rateLimit {{cost remaining}}
}}"""
MORE_REVIEWS_QUERY = f"""query($owner:String!,$name:String!,$number:Int!,$cursor:String) {{
  repository(owner:$owner,name:$name) {{pullRequest(number:$number) {{
    reviews(first:100,after:$cursor) {{pageInfo {{hasNextPage endCursor}}
      nodes {{id submittedAt state author {{{ACTOR}}}}}}}
  }}}} rateLimit {{cost remaining}}
}}"""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def actor(value):
    if not value:
        return None
    login = value.get("login")
    kind = value.get("type") or value.get("__typename")
    ident = value.get("id") if "id" in value else value.get("databaseId")
    bot = kind == "Bot" or bool(login and login.endswith("[bot]"))
    return {"id": ident, "login": login, "type": kind, "bot": bot}


def in_window(date):
    return bool(date and START <= date < END)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Client:
    def __init__(self):
        self.token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
        if not self.token:
            raise RuntimeError("No GitHub authentication token")

    def get(self, path, params=None):
        url = "https://api.github.com/" + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return self._request(url, None, {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": API_VERSION})

    def graphql(self, query, variables):
        body = json.dumps({"query": query, "variables": variables}, separators=(",", ":")).encode()
        return self._request("https://api.github.com/graphql", body, {"Accept": "application/vnd.github+json"}, query_hash=sha(body))

    def _request(self, url, body, extra_headers, query_hash=None):
        headers = {"Authorization": "Bearer " + self.token, "User-Agent": "DeudaMundi-maintenance-research", **extra_headers}
        request = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    raw = response.read()
                    status = response.status
                    data = json.loads(raw)
                    if isinstance(data, dict) and data.get("errors"):
                        raise RuntimeError(f"GraphQL errors: {data['errors']}")
                    meta = {"url": url, "method": request.get_method(), "query_sha256": query_hash,
                            "consulted_at_utc": now(), "http_status": status, "body_sha256": sha(raw),
                            "rate_remaining": response.headers.get("x-ratelimit-remaining")}
                    return data, meta
            except urllib.error.HTTPError as error:
                detail = error.read(500).decode("utf-8", errors="replace")
                if error.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt + 1)
                    continue
                raise RuntimeError(f"HTTP {error.code} for {url}: {detail}") from error
            except (urllib.error.URLError, TimeoutError) as error:
                if attempt < 3:
                    time.sleep(2 ** attempt + 1)
                    continue
                raise RuntimeError(f"Network error for {url}: {error}") from error
        raise AssertionError("unreachable")


def page_files(folder):
    return sorted(folder.glob("[0-9][0-9][0-9][0-9][0-9].json"))


def save_page(folder, number, meta, rows, next_cursor, complete, **details):
    write_json(folder / f"{number:05d}.json", {"request": meta, "records": rows,
                                                "next_cursor": next_cursor, "complete": complete, **details})


def collect_rest(client, repo, out, kind, path, params, normalizer, *, stop_before_start=False):
    folder = out / kind
    files = page_files(folder)
    if files and read_json(files[-1])["complete"]:
        return
    page = len(files) + 1
    while True:
        query = {**params, "per_page": 100, "page": page}
        data, meta = client.get(path, query)
        if not isinstance(data, list):
            raise RuntimeError(f"Expected list for {repo}/{kind} page {page}")
        rows = [normalizer(item) for item in data]
        boundary = bool(stop_before_start and rows and all((r.get("date") or "9999") < START for r in rows))
        complete = len(data) < 100 or boundary
        save_page(folder, page, meta, rows, page + 1 if not complete else None, complete,
                  response_records=len(data), boundary_stop=boundary)
        print(f"{repo} {kind} page {page}: {len(rows)}", flush=True)
        if complete:
            break
        page += 1


def commit_row(item):
    obj = item.get("commit") or {}
    return {"sha": item.get("sha"), "date": (obj.get("committer") or {}).get("date"),
            "author": actor(item.get("author")), "committer": actor(item.get("committer")),
            "parent_count": len(item.get("parents") or [])}


def release_row(item):
    return {"id": item.get("id"), "date": item.get("published_at"), "draft": item.get("draft"),
            "prerelease": item.get("prerelease"), "author": actor(item.get("author"))}


def review_row(item):
    return {"id": item.get("id"), "date": item.get("submittedAt"), "state": item.get("state"),
            "author": actor(item.get("author"))}


def pr_row(item):
    reviews = item["reviews"]
    return {"number": item["number"], "date": item.get("updatedAt"), "merged_at": item.get("mergedAt"),
            "base_ref": item.get("baseRefName"), "author": actor(item.get("author")),
            "merged_by": actor(item.get("mergedBy")), "review_total": reviews["totalCount"],
            "reviews": [review_row(r) for r in reviews["nodes"]],
            "reviews_next_cursor": reviews["pageInfo"]["endCursor"] if reviews["pageInfo"]["hasNextPage"] else None}


def collect_prs(client, repo, out):
    owner, name = repo.split("/")
    folder = out / "prs"
    files = page_files(folder)
    if files and read_json(files[-1])["complete"]:
        return
    cursor = read_json(files[-1])["next_cursor"] if files else None
    page = len(files) + 1
    while True:
        data, meta = client.graphql(PR_QUERY, {"owner": owner, "name": name, "cursor": cursor})
        connection = data["data"]["repository"]["pullRequests"]
        rows = [pr_row(item) for item in connection["nodes"]]
        boundary = bool(rows and all(r["date"] < START for r in rows))
        more = connection["pageInfo"]["hasNextPage"] and not boundary
        next_cursor = connection["pageInfo"]["endCursor"] if more else None
        meta["graphql_cost"] = data["data"]["rateLimit"]["cost"]
        meta["variables"] = {"owner": owner, "name": name, "cursor": cursor}
        save_page(folder, page, meta, rows, next_cursor, not more, response_records=len(rows), boundary_stop=boundary)
        print(f"{repo} prs page {page}: {len(rows)}", flush=True)
        if not more:
            break
        cursor = next_cursor
        page += 1


def collect_extra_reviews(client, repo, out):
    owner, name = repo.split("/")
    for file in page_files(out / "prs"):
        for pr in read_json(file)["records"]:
            cursor = pr["reviews_next_cursor"]
            if not cursor or pr["date"] < START:
                continue
            folder = out / "reviews-extra" / str(pr["number"])
            files = page_files(folder)
            if files and read_json(files[-1])["complete"]:
                continue
            if files:
                cursor = read_json(files[-1])["next_cursor"]
            page = len(files) + 1
            while cursor:
                data, meta = client.graphql(MORE_REVIEWS_QUERY, {"owner": owner, "name": name,
                                                                  "number": pr["number"], "cursor": cursor})
                conn = data["data"]["repository"]["pullRequest"]["reviews"]
                rows = [review_row(r) for r in conn["nodes"]]
                more = conn["pageInfo"]["hasNextPage"]
                next_cursor = conn["pageInfo"]["endCursor"] if more else None
                meta["graphql_cost"] = data["data"]["rateLimit"]["cost"]
                meta["variables"] = {"owner": owner, "name": name, "number": pr["number"], "cursor": cursor}
                save_page(folder, page, meta, rows, next_cursor, not more, response_records=len(rows))
                print(f"{repo} reviews PR {pr['number']} page {page}: {len(rows)}", flush=True)
                cursor = next_cursor
                page += 1


def scan_events(out):
    count = {}
    for kind in ("commits", "prs", "releases"):
        files = page_files(out / kind)
        complete = bool(files and read_json(files[-1])["complete"])
        count[kind] = {"pages": len(files), "complete": complete,
                       "records_24m": sum(1 for f in files for r in read_json(f)["records"]
                                          if in_window(r.get("merged_at") if kind == "prs" else r.get("date"))
                                          and (kind != "releases" or not r["draft"]))}
    extra = list((out / "reviews-extra").glob("*/*.json")) if (out / "reviews-extra").exists() else []
    count["reviews_extra_pages"] = len(extra)
    pending = []
    review_count = 0
    for f in page_files(out / "prs"):
        for pr in read_json(f)["records"]:
            if pr["date"] < START:
                continue
            review_count += sum(in_window(r["date"]) and r["state"] in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED") for r in pr["reviews"])
            if pr["reviews_next_cursor"]:
                files = page_files(out / "reviews-extra" / str(pr["number"]))
                if not files or not read_json(files[-1])["complete"]:
                    pending.append(pr["number"])
                review_count += sum(in_window(r["date"]) and r["state"] in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED")
                                    for f2 in files for r in read_json(f2)["records"])
    count["reviews"] = {"records_24m": review_count, "complete": count["prs"]["complete"] and not pending,
                        "pending_prs": pending}
    return count


def collect_repo(client, repo, base):
    out = base / repo.replace("/", "__")
    out.mkdir(parents=True, exist_ok=True)
    coverage_file = out / "coverage.json"
    if coverage_file.exists() and read_json(coverage_file)["complete"]:
        return read_json(coverage_file)
    metadata_file = out / "repository.json"
    if not metadata_file.exists():
        data, meta = client.get("repos/" + repo)
        write_json(metadata_file, {"request": meta, "id": data["id"], "full_name": data["full_name"],
                                   "default_branch": data["default_branch"], "archived": data["archived"],
                                   "fork": data["fork"]})
    metadata = read_json(metadata_file)
    full = metadata["full_name"]
    if full.lower() != repo.lower():
        raise RuntimeError(f"Repository redirect {repo} -> {full}; inspect before continuing")
    collect_rest(client, repo, out, "commits", "repos/" + repo + "/commits",
                 {"sha": metadata["default_branch"], "since": START, "until": END}, commit_row)
    collect_rest(client, repo, out, "releases", "repos/" + repo + "/releases",
                 {}, release_row, stop_before_start=True)
    collect_prs(client, repo, out)
    collect_extra_reviews(client, repo, out)
    coverage = {"repo": repo, "repository_id": metadata["id"], "default_branch": metadata["default_branch"],
                "archived": metadata["archived"], "fork": metadata["fork"], "checked_at_utc": now(),
                "streams": scan_events(out)}
    coverage["complete"] = all(coverage["streams"][k]["complete"] for k in ("commits", "prs", "releases", "reviews"))
    write_json(coverage_file, coverage)
    return coverage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="Only the four preregistered pilot repositories")
    parser.add_argument("--repo", help="One repository from the fixed universe")
    parser.add_argument("--output", type=Path, default=HERE / "data")
    args = parser.parse_args()
    if sha(SOURCES.read_bytes()) != EXPECTED_SHA:
        raise RuntimeError("Step 3 source-repos.csv differs from the frozen attribution")
    with SOURCES.open(newline="", encoding="utf-8") as f:
        repos = sorted({row["repo_owner"] + "/" + row["repo_name"] for row in csv.DictReader(f)})
    if len(repos) != 35:
        raise RuntimeError(f"Expected 35 unique repositories, found {len(repos)}")
    if args.repo:
        if args.repo not in repos:
            raise RuntimeError(f"Repository not in fixed universe: {args.repo}")
        repos = [args.repo]
    elif args.pilot:
        repos = [repo for repo in repos if repo in PILOT]
        if len(repos) != 4:
            raise RuntimeError(f"Expected 4 pilot repositories, found {len(repos)}")
    args.output.mkdir(parents=True, exist_ok=True)
    need_network = any(not (args.output / repo.replace("/", "__") / "coverage.json").exists()
                       or not read_json(args.output / repo.replace("/", "__") / "coverage.json")["complete"]
                       for repo in repos)
    client = Client() if need_network else None
    failures = []
    for repo in repos:
        try:
            result = collect_repo(client, repo, args.output)
            print(f"{repo}: {'COMPLETE' if result['complete'] else 'INCOMPLETE'}", flush=True)
        except Exception as error:
            failures.append({"repo": repo, "error": str(error), "at_utc": now()})
            print(f"{repo}: ERROR {error}", file=sys.stderr, flush=True)
            if args.repo:
                break
    summary = {"universe": 35, "source_csv_sha256": EXPECTED_SHA,
               "window_start": START, "window_end_exclusive": END,
               "selected": repos, "completed": [], "failed": failures}
    for repo in repos:
        coverage_file = args.output / repo.replace("/", "__") / "coverage.json"
        if coverage_file.exists() and read_json(coverage_file)["complete"]:
            summary["completed"].append(repo)
    write_json(args.output / "run-summary.json", summary)
    return 1 if failures or len(summary["completed"]) != len(repos) else 0


if __name__ == "__main__":
    sys.exit(main())
