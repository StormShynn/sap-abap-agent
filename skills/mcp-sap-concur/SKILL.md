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

### Yeu cau

- Java 11+
- Maven (de build)
- CData JDBC Driver for SAP Concur (download + license)

### Buoc 1: Clone & build

```bash
git clone https://github.com/CDataSoftware/sap-concur-mcp-server-by-cdata.git
cd sap-concur-mcp-server-by-cdata
mvn clean install
```

### Buoc 2: Tao .prp config file

Tao file `sap-concur.prp`:

```properties
# Connection string (lay tu CData JDBC utility)
connection.string = "JDBC URL cua SAP Concur..."

# Driver path
driver.path = "/path/to/cdata.jdbc.concur.jar"

# Tables cho phep truy van
tables = *
```

### Buoc 3: Cau hinh MCP

```json
{
  "mcpServers": {
    "sap-concur": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/CDataMCP-jar-with-dependencies.jar",
        "/path/to/sap-concur.prp"
      ]
    }
  }
}
```

### Environment variables (qua JDBC connection string)

```env
# OAuth2 credentials
OAuthClientId=your_client_id
OAuthClientSecret=your_client_secret
# Hoac: Basic Auth
User=your_username
Password=your_password
```

## Tools

| Tool | Mo ta |
|------|-------|
| `concur_get_tables` | Liet ke tat ca bang trong SAP Concur instance |
| `concur_get_columns` | Liet ke columns cua 1 table |
| `concur_run_query` | Thuc thi SQL SELECT query |

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
