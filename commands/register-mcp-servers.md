---
description: |
  Dang ky / cai MCP servers vao Claude Code (Core + remote + ADT tuy chon) —
  1 lenh thay cho viec go `claude mcp add` tung cai. KHONG phai slash /mcp
  (lenh Claude Code de dang nhap OAuth Notion…).
argument-hint: "[--apply | --json | --skip-env]"
---

# /register-mcp-servers — Dang ky MCP servers (1 lan)

> **Ten cu:** `/mcp-setup` (da doi ten de khong lan voi `/mcp` cua Claude Code).

Danh sach day du (ten, category, transport, env): `reference/scripts/mcp_inventory.json`
(hien **15 servers** — doi inventory khi them/bot server, khong hardcode so o day).

## Khac `/mcp` (Claude Code) nhu the nao?

| Lenh | Ai so huu | Lam gi |
|------|-----------|--------|
| `/mcp` | Claude Code | Mo bang MCP + **dang nhap OAuth** (vd Notion) |
| `/register-mcp-servers` | Plugin SAP ABAP Agent | **Dang ky** server Core/remote/ADT vao config |

## Cach dung

Trong Claude Code:

```text
/register-mcp-servers
```

Hoac tuong duong CLI / script:

```bash
# Tuong tac: hoi tung server (khuyen dung lan dau)
python reference/scripts/mcp_register.py

# Auto: dung ngay khong hoi (dang ky het nhung gi co the)
python reference/scripts/mcp_register.py --apply

# Chi sinh .mcp.json (de commit vao git, dung chung team)
python reference/scripts/mcp_register.py --json

# CLI (ten moi + alias cu)
mcp-sap-connect register-mcp-servers
mcp-sap-connect mcp-setup
```

Script se tu dong:
1. Quet inventory (`mcp_inventory.json` — 15 servers)
2. Kiem tra server nao da register roi
3. **Core + Remote** (sap-btp, sap-dict-bridge, cds-kb, mcp-sap-docs-btp, notion) → register ngay
4. **ADT alternatives** (arc-1, mcp-abap-adt, …) → hoi xac nhan + env vars
5. **Product-specific / dev-tool** → huong dan cai dat thu cong (hoac prompt Y/n)
6. Ghi vao `~/.claude.json` (user scope) + `.mcp.json` (project scope)

## Kiem tra

Sau khi register:

```bash
python reference/scripts/mcp_status.py
# hoac skill /sap-mcp-status
```

Khoi dong lai Claude Code de nhan server moi. Neu can OAuth Notion: dung **`/mcp`** (Claude Code), khong dung lenh nay.

## ─── Servers co the auto-register ngay ───

```bash
claude mcp add --transport stdio sap-btp -- mcp-sap-connect
claude mcp add --transport stdio sap-dict-bridge -- python -m mcp_sap_connect.bridge_server
claude mcp add --transport sse cds-kb --url https://cds-kb-mcp-kit-production.up.railway.app/sse
```

## ─── ADT alternatives (npx, can Node.js) ───

```bash
claude mcp add --transport stdio arc-1 -- npx -y arc-1@latest
claude mcp add --transport stdio mcp-abap-adt -- npx -y mcp-abap-adt
claude mcp add --transport stdio mcp-abap-adt-dict -- npx -y @mcp-abap-adt/core
```

## ─── Servers can cai dat thu cong ───

### sap-notes
```bash
git clone https://github.com/marianfoo/sap-mcp-servers.git
cd sap-mcp-servers/packages/notes
npm install && npm run build
claude mcp add --transport stdio sap-notes -- node /abs/path/to/dist/mcp-server.js
```

### sap-gui (Windows + SAP GUI)
```bash
pip install uvx
claude mcp add --transport stdio sap-gui -- uvx mcp-sap-gui[screenshots] --read-only
```

### sf-mcp (SuccessFactors)
```bash
git clone https://github.com/aiadiguru2025/sf-mcp.git
cd sf-mcp && uv sync
claude mcp add --transport stdio sf-mcp -- uv --directory /path/to/sf-mcp run main.py
```

### CData servers (sf-cdata, sap-concur, sap-fieldglass)
Can JDBC license tu CData. Xem skill doc huong dan chi tiet.
