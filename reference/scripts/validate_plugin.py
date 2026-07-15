#!/usr/bin/env python3
"""Structural + cross-file consistency checks for the sap-abap-agent plugin.

Stdlib-only (no new dependencies). Run before committing:

    python scripts/validate_plugin.py

Exits 1 if any check fails, 0 if all pass.

Checks:
  1. agents/*.md frontmatter: required fields, name == filename
  2. skills: [...] references resolve to a real skills/ or reference/modules/ dir
  3. body text mentioning a `sap-*` skill name not declared in frontmatter skills:
  4. reference/modules/<mod>/SKILL.md CORE size (<=30 lines) when a deep/SKILL.md sibling exists
  5. duplicated consecutive lines/table-rows in tracked *.md files (copy-paste artifacts)
  6. MCP tool count in registry.py vs "N MCP tools" claims in docs
  7. every scripts/*.py and reference/mcp-server/**/*.py parses (py_compile)
  8. every sap-*-consultant-cloud agent is referenced in the routing matrix, and vice versa
  9. index.html hardcoded counts ("N skill implementations", "N module knowledge bases") vs
     actual skills/ and reference/modules/ directory counts on disk
  10. version consistency between .claude-plugin/plugin.json and the newest CHANGELOG.md header
      (2 independent sources that can drift if only one gets bumped)

Only checks facts derivable from this repo's own filesystem — third-party stats quoted in docs
(e.g. a vendored MCP server's own tool count, an external knowledge base's row count) are NOT
verifiable from here and are intentionally left unchecked.
"""
from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FAILURES: list[str] = []
WARNINGS: list[str] = []


def fail(check: str, msg: str) -> None:
    FAILURES.append(f"[{check}] {msg}")


def warn(check: str, msg: str) -> None:
    WARNINGS.append(f"[{check}] {msg}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not m:
        return None
    fm: dict[str, str] = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", lines[i])
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1]
        if not val:
            # Possibly a multi-line YAML list:
            #   key:
            #     - item1
            #     - item2
            items = []
            j = i + 1
            while j < len(lines):
                lm = re.match(r"^\s+-\s+(.*)$", lines[j])
                if not lm:
                    break
                items.append(lm.group(1).strip())
                j += 1
            if items:
                val = "[" + ", ".join(items) + "]"
                i = j - 1
        fm[key] = val
        i += 1
    return fm


def parse_inline_list(val: str) -> list[str]:
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        val = val[1:-1]
    return [x.strip().strip('"').strip("'") for x in val.split(",") if x.strip()]


def skill_exists(name: str) -> bool:
    return (
        (ROOT / "skills" / name / "SKILL.md").exists()
        or (ROOT / "reference" / "modules" / name / "SKILL.md").exists()
        or (ROOT / "reference" / "mcp-guides" / f"{name}.md").exists()
        or (ROOT / "reference" / "process" / f"{name}.md").exists()
    )


def check_agent_frontmatter() -> None:
    agents_dir = ROOT / "agents"
    for path in sorted(agents_dir.glob("*.md")):
        text = read(path)
        fm = parse_frontmatter(text)
        stem = path.stem
        if fm is None:
            fail("frontmatter", f"{path.relative_to(ROOT)}: no --- frontmatter block found")
            continue
        for required in ("name", "description", "model"):
            if required not in fm:
                fail("frontmatter", f"{path.relative_to(ROOT)}: missing '{required}:' field")
        if fm.get("name") and fm["name"] != stem:
            fail(
                "frontmatter",
                f"{path.relative_to(ROOT)}: name: '{fm['name']}' does not match filename '{stem}'",
            )

        declared_skills = parse_inline_list(fm.get("skills", "[]"))
        for skill in declared_skills:
            if not skill_exists(skill):
                fail(
                    "skill-ref",
                    f"{path.relative_to(ROOT)}: declares skills: [{skill}] but no "
                    f"skills/{skill}/SKILL.md or reference/modules/{skill}/SKILL.md exists",
                )

        body = text[len(re.match(r"^---.*?---\r?\n", text, re.DOTALL).group(0)):]
        # Only flag mentions that read like a self-directed instruction ("ap dung ... trong
        # `X`", "theo `X`") — skip mentions like "skill `X`", "dispatch `X`", "`X` ... dispatch
        # sang ..." that are just naming another (downstream/upstream) skill/agent for context,
        # not claiming to use it.
        known_skill_names = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
        known_module_names = {p.name for p in (ROOT / "reference" / "modules").iterdir() if p.is_dir()}
        for m in re.finditer(r"`(sap-[a-z0-9-]+)`", body):
            name = m.group(1)
            if name not in (known_skill_names | known_module_names) or name in declared_skills:
                continue
            preceding = body[max(0, m.start() - 30) : m.start()].lower()
            following = body[m.end() : m.end() + 40].lower()
            if "skill" in preceding or "dispatch" in preceding or "dispatch" in following:
                continue
            if re.search(r"`\s*/\s*$", preceding):
                continue
            warn(
                "skill-drift",
                f"{path.relative_to(ROOT)}: body references `{name}` as if it were loaded, "
                f"but frontmatter skills: {declared_skills} does not include it",
            )


def check_core_deep_size() -> None:
    modules_dir = ROOT / "reference" / "modules"
    limit = 30
    for mod_dir in sorted(p for p in modules_dir.iterdir() if p.is_dir()):
        core = mod_dir / "SKILL.md"
        deep = mod_dir / "deep" / "SKILL.md"
        if not core.exists() or not deep.exists():
            continue
        n_lines = len(read(core).splitlines())
        if n_lines > limit:
            fail(
                "core-size",
                f"{core.relative_to(ROOT)}: {n_lines} lines, exceeds the {limit}-line CORE "
                f"budget documented in reference/process/sap-context-module-routing.md "
                f"(has a deep/SKILL.md sibling, so overflow content belongs there)",
            )


def check_duplicate_lines() -> None:
    md_files = [
        p
        for p in ROOT.rglob("*.md")
        if ".git" not in p.parts
        and "node_modules" not in p.parts
        and "in" not in p.relative_to(ROOT).parts[:1]
        and "out" not in p.relative_to(ROOT).parts[:1]
    ]
    for path in sorted(md_files):
        lines = read(path).splitlines()
        for i in range(len(lines) - 1):
            a, b = lines[i].strip(), lines[i + 1].strip()
            if len(a) >= 40 and a == b:
                fail(
                    "dup-block",
                    f"{path.relative_to(ROOT)}:{i + 1}-{i + 2}: identical consecutive lines "
                    f"(likely copy-paste duplicate): {a[:70]!r}",
                )


def check_tool_count_drift() -> None:
    registry = ROOT / "reference" / "mcp-server" / "sap_btp_agent" / "tools" / "registry.py"
    if not registry.exists():
        warn("tool-drift", "registry.py not found, skipping tool-count check")
        return
    real_count = len(re.findall(r'"name":\s*"sap_', read(registry)))

    doc_patterns = [
        ROOT / ".vscode-extensions" / "sap-btp-mcp" / "README.md",
        ROOT / "reference" / ".vscode-extensions" / "sap-btp-mcp" / "README.md",
        ROOT / "README.md",
    ]
    for doc in doc_patterns:
        if not doc.exists():
            continue
        for m in re.finditer(r"(\d+)\s+MCP tools?", read(doc)):
            claimed = int(m.group(1))
            if claimed != real_count:
                fail(
                    "tool-drift",
                    f"{doc.relative_to(ROOT)}: claims '{claimed} MCP tools' but "
                    f"registry.py currently registers {real_count}",
                )


def check_python_syntax() -> None:
    py_files = list((ROOT / "reference" / "scripts").glob("*.py"))
    mcp_server = ROOT / "reference" / "mcp-server"
    if mcp_server.exists():
        py_files += [
            p
            for p in mcp_server.rglob("*.py")
            if "__pycache__" not in p.parts
        ]
    for path in sorted(py_files):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as e:
            fail("py-syntax", f"{path.relative_to(ROOT)}: {e.msg.strip()}")


def check_routing_matrix_coverage() -> None:
    routing_file = ROOT / "skills" / "sap-ask-consultant" / "SKILL.md"
    if not routing_file.exists():
        warn("routing", "skills/sap-ask-consultant/SKILL.md not found, skipping")
        return
    text = read(routing_file)
    referenced = set(re.findall(r"`(sap-[a-z0-9-]+-consultant-cloud)`", text))

    agent_files = {
        p.stem
        for p in (ROOT / "agents").glob("sap-*-consultant-cloud.md")
    }

    missing_agent_file = referenced - agent_files
    for name in sorted(missing_agent_file):
        fail(
            "routing",
            f"skills/sap-ask-consultant/SKILL.md references `{name}` but "
            f"agents/{name}.md does not exist",
        )

    orphaned_agents = agent_files - referenced
    for name in sorted(orphaned_agents):
        warn(
            "routing",
            f"agents/{name}.md exists but is never mentioned in "
            f"skills/sap-ask-consultant/SKILL.md's routing matrix",
        )


def _real_skill_count() -> int:
    skills_dir = ROOT / "skills"
    count = len([p for p in skills_dir.iterdir() if p.is_dir()])
    if (skills_dir / "sap-user-skills").is_dir():
        count -= 1  # empty placeholder, excluded by convention (see .github/workflows/version-bump.yml)
    return count


def _real_module_count() -> int:
    modules_dir = ROOT / "reference" / "modules"
    return len([p for p in modules_dir.iterdir() if p.is_dir()])


def check_index_html_counts() -> None:
    index_html = ROOT / "index.html"
    if not index_html.exists():
        warn("doc-drift", "index.html not found, skipping count check")
        return
    text = read(index_html)
    real_skills = _real_skill_count()
    real_modules = _real_module_count()

    for m in re.finditer(r"(\d+)\s+skill implementations", text):
        claimed = int(m.group(1))
        if claimed != real_skills:
            fail(
                "doc-drift",
                f"index.html claims '{claimed} skill implementations' but skills/ currently "
                f"has {real_skills} (excluding the sap-user-skills placeholder)",
            )

    for m in re.finditer(r"(\d+)\s+module knowledge bases", text):
        claimed = int(m.group(1))
        if claimed != real_modules:
            fail(
                "doc-drift",
                f"index.html claims '{claimed} module knowledge bases' but "
                f"reference/modules/ currently has {real_modules}",
            )


def check_version_consistency() -> None:
    plugin_json = ROOT / ".claude-plugin" / "plugin.json"
    changelog = ROOT / "CHANGELOG.md"
    if not plugin_json.exists() or not changelog.exists():
        warn("version-drift", "plugin.json or CHANGELOG.md not found, skipping version check")
        return
    m = re.search(r'"version"\s*:\s*"([^"]+)"', read(plugin_json))
    if not m:
        warn("version-drift", "could not find \"version\" field in plugin.json")
        return
    plugin_version = m.group(1)

    m = re.search(r"^##\s+\[v?([0-9]+\.[0-9]+\.[0-9]+)\]", read(changelog), re.MULTILINE)
    if not m:
        warn("version-drift", "could not find a '## [vX.Y.Z]' header in CHANGELOG.md")
        return
    changelog_version = m.group(1)

    if plugin_version != changelog_version:
        warn(
            "version-drift",
            f".claude-plugin/plugin.json version '{plugin_version}' does not match the newest "
            f"CHANGELOG.md entry 'v{changelog_version}' — these are 2 independent sources "
            f"(plugin.json is auto-bumped by CI on push, CHANGELOG.md is hand-written); a mismatch "
            f"just means CI hasn't caught up yet, not necessarily a real error (warn, not fail)",
        )


def main() -> int:
    check_agent_frontmatter()
    check_core_deep_size()
    check_duplicate_lines()
    check_tool_count_drift()
    check_python_syntax()
    check_routing_matrix_coverage()
    check_index_html_counts()
    check_version_consistency()

    if WARNINGS:
        print(f"--- {len(WARNINGS)} warning(s) ---")
        for w in WARNINGS:
            print(f"  WARN  {w}")
        print()

    if FAILURES:
        print(f"--- {len(FAILURES)} failure(s) ---")
        for f in FAILURES:
            print(f"  FAIL  {f}")
        print(f"\nvalidate_plugin.py: {len(FAILURES)} failure(s), {len(WARNINGS)} warning(s)")
        return 1

    print(f"validate_plugin.py: all checks passed ({len(WARNINGS)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
