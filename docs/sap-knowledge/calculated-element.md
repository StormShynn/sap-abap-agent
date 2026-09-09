# Calculated Element (Virtual Field) trong CDS

Khi cần field "tính toán tại runtime" (không lưu DB), dùng **calculated element** với class impl `if_sadl_exit_calc_element_read`.

## Pattern

### Bước 1: Khai báo trong CDS

```abap
define view entity ZSCM_I_PR_ITEMS
  as select from I_PurchaseRequisitionItemAPI01 as items
  {
    key items.PurchaseRequisition,
    key items.PurchaseRequisitionItem,
        items.Material,
        
        " Calculated field (không lưu DB, tính lúc runtime)
        @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_GET_ITEM_NOTE'
        cast( '' as abap.char( 1000 ) ) as note,
        
        " Field khác cũng tính tương tự
        @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_GET_ITEM_NOTE'
        cast( '' as abap.char( 1000 ) ) as mucdichsd
  }
```

### Bước 2: Implement class

```abap
CLASS zcl_get_item_note DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_sadl_exit.
    INTERFACES if_sadl_exit_calc_element_read.
ENDCLASS.

CLASS zcl_get_item_note IMPLEMENTATION.
  METHOD if_sadl_exit_calc_element_read~calculate.
    " 1. Nhận input
    DATA: lt_data TYPE STANDARD TABLE OF zscm_i_pr_items WITH DEFAULT KEY.
    lt_data = CORRESPONDING #( it_original_data ).
    
    " 2. Loop, tính toán cho mỗi row
    LOOP AT lt_data ASSIGNING FIELD-SYMBOL(<lfs_data>).
      " Logic tính note: gọi API, lookup text, etc.
      <lfs_data>-note     = compute_note( <lfs_data> ).
      <lfs_data>-mucdichsd = compute_purpose( <lfs_data> ).
    ENDLOOP.
    
    " 3. Trả về
    ct_calculated_data = CORRESPONDING #( lt_data ).
  ENDMETHOD.

  METHOD if_sadl_exit~get_exit_info.
    " Khai báo class này handle các field nào
    rs_exit_info-def_entity = VALUE #( ( entity = 'ZSCM_I_PR_ITEMS' ) ).
  ENDMETHOD.
ENDCLASS.
```

## Khi nào dùng

- ✅ Field derived từ nhiều nguồn (gọi API, lookup text, format...).
- ✅ Field phụ thuộc context (user language, system date).
- ✅ Field không muốn lưu DB (transient, thay đổi theo logic business).
- ❌ KHÔNG dùng cho field thuần tính toán đơn giản (dùng CDS virtual element với cú pháp đơn giản hơn).
- ❌ KHÔNG dùng khi data cần persist.

## So sánh với CDS virtual element thuần

```abap
" CDS virtual element thuần (no ABAP class):
define view ZI_FOO
  as select from ztb_foo
{
  key id,
      price,
      currency,
      
      " Tính amount = price * quantity
      @Semantics.amount.currencyCode: 'currency'
      price * quantity as amount
}
```

Dùng khi logic **đơn giản**, có thể tính trong CDS. Khi logic phức tạp (gọi API, lookup) → dùng class như trên.

## Gotcha: timestamp `utclong` — KHÔNG convert sang packed (overflow)

Field ngày giờ trong CDS TM released (vd `I_TransportationOrderStop_2.TranspOrdStopApptEndDteTme`,
`I_TransportationOrderEvent.TranspOrdEvtActualDateTime`) là **`utclong`** (số nội bộ ~17–18 chữ số),
KHÔNG phải DEC15 `yyyymmddhhmmss`.

- Gán vào tham số `p LENGTH 8 DECIMALS 0` (15 chữ số) → `:=` overflow → **`CX_SY_ARITHMETIC_OVERFLOW`**
  → trong `if_sadl_exit_calc_element_read` bung thành `CX_SADL_EXIT_PROCESSING_ERROR` → **short dump khi mở app**.
- ✅ So sánh 2 timestamp TM **trực tiếp** (`actual > planned`, kèm `IS NOT INITIAL`) — KHÔNG convert sang
  packed. Cần tách ngày từ utclong → `CONVERT UTCLONG ... INTO DATE ... TIME ZONE`.
- Helper thuần nên nhận `abap_bool` (đã tính sẵn) thay vì nhận timestamp có kiểu cứng, để không phụ thuộc
  kiểu field. Kiểu field TM = [Unverified] cho tới khi verify View Browser. *(memory: tm-timestamp-utclong-overflow; gặp ở ZSD18 ZCL_VE_ZSD18)*

## Reference

- SAP doc: https://help.sap.com/docs/abap-cloud/abap-rap/virtual-element
- Interface: `if_sadl_exit_calc_element_read`
- Ví dụ thật: `examples/ITC_SCM_PO_V101/src/zcl/zcl_po_print.clas.abap` (sẽ thêm)
