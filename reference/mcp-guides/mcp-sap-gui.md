# mcp-sap-gui — SAP GUI Automation MCP Server

**Dung o dau**: agent `sap-docs-researcher` (khai bao `skills: [..., mcp-sap-gui, ...]`) —
doc file nay khi user can cai dat/dung SAP GUI Scripting automation qua MCP.

## Tong quan

`mcp-sap-gui` (kts982) cho phep AI assistant dieu khien **SAP GUI for Windows** qua MCP, su dung
**SAP GUI Scripting COM API**. Ho tro: mo transaction, doc/ghi field, thao tac bang (ALV, Grid,
Tree), screenshots, va nhieu tinh nang bao mat.

**Repository**: `https://github.com/kts982/mcp-sap-gui`

**Yeu cau**: Windows + SAP GUI installed + SAP GUI Scripting enabled.

## Cai dat

### Yeu cau he thong

- **OS**: Windows (SAP GUI Scripting COM API chi chay tren Windows)
- **SAP GUI**: SAP GUI for Windows 7.70+ (da cai)
- **SAP GUI Scripting**: Enabled (xem phan Cau hinh ben duoi)
- **Python**: >= 3.10 (neu dung pip)
- **uvx**: (recommended) `pip install uvx`

### Buoc 1: Cai dat

#### Cach 1: uvx (nhanh nhat, khuyen dung)

```bash
# Cai dat uvx neu chua co
pip install uvx

# Cai dat mcp-sap-gui (kem screenshot support)
uvx mcp-sap-gui[screenshots]
```

#### Cach 2: Tu source

```bash
git clone https://github.com/kts982/mcp-sap-gui.git
cd mcp-sap-gui
uv sync --extra screenshots
```

### Buoc 2: Cau hinh .env

Tao file `.env` trong thu muc project:

```env
SAP_USER=your_username
SAP_PASSWD=your_password
SAP_CLIENT=100
SAP_LANG=EN
SAP_ASHOST=sap.router.company.com
SAP_SYSNR=00
```

### Buoc 3: Cau hinh trong MCP client

#### Claude Code (.mcp.json)

```json
{
  "mcpServers": {
    "sap-gui": {
      "command": "uvx",
      "args": [
        "mcp-sap-gui[screenshots]",
        "--read-only",
        "--allowed-transactions",
        "MM03 VA03 IW33"
      ]
    }
  }
}
```

**Security flags**:

| Flag | Mo ta |
|------|-------|
| `--read-only` | Chi doc, khong cho phep ghi/sua |
| `--allowed-transactions` | Whitelist transaction duoc phep (VD: MM03, VA03) |
| `--profile` | `exploration` / `operator` / `full`: so luong tools xuat hien |
| `--audit-log` | Ghi log JSONL vao file de audit |

## Tools (57 tools)

### Connection
- `sap_connect` — Ket noi SAP GUI
- `sap_connect_existing` — Ket noi vao session co san
- `sap_set_policy_profile` — Set policy

### Navigation
- `sap_run_transaction` — Mo transaction (/nMM03)
- `sap_go_back` — Quay lai (/n)
- `sap_end_transaction` — Ket thuc transaction (/ns000)

### Fields & UI
- `sap_read_field` — Doc gia tri field
- `sap_write_field` — Ghi gia tri field
- `sap_press_button` — Nhan button
- `sap_select_combobox` — Chon combo box value
- `sap_set_textedit` — Set text editor

### Tables & Grids
- `sap_read_table` — Doc toan bo ALV/Grid table
- `sap_get_table_info` — Lay metadata cua table
- `sap_select_table_row` — Chon row trong table
- `sap_get_grid_cell` — Doc 1 cell cu the

### Tree
- `sap_get_tree` — Doc tree structure
- `sap_select_tree_node` — Chon node trong tree

### Screenshot
- `sap_take_screenshot` — Chup man hinh (can extra `[screenshots]`)
- `sap_get_screen_info` — Lay thong tin man hinh hien tai

## Cau hinh SAP GUI Scripting

### Tren SAP Server (Basis admin)

```bash
# RZ11 -> sapgui/user_scripting -> TRUE
# RZ11 -> sapgui/user_scripting_per_user -> TRUE (khuyen dung, chi user duoc cap quyen)
```

### Tren SAP GUI Client

```
SAP GUI -> Options -> Scripting:
  ☑ Enable scripting
  ☑ Notify when a script attaches to SAP GUI
  ☑ Attach automatically (khong can confirm)

SAP GUI -> Security -> Security Settings:
  ☑ Allow scripting (hoac chon "Custom" va them trust file)
```

## Security & Best Practices

| Tinh nang | Mo ta |
|-----------|-------|
| **Transaction blocklist** | Transaction nguy hiem (SU01, SE16N, STMS) bi chan mac dinh |
| **Read-only mode** | `--read-only` chan toan bo ghi/sua |
| **Transaction whitelist** | Chi cho phep transaction duoc explicit khai bao |
| **Audit log** | Ghi lai TOAN BO tool call vao JSONL file |
| **Safe credential** | Credentials doc tu .env, khong log/dua vao tool params |

## Vi du su dung trong Claude

```text
"Lay danh sach material tu SAP GUI"
  → sap_connect + sap_run_transaction("MM03") + sap_read_table

"Kiem tra thong tin sales order tren SAP GUI"
  → sap_connect + sap_run_transaction("VA03") + sap_read_field("VBAK-VBELN")
```

## Nguon tham khao

- Repository: `https://github.com/kts982/mcp-sap-gui`
- SAP Note 983990: SAP GUI Scripting security
- SAP Note 692245: Scripting API reference
