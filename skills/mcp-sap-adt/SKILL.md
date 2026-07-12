---
name: mcp-sap-adt
description: Huong dan cai dat va su dung ADT MCP servers — 3 lua chon: (1) SAP Official ADT MCP for VS Code (zero-config, built-in), (2) ARC-1 (enterprise, secure-by-default), (3) mcp-abap-adt (community, de su dung). Cho phep AI doc ABAP code, activate, syntax-check, manage transport, chay ATC.
when_to_use: |
  "cai dat ADT MCP server", "SAP official MCP", "ARC-1 MCP", "mcp-abap-adt",
  "ket noi ABAP ADT qua MCP", "tool ADT MCP", "doc ABAP code tu AI".
argument-hint: "[cai dat SAP Official / ARC-1 / mcp-abap-adt]"
effort: low
model: haiku
tools: [Read, WebFetch]
---

# ADT MCP Servers — 3 lua chon cho ABAP Development

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
| `Run ATC Check` | Chay ATC check |
| `Search ABAP Objects` | Tim object theo ten |
| `Transport Management` | Quan ly transport request |
| `Run ABAP Unit Tests` | Chay unit test |
| `Debug ABAP` | Debugging support |

**Uu diem**: Khong can cau hinh MCP JSON, SAP tu dong quan ly authentication (single sign-on),
tuong thich hoan toan voi ABAP Cloud.

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

MCP server cong dong pho bien nhat, de cai dat va su dung.

**Repository**: `https://github.com/mario-andreschak/mcp-abap-adt`

### Installation

```bash
# Khong can clone - chay truc tiep
npx -y mcp-abap-adt

# Hoac tu source
git clone https://github.com/mario-andreschak/mcp-abap-adt.git
cd mcp-abap-adt
npm install
npm run build
```

### Cau hinh (Claude Code)

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

### Tools

| Tool | Mo ta |
|------|-------|
| `GetProgram` | Doc ABAP program source |
| `GetClass` | Doc ABAP class |
| `GetFunctionGroup` | Doc function group |
| `GetCDSView` | Doc CDS view definition |
| `GetTable` | Doc DDIC table structure |
| `GetRAPBehaviorDef` | Doc RAP behavior definition |
| `GetRAPServiceDef` | Doc RAP service definition |
| `ActivateObject` | Activate ABAP object |
| `SearchObjects` | Tim object theo ten/pattern |

**Uu diem**: De cai nhat (1 lenh), nhieu tool cho RAP/CDS, active cong dong.

**Nhuoc diem**: Can env config, khong co audit/security mac dinh.

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
