---
name: fiori-elements-cloud
description: Knowledge note tổng hợp từ `secondsky/sap-skills`, `skalmodiya/sap-ai-core-launchpad` và `google/ai-abap-assistant-sample` — SAP Fiori Elements trên ABAP Cloud, dùng để tra cứu nhanh. Knowledge note (không phải instruction skill), đồng nhất cấu trúc với `reference/modules/<module>-cloud/SKILL.md`.
effort: low
model: haiku
---

# SAP Fiori Elements — Cloud Knowledge Note

Module con của plugin, dùng khi contributor cần tra nhanh khái niệm Fiori Elements mà không cần
scaffold thật. Không thay thế skill `sap-fiori-consultant-cloud` (agent consult thật).

## 1. Fiori Elements là gì?

Fiori Elements = **framework sinh UI theo metadata**. Dev chỉ cần expose 1 OData V4 service với
annotation đúng chuẩn SAP, Fiori Elements tự render List Report, Object Page, Analytical List
Page, Overview Page, Form, Wizard… Không cần viết UI5/JavaScript thủ công cho use case CRUD.

## 2. Các floorplan chính

| Floorplan              | Mục đích                                  | Annotation chính           |
|------------------------|-------------------------------------------|----------------------------|
| **List Report**        | Bảng tìm kiếm + filter + action          | `@UI`, `@Search`           |
| **Object Page**        | Chi tiết 1 entity + section + facet        | `@UI.facet`, `@UI.lineItem`|
| **Analytical List Page** | Báo cáo với chart + grouping             | `@UI.chart`, `@UI.aggregation` |
| **Overview Page**      | Dashboard nhiều card                       | `@UI.card`                 |
| **Form / Wizard**      | Nhập liệu từng step                       | `@UI.fieldGroup`           |

## 3. Kết hợp với RAP

Fiori Elements consume **OData V4 của RAP Service Binding**. Tức là:

```
CDS View (ZI/ZC)  →  Behavior Definition  →  Behavior Impl (ZBP)
                                          ↓
                                  Service Definition (ZSD_*)
                                          ↓
                                  Service Binding (ZUI_*_O4)
                                          ↓
                                  Fiori Elements App
```

- Annotation thêm vào **CDS View** (khai báo `@UI`/`@Search` ngay trong DDL).
- KPI / Chart thêm ở **Cube / Dimension CDS** (analytical).

## 4. Skeleton annotation mẫu

```sql
@AbapCatalog.sqlViewName: 'ZSORDER'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@UI: {
  headerInfo: { typeName: 'Sales Order', typeNamePlural: 'Sales Orders' }
}
define view ZI_SORDER as select from I_SalesOrder
{
  key SalesOrder                 as SalesOrder,
      SalesOrderType             as SalesOrderType,
      SalesOrganization           as SalesOrganization,
      @UI: { lineItem: [{ position: 10, label: 'Order Date' }] }
      OrderDate                   as OrderDate,
      @UI: { lineItem: [{ position: 20, label: 'Total Amount' }] }
      TotalNetAmount              as TotalNetAmount,
      @UI: { lineItem: [{ position: 30, label: 'Status' }] }
      OverallStatus               as OverallStatus
}
```

Activation → preview Service Binding trong ADT → launchpad hiển thị List Report.

## 5. Naming convention (tham khảo `sap-clean-code`)

| Object            | Pattern    | Ví dụ           |
|-------------------|------------|-----------------|
| Interface view    | `ZI_*`     | `ZI_SORDER`     |
| Consumption view  | `ZC_*`     | `ZC_SORDER`     |
| Service binding   | `ZUI_*_O4` | `ZUI_SORDER_O4` |

## 6. Anti-pattern

- ⚠️ Viết Fiori App thủ công bằng UI5 thuần cho CRUD đơn giản — Fiori Elements + RAP đã đủ.
- ⚠️ Dùng OData V2 — luôn chọn V4 cho Cloud (V2 đang ở maintenance mode).
- ⚠️ Annotation rải khắp CDS layer — giữ annotation gọn trong view gần nhất với UI.
- ⚠️ Bỏ qua Field Control (`@UI.fieldControl`) — dùng để READ-ONLY field có điều kiện.

## 7. Liên kết với các skill khác

- **Consultant thật**: `sap-fiori-consultant-cloud` (Fiori/UI5 module).
- **Scaffold OData**: `sap-odata-service`, `sap-scaffold-rap`.
- **Review code**: `sap-atc-review` mục "RAG Review Pattern".
- **Bootstrap hệ thống thật**: `sap-bootstrap-system-context`.

## 8. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — plugin AI coding assistant
  production-ready (có module Fiori Elements).
- [`skalmodiya/sap-ai-core-launchpad`](https://github.com/skalmodiya/sap-ai-core-launchpad) —
  FastAPI + React chatbot học SAP AI Core (frontend pattern kết hợp Fiori/UI5).
- [`google/ai-abap-assistant-sample`](https://github.com/google/ai-abap-assistant-sample).
- SAP Help: Fiori Elements.
