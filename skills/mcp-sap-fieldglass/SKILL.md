---
name: mcp-sap-fieldglass
description: Huong dan cai dat va su dung CData SAP Fieldglass MCP Server — tra cuu Services Procurement data (statement of work, worker, timesheet, invoice) tu SAP Fieldglass qua SQL-based MCP. Read-only, Java-based.
when_to_use: |
  "cai dat Fieldglass MCP", "tra cuu services procurement", "SAP Fieldglass data query",
  "lay worker/SoW data tu Claude", "CData Fieldglass setup".
argument-hint: "[Fieldglass services procurement / worker data query]"
effort: low
model: haiku
tools: [Read, WebFetch]
---

# mcp-sap-fieldglass — SAP Fieldglass MCP Server

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
