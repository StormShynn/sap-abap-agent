# Naming Conventions cho SAP S/4HANA Cloud Public Edition

Bắt buộc cho mọi object custom. Vi phạm = không commit.

## Quy tắc prefix

| Prefix | Loại object | Convention chi tiết |
|--------|-------------|---------------------|
| `ZTB*` | Transparent table (custom DB) | `ZTB_<OBJECT>`, `ZTB_<OBJECT>_<SUB>` — **≤ 16 ký tự** (vd `ZTB_ZSD18_NOTE`, `ZTB_PO_ITEM`) |
| `ZI*`  | CDS interface view (base layer) | `ZI_<OBJECT>`, `ZI_<OBJECT>_<SUB>` — joins trực tiếp với DB table, layer kỹ thuật |
| `ZR*`  | CDS reuse view (root, có associations) | `ZR_<OBJECT>` — projection on `ZI`, có associations, dùng làm base cho behavior |
| `ZC*`  | CDS consumption view (projection) | `ZC_<OBJECT>` — projection on `ZR`, có `@UI` annotation cho Fiori |
| `ZE*`  | CDS extension view | `ZE_<OBJECT>` — bổ sung field cho standard SAP CDS |
| `ZP*`  | CDS projection view (custom) | `ZP_<OBJECT>` — alternative cho C, dùng cho riêng use case |
| `ZA*`  | CDS abstract entity (action parameter / result) | `ZA_PO_PRINT_PARAM`, `ZA_PDF_RESPONSE` |
| `ZBP*` | Behavior implementation (ABAP class, behavior pool) | `ZBP_<ZR_NAME>` — impl cho behavior definition |
| `ZUI*` | Service def + binding cho **APP / UI** (cùng tên) | `ZUI_<OBJECT>_O4` (V4 UI), `ZUI_<OBJECT>_O2` (V2 UI) |
| `ZAPI*` | Service def + binding cho **API M2M** (cùng tên) | `ZAPI_<OBJECT>_O4` (V4 API), `ZAPI_<OBJECT>_O2` (V2 API) |
| `ZCL_*` | ABAP class thường (helper) | `ZCL_<DOMAIN>_<ACTION>` (vd `ZCL_PO_HELPER`) |
| `ZF_*` | Function module / Function group | `ZF_<DOMAIN>_<ACTION>` (vd `ZF_PO_PRINT`) |
| `ZIF_*` | Interface (ABAP) | `ZIF_<DOMAIN>_<CONTRACT>` |

## `<OBJECT>` = MÃ BÁO CÁO / TICKET (BẮT BUỘC)

Phần `<OBJECT>` sau prefix phải là **mã báo cáo/chức năng (ticket code)**, KHÔNG dùng tên
nghiệp vụ mô tả. Ví dụ báo cáo **ZSD01 Packing List**:

- ✅ `ZI_ZSD01`, `ZR_ZSD01`, `ZC_ZSD01`, `ZUI_ZSD01_O4` (service def + binding cùng tên), `ZBP_R_ZSD01`
- ❌ `ZI_PACKINGLIST`, `ZC_PACKINGLIST` (tên mô tả — sai)

Khớp với các story đã có: `ZC_ZMM05`, `ZI_ZMM07`, `ZR_ZSD06`, `ZUI_ZSD06_O4`.
Nếu cần tách header/item: thêm hậu tố `_H` / `_IT` (vd `ZC_ZSD06_IT`, `ZR_ZMM05_H`).
Object dùng chung / master của KH giữ tên riêng (vd `ZI_ACME_COMPCODE`).

## 3-layer CDS pattern (BẮT BUỘC cho mọi BO)

```
   ┌─────────────────────────────────────────────┐
   │ ZC_<OBJECT>  (Consumption)                   │  ← Layer 3: UI annotation (@UI, @Search)
   │   └─ projection on ZR                       │     Dùng cho Fiori binding
   │                                             │     Behavior: projection; + use action
   └─────────────────────────────────────────────┘
                       ↑
   ┌─────────────────────────────────────────────┐
   │ ZR_<OBJECT>  (Reuse)                        │  ← Layer 2: associations, joins
   │   └─ projection on ZI                       │     Behavior: managed; + action + mapping
   │   └─ base cho C và behavior pool            │     DCL ở đây (pfcg_auth)
   └─────────────────────────────────────────────┘
                       ↑
   ┌─────────────────────────────────────────────┐
   │ ZI_<OBJECT>  (Interface)                     │  ← Layer 1: technical, joins DB
   │   └─ as select from DB tables               │     Có thể split: ZI_<H>, ZI_<I> cho perf
   │   └─ annotation @Semantics.largeObject       │     Cho attachment / file fields
   └─────────────────────────────────────────────┘
```

### Tại sao 3 layer?

- **Tái sử dụng**: nhiều `ZC_*` (cho các use case / OData khác nhau) có thể projection trên cùng `ZR_*`.
- **Phân tách trách nhiệm**: `ZI_*` thuần kỹ thuật (DB), `ZR_*` thuần nghiệp vụ (associations), `ZC_*` thuần UI.
- **Performance**: có thể split `ZI_*` thành `ZI_<H>` (header) + `ZI_<I>` (item) nếu một view quá lớn.
- **Bảo trì**: thay đổi UI annotation không ảnh hưởng data layer.

## Giới hạn độ dài tên (BẮT BUỘC — nguồn chính thống SAP)

Nguồn: **ABAP Keyword Documentation – Names of Repository Objects** (bản CLOUD):
- *"The length of names is restricted to **30 characters** or less"* (đã gồm namespace prefix).
- *"the names of **database tables** are restricted to **16 characters**"*.

→ Phân nhóm áp dụng cho ABAP Cloud / S/4HANA Cloud Public:

| Loại object | Max ký tự | Ghi chú |
|-------------|-----------|---------|
| **Database table** (transparent) — `ZTB*` | **16** | Sinh physical DB object. Cả DDL `define table` lẫn TABL classic. **Chặt nhất.** |
| Classic DDIC view, lock object | 16 | ABAP Cloud thường không tạo (dùng CDS/RAP thay thế) |
| **Structure** (DDIC, `INTTAB`) — `ZST*` | 30 | KHÔNG phải DB table → 30 |
| **Data element** — `ZE*`/`ZDT*` | 30 | |
| **Domain** — `ZD*` | 30 | |
| **Table type** — `ZTT*` | 30 | |
| **CDS view entity / DDL source** — `ZI/ZR/ZC/ZE/ZA*` | 30 | |
| **Behavior definition** (BDEF) | 30 | Trùng tên root entity → cũng ≤30 |
| **Service definition / binding** — `ZUI*/ZAPI*` | 30 | |
| **ABAP class / interface** — `ZCL_*/ZIF_*` | 30 | |
| **Table field / component** | 30 | Tên cột trong table/structure |
| **Package** | 30 | |
| **Program / Report** — `ZP*` | 30 | (tiêu đề program ≤ 74, xem bảng mô tả) |
| **Message class** | **20** | ⚠️ KHÔNG phải 30 — tên message class (T100/ARBGB) ≤ 20 |

> ⚠️ **Bẫy thường gặp**: ghép `ZTB_<MODULE>_<TICKET>_<SUB>_D` (draft) rất dễ vượt 16.
> Ví dụ `ZTB_SD_ZSD18_NOTE_D` = 19 ký tự (SAI). Bỏ bớt segment phân hệ → `ZTB_ZSD18_NOTE_D` = 16 (ĐÚNG).
> Với table, **ưu tiên mã ticket + hậu tố ngắn**, bỏ tiền tố module nếu cần. Lint `sap_naming_lint.py`
> tự enforce: TABL/`define table` = 16, structure/CDS/class = 30.

## Mô tả / nhãn (description, field label, message)

**Rule of thumb**: hầu hết **Short Text / Description** của object trong SAP = **60 ký tự**
(database table DDTEXT, data element, domain, structure, table type, CDS, class, interface, package,
message class). Ngoại lệ là **field labels** và **program/message text**.

| Loại text | Max ký tự | Nguồn |
|-----------|-----------|-------|
| Description / Short Text (đa số object) | **60** | Rule of thumb SAP |
| `@EndUserText.label` (CDS view / element / BDEF) | **60** | [ABAP CDS – element_annot](https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/abencds_f1_element_annotation.htm): *"the value is limited to a length of 60 characters"* |
| Field label – Short | 10 | Data element field labels (SE11/ADT) |
| Field label – Medium | 20 | [sapdatasheet SCRLEN_M](https://www.sapdatasheet.org/abap/dtel/scrlen_m.html) — *"max 20, 15 recommended"* |
| Field label – Long | 40 | Data element field labels |
| Field label – Heading | 55 | Data element heading (column header) |
| Program title | 74 | |
| Message text (1 dòng trong message class) | 73 | T100 |

> Lưu ý: nếu CDS element dựa trên data element, framework tự suy nhãn từ **field labels** của data
> element (short/medium/long ≤ 40); `@EndUserText.label` (≤60) override khi không có data element.

## Quy tắc khác

- **Upper snake_case** sau prefix (vd `ZTB_ZSD18_NOTE`, không phải `ztb_zsd18_note` khi viết tên object).
- **Không dùng số** ở cuối tên trừ khi có versioning.
- **Tiếng Anh**, không viết tắt nếu không phổ biến.
- Mỗi customer namespace cần check với tech lead KH trước khi áp dụng.

## Strict mode (BẮT BUỘC cho mọi behavior definition)

```abap
managed implementation in class zbp_<zr> unique;
strict ( 2 );                            // ⬅ BẮT BUỘC trong R behavior
...
projection;
strict ( 2 );                            // ⬅ BẮT BUỘC trong C behavior
```

`strict ( 2 )` ép type-safe, SAP enforce:
- Không implicit conversion giữa các type không tương thích.
- Table/structure phải có đầy đủ type info.
- Mọi field dùng trong action/validation phải khai báo trong BDEF hoặc CDS.

## Mapping clause (BẮT BUỘC khi CDS name ≠ DB column)

Khi dùng table generic cho nhiều report (vd `ztb_scm_pdf_draf` dùng cho PR, PO, GR...), map field:

```abap
managed implementation in class zbp_<zr> unique;
strict ( 2 );

define behavior for ZR_<OBJECT> {
  field ( readonly ) PurchaseRequisition;
  action CreatePDF result [1..*] $self;
  
  mapping for ztb_scm_pdf_draf              // ⬅ BẮT BUỘC nếu dùng table generic
    {
      PurchaseRequisition = object_id;
      Attachment          = attachment;
      MimeType            = Mimetype;
      FileName            = Filename;
    }
}
```

## Service definition + binding naming

**Service binding TRÙNG TÊN service definition** (SRVD và SRVB là 2 object type khác nhau nên
được phép cùng tên — KHÔNG tách hậu tố `_SD`). Phân biệt **APP/UI** (`ZUI*`) vs **API M2M** (`ZAPI*`)
và version OData qua hậu tố `_O4` / `_O2`.

| Pattern | Mục đích | Provider contract (trong service def) |
|---------|----------|----------------------------------------|
| `ZUI_<OBJECT>_O4` | APP / Fiori UI, OData **V4** | `odata_v4_ui` |
| `ZUI_<OBJECT>_O2` | APP / UI, OData V2 | `odata_v2_ui` |
| `ZAPI_<OBJECT>_O4` | Web API machine-to-machine, OData **V4** | `odata_v4_api` |
| `ZAPI_<OBJECT>_O2` | Web API M2M, OData V2 | `odata_v2_api` |

Service definition dùng cú pháp **provider contract**:

```abap
define service ZUI_ZCO04_O4
  provider contracts odata_v4_ui {
  expose ZC_ZCO04 as ProductionCost;
}
```

File abapGit: `zui_<object>_o4.srvd.srvd` (definition) + `zui_<object>_o4.srvb.srvb` (binding), cùng tên.

## Cho abstract entity (parameter / result cho action)

Khi action trong behavior cần parameter hoặc result, dùng **abstract entity**:

```abap
define abstract entity ZA_PO_PRINT_PARAM
{
  po_numbers : abap.string_table;
}
```

## Cho Fiori Elements

- Metadata extension file cùng tên consumption view + `.MDE` (vd `ZC_PURCHASEORDER.MDE.asmd`).
- Annotation dùng cú pháp `@UI: { ... }` trong CDS hoặc metadata extension.

## Cho ABAP behavior

- Behavior definition cho `ZR_*` (managed): business logic ở đây.
- Behavior definition cho `ZC_*` (projection): chỉ `use action` re-expose.
- Behavior implementation (ZBP_*) nằm trong **behavior pool** (class ABAP cụ thể).

## Ví dụ đầy đủ: BO Purchase Order

```
ZTB_PO                        -- DB table (header)   ≤16 ký tự
ZTB_PO_ITEM                   -- DB table (item)     ≤16 ký tự (KHÔNG đặt ZTB_PURCHASEORDER_ITEM = 22)
ZTB_SCM_PDF_DRAF              -- DB table chung cho PDF (reuse cho nhiều report)
ZI_PURCHASEORDER              -- I: interface (base, JOIN PDF table)
ZR_PURCHASEORDER              -- R: reuse (associations, semantic)
ZC_PURCHASEORDER              -- C: consumption (UI annotation)
ZC_PURCHASEORDER.MDE          -- MDE: metadata extension
ZC_PURCHASEORDER.bdef.asbdef  -- C: projection; use action
ZR_PURCHASEORDER.bdef.asbdef  -- R: managed; + action + mapping
ZBP_PURCHASEORDER             -- ZBP: behavior pool cho R
ZR_PURCHASEORDER.dcls.asdcls  -- DCL R: pfcg_auth (Plant, PurchOrg)
ZC_PURCHASEORDER.dcls.asdcls  -- DCL C: inheriting conditions from entity ZR
ZUI_PURCHASEORDER_O4          -- ZUI: service definition + binding (cùng tên), OData V4 UI
ZCL_PO_HELPER                 -- ZCL: helper class (PDF generation)
ZF_PO_PRINT                   -- ZF: function module
```

## Reference SAP chính thức

- SAP doc: https://help.sap.com/docs/abap-cloud/abap-rap/naming-conventions-for-development-objects
- SAP doc CDS 3-layer: https://help.sap.com/docs/abap-cloud/abap-rap/consumption-view
- Áp dụng cùng các best practice Clean ABAP (xem clean-abap.md).

## Lint

```bash
python scripts/sap_naming_lint.py src/
```

Lint check:
- Transparent table: prefix `ZTB*`
- Interface view: prefix `ZI*`
- Reuse view: prefix `ZR*`
- Consumption view: prefix `ZC*`
- Extension view: prefix `ZE*`
- Abstract entity: prefix `ZA*`
- Behavior definition: prefix `Z*` (ZC cho C, ZR cho R)
- Behavior implementation class: prefix `ZBP*`
- Service binding / service definition: prefix `ZUI*`
- ABAP class helper: prefix `ZCL_*`
- Function module: prefix `ZF_*`
- Độ dài tên: **database table (TABL / `define table`) ≤ 16**, structure/CDS/class/service... ≤ 30
  (xem mục "Giới hạn độ dài tên" ở trên — nguồn ABAP Keyword Documentation).
