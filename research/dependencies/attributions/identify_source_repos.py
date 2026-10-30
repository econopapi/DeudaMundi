#!/usr/bin/env python
"""Step 3 of the research protocol: attribute each of the 37 runtime
dependencies of the frozen DeudaMundi graph to its source repository.

Nothing is rebuilt, installed or upgraded. The frozen universe is FIXED:
- nodes.csv                  (step-2 artefact; category in runtime:direct/transitive)
- ../pip-inspect.json        (step-1 photo; provides FROZEN name+version and
                              the wheel metadata `Project-URL` entries)

Evidence is gathered read-only from:
  1. the FROZEN wheel metadata (offline, bit-recorded in pip-inspect.json);
  2. the PyPI JSON API for THE EXACT frozen version
     (https://pypi.org/pypi/<name>/<version>/json) — live data, may drift:
     every response is cached verbatim under pypi-evidence/ with the UTC
     instant of the query, so decisions stay auditable;
  3. the GitHub REST API via `gh` (only to *resolve* a candidate repository:
     final full_name after redirects, status) — cached verbatim under
     github-evidence/.

Attribution rules (no guessing by name):
  confidence 'verified' — frozen metadata AND current PyPI metadata agree on
  the same canonical repository, and the repository resolves on GitHub.
  'single-source' — exactly one of the two sources holds a repo URL (it is
  not corroborated; flagged in ambiguous.md).
  'pending' — conflicting sources, unresolvable repository, or no code URL
  at all; the reason is recorded, never invented.

With cached evidence present the ENTIRE table is regenerated deterministically
(every consult uses the archived instant), so a rerun without network output
is byte-identical — see orchestrator build_source_attribution.sh.

This step identifies DISTRIBUTION -> REPOSITORY (+ repository owner).
Person maintainers and activity metrics are explicitly out of scope.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH_DIR = Path(os.environ.get("ATTR_GRAPH_DIR", HERE.parent / "graph"))
SNAPSHOT_FILE = Path(os.environ.get("ATTR_SNAPSHOT", HERE.parent / "pip-inspect.json"))
NODES_FILE = Path(os.environ.get("ATTR_NODES", GRAPH_DIR / "nodes.csv"))
OUT_DIR = Path(os.environ.get("ATTR_OUT", HERE))
# Evidence cache is SHARED and fixed in the attributions folder (not per-run
# table output): consult instants are frozen in the cached wrappers, so the
# tables stay deterministic while evidence cache directories get reused.
PYPI_CACHE = Path(os.environ.get("ATTR_EVIDENCE_DIR", HERE / "pypi-evidence"))
GITHUB_CACHE = Path(os.environ.get("ATTR_EVIDENCE_DIR", HERE / "github-evidence"))
NOW = dt.datetime.now(dt.timezone.utc)
EXPECTED_TOTAL = 37

COVERAGE_TEST = os.environ.get("COVERAGE_TEST", "")

CODE_HOSTS = {
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "codeberg.org",
    "sr.ht",
    "launchpad.net",
}
REPO_LABEL_KEYS = ("repository", "source", "source code", "source code repository", "repo")
EXTRA_HINT_KEYS = ("github", "code")
# Projects whose `home page` IS the code repository (common for small libs);
# and trackers whose URL is the repository root — accepted with a note.
SECONDARY_KEYS = ("home page", "homepage", "home", "website", "url")
TRACKER_KEYS = ("issue tracker", "tracker", "bug tracker", "issues", "bugs")


def repo_candidates(labelled: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Candidate repo URLs in priority order: explicit repo labels, github/code
    hints, homepage-and-code, then repository-root trackers. Only URLs that
    reduce to an owner/repo root on a code host count; the label used is kept
    so the evidence chain shows WHY a URL was picked."""
    ordered = []
    for tier in (REPO_LABEL_KEYS, EXTRA_HINT_KEYS, SECONDARY_KEYS, TRACKER_KEYS):
        for key in tier:
            for url in labelled.get(key, []):
                if url in {u for _, u in ordered}:
                    continue
                fragment = canonical_repo_fragment(url)
                if fragment and reduce_repo_to_owner_repo(fragment):
                    ordered.append((key, url))
    return ordered


def canonical_pkg(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def utcnow() -> str:
    return NOW.strftime("%Y-%m-%dT%H:%M:%SZ")


def http_get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "deudamundi-research/step3"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as exc:
        try:
            payload = exc.read().decode("utf-8", errors="replace")
        except Exception:
            payload = ""
        if payload.strip().startswith("{"):
            try:
                return exc.code, json.loads(payload)
            except Exception:
                pass
        return exc.code, payload or None
    except Exception as exc:  # transport-level failures
        return None, f"transport-error: {exc!r}"


def pypi_evidence(canonical_name: str, version: str) -> dict:
    """Fetch (or reuse from cache) the PyPI JSON for the EXACT frozen version."""
    directory = PYPI_CACHE / canonical_name
    directory.mkdir(parents=True, exist_ok=True)
    cache_file = directory / f"{version}.json"
    if cache_file.is_file():
        return json.loads(cache_file.read_text())
    url = f"https://pypi.org/pypi/{canonical_name}/{version}/json"
    requested_at = utcnow()
    status, body = http_get_json(url)
    wrapper = {
        "requested_at_utc": requested_at,
        "url": url,
        "http_status": status,
        "body": body,
    }
    cache_file.write_text(json.dumps(wrapper, indent=1, sort_keys=True) + "\n")
    return wrapper


def github_evidence(owner: str, repo: str) -> dict:
    """Resolve one candidate GitHub repository via `gh api` (redirects are
    resolved transparently); cache the verbatim result for audit."""
    GITHUB_CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = GITHUB_CACHE / f"{owner.lower()}__{repo.lower()}.json"
    if cache_file.is_file():
        return json.loads(cache_file.read_text())
    requested_at = utcnow()
    requested = f"{owner}/{repo}"
    proc = subprocess.run(
        ["gh", "api", f"repos/{requested}", "--jq", ".full_name"],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        error_line = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"exit {proc.returncode}"
        wrapper = {
            "requested_at_utc": requested_at,
            "requested_repo": requested,
            "resolved_full_name": None,
            "error": error_line,
        }
    else:
        resolved = proc.stdout.strip().strip('"')
        proc2 = subprocess.run(
            ["gh", "api", f"repos/{requested}",
             "--jq", '{"html_url": .html_url, "archived": .archived, "fork": .fork, "description": .description}'],
            capture_output=True, text=True, timeout=60,
        )
        details = {}
        if proc2.returncode == 0:
            try:
                details = json.loads(proc2.stdout)
            except Exception:
                details = {}
        wrapper = {
            "requested_at_utc": requested_at,
            "requested_repo": requested,
            "resolved_full_name": resolved,
            "html_url": details.get("html_url"),
            "archived": details.get("archived"),
            "fork": details.get("fork"),
            "description": details.get("description"),
        }
    cache_file.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n")
    return wrapper


CODE_PATH_NOISE = {
    "tree", "src", "issues", "releases", "commits", "blob", "tags", "pulls",
    "projects", "milestones", "wiki", "activities",
}


def frozen_urls(meta: dict) -> dict[str, list[str]]:
    """Name(lowercased)->URL pairs from the FROZEN wheel metadata."""
    urls: dict[str, list[str]] = defaultdict(list)
    project_url = meta.get("project_url")
    if isinstance(project_url, list):
        for entry in project_url:
            if isinstance(entry, str) and "," in entry:
                label, _, target = entry.partition(",")
                if target.strip():
                    urls[label.strip().lower()].append(target.strip())
            elif isinstance(entry, str) and entry:
                urls["home page"].append(entry.strip())
    home_page = meta.get("home_page")
    if isinstance(home_page, str) and home_page:
        urls["home page"].append(home_page.strip())
    return urls


def canonical_repo_fragment(url: str) -> str | None:
    """Reduce a URL to `host/path…` ONLY for code-host hosts; None otherwise."""
    url = url.strip()
    match = re.match(r"^(https?)://([^/#?]*)/?(.*?)([#?].*)?$", url)
    if not match:
        return None
    host = match.group(2).lower().removeprefix("www.")
    if host not in CODE_HOSTS:
        return None
    path = (match.group(3) or "").strip("/")
    return f"{host}{('/' + path) if path else ''}"


def reduce_repo_to_owner_repo(fragment: str) -> str | None:
    """Turn `host/owner/repo/…` into `owner/repo`; None if not applicable."""
    if not fragment:
        return None
    parts = [
        p for p in fragment.split("/")
        if p and p.lower() not in CODE_PATH_NOISE
    ]
    if len(parts) < 3:
        return None
    _, owner, repo = parts[0], parts[1], parts[2]
    if repo.lower().endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def parse_pypi_urls(info: dict) -> dict[str, list[str]]:
    urls: dict[str, list[str]] = defaultdict(list)
    project_urls = info.get("project_urls") or {}
    if isinstance(project_urls, dict):
        for label, target in project_urls.items():
            if isinstance(target, str) and target:
                urls[label.strip().lower()].append(target.strip())
    if isinstance(info.get("home_page"), str) and info["home_page"]:
        urls["home page"].append(info["home_page"].strip())
    if isinstance(info.get("project_url"), str) and info["project_url"]:
        urls["project url"].append(info["project_url"].strip())
    return urls


def main() -> int:
    nodes_rows = list(csv.DictReader(NODES_FILE.open(newline="")))
    universe = [
        r for r in nodes_rows
        if r["category"] in ("runtime:direct", "runtime:transitive")
    ]
    if COVERAGE_TEST != "drop" and len(universe) != EXPECTED_TOTAL:
        print(
            f"ERROR: universe has {len(universe)} runtime deps, expected {EXPECTED_TOTAL}",
            file=sys.stderr,
        )
        return 2

    # Simulate a lost distribution on purpose, to prove the coverage check
    # fails hard instead of reporting 36/37 as green.
    if COVERAGE_TEST == "drop":
        universe = universe[:-1]

    snapshot = json.loads(SNAPSHOT_FILE.read_text())
    frozen_by_name = {
        canonical_pkg(pkg["metadata"]["name"]): pkg["metadata"]
        for pkg in snapshot.get("installed", [])
    }

    packages = []
    for node in sorted(universe, key=lambda r: (r["category"], r["name"])):
        canonical = canonical_pkg(node["name"])
        meta = frozen_by_name.get(canonical)
        if meta is None:  # pragma: no cover
            print(f"ERROR: {canonical} missing from frozen snapshot", file=sys.stderr)
            return 2
        frozen_version = node["version"]

        labelled_frozen = frozen_urls(meta)
        pypi = pypi_evidence(canonical, frozen_version)
        consulted_at = pypi.get("requested_at_utc", "")
        pypi_body = pypi.get("body")
        pypi_info = pypi_body.get("info") if isinstance(pypi_body, dict) else None
        labelled_pypi = parse_pypi_urls(pypi_info) if pypi_info else {}

        candidates_frozen = repo_candidates(labelled_frozen)   # [(label, url), ...]
        candidates_pypi = repo_candidates(labelled_pypi)

        resolved = {}
        for origin, candidates in (("frozen", candidates_frozen), ("pypi", candidates_pypi)):
            resolved[origin] = None
            for label, url in candidates:
                fragment = canonical_repo_fragment(url)
                if not fragment:
                    continue
                pair = reduce_repo_to_owner_repo(fragment)
                if not pair:
                    continue
                evidence = github_evidence(*pair.split("/"))
                full_name = evidence.get("resolved_full_name")
                if not full_name or "/" not in str(full_name):
                    continue
                final_owner, final_repo = full_name.split("/", 1)
                resolved[origin] = {
                    "supporting_url": url,
                    "supporting_label": label,
                    "requested": pair,
                    "full_name": full_name,
                    "canonical": f"{final_owner.lower()}/{final_repo.lower()}",
                    "owner": final_owner,
                    "repo": final_repo,
                    "url": f"https://github.com/{full_name}",
                    "redirect": f"{final_owner.lower()}/{final_repo.lower()}" != pair.lower(),
                    "evidence": evidence,
                }
                break  # first resolving candidate decides

        src_frozen, src_pypi = resolved["frozen"], resolved["pypi"]
        sources = []
        if src_frozen:
            sources.append("wheel-metadata")
        if src_pypi:
            sources.append("pypi-current")

        if src_frozen and src_pypi:
            if src_frozen["canonical"] != src_pypi["canonical"]:
                confidence = "pending"
                method = "conflicting-repository"
                final = None
                notes = [
                    f"frozen points at {src_frozen['full_name']}"
                    f" (from {src_frozen['supporting_url']});"
                    f" pypi points at {src_pypi['full_name']}"
                    f" (from {src_pypi['supporting_url']})"
                ]
            else:
                confidence = "verified"
                method = "frozen-metadata+current-pypi"
                final = src_frozen
                notes = ["two independent sources agree on the same repository"]
        elif src_frozen or src_pypi:
            final = src_frozen or src_pypi
            confidence = "single-source"
            method = "frozen-metadata-only" if src_frozen else "current-pypi-only"
            notes = ["not corroborated by the other source; flagged in ambiguous.md"]
        else:
            confidence = "pending"
            method = "no-code-repository-url"
            final = None
            observed = candidates_frozen + candidates_pypi
            notes = [
                "no code-host URL in either source; do not guess"
                + (("; non-code URL observed: " + "; ".join(observed)) if observed else "")
            ]

        final_label = (final or {}).get("supporting_label")
        tier_note = (
            f"repo URL taken from metadata label '{final_label}'"
            if final_label in (SECONDARY_KEYS + TRACKER_KEYS) and final is not None
            else None
        )
        if tier_note and tier_note not in notes:
            notes.append(tier_note)

        packages.append({
            "canonical_name": canonical,
            "display_name": node["display_name"],
            "frozen_version": frozen_version,
            "category": node["category"],
            "frozen_repo_urls": [[k, u] for k, u in candidates_frozen],
            "pypi_repo_urls": [[k, u] for k, u in candidates_pypi],
            "resolved": final,
            "src_frozen": src_frozen,
            "src_pypi": src_pypi,
            "sources": sources,
            "confidence": confidence,
            "method": method,
            "consulted_at_utc": consulted_at,
            "notes": notes,
        })

    # shared repositories (after resolution)
    shared = defaultdict(list)
    for p in packages:
        final = p["resolved"]
        if final and final.get("canonical"):
            shared[final["canonical"]].append(p["canonical_name"])
    shared_repos = {k: sorted(v) for k, v in sorted(shared.items()) if len(v) > 1}

    # ------------------------------ write outputs ----------------------------
    with (OUT_DIR / "source-repos.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "name", "display_name", "frozen_version", "category",
            "repo_url", "repo_owner", "repo_name", "redirect_from",
            "supporting_urls", "method", "confidence",
            "consulted_at_utc", "shared_repository", "notes",
        ])
        for p in packages:
            final = p["resolved"]
            if final:
                repo_url = final["url"]
                owner, repo_name = final["canonical"].split("/", 1)
                redirect_from = final["evidence"].get("requested_repo", "") if final.get("redirect") else ""
                shared_flag = "yes" if final["canonical"] in shared_repos else ""
            else:
                repo_url = owner = repo_name = redirect_from = shared_flag = ""
            support = sorted({u for _, u in (*p["frozen_repo_urls"], *p["pypi_repo_urls"])})
            notes = p["notes"]
            if p["method"] in ("frozen-metadata-only", "current-pypi-only", "no-code-repository-url", "conflicting-repository") or p["confidence"] == "pending":
                notes = ["ambiguous: " + n for n in notes]
            writer.writerow([
                p["canonical_name"], p["display_name"], p["frozen_version"], p["category"],
                repo_url, owner, repo_name,
                redirect_from,
                ";".join(support),
                p["method"], p["confidence"], p["consulted_at_utc"],
                shared_flag, "; ".join(notes),
            ])

    (OUT_DIR / "attributions.json").write_text(json.dumps({
        "schema": "deudamundi.research.repo-attribution/1",
        "step": "3 - source repository per runtime dependency",
        "universe": {
            "source": "research/dependencies/graph/nodes.csv + pip-inspect.json (frozen)",
            "count": len(universe),
            "direct": sorted(p["canonical_name"] for p in packages if p["category"] == "runtime:direct"),
            "transitive": sorted(p["canonical_name"] for p in packages if p["category"] == "runtime:transitive"),
            "root_excluded": "deudamundi-api",
            "build_tooling_excluded": ["pip", "setuptools", "wheel"],
        },
        "attribution_rules": {
            "verified": "frozen wheel metadata AND current PyPI metadata agree on the same canonical repository; repository resolves on GitHub",
            "single-source": "exactly one source holds the repo URL (not corroborated; see ambiguous.md)",
            "pending": "conflicting sources, unresolvable repo, or no code URL (never guessed)",
        },
        "consulted_at_utc": sorted({p["consulted_at_utc"] for p in packages}) or [utcnow()],
        "packages": packages,
        "shared_repositories": shared_repos,
    }, indent=2, sort_keys=True) + "\n")

    # ------------------------------ coverage check ---------------------------
    universe_names = {canonical_pkg(r["name"]) for r in universe}
    attributed_names = {p["canonical_name"] for p in packages}
    duplicates = sorted(
        n for n in attributed_names
        if sum(1 for p in packages if p["canonical_name"] == n) > 1
    )
    missing = sorted(universe_names - attributed_names)
    unexpected = attributed_names - universe_names
    version_by_name_universe = {canonical_pkg(r["name"]): r["version"] for r in universe}
    node_versions_match = all(
        p["frozen_version"] == version_by_name_universe[p["canonical_name"]]
        for p in packages
    )
    counts = {
        "expected": EXPECTED_TOTAL,
        "attributed": len(packages),
        "verified": sum(1 for p in packages if p["confidence"] == "verified"),
        "single_source": sum(1 for p in packages if p["confidence"] == "single-source"),
        "pending": sum(1 for p in packages if p["confidence"] == "pending"),
    }
    report = {
        "counts": counts,
        "missing_vs_universe": missing,
        "unexpected_vs_universe": sorted(unexpected),
        "duplicated_names": duplicates,
        "frozen_versions_match_nodes": node_versions_match,
        "shared_repositories": shared_repos,
        "redirects_resolved": sorted(
            p["canonical_name"] for p in packages
            if p["resolved"] and p["resolved"].get("redirect")
        ),
        "single_source_detail": sorted(
            p["canonical_name"] for p in packages if p["confidence"] == "single-source"
        ),
        "pending_detail": sorted(
            p["canonical_name"] for p in packages if p["confidence"] == "pending"
        ),
    }
    ok = (
        counts["attributed"] == EXPECTED_TOTAL
        and not missing and not unexpected and not duplicates
        and node_versions_match
    )
    status = "PASS" if ok else "FAIL"
    (OUT_DIR / "coverage-check.txt").write_text(
        json.dumps({"result": status, **report}, indent=2, sort_keys=True) + "\n"
    )

    print(
        f"OK: attributed={counts['attributed']} verified={counts['verified']} "
        f"single-source={counts['single_source']} pending={counts['pending']} {status}"
    )
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
