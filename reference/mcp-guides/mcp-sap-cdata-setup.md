# CData JDBC MCP Server — Generic Setup Guide

Co che cai dat/cau hinh dung chung cho **bat ky CData JDBC-based MCP server** nao cho SAP (SAP
Concur, SAP Fieldglass, SAP SuccessFactors CData option, va cac connector CData khac trong tuong
lai). Cac skill rieng cua tung connector chi giu lai phan **dac thu product** (bang/entity nao
quan trong, sample query, link tai lieu rieng) va tro ve day cho phan cai dat chung.

**Dung o dau**: `skills/mcp-sap-concur/SKILL.md`, `skills/mcp-sap-fieldglass/SKILL.md`,
`reference/mcp-guides/mcp-sap-successfactors.md` (Option 2 — CData).

## Kien truc

`CData <Product> MCP Server` = CData JDBC Driver rieng cho product + `CDataMCP-jar-with-dependencies.jar`
(MCP wrapper Java dung chung cho moi driver CData). **Read-only**, expose 3 tool SQL-based.

## Yeu cau

- Java 11+
- Maven (chi can neu build MCP wrapper tu source)
- CData JDBC Driver rieng cho tung product (download + license/trial tren cdata.com)

## Buoc 1: Lay driver JDBC + MCP jar

1. Download CData JDBC Driver cho product can dung (vd: `cdata.jdbc.concur.jar`,
   `cdata.jdbc.sapfieldglass.jar`, `cdata.jdbc.sapsuccessfactors.jar`).
2. License driver (neu dung ban trial):
   ```bash
   java -jar cdata.jdbc.<product>.jar --license
   ```
3. Lay `CDataMCP-jar-with-dependencies.jar` — day la MCP wrapper **dung chung**, khong doi theo
   product.

Neu build tu source repo cua 1 connector CData cu the (vd repo `sap-<product>-mcp-server-by-cdata`
tren GitHub cua CDataSoftware):

```bash
git clone <repo-cua-connector>
cd <ten-thu-muc-repo>
mvn clean install
```

## Buoc 2: Tao file `.prp` (connection config)

Format `.prp` giong het nhau cho moi connector CData, chi khac gia tri:

```properties
# Connection string (lay tu CData JDBC connection string designer/utility cua driver)
connection.string = "JDBC URL cua <Product>..."

# Duong dan toi driver JDBC rieng cua product (Buoc 1)
driver.path = "/path/to/cdata.jdbc.<product>.jar"

# Danh sach bang cho phep truy van ('*' = tat ca)
tables = *
```

Auth thuong khai bao ngay trong `connection.string` (hoac qua param rieng), 2 kieu pho bien:

```env
# OAuth2
OAuthClientId=your_client_id
OAuthClientSecret=your_client_secret

# Hoac Basic Auth
User=your_username
Password=your_password
```

## Buoc 3: Dang ky MCP server

### Cach A — `claude mcp add` (CLI, khuyen dung)

```bash
claude mcp add --transport stdio <server-name> -- java -jar /path/to/CDataMCP-jar-with-dependencies.jar /path/to/<product>.prp
```

### Cach B — file cau hinh MCP (JSON, vd `.mcp.json`)

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/CDataMCP-jar-with-dependencies.jar",
        "/path/to/<product>.prp"
      ]
    }
  }
}
```

## Tools (giong nhau cho moi connector CData)

| Tool pattern | Mo ta |
|------|-------|
| `<prefix>_get_tables` | Liet ke tat ca bang trong instance |
| `<prefix>_get_columns` | Liet ke columns cua 1 table |
| `<prefix>_run_query` | Thuc thi SQL SELECT query (read-only) |

`<prefix>` la ten server cho tung connector (vd: `concur_`, `fieldglass_`, `sf_` / `{sf}_`).

## Nguon tham khao chung

- CData MCP (tong quan): `https://www.cdata.com/drivers/<product>/mcp/`
- CData JDBC Driver download: `https://www.cdata.com/drivers/<product>/download/jdbc`

(Thay `<product>` bang ten CData dung cho connector: `concur`, `sapfieldglass`,
`sapsuccessfactors`, ...)
