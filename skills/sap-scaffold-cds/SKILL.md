---
name: sap-scaffold-cds
description: |
  Sinh CDS view skeleton (interface, consumption, metadata extension) tu field list trong
  INTAKE.md/TECHNICAL_SPEC.md — dung cho pattern chi-read (bao cao, list/detail khong save).
  Dung khi TECHNICAL_SPEC.md da chon pattern "3-layer CDS" (khong RAP/CRUD).
  KHONG dung khi can CRUD (dung sap-scaffold-rap).
when_to_use: |
  "sinh CDS view tu TECHNICAL_SPEC nay", "tao interface view read-only cho bao cao",
  "scaffold CDS 3-layer cho X".
argument-hint: "[duong dan TECHNICAL_SPEC.md hoac field list]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Glob]
---

# SAP Scaffold CDS — Field list → CDS view skeleton (read-only)

## Khi nao dung

- ✅ Bao cao in (PDF/Word) — chi can CDS view + ABAP class.
- ✅ List/Detail don gian, khong save — CDS + Service Definition expose OData.
- ✅ Bao cao phan tich — CDS view analytical.
- ❌ Can CRUD (create/update/delete) — dung `sap-scaffold-rap`.

## Output

- `zi_<object>.ddls.asddls` — interface view (dat len standard SAP CDS neu co).
- `zr_<object>.ddls.asddls` — consumption/reuse view (cho OData/Fiori).
- `zr_<object>.mde.asmd` — metadata extension (Fiori annotation).

Dat trong `out/<ticket>/src/zcds/` (`out/` la thu muc local per-user, KHONG nam trong repo — xem
skill `sap-doc-to-md` de biet duong dan day du).

## Quy trinh

### Buoc 0: Xac dinh CDS base (released)

Neu build tren du lieu standard SAP (khong phai `ztb_*` custom):
1. Tim CDS base theo phan he — hoi agent consultant tuong ung (vd `sap-mm-consultant-cloud`) hoac
   `sap-docs-researcher` / skill `sap-cds-kb`. Uu tien `I_*` (VDM interface) da released, khop
   nghiep vu + field FS yeu cau.
2. **Verify released** cho dung version Cloud dang dung (catalog KHONG tu noi released) — dung
   `sap-docs-researcher` hoac View Browser trong Eclipse ADT.
3. Neu chua released hoac thieu field -> tim nguon chinh thong (`api.sap.com`/`help.sap.com`).
   `ZI_*` cua ta `select from` view base do; KHONG tu bia ten view standard.

### Buoc 1: Tao interface view (ZI_*)

```abap
@AbapCatalog: { sqlViewName: 'ZI_<OBJECT>', compiler.compareFilter: true }
@AccessControl: { authorizationCheck: #CHECK }
@EndUserText: { label: '<Object> Interface View' }
define view ZI_<OBJECT>
  as select from ztb_<object>
{
  key <key_field>  as <KeyField>,
      <field_1>    as <Field1>,
      ...
}
```

### Buoc 2: Tao consumption/reuse view (ZR_*) — cho Fiori

```abap
@AbapCatalog: { sqlViewName: 'ZR_<OBJECT>', compiler.compareFilter: true }
@AccessControl: { authorizationCheck: #CHECK }
@EndUserText: { label: '<Object>' }
@UI: {
  headerInfo: {
    typeName: '<Object>', typeNamePlural: '<Objects>',
    title: { type: #STANDARD, value: '<KeyField>' }
  }
}
define root view ZR_<OBJECT>
  as select from ZI_<OBJECT>
{
  key <KeyField>, <Field1>, <Field2>
}
```

### Buoc 3: Tao metadata extension (MDE) — cho Fiori Elements

⚠️ **Cu phap ABAP Cloud** (S/4HANA Cloud Public) dung `@Metadata.layer` + `annotate entity` —
KHONG dung `metadata layer` / `annotate view` (cu phap cu, se activate fail):

```abap
@Metadata.layer: #CORE
annotate entity ZR_<OBJECT> with
{
  @UI: { lineItem: [ { position: 10, importance: #HIGH, label: '<Field1>' } ] }
  <Field1>;
}
```

- `@Metadata.layer` (co `@`, dong dau) — layer hop le: `#CORE` (object du an tu tao), `#CUSTOMER`,
  `#PARTNER`, `#INDUSTRY`, `#LOCALIZATION`.
- **Scope annotation trong MDE** (hay vap): annotation **cap ENTITY** phai dat **NGOAI `{}`**, giua
  `@Metadata.layer` va `annotate entity`. Dat trong `{}` se bi gan vao element ngay sau no -> activate
  fail *"Annotation '...' used at wrong position (wrong scope)"*. Entity-level: `@UI.presentationVariant`,
  `@UI.headerInfo`, `@UI.selectionPresentationVariant`, `@UI.chart`. Element-level (trong `{}`, gan
  field): `@UI.lineItem`, `@UI.identification`, `@UI.selectionField`, `@UI.fieldGroup`, `@UI.dataPoint`.
  Ngoai le: `@UI.facet` (entity-level nhung theo quy uoc dat o field key dau tien trong `{}` — chap nhan).

### Buoc 4: (Optional) Service definition — neu expose qua OData

```abap
define service ZUI_<OBJECT>_SD {
  expose ZR_<OBJECT> as <Object>;
}
```

## Annotation tham khao nhanh

| Annotation | Muc dich |
|---|---|
| `@UI.lineItem` | Hien field trong List Report — **bat buoc** neu muon field xuat hien trong list |
| `@UI.fieldGroup` + `@UI.facet` | Hien field trong Object Page (group + facet tro toi group) |
| `@UI.headerInfo` (entity-level) | Title/description cho header cua Object Page |
| `@UI.selectionField` | Field xuat hien o filter bar |
| `@Search.defaultSearchElement: true` | Field duoc search full-text mac dinh |
| `@Consumption.filter.mandatory: true` | Filter bat buoc phai nhap truoc khi list load |
| `@Semantics.amount.currencyCode` / `@Semantics.quantity.unitOfMeasure` | Gan field tien/so luong voi field don vi tuong ung |
| `@ObjectModel.createEnabled/updateEnabled/deleteEnabled` | Bat CRUD tren consumption view (RAP) |

## Gotcha activate CDS (da xac minh — kiem tra truoc khi pull)

1. **`@Semantics.quantity`/`amount` — KHONG annotate field don vi trong `view entity`.** Annotate
   field **gia tri** (`@Semantics.amount.currencyCode: '<CurrencyField>'`), de field don vi/tien te
   trong. Dung `@Semantics.unitOfMeasure: true`/`@Semantics.currencyCode: true` truc tiep tren field
   don vi trong `define view entity` -> loi *"Semantics.unitOfMeasure is not allowed in view
   entities"*. Neu view bat `@Metadata.ignorePropagatedAnnotations: true`, phai khai lai annotation
   nay o **moi layer** bat ignore (ZI, ZR).
2. **CAST sang NUMC — literal nguon phai dai DUNG bang target.** `cast( '0' as abap.numc( 10 ) )`
   -> loi *"lengths must match"*. Dung: `cast( '0000000000' as abap.numc( 10 ) )`. `char`/`dec`/`cuky`
   cast tu `''`/`0` thi OK (tu pad duoc), chi NUMC bi chat length — ap dung ca khi CAST lan khi so
   sanh 2 field NUMC khac do dai trong `WHERE`.
3. **Association scalar projection phai to-one; to-many dung JOIN.** `assoc.field as X` chi hop le
   khi association la `[1..1]`/`[0..1]`; to-many (`[0..*]`) phai dung `LEFT OUTER JOIN` trong FROM.
   ON-condition cua association dung `$projection.<field>` ma field do lai den tu association khac
   -> loi "cannot be used locally" — phai lay field qua chain association base-resolvable.
4. **Parameterized view (`with parameters`) chi JOIN duoc, KHONG association.**
   `association ... to <ParamView>(p:...)` -> loi cu phap. Dung
   `left/inner join ZI_VIEW(p_param: 'X') as _alias on _alias.Key = Item.Key` (ON dung alias data
   source, khong `$projection`; alias nay khong dua vao "Exposed associations").
5. **`GROUP BY` khong nhan bieu thuc `cast(...)`/`concat(...)` truc tiep** — parser bao "Unexpected
   keyword". Group by field goc, de bieu thuc derive o phan SELECT (van hop le vi la ham thuan tren
   field da group).
6. **Value help/association tro view giao dich nang co field dung conversion exit dac biet** (vd
   ty gia) co the gay dump `CX_SADL_GW_V4_MODEL_EXCEPTION` khi **publish service binding** (khong lo
   luc activate CDS). Value help chi nen tro **master/config view** (Company Code, Plant, Sales
   Organization, Business Partner...); giu report phang — materialize field thanh cot scalar thay vi
   expose association toi view giao dich nang.

## Reference

- Template: `reference/templates/rap-boilerplate/managed/zi_object.ddls.asddls`,
  `zr_object.ddls.asddls`, `zr_object.mde.asmd` (bo qua phan behavior neu khong can CRUD).
- Naming: skill `sap-clean-code`.
- Buoc tiep theo: `sap-atc-review`.
