---
name: sap-badi-enhancement
description: Huong dan BAdI va Enhancement trong SAP S/4HANA Cloud Public Edition — Cloud BAdI, enhancement spot, BAdI definition, BAdI implementation, key-user extensibility, Custom Logic (Cloud BAdI).
when_to_use: |
  "them BAdI trong ABAP Cloud", "Cloud BAdI vs classic BAdI", "enhancement spot",
  "key user BAdI", "Custom Logic trong Public Cloud".
argument-hint: "[cau hoi ve BAdI / enhancement / Cloud BAdI]"
effort: medium
model: sonnet
---

# Cloud BAdI & Enhancement — ABAP Cloud

## 1. Kien truc tong quan

Tren ABAP Cloud, **chi co the dung BAdI do SAP release san** (Cloud BAdI). KHONG tu tao BAdI
definition tren ABAP Cloud (tru BTP Steampunk, noi co the tu tao).

| Loai | Tren S/4HANA Cloud | Tren BTP Steampunk |
|------|-------------------|-------------------|
| Cloud BAdI (released san) | ✅ Dung duoc (Custom Logic) | ✅ Dung duoc |
| Tu tao BAdI definition | ❌ | ✅ |
| Tu tao BAdI implementation | ✅ | ✅ |
| Classic BAdI (SE18/19) | ❌ | ❌ |
| Enhancement point/section | ❌ | ❌ |
| User exit (CMOD/SMOD) | ❌ | ❌ |

## 2. Cloud BAdI tren S/4HANA Cloud

Cloud BAdI la cac diem mo rong SAP da release san cho Key User va Developer:

**Key User (Custom Logic)**:
- Vao app Fiori **Custom Fields and Logic** -> tab **Custom Logic**
- Chon Business Context + BAdI tu danh muc SAP release
- Viet ABAP logic don gian (validation, derivation) bang cu phap rut gon **ABAP for Key Users**
- KHONG can developer
- Thao tac tung buoc tren Fiori app + rang buoc cu phap chi tiet: xem skill `sap-key-user-toolkit` §3.2

**Developer (Cloud BAdI Implementation)**:
- Tao ABAP class implement BAdI definition
- Dung `GET BADI` + `CALL BADI` trong code
- Can developer ABAP Cloud knowledge

## 3. Tim Cloud BAdI release san

Cach tim BAdI co the dung tren he thong:

```abap
" Kiem tra BAdI definition co release cho cloud khong
SELECT * FROM sbi_badi_def
  WHERE badi_name = 'BADI_NAME_HERE'
  AND cloud_released = 'X'
  INTO TABLE @lt_badis.
```

Hoac tra cuu SAP API Business Hub (section "Enhancement Options").

## 4. Tao BAdI Implementation

```abap
" 1. Tao class implement BAdI interface
CLASS zcl_badi_my_impl DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_ex_badi_name.
ENDCLASS.

CLASS zcl_badi_my_impl IMPLEMENTATION.
  METHOD if_ex_badi_name~method_name.
    " custom logic here
  ENDMETHOD.
ENDCLASS.

" 2. Dung trong code
DATA(lo_badi) = CAST cl_badi_interface(
  cl_badi_factory=>get_badi( badi_name = 'BADI_NAME' )
).

CALL BADI lo_badi->if_ex_badi_name~method_name(
  IMPORTING ev_result = lv_result
).
```

Tren ABAP Cloud, `cl_badi_factory` la class duoc release.

## 5. Custom Logic (Key User) — gioi han o cap implementation

Quy trinh thao tac tung buoc (vao app, chon Business Context, chon BAdI, phan biet 2 loai
Validation/Determination, viet logic bang cu phap ABAP for Key Users, active/assign scope) +
rang buoc cu phap ABAP for Key Users: xem skill `sap-key-user-toolkit` §3.2 — skill do di sau
vao thao tac Fiori app cho key user, kem vi du Validation/Determination cu the.

**Gioi han Key User Custom Logic o cap implementation** (khac voi rang buoc cu phap ABAP for
Key Users da liet ke o skill `sap-key-user-toolkit` §3.2 — day la gioi han rieng cua co che
BAdI implementation, khong phai gioi han ngon ngu):
- Chi 1 BAdI implementation active
- Khong the goi external service (HTTP, RFC)
- Gioi han ve cu phap ABAP (khong REFRESH, khong EXPORT/IMPORT)
- Debug gioi han (chi ADT trace)

## 6. BAdI Filtering

```abap
" Filter BAdI implementation bang filter value
cl_badi_factory=>get_badi(
  filter_table = VALUE cl_badi_factory=>ty_filter_table(
    ( name = 'ORGANIZATION' value = lv_org )
    ( name = 'PURCH_GROUP' value = lv_group )
  )
  badi_name = 'BADI_NAME'
).
```

## 7. Kien truc khi can Custom Logic

Khi can custom logic (validation, derive, check), ap dung bac thang:

1. **Cloud BAdI (Custom Logic)**: Neu SAP release BAdI cho use case do
2. **RAP Behavior**: Neu la RAP BO, viet validation/determination trong behavior definition
3. **Key User Field Logic**: Custom field + logic don gian
4. **Side-by-side BTP**: Khi khong co BAdI nao dap ung, can custom service tren BTP

## 8. BAdI vs RAP Behavior

| Tinh huong | Dung |
|------------|------|
| Validate truoc khi save RAP BO | RAP behavior (trigger validate) |
| Thay doi field khi user nhap | RAP determination |
| Hook sau khi save BO | RAP behavior (after save) |
| Hook o he thong khac (VD pricing) | Cloud BAdI |
| Thay doi output form | Output Management BAdI |
| Custom check truoc khi approve | CB BAdI (Workflow) |

## Nguon tham khao

- SAP Help Portal: Cloud BAdI, Custom Logic
- API Business Hub: BAdI definitions
- SAP Community: "ABAP Cloud BAdI vs RAP Behavior"
