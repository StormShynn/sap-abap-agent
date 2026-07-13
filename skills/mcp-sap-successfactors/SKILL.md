---
name: mcp-sap-successfactors
description: |
  Huong dan cai dat va su dung MCP servers cho SAP SuccessFactors — 2 options: sf-mcp
  (open-source, 62+ tools) va CData SuccessFactors MCP (SQL-based read-only). Tra cuu Employee
  Central, RBP security, Time Off, Hiring, Position Management.
when_to_use: |
  "cai dat SuccessFactors MCP", "tra cuu nhan vien tu Claude", "SF employee data",
  "SuccessFactors API integration", "sf-mcp setup".
argument-hint: "[SuccessFactors Employee Central / user data query]"
effort: low
model: haiku
tools: [Read, WebFetch]
---

# mcp-sap-successfactors — SAP SuccessFactors MCP Servers

## Tong quan

2 options de tich hop SAP SuccessFactors voi AI assistant qua MCP:

| Option | Repository / Nguon | Loai | So tools |
|--------|-------------------|------|----------|
| **sf-mcp** | `aiadiguru2025/sf-mcp` | Open-source, Python/FastMCP | 62+ tools |
| **CData SF MCP** | `CDataSoftware/sap-successfactors-mcp-server-by-cdata` | Commercial (JDBC), Java | 3 tools (SQL) |

## Option 1: sf-mcp (Open-source, khuyen dung)

### Cai dat

```bash
# Yeu cau: Python 3.10+, uv package manager
git clone https://github.com/aiadiguru2025/sf-mcp.git
cd sf-mcp
uv sync
```

### Cau hinh

```json
{
  "mcpServers": {
    "sf-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/sf-mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

### Environment variables

```env
# SAP SuccessFactors OData API credentials
SF_API_URL=https://apiXX.successfactors.com
SF_API_USER=your_username
SF_API_PASS=your_password
SF_COMPANY_ID=your_company
```

## Option 2: CData SuccessFactors MCP (SQL-based, read-only)

### Cai dat

```bash
git clone https://github.com/CDataSoftware/sap-successfactors-mcp-server-by-cdata.git
cd sap-successfactors-mcp-server-by-cdata
mvn clean install
```

### Yeu cau

- Java 11+
- CData JDBC Driver for SAP SuccessFactors (download + license trial)

### Cau hinh

```json
{
  "mcpServers": {
    "sf-cdata": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/CDataMCP-jar-with-dependencies.jar",
        "/path/to/sap-successfactors.prp"
      ]
    }
  }
}
```

### Tools (both options)

| Option | Tool | Mo ta |
|--------|------|-------|
| sf-mcp | `get_employee_info` | Tra cuu thong tin nhan vien |
| sf-mcp | `search_employees` | Tim nhan vien theo criteria |
| sf-mcp | `get_org_structure` | Lay so do to chuc |
| sf-mcp | `get_time_off_balance` | Kiem tra ngay nghi con lai |
| sf-mcp | `get_position_details` | Chi tiet vi tri/position |
| sf-mcp | `get_role_permissions` | Kiem tra RBP permissions |
| CData | `{sf}_get_tables` | Liet ke tables co san |
| CData | `{sf}_get_columns` | Liet ke columns cua 1 table |
| CData | `{sf}_run_query` | Execute SQL SELECT query |

## Vi du su dung

```text
"Tim thong tin nhan vien ma 12345 tren SuccessFactors"
  → sf-mcp_get_employee_info({ employeeId: "12345" })

"Kiem tra ngay nghi con lai cua nhan vien"
  → sf-mcp_get_time_off_balance({ employeeId: "12345" })

"Liet ke tat ca departments"
  → sf-cdata_run_query({ query: "SELECT * FROM Department" })
```

## Nguon tham khao

- sf-mcp: `https://github.com/aiadiguru2025/sf-mcp`
- CData SF: `https://github.com/CDataSoftware/sap-successfactors-mcp-server-by-cdata`
- SAP Community blog: `https://community.sap.com/t5/human-capital-management-blog-posts-by-members/querying-sap-successfactors-in-natural-language-with-claude-desktop-and-the/ba-p/14404437`
