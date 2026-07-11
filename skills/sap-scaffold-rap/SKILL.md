---
name: sap-scaffold-rap
description: |
  Sinh skeleton code RAP 3-layer (I -> R -> C) theo chuan SAP S/4HANA Cloud Public Edition, tu
  TECHNICAL_SPEC.md. Output la file abapGit import duoc vao Eclipse ADT.
  Dung sau khi co TECHNICAL_SPEC.md (skill sap-write-technical-spec) va pattern da chon la RAP
  (managed hoac unmanaged).
  KHONG dung cho pattern chi-read (dung sap-scaffold-cds) hoac class thuong don gian.
when_to_use: |
  "sinh RAP scaffold tu TECHNICAL_SPEC", "tao behavior managed cho X",
  "scaffold RAP unmanaged co custom save".
argument-hint: "[duong dan TECHNICAL_SPEC.md] [--managed|--unmanaged]"
model: sonnet
effort: high
tools: [Read, Write, Edit, Glob, Bash]
---

# SAP Scaffold RAP — TECHNICAL_SPEC.md → RAP 3-layer skeleton

## Khi nao dung

- ✅ Da co `TECHNICAL_SPEC.md` voi pattern = RAP Managed hoac Unmanaged.
- ✅ Can sinh file cho: table, CDS view 3-layer, behavior (R+C), behavior pool class, DCL, service.
- ❌ Pattern chi-read (khong CRUD) -> dung `sap-scaffold-cds`.

## Output — cau truc thu muc

`out/` la thu muc local per-user, KHONG nam trong repo (xem skill `sap-doc-to-md` de biet duong
dan day du):

```
out/<ticket>/src/
├── package.devc.xml
├── abapgit.xml
├── zdb/
│   └── ztb_<object>.tabl.xml
├── zcds/
│   ├── zi_<object>.ddls.asddls
│   ├── zr_<object>.ddls.asddls
│   ├── zc_<object>.ddls.asddls
│   └── zc_<object>.mde.asmd
├── zrap/
│   ├── zr_<object>.bdef.asbdef
│   ├── zc_<object>.bdef.asbdef
│   ├── zbp_<object>.clas.abap
│   ├── zbp_<object>.clas.testclasses.abap
│   ├── zbp_<object>.clas.locals_imp.abap
│   ├── zr_<object>.dcls.asdcls
│   ├── zc_<object>.dcls.asdcls
│   ├── zui_<object>_sd.srvd.srvd
│   └── zui_<object>_o4.srvb.srvb
└── zcl/
    └── zcl_<helper>.clas.abap  (neu can helper class)
```

Template co san (copy roi thay `<OBJECT>`/`<Object>`/`<Field...>`): `reference/templates/rap-boilerplate/managed/`.

## Quy trinh

### Buoc 1: Doc TECHNICAL_SPEC.md

Lay: danh sach object can tao, pseudo code behavior definition, test plan.

### Buoc 2-9: Generate tung layer — sinh xong 1 buoc, verify roi moi sang buoc sau

KHONG sinh het toan bo file roi moi activate 1 lan cuoi — loi activation thuong do object sau
phu thuoc object truoc (vd behavior can CDS I da activate duoc), dong het lai kho biet loi nam
o dau. Sinh + activate + xac nhan tung buoc theo thu tu:

| # | Sinh object | Activate + xac nhan (ADT) truoc khi qua buoc sau |
|---|---|---|
| 2 | Table (`ztb_*`) | Activate table, xac nhan field/key dung TECHNICAL_SPEC |
| 3 | CDS Interface (I) | Activate, xac nhan field expose dung tu VDM nguon |
| 4 | CDS Reuse/Consumption (R/C) | Activate, xac nhan association/annotation |
| 5 | Behavior Definition (R) | Activate — day la buoc hay fail nhat neu `numbering`/field control sai (xem Gotcha #2-3) |
| 6 | Behavior Implementation (ZBP) | Activate class, xac nhan method stub dung tu behavior |
| 7 | Behavior Definition (C, projection) | Activate — xac nhan alias/association khop projection (Gotcha #7) |
| 8 | DCL (R + C) | Activate, xac nhan rule/inheriting dung |
| 9 | Service Definition/Binding | Publish, xac nhan preview mo duoc trong Fiori Elements |

Neu 1 buoc activate fail: DUNG, doc dung thong bao loi ADT (khong doan), sua, activate lai —
roi moi sang buoc ke tiep. Ap dung skill `sap-verification-before-completion`: "activate duoc"
phai la ket qua that trong ADT, khong phai "code nhin dung syntax".

Dung template trong `reference/templates/rap-boilerplate/managed/` lam khung cho tung layer. Xem
chi tiet cu phap trong skill `sap-clean-code` (muc CDS View — 5 layer VDM) va vi du duoi day.

**R behavior (managed, bat buoc `strict ( 2 )`):**
```abap
managed implementation in class zbp_<object> unique;
strict ( 2 );

define behavior for ZR_<OBJECT> alias <Object>
implementation in class zbp_<object> unique
with draft
{
  field ( readonly ) Key, CreatedBy, CreatedAt;
  field ( numbering : managed ) Key;   // BAT BUOC neu Key la UUID tu sinh — xem Gotcha #3
  create; update; delete;
  validation validateHeader on save { field Supplier, Date; }
  action ( features : instance ) approve result [1] $self;
}
```

**C behavior (projection, chi re-expose):**
```abap
projection;
strict ( 2 );

define behavior for ZC_<OBJECT> alias <Object>
{
  use action approve;
}
```

**Tai sao tach R/C thanh 2 behavior?**

| Aspect | R behavior (managed) | C behavior (projection) |
|---|---|---|
| Muc dich | Business logic | UI / OData exposure |
| Action | Define + implement | Re-expose qua `use action` |
| CRUD | Define + implement | (khong khai bao — ke thua tu R) |
| Field control | `field ( readonly )`, `field ( mandatory )` | (ke thua tu R) |
| Mapping | `mapping for <table>` | (ke thua tu R) |
| Authorization (DCL) | Rule chinh (`pfcg_auth`) | `inheriting conditions from entity ZR` |

Loi: business logic o 1 cho (R) co the tai su dung cho nhieu C (Fiori, side-by-side, mobile...);
doi UI annotation o C khong anh huong business logic. Trong C, chi co the `use action`/`use
association` (khong the re-define hay override).

### Pattern PDF/file attachment (khi FS yeu cau in PDF/download file)

Dung `@Semantics.largeObject` — SAP-blessed, khong can CMIS/Object Store/custom Fiori code:

1. **Custom table generic** (tai su dung cho nhieu report) — vd `ZTB_<NS>_PDF_DRAF`:
   `object_id TYPE <key_type>` (PR/PO/GR... generic key), `report_id TYPE char20` (phan biet report
   nao), `attachment TYPE xstring`, `filename TYPE string`, `mimetype TYPE string`.
2. **Interface view (ZI) LEFT JOIN** voi table nay, annotate field attachment:
   ```abap
   left outer join ztb_<ns>_pdf_draf as pdf
     on header.Key = pdf.object_id and pdf.report_id = '<REPORT_ID>'
   ...
   @Semantics.largeObject: {
     mimeType: 'MimeType', fileName: 'FileName',
     acceptableMimeTypes: ['application/pdf'],
     contentDispositionPreference: #ATTACHMENT
   }
   pdf.attachment as Attachment,
   @Semantics.mimeType: true
   pdf.mimetype as MimeType,
   pdf.filename as FileName
   ```
3. **Action CreatePDF trong R behavior** + `mapping for` table generic (xem vi du o skill
   `sap-clean-code` muc mapping clause).
4. **C behavior re-expose**: `use action CreatePDF;`.
5. **Fiori tu dong**: hien button action tren identification facet; sau khi chay, field
   `Attachment` hien nhu file dinh kem, click de download/xem (tuy `contentDispositionPreference`).

Luu y: size limit xstring ~2GB nhung Fiori nen gioi han <100MB de responsive; authorization cho
attachment phai check field nhu cac field khac (Plant, PurchasingOrganization...); can nhieu
PDF/version cho 1 BO -> them field `version` vao table.

### Buoc 10: Bao user

Liet ke file da tao + xac nhan da activate tung buoc (Buoc 2-9). Nhac chay `sap-atc-review`, tao
transport request, chay `sap-unit-test`, roi `sap-finish-ticket` de dong ticket.

## Quy tac bat buoc

1. **`strict ( 2 )` bat buoc** trong moi behavior (R va C).
2. **`mapping for`** bat buoc khi dung table generic (ten CDS element khac ten cot DB).
3. **DCL R** co rule `pfcg_auth`, **DCL C** chi `inheriting`.
4. **Service binding** suffix `_O4` (UI OData V4) hoac `_O2` (UI OData V2); dung `_APIO4`/`ZAPI_*`
   rieng cho service machine-to-machine (xem skill `sap-clean-code`).
5. Moi file khong qua 200 dong.
6. Unit test cover moi action + validation (skill `sap-unit-test`).

## Gotcha BDEF/RAP (da xac minh qua thuc te — kiem tra truoc khi pull vao ADT)

### 1. Comment trong BDEF/DDL dung `//`, KHONG dung `"`

File `.bdef.asbdef`, `.ddls`, `.ddlx`, `.srvd` dung comment dong bang **`//`** (hoac `/* */`). Viet
`"` (kieu ABAP class) -> parser bao hang loat *"Unexpected character"* -> behavior "contains
errors" -> projection bao *"base entity does not define action"*. File **ABAP class** thi van dung
`"` binh thuong. `//` chi an toan **trong `{ }` body** — dung dat comment giua cac keyword header
cua behavior (giua `lock`/`authorization`/`etag`, truoc `{`), parser vo trang thai se bao loi lech
o dong KE TIEP. Check nhanh: `grep -nE '^\s*"' *.asbdef *.asddls *.asddlxs` phai rong.

### 2. Field control — sau `:` la operation, KHONG phai boolean

`field ( <feature> : <x> )` thi `<x>` bat buoc la `create` | `update` | `execute`, KHONG phai
boolean. `field ( mandatory : false ) X;` -> loi *'"create | execute | update" was expected, not
"false"'*. Field editable + optional = **mac dinh** (khong khai gi, chi can khong nam trong
`readonly`). Khong co cu phap `mandatory : false`. `field ( mandatory ) X;` luon bat buoc,
`field ( readonly : update ) X;` set duoc luc create, readonly khi update (dung cho key).

### 3. Managed BO key UUID phai khai `field ( numbering : managed )`

Key UUID (`SYSUUID_X16`) **KHONG tu sinh** mac dinh chi voi `field ( readonly )`. Phai them cau
rieng: `field ( numbering : managed ) <KeyField>;` de framework tu sinh UUID luc create. Thieu ->
key rong -> create/save fail (draft tao duoc nhung Activate loi key rong vao cot NOT NULL).
Composition: root khai cho key cha; entity con khai rieng cho key cua no.

### 4. Action tren entity con can `authorization master ( instance )` + handler rieng

Action (bound) tren entity con ma con khai `authorization dependent by _Parent` -> runtime dump
`CX_RAP_HANDLER_NOT_IMPLEMENTED` (method INSTANCE_AUTHORIZATION) khi bam action — vi `dependent`
chi cover CRUD chay qua parent, KHONG cover action rieng cua con. Fix: doi entity con sang
`authorization master ( instance )` (lock/etag van co the `dependent by _Parent`), va implement
`get_instance_authorizations FOR INSTANCE AUTHORIZATION` trong local handler rieng cho con (body
rong = grant full).

### 5. Custom query provider phai goi `get_paging` + tu ap filter/sort

Class implement `IF_RAP_QUERY_PROVIDER~select` bat buoc goi `io_request->get_paging( )` va ap
offset/page_size, khong thi runtime bao *"Query not fully covered ... get_paging missing"*. Client
gui sort -> cung phai goi `get_sort_elements` va tu SORT (framework khong sort ho). Provider **tu
ap filter**: framework chi dua filter qua `get_filter`, KHONG tu filter lai `set_data`. Doc filter
qua `get_filter( )->get_as_ranges( )` — component `range` la internal table truc tiep, KHONG phai
`REF TO data`, dung field-symbol (`type index table`), khong `->range->*`. `set_data` bind theo
**ten component chinh xac** — ten khac case/underscore so voi element CDS -> field hien trong
nhung rong.

### 6. Post chung tu SAP can so ngay -> dung OData API, KHONG EML-in-handler

BO unmanaged wrap BAPI/API chuan gan so **LATE** (save phase). EML `MODIFY ENTITIES ... CREATE`
trong handler chi tra `%pid`, KHONG co so that; `COMMIT ENTITIES` bi **cam** trong behavior class
-> khong lay so dong bo duoc. Neu can so ngay (synchronous): goi **OData API qua HTTP client**
(khong phai `COMMIT ENTITIES`, la 1 LUW rieng tra so ngay — can Communication Arrangement
outbound), hoac dung background job + `COMMIT ENTITIES ... RESPONSE OF` o class thuong (async).

### 7. Gotcha activation trong ADT (chi lo ra khi pull + activate, khong thay khi doc code)

- **Draft table field = ten ELEMENT cua CDS entity, KHONG phai ten cot DB.** Active table di qua
  `mapping for` nen cot DB co the khac ten, nhung draft table KHONG qua mapping -> field phai
  trung element name. Sai -> draft khong khop entity, activate fail.
- **Projection behavior/metadata dung ALIAS cua projection**, khong phai ten composition goc. Neu
  projection CDS expose `_Child as data : redirected to composition child ...` thi bdef projection
  viet `use association data { ... }` va MDE facet `targetElement: 'data'` — KHONG ten association
  goc. Sai -> "no association".
- **Kiem tra data element co duoc phep trong ABAP Cloud khong** truoc khi dung cho field ngay/gio —
  1 so data element chuan (vd kieu TIME co dinh dang cu) khong duoc phep, dung built-in `t` (time)
  / `d` (date) trong TYPES/method signature thay the.
- **Unmanaged saver chi co action (khong CRUD): redefine `save` (rong), KHONG `save_modified`.**
  `save_modified` chi hop le khi co create/update/delete; saver rong khong redefine gi -> loi
  "method SAVE must be redefined". Dung: redefine `save` voi impl rong.
- **`TABLE FOR DELETE <entity>` chi co KEY** (+ `%tky`/`%is_draft`), KHONG co business field.
  `APPEND VALUE #( Id = ... FieldX = ... )` -> loi "No component FIELDX". Chi set key.
- **HTTP client Cloud**: set body bang `set_binary( i_data = xstr )` (KHONG `set_binary_body`).
- **Timestamp field: KHONG doan kieu built-in — verify truoc khi CONVERT.** ADT rat strict ve kieu
  timestamp; doan sai -> "type cannot be converted"/"not type-compatible". Kiem tra kieu that (F2
  data element trong ADT, hoac `SELECT ... INTO @DATA(...)` de lay kieu tu view) roi moi chon cau
  CONVERT dung (`utclong` vs `timestamp`/`timestampl` co cu phap CONVERT khac nhau, dac biet vi
  tri `TIME ZONE` trong cau lenh).

## Reference

- `reference/templates/rap-boilerplate/managed/` — template 3-layer day du.
- Skill `sap-clean-code` — quy uoc dat ten, VDM layer.
- Skill `sap-extensibility` — decision tree managed/unmanaged/side-by-side.
- Buoc tiep theo: `sap-atc-review`, `sap-unit-test`, `sap-finish-ticket`.
- Loi runtime kho hieu sau khi activate -> skill `sap-systematic-debugging`.
