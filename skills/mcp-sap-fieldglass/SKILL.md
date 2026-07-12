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

### Yeu cau

- Java 11+
- Maven (de build)
- CData JDBC Driver for SAP Fieldglass (download + license trial)

### Buoc 1: Clone & build

```bash
git clone https://github.com/CDataSoftware/sap-fieldglass-mcp-server-by-cdata.git
cd sap-fieldglass-mcp-server-by-cdata
mvn clean install
```

### Buoc 2: License JDBC Driver

```bash
java -jar cdata.jdbc.sapfieldglass.jar --license
```

### Buoc 3: Tao .prp config file

Tao file `sap-fieldglass.prp`:

```properties
# Connection string
connection.string = "JDBC URL cua SAP Fieldglass..."

# Driver path
driver.path = "/path/to/cdata.jdbc.sapfieldglass.jar"

# Tables cho phep truy van
tables = *
```

### Buoc 4: Cau hinh MCP

```json
{
  "mcpServers": {
    "sap-fieldglass": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/CDataMCP-jar-with-dependencies.jar",
        "/path/to/sap-fieldglass.prp"
      ]
    }
  }
}
```

## Tools

| Tool | Mo ta |
|------|-------|
| `fieldglass_get_tables` | Liet ke tat ca bang trong SAP Fieldglass instance |
| `fieldglass_get_columns` | Liet ke columns cua 1 table |
| `fieldglass_run_query` | Thuc thi SQL SELECT query |

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
