---
description: Dang ky toan bo MCP servers (13 servers) chi bang 1 lenh — su dung chung lau dai
argument-hint: "[--apply | --json | --skip-env]"
---

# MCP Setup — Dang ky toan bo MCP servers trong 1 lan

## Cach dung

```bash
# Tuong tac: hoi tung server (khuyen dung lan dau)
python reference/scripts/mcp_register.py

# Auto: dung ngay khong hoi (dang ky het nhung gi co the)
python reference/scripts/mcp_register.py --apply

# Chi sinh .mcp.json (de commit vao git, dung chung team)
python reference/scripts/mcp_register.py --json
```

Script se tu dong:
1. Quet inventory (13 servers)
2. Kiem tra server nao da register roi
3. **Core + Remote** (sap-btp, sap-dict-bridge, cds-kb, mcp-sap-docs-btp) → register ngay
4. **ADT alternatives** (arc-1, mcp-abap-adt) → hoi xac nhan + env vars
5. **Product-specific** → huong dan cai dat thu cong
6. Ghi vao `~/.claude.json` (user scope) + `.mcp.json` (project scope)

## Kiem tra

Sau khi register, kiem tra lai bang:

```bash
python reference/scripts/mcp_status.py
```

Khoi dong lai Claude Code de nhan server moi.

## ─── 3 servers co the auto-register ngay ───

```bash
claude mcp add --transport stdio sap-btp -- sap-btp-agent
claude mcp add --transport stdio sap-dict-bridge -- python -m sap_btp_agent.bridge_server
claude mcp add --transport sse cds-kb --url https://cds-kb-mcp-production.up.railway.app/sse
```

## ─── 3 servers ADT alternatives (npx, can Node.js) ───

```bash
claude mcp add --transport stdio arc-1 -- npx -y arc-1@latest
claude mcp add --transport stdio mcp-abap-adt -- npx -y mcp-abap-adt
claude mcp add --transport stdio mcp-abap-adt-dict -- npx -y @mcp-abap-adt/core
```

## ─── 6 servers can cai dat thu cong ───

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
