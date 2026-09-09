---
name: cap-cloud
description: Knowledge note tổng hợp từ `secondsky/sap-skills`, `gavdilabs/cap-mcp-plugin` — SAP Cloud Application Programming Model (CAP) trên BTP, dùng để tra cứu nhanh. Knowledge note (không phải instruction skill), đồng nhất cấu trúc với `reference/modules/<module>-cloud/SKILL.md`.
effort: low
model: haiku
---

# SAP CAP — Cloud Knowledge Note

Module con của plugin, dùng khi contributor cần tra nhanh khái niệm CAP mà không cần scaffold thật.
Không thay thế skill `sap-cap-consultant-cloud`.

## 1. CAP là gì?

CAP = **Cloud Application Programming Model**. Framework của SAP để xây dựng side-by-side
extension / custom app trên BTP. Hỗ trợ 2 runtime:

- **Node.js** (`@sap/cds`) — phổ biến nhất, JavaScript/TypeScript.
- **Java** (`cds-services`) — Spring Boot stack.

**Khác RAP**: RAP chạy thuần ABAP trên Steampunk / S/4HANA; CAP chạy Node.js/Java trên BTP
Cloud Foundry hoặc Kyma.

## 2. Kiến trúc

```
┌────────────────────────────────────────────────────┐
│ SAP Fiori (UI5) / SAP Build Apps / Custom UI       │  ← Frontend
├────────────────────────────────────────────────────┤
│ OData V4 / REST / GraphQL / Event Mesh              │  ← API layer
├────────────────────────────────────────────────────┤
│ CAP Service (Node.js / Java)                       │  ← Service layer (CDS + handlers)
├────────────────────────────────────────────────────┤
│ SAP HANA Cloud / PostgreSQL / SQLite               │  ← Persistence
└────────────────────────────────────────────────────┘
```

## 3. Cấu trúc thư mục chuẩn

```
my-cap-app/
├── db/                      # CDS schema (database layer)
│   └── data-model.cds
├── srv/                     # Service implementation (Node.js / Java)
│   ├── catalog-service.cds
│   └── catalog-service.js
├── app/                     # Fiori UI5 app (optional - có thể ở repo khác)
├── package.json
└── README.md
```

## 4. CDS snippet (Node.js flavor)

```cds
// db/data-model.cds
namespace my.bookshop;

entity Books {
  key ID : Integer;
  title  : String;
  stock  : Integer;
}
```

```cds
// srv/catalog-service.cds
using my.bookshop as my;

service CatalogService {
  entity Books as projection on my.Books;
}
```

```javascript
// srv/catalog-service.js
const cds = require('@sap/cds');

module.exports = cds.service.impl(async function() {
  this.on('READ', 'Books', async (req) => {
    // custom logic trước/sau khi đọc
    return await cds.tx(req).run(req.query);
  });
});
```

## 5. Lệnh `cds` CLI phổ biến

| Lệnh                  | Mục đích                              |
|-----------------------|----------------------------------------|
| `cds init`            | Khởi tạo project CAP                   |
| `cds add hana`        | Thêm HANA Cloud configuration          |
| `cds watch`           | Live-reload dev server (Node.js)       |
| `cds build`           | Build production artifact              |
| `cds deploy`          | Deploy lên Cloud Foundry / Kyma        |
| `cds compile`         | Compile CDS → SQL / EDMX              |
| `cds test`            | Chạy unit test                        |

## 6. Multi-tenancy (SaaS)

CAP hỗ trợ multi-tenant SaaS extension:

- `@sap/cds-mtxs` — extension framework cho SaaS.
- `@sap/cds-mtxs-sidecar` — HDI container per tenant.
- Tenant routing qua `xsappname` + XSUAA.

## 7. Anti-pattern

- ⚠️ Hardcode business logic trong CDS layer — để ở handler service.
- ⚠️ Mix Node.js + Java trong 1 service — chọn 1.
- ⚠️ Dùng SQLite cho production — chỉ dùng dev/test.
- ⚠️ Không viết unit test — CAP có test framework riêng (`cds.test`).

## 8. So sánh nhanh CAP vs RAP

| Tiêu chí            | CAP (Node.js/Java)      | RAP (ABAP)         |
|----------------------|-------------------------|---------------------|
| Runtime              | BTP CF / Kyma           | ABAP Cloud / Steampunk |
| Ngôn ngữ             | JavaScript / TypeScript / Java | ABAP |
| Database             | HANA Cloud / Postgres  | HANA Cloud         |
| OData                | V4 (native), V2         | V4 (native), V2     |
| Microservice         | Built-in                | Qua Service Binding |
| Event Mesh           | Built-in                | Enterprise Event Enablement |

## 9. Liên kết với các skill khác

- **Consultant thật**: `sap-cap-consultant-cloud`.
- **MCP plugin cho CAP**: xem `docs/sap-mcp-recommendations.md` Tier 2 (`gavdilabs/cap-mcp-plugin`).
- **Review code**: `sap-atc-review` (không cover CAP nhưng áp dụng được pattern chung).

## 10. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — có module CAP.
- [`gavdilabs/cap-mcp-plugin`](https://github.com/gavdilabs/cap-mcp-plugin) — MCP plugin cho CAP
  NodeJS (tham khảo cách expose CAP service qua MCP).
- [`skalmodiya/sap-ai-core-launchpad`](https://github.com/skalmodiya/sap-ai-core-launchpad) —
  CAP integration với SAP AI Core.
- SAP Help: CAP documentation.
