# Name Conversion Guide: Legacy → ABAP Cloud

Reference chi tiet cho skill `sap-clean-code` — vi du convert tung loai object tu Legacy ABAP
sang ABAP Cloud.

## Muc luc

- Class Names
- Method Names
- Variable Names
- Parameter Names

## Class Names

> **Luu y:** `/s4clean/` la namespace registered. Neu chua co namespace, dung `Z_` thay the (VD: `ZCL_MATERIAL_READER`).

```ABAP
" ❌ Legacy
CLASS zcl_bapi_material_read.
CLASS zcl_handle_bapi_return.
CLASS ycl_webshop_order_helper.

" ✅ ABAP Cloud (co namespace)
CLASS /s4clean/material_reader.
CLASS /s4clean/bapi_return_handler.
CLASS /s4clean/webshop_order_helper.

" ✅ ABAP Cloud (ko namespace - dung Z)
CLASS zcl_material_reader.
CLASS zcl_bapi_return_handler.
```

## Method Names

```ABAP
" ❌ Legacy
METHODS execute_bapi_material_getall.
METHODS call_bapi_transaction_commit.
METHODS get_list_of_open_orders_for_customer.

" ✅ ABAP Cloud
METHODS find_materials.
METHODS commit_transaction.
METHODS find_open_orders.
```

## Variable Names

```ABAP
" ❌ Legacy (Hungarian)
DATA: lv_matnr TYPE matnr,
      ls_mara TYPE mara,
      lt_mara TYPE TABLE OF mara,
      lv_lines TYPE i,
      lv_subrc TYPE sysubrc.

" ✅ ABAP Cloud
DATA: material_number TYPE matnr,
      material_data TYPE mara,
      materials TYPE TABLE OF mara,
      line_count TYPE i,
      subrc TYPE sysubrc.
```

## Parameter Names

```ABAP
" ❌ Legacy
METHODS get_material_description
  IMPORTING
    iv_matnr       TYPE matnr
    iv_spras       TYPE spras
  EXPORTING
    ev_maktx       TYPE maktx
    ev_subrc       TYPE sysubrc.

" ✅ ABAP Cloud
METHODS get_material_description
  IMPORTING
    material_number TYPE matnr
    language        TYPE spras
  RETURNING
    VALUE(result)   TYPE maktx
  RAISING
    cx_not_found.
```
