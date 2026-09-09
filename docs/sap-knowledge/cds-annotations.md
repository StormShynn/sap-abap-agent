# CDS Annotations cho Fiori Elements & OData

Fiori Elements đọc annotation từ CDS view (consumption view + metadata extension)
để tự generate UI: List Report, Object Page, Facets, Field groups, v.v.

## Các annotation phổ biến

### @UI — cho UI layout

```abap
@UI: {
  headerInfo: {
    typeName: 'Purchase Order',
    typeNamePlural: 'Purchase Orders',
    title: { type: #STANDARD, value: 'PurchaseOrderNo' },
    description: { type: #STANDARD, value: 'SupplierName' }
  }
}
define root view ZR_PURCHASEORDER
  as select from ZI_PURCHASEORDER
{
  // Line item (list view)
  @UI: { lineItem: [ { position: 10, importance: #HIGH, label: 'PO Number' } ] }
  key PurchaseOrderNo,
  // Field group
  @UI: { fieldGroup: [ { position: 10, qualifier: 'GeneralData', label: 'PO Date' } ] }
  PurchaseOrderDate,
  // Facet (object page)
  @UI: { facet: [ { id: 'GeneralData', label: 'General', type: #FIELDGROUP_REFERENCE, position: 10, targetQualifier: 'GeneralData' } ] }
  ...
}
```

### @Search — cho search field

```abap
@Search: { defaultSearchElement: true, fuzzinessThreshold: 0.8 }
PurchaseOrderNo,
@Search: { defaultSearchElement: true }
Supplier,
```

### @OData — cho OData exposure

```abap
@OData: { entitySet.name: 'PurchaseOrder', publishingEnabled: true }
define root view ZR_PURCHASEORDER as ...
```

### @Consumption — cho filter

```abap
@Consumption: { filter: { mandatory: true, selectionField: { position: 10 } } }
key PurchaseOrderNo,
```

### @ObjectModel — cho CRUD

```abap
@ObjectModel: {
  semanticKey: [ 'PurchaseOrderNo' ],
  createEnabled: true,
  updateEnabled: true,
  deleteEnabled: true
}
```

## MDE (Metadata Extension) — tách annotation khỏi view

⚠️ **Cú pháp ABAP Cloud mới** (S/4HANA Cloud Public) — dùng annotation `@Metadata.layer` và
`annotate entity`, KHÔNG dùng `metadata layer` / `annotate view` (cú pháp cũ, activate fail):

```abap
@Metadata.layer: #CORE
annotate entity ZC_PURCHASEORDER with
{
  @UI: { lineItem: [ { position: 10, label: 'PO Number' } ] }
  PurchaseOrderNo;
  // ...
}
```

File riêng: `zc_purchaseorder.mde.asmd`.

- `@Metadata.layer` (có `@`, dòng đầu) — layer hợp lệ: `#CORE` (object dự án mình tạo),
  `#CUSTOMER`, `#PARTNER`, `#INDUSTRY`, `#LOCALIZATION`. `metadata layer` (không `@`) = sai/cũ → fail.
- `annotate entity` cho CDS view entity / custom entity; `annotate view` là cú pháp cũ.
- ⚠️ File mẫu cũ trong repo (`source code/ACME_FI_GL_ZGL07_V10/.../zc_gl07_voucher.mde.asmd`) còn
  dùng `metadata layer` sai — **đừng copy theo**.
- 🔴 **Scope annotation trong MDE (hay vấp — ZCO10 2026-07-07)**: annotation **cấp ENTITY** phải đặt
  **NGOÀI `{}`**, giữa `@Metadata.layer` và `annotate entity`. Đặt trong `{}` sẽ bị gán vào element
  ngay sau nó → activate fail `Annotation '...' used at wrong position (wrong scope)`. Entity-level:
  `@UI.presentationVariant` (sortOrder/groupBy/visualizations), `@UI.headerInfo`,
  `@UI.selectionPresentationVariant`, `@UI.chart`. Element-level (trong `{}`, gắn field):
  `@UI.lineItem`, `@UI.identification`, `@UI.selectionField`, `@UI.fieldGroup`, `@UI.dataPoint`.
  Ngoại lệ: **`@UI.facet`** (entity-level) theo quy ước đặt ở field key đầu tiên trong `{}` — chấp nhận,
  không lỗi. Mẫu đúng:
  ```abap
  @Metadata.layer: #CORE
  @UI.presentationVariant: [ { sortOrder: [ { by: 'Seq', direction: #ASC } ],
                               groupBy: [ 'Field1' ], visualizations: [ { type: #AS_LINEITEM } ] } ]
  annotate entity ZC_X with
  {
    @UI.facet: [ ... ]          // facet o day OK
    @UI.lineItem: [ ... ]
    Field1;
  }
  ```

## Field control trong behavior

Trong behavior definition, control field bằng:

```abap
field ( readonly ) CreatedBy, CreatedAt, ChangedBy, ChangedAt;
field ( mandatory ) Supplier, PurchaseOrderDate;
```

## Quy tắc annotation

1. **Tất cả field trong list view cần `@UI.lineItem`** — không có = không hiển thị.
2. **Tất cả field trong object page cần `@UI.fieldGroup`** hoặc nằm trong facet.
3. **Search field cần `@Search.defaultSearchElement: true`**.
4. **Filter trên list cần `@Consumption.filter.mandatory: true`** nếu bắt buộc.
5. **Title và Description** dùng `@UI.headerInfo` trên root view.

## Gotchas activate CDS (đã gặp thật — verify trước khi pull)

### 1. `@Semantics.quantity`/`amount` — ở view entity CẤM annotate field đơn vị

- Field **số lượng** → `@Semantics.quantity.unitOfMeasure: '<UnitField>'`; field **tiền** →
  `@Semantics.amount.currencyCode: '<CurrencyField>'` (annotate trên field giá trị, không phải field đơn vị).
- ⚠️ Trong `define view entity` / `define root view entity`: **TUYỆT ĐỐI KHÔNG** dùng
  `@Semantics.unitOfMeasure: true` / `@Semantics.currencyCode: true` trên field đơn vị → lỗi
  *"Semantics.unitOfMeasure is not allowed in view entities"*. Field unit/currency để trống (được
  reference từ field quantity/amount là đủ). (Cấm này KHÁC `define view` cũ.)
- View bật `@Metadata.ignorePropagatedAnnotations: true` → annotation KHÔNG propagate → phải khai lại
  `@Semantics.quantity/amount` ở **mỗi layer bật ignore** (ZI, ZR). Currency cố định: thêm
  `cast( 'USD' as abap.cuky ) as Currency` rồi trỏ annotation vào. *(memory: cds-semantics-unit-currency)*

### 2. CAST sang NUMC — literal nguồn phải dài ĐÚNG bằng target

- `cast( '0' as abap.numc( 10 ) )` → lỗi *"CAST NUMC ... lengths must match"*. NUMC không tự pad.
- Đúng: `cast( '0000000000' as abap.numc( 10 ) )` (đủ 10 ký tự). `char(n)`/`dec(p,s)`/`cuky` cast từ
  `''`/`0` thì OK (pad được), chỉ NUMC bị chặt length. *(memory: cds-cast-numc-length)*
- **Cast/so sánh NUMC(a) ↔ NUMC(b) khác độ dài CẤM**: *"Datatypes NUMC and NUMC are compatible, but their
  lengths ... differ"*. Xảy ra cả khi CAST (numc6→numc2) LẪN khi `WHERE numc2_field BETWEEN '6-char-literal'`.
  Fix cast: **qua CHAR trước** rồi numc cùng độ dài `cast( substring( cast(x as abap.char(6)),5,2) as numc(2))`.
  Fix WHERE: literal phải đúng độ dài field. ⚠️ **Verify field trước**: `I_CalendarMonth.CalendarMonth` là
  **NUMC(2) = 01..12** (month-of-year, 12 dòng), KHÔNG phải YYYYMM → month value-help chỉ cần `key CalendarMonth
  as ReportMonth` (khỏi cast/substring). (verified ZI_ZCO04_MONTH_VH data-preview 2026-07-06)

### 3. Association vs JOIN — to-one dùng assoc, to-many dùng JOIN

- Association project scalar (`assoc.field as X`) phải **to-one** (`[1..1]`/`[0..1]`); to-many `[0..*]`
  → lỗi (path trả nhiều dòng). Bước fan-out to-many → dùng **LEFT OUTER JOIN** trong FROM.
- Lỗi *"The association X cannot be used locally in the view"*: ON-condition của assoc dùng
  `$projection.<field>` mà `<field>` lại đến từ **association khác** → CDS không resolve local. Fix: lấy
  field bằng **chain qua association base-resolvable** (`_SalesOrder._SalesOrganization.CompanyCode`),
  ON chỉ trỏ **field gốc** của data source/join. *(memory: cds-association-local-use-cardinality)*

### 4. Parameterized view (`with parameters`) — chỉ JOIN được, KHÔNG association

- `association ... to <ParamView>(p:...)` → lỗi *"Unexpected word "("; ... "ON" was expected"*.
- Phải dùng `left/inner join ZI_ATTACHMENT(p_module_obj: 'TRSD', p_app_id: 'ZSD02') as _X on _X.Key = Item.Key`.
  ON dùng alias data-source (`Item.X`), KHÔNG `$projection`. Join alias KHÔNG đưa vào "Exposed
  associations". *(memory: cds-parameterized-view-join)*

### 5. Value help / assoc trỏ view giao dịch nặng → OData V4 dump (EXCRT)

- Gắn `@Consumption.valueHelpDefinition` (hoặc expose assoc) trỏ `I_SalesOrder` và các view có field
  dùng **conversion exit EXCRT** (field tỷ giá) → `CX_SADL_GW_V4_MODEL_EXCEPTION` "Do not use
  conversion exit EXCRT" → **dump khi publish service binding** (không lộ lúc activate CDS).
- Filter số chứng từ SD → để filter tự do (đừng gắn value help trỏ I_SalesOrder). Value help chỉ trỏ
  **master/config view** (I_CompanyCode, I_Plant, I_SalesOrganization, I_BusinessPartner...). Giữ report
  phẳng — materialize field thành cột scalar, không expose assoc tới view giao dịch nặng.
  *(memory: odata-v4-valuehelp-excrt-dump)*

### 6. `GROUP BY` KHÔNG nhận biểu thức `cast(...)`/`concat(...)` trực tiếp

- CDS view entity: đặt cả biểu thức (vd `cast( concat( left(...), right(...) ) as abap.char(6) )`) ngay
  sau `GROUP BY` → parser báo *"Unexpected keyword cast"* (activation fail).
- **Fix**: `GROUP BY` **field gốc** (vd `FiscalYearPeriod`); phần tử SELECT vẫn để biểu thức derive được
  vì nó là hàm thuần trên field đã group.

```abap
// ❌ group by cast( concat( left( ... ), right( ... ) ) as abap.char(6) )
// ✅
key cast( concat( left( rtrim(cast(FiscalYearPeriod as abap.char(10)),' '),4 ),
                  right( rtrim(cast(FiscalYearPeriod as abap.char(10)),' '),2 ) ) as abap.char(6) ) as PeriodId
...
group by FiscalYearPeriod
```

(verified ZCO04 `ZI_ZCO04_PERIOD_VH` activation 2026-07-06)

## Reference

- SAP doc CDS annotations: https://help.sap.com/docs/abap-cloud/abap-rap/annotation-lists
- Fiori Elements: https://experience.sap.com/fiori-design-web/
