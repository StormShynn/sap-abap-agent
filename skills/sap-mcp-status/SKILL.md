---
name: sap-mcp-status
description: |
  Doi chieu danh sach MCP server ma cac skill/README cua plugin nay co nhac toi
  (sap-btp, sap-dict-bridge, arc-1, mcp-abap-adt, cds-kb, mcp-sap-docs-btp,
  sap-notes, sap-gui, sf-mcp, sf-cdata, sap-concur, sap-fieldglass...) voi
  nhung gi THUC SU dang duoc dang ky trong Claude Code (user/local/project
  scope) cho project hien tai. Chi doc - khong sua `.claude.json`/`.mcp.json`,
  khong chay `claude mcp add/remove`, khong bao gio in gia tri secret (chi
  bao ten field bi thieu).
  Dung khi user hoi "MCP nao dang bat/tat", "kiem tra tinh trang MCP server",
  "co MCP nao cau hinh sai khong", "liet ke MCP server dang dung cho project
  nay", hoac muon 1 buc tranh tong quan truoc khi them/xoa server thu cong.
when_to_use: |
  "kiem tra MCP server", "MCP nao dang chay", "audit MCP config",
  "co MCP server nao bi sai cau hinh khong", "liet ke MCP dang dung".
argument-hint: "(khong can tham so - chay tren project hien tai)"
model: haiku
effort: low
tools: [Bash, Read]
---

# SAP MCP Status — Doi chieu MCP server (read-only)

## Khi nao dung

- User muon biet MCP server nao (trong so nhung cai plugin nay co doc) dang
  thuc su duoc dang ky, o scope nao (user/local/project), va co bi cau hinh
  sai khong (vd thieu `"type"` cho server dung `"url"`, thieu env var mong
  doi nhu `ADT_USER`).
- User dang lung tung giua nhieu skill deu co doan `claude mcp add ...`
  rieng, muon 1 bang tong hop thay vi doc tung skill.
- Truoc khi quyet dinh xoa/them 1 MCP server thu cong - chay skill nay truoc
  de biet chac hien trang.

## Cach chay

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_status.py"
```

Script tu doc:
- `~/.claude.json` -> `mcpServers` (user scope) va `projects[<project nay>].mcpServers` (local scope)
- `<project-root>/.mcp.json` (project scope) + trang thai approve/reject tuong ung

roi doi chieu voi `reference/scripts/mcp_inventory.json` (danh sach server da
biet, tu cac skill/README trong plugin nay).

## Doc ket qua

| Ky hieu | Y nghia |
|---|---|
| `OK` | Dang ky dung, khong thay van de cau truc |
| `WARN` | Dang ky nhung thieu `"type"` (se bi Claude Code bo qua) hoac thieu env var mong doi |
| `-` (not registered) | Chua dang ky - **binh thuong** neu server do khong lien quan (vd sf-mcp khi khong dung SuccessFactors), KHONG tu dong bao la loi |
| `?` (unknown) | Dang ky that nhung khong nam trong `mcp_inventory.json` - can nguoi dung tu xac nhan con dung khong, script khong tu ket luan |

## Gioi han da biet (khong phai loi cua script)

- **MCP server do 1 plugin khac cung cap** (vd `hana-cli` tu plugin
  `sap-hana-cli`) - vong doi gan voi `claude plugin enable/disable`, khong
  nam trong `.claude.json`/`.mcp.json` nen script nay khong thay. Dung
  `claude plugin list` / `claude mcp list` de kiem tra rieng.
- **Server do VS Code extension tu dang ky luc runtime** (vd extension
  `reference/.vscode-extensions/sap-btp-mcp/`) - dang ky truc tiep vao
  process VS Code, khong ghi ra file config tinh nao de doc duoc. Kiem tra
  qua VS Code Chat: go `@mcp`.

## Cap nhat inventory

Khi 1 skill moi bat dau (hoac ngung) doc huong dan `claude mcp add ...`, sua
`reference/scripts/mcp_inventory.json` tuong ung (them/xoa 1 entry) — khong
sua logic trong `mcp_status.py`.
