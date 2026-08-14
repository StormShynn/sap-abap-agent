---
name: sap-virtual-element
description: |
  Tao virtual element (calculated field) trong CDS view — field khong luu DB, tinh toan tai
  runtime khi Fiori/OData doc. Dung khi logic phuc tap (goi API, lookup, format dac biet) khong
  the tinh bang CDS expression don gian.
  KHONG dung cho logic don gian (vd price * quantity) — dung CDS expression thuan.
when_to_use: |
  "tao calculated field trong CDS view", "field nay can tinh luc runtime khong luu DB",
  "them virtual element cho X".
argument-hint: "[ten CDS view] [ten field can them]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Glob]
---

# SAP Virtual Element — Calculated field trong CDS view

## Khi nao dung

- ✅ Field derived tu nhieu nguon (text tu longtext, format tu nhieu field...).
- ✅ Field phu thuoc context (user language, system date, role).
- ✅ Field thay doi theo logic business (note, status text, computed value).
- ❌ Logic don gian (vd `price * quantity as amount`) — dung CDS expression thuan.
- ❌ Data can persist (audit, reporting) — luu DB binh thuong.

## Output

- 1 file class ABAP implement `if_sadl_exit_calc_element_read`.
- Update CDS view: them virtual element voi `@ObjectModel.virtualElementCalculatedBy`.

## Quy trinh

### Buoc 1: Khai bao trong CDS

```abap
define view entity ZI_<OBJECT>
  as select from <source> as items
{
  key items.<KeyField>,
      items.<Field1>,
      ...

      @ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_<CLASS_NAME>'
      cast( '' as abap.char( 1000 ) ) as <virtual_field>
}
```

Quy tac khai bao:
- Annotation `@ObjectModel.virtualElementCalculatedBy: 'ABAP:<class_name>'` — ten class ABAP,
  KHONG co prefix trong syntax (nhung class thuc te van dat ten theo quy uoc `ZCL_*`).
- `cast( '' as abap.char( 1000 ) )` — placeholder, type phai match field mong muon.

### Buoc 2: Implement class

```abap
CLASS zcl_<class_name> DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_sadl_exit.
    INTERFACES if_sadl_exit_calc_element_read.
ENDCLASS.

CLASS zcl_<class_name> IMPLEMENTATION.

  METHOD if_sadl_exit_calc_element_read~calculate.
    DATA: lt_data TYPE STANDARD TABLE OF zi_<object> WITH DEFAULT KEY.
    lt_data = CORRESPONDING #( it_original_data ).

    LOOP AT lt_data ASSIGNING FIELD-SYMBOL(<lfs_data>).
      <lfs_data>-<virtual_field> = compute_value( <lfs_data> ).
    ENDLOOP.

    ct_calculated_data = CORRESPONDING #( lt_data ).
  ENDMETHOD.

  METHOD if_sadl_exit~get_exit_info.
    rs_exit_info-def_entity = VALUE #( ( entity = 'ZI_<OBJECT>' ) ).
  ENDMETHOD.

ENDCLASS.
```

### Buoc 3: Test

```abap
CLASS ltc_<class_name> DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS test_calculate FOR TESTING RAISING cx_static_check.
ENDCLASS.

CLASS ltc_<class_name> IMPLEMENTATION.
  METHOD test_calculate.
    DATA(lt_input) = VALUE zi_<object>( ( <KeyField> = '1000001' ... ) ).
    DATA(lt_calculated) = lt_input.

    zcl_<class_name>=>if_sadl_exit_calc_element_read~calculate(
      EXPORTING it_original_data  = lt_input
      CHANGING  ct_calculated_data = lt_calculated
    ).

    cl_abap_unit_assert=>assert_not_initial( lt_calculated[ 1 ]-<virtual_field> ).
  ENDMETHOD.
ENDCLASS.
```

## Gotcha: field timestamp `utclong` — KHONG convert sang packed (overflow)

Mot so field ngay/gio trong CDS released la kieu **`utclong`** (so noi bo ~17-18 chu so), KHONG
phai `DEC15` dang `yyyymmddhhmmss` — de nham nhau vi ca hai deu "trong nhu" con so ngay gio.

- Gan truc tiep vao tham so `p LENGTH 8 DECIMALS 0` (15 chu so) -> `:=` overflow ->
  `CX_SY_ARITHMETIC_OVERFLOW` -> trong `if_sadl_exit_calc_element_read` bung thanh
  `CX_SADL_EXIT_PROCESSING_ERROR` -> **short dump khi mo app** (khong loi luc activate).
- ✅ So sanh 2 timestamp **truc tiep** (`actual > planned`, kem `IS NOT INITIAL`) — KHONG convert
  sang packed. Can tach ngay tu utclong thi dung `CONVERT UTCLONG ... INTO DATE ... TIME ZONE`.
- Helper method nen nhan `abap_bool` (da tinh san o noi goi) thay vi nhan timestamp voi kieu cung,
  de khong phu thuoc kieu field that. **Verify kieu field that truoc** (F2 data element trong ADT
  hoac `SELECT ... INTO @DATA(...)` de lay kieu tu view) — KHONG doan `utclong` hay `timestamp`.

## Performance considerations

Virtual element duoc tinh cho **moi row** khi doc -> neu logic nang (goi API), can nhac:
- Cache ket qua trong memory.
- Batch API call (1 call lay data cho nhieu row).
- Dung join/association thay vi tinh.
- KHONG dung virtual element cho logic chay > 100ms/row.

## Reference

- Interface: `if_sadl_exit_calc_element_read`.
- Skill `sap-clean-code` — quy uoc dat ten class/CDS.
