#!/usr/bin/env python
"""Categorize the production-image Python environment from `pip inspect` output.

Designed to run inside the built production image (Python >= 3.11 provides
``tomllib``) with the artifacts directory mounted at /work:

    docker run --rm --entrypoint python -e SNAPSHOT_WRITES_MANIFEST=1 \
        -v "$OUT_DIR":/work "${IMAGE}" /work/categorize_env.py

Inputs (in the mounted directory):
  - pip-inspect.json         raw `python -m pip inspect` output

Environment facts (optional, only used to write manifest.json):
  - SNAPSHOT_WRITES_MANIFEST=1        enable manifest generation
  - SNAPSHOT_COMMIT_SHA, SNAPSHOT_COMMIT_DATE, SNAPSHOT_COMMIT_SUBJECT,
    SNAPSHOT_BRANCH, SNAPSHOT_BUILD_CMD, SNAPSHOT_BASE_REF,
    SNAPSHOT_BASE_DIGEST, SNAPSHOT_BASE_REPO_DIGESTS, SNAPSHOT_IMAGE_TAG,
    SNAPSHOT_IMAGE_ID, SNAPSHOT_IMAGE_PLATFORM, SNAPSHOT_HOST_PLATFORM,
    SNAPSHOT_SYSCONF_PLATFORM, SNAPSHOT_DOCKER_VERSION, SNAPSHOT_MANIFEST_NOTE

Outputs (in the mounted directory):
  - installed-packages.txt   human-readable inventory grouped by category
  - manifest.json            extraction metadata (commit, image, versions, ...)

Categories:
  - project:package     the deudamundi-api distribution installed by `pip install .`
  - runtime:direct      packages declared in api/pyproject.toml `[project.dependencies]`
  - runtime:transitive  every other runtime package (with direct ancestors in the active graph)
  - build:tooling       pip / setuptools / wheel (upgraded by the Dockerfile)
"""

import json
import os
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

OUT_DIR = Path(os.environ.get("SNAPSHOT_OUT", "/tmp"))
INSPECT_FILE = OUT_DIR / "pip-inspect.json"
PYPROJECT_FILE = Path(os.environ.get("SNAPSHOT_PYPROJECT", "/app/pyproject.toml"))

# Membership of each category
BUILD_TOOLING = {"pip", "setuptools", "wheel"}


def norm(name: str) -> str:
    """PEP 503-style canonicalization."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def requirement_name(req: str):
    """Return the normalized distribution name of a requirement string."""
    req = req.split(";", 1)[0]          # drop environment marker
    req = re.sub(r"\[[^\]]*\]", "", req)  # drop extras
    match = re.match(r"\s*([A-Za-z0-9._-]+)", req)
    return norm(match.group(1)) if match else None


def requirement_is_active(req: str, requirer: str, extras_installed: dict[str, set[str]]):
    """True when `req` is active for the distribution `requirer` that was
    installed in this environment.

    - `extra == "x"` markers are active only if the requiring distribution was
      actually installed with that extra (extras are resolved from the direct
      requirements in api/pyproject.toml).
    - Other markers (python_version, sys_platform, ...) are conservatively
      treated as active, since this image is a single linux/amd64 CPython
      environment and pip inspect only lists what got installed here.
    """
    marker = req.split(";", 1)[1] if ";" in req else ""
    extra_match = re.search(r'extra\s*==\s*[\'"]([^\'"]+)[\'"]', marker)
    if extra_match:
        return extra_match.group(1) in extras_installed.get(requirer, set())
    return True


def main() -> int:
    inspect_data = json.loads(INSPECT_FILE.read_text())
    installed = []
    for pkg in inspect_data["installed"]:
        meta = pkg["metadata"]
        installed.append(
            {
                "name": meta["name"],
                "norm": norm(meta["name"]),
                "version": meta.get("version", ""),
                "requires": [
                    r for r in (meta.get("requires_dist") or [])
                    if isinstance(r, str)
                ],
            }
        )
    by_name = {p["norm"]: p for p in installed}

    if not PYPROJECT_FILE.is_file():
        print(f"ERROR: {PYPROJECT_FILE} not found; mount the image and keep /app intact", file=sys.stderr)
        return 1
    pyproject = tomllib.loads(Path(PYPROJECT_FILE).read_text())
    project_name = norm(pyproject["project"]["name"])
    declared = [
        d for d in (requirement_name(r) for r in pyproject["project"]["dependencies"]) if d
    ]
    try:
        dev_metadata = [requirement_name(r) for r in pyproject["project"]["optional-dependencies"]["dev"]]
    except KeyError:
        dev_metadata = []
    dev_present = sorted(d for d in (n for n in dev_metadata if n) if d in by_name)

    extras_installed: dict[str, set[str]] = defaultdict(set)
    for req in pyproject["project"]["dependencies"]:
        for extra in re.findall(r"\[([^\]]*)\]", req.split(";", 1)[0]):
            base = requirement_name(req)
            if base:
                extras_installed[base].update(
                    e.strip() for e in extra.split(",") if e.strip()
                )

    # Direct ancestors: which declared runtime packages (or the project package
    # itself) reach each installed package through the active dependency graph.
    roots = [*declared, project_name]
    direct_ancestors: dict[str, set[str]] = defaultdict(set)
    for root in roots:
        seen = set()
        queue = [root]
        while queue:
            current = queue.pop()
            pkg = by_name.get(current)
            if not pkg:
                continue
            for req in pkg["requires"]:
                if not requirement_is_active(req, current, extras_installed):
                    continue
                target = requirement_name(req)
                if not target or target == current or target in seen:
                    continue
                if target in BUILD_TOOLING:
                    continue
                seen.add(target)
                queue.append(target)
                if target in roots:
                    continue  # avoid attributing a root to itself once reached
                direct_ancestors[target].add(root)

    def category_of(name: str) -> str:
        if name == project_name:
            return "project:package"
        if name in BUILD_TOOLING:
            return "build:tooling"
        if name in set(declared):
            return "runtime:direct"
        return "runtime:transitive"

    rows = []
    for pkg in installed:
        cat = category_of(pkg["norm"])
        note = ""
        if cat == "runtime:transitive":
            ancestors = sorted(direct_ancestors.get(pkg["norm"], set()))
            note = f"<- {', '.join(ancestors) if ancestors else '(not reached from declared runtime deps)'}"
        rows.append((cat, pkg["name"], pkg["version"], note))

    order = {"project:package": 0, "runtime:direct": 1, "runtime:transitive": 2, "build:tooling": 3}
    rows.sort(key=lambda r: (order[r[0]], r[1]))

    counts = defaultdict(int)
    for cat, _n, _v, _note in rows:
        counts[cat] += 1

    env = inspect_data.get("environment", {})
    lines = [
        "# Installed Python packages - DeudaMundi backend production image",
        "# Source: `python -m pip inspect` executed in image {host}".format(
            host=os.environ.get("SNAPSHOT_IMAGE_TAG", "<built production image>"),
        ),
        "# Categories:"
        "\n#   project:package     the deudamundi-api distribution itself (`pip install .`)",
        "#   runtime:direct      declared in api/pyproject.toml [project.dependencies]",
        "#   runtime:transitive  resolved at build time by pip (<- direct packages that require it)",
        "#   build:tooling       pip / setuptools / wheel (upgraded by Dockerfile builder)",
        "",
        f"# Python {env.get('python_full_version', '?')} ({env.get('platform_python_implementation', '?')}), "
        f"pip {inspect_data.get('pip_version','?')}, "
        f"platform {env.get('platform_system','?')} {env.get('platform_machine','?')}",
        f"# packages: {len(rows)}"
        f" (project:package={counts['project:package']}"
        f", runtime:direct={counts['runtime:direct']}"
        f", runtime:transitive={counts['runtime:transitive']}"
        f", build:tooling={counts['build:tooling']})",
        "# Note: dev extra (pytest, pytest-cov, ruff, locust) is NOT installed in the production target.",
        "",
        f"# dev-extra metadata present in installed env: "
        + (", ".join(dev_present) if dev_present else "none"),
        "",
    ]
    width_cat = max(len(r[0]) for r in rows)
    width_name = max(len(r[1]) for r in rows)
    width_ver = max((len(r[2]) for r in rows), default=1)
    for cat, name, version, note in rows:
        lines.append(f"[{cat:<{width_cat}}] {name:<{width_name}} {version:<{width_ver}} {note}")
    (OUT_DIR / "installed-packages.txt").write_text("\n".join(lines) + "\n")

    if os.environ.get("SNAPSHOT_WRITES_MANIFEST") == "1":
        manifest = {
            "schema": "deudamundi.research.env-snapshot/1",
            "kind": "environment-snapshot (NOT a reproducible lockfile)",
            "generated_at_utc": os.environ.get("SNAPSHOT_GENERATED_AT", ""),
            "repository": {
                "project": "econopapi/DeudaMundi",
                "component": "api (FastAPI backend)",
                "commit_sha": os.environ.get("SNAPSHOT_COMMIT_SHA", ""),
                "commit_subject": os.environ.get("SNAPSHOT_COMMIT_SUBJECT", ""),
                "commit_date": os.environ.get("SNAPSHOT_COMMIT_DATE", ""),
                "branch": os.environ.get("SNAPSHOT_BRANCH", ""),
            },
            "image": {
                "name": os.environ.get("SNAPSHOT_IMAGE_TAG", ""),
                "id": os.environ.get("SNAPSHOT_IMAGE_ID", ""),
                "platform": os.environ.get("SNAPSHOT_IMAGE_PLATFORM", ""),
                "dockerfile_target": "production",
                "dockerfile": "api/Dockerfile",
                "compose_equivalent": "service api in docker-compose.prod.yml"
                " (build.context: ./api, build.target: production)",
            },
            "base_image": {
                "ref": os.environ.get("SNAPSHOT_BASE_REF", ""),
                "digest": os.environ.get("SNAPSHOT_BASE_DIGEST", ""),
                "local_repo_digests": os.environ.get("SNAPSHOT_BASE_REPO_DIGESTS", ""),
            },
            "build": {
                "command": os.environ.get("SNAPSHOT_BUILD_CMD", ""),
                "docker_version": os.environ.get("SNAPSHOT_DOCKER_VERSION", ""),
            },
            "runtime": {
                "python_version": env.get("python_full_version", ""),
                "python_implementation": env.get("platform_python_implementation", ""),
                "sysconfig_platform": os.environ.get("SNAPSHOT_SYSCONF_PLATFORM", ""),
                "pip_version": inspect_data.get("pip_version", ""),
                "platform_system": env.get("platform_system", ""),
                "platform_machine": env.get("platform_machine", ""),
            },
            "dominant": {
                "packages_total": len(rows),
                "project_package": counts["project:package"],
                "runtime_direct": counts["runtime:direct"],
                "runtime_transitive": counts["runtime:transitive"],
                "build_tooling": counts["build:tooling"],
                "dev_extra_installed": bool(dev_present),
            },
            "artifacts": {
                "pip_inspect_json": "pip-inspect.json",
                "installed_packages_txt": "installed-packages.txt",
                "category_of": "categorize_env.py",
                "reproduce_with": "extract_env_snapshot.sh",
                "checksums": "SHA256SUMS",
            },
            "reproducibility_note": os.environ.get(
                "SNAPSHOT_MANIFEST_NOTE",
                "Snapshot of the resolved environment at a single build; not a guarantee of"
                " bit-identical reconstruction (no pinned wheel digests).",
            ),
        }
        (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
