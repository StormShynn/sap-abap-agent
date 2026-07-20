#!/usr/bin/env python3
"""Sync version + counts vao `index.html` (thay the `sed -i` trong sync-index.yml).

Workflow CI (GitHub Actions) goi script nay thay vi chay `sed` truc tiep:
    python reference/scripts/build_index.py

Doc:
  - `CHANGELOG.md` (header `## [vX.Y.Z]`)            -> version
  - `agents/*.md` (file count)                       -> agent count
  - `skills/*/SKILL.md` (dir count, exclude placeholder) -> skill count
  - `docs/sap-knowledge/released-objects-index.json` -> CDS view count (DDLS released)

Sau do update `index.html` (in-place) theo cac pattern giong workflow cu:
  - `vX.Y.Z \u00b7 N agents \u00b7 M skills`
  - `vX.Y.Z \u00b7 N modules \u00b7 M skills`
  - `vX.Y.Z \u00b7 N modules + M skills`
  - `N,NNN CDS views`        (number_format: 7,355)

Thoat 0 neu khong co gi thay doi, 1 neu co loi parse. Khong pha logic - chi
chuyen `sed` shell pipeline thanh Python portable (chay duoc tren Windows).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
INDEX_HTML = REPO_ROOT / "index.html"
CDS_INDEX = REPO_ROOT / "docs" / "sap-knowledge" / "released-objects-index.json"

# Header `## [v1.12.0] - 2026-07-18` hoac `## [1.12.0]` (khong co 'v'),
# hoac em-dash `## [v1.11.0] \u2014 2026-07-16`.
_VERSION_RE = re.compile(r"^##\s*\[v?(\d+\.\d+(?:\.\d+)?)\]")

# Pattern sidebar/footer trong index.html (giong regex `sed -i` cua workflow).
# Moi pattern match 1 placeholder `vX.Y.Z ... counts` -> replace bang version moi.
_SIDEBAR_PATTERNS = [
    # vX.Y.Z \u00b7 N agents \u00b7 M skills   (format chinh)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+agents\s*\u00b7\s*\d+\s+skills"),
    # vX.Y.Z \u00b7 N modules \u00b7 M skills   (fallback)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+modules\s*\u00b7\s*\d+\s+skills"),
    # vX.Y.Z \u00b7 N modules + M skills   (fallback)
    re.compile(r"v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+modules\s*\+\s*\d+\s+skills"),
    # <small>vX.Y.Z \u00b7 N agents \u00b7 M skills</small> (HTML wrap)
    re.compile(r"(<small>)v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+agents\s*\u00b7\s*\d+\s+skills(</small>)"),
    # <span class="header-version">vX.Y.Z \u00b7 N agents \u00b7 M skills</span>
    re.compile(r"(class=\"header-version\">)v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+agents\s*\u00b7\s*\d+\s+skills"),
    # Plain text: SAP ABAP Agent &middot; vX.Y.Z \u00b7 N agents \u00b7 M skills
    re.compile(r"((?:&middot;)\s+)v\d+\.\d+(?:\.\d+)?\s*\u00b7\s*\d+\s+agents\s*\u00b7\s*\d+\s+skills"),
]

# Pattern cho CDS view count trong index.html.
# Dung 1 regex duy nhat (khong lien tiep) de tranh khop loi 7,7,355.
# Group 1: so thap phan co dau phay (7,355) HOAC so nguyen (7355).
_CDS_PATTERN = re.compile(
    r"(\d{1,3}(?:,\d{3})+|\d+)\s+CDS\s+views"
)


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


def count_cds_views() -> int | None:
    """Dem CDS view (DDLS released) tu `released-objects-index.json`.

    Object key co format `TYPE:NAME` (vi du `DDLS:ZTEST_NOTE`). Dem nhung
    entry bat dau bang `DDLS:` va co state = 'released'.

    Tra ve None neu file khong ton tai / parse loi (de skip update).
    """
    if not CDS_INDEX.is_file():
        return None
    try:
        data = json.loads(CDS_INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    objs = data.get("objects")
    if not isinstance(objs, dict):
        return None
    count = 0
    for key, value in objs.items():
        if not isinstance(key, str) or not key.startswith("DDLS:"):
            continue
        if not isinstance(value, dict):
            continue
        if value.get("state") == "released":
            count += 1
    return count


def _format_number_with_thousands(n: int) -> str:
    """Format so 7355 -> '7,355' (locale-independent, ASCII comma)."""
    return f"{n:,}"


def update_index_html(
    version: str,
    agent_count: int,
    skill_count: int,
    cds_count: int | None,
) -> bool:
    """Ap dung cac pattern regex len `index.html`. Tra ve True neu co thay doi.

    Moi pattern chi replace 1 lan (count=1) de tranh bug "7,7,355" khi placeholder
    da duoc sua boi lan truoc.
    """
    if not INDEX_HTML.is_file():
        print(f"WARNING: {INDEX_HTML} not found - skipped", file=sys.stderr)
        return False
    text = INDEX_HTML.read_text(encoding="utf-8")
    new_text = text

    # Sidebar / footer (version + counts)
    # 3 pattern don gian (replace toan bo match = new_line)
    # 3 pattern co HTML wrap (su dung capture groups de giu lai tags)
    new_line = f"v{version} \u00b7 {agent_count} agents \u00b7 {skill_count} skills"

    # Patterns with capture groups (keep HTML intact)
    # Moi pattern wrap co 1 hoac 2 capture groups (prefix va optional suffix).
    # Re.sub callback xu ly ca 2 truong hop.
    wrap_patterns = _SIDEBAR_PATTERNS[3:]  # <small>, header-version, &middot;
    for pat in wrap_patterns:
        def _sub_wrap(m):
            prefix = m.group(1) if m.lastindex and m.lastindex >= 1 else ""
            suffix = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
            return f"{prefix}{new_line}{suffix}"
        new_text = pat.sub(_sub_wrap, new_text, count=1)

    # Simple patterns (no HTML wrap)
    simple_patterns = _SIDEBAR_PATTERNS[:3]
    for pat in simple_patterns:
        new_text = pat.sub(new_line, new_text, count=1)

    # CDS view count (chi update neu detect duoc) - match tat ca occurrence nhung
    # chi 1 lan moi pattern, voi pattern duy nhat tranh re-sub noi tieng.
    if cds_count is not None:
        cds_str = f"{_format_number_with_thousands(cds_count)} CDS views"
        # Dung sub voi count=0 (all) nhung pattern chi khop 1 dang (comma-or-not) moi lan
        # de tranh cap so bi noi vao nhau.
        new_text = _CDS_PATTERN.sub(cds_str, new_text)

    if new_text == text:
        print(f"No changes to {INDEX_HTML.name}")
        return False
    INDEX_HTML.write_text(new_text, encoding="utf-8")
    print(
        f"Updated {INDEX_HTML.name}: version=v{version} "
        f"agents={agent_count} skills={skill_count} cds={cds_count}"
    )
    return True


def main() -> int:
    version = read_changelog_version()
    if not version:
        print(f"ERROR: cannot find version header in {CHANGELOG}", file=sys.stderr)
        return 1
    agents = count_agents()
    skills = count_skills()
    cds = count_cds_views()
    print(f"version=v{version} agents={agents} skills={skills} cds={cds}")
    update_index_html(version, agents, skills, cds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
