# Clean ABAP — Style guide

ABAP clean code, dựa trên SAP Clean ABAP guide. Mục đích: code dễ đọc, dễ test, dễ maintain.

## Quy tắc chính

### 1. Tên có ý nghĩa

❌ BAD:
```abap
DATA lv_val TYPE i.
DATA lt_tab TYPE TABLE OF mara.
```

✅ GOOD:
```abap
DATA lv_po_count TYPE i.
DATA lt_purchase_orders TYPE TABLE OF ZI_PURCHASEORDER.
```

### 2. Một method, một việc

Method < 50 dòng, có thể giải thích bằng 1 câu.
Nếu method dài → tách.

### 3. Tránh SELECT ... ENDSELECT

❌ BAD (performance):
```abap
SELECT * FROM ztb_po INTO TABLE lt_po.
LOOP AT lt_po INTO ls_po.
  SELECT SINGLE * FROM ztb_po_item WHERE po_no = ls_po-po_no INTO ls_item.
ENDLOOP.
```

✅ GOOD (1 lần SELECT):
```abap
SELECT * FROM ztb_po INTO TABLE lt_po.
SELECT * FROM ztb_po_item FOR ALL ENTRIES IN lt_po
  WHERE po_no = lt_po-po_no INTO TABLE lt_items.
```

### 4. Không SELECT *

Luôn liệt kê field cần thiết.

❌ BAD:
```abap
SELECT * FROM ztb_po INTO TABLE lt_po.
```

✅ GOOD:
```abap
SELECT po_no, supplier, po_date, status
  FROM ztb_po
  INTO TABLE @DATA(lt_po).
```

### 5. Inline declaration

Dùng `DATA(... )` để giảm boilerplate.

```abap
LOOP AT lt_po INTO DATA(ls_po).
  " ...
ENDLOOP.
```

### 6. Type thay vì LIKE

```abap
DATA ls_po TYPE ZI_PURCHASEORDER.  " OK
DATA ls_po LIKE LINE OF lt_po.     " OK nhưng kém rõ ràng hơn
```

### 7. Constant

```abap
CONSTANTS: c_status_open  TYPE ztb_po_status VALUE 'OPEN',
            c_status_approved TYPE ztb_po_status VALUE 'APPR'.
```

### 8. Test class

```abap
CLASS ltc_po_helper DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS:
      test_validate_supplier FOR TESTING RAISING cx_static_check,
      test_calculate_total FOR TESTING RAISING cx_static_check.
ENDCLASS.
```

### 9. Không hardcode magic value

❌ BAD:
```abap
IF ls_po-status = 'OPEN'.
```

✅ GOOD:
```abap
IF ls_po-status = c_status_open.
```

### 10. Comment giải thích "tại sao", không phải "cái gì"

❌ BAD:
```abap
" Increment counter
lv_count = lv_count + 1.
```

✅ GOOD:
```abap
" Đếm số PO đã approved để log metric cho dashboard
lv_count = lv_count + 1.
```

### 11. RETURNING (và mọi param method) phải trỏ type đã đặt tên

Tham số **RETURNING** bắt buộc **complete type đã đặt tên** (data element DDIC hoặc `TYPES` tự định
nghĩa) — KHÔNG viết `LENGTH`/`DECIMALS` inline trong chữ ký method (chỉ hợp lệ trong `TYPES`/`DATA`).

❌ BAD → ADT báo *"A RETURNING parameter must be fully typed"*:
```abap
METHODS get_total RETURNING VALUE(rv) TYPE p LENGTH 15 DECIMALS 2.
```

✅ GOOD — định nghĩa type trong interface dùng chung (vd `ZIF_*_TYPES`):
```abap
" ZIF_FOO_TYPES:
TYPES ty_amount TYPE p LENGTH 15 DECIMALS 2.
" method:
METHODS get_total RETURNING VALUE(rv) TYPE zif_foo_types=>ty_amount.
```

IMPORTING/CHANGING vẫn cho phép generic `TYPE p`. *(memory: abap-returning-named-type)*

### 12. `CONV n( )` / `VALUE n( )` — KHÔNG construct được type generic

`n`, `p`, `c`, `x` (không kèm LENGTH/DECIMALS) là **type generic** — dùng trong constructor operator
(`CONV`/`VALUE`) → ADT báo *"A value of the generic type N cannot be constructed"*.

❌ BAD:
```abap
data(lv_year_prev) = CONV n( is_selection-year - 1 ).   " n generic -> activation fail
```

✅ GOOD — khai biến typed rồi gán (hoặc `CONV` sang type ĐÃ đặt tên / có length):
```abap
data lv_year_prev type n length 4.
lv_year_prev = is_selection-year - 1.
```
Áp cho mọi `CONV`/`VALUE`/`REDUCE` — target phải là type **complete** (có length). (verified ZCO04 2026-07-06)

### 13. ABAP SQL strict — literal KHÔNG được rộng hơn cột (narrowing bị cấm)

Strict SQL (ABAP Cloud) **cấm narrowing lossy**: so field với literal **dài hơn** kiểu cột → báo
*"type of 'X' cannot be converted to the type of `COLUMN`"* (activation fail), KHÔNG âm thầm truncate.

❌ BAD — `CostingVariant` là CHAR(4) nhưng literal 5 ký tự:
```abap
where costingvariant in ( 'ZUTG1', 'ZUTG2', 'ZUTG3' ).   " literal CHAR(5) > CHAR(4) -> fail
```

✅ Cách xử: dùng **host variable/range typed theo cột** (`RANGE OF <cds>-<field>`), hoặc nếu giá trị
literal **sai độ dài so với field thật** (dấu hiệu FS hiểu nhầm) → **verify field type + hỏi KH**, ĐỪNG
truncate cho "chạy được" (3 giá trị 5-ký-tự truncate về CHAR(4) có thể trùng nhau). (verified ZCO04 2026-07-06)

### 14. KHÔNG offset/length trực tiếp trên kết quả method call

`cl_abap_context_info=>get_system_date( )+0(4)` → lỗi *"Method ... does not have any parameters"* (ABAP
hiểu `( )+0(4)` là truyền tham số). Gán ra biến trước rồi mới `+off(len)`:
```abap
data(lv_today) = cl_abap_context_info=>get_system_date( ).
lv_year = lv_today+0(4).
```
(verified ZCL_ZCO04_QUERY 2026-07-06)

## Header cho mỗi file ABAP

```abap
"! <Mô tả ngắn 1 dòng>
"!
"! <Mô tả chi tiết (nếu cần)>
"!
"! \param {<type>} <name> <mô tả>
"! \return {<type>} <mô tả>
"!
"! Package: <package>
"! Author: <tên>
"! Date: <YYYY-MM-DD>
"! Version: 1.0
```

Hoặc dùng `---` để comment, dùng `!!` cho class doc.

## Khi nào phá vỡ quy tắc

Đã có ADR giải thích. Ví dụ: hardcode value cho magic constant trong config → có ADR.

## Reference

- SAP Clean ABAP: https://github.com/SAP/styleguides/blob/main/clean-abap/CleanABAP.md
- ABAP Keyword Documentation: https://help.sap.com/doc/abapdocu
