#!/usr/bin/env python3
"""Sync version + counts vao `index.html` (thay the `sed -i` trong sync-index.yml).

Workflow CI (GitHub Actions) goi script nay thay vi chay `sed` truc tiep:
    python reference/scripts/build_index.py

Doc:
  - `CHANGELOG.md` (header `## [vX.Y.Z]`)  -> version
  - `agents/*.md` (file count)             -> agent count
  - `skills/*/SKILL.md` (dir count, exclude `sap-user-skills`) -> skill count

Sau do update `index.html` (in-place) theo cac pattern giong workflow cu:
  - `vX.Y.Z \u00b7 N agents \u00b7 M skills`
  - `vX.Y.Z \u00b7 N modules \u00b7 M skills`
  - `vX.Y.Z \u00b7 N modules + M skills`

Thoat 0 neu khong co gi thay doi, 1 neu co loi parse. Khong pha logic - chi
chuyen `sed` shell pipeline thanh Python portable (chay duoc tren Windows).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
INDEX_HTML = REPO_ROOT / "index.html"

# Header `## [v1.12.0] - 2026-07-18` hoac `## [1.12.0]` (khong co 'v').
_VERSION_RE = re.compile(r"^##\s*\[v?(\d+\.\d+(?:\.\d+)?)\]")

# Pattern sidebar/footer trong index.html (giong regex `sed -i` cua workflow).
# Moi pattern match 1 placeholder `vX.Y.Z ... counts` -> replace bang version moi.
_SIDEBAR_PATTERNS = [
    # vX.Y.Z · N agents · M skills   (format chinh)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+agents\s*\u00b7\s*\d+\s+skills"),
    # vX.Y.Z · N modules · M skills   (fallback)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+modules\s*\u00b7\s*\d+\s+skills"),
    # vX.Y.Z · N modules + M skills   (fallback)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+modules\s*\+\s*\d+\s+skills"),
]


def read_changelog_version() -> str | None:
    """Doc header CHANGELOG.md, tra ve `X.Y.Z` (khong co 'v'). None neu khong thay."""
    if not CHANGELOG.is_file():
        return None
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = _VERSION_RE.match(line.strip())
        if m:
            return m.group(1)
    return None


def count_agents() -> int:
    """Dem file `agents/*.md` (tuong duong `ls -1 agents/*.md | wc -l`)."""
    agents_dir = REPO_ROOT / "agents"
    if not agents_dir.is_dir():
        return 0
    return sum(1 for p in agents_dir.glob("*.md") if p.is_file())


def count_skills() -> int:
    """Dem thu muc `skills/*/` tru `sap-user-skills/` (placeholder, giong workflow cu)."""
    skills_dir = REPO_ROOT / "skills"
    if not skills_dir.is_dir():
        return 0
    total = sum(1 for p in skills_dir.iterdir() if p.is_dir())
    # Tru placeholder (giong rule PLACEHOLDER=1 neu co `skills/sap-user-skills`).
    if (skills_dir / "sap-user-skills").is_dir():
        total -= 1
    return max(total, 0)


def update_index_html(version: str, agent_count: int, skill_count: int) -> bool:
    """Ap dung 3 pattern regex len `index.html`. Tra ve True neu co thay doi."""
    if not INDEX_HTML.is_file():
        print(f"WARNING: {INDEX_HTML} not found - skipped", file=sys.stderr)
        return False
    text = INDEX_HTML.read_text(encoding="utf-8")
    new_line = f"v{version} \u00b7 {agent_count} agents \u00b7 {skill_count} skills"
    new_text = text
    for pat in _SIDEBAR_PATTERNS:
        new_text = pat.sub(new_line, new_text)
    if new_text == text:
        print(f"No changes to {INDEX_HTML.name}")
        return False
    INDEX_HTML.write_text(new_text, encoding="utf-8")
    print(
        f"Updated {INDEX_HTML.name}: version=v{version} "
        f"agents={agent_count} skills={skill_count}"
    )
    return True


def main() -> int:
    version = read_changelog_version()
    if not version:
        print(f"ERROR: cannot find version header in {CHANGELOG}", file=sys.stderr)
        return 1
    agents = count_agents()
    skills = count_skills()
    print(f"version=v{version} agents={agents} skills={skills}")
    update_index_html(version, agents, skills)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
