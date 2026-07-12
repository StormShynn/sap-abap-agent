---
name: sap-cap-cloud
description: Kien thuc CAP chi tiet — project structure, CDS, service, Fiori, deployment, extension pattern, testing, best practices.
effort: medium
model: haiku
---

# CAP — DEEP — BTP

[Seed set — kiem chung qua CAP documentation (`cap.cloud.sap`) va SAP Community.]

## 1. CAP Project Structure

```
my-cap-app/
+-- app/               # frontend (UI5 / Fiori)
+-- srv/               # service layer (Node.js / Java)
|   +-- cat-service.cds
|   +-- cat-service.js
+-- db/                # data model
|   +-- schema.cds
+-- package.json       # (Node.js) hoac pom.xml (Java)
+-- .cdsrc.json        # CAP config
+-- mta.yaml           # MTA deployment
```

## 2. CAP CDS

### Entity & Service

```cds
// db/schema.cds
entity Books {
  key ID : Integer;
  title  : String(100);
  author : Association to Authors;
}

// srv/cat-service.cds
service CatalogService {
  entity Books as projection on books.Books;
}
```

### CAP vs ABAP CDS khac biet

| Tinh nang | CAP CDS | ABAP CDS |
|---|---|---|
| Runtime | Node.js / Java | ABAP |
| Database | HANA / SQLite / PostgreSQL | HANA only |
| Association | `Association to` | `Association to` (tuong tu) |
| Annotation | `@title`, `@Common:` | `@EndUserText`, `@Metadata.allowExtensions` |
| Deployment | `cds deploy` | ADT activate |
| Extension | `@cap-js/*` packages | ABAP BAdI |

- **Persistence annotation**: CAP dung `@cds.persistence`, khong co `@AbapCatalog`.

## 3. CAP Service

```cds
// RESTful handler
service CatalogService @(path: '/browse') {
  entity Books as projection on books.Books
    excluding { price };   // hide field from external
  
  // Custom action
  action submitOrder(book: Books:ID, quantity: Integer);
}
```

## 4. CAP + Fiori Elements

```cds
// CDS annotation cho Fiori
annotate CatalogService.Books with @(
  UI : {
    SelectionFields : [title],
    LineItem : [
      { value: title, critical: true },
      { value: author.name }
    ]
  }
);
```

## 5. CAP + S/4HANA Extension

```cds
// External service (remote)
using { API_SALES_ORDER_SRV as S4 } from 's4-api';

service ExtensionService {
  entity SalesOrders as projection on S4.A_SalesOrder;
}
```

**Destination**: S/4HANA API can cau hinh destination trong BTP Cockpit.

## 6. CAP Deployment (MTA)

- **CAP 8+** chay tren SAP BTP, Cloud Foundry, Kyma.

```yaml
# mta.yaml
_schema-version: '3.2'
ID: my-cap-app
version: 1.0.0

modules:
  - name: my-cap-app-srv
    type: nodejs
    path: srv
    requires:
      - name: my-cap-app-db
      - name: my-cap-app-uaa

resources:
  - name: my-cap-app-db
    type: com.sap.xs.hana-container
  - name: my-cap-app-uaa
    type: com.sap.xs.uaa
```

## 7. Testing

```
npm test         # Mocha/Chai (Node.js)
cds test         # CAP test framework
mvn test         # JUnit (Java)
```

## 8. Best Practices

- **Luon dung `@cap-js/hana`** cho production (khong dung `@sap/cds` direct HANA)
- **`@cap-js/*`**: Official CAP packages (`@cap-js/sqlite`, `@cap-js/hana`, `@cap-js/cds-types`).
- **Phan tach app/srv/db** ro rang
- **Dung cds watch**: `cds watch` de hot-reload development
- **Dung cds add**: `cds add xsa`, `cds add hana`, `cds add multitenancy`
- **Error handling**: `req.error(422, 'message')` in handler

## 9. Nguon tham khao

- Official CAP docs: `https://cap.cloud.sap/docs/`
- CAP GitHub: `https://github.com/sap-samples/cloud-cap-samples`
- CDS Language Reference: `https://cap.cloud.sap/docs/cds/`
