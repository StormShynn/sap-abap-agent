# SAP ABAP Agent (tieng Viet)

Plugin Claude Code + MCP server tu dong ket noi **SAP BTP / S/4HANA Cloud** de thao tac
ABAP (doc / tim / syntax-check / activate). Ho tro **multi-profile** -- moi project SAP
co profile rieng (URL, tenant, secret), luu trong **folder user** tren may
(`%USERPROFILE%\.sap-btp-agent\` Windows, `~/.sap-btp-agent/` macOS/Linux).

## Noi bat

- **Them project SAP moi chi bang 1 lenh**: `sap-btp-agent setup https://project1.s4hana.cloud.sap`
- **Multi-profile**: chuyen qua lai giua cac project SAP trong cung 1 phien Claude
- **Tu dong refresh token** khi OAuth2 het han
- **Secret duoc ma hoa** (DPAPI tren Windows, AES-256-GCM cho macOS/Linux)

## Cau truc

```text
sap-abap-agent/
+-- .claude-plugin/        # Manifest plugin Claude Code
+-- commands/              # /abap-scaffold, /sap-connect
+-- skills/                # abap-code-review, sap-btp-setup
+-- agents/                # abap-reviewer
+-- hooks/                 # Canh bao SELECT *
+-- reference/             # Tai lieu ABAP
+-- mcp-server/            # MCP server Node.js (multi-profile)
    +-- src/
    |   +-- config/        # paths, profile (registry), store, secrets
    |   +-- sap/           # auth (OAuth2), client (REST + auto-reconnect)
    |   +-- tools/         # registry cac tool MCP (co tham so `profile`)
    |   +-- cli/           # wizard setup + quan ly profile
    |   +-- server.js      # entry MCP server (stdio)
    +-- test/smoke.js
    +-- package.json
```

## Cai dat (1 lan)

Yeu cau: **Node.js >= 18**.

```bash
cd mcp-server
npm install
npm link
```

Sau buoc `npm link` ban se co lenh `sap-btp-agent` trong PATH.

## Them project SAP moi

Cach nhanh nhat -- truyen URL truc tiep:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Wizard se tu sinh profile id tu hostname (`project1.s4hana.cloud.sap`) va hoi:

- OAuth2 `client_id` + `client_secret` (hoac `username/password`, hoac bearer token)
- Region, service type

Thong tin duoc luu rieng trong `profiles/<id>/`:

```
%USERPROFILE%\.sap-btp-agent\profiles\project1.s4hana.cloud.sap\
+-- config.json     <- URL, tenant, client_id, region, service (khong nhay cam)
+-- secrets.json    <- client_secret / token (DA MA HOA)
```

**Them project thu 2, 3...** cung de:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Moi project se co profile rieng, secret rieng (ma hoa doc lap).

## Quan ly nhieu profile

```bash
sap-btp-agent profiles list             # liet ke profile (* = active)
sap-btp-agent profiles use project1     # chon profile active
sap-btp-agent profiles show             # xem chi tiet profile active
sap-btp-agent profiles remove project2  # xoa 1 profile
sap-btp-agent reset                     # xoa TAT CA (can than!)
```

## Kiem tra ket noi

```bash
sap-btp-agent connect                            # test profile active
sap-btp-agent connect project1.s4hana.cloud.sap  # test 1 profile cu the
```

## Dang ky MCP voi Claude Code

`~/.claude/mcp_servers.json` (Windows: `%USERPROFILE%\.claude\mcp_servers.json`):

```json
{
  "mcpServers": {
    "sap-btp": {
      "command": "sap-btp-agent",
      "args": []
    }
  }
}
```

Mo Claude Code voi plugin, cac tool sau se xuat hien:

| Tool                  | Mo ta                                                       |
|-----------------------|-------------------------------------------------------------|
| `sap_list_profiles`   | Liet ke cac profile da cau hinh                             |
| `sap_ping`            | Test ket noi profile (co tham so `profile`)                 |
| `sap_list_packages`   | Liet ke package ABAP                                        |
| `sap_search`          | Tim object ABAP theo ten                                    |
| `sap_read_source`     | Doc source code (class, program, include...)                |
| `sap_syntax_check`    | Syntax check (khong activate)                               |
| `sap_activate`        | Activate object (transport local)                           |

Moi tool deu co tham so `profile` (de trong = profile active). Vi du:

```
"Liet ke cac package trong project project1"
-> Claude goi sap_list_packages({ profile: "project1.s4hana.cloud.sap" })

"Tim class ZCL_* trong project dang dung"
-> Claude goi sap_search({ query: "ZCL_" })
```

## Chay nhieu instance cung luc (1 profile / instance)

Dat env `SAP_BTP_PROFILE=<id>` truoc moi lan chay:

```bash
# Terminal 1: Claude 1 voi profile A
SAP_BTP_PROFILE=project1.s4hana.cloud.sap sap-btp-agent

# Terminal 2: Claude 2 voi profile B
SAP_BTP_PROFILE=project1.s4hana.cloud.sap sap-btp-agent
```

## Cau hinh folder

```
%USERPROFILE%\.sap-btp-agent\   (Windows)
~/.sap-btp-agent/               (macOS/Linux)
+-- profiles.json                <- registry (danh sach + active)
+-- profiles/
|   +-- <profile-id>/            <- 1 folder / project SAP
|       +-- config.json
|       +-- secrets.json         <- MA HOA
+-- log/
+-- cache/
```

- **Windows**: secrets ma hoa bang **DPAPI** qua PowerShell (gan voi tai khoan Windows).
- **macOS/Linux**: **AES-256-GCM**, key derive tu `hostname + username`.
- File mode `0o600`, chi owner doc/ghi.

## Env

- `SAP_BTP_PROFILE=<id>` -- khoa profile cho 1 lan chay (uu tien registry)
- `SAP_BTP_AGENT_HOME=/path` -- doi folder cau hinh (test, multi-tenant)

## Test local

```bash
cd ..
claude --plugin-dir ./sap-abap-agent
```

Trong Claude:
- "Setup SAP BTP cho project https://project1.s4hana.cloud.sap" -> goi wizard
- "Liet ke cac profile SAP cua toi" -> goi `sap_list_profiles`
- "Tim class bat dau bang ZCL_ trong project project1" -> goi `sap_search` voi `profile="project1..."`

## Loi thuong gap

| Loi                                 | Cach sua                                                  |
|-------------------------------------|-----------------------------------------------------------|
| `401 Unauthorized`                  | Client_secret sai / het han. Chay `setup <profile-id>`    |
| `404 /oauth/token`                  | Sua `tokenUrl` trong `profiles/<id>/secrets.json`         |
| `Khong giai ma duoc secret`         | Doi may. Chay `setup <profile-id>` de tao lai             |
| `Chua co profile nao`               | Chay `sap-btp-agent setup <URL>`                          |

## Trang thai

v0.2.0 -- da ho tro **multi-profile**, them `sap_list_profiles`, moi tool co tham so
`profile`, wizard sinh id tu URL.
