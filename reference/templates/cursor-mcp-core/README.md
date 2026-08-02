# Cursor / VS Code — MCP Core pack (docs-only)

Template khớp **Core bắt buộc** của plugin (không port skills/hooks):

| Server | Transport |
|--------|-----------|
| `sap-btp` | stdio → `mcp-sap-connect` |
| `sap-dict-bridge` | stdio → `python -m mcp_sap_connect.bridge_server` |
| `cds-kb` | stdio bridge → SSE via `npx supergateway` |
| `mcp-sap-docs-btp` | stdio bridge → SSE via `npx supergateway` |

## Emit

```powershell
python reference/scripts/emit_cursor_mcp_pack.py -o %USERPROFILE%\.cursor\mcp.json
```

Optional: set env `SAP_API_HUB_KEY` trước khi emit để gắn vào `mcp-sap-docs-btp`.

Policy: Claude Code owns skills — xem onboarding Host matrix.
