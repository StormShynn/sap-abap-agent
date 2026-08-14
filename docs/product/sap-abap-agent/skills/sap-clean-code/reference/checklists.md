# Checklists & Cong Cu — Naming Chi Tiet, Clean Code Rules, Released API, ATC

Reference chi tiet cho skill `sap-clean-code` — field symbol/constants/exception/DI naming, clean
code rules quan trong, checklist Released API, va cau hinh Code Inspector/ATC.

## Muc luc

- Dat ten cho Field Symbols
- Constants va Enums
- Naming cho Exception Classes
- Naming Pattern cho Dependency Injection / Testing
- Clean Code Rules Quan Trong
- ABAP Cloud Released APIs Checklist
- ABAP Formatter & Auto-check
- Code Inspector (SCI) & ATC Checks

## Dat ten cho Field Symbols

Field symbols **luon** duoc bao boi `<>`:

```ABAP
" ✅ Dep
FIELD-SYMBOLS <entry> TYPE any.
FIELD-SYMBOLS <material> TYPE ty_material.
FIELD-SYMBOLS <order> TYPE ty_order.

" ❌ Legacy
FIELD-SYMBOLS <fs_entry> TYPE any.
FIELD-SYMBOLS <ls_material> TYPE ty_material.
```

## Constants va Enums

```ABAP
" ✅ Clean ABAP
CONSTANTS:
  BEGIN OF order_status,
    new      TYPE string VALUE 'N',
    approved TYPE string VALUE 'A',
    shipped  TYPE string VALUE 'S',
    closed   TYPE string VALUE 'C',
  END OF order_status.
  
" Gọi: order_status-new, order_status-shipped

" ❌ Legacy
CONSTANTS:
  gc_order_status_new      TYPE string VALUE 'N',
  gc_order_status_approved TYPE string VALUE 'A'.
```

## Naming cho Exception Classes

```ABAP
" ✅ ABAP Cloud
CLASS cx_s4clean_not_found DEFINITION INHERITING FROM cx_static_check.
CLASS cx_s4clean_validation_error DEFINITION INHERITING FROM cx_static_check.
CLASS cx_s4clean_unauthorized DEFINITION INHERITING FROM cx_no_check.

" ❌ Legacy
CLASS zcx_material_not_found DEFINITION.
CLASS zcx_bapi_error DEFINITION.
```

## Naming Pattern cho Dependency Injection / Testing

```ABAP
" Interface
INTERFACE /s4clean/if_material_reader.
  METHODS read
    IMPORTING
      material_id TYPE matnr
    RETURNING
      VALUE(result) TYPE ty_material.
ENDINTERFACE.

" Production implementation
CLASS /s4clean/material_reader DEFINITION
  CREATE PUBLIC
  FINAL.
  PUBLIC SECTION.
    INTERFACES /s4clean/if_material_reader.
ENDCLASS.

" Test double (local test class)
CLASS ltd_material_reader DEFINITION
  CREATE PUBLIC
  FINAL.
  PUBLIC SECTION.
    INTERFACES /s4clean/if_material_reader.
ENDCLASS.

" Code under test
CLASS lcl_handler DEFINITION
  CREATE PUBLIC
  FINAL.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        material_reader TYPE REF TO /s4clean/if_material_reader.
  PRIVATE SECTION.
    DATA material_reader TYPE REF TO /s4clean/if_material_reader.
ENDCLASS.
```

## Clean Code Rules Quan Trong

### SRP: Mot method lam mot viec

```ABAP
" ✅ Dep
METHODS validate_input.
METHODS save_to_database.
METHODS send_notification.

" ❌ Legacy - 1 method lam 3 viec
METHODS validate_save_notify.
```

### Fail Fast (Guard Clauses)

```ABAP
METHOD read_material.
  IF material_id IS INITIAL.
    RAISE EXCEPTION TYPE cx_s4clean_invalid_input.
  ENDIF.
  " ... logic chinh ...
ENDMETHOD.
```

### Prefer RETURNING to EXPORTING

```ABAP
" ✅ Dep (RETURNING)
METHODS get_document_count
  RETURNING VALUE(result) TYPE i.

" ❌ Legacy (EXPORTING)
METHODS get_document_count
  EXPORTING
    count TYPE i.
```

### Dat ten RETURN parameter la RESULT

```ABAP
" ✅ Dep
METHODS get_name
  RETURNING VALUE(result) TYPE string.

" ❌ Khong dep
METHODS get_name
  RETURNING VALUE(name) TYPE string.
```

### RETURNING (va moi param method) phai tro type da dat ten

Tham so **RETURNING** bat buoc **complete type da dat ten** (data element DDIC hoac `TYPES` tu
dinh nghia) — KHONG viet `LENGTH`/`DECIMALS` inline trong chu ky method (chi hop le trong
`TYPES`/`DATA`).

```ABAP
" ❌ ADT bao "A RETURNING parameter must be fully typed"
METHODS get_total RETURNING VALUE(rv) TYPE p LENGTH 15 DECIMALS 2.

" ✅ Dinh nghia type trong interface dung chung
" ZIF_FOO_TYPES: TYPES ty_amount TYPE p LENGTH 15 DECIMALS 2.
METHODS get_total RETURNING VALUE(rv) TYPE zif_foo_types=>ty_amount.
```

IMPORTING/CHANGING van cho phep generic `TYPE p`.

### `CONV n( )` / `VALUE n( )` — KHONG construct duoc type generic

`n`, `p`, `c`, `x` (khong kem LENGTH/DECIMALS) la **type generic** — dung trong constructor
operator (`CONV`/`VALUE`/`REDUCE`) se bi ADT bao *"A value of the generic type N cannot be
constructed"*.

```ABAP
" ❌ n generic -> activation fail
DATA(lv_year_prev) = CONV n( is_selection-year - 1 ).

" ✅ Khai bien typed roi gan (hoac CONV sang type DA dat ten / co length)
DATA lv_year_prev TYPE n LENGTH 4.
lv_year_prev = is_selection-year - 1.
```

### ABAP SQL strict — literal KHONG duoc rong hon cot (narrowing bi cam)

Strict SQL (ABAP Cloud) cam narrowing lossy: so field voi literal **dai hon** kieu cot -> bao
*"type of 'X' cannot be converted to the type of `COLUMN`"* (activation fail), KHONG am tham
truncate.

```ABAP
" ❌ field CHAR(4) nhung literal 5 ky tu -> fail
WHERE material_group IN ( 'ABCDE' ).
```

Fix: dung host variable/range typed theo cot, hoac neu literal sai do dai so voi field that (dau
hieu hieu nham yeu cau) -> verify field type + hoi lai, DUNG truncate cho "chay duoc".

### Khong offset/length truc tiep tren ket qua goi method

`cl_abap_context_info=>get_system_date( )+0(4)` -> loi *"Method ... does not have any
parameters"* (ABAP hieu `( )+0(4)` la truyen tham so). Gan ra bien truoc roi moi `+off(len)`:

```ABAP
DATA(lv_today) = cl_abap_context_info=>get_system_date( ).
lv_year = lv_today+0(4).
```

## ABAP Cloud Released APIs Checklist

ABAP Cloud yeu cau **Clean Core**: chi duoc su dung **released APIs** cua SAP. Day la quy dinh bat buoc, khong phai tuy chon.

### Released API la gi?

Released API la nhung doi tuong phat trien (class, interface, CDS view, function module, BAPI, ...) ma SAP cam ket **on dinh** — khong thay doi signature hoac behavior trong cac ban upgrade.

- **C1 contract**: API duoc release on dinh, co the dung trong ABAP Cloud.
- **C0 contract**: Chi dung noi bo SAP, **KHONG duoc** dung tu code customer.
- **Unreleased**: Khong co stability contract, co the bi thay doi bat ky luc nao.

> **Luat bat buoc:** Trong ABAP Cloud language version, code **KHONG THE** goi truc tiep unreleased APIs. Trinh bien dich se bao loi.

### Kiem tra API release status trong ADT

#### Cach 1: API State indicator

Khi mo bat ky doi tuong nao trong ADT, nhin vao **goc phai tab editor**:

```
🟢 Released     — API co C1 contract, duoc phep dung
🟡 Deprecated   — Van dung duoc nhung sap bi thay the (nen chuyen sang API moi)
🔴 Unreleased   — KHONG duoc dung trong ABAP Cloud
```

#### Cach 2: ABAP Repository Tree (Released Objects)

1. **Right-click** ABAP project → **New** → **ABAP Repository Tree**
2. Select **Released Object** lam tree type
3. Trong property filter, nhap `api:` va `Ctrl+Space` de xem danh sach API types:
   - `USE_IN_CLOUD_DEVELOPMENT` — chi released APIs
   - `USE_IN_CLOUD_DEVELOPMENT_EXTENDED` — released APIs + extension points
4. Tree nay chi hien thi nhung object duoc release cho cloud.

#### Cach 3: Properties view

Chon object → **Properties** (F3) → tab **API State**:

| Field | Y nghia |
|-------|---------|
| `Release State` | `Released` / `Unreleased` / `Deprecated` |
| `Contract` | `C1` (cloud-safe) / `C0` (internal) |
| `Cloud Development` | `Allowed` / `Not Allowed` |
| `Since Release` | Ban ABAP release dau tien duoc release |

### Nhung released APIs quan trong cho ABAP Cloud

| Loai | Vi du | Ghi chu |
|------|-------|---------|
| **CDS View** | `I_Product`, `C_SalesOrder`, `I_BusinessPartner` | CDS views la released APIs co ban nhat |
| **RAP BO** | `R_Product`, `R_SalesOrder` | RAP business objects |
| **Class** | `CL_ABAP_UNIT_ASSERT`, `CL_HTTP_CLIENT` | Kiem tra API state tung class |
| **Interface** | `IF_ABAP_UNIT_CONSTANTS` | Interface co the released hoac khong |
| **BAPI** | `BAPI_MATERIAL_GETLIST` | BAPI can kiem tra API release status |
| **Function** | `DDIF_FIELDINFO_GET` | Phan lon function modules cu la unreleased |
| **Data Element** | `MATNR`, `SPRAS` | Data elements thuong la released (C1) |

### Checklist: Kiem tra code co dung released APIs khong

Truoc khi activate / commit, kiem tra:

- [ ] **ATC check ABAP_CLOUD_READINESS** — quet toan bo code tim unreleased APIs
- [ ] **Khong co goi** `CALL FUNCTION` vao function module cu (unreleased)
- [ ] **Khong co SELECT** truc tiep vao bang SAP (`MARA`, `VBAK`, ...) — phai qua CDS views
- [ ] **Khong co** `MODIFY`, `DELETE`, `INSERT` truc tiep vao bang SAP
- [ ] **Khong goi** class method unreleased (kien tra API State)
- [ ] **Khong su dung** `ABAP_SLEEP` hoac `WAIT UP TO` — dung `IF_ABAP_CLOUD_UTILITY` hoac `CL_ABAP_SLEEP` (released)
- [ ] **Cham deprecation notices** — neu API co trang thai Deprecated, can chuyen sang API moi
- [ ] **Custom wrapper** — neu that su can dung unreleased API, tao wrapper class va tu release (neu co quyen)

### Cach xu ly khi can dung unreleased API

**Tinh huong:** Can dung 1 class / FM khong duoc release.

| Cach | Mo ta | Khi nao dung |
|------|-------|-------------|
| **Wrapper** | Tao class wrapper goi unreleased API, danh dau la `@deprecated` | Khi that su can, khong co alternative |
| **CDS thay the** | Dung CDS view thay cho table truc tiep | Luon uu tien, CDS la released |
| **RAP BO thay the** | Dung RAP business object thay cho BAPI cu | Khi can modify data |
| **Cloud API** | Tim API thay the trong SAP API Business Hub | Nen uu tien nhat |

Vi du wrapper (dung `@deprecated` de danh dau cho team):

```ABAP
CLASS zcl_unreleased_wrapper DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    "! @deprecated Use CDS view I_Product instead
    METHODS get_product_data
      IMPORTING
        product_id     TYPE string
      RETURNING
        VALUE(result)  TYPE string
      RAISING
        cx_static_check.

  PRIVATE SECTION.
    METHODS call_unreleased_api
      IMPORTING
        product_id     TYPE string
      RETURNING
        VALUE(result)  TYPE string
      RAISING
        cx_static_check.
ENDCLASS.

CLASS zcl_unreleased_wrapper IMPLEMENTATION.
  METHOD get_product_data.
    result = call_unreleased_api( product_id ).
  ENDMETHOD.

  METHOD call_unreleased_api.
    TRY.
        " Goi unreleased API - ATC se canh bao o day
        CALL FUNCTION 'UNRELEASED_FUNCTION'
          EXPORTING
            product_id = product_id
          IMPORTING
            data       = result.
      CATCH cx_root INTO DATA(error).
        RAISE EXCEPTION TYPE cx_static_check
          EXPORTING
            previous = error.
    ENDTRY.
  ENDMETHOD.
ENDCLASS.
```

### Resources

- [SAP Help: Released APIs](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis)
- [SAP API Business Hub](https://api.sap.com/)
- [Cloudification Repository (ATC checks)](https://github.com/SAP/abap-atc-cr-cv-s4hc)
- [ABAP Cloud FAQ](https://pages.community.sap.com/topics/abap/abap-cloud-faq)
- Transaction `ATC` de chay ABAP Test Cockpit

## ABAP Formatter & Auto-check

### ABAP Formatter (Eclipse/ADT - tich hop san)

- **Format truoc khi activate** (Ctrl+F1 trong ADT)
- Su dung **Project → Properties → ABAP Development → Formatter** de cau hinh team settings
- Xuat settings (.settings file) cho team dung chung

### Code Inspector / Checkman

- Tao VARIANT rieng cho ABAP Cloud
- Active cac check: Naming Conventions, Unused Variables, Obsolete Statements

### ABAP Cleaner (plugin ADT ben thu ba)

- [GitHub: ABAP Cleaner](https://github.com/HugoFara/abap-cleaner)
- Clean code tu dong: xoa Hungarian, reformat, collapse, optimize
- **Rieng biet** voi ABAP Formatter; ABAP Cleaner dung file config rieng (`.abapCleaner.json`)
- Ho tro ABAP Cloud clean naming (tu dong bo Hungarian prefixes)

## Code Inspector (SCI) & ATC Checks

### Tong quan 2 cong cu

| Tinh nang | Code Inspector (SCI) | ABAP Test Cockpit (ATC) |
|-----------|----------------------|------------------------|
| **Cach goi** | Transaction `SCI` / `SCII` | Transaction `ATC` hoac trong ADT |
| **Muc dich** | Kiem tra tinh hop le, naming, syntax | Kiem tra tuan thu ABAP Cloud / Clean Core |
| **Naming** | Cau hinh duoc trong check variant | Ke thua tu SCI configuration |
| **Cloud check** | Khong ho tro cloud | `ABAP_CLOUD_READINESS` la chinh |
| **Giao dien** | SAP GUI (SE38) | ADT (Eclipse) & SAP BTP |

> **Khuyen nghi:** Dung **ATC trong ADT** cho ABAP Cloud. Tao check variant bao gom ca `ABAP_CLOUD_READINESS` + `Naming Conventions` tu SCI.

### Cau hinh Code Inspector (SCI) cho Naming Conventions

#### Buoc 1: Mo transaction SCI

`/nSCI` → **Check Configuration** → **Create** / **Change Check Variant**

#### Buoc 2: Them Naming Conventions check

Trong check variant, mo: **List of Checks → Programming Conventions → Naming Conventions**

Tick vao cac check sau:

| Check | Mo ta |
|-------|-------|
| `Naming Conventions` | Kiem tra prefix/suffix naming cho development objects |
| `Structure Naming` | Kiem tra naming cua structure types |
| `Parameter Naming` | Kiem tra Hungarian notation (`iv_`, `ev_`, ...) |
| `Program Structure` | Phat hien unused variables, redundant declarations |
| `Obsolete Statements` | Phat hien Add/Subtract, Move-Corresponding, ... |

#### Buoc 3: Cau hinh Naming Rules (Parameters)

Chon check `Naming Conventions` → **Parameters** icon (nut kinh lup). Day la noi ban dinh nghia prefix/pattern cho tung loai object:

**Parameters Reference:**

| Object Type | Tham so | Legacy (vd) | ABAP Cloud | Ghi chu |
|-------------|---------|-------------|------------|---------|
| Variables | `gv_`/`lv_`/`mv_` | `gv_` = global | **Bo trong** | ABAP Cloud ko can Hungarian |
| Types/Structures | `ty_`/`ts_` | `ty_mara` | `ty_mara` | Van nen dung `ty_` prefix |
| Constants | `c_`/`gc_` | `gc_status` | **Bo trong** | Dung ten co nghia, bo gc_ |
| Parameters | `iv_`/`ev_`/`ct_` | `iv_matnr` | **Bo trong** | ABAP Cloud ko can |
| Field Symbols | `<fs_>` | `<fs_name>` | **`<name>`** | Chi dung ten mo ta |

> **ABAP Cloud:** De **trong** cac truong prefix. Neu muon enforce clean naming (ko Hungarian), can disable hoac custom check rieng.

### ATC Check Variant cho ABAP Cloud

#### Buoc 1: Tao ATC check variant trong ADT

**File → New → Other → ABAP Test Cockpit → Check Variant** (hoac dung transaction `ATC`)

#### Buoc 2: Them cac check can thiet

Check variant ABAP Cloud nen gom:

| Check | Loai | Mo ta |
|-------|------|-------|
| `ABAP_CLOUD_READINESS` | ATC (SAP standard) | **Bat buoc**: quet unreleased APIs, syntax ABAP Cloud |
| `SAP_CP_READINESS` | ATC (SAP standard) | Kiem tra kha nang chuyen doi S/4HANA Cloud |
| `Naming Conventions` | SCI (ke thua) | Kiem tra naming patterns (neu muon enforce) |
| `Search for Obsolete Statements` | SCI | Phat hien ADD, SUBTRACT, MOVE-CORRESPONDING, ... |
| `Performance Checks` | SCI | Phat hien SELECT khong toi uu, nested loops |
| `Security Checks` | SCI | Phat hien SQL injection, XSS, authorization missing |

#### Buoc 3: Cau hinh ATC properties

Trong ADT: **Properties** cua check variant → ABAP Test Cockpit:

```
❑ Quet toan bo project
❑ Chi quet su thay doi tu lan ATC truoc
❑ Mac dinh: quet project
```

### Cac ATC check ABAP Cloud quan trong

#### ABAP_CLOUD_READINESS

Day la check quan trong **nhat** cho ABAP Cloud. No kiem tra:

| Kiem tra | Vi du loi |
|----------|----------|
| Chi su dung released APIs | `"Call to non-released API IF_OLD_STUFF"` |
| Khong goi function module unreleased | `"FM OLD_FUNCTION is not released"` |
| Khong SELECT vao bang SAP truc tiep | `"SELECT from MARA is not allowed"` |
| Khong dung ABAP_SLEEP / WAIT | `"ABAP_SLEEP is not allowed"` |
| Cac tu khoa ABAP Cloud bi cam | `"CALL TRANSACTION is obsolete"` |
| Khong dung OVERFLOW, TYPE-POOLS, ... | `"Obsolete language element"` |
| Khong REFERENCES TO cross-class | `"Cross-class reference not allowed"` |

#### Cac ATC checks khac

| Check | Mo ta |
|-------|-------|
| `ABAP_CLOUD_READINESS_EXTENDED` | Check chat hon cho private cloud / on-prem with cloud extension |
| `ABAP_CLOUD_READINESS_RAP` | Kiem tra RAP BO compliance, behavior definition |
| `ABAP_CLOUD_READINESS_UI5` | Kiem tra UI5/Fiori integration trong ABAP Cloud |
| `EXCLUDE_FROM_CLOUD_CHECK` | Check tu dong loai tru (cho wrapper classes) |

### ATC Priority Levels

| Priority | Y nghia | Hanh dong |
|----------|---------|-----------|
| 🔴 **Error** | Vi pham nghiem trong (unreleased API, obsolete syntax) | **Khong duoc activate** code |
| 🟡 **Warning** | Can xem xet (performance, naming, security) | Nen sua truoc khi commit |
| 🔵 **Info** | Gay chu y (code mai quy uoc team) | Co the de lai neu co ly do chinh dang |

### Cach chay ATC tu ADT

1. **Tren 1 object:** Right-click class/program → **ABAP Test Cockpit** → **Run**
2. **Tren project:** Right-click ABAP project → **ABAP Test Cockpit** → **Run**
3. **Tren transport (S/4HANA):** Trong ADT transport organizer → **Right-click** → **ATC Check**.
   > **Luu y:** Tren pure ABAP Cloud (BTP, Cloud Foundry), khong co transport organizer. Dung ADT project check (cach 2).
4. **Automation:** Kich hoat ATC tu dong khi activate:
   - **Window → Preferences → ABAP Development → ABAP Test Cockpit**
   - Tick: *"Run ATC checks after activation"*

### Cac Code Inspector check khac nen dung

Ngoai naming, nen active them trong check variant:

| Nhom check | Check | Mo ta |
|------------|-------|-------|
| **Security** | `Authorization Check` | Phat hien thieu authority check |
| **Security** | `SQL Injection` | Phat hien SQL injection nguy co |
| **Performance** | `SELECT Without Key` | Phat hien SELECT khong co dieu kien |
| **Performance** | `Nested Loop` | Phat hien loop trong loop |
| **Performance** | `For All Entries` | Kiem tra cach dung FOR ALL ENTRIES |
| **Programming** | `Unused Variables` | Phat hien bien khong dung |
| **Programming** | `Unused Methods` | Phat hien method khong goi |
| **Programming** | `Enhancement Implementation` | Kiem tra BAdI / Enhancement implementation |
| **Syntax** | `Obsolete Statements` | Phat hien ADD, SUBTRACT, ... |
| **Syntax** | `Short Dumps` | Phat hien cac truong hop co the gay dump |
