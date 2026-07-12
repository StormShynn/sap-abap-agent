---
name: sap-clean-code
description: Huong dan clean code & name conversion cho SAP ABAP Public Cloud (ABAP Cloud). Dung khi user hoi ve naming conventions, clean ABAP code style, name conversion tu legacy ABAP sang ABAP Cloud, quy tac dat ten cho development objects.
when_to_use: |
  "dat ten class nay dung chuan chua", "convert code legacy sang ABAP Cloud",
  "review naming convention", "gioi han do dai ten CDS view la bao nhieu".
effort: medium
model: haiku
---

# SAP ABAP Clean Code & Name Conversion (Public Cloud)

## Tong quan

ABAP Cloud (SAP S/4HANA Cloud, Public Edition) yeu cau tuan thu **Clean Core** — chi su dung released APIs, tuan thu naming conventions, va viet code sach, de bao tri.

Tai lieu tham khao:
- [Clean ABAP Style Guide (GitHub SAP/styleguides)](https://github.com/SAP/styleguides/blob/main/clean-abap/CleanABAP.md)
- [ABAP Language in ABAP Cloud](https://help.sap.com/docs/abap-cloud/abap-cloud/abap-language)
- [ABAP Programming Guidelines](https://help.sap.com/doc/abapdocu_latest_index_htm/latest/en-US/index.htm?file=abenabap_pgl.htm)
- [Naming Conventions for Development Objects](https://help.sap.com/docs/abap-cloud/abap-rap/naming-conventions-for-development-objects)
- [ABAP Test Cockpit / Code Inspector](https://help.sap.com/docs/ABAP_PLATFORM_NEW/fc4c71aa50014fd1b43721701471913d/8b8f9d8f3cb948b2841d6045a255e503.html)

## 1. Naming Conventions co ban

> **Quan trong:** Trong ABAP Cloud, **moi** development object do customer tao ra **bat buoc** phai bat dau bang `Z` hoac `Y`. Day la quy dinh cua SAP, khong duoc dung tien to khac.
>
> Namespace `/prefix/` (VD: `/s4clean/`) chi duoc su dung neu da dang ky namespace voi SAP. Neu chua co namespace registered, dung `Z_` thay the.
>
> ⚠️ **Rao chan an toan (ap dung cho MOI thao tac tao/sua/xoa, khong chi luc dat ten):** object
> KHONG bat dau bang `Z`/`Y` (hoac namespace `/registered/` cua customer) la object **chuan SAP**
> — TUYET DOI KHONG tao/sua/xoa, ke ca khi user yeu cau truc tiep. Neu 1 yeu cau co ve dung cham
> object ngoai Z/Y, DUNG lai va hoi ro user truoc khi lam gi tiep (xem chi tiet quy trinh + pham
> vi package trong skill `sap-deployment-target`). Doc/SELECT/association toi object chuan qua
> released API/CDS van OK — rao chan chi ap dung cho **tao moi/sua/xoa**. Co backstop ky thuat:
> `hooks/zy_namespace_guard.py` (PreToolUse) tu dong chan goi tool DDIC/CDS/RAP create/update/delete
> nham vao ten khong phai Z/Y.

### Gioi han ky tu & do dai ten

- ABAP chi ho tro **ASCII** — khong duoc dung tieng Viet co dau (UTF-8) trong ten.
- Gioi han do dai: **30 ky tu** cho tat ca development objects (class, interface, method, variable, CDS view, data element, ...).
- Khi vuot 30 ky tu, viet tat tu *cuoi* (tu *it quan trong* nhat).

### Snake Case (khuyen dung)

ABAP la case-insensitive, nen dung `snake_case` de dam bao doc duoc:

```ABAP
" ✅ Dep
DATA max_wait_time_in_seconds TYPE i.
METHODS read_user_preferences.

" ❌ Khong dep
DATA maxresponsetimeinmilliseconds TYPE i.
DATA mw_tis TYPE i.
```

Vi du viet tat khi vuot 30 ky tu:

```ABAP
" Kho: `maximum_execution_time_in_milliseconds` (38 ky tu)
" -> `max_execution_time_in_ms` (26 ky tu) ✅
" -> `max_exe_time_in_millisec` (26 ky tu) ✅
" -> `maxexectimeinmillisec` (20 ky tu) ❌ (flatcase)
```

### Dat ten mo ta, co y nghia

```ABAP
" ✅ Ten ro rang
CONSTANTS max_wait_time_in_seconds TYPE i ...
DATA customizing_entries TYPE STANDARD TABLE ...
METHODS read_user_preferences ...
CLASS /clean/user_preference_reader ...

" ❌ Ten toi (tap trung vao kieu du lieu)
CONSTANTS sysubrc_04 TYPE sysubrc ...
DATA iso3166tab TYPE STANDARD TABLE ...
METHODS read_t005 ...
CLASS /dirty/t005_reader ...
```

## 2. Clean ABAP — Naming Rules

### BO KRY HUNGARIAN NOTATION (tieng to kieu du lieu)

Day la thay doi lon nhat tu legacy ABAP sang ABAP Cloud.

```ABAP
" ❌ Legacy ABAP: Hungarian notation
DATA lv_name TYPE string.
DATA ls_address TYPE ty_address.
DATA lt_users TYPE STANDARD TABLE OF user.
DATA lr_ref TYPE REF TO object.
DATA lv_result TYPE i.
FIELD-SYMBOLS <ls_entry> TYPE ty_entry.

" ✅ ABAP Cloud: ten mo ta
DATA name TYPE string.
DATA address TYPE ty_address.
DATA users TYPE STANDARD TABLE OF user.
DATA reference TYPE REF TO object.
DATA result TYPE i.
FIELD-SYMBOLS <entry> TYPE ty_entry.
```

### Quy tac cu the:

| Tieng to | Legacy | Clean ABAP |
|----------|--------|------------|
| Local variable | `lv_<name>` | `<name>` |
| Static variable | `gv_<name>` | `<name>` (class attribute) |
| Global variable | `gv_<name>` | **Khong dung** (dung instance attribute) |
| Structure | `ls_<name>` / `gs_<name>` | `<name>` |
| Table | `lt_<name>` / `gt_<name>` | `<name>` (plural) |
| Reference | `lr_<name>` / `gr_<name>` | `<name>` / `ref_<name>` |
| Object ref | `mo_<name>` / `go_<name>` | `<name>` / `instance` |
| Parameter (import) | `iv_<name>` / `it_<name>` | `<name>` |
| Parameter (export) | `ev_<name>` / `et_<name>` | `<name>` |
| Parameter (return) | `rv_<name>` / `rt_<name>` | `result` |
| Changing param | `cv_<name>` / `ct_<name>` | `<name>` |

### Tu bo "noise words" (data, info, object)

```ABAP
" ❌ Noise words
DATA account_data TYPE ...
DATA alert_object TYPE ...
DATA user_info TYPE ...

" ✅ Sach
DATA account TYPE ...
DATA alert TYPE ...
DATA user_preferences TYPE ...
```

### Danh tu cho class, dong tu cho method

```ABAP
" ✅ Class = danh tu
CLASS /clean/account.
CLASS /clean/user_preferences.
INTERFACE /clean/customizing_reader.

" ✅ Method = dong tu
METHODS withdraw.
METHODS add_message.
METHODS read_entries.
METHODS is_empty.  " Boolean methods bat dau bang is_/has_
```

### Mot tu cho mot concept

```ABAP
" ✅ Nhat quan
METHODS read_this.
METHODS read_that.
METHODS read_those.

" ❌ Luc nac
METHODS read_this.
METHODS retrieve_that.
METHODS query_those.
```

### Dat ten so nhieu cho table/bang

```ABAP
" ✅ So nhieu
DATA countries TYPE STANDARD TABLE OF country.
METHODS find_users_by_role.
CLASS /clean/accounts.

" ❌ So it
DATA country TYPE STANDARD TABLE OF country.
METHODS find_user_by_role.
CLASS /clean/account.  " neu chi la 1 account
```

## Chi tiet day du (doc khi can, khong load san)

- **Name Conversion Guide** (Legacy → ABAP Cloud: class/method/variable/parameter voi vi du day du) — [reference/name-conversion.md](reference/name-conversion.md)
- **ABAP Cloud Specific Rules** (Development Object Naming; CDS VDM 5-layer; bien the ticket-based; CDS field/association/annotation/parameter/table function/abstract entity/projection naming; RAP BO naming) — [reference/abap-cloud-rules.md](reference/abap-cloud-rules.md)
- **Checklists & Cong Cu** (field symbol, constants/enums, exception class, DI/testing pattern, clean code rules quan trong — SRP/fail-fast/RETURNING/strict SQL, Released APIs checklist chi tiet, ABAP Formatter, Code Inspector/ATC config chi tiet) — [reference/checklists.md](reference/checklists.md)

## 13. Cheat Sheet: Legacy vs ABAP Cloud

| Legacy | ABAP Cloud | Ghi chu |
|--------|------------|---------|
| `lv_name` | `name` | Bo tien to kieu |
| `ls_address` | `address` | Bo loai struct |
| `lt_users` | `users` | Danh tu so nhieu |
| `lr_ref` | `ref` / `reference` | Bo loai reference |
| `iv_param` | `param` / `input_param` | Import param |
| `ev_result` | `result` (neu RETURNING) | Export param |
| `rv_result` | `result` | Returning param |
| `gc_const` | `some_constant` | Bo tien to gc_ |
| `ZCL_...` | `/prefix/...` | Namespace `/` |
| `ZIF_...` | `/prefix/if_...` | Interface |
| `SELECT ... INTO TABLE @itab` | `SELECT ... INTO TABLE @result` | Inline declaration |
| `LOOP AT ... INTO wa` | `LOOP AT ... INTO REF TO` | Field-symbol hoac REF TO |
| `CREATE OBJECT` | `NEW #( )` | Constructor expression |
| `CALL METHOD` | `method( )` | Functional call |

## Reference

- `reference/name-conversion.md`, `reference/abap-cloud-rules.md`, `reference/checklists.md` — chi tiet day du, doc khi can (xem muc "Chi tiet day du" o tren).
- Skill `sap-extensibility` — bac thang extensibility, dung chung quy uoc dat ten CDS.
- Skill `sap-atc-review` — chay check naming/released-API tu dong (script), doi chieu voi convention trong file nay.
- Skill `sap-scaffold-rap` / `sap-scaffold-cds` — noi ap dung quy uoc dat ten khi sinh code.
