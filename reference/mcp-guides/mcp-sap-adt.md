# ADT MCP Servers — 3 lua chon cho ABAP Development

**Dung o dau**: agent `sap-docs-researcher` (khai bao `skills: [..., mcp-sap-adt, ...]`), va cac
skill `sap-bootstrap-system-context`, `sap-cloud-dictionary`, `sap-deployment-target` (dan chieu
bang ten khi user can chon/cai dat 1 trong 3 lua chon ADT MCP server ben duoi).

## Lua chon 1: SAP Official ADT MCP (VS Code Extension) 🏆

SAP da tich hop MCP server vao **ABAP Development Tools (ADT) for Visual Studio Code** extension.
Day la giai phap **chinh thong** va **zero-config** nhat.

### Installation

1. Cai extension **ABAP Development Tools for Visual Studio Code** tu VS Code marketplace
2. Enable MCP Server:
   - VS Code -> Settings -> ABAP > AI: Enable ADT MCP Server -> **true**
3. Connect to ABAP system:
   - VS Code -> ABAP Explorer -> Add System -> Nhap URL SAP BTP / S/4HANA Cloud

### Tools (built-in)

| Tool | Mo ta |
|------|-------|
| `Read ABAP Class / Program / CDS` | Doc source code |
| `Activate ABAP Object` | Activate object |
| `Syntax Check` | Kiem tra syntax |
| `Search ABAP Objects` | Tim object theo ten |
| `Transport Management` | Quan ly transport request |
| `Run ABAP Unit Tests` | Chay unit test |
| `Debug ABAP` | Debugging support |

**Uu diem**: Khong can cau hinh MCP JSON, SAP tu dong quan ly authentication (single sign-on),
tuong hoa hoan toan voi ABAP Cloud.

**Nhuoc diem**: Chi dung duoc trong VS Code ADT.

---

## Lua chon 2: ARC-1 (Enterprise, Secure-by-default) 🏢

ARC-1 la MCP server doanh nghiep, duoc thiet ke voi bao mat cao nhat.

**Repository**: `https://github.com/arc-mcp/arc-1`

### Installation

```bash
# Local (nhanh)
npx arc-1@latest

# Docker (production)
docker pull ghcr.io/arc-mcp/arc-1
docker run -p 3000:3000 ghcr.io/arc-mcp/arc-1

# Cloud Foundry (BTP)
cf push arc-1 --docker-image ghcr.io/arc-mcp/arc-1
```

### Cau hinh (Claude Code)

```json
{
  "mcpServers": {
    "arc-1": {
      "command": "npx",
      "args": ["-y", "arc-1@latest"]
    }
  }
}
```

### Tools

| Tool | Mo ta |
|------|-------|
| `abap_read_source` | Doc source code ABAP |
| `abap_search` | Tim kiem ABAP object |
| `abap_activate` | Activate object |
| `abap_syntax_check` | Syntax check |
| `abap_atc_check` | Chay ATC check |
| `abap_transport_list` | List transport requests |
| `abap_transport_release` | Release transport |
| `abap_unit_test` | Chay ABAP unit test |

**Uu diem**: 3000+ unit tests, principal propagation (XSUAA/OIDC), audit logging,
package allowlist, read-only mode, deploy central (BTP/Docker).

**Nhuoc diem**: Can cau hinh BTP destination cho authentication.

---

## Lua chon 3: mcp-abap-adt (Community, De su dung) 👥

Co **2 fork** chinh cua MCP server cong dong cho ADT:

| Fork | Tac gia | Dac diem |
|------|---------|----------|
| **mario-andreschak/mcp-abap-adt** | `mario-andreschak` | Original — 9 read-only tools: doc ABAP code, activate, search. De dung, POC nhanh. |
| **fr0ster/mcp-abap-adt** (khuyen dung) | `fr0ster` | **Full CRUD**: tao Domain, Data Element, Database Table, CDS View, RAP artifacts. Auth destination-based, nhieu transport mode. Version 8.x. |

---

### Option A: mario-andreschak/mcp-abap-adt (read-only)

**Repository**: `https://github.com/mario-andreschak/mcp-abap-adt`

```bash
npx -y mcp-abap-adt
```

**Cau hinh (Claude Code):**
```json
{
  "mcpServers": {
    "mcp-abap-adt": {
      "command": "npx",
      "args": ["-y", "mcp-abap-adt"],
      "env": {
        "ADT_URL": "https://my-system.s4hana.cloud.sap",
        "ADT_USER": "username",
        "ADT_PASS": "password",
        "ADT_CLIENT": "100"
      }
    }
  }
}
```

**Tools:** `GetProgram`, `GetClass`, `GetFunctionGroup`, `GetCDSView`, `GetTable`, `GetRAPBehaviorDef`, `GetRAPServiceDef`, `ActivateObject`, `SearchObjects`.

---

### Option B: fr0ster/mcp-abap-adt (Full CRUD)

**Repository**: `https://github.com/fr0ster/mcp-abap-adt`

Full CRUD MCP server cho ADT: tao Domain, Data Element, Database Table, CDS View, RAP Behavior, v.v.

📌 **Cap nhat thuc te trong repo nay**: sau khi thu wiring option nay, du an da chuyen sang tu xay
**`sap-dict-bridge`** (`reference/mcp-server/sap_btp_agent/bridge_server.py`) — tai su dung cookie
auth co san cua `sap-btp-agent` thay vi can basic auth/config `.env` rieng nhu duoi day. Xem skill
`sap-cloud-dictionary` (Buoc 8) de dung ban native nay. Noi dung Option B duoi day van giu lai lam
tham khao neu muon dung ban goc cua `fr0ster`.

#### Cai dat

```bash
npm install -g @mcp-abap-adt/core
npm install -g @mcp-abap-adt/configurator   # (optional) config tool
```

#### Cau hinh .env file

Tao file `.env` (vd: `mcp-abap-adt.env`) voi thong tin SAP ADT:
```ini
SAP_URL=https://my-system.s4hana.cloud.sap
SAP_CLIENT=100
SAP_AUTH_TYPE=basic
SAP_USERNAME=username@domain.com
SAP_PASSWORD=your-password
SAP_LANGUAGE=EN
SAP_SYSTEM_TYPE=cloud       # cloud | onprem | legacy
```

#### Cau hinh YAML (optional)

Tao file `mcp-abap-adt-config.yaml`:
```yaml
transport: stdio
exposition: readonly,high    # high = Create*, Update*High (dictionary CRUD)
system-type: cloud
```

**Handler sets:**
| Set | Mo ta | Tools |
|-----|-------|-------|
| `readonly` | Doc, lock, validate | GetClass, GetTable, GetCDSView, Lock/Unlock... |
| `high` | Tao/sua an toan | **CreateDomain**, **CreateDataElement**, **CreateTable**, Update*High |
| `low` | Nguy hiem (can than) | ActivateObject, Delete*, Update*Low |
| `compact` | Facade object_type | `CreateObject`, `GetObject`, `UpdateObject`, `DeleteObject` |

#### Dang ky voi Claude Code

```bash
claude mcp add --transport stdio --scope project mcp-abap-adt-dict -- npx -y @mcp-abap-adt/core --env-path=mcp-abap-adt.env --conf=mcp-abap-adt-config.yaml
```

#### Tools tao Dictionary

| Tool | Mo ta |
|------|-------|
| `CreateDomain` | Tao Domain ABAP Cloud (`define domain ...`) |
| `CreateDataElement` | Tao Data Element (`define data element ...`) |
| `CreateTable` | Tao Database Table (`define table ...`) |
| `CreateView` | Tao CDS View (`define view entity ...`) |
| `CreateBehaviorDef` | Tao RAP Behavior Definition |
| `Get*` (nhieu loai) | Doc source code |
| `ActivateObject` | Activate + transport |

**Uu diem**: Full CRUD (khong chi read), tao duoc dictionary objects truc tiep, nhieu transport mode (stdio/http/SSE), handler co the filter theo level (readonly/high/low).

**Nhuoc diem**: Can cai them npm global package, can .env config.

---

## So sanh

| Tinh nang | SAP Official ADT (VS Code) | ARC-1 | mcp-abap-adt |
|-----------|---------------------------|-------|--------------|
| **Config** | Zero-config | `npx arc-1@latest` | `npx mcp-abap-adt` |
| **Security** | SSO (SAP) | XSUAA, Auditing | Basic auth |
| **Deployment** | Built-in VS Code | Local/Docker/BTP | Local |
| **ABAP Cloud** | ✅ Full | ✅ Full | ✅ Full |
| **RAP** | ✅ | ✅ | ✅ |
| **ATC** | ✅ | ✅ | ❌ |
| **Transport** | ✅ | ✅ | ❌ |
| **Unit Test** | ✅ | ✅ | ❌ |
| **Audit Log** | SAP system log | Built-in JSONL | ❌ |
| **Open Source** | ❌ (SAP proprietary) | ✅ | ✅ |

## Khuyen nghi

| Ai nen dung | Lua chon |
|-------------|----------|
| Developer VS Code ADT | **SAP Official ADT MCP** (zero-config) |
| Enterprise/Team can security | **ARC-1** (audit, principal propagation) |
| Ca nhan / POC nhanh | **mcp-abap-adt** (1 lenh, de dung) |
| Team mix tool (Cursor, Claude) | **ARC-1** (ho tro nhieu client) |

## Nguon tham khao

- SAP ADT for VS Code: `https://marketplace.visualstudio.com/items?itemName=SAP.adt`
- ARC-1: `https://github.com/arc-mcp/arc-1`
- mcp-abap-adt: `https://github.com/mario-andreschak/mcp-abap-adt`
- SAP MCP Server Catalog: `https://github.com/marianfoo/sap-ai-mcp-servers`
