# RAP Projection Pattern — `projection;` + `use action`

Khi có 3-layer CDS (ZI → ZR → ZC), behavior cũng tách thành 2 file:
- **ZR behavior** (managed/unmanaged): business logic, action implementation, mapping.
- **ZC behavior** (projection): chỉ re-expose action và field từ R.

## Pattern chuẩn

### R behavior (managed) — business logic ở đây

```abap
managed implementation in class zbp_purchaseorder unique;
strict ( 2 );                            // BẮT BUỘC

define behavior for ZR_PURCHASEORDER alias PurchaseOrder
implementation in class zbp_purchaseorder unique
{
  field ( readonly ) PurchaseRequisition, CreatedBy, CreatedAt;

  // CRUD — managed
  create;
  update;
  delete;

  // Validation
  validation validateSupplier on save { field Supplier; }

  // Action (logic thật ở đây, impl trong ZBP)
  action CreatePDF result [1..*] $self;

  // ⬇ BẮT BUỘC khi dùng table generic (mapping cho PDF draft table)
  mapping for ztb_scm_pdf_draf
    {
      PurchaseRequisition = object_id;
      Attachment          = attachment;
      MimeType            = Mimetype;
      FileName            = Filename;
    }
}
```

### C behavior (projection) — chỉ re-expose

```abap
projection;
strict ( 2 );                            // BẮT BUỘC

define behavior for ZC_PURCHASEORDER alias PurchaseOrder
{
  // Không CRUD ở đây. Chỉ re-expose:
  use action CreatePDF;                   // Re-expose action từ R
}
```

## Tại sao tách thành 2 behavior?

| Aspect | R behavior (managed) | C behavior (projection) |
|--------|----------------------|--------------------------|
| Mục đích | Business logic | UI / OData exposure |
| Action | Define + implement | Re-expose qua `use action` |
| CRUD | Define + implement | (không khai báo) |
| Field control | `field ( readonly )`, `field ( mandatory )` | (kế thừa từ R) |
| Mapping | `mapping for <table>` | (kế thừa từ R) |
| Authorization (DCL) | Rule chính | `inheriting conditions from entity ZR` |
| Service binding expose | (không, chỉ internal) | (expose qua ZUI_*) |

**Lợi**:
- Business logic ở 1 chỗ (R), có thể tái sử dụng cho nhiều C (Fiori, side-by-side, mobile...).
- Thay đổi UI annotation (ở C) không ảnh hưởng business logic.
- Multiple consumption views có thể re-use cùng R action.

## `use action` chi tiết

Trong C behavior, có thể:
- `use action ActionName;` — re-expose action không thay đổi.
- `use association _AssociationName;` — re-expose association.
- Không thể re-define hoặc override.

## Strict mode

```abap
managed implementation in class zbp_<zr> unique;
strict ( 2 );
```

`strict ( 2 )`:
- Bắt buộc type-safe.
- Không implicit conversion.
- Bắt buộc khai báo tất cả field dùng trong action/validation.
- Bắt buộc `mapping for` khi CDS name ≠ DB name.

`strict ( 1 )` — ít strict hơn, deprecated.
`strict ( 2 )` — chuẩn SAP khuyến khích.

## Khi nào KHÔNG dùng projection

- Single layer CDS (chỉ I + ZC, không có ZR) → dùng managed/unmanaged trực tiếp trên ZC.
- Legacy migration → giữ pattern cũ.

## Reference

- SAP doc: https://help.sap.com/docs/abap-cloud/abap-rap/projection-behavior-definition
- SAP doc: https://help.sap.com/docs/abap-cloud/abap-rap/managed-scenario
- Ví dụ thật: `examples/ITC_SCM_PO_V101/src/zrap/zc_purchaseorder.bdef.asbdef`
