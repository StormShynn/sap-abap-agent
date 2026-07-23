---
name: mcp-sap-concur
description: Huong dan cai dat va su dung CData SAP Concur MCP Server — tra cuu Travel & Expense data (chi phi, bao cao, booking) tu SAP Concur qua SQL-based MCP. Read-only, Java-based, ho tro query bang SQL.
when_to_use: |
  "cai dat Concur MCP", "tra cuu chi phi travel", "SAP Concur data query",
  "lay bao cao expense tu Claude", "CData Concur setup".
argument-hint: "[Concur expense / travel data query]"
effort: low
model: haiku
tools: [Read, WebFetch]
---

# mcp-sap-concur — SAP Concur MCP Server

## Tong quan

`CData SAP Concur MCP Server` cho phep AI assistant query SAP Concur (Travel & Expense) data truc tiep
qua SQL, su dung CData JDBC Driver cho SAP Concur. **Read-only**, Java-based.

**Repository**: `https://github.com/CDataSoftware/sap-concur-mcp-server-by-cdata`

## Cai dat

Co che cai dat/cau hinh (driver JDBC, file `.prp`, dang ky MCP, 3-tool pattern) giong het moi
connector CData khac — xem huong dan chung: `reference/mcp-guides/mcp-sap-cdata-setup.md`.

Rieng cho Concur:

| | |
|---|---|
| Driver JDBC | `cdata.jdbc.concur.jar` |
| File `.prp` | `sap-concur.prp` |
| Server name goi y | `sap-concur` |

## Tools

3 tools SQL chuan cua CData (chi tiet trong shared doc o tren): `concur_get_tables`,
`concur_get_columns`, `concur_run_query`.

## Cac bang pho bien

| Bang | Mo ta |
|------|-------|
| `ExpenseEntry` | Cac khoan chi phi |
| `ExpenseReport` | Bao cao chi phi tong hop |
| `TravelRequest` | Yeu cau dat travel |
| `TravelBooking` | Thong tin booking (ve may bay, khach san) |
| `Employee` | Thong tin nhan vien |
| `Vendor` | Nha cung cap / merchant |
| `Currency` | Ty gia tien te |

## Vi du su dung

```text
"Lay bao cao chi phi thang 12/2025"
  → concur_run_query({ query: "SELECT * FROM ExpenseReport WHERE CreateDate >= '2025-12-01'" })

"Tong chi phi travel cua phong Sales"
  → concur_run_query({ query: "SELECT SUM(Amount) FROM ExpenseEntry WHERE CostCenter = 'SALES'" })
```

## Nguon tham khao

- Repository: `https://github.com/CDataSoftware/sap-concur-mcp-server-by-cdata`
- CData JDBC Driver: `https://www.cdata.com/drivers/concur/download/jdbc`
- CData MCP Official: `https://www.cdata.com/drivers/concur/mcp/`
- Cai dat CData MCP tong quat: `reference/mcp-guides/mcp-sap-cdata-setup.md`
