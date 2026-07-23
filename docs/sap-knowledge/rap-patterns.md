# RAP Patterns — Managed vs Unmanaged

Decision tree xem `docs/ARCHITECTURE.md`. Đây là chi tiết từng pattern.

## Managed Scenario (mặc định)

Dùng khi: CRUD đơn giản, không cần custom save logic phức tạp, sequence theo SAP standard.

### Cấu trúc file

```
src/
├── zr_purchaseorder.ddls.asddls          # Consumption view
├── zr_purchaseorder.mde.asmd             # Metadata extension
├── zi_purchaseorder.ddls.asddls          # Interface view (header)
├── zi_purchaseorder_i.ddls.asddls        # Interface view (item)
├── zc_purchaseorder.bdef.asbdef          # Behavior definition
├── zbp_purchaseorder.clas.abap           # Behavior implementation class
└── zui_purchaseorder_sd.srvd.srvd       # Service definition
```

### Behavior definition skeleton

```abap
managed; // <-- keyword
implementation in class zbp_purchaseorder unique;
// Với draft:
with draft;

define behavior for ZI_PURCHASEORDER alias PurchaseOrder
implementation in class zbp_purchaseorder unique
with draft
{
  // Field control
  field ( readonly ) PurchaseOrderNo, CreatedBy, CreatedAt, ChangedBy, ChangedAt;

  // Numbering
  numbering: managed by master; // <-- SAP tự sinh PO number
  // Hoặc: numbering: external; // <-- nếu KH tự cấp

  // CRUD
  create;
  update;
  delete;

  // Validation
  validation validateHeader on save { field Supplier, PurchaseOrderDate; }

  // Action
  action ( features : instance ) approve result [1] $self;
  action ( features : instance ) reject  result [1] $self;

  // Determination
  determination setDefaultDate on modify { field PurchaseOrderDate; }

  // Association
  association _Item { create; with draft; }
}

define behavior for ZI_PURCHASEORDER_I alias PurchaseOrderItem
implementation in class zbp_purchaseorder unique
with draft
{
  // ...
}
```

### Behavior implementation skeleton (managed)

```abap
class ZBP_PURCHASEORDER definition public abstract behavior for ZI_PURCHASEORDER.

  // Một số method implement bắt buộc:
  method VALIDATEHEADER.
    " Validation logic
    if iv_supplier is initial.
      append 'Supplier is required' to failed-purchaseorder.
    endif.
  endmethod.
endclass.
```

## Unmanaged Scenario

Dùng khi: cần custom save logic phức tạp, sequence custom, gọi API bên ngoài,
update nhiều bảng trong 1 transaction không khớp standard RAP.

### Cấu trúc giống managed, nhưng behavior implementation đầy đủ hơn

```abap
unmanaged; // <-- keyword
implementation in class zbp_purchaseorder unique;
// Phải implement: create, update, delete, plus read nếu không dùng CDS
```

### Method bắt buộc trong ZBP_*

- `READ` — đọc instance(s).
- `CREATE` — tạo mới (tự sinh PK, gọi API, etc.).
- `UPDATE` — cập nhật (validate, lock).
- `DELETE` — xóa (check FK, archive).
- `LOCK` — tự implement hoặc dùng SAP.

### Khi nào dùng

- Sequence custom: KH muốn `PO-2025-0001` thay vì SAP auto-number.
- Multi-table transaction: 1 lần save update 3 bảng liên quan.
- Gọi BAPI / API bên ngoài trong save.
- Validate phức tạp cần gọi function khác.

### Trade-off

- **Pros**: control hoàn toàn, linh hoạt.
- **Cons**: nhiều code hơn, dễ sai, cần test kỹ.

## Bảng so sánh

| | Managed | Unmanaged |
|---|---|---|
| Số method cần implement | Vài method (validation, determination) | Toàn bộ CRUD |
| Sequence | SAP tự sinh (hoặc external) | Tự implement |
| Draft support | Có sẵn với `with draft` | Có sẵn |
| ETag | Tự động | Tự implement |
| Side effects | Tự khai báo | Tự implement |
| Test effort | Thấp | Cao |
| Best for | CRUD thuần | Custom logic |

## Code skeleton

Xem:
- `templates/rap-boilerplate/managed/` — full template có thể copy.
- `templates/rap-boilerplate/unmanaged/` — full template có thể copy.

## Gotchas BDEF / RAP (đã gặp thật — verify trước khi pull)

### 1. Comment trong BDEF/DDL dùng `//` KHÔNG dùng `"`

- File `.bdef.asbdef`, `.ddls`, `.ddlx`, `.srvd` → comment dòng dùng **`//`** (hoặc `/* */`).
  Viết `"` (kiểu ABAP class) → parser báo hàng loạt *"Unexpected character"* → behavior "contains
  errors" → projection báo *"base entity does not define action"*.
- File **ABAP class** (`.clas.abap`, locals_imp, testclasses) thì dùng `"` bình thường (OK UTF-8).
- `//` chỉ an toàn **TRONG `{ }` body**. ĐỪNG đặt comment giữa các keyword header của behavior
  (giữa `lock` / `authorization` / `etag`, trước `{`) — parser vỡ trạng thái, báo lệch kiểu
  *"authorization is not expected here"* ở dòng KẾ TIẾP (nhất là entity con).
- Check: `grep -nE '^\s*"' *.asbdef *.asddls *.asddlxs` phải rỗng. *(memory: bdef-comment-syntax)*

### 2. Field control — sau `:` là operation, KHÔNG boolean

- `field ( <feature> : <x> )` thì `<x>` BẮT BUỘC là `create` | `update` | `execute`, KHÔNG phải boolean.
- ❌ `field ( mandatory : false ) X;` → lỗi *'"create | execute | update" was expected, not "false"'*.
- Field **editable + optional = MẶC ĐỊNH** → KHÔNG khai gì (chỉ cần không nằm trong `readonly`). Không
  có cú pháp `mandatory : false`.
- `field ( mandatory ) X;` luôn bắt buộc · `field ( mandatory : create ) X;` bắt buộc khi create ·
  `field ( readonly ) X;` luôn readonly · `field ( readonly : update ) X;` set được lúc create, readonly
  khi update (dùng cho key). *(memory: rap-bdef-field-control-syntax)*

### 3. Managed BO key UUID phải khai `field ( numbering : managed )`

- BO managed key UUID (SYSUUID_X16) **KHÔNG tự sinh** mặc định. Ngoài `field ( readonly )`, thêm câu riêng:
  `field ( numbering : managed ) <KeyField>;` → framework tự sinh UUID lúc create (không cần numbering handler).
- Thiếu → key rỗng → create/save fail (draft tạo được nhưng Activate lỗi key rỗng vào cột NOT NULL).
- Composition: root khai `numbering : managed` cho key cha; con khai cho **key riêng của nó** (`ItemId`) —
  phần key cha do `CREATE BY _assoc` tự điền. Scaffold hay QUÊN mục này. *(memory: rap-managed-uuid-numbering)*

### 4. Action trên entity CON cần `authorization master ( instance )` + handler

- Action (bound) trên entity con mà con khai `authorization dependent by _Header` → runtime dump
  **`CX_RAP_HANDLER_NOT_IMPLEMENTED`** (Method INSTANCE_AUTHORIZATION) khi bấm action. `dependent` chỉ
  cover CRUD chảy qua parent, KHÔNG cover action riêng của con.
- Fix: BDEF đổi con sang `authorization master ( instance )` (lock/etag vẫn `dependent by _Header` được),
  và implement `get_instance_authorizations FOR INSTANCE AUTHORIZATION` trong local handler riêng cho con
  (`lhc_Item`). Body rỗng = grant full. Static action (không key) → `authorization ... ( global )` +
  get_global. *(memory: rap-child-action-authorization)*

### 5. Custom query provider (`IF_RAP_QUERY_PROVIDER~select`) phải gọi `get_paging` + tự áp filter

- Bắt buộc gọi `io_request->get_paging( )` và áp offset/page_size, nếu không runtime báo
  *"Query not fully covered ... get_paging missing"*. Client gửi sort → cũng phải gọi `get_sort_elements`.
- **Provider TỰ áp filter**: framework chỉ đưa filter qua `get_filter`, KHÔNG re-filter `set_data`. Đọc
  từng filter (Plant/Year/Month) rồi áp vào SELECT/loop. Quên → filter "không tác dụng".
- Đọc filter (2602): `get_filter( )->get_as_ranges( )` trả `tt_name_range_pairs`, component **`range` là
  internal table trực tiếp, KHÔNG phải REF TO data** → `assign lr_cond->range to <range>` (field-symbol
  `type index table`), KHÔNG `->range->*`. Bọc TRY/CATCH `cx_rap_query_filter_no_range`.
- **`set_data` bind theo TÊN component**: tên component result phải KHỚP CHÍNH XÁC tên element custom
  entity (`MaterialGroup` ≠ `MATERIAL_GROUP`) — lệch → field hiển thị TRỐNG dù có data.
  *(memory: rap-query-provider-paging)*
- **Sort phải áp TRƯỚC paging** (provider tự sort, framework không sort hộ): đọc
  `io_request->get_sort_elements( )` (line có `element_name` + `descending`), map sang
  `abap_sortorder_tab` rồi `SORT lt_result BY (lt_order)` (dynamic sort — released ABAP Cloud, qua
  gate). Client KHÔNG gửi sort → fallback thứ tự mặc định theo FS (vd `Plant → MaterialGroup →
  CostComponent`). Sort SAU paging = trang bị xáo, sai window. Ví dụ: `ZCL_ZCO04_QUERY`.
- **Authorization cho custom entity + code query provider**: `@ObjectModel.query.implementedBy`
  KHÔNG có SQL data source để CDS **DCL** attach → DCL chuẩn (`pfcg_auth`) không áp trực tiếp lên
  custom entity; mà dự án **CẤM `AUTHORITY-CHECK`** (`scripts/check_released_api.py` → ERROR "use DCL").
  → Enforce ở **1 seam trong `select( )`** (method `is_plant_authorized` gọi trước khi đọc data;
  không authorized → trả empty set NHƯNG vẫn chạy count/sort/`get_paging` để giữ RAP contract), với
  cơ chế cụ thể là **DCL trên các source view released** (chúng tự mang SAP DCL) hoặc **released auth
  API** (confirm trong ADT) — KHÔNG dùng `AUTHORITY-CHECK`. Auth object của KH thường là open item →
  đừng bịa; để 1 constant flagged `[Unverified]`. Đáng cân nhắc **ADR**. Ví dụ: `ZCL_ZCO04_QUERY`.
- **Object Page cho custom entity: cần `@UI.facet` + params phải là KEY**. Thiếu `@UI.facet` (trong MDE,
  đặt ở field đầu; `#IDENTIFICATION_REFERENCE` cho dimension + `#FIELDGROUP_REFERENCE` targetQualifier cho
  từng nhóm) → click dòng ra **OP trống**. NHƯNG quan trọng hơn: FE mở OP bằng **GET theo KEY** → `select( )`
  bị gọi lại chỉ với filter = các **key field**. Nếu report cần tham số **non-key** (vd ReportMonth/ReportYear
  chi phối rolling) mà chúng KHÔNG nằm trong key → `select( )` không có tham số → tính ra rỗng → **OP vẫn trống
  dù đã có facet**. Fix: đưa các tham số cần cho tính toán **vào KEY** của custom entity (và `get_selection`
  đọc thêm chúng), hoặc bỏ điều hướng OP nếu report chỉ cần list phẳng. Ví dụ: `ZC_ZCO04`.
- 🔴 **Custom entity + query provider = `define custom entity` (KHÔNG `root`)** (ZCO10 2026-07-07):
  custom entity đọc-only (code-based query, `@ObjectModel.query.implementedBy`) KHÔNG phải composition
  root của RAP BO. Khai `define root custom entity` → activate service def lỗi **"The use of CDS Entity
  ZC_X is not permitted"** (vì `root` báo hiệu BO root cần behavior/composition). Đúng: `define custom
  entity ZC_X { ... }`. Mẫu đã chạy: **`ZC_ZMM07`** (`define custom entity` + `@ObjectModel.query.implementedBy`).
  ⚠️ Clause `provider contracts odata_v4_ui` trên service definition **KHÔNG phải nguyên nhân** — `ZC_ZMM07`
  có clause đó vẫn chạy; có thể để hoặc bỏ (custom entity expose được cả 2 cách). Gốc lỗi là `root`.

### 6. Post chứng từ SAP + cần số ngay → OData API, KHÔNG EML-in-handler

- BO unmanaged wrap BAPI (vd `I_MaterialDocumentTP`) gán số **LATE** (save phase). EML `MODIFY ENTITIES
  ... CREATE` trong handler chỉ trả `%pid`, **KHÔNG có số thật**; `COMMIT ENTITIES` bị **cấm** trong
  behavior class → không lấy số đồng bộ. Backfill theo XBLNR không deterministic.
- Lấy số synchronous: gọi **OData API HTTP** (`API_MATERIAL_DOCUMENT_SRV`) trong action (HTTP ≠ COMMIT
  ENTITIES → hợp lệ, commit LUW riêng trả số ngay; cần Communication Arrangement OUTBOUND), hoặc
  **background job** + `COMMIT ENTITIES ... RESPONSE OF` ở class thường (async). Đóng gói poster sau
  interface (`ZCL_CORE_GOODS_MVT_POSTER`) + inject qua static seam để ABAP Unit double.
  Xem `document-creation-pattern.md`, ADR-0022. *(memory: rap-doc-number-late-numbering)*

## Released API list (2602)

Xem `released-objects-2602.md`. Một số class quan trọng cho RAP:
- `CL_ABAP_BEHAVIOR_HANDLER` — base class cho behavior pool.
- `CL_ABAP_BEHAVIOR_EVENT_HANDLER` — xử lý event.
- `CL_ABAP_BEHAVIOR_SAVER` — saver cho unmanaged.
- `CL_ABAP_CORRESPONDING` — move data giữa structure.
- `ABAP_BEHV_DESCR` — runtime behavior description.

Tất cả class trên đều released trong 2602. Xem SAP API state cho từng class.

## Gotcha ADT activation (scaffold hay sai — verified ZSD07 2026-07-04)

Các lỗi này lộ ra khi **pull vào ADT + activate**, không thấy khi chỉ đọc code. Scaffold managed+draft
hay dính — check trước:

- **Draft table field name = ELEMENT NAME của CDS entity, KHÔNG phải tên cột DB.** Active table đi qua
  `mapping for <table> { Element = db_col; }` nên cột DB có thể là `ZFO`… Nhưng **draft table KHÔNG qua
  mapping** → field phải trùng element name (`FREIGHTORDER`, `REGISTRATIONNUMBER`…). Đặt sai (ZFO…) →
  draft không khớp entity, activate fail. Admin: `.INCLUDE %ADMIN = SYCH_BDL_DRAFT_ADMIN_INC`.
- **Projection behavior/metadata phải dùng ALIAS của projection, không phải tên composition gốc.** Nếu
  projection CDS expose `_ZSD07 as data : redirected to composition child …` thì bdef projection viết
  `use association data { … }` và MDE facet `targetElement: 'data'` — KHÔNG `_ZSD07`. Sai → "no association".
- **Data element `TIMS` (và có thể `DATS`) KHÔNG được phép trong ABAP Cloud** ("The use of Data Element TIMS
  is not permitted"). Dùng **built-in `t`** (time) / `d` (date) trong TYPES/method signature. (DATS thường
  vẫn được phép — theo compiler, nhưng nếu bị chặn thì đổi `d`.)
- **Unmanaged saver `lsc_` cho BO read-only + chỉ `action` (không CRUD): redefine `save` (rỗng), KHÔNG
  `save_modified`, KHÔNG để class rỗng.** Hai lỗi ADT phải né đúng thứ tự: (1) `save_modified` → "SAVE_MODIFIED
  cannot be redefined in accordance with BEHAVIOR definition" (chỉ hợp lệ khi có create/update/delete); (2)
  saver class rỗng (không redefine gì) → "method SAVE must be redefined". ✅ Đúng = redefine `save` với impl
  rỗng (`METHODS save REDEFINITION.` + `METHOD save. ENDMETHOD.` — nothing to persist). Behavior CÓ CRUD → mới
  dùng `save_modified` (bảng create/update/delete). Kèm: strict(2) + chỉ action vẫn cần `lock master` (root) + `lock FOR LOCK` stub.
- **HTTP client Cloud: `if_web_http_request` set body = `set_binary( i_data = xstr )`** (KHÔNG `set_binary_body`).
- **`TABLE FOR DELETE <entity>` chỉ có KEY (+ `%tky`/`%is_draft`), KHÔNG có business field.** `APPEND VALUE #(
  Id = … FreightOrder = … )` → "No component FREIGHTORDER". Chỉ set key: `VALUE #( Id = … )`.
- **Timestamp field của BO chuẩn: KHÔNG ĐOÁN built-in — VERIFY trước khi CONVERT.** ADT rất strict về kiểu
  timestamp; đoán sai → "type cannot be converted" / "not type-compatible". Cây CONVERT theo kiểu THẬT:
  `utclong` → `CONVERT UTCLONG ts INTO DATE d TIME t TIME ZONE tz` (TIME ZONE ở GIỮA); `timestamp`/`timestampl`
  → `CONVERT DATE d TIME t INTO TIME STAMP ts TIME ZONE tz` / `CONVERT TIME STAMP ts TIME ZONE tz INTO DATE d
  TIME t` (TIME ZONE ở CUỐI); `DEC` thuần → arithmetic. **Cách verify (không đoán)**: F2 data element trong ADT,
  hoặc `SELECT ... INTO @DATA(...)` (lấy kiểu từ view), hoặc reuse precedent ACME (vd ZSD18 dùng chính data element).
  ⚠️ Thực tế TM (VERIFIED F2 ADT 2026-07-04): `/scmtms/vdm_event_actl_dtetme` + `/scmtms/vdm_tor_order_datetime`
  = domain **`TZNTSTMPS`** = built-in **`timestamp`** (DEC15,0) — KHÔNG phải `utclong`, KHÔNG phải `timestampl`
  (ADT reject cả 2). → param `TYPE timestamp` + `CONVERT TIME STAMP`. ĐỪNG tin "TM = utclong" (giả định cũ sai,
  đoán 3 lần mới F2 ra sự thật). *(memory: tm-timestamp-utclong-overflow — RESOLVED.)*
