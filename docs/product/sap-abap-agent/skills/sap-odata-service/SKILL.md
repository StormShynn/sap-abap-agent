---
name: sap-odata-service
description: Huong dan OData Service Development trong SAP S/4HANA Cloud — RAP-based OData V4, SEGW OData V2, service binding, metadata, testing, extension.
when_to_use: |
  "tao OData service", "RAP expose OData", "service binding", "metadata OData",
  "SEGW vs RAP OData", "OData V2 vs V4 tren cloud".
argument-hint: "[cau hoi ve OData / service / RAP / SEGW]"
effort: medium
model: sonnet
---

# OData Service Development — ABAP Cloud

## 1. RAP-based OData (Khuyen dung)

Tren ABAP Cloud, **RAP-based OData V4 la chuan**. Moi RAP Business Object tu dong co OData service:

### Quy trinh

```text
1. CDS View (ZI_*) -> Behavior Definition -> Service Definition -> Service Binding -> OData
```

### Service Binding

```abap
" Service Definition
@EndUserText.label: 'Sales Order Service Definition'
define service Z_SALES_ORDER_SD {
  expose Z_I_SalesOrder as SalesOrder;
  expose Z_C_SalesOrderItem as Item;
}

" Service Binding (UI / Web API)
-> OData V4 - UI (hoac V4 - Web API)
```

**Hai loai Service Binding**:

| Loai | Dung khi | Vi du |
|------|----------|-------|
| `OData V4 - UI` | Fiori app dung | Fiori Elements, UI5 |
| `OData V4 - Web API` | External integration | CPI, non-SAP, side-by-side |

### Metadata Generation

Khi active service binding, SAP tu dong sinh OData metadata document:
`/sap/opu/odata4/sap/Z_SALES_ORDER_SD/$metadata`

## 2. SEGW OData V2 (Legacy, khong khuyen dung tren Cloud)

SEGW van duoc ho tro tren ABAP Cloud nhung **khong phai la chuan cua ABAP Cloud**:

```abap
" SEGW project -> Data Model -> Entity Type -> Association
" -> Service Maintenance -> Activate
```

| Tieu chi | RAP-based | SEGW |
|----------|-----------|------|
| Cloud chuan | ✅ Chuan ABAP Cloud | ⚠️ Ho tro nhung khuyen dung |
| OData version | V4 | V2 |
| Code generation | Tu dong (boilerplate) | Can code mapping + MPC |
| Annotation | CDS annotation | MPC annotation class |
| Fiori Elements | ✅ | ⚠️ Hack more |
| Performance | Tu dong toi uu | Can manual tune |
| Extension | Custom field tu dong | Can manual |

**Khuyen nghi**: Luon dung RAP-based OData V4 cho project moi. Chi dung SEGW khi can backward compatibility voi OData V2 client cu.

Da co SEGW project can nang cap len RAP? Dung skill `sap-migrate-segw-to-rap` — reverse-engineer Data Model + logic DPC_EXT sang RAP thay vi tu scaffold lai tu dau.

## 3. Service Expose Patterns

```abap
" 1. CRUD — RAP behavior (chu Y)
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique;
  create; update; delete;

" 2. Read-only — CDS view chi doc
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique;
  readonly;

" 3. Unmanaged — custom persistence
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique
  persistent table ztt_salesorder;
  create; update; delete;
```

## 4. OData V2 vs V4

| Tinh nang | OData V2 | OData V4 |
|-----------|----------|----------|
| Response format | JSON (verbose) | JSON (compact) |
| Batch | `$batch` endpoint | Async batch |
| Navigation | `EntitySet` / `EntityType` | `NavigationProperty` |
| Action/Function | `ActionImport` | Bound/Unbound action |
| Annotation | V2 annotation (UI5) | V4 annotation (capable) |
| Lambda | `$filter` + `any/all` | Native `any/all` |
| Cloud chuan | Legacy | ABAP Cloud chuan |

## 5. Service Testing

```bash
# Test OData V4 service
# GET entity set
GET /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder

# GET single entity
GET /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder('10000001')

# POST create
POST /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder

# PATCH update
PATCH /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder('10000001')

# DELETE
DELETE /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder('10000001')

# Function/action
POST /sap/opu/odata4/sap/Z_SALES_ORDER_SD/salesorder/IV_SalesOrder/SubmitOrder
```

**Tools**: SAP API Business Hub, REST Client (VS Code), Postman, CPI test suite.

## 6. Service Extension

### Custom field tu dong co trong OData

Key User Custom Field -> tu dong xuat hien trong OData response:
```
GET .../salesorder -> response: ... "customField1": "abc", ...
```

### Virtual element trong service

CDS virtual element + DCL + annotation -> xuat hien trong OData:
```cds
@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_CALC_SHIPPING'
cast( '' as abap.char( 1000 ) ) as ShippingStatus
```

## 7. Performance Optimization

| Issue | Solution |
|-------|----------|
| Slow query | Add `$filter` + index, tranh `$top` lon |
| Too many expand | `$expand` limit to max 2 levels |
| Batch processing | `$batch` thay vi tung request |
| Large metadata | `$metadata` cached, dung ETag |
| Custom field performance | Virtual element thay vi custom logic tren service |

## Nguon tham khao

- SAP Help: RAP Service Binding, OData V4
- SAP Community: RAP OData best practices
- API Business Hub: `https://api.sap.com`
