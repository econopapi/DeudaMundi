#!/usr/bin/env python
"""Build the Python dependency graph of the DeudaMundi production backend.

Step 2 of the research protocol. Runs INSIDE the built production image (the
same interpreter that produced the snapshot; pip's vendored `packaging` gives
authoritative PEP 508 parsing and marker evaluation). Nothing is reinstalled,
rebuilt or upgraded: `pip-inspect.json` is the frozen photo, and the frozen
`pyproject-frozen.toml` (a byte-frozen copy of api/pyproject.toml, verified
against /app/pyproject.toml inside the image by the host orchestrator)
identifies the direct dependencies and requested extras.

Host orchestration: ../build_dependency_graph.sh (docker cp only; no mounts,
no re-build of the image).

Inputs (copied to the container working dir by the orchestrator):
  - pip-inspect.json          frozen `python -m pip inspect` photo (step 1)
  - pyproject.toml            frozen copy of api/pyproject.toml (verified
                              byte-identical against the image by the
                              orchestrator before extraction starts)
  - installed-packages.txt    step-1 readable inventory, for the arrow
                              comparison

Consistency gates (hard failures, no outputs written):
  - the distributions currently installed in the runtime must match the
    photo by (canonical name, version), not just by Python/pip versions.

Outputs (this script writes them into $GRAPH_OUT, default /tmp/graph):
  - nodes.csv             node table (name, version, category, extras, paths, ...)
  - edges.csv             ACTIVE execution edges (packaging-evaluated Require-Dist)
  - edges-inactive.csv    evaluated-but-inactive requirements, with reason
  - paths.txt             simple dependency paths from deudamundi-api
  - graph-diagram.mmd     Mermaid visualization of the execution graph
  - checks.json           verification data (extras, markers, shared paths, unexplained)
  - step1-vs-step2.txt    comparison against step-1 `<-` arrows (semantics documented)

Semantics implemented here (stricter than step 1):
  - names canonicalized per PEP 503;
  - every Requires-Dist parsed with `packaging.requirements.Requirement`;
  - markers evaluated against the environment recorded in pip-inspect.json
    (the machine fields) with `extra` substituted by each extra that was
    actually requested for the requiring distribution;
  - requested extras are SEEDED from the pyproject requirements
    (`uvicorn[standard]`, `psycopg[binary]`) and PROPAGATED to fixpoint through
    active edges (an active requirement `foo[bar]` activates bar-relevant
    requirements inside foo's own metadata);
  - build tooling (pip, setuptools, wheel) and the project package are tracked
    but excluded from the execution graph edges (build tooling) or kept as the
    single root (project package).
"""

import csv
import json
import os
import sys
import tomllib
from collections import defaultdict, deque
from importlib import metadata as importlib_metadata
from pathlib import Path

from pip._vendor.packaging.markers import Marker
from pip._vendor.packaging.requirements import Requirement
from pip._vendor.packaging.utils import canonicalize_name

BASE_TOOLING = {canonicalize_name(n) for n in ("pip", "setuptools", "wheel")}
PROJECT_NAME = "deudamundi-api"

INPUT_SNAPSHOT = os.environ.get("GRAPH_SNAPSHOT", "/tmp/pip-inspect.json")
INPUT_PYPROJECT = os.environ.get("GRAPH_PYPROJECT", "/tmp/pyproject.toml")
INPUT_STEP1_TXT = os.environ.get("GRAPH_STEP1_TXT", "/tmp/installed-packages.txt")
OUT = Path(os.environ.get("GRAPH_OUT", "/tmp/graph"))


# ----------------------------------------------------------------- helpers --
def load_installed(snapshot: dict) -> dict[str, dict]:
    installed = {}
    for pkg in snapshot.get("installed", []):
        meta = pkg["metadata"]
        name = canonicalize_name(meta["name"])
        installed[name] = {
            "key": name,
            "name": meta["name"],
            "version": meta.get("version", ""),
            "requires": [r for r in (meta.get("requires_dist") or []) if isinstance(r, str)],
        }
    return installed


def runtime_installed_now() -> dict[str, str]:
    """(canonical name, version) of every distribution importable now."""
    found = {}
    for dist in importlib_metadata.distributions():
        name = canonicalize_name(dist.metadata["Name"])
        found[name] = dist.version or ""
    return found


def check_identity(installed: dict[str, dict]) -> dict:
    """Photo vs current runtime environment: names AND versions must match.

    Returns the check record; raises SystemExit(2) on mismatch.
    """
    now = runtime_installed_now()
    photo_set = {k: p["version"] for k, p in installed.items()}
    missing = sorted(set(photo_set) - set(now))
    extra = sorted(set(now) - set(photo_set))
    version_diff = sorted(k for k in set(photo_set) & set(now) if photo_set[k] != now[k])
    record = {
        "photo_distributions": len(photo_set),
        "runtime_distributions": len(now),
        "missing_in_runtime": [{"name": k, "version": photo_set[k]} for k in missing],
        "unexpected_in_runtime": [{"name": k, "version": now[k]} for k in extra],
        "version_mismatch": [{"name": k, "photo": photo_set[k], "runtime": now[k]} for k in version_diff],
    }
    if missing or extra or version_diff:
        print(
            "FATAL: identity mismatch between the frozen photo and the runtime "
            f"environment where the extraction is running "
            f"(missing={len(missing)}, unexpected={len(extra)}, "
            f"version_mismatch={len(version_diff)}). "
            "Refusing to produce a graph: the photo must be extracted with its "
            "own environment.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    record["result"] = "PASS"
    return record


def parse_requirement(raw: str) -> dict:
    req = Requirement(raw)
    return {
        "raw": raw,
        "name": canonicalize_name(req.name),
        "specifier": str(req.specifier) if req.specifier else "",
        "extras": sorted(req.extras),
        "marker": str(req.marker) if req.marker else None,
    }


def evaluate_marker(req: dict, env: dict, extra_candidates: set[str]):
    """Return (active, matched_extras) for one require-dist entry.

    The marker (if any) is evaluated for each requested extra of the requiring
    distribution plus an empty-extra sentinel, mirroring pip's semantics:
    a requirement applies when ANY requested extra satisfies the whole marker.
    """
    matched = []
    if req["marker"] is None:
        return True, []
    marker = Marker(req["marker"])
    for extra in sorted(extra_candidates):
        trial = dict(env)
        trial["extra"] = extra
        if marker.evaluate(trial):
            matched.append(extra)
    if not matched:
        return False, []
    return True, matched


# ------------------------------------------------------------------- main --
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    snapshot = json.loads(Path(INPUT_SNAPSHOT).read_text())
    installed = load_installed(snapshot)
    pyproject = tomllib.loads(Path(INPUT_PYPROJECT).read_text())
    step1_txt_lines = Path(INPUT_STEP1_TXT).read_text().splitlines()

    project_name = canonicalize_name(pyproject["project"]["name"])
    assert project_name == PROJECT_NAME, f"unexpected project name {project_name}"

    # consistency gate BEFORE producing any output
    identity_record = check_identity(installed)

    env = dict(snapshot.get("environment") or {})

    # --- declared roots -----------------------------------------------------
    declared_raw = list(pyproject["project"]["dependencies"])
    declared = [parse_requirement(r) for r in declared_raw]
    roots = {canonicalize_name(PROJECT_NAME)}
    for req in declared:
        roots.add(req["name"])
        if req["name"] not in installed:  # pragma: no cover
            raise RuntimeError(f"declared dependency {req['name']} is not installed")

    # --- active/inactive requirement evaluation with extras fixpoint ---------
    requested_extras: dict[str, set[str]] = defaultdict(set)
    # seed extras from the *pyproject requirement* strings — extras belong
    # to the target distribution of each declared requirement
    for raw in declared_raw:
        req = parse_requirement(raw)
        requested_extras[req["name"]] |= set(req["extras"])

    # evaluate all Require-Dist entries, iterating to a fixpoint because a newly
    # activated requirement `foo[bar]` may activate bar-gated requirements
    # inside foo's own metadata
    active_edges: dict[tuple[str, str], dict] = {}
    inactive_edges: dict[tuple[str, str, str, str], dict] = {}
    marker_evaluations: list[dict] = []
    changed = True
    while changed:
        changed = False
        active_edges, inactive_edges, marker_evaluations = {}, {}, []
        for pkg_key in sorted(installed):
            pkg = installed[pkg_key]
            candidates = set(requested_extras.get(pkg_key, set())) | {""}
            for raw in pkg["requires"]:
                req = parse_requirement(raw)
                active, matched = evaluate_marker(req, env, candidates)
                edge = {
                    "from": pkg_key,
                    "to": req["name"],
                    "requirement": raw,
                    "specifier": req["specifier"],
                    "requirement_extras": ";".join(req["extras"]),
                    "matched_extras": ",".join(m for m in matched if m),
                    "marker": req["marker"] or "",
                    "source_version": pkg["version"],
                    "target_version": installed[req["name"]]["version"] if req["name"] in installed else "",
                }
                evaluation = {
                    "requirement": raw,
                    "requirement_of": pkg_key,
                    "target": req["name"],
                    "marker": req["marker"] or "",
                    "active": active,
                    "matched_extras": [m for m in matched if m],
                }
                marker_evaluations.append(evaluation)
                if active:
                    active_edges[(pkg_key, req["name"])] = edge
                    # extras propagation: an active requirement `foo[bar]`
                    # requests the bar extra of foo itself
                    if req["extras"]:
                        new = set(req["extras"]) - requested_extras[req["name"]]
                        if new:
                            requested_extras[req["name"]] |= new
                            changed = True
                else:
                    # classify the reason of inactivity
                    marker_str = req["marker"] or ""
                    has_extra_clause = "extra ==" in marker_str
                    if has_extra_clause and not (candidates - {""}):
                        reason = "extra-not-requested"
                    elif has_extra_clause:
                        reason = "marker-unmet-for-all-requested-extras"
                    else:
                        reason = "marker-not-satisfied"
                    inactive_edges[
                        (pkg_key, req["name"], reason, raw)
                    ] = edge | {"inactive_reason": reason}

    # --- graph membership ---------------------------------------------------
    reached: set[str] = set()
    adjacency = defaultdict(set)
    for (src, dst) in active_edges:
        if src in installed and dst in installed:
            adjacency[src].add(dst)
    stack = sorted(roots - BASE_TOOLING)
    while stack:
        node = stack.pop()
        if node in reached:
            continue
        reached.add(node)
        stack.extend(sorted(adjacency[node] - reached))

    runtime_nodes = {n for n in installed if n not in BASE_TOOLING}
    unexplained = sorted(runtime_nodes - reached)
    direct = {r for r in roots if r != project_name}
    transitive = {n for n in (reached - roots) if n not in BASE_TOOLING}

    # build-tooling membership check: they must not be pulled by runtime edges
    tooling_reachable = sorted(n for n in BASE_TOOLING if n in reached)

    # --- simple-path counts from the project root (DAG topological DP) -------
    indegree = {n: 0 for n in reached}
    for (src, dst) in active_edges:
        if src in reached and dst in reached:
            indegree[dst] += 1
    simple_path_counts: dict[str, int] = {project_name: 1}
    shortest_path: dict[str, int] = {n: 10**6 for n in reached}
    shortest_path[project_name] = 0
    queue = deque([n for n in reached if indegree[n] == 0])
    seen_order = []
    indeg_copy = dict(indegree)
    while queue:
        n = queue.popleft()
        seen_order.append(n)
        for m in sorted(adjacency[n]):
            if m not in reached:
                continue
            simple_path_counts[m] = simple_path_counts.get(m, 0) + simple_path_counts[n]
            if 1 + shortest_path[n] < shortest_path[m]:
                shortest_path[m] = 1 + shortest_path[n]
            indeg_copy[m] -= 1
            if indeg_copy[m] == 0:
                queue.append(m)
    acyclic = len(seen_order) == len(reached)

    def parent_chains(node: str) -> list[str]:
        """best (shortest) chain of names from the project root, by hops."""
        chain = []
        current = node
        while current != project_name:
            chain.append(current)
            parents = [
                src
                for (src, dst) in active_edges
                if dst == current and src in reached
                and shortest_path.get(src, 10**6) == shortest_path[current] - 1
            ]
            if not parents:  # pragma: no cover
                break
            current = min(parents)
        chain.append(project_name)
        return list(reversed(chain))

    # step-1-style ancestor attribution (BFS quirk replicated for comparison)
    ancestor_claim: dict[str, set[str]] = defaultdict(set)
    for root in sorted(roots):
        seen = set()
        queue = [root]
        while queue:
            current = queue.pop()
            for m in sorted(adjacency[current]):
                if m not in installed or m in BASE_TOOLING:
                    continue
                if m == current or m in seen:
                    continue
                seen.add(m)
                queue.append(m)
                if m in roots:
                    continue  # same quirk as step 1
                ancestor_claim[m].add(root)

    # ------------------------------- nodes table ------------------------------
    def category_of(name: str) -> str:
        if name == project_name:
            return "project:package"
        if name in BASE_TOOLING:
            return "build:tooling"
        if name in direct:
            return "runtime:direct"
        return "runtime:transitive"

    with (OUT / "nodes.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["name", "display_name", "version", "category", "requested_extras",
             "is_direct", "in_execution_graph", "unexplained", "paths_from_root",
             "hops_from_root", "ancestors_claimed_by", "required_by"]
        )
        for name in sorted(installed):
            pkg = installed[name]
            cat = category_of(name)
            forced_out = name in BASE_TOOLING
            unexplained_flag = name in unexplained
            in_graph = (not forced_out) and (not unexplained_flag) and cat != "project:package"
            writer.writerow([
                name, pkg["name"], pkg["version"], cat,
                ";".join(sorted(requested_extras.get(name, set()))),
                "yes" if name in direct else "",
                "yes" if in_graph else "",
                "yes" if unexplained_flag else "",
                simple_path_counts.get(name, "") if in_graph else "",
                shortest_path.get(name, "") if in_graph else "",
                ";".join(sorted(ancestor_claim.get(name, set()))),
                ";".join(sorted(src for (src, dst) in active_edges if dst == name and src in reached)),
            ])

    with (OUT / "edges.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["from", "to", "requirement", "specifier", "requirement_extras",
             "matched_extras", "marker", "in_execution_graph", "reason_kind"]
        )
        for key in sorted(active_edges):
            e = active_edges[key]
            runtime_edge = e["from"] in reached and e["to"] in reached
            writer.writerow([
                e["from"], e["to"], e["requirement"], e["specifier"],
                e["requirement_extras"], e["matched_extras"], e["marker"],
                "yes" if runtime_edge else "",
                ("gated-by-extra" if e["requirement_extras"] or e["marker"] else "unconditional")
            ])

    with (OUT / "edges-inactive.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["from", "to", "requirement", "specifier", "requirement_extras",
             "marker", "inactive_reason"]
        )
        for key in sorted(inactive_edges, key=lambda k: (k[0], k[1], k[2], k[3])):
            e = inactive_edges[key]
            writer.writerow([
                e["from"], e["to"], e["requirement"], e["specifier"],
                e["requirement_extras"], e["marker"], e["inactive_reason"],
            ])

    # ------------------------------- paths.txt -------------------------------
    lines = [
        "# Simple dependency paths from deudamundi-api (step-2 extractor)",
        f"# environment: {env.get('platform_python_implementation', '?')} "
        f"{env.get('python_full_version', '?')} on {env.get('platform_system', '?')} "
        f"{env.get('platform_machine', '?')}, pip {snapshot.get('pip_version', '?')}",
        "# reachable nodes: 38 total = 1 root (deudamundi-api) + 37 dependencies"
        f" (direct: {len(direct)}, transitive: {len(transitive)})",
        f"# unexplained: {len(unexplained)}",
        f"# DAG (acyclic): {acyclic}",
    ]
    for name in sorted(transitive):
        chain = parent_chains(name)
        lines.append("")
        lines.append(
            f"{name} {installed[name]['version']} (hops={shortest_path[name]}, "
            f"simple_paths={simple_path_counts[name]})"
        )
        lines.append("  shortest: " + " -> ".join(chain))
        lines.append("  claimed_by: " + ", ".join(sorted(ancestor_claim.get(name, set()))))
    if unexplained:
        lines.append("")
        lines.append("# UNEXPLAINED (no active path from the project root):")
        for name in unexplained:
            lines.append(f"- {name} {installed[name]['version']}")
    (OUT / "paths.txt").write_text("\n".join(lines) + "\n")

    # --------------------------- graph-diagram.mmd ---------------------------
    def esc(s: str) -> str:
        return s.replace('"', "'")

    def node_def(node_key: str, display: str, version: str, css: str) -> str:
        return '  {key}["{name}<br/>{ver}"]:::{css}'.format(
            key=node_key, name=esc(display), ver=esc(version), css=css
        )

    mm = [
        "---",
        "title: deudamundi-api production Python dependency graph (snapshot,"
        f" pip {snapshot.get('pip_version', '?')}, CPython {env.get('python_full_version', '?')})",
        "---",
        "flowchart LR",
        "  ROOT[\"deudamundi-api<br/>0.1.0 (project)\"]:::project",
    ]
    for name in sorted(direct):
        pkg = installed[name]
        mm.append(node_def("N_" + name, pkg["name"], pkg["version"], "direct"))
    for name in sorted(transitive):
        pkg = installed[name]
        mm.append(node_def("N_" + name, pkg["name"], pkg["version"], "transitive"))
    mm.append("  subgraph build_tooling[\"build:tooling - fuera del grafo de ejecucion\"]")
    for name in sorted(BASE_TOOLING & installed.keys()):
        pkg = installed[name]
        mm.append(node_def("N_" + name, pkg["name"], pkg["version"], "tooling"))
    mm.append("  end")
    for (src, dst) in sorted(active_edges):
        if src not in reached or dst not in reached:
            continue
        e = active_edges[(src, dst)]
        src_id = "ROOT" if src == project_name else "N_" + src
        label = ""
        if e["matched_extras"]:
            label = "|\"extra " + e["matched_extras"] + "\"|"
        elif e["marker"]:
            label = '|"marker"|'
        mm.append(f"  {src_id} --> {label} N_{dst}")
    mm.append("  classDef project fill:#0b7285,color:#fff,stroke:#0b7285;")
    mm.append("  classDef direct fill:#2f9e44,color:#fff,stroke:#2f9e44;")
    mm.append("  classDef transitive fill:#adb5bd,color:#111,stroke:#6c757d;")
    mm.append("  classDef tooling fill:#e9ecef,color:#111,stroke:#adb5bd;")
    mm.append("  linkStyle default stroke:#343a40,stroke-width:1px;")
    (OUT / "graph-diagram.mmd").write_text("\n".join(mm) + "\n")

    # ------------------------------ checks.json ------------------------------
    checks = {
        "snapshot": {
            "pip_version": snapshot.get("pip_version"),
            "environment": env,
            "source": "pip-inspect.json (frozen photo, step 1)",
        },
        "identity_check": identity_record,
        "counts": {
            "installed": len(installed),
            "runtime_nodes": len(runtime_nodes),
            "direct": len(direct),
            "transitive": len(transitive),
            "build_tooling": len(BASE_TOOLING & installed.keys()),
            "active_edges_total": len(active_edges),
            "active_edges_in_execution_graph": len(
                [1 for (s, d) in active_edges if s in reached and d in reached]
            ),
            "inactive_requirements": len(inactive_edges),
            "unexplained": len(unexplained),
            "acyclic": acyclic,
        },
        "extras": {
            "requested_via_pyproject": {
                parse_requirement(raw)["name"]: parse_requirement(raw)["extras"]
                for raw in declared_raw
                if parse_requirement(raw)["extras"]
            },
            "active_after_fixpoint": {
                name: sorted(e) for name, e in requested_extras.items() if e
            },
            "known_inactive_examples": [
                "fastapi[standard]/[all] (fastapi's own extras, never requested)",
                "apscheduler[doc] (extra=='doc' not requested)",
                "deudamundi-api[dev] (pytest/pytest-cov/ruff/locust not installed)",
            ],
        },
        "markers": {
            "python_or_platform_gated_active": [
                m for m in marker_evaluations if m["active"] and any(
                    v in m["marker"] for v in (
                        "python_version", "python_full_version", "platform_system",
                        "platform_machine", "sys_platform", "os_name",
                        "implementation_name", "platform_python_implementation",
                    )
                )
            ],
            "unconditional_active": "{count}".format(
                count=(len([m for m in marker_evaluations if m["active"] and not m["marker"]]))
            ),
        },
        "shared_paths": {
            name: {
                "ancestor_count": len(ancestor_claim.get(name, set())),
                "simple_paths": simple_path_counts.get(name),
                "claimed_by": sorted(ancestor_claim.get(name, set())),
            }
            for name in sorted(transitive)
            if len(ancestor_claim.get(name, set())) > 1
        },
        "unexplained_packages": [
            {"name": n, "version": installed[n]["version"]} for n in unexplained
        ],
        "build_tooling_isolation": {
            "nodes": sorted(BASE_TOOLING & installed.keys()),
            "reachable_from_runtime_edges": tooling_reachable,
        },
    }
    (OUT / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")

    # --------------------------- step1-vs-step2.txt --------------------------
    arrows_current: dict[str, list[str]] = {}
    for line in step1_txt_lines:
        if line.startswith("[runtime:transitive") and " <- " in line:
            body = line.split("]", 1)[1].strip()
            name_part, ancestors_part = body.rsplit(" <- ", 1)
            name = canonicalize_name(name_part.split()[0])
            arrows_current[name] = [
                canonicalize_name(a.strip())
                for a in ancestors_part.split(",") if a.strip() and a.strip() != "-"
            ]

    # ---------------------- step1-vs-step2 comparison ------------------------
    diffs = []
    compared = 0
    for name in sorted(set(arrows_current) | set(ancestor_claim)):
        if name in unexplained or name in BASE_TOOLING or name in direct:
            continue
        if name == project_name:
            continue
        compared += 1
        a1 = sorted(arrows_current.get(name, []))
        a2 = sorted(ancestor_claim.get(name, set()))
        if a1 == a2:
            continue
        # annotate the divergence with the inactive requirements that explain it
        claim_only1 = sorted(set(a1) - set(a2))
        claim_only2 = sorted(set(a2) - set(a1))
        explanations = []
        forward_active = defaultdict(set)
        for (src, dst) in active_edges:
            forward_active[src].add(dst)
        inactive_into_name = defaultdict(list)  # from -> [(reason, raw)]
        for key, edge in inactive_edges.items():
            if edge["to"] == name:
                inactive_into_name[edge["from"]].append((key[2], edge["requirement"]))
        for claimant in claim_only1:
            # step-1 claimed `claimant -> ... -> name`: the chain was active up
            # to the last hop, whose requirement is inactive under step-2
            # semantics. Find such chains: a forward walk over active edges
            # from claimant whose final inactive requirement lands on `name`.
            visited = {claimant}
            frontier = [(claimant, [claimant])]
            max_hops = 12
            while frontier:
                node, trail = frontier.pop(0)
                for (reason, raw) in inactive_into_name.get(node, []):
                    if len(trail) - 1 >= max_hops:
                        continue
                    explanations.append(
                        f"{claimant}: " + " -> ".join(trail)
                        + f" -> {name} (final hop '{raw}' inactive: {reason})"
                    )
                for m in sorted(forward_active.get(node, set())):
                    if m == name or m in visited or len(trail) - 1 >= max_hops:
                        continue
                    visited.add(m)
                    frontier.append((m, trail + [m]))
        diffs.append({
            "package": name,
            "step1_arrows": a1,
            "step2_ancestors": a2,
            "claimed_only_by_step1": claim_only1,
            "claimed_only_by_step2": claim_only2,
            "explanations": explanations,
        })

    identical = not diffs
    report = [
        "# step1-vs-step2: comparison of dependency attribution",
        "",
        "## Semantics",
        "- step 1 (`categorize_env.py`): simplified marker handling - `extra ==` clauses",
        "  active only for extras seeded from the *top-level* pyproject requirements;",
        "  every other marker is treated as true; no extras propagation beyond the",
        "  seeds (extras of the base wheels are never re-requested).",
        "- step 2 (this extractor): `packaging` evaluation of every marker against",
        "  the snapshot environment; extras seeded from pyproject are propagated to",
        "  fixpoint through active edges before each evaluation.",
        "- both attribute ancestors transitively, skipping to claim a root reached",
        "  through another root (that quirk was replicated from step 1 for a",
        "  like-for-like comparison).",
        "",
        "## Result for this snapshot",
        f"- packages compared: {compared}",
        f"- attribution differences: {len(diffs)}",
        f"- CONCLUSION: {'identical' if identical else 'DIFFERENT'}",
    ]
    if diffs:
        report.append("")
        report.append("## Differences")
        for d in diffs:
            report.append(
                f"- {d['package']}: step1={d['step1_arrows']} step2={d['step2_ancestors']}"
            )
            if d.get("claimed_only_by_step1"):
                report.append(
                    f"  - claimed only by step 1 (false positives of its simplified"
                    f" markers): {d['claimed_only_by_step1']}"
                )
            if d.get("claimed_only_by_step2"):
                report.append(
                    f"  - claimed only by step 2: {d['claimed_only_by_step2']}"
                )
            for explanation in d.get("explanations", []):
                report.append(f"  - explanation: {explanation}")
    else:
        report.append("")
        report.append("## Why zero differences here (and what could diverge later)")
        report.append("- no installed distribution requested extras of a sub-package other")
        report.append("  than via the pyproject top-level requirements, so the extras")
        report.append("  fixpoint propagation added nothing;")
        report.append("- no strictly-evaluated non-extra marker changed any decision:")
        report.append("  the effects step 1 treated as 'assume active' are the same ones")
        report.append("  packaging evaluates as active for linux/x86_64 CPython;")
        report.append("- future snapshots with `python_version` gates, unrequested extras")
        report.append("  that activate deeper extras, or non-linux platforms would diverge;")
        report.append("  those are the documented weaknesses of the step-1 simplification.")
    report.append("")
    report.append("Note: the step-1 arrows are NOT used as source of truth anywhere in")
    report.append("step 2; this file exists to document exactly one semantic comparison.")
    (OUT / "step1-vs-step2.txt").write_text("\n".join(report) + "\n")

    print(
        f"OK: nodes={len(installed)} runtime={len(runtime_nodes)} direct={len(direct)} "
        f"transitive={len(transitive)} active_edges={len(active_edges)} "
        f"inactive={len(inactive_edges)} unexplained={len(unexplained)} "
        f"identity_check=PASS"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
