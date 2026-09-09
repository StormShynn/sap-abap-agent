# @Semantics.largeObject — Pattern lưu file (PDF/image) trong CDS

Annotation `@Semantics.largeObject` cho phép CDS view expose binary content (PDF, image, file đính kèm) một cách **chuẩn SAP** mà không cần CMIS, Object Store, hay custom Fiori code.

## Pattern tổng quan

```
┌────────────────────────────────────────────────────────┐
│ Custom table (generic, reuse cho nhiều report)        │
│   ZTB_<NAMESPACE>_PDF_DRAF                             │
│   ┌────────────────────────────────────────┐           │
│   │ object_id   TYPE <key_type>             │ ← generic key│
│   │ report_id   TYPE char20                 │ ← 'ZSCM_PR' │
│   │ attachment  TYPE xstring (rawstring)     │ ← PDF binary│
│   │ filename    TYPE string                 │             │
│   │ mimetype    TYPE string                 │             │
│   └────────────────────────────────────────┘           │
└────────────────────────────────────────────────────────┘
                          ↑ LEFT JOIN
┌────────────────────────────────────────────────────────┐
│ Interface view (ZI)                                     │
│   @Semantics.largeObject: {                            │
│     mimeType: 'MimeType',                              │
│     fileName: 'FileName',                              │
│     acceptableMimeTypes: ['application/pdf', ...],     │
│     contentDispositionPreference: #ATTACHMENT          │
│   }                                                    │
│   pdf.attachment as Attachment,                        │
└────────────────────────────────────────────────────────┘
                          ↑ projection
┌────────────────────────────────────────────────────────┐
│ Reuse view (ZR) → Consumption view (ZC)               │
│   → Service binding (OData V4)                         │
│   → Fiori Elements tự render attachment button         │
└────────────────────────────────────────────────────────┘
```

## Bước 1: Tạo custom table

```abap
" abapGit source: ztb_scm_pdf_draf.tabl.xml
" Table name: ZTB_SCM_PDF_DRAF
" Fields:
"   OBJECT_ID   TYPE CHAR20  (generic: PR/PO/GR/...)
"   REPORT_ID   TYPE CHAR20  ('ZSCM_PR', 'ZSCM_PO', ...)
"   ATTACHMENT  TYPE RAWSTRING (max 2GB binary)
"   FILENAME    TYPE STRING
"   MIMETYPE    TYPE STRING
"   CREATED_BY  TYPE SYUNAME
"   CREATED_AT  TYPE TIMESTAMP
```

Tại sao **generic** (object_id, report_id) thay vì (pr_number, po_number):
- 1 table dùng cho nhiều report → giảm số table, dễ maintain.
- Logic insert/select giống nhau, dùng `report_id` để filter.

## Bước 2: JOIN trong Interface view (ZI)

```abap
define view entity ZSCM_I_PR
  as select from ZSCM_I_PR_HEADER as header
    left outer join ztb_scm_pdf_draf as pdf 
      on  header.PurchaseRequisition = pdf.object_id
      and pdf.report_id              = 'ZSCM_PR'
{
  key header.PurchaseRequisition,
      ...
      
      @Semantics.largeObject: { 
        mimeType: 'MimeType', 
        fileName: 'FileName',
        acceptableMimeTypes: ['image/png', 'image/jpeg', 'application/pdf'],
        contentDispositionPreference: #ATTACHMENT 
      }
      pdf.attachment as Attachment,
      
      @Semantics.mimeType: true
      pdf.mimetype    as MimeType,
      
      pdf.filename    as FileName
}
```

**Annotation quan trọng**:
- `@Semantics.largeObject` trên field binary (attachment).
- `@Semantics.mimeType: true` trên field mime type.
- `contentDispositionPreference: #ATTACHMENT` → download, không inline view.

## Bước 3: Project lên R và C

```abap
" ZR (reuse) — chỉ cần chọn field, không annotation thêm
define view entity ZSCM_R_PR
  as select from ZSCM_I_PR
{
  key ZSCM_I_PR.PurchaseRequisition,
      ZSCM_I_PR.Attachment,                    -- ⬅ kế thừa annotation
      ZSCM_I_PR.MimeType,
      ZSCM_I_PR.FileName
}

" ZC (consumption) — projection on ZR
define root view entity ZSCM_C_PR
  as projection on ZSCM_R_PR
{
  key PurchaseRequisition,
      Attachment,
      MimeType,
      FileName
}
```

## Bước 4: Behavior action

```abap
" ZR behavior (managed)
managed implementation in class zbp_scm_r_pr unique;
strict ( 2 );

define behavior for ZSCM_R_PR {
  field ( readonly ) PurchaseRequisition;
  action CreatePDF result [1..*] $self;
  mapping for ztb_scm_pdf_draf
    {
      PurchaseRequisition = object_id;
      Attachment          = attachment;
      MimeType            = Mimetype;
      FileName            = Filename;
    }
}

" ZC behavior (projection)
projection;
strict ( 2 );

define behavior for ZSCM_C_PR {
  use action CreatePDF;
}
```

## Bước 5: Action impl (ZBP)

```abap
CLASS zbp_scm_r_pr DEFINITION PUBLIC ABSTRACT BEHAVIOR FOR ZSCM_R_PR.
  PUBLIC SECTION.
    METHODS createpdf FOR ACTION
      IMPORTING keys      FOR ZSCM_R_PR~CreatePDF
      RESULT    DATA(ls_pdf) TYPE ZSCM_R_PR.
ENDCLASS.

CLASS zbp_scm_r_pr IMPLEMENTATION.
  METHOD createpdf.
    " 1. For each key, generate PDF
    READ ENTITIES OF ZSCM_R_PR IN LOCAL MODE
      ENTITY ZSCM_R_PR ALL FIELDS WITH CORRESPONDING #( keys )
      RESULT DATA(lt_records).

    LOOP AT lt_records INTO DATA(ls_record).
      " 2. Generate PDF via ADS / Adobe Form
      DATA(lv_pdf) = zcl_pdf_helper=>generate_pdf( ls_record ).
      
      " 3. Update entity with attachment (will be saved to ZTB_SCM_PDF_DRAF)
      MODIFY ENTITIES OF ZSCM_R_PR IN LOCAL MODE
        ENTITY ZSCM_R_PR
        UPDATE
          FIELDS ( Attachment MimeType FileName )
          WITH VALUE #( ( 
            %tky = ls_record-%tky
            Attachment = lv_pdf
            MimeType   = 'application/pdf'
            FileName   = |PR_{ ls_record-PurchaseRequisition }.pdf|
          ) )
        REPORTED DATA(ls_reported).
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.
```

## Bước 6: Fiori UI

Trong metadata extension (ZC.MDE):
```abap
annotate view ZC_PURCHASEORDER with
{
  @UI.identification: [
    { position: 10, label: 'Purchase Requisition' },
    { type: #FOR_ACTION, dataAction: 'createPDF', label: 'Create PDF' }
  ]
  PurchaseRequisition;
  
  @UI.identification: [
    { position: 100, label: 'PDF Attachment' }
  ]
  Attachment;
}
```

**Fiori tự động**:
- Hiển thị button "Create PDF" trên identification facet.
- Sau khi action chạy, field `Attachment` hiển thị như file đính kèm.
- User click → download PDF hoặc open in viewer (tuỳ `contentDispositionPreference`).

## Ưu điểm so với CMIS/URL pattern

| Aspect | Table + @Semantics.largeObject | CMIS/Object Store |
|--------|--------------------------------|---------------------|
| Setup | Tạo 1 table | Cài CMIS / config Object Store |
| Transaction | Cùng BO | Riêng |
| Rollback | Tự động với BO | Thủ công |
| Fiori | Tự render | Custom code |
| Performance | Cùng DB | Network call |
| Cleanup | Tự xoá khi xoá BO | Phải có retention policy |
| Reuse | 1 table cho nhiều report | Mỗi report 1 storage |
| SAP-blessed | ✅ Native | ⚠ Custom |

## Lưu ý quan trọng

1. **Mime types**: chỉ định rõ `acceptableMimeTypes` để Fiori filter.
2. **Size limit**: xstring cho phép ~2GB, nhưng Fiori thường giới hạn < 100MB để responsive.
3. **Authorization**: DCL cho attachment phải check `Plant`, `PurchasingOrganization` như các field khác.
4. **Multiple PDF cho 1 BO**: nếu cần (vd 1 PR có nhiều PDF version) → thêm field `version` vào table.

## Reference

- SAP doc: https://help.sap.com/docs/abap-cloud/abap-rap/semantics-annotation
- SAP doc CDS: https://help.sap.com/docs/abap-cloud/abap-rap/semantics-largeobject
- Ví dụ thật: `examples/ITC_SCM_PO_V101/src/zcds/zi_purchaseorder.ddls.asddls`
