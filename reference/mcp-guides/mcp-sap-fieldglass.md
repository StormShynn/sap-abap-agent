# mcp-sap-fieldglass — SAP Fieldglass MCP Server

**Dung o dau**: agent `sap-docs-researcher` (khai bao `skills: [..., mcp-sap-fieldglass, ...]`)
— doc file nay khi user can cai dat hoac tra cuu SAP Fieldglass Services Procurement qua MCP.
Chuyen tu `skills/mcp-sap-fieldglass/` sang day 2026-07-31 (xem
`docs/audits/2026-Q3-skill-consolidation-part2.md`) — thuan tuy huong dan cai dat 1 lan, khong
can tu-trigger toan cuc qua tu khoa.

## Tong quan

`CData SAP Fieldglass MCP Server` cho phep AI assistant query SAP Fieldglass (Services Procurement)
data qua SQL. Quan ly contingent workforce, Statement of Work (SoW), worker profiles, timesheets,
invoices. **Read-only**, Java-based.

**Repository**: `https://github.com/CDataSoftware/sap-fieldglass-mcp-server-by-cdata`

## Cai dat

Co che cai dat/cau hinh (driver JDBC, file `.prp`, dang ky MCP, 3-tool pattern) giong het moi
connector CData khac — xem huong dan chung: `reference/mcp-guides/mcp-sap-cdata-setup.md`.

Rieng cho Fieldglass:

| | |
|---|---|
| Driver JDBC | `cdata.jdbc.sapfieldglass.jar` |
| File `.prp` | `sap-fieldglass.prp` |
| Server name goi y | `sap-fieldglass` |

## Tools

3 tools SQL chuan cua CData (chi tiet trong shared doc o tren): `fieldglass_get_tables`,
`fieldglass_get_columns`, `fieldglass_run_query`.

## Cac bang pho bien

| Bang | Mo ta |
|------|-------|
| `Worker` | Thong tin contingent worker |
| `StatementOfWork` | Statement of Work (SoW) |
| `Timesheet` | Timesheet cua worker |
| `Invoice` | Hoa don tu nha cung cap |
| `Msa` | Master Service Agreement |
| `WorkOrder` | Work order / job order |
| `Supplier` | Nha cung cap dich vu |

## Vi du su dung

```text
"Lay danh sach worker active theo SoW 12345"
  → fieldglass_run_query({ query: "SELECT * FROM Worker WHERE SoWId = '12345' AND Status = 'Active'" })

"Kiem tra timesheet chua duyet cua worker"
  → fieldglass_run_query({ query: "SELECT * FROM Timesheet WHERE Status = 'Pending Approval'" })
```

## Nguon tham khao

- Repository: `https://github.com/CDataSoftware/sap-fieldglass-mcp-server-by-cdata`
- CData JDBC Driver: `https://www.cdata.com/drivers/sapfieldglass/download/jdbc`
- CData MCP Official: `https://www.cdata.com/drivers/sapfieldglass/mcp/`
- Cai dat CData MCP tong quat: `reference/mcp-guides/mcp-sap-cdata-setup.md`
