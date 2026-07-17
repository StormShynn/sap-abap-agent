---
name: abap-rap-cloud
description: Knowledge note tổng hợp từ `anfisc/abap-rap-introduction` và `google/ai-abap-assistant-sample` — RAP (ABAP RESTful Application Programming) trên ABAP Cloud, dùng để tra cứu nhanh. Đây là knowledge note (không phải instruction skill), đồng nhất cấu trúc với `reference/modules/<module>-cloud/SKILL.md`.
effort: low
model: haiku
---

# ABAP RAP — Cloud Knowledge Note

Module con của plugin, dùng khi contributor cần tra nhanh khái niệm RAP mà không cần scaffold thật.
Không thay thế các skill scaffold thật (`sap-scaffold-rap`, `sap-rap-events`).

## 1. RAP là gì?

RAP = **ABAP RESTful Application Programming**. Là framework chính thức của SAP để xây dựng
business object và expose chúng ra OData V4 trên ABAP Cloud (S/4HANA Cloud, Steampunk, BTP
ABAP Environment).

## 2. Lớp kiến trúc (3 layer)

```
┌────────────────────────────────────────┐
│ Service Binding (OData V4 / Fiori)     │  ← Service Definition + Binding
├────────────────────────────────────────┤
│ Behavior Implementation               │  ← Handler class (LMT/Early numbering)
├────────────────────────────────────────┤
│ Behavior Definition + CDS View         │  ← Managed / Unmanaged / Projection
└────────────────────────────────────────┘
```

- **Layer 1 — CDS View**: Data model (interface view `ZI_*`, consumption view `ZC_*`).
- **Layer 2 — Behavior Definition (BDEF)**: định nghĩa operation (CRUD, action, determination,
  validation, side effect) + control (authorization, locking).
- **Layer 3 — Behavior Implementation**: class `ZBP_*` chứa handler method thật.
- **Service layer**: Service Definition `ZSD_*` + Service Binding `ZUI_*`/`ZAPI_*` để expose.

## 3. So sánh với các công nghệ lân cận

| Tiêu chí                 | RAP (ABAP Cloud)     | CAP (Node.js/Java)         | Legacy BAPI/RFC |
|--------------------------|----------------------|----------------------------|------------------|
| Run on S/4HANA Cloud     | ✅                   | ✅ (qua side-by-side)      | ❌ (released hạn chế) |
| Wizard / Generator       | Eclipse + ADT + BOPF | `@sap/cds` CLI             | SE37 / SE11      |
| OData V4 native          | ✅                   | ✅                         | ❌ (OData V2 chủ yếu) |
| Released object trên Public Cloud | ✅              | ✅                         | ⚠️ Theo từng BAPI |
| Locking + Draft          | Built-in             | Custom                     | Không            |
| Authorization             | CDS DCL              | `@requires`                | AUTH-CHECK       |

## 4. Skeleton code mẫu (Hello World RAP)

```abap
" CDS — ZI_HELLOWORLD (Interface View)
@AbapCatalog.sqlViewName: 'ZHELLOWORLD'
@AccessControl.authorizationCheck: #NOT_REQUIRED
define view ZI_HELLOWORLD as select from t100
{
  key sprsl as Language,
  key arbgb as Area,
  key msgnr as Number,
      text  as MessageText
}
```

```abap
" BDEF — ZI_HELLOWORLD (Behavior Definition)
managed; // implementation in class ZBP_I_HELLOWORLD

define behavior for ZI_HELLOWORLD alias HelloWorld
{
  create;
  update;
  delete;
}
```

```abap
" Behavior Implementation
class ZBP_I_HELLOWORLD definition public abstract
                                final behavior for ZI_HELLOWORLD.

  " create / update / delete / read handlers có thể để trống (managed sẽ tự xử lý)
endclass.
```

```abap
" Service Definition
define service ZSD_HELLOWORLD {
  expose ZI_HELLOWORLD as HelloWorld;
}
```

Service Binding `ZUI_HELLOWORLD_O4` (OData V4) sau đó activate và preview qua ADT.

## 5. Naming convention (tham khảo `sap-clean-code`)

| Object            | Pattern    | Ví dụ               |
|-------------------|------------|---------------------|
| Interface view    | `ZI_*`     | `ZI_HELLOWORLD`     |
| Consumption view  | `ZC_*`     | `ZC_HELLOWORLD`     |
| Behavior def      | `ZI_*`     | `ZI_HELLOWORLD`     |
| Behavior impl     | `ZBP_*`    | `ZBP_I_HELLOWORLD`  |
| Service def       | `ZSD_*`    | `ZSD_HELLOWORLD`    |
| Service binding   | `ZUI_*`/`ZAPI_*` | `ZUI_HELLOWORLD_O4` |

## 6. Anti-pattern

- ⚠️ Dùng `unmanaged` khi không cần thiết — `managed` đủ cho hầu hết use case CRUD.
- ⚠️ Logic nghiệp vụ trong CDS view — chuyển vào Behavior handler.
- ⚠️ Bỏ qua `draft` khi cần editing experience — enable draft để có Fiori UI chuẩn.
- ⚠️ Không viết ABAP Unit test cho handler — bắt buộc xem `sap-unit-test`.

## 7. Liên kết với các skill khác

- **Scaffold thật**: `sap-scaffold-rap` (sinh skeleton 3 layer từ TECHNICAL_SPEC.md).
- **Sự kiện RAP**: `sap-rap-events` (BEFORE/AFTER, determination, validation).
- **Review code**: `sap-atc-review` → mục RAG Review Pattern (vừa bổ sung) dùng bảng này để
  check.
- **Released class cho RAP runtime**: `sap-released-classes` mục "RAP Runtime".
- **Unit test**: `sap-unit-test`.
- **Cloud migration**: `sap-cloud-migration`.

## 8. Nguồn tham khảo

- [`anfisc/abap-rap-introduction`](https://github.com/anfisc/abap-rap-introduction) — ghi chú cá
  nhân + learning path theo tài liệu RAP chính thức.
- [`google/ai-abap-assistant-sample`](https://github.com/google/ai-abap-assistant-sample) — Genie
  for SAP (AI-assisted codegen cho RAP).
- [`microsoft/aisdkforsapabap`](https://github.com/microsoft/aisdkforsapabap) — AI SDK cho ABAP.
- SAP Help: RESTful Application Programming.
