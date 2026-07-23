# CLAUDE.md — file convention cho Claude Code contributor.
# Dat o root de Claude Code session moi tu doc khi start (chi can 1 lan).
# Noi dung ngan gon (~80 dong), chi chua "must-know" cho AI assistant.
#
# KHONG trung lap README/CHANGELOG/CONTRIBUTING — chi dan den.

# sap-abap-agent — Claude Code Contributor Guide

> File nay duoc Claude Code doc tu dong khi moi session bat dau.
> Noi dung ngan gon, chi chua "must-know". Chi tiet xem `README.md`, `CONTRIBUTING.md`.

## What this repo is

Claude Code plugin + MCP server (Python) cho SAP S/4HANA Cloud Public Edition.

- 28 agents (module consultants + 3 cross-cutting)
- 43 skills (pipelines + reference docs)
- 6 GitHub Actions workflows
- MCP server source: `reference/mcp-server/sap_btp_agent/`

## Truoc khi sua gi

1. **Chay validation**: `python reference/scripts/validate_plugin.py`
   - 10 check (frontmatter, drift, version, syntax, MCP tool count, ...)
   - Phai PASS truoc khi commit.
2. **Chay test**: `python -m pytest tests/ hooks/hook_tests/ --collect-only`
   - 126 tests collected; moi file test moi phai PASS.
3. **Doc CONTRIBUTING.md** (nhat la section "Pre-commit Hook" — co ruff, hooks moi tu v1.12.0).

## Quy tac code

- **KHONG sua logic** cua source trong `reference/mcp-server/sap_btp_agent/` khi khong duoc yeu cau.
- **Moi skill** = 1 file `skills/<name>/SKILL.md`. Co frontmatter (name, description, model).
- **Moi agent** = 1 file `agents/<name>.md`. Co frontmatter (name, description, tools, skills).
- **Hook moi** (PostToolUse, PreToolUse, ...): them vao `hooks/` (Python portable, khong shell).
- **CI**: moi push/PR chay 6 workflow. Check `validate.yml` (chay smoke test moi commit).

## Versioning

- Canonical source: `## [vX.Y.Z] — DATE` header trong `CHANGELOG.md`.
- `reference/scripts/build_index.py` parse version tu CHANGELOG → update `index.html`.
- `build_index.py` cung dem agents (28), skills (43, exclude `sap-user-skills`), CDS views (DDLS released tu `released-objects-index.json`).
- Khi bump version: edit CHANGELOG.md header → push → `version-bump.yml` se bump plugin.json + pyproject.toml.

## Lien ket nhanh

| `REUSE.toml`           | REUSE 3.0 license declaration (per-pattern) |
| File | Muc dich |
|---|---|
| `README.md` | Tong quan plugin, install, su dung |
| `CONTRIBUTING.md` | Workflow contribute, pre-commit, naming |
| `CHANGELOG.md` | Version history |
| `docs/architecture.md` | *(chua co — co the tao neu can)* |
| `docs/audits/` | Audit per-release |
| `hooks/hooks.json` | Claude Code hook schema |
| `.pre-commit-config.yaml` | Hook list |
| `.github/workflows/` | 6 CI workflows |
| `pyproject.toml` (root) | Tool config (ruff, pytest) |
| `reference/mcp-server/pyproject.toml` | MCP server package |
