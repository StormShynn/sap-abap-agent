---
name: mcp-sap-notes
description: Huong dan cai dat va su dung mcp-sap-notes MCP server — tra cuu SAP Notes va Knowledge Base articles truc tiep tu AI assistant. Tim kiem theo keyword, error code, component, hoac lay full noi dung SAP Note kem ABAP correction instructions.
when_to_use: |
  "cai dat mcp-sap-notes", "tra cuu SAP Notes tu Claude", "tim SAP Note ve loi XXX",
  "lay noi dung SAP Note 123456", "cau hinh mcp-sap-notes".
argument-hint: "[SAP Note number / keyword / error code]"
effort: low
model: haiku
tools: [Read, WebFetch]
---

# mcp-sap-notes — SAP Notes Lookup MCP Server

## Tong quan

`mcp-sap-notes` cho phep AI assistant (Claude Code, Cursor, VS Code) tra cuu SAP Notes va
Knowledge Base articles truc tiep tu SAP Support Portal. Ho tro tim kiem theo tu khoa, lay full
noi dung Note, va kem ABAP correction instructions.

**Repository**: `https://github.com/marianfoo/sap-mcp-servers` (package `packages/notes`)

## Cai dat

### Yeu cau
- Node.js >= 18
- Tai khoan SAP S-user (SAP Support Portal)
- (Option) SAP Passport PFX file cho certificate auth

### Buoc 1: Clone & build

```bash
git clone https://github.com/marianfoo/sap-mcp-servers.git
cd sap-mcp-servers/packages/notes
npm install
npm run build
```

### Buoc 2: Cau hinh trong MCP client

#### Claude Code (.mcp.json)

```json
{
  "mcpServers": {
    "sap-notes": {
      "command": "node",
      "args": ["/path/to/sap-mcp-servers/packages/notes/dist/mcp-server.js"],
      "env": {
        "SAP_USERNAME": "your.s-user@sap.com",
        "SAP_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "sap-notes": {
      "command": "node",
      "args": ["/abs/path/to/sap-mcp-servers/packages/notes/dist/mcp-server.js"],
      "env": {
        "SAP_USERNAME": "your.s-user@sap.com",
        "SAP_PASSWORD": "your_password"
      }
    }
  }
}
```

### Cau hinh Certificate (thay cho password)

```json
{
  "env": {
    "AUTH_METHOD": "certificate",
    "PFX_PATH": "/path/to/certificate.pfx",
    "PFX_PASSPHRASE": "your_passphrase"
  }
}
```

## Tools

| Tool | Tham so | Mo ta |
|------|---------|-------|
| `search` | `q` (string, required), `lang` (EN/DE, default EN) | Tim SAP Note theo keyword, error code, component |
| `fetch` | `id` (string, required), `lang` (EN/DE), `includeCorrections` (bool, default false) | Lay full noi dung SAP Note |

## Cach su dung trong Claude

```text
"Tim SAP Note ve loi 'RFC_ERROR_SYSTEM_FAILURE'"
  → sap-notes_search({ q: "RFC_ERROR_SYSTEM_FAILURE" })

"Lay noi dung SAP Note 123456"
  → sap-notes_fetch({ id: "123456", includeCorrections: true })
```

## Debug

- Set env `HEADFUL=true` de mo browser debug (neu can 2FA)
- Token cache: `token-cache.json` (xoa file de force re-auth)
- MFA timeout: `MFA_TIMEOUT=120000` (default 120s)

## Nguon tham khao

- Repository: `https://github.com/marianfoo/sap-mcp-servers/tree/main/packages/notes`
- SAP Support Portal: `https://support.sap.com`
