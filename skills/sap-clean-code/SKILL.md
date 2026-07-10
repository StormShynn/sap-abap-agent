---
name: sap-clean-code
description: Huong dan clean code & name conversion cho SAP ABAP Public Cloud (ABAP Cloud). Dung khi user hoi ve naming conventions, clean ABAP code style, name conversion tu legacy ABAP sang ABAP Cloud, quy tac dat ten cho development objects.
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

## 3. Name Conversion Guide: Legacy → ABAP Cloud

### Class Names

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

### Method Names

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

### Variable Names

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

### Parameter Names

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

## 4. ABAP Cloud Specific Rules

### Development Object Naming

| Object Type | Convention | Vi du |
|-------------|-----------|-------|
| Class (co namespace) | `/prefix/descriptive_name` | `/s4clean/order_validator` |
| Class (ko namespace) | `ZCL_<Name>` hoac `Z_<Name>` | `ZCL_ORDER_VALIDATOR` |
| Interface (co namespace) | `/prefix/if_descriptive_name` | `/s4clean/if_order_validator` |
| Interface (ko namespace) | `ZIF_<Name>` | `ZIF_ORDER_VALIDATOR` |
| CDS View | `Z_C_<Entity>` / `Z_I_<Entity>` | `Z_C_Product`, `Z_I_SalesOrder` |
| CDS Table Function | `Z_TF_<Name>` | `Z_TF_ProductData` |
| Data Element | `Z<Entity>ID` hoac `Z<Entity>Type` | `ZProductID`, `ZOrderType` |
| Table Type | `Z<Entity>Table` | `ZProductTable` |
| Message Class | `Z<Name>` | `ZORDER_MESSAGES` |

### Naming cho CDS Views (RAP)

CDS views trong ABAP Cloud tuan theo **Virtual Data Model (VDM)** cua SAP, chia thanh nhiều layer (lop). Moi layer co prefix rieng de phan biet vai tro.

> **Luu y 1:** Tat ca prefix phai bat dau bang `Z` (hoac namespace registered).
>
> **Luu y 2:** CDS views can annotation `@AbapCatalog.sqlViewName` de tao ten view ngan (toi da 30 ky tu) cho database compatibility.
>
> **Luu y 3:** Ten CDS view va `@AbapCatalog.sqlViewName` deu co gioi han **30 ky tu**. Vi du `ZPRD_APPROVED` (13 ky tu) OK, nhung `ZPRODUCT_STOCK_WITH_LONG_NAME` (30 ky tu) la toi da.
>
> **Luu y 4:** Gioi han do dai ten CDS view la **30 ky tu**, tinh ca prefix `Z_C_`. Khi dat ten, luon tinh ca prefix vao gioi han nay.

#### 4.1 VDM Layers — Cac lop CDS View

| Layer | Prefix | Vai tro | Vi du |
|-------|--------|---------|-------|
| **Interface View** | `Z_I_` | Lop co ban nhat: doc truc tiep tu database table hoac cac interface view khac. La "single source of truth". | `Z_I_Product`, `Z_I_SalesOrder` |
| **Consumption View** | `Z_C_` | Lop tieu dung: build tren interface views, toi uu cho OData / Fiori / analytics. | `Z_C_Product`, `Z_C_SalesOrder` |
| **Extension View** | `Z_X_` | Lop mo rong: them field / logic vao standard SAP views (khi can extend). | `Z_X_Product`, `Z_X_SalesOrder` |
| **Projection View** | `Z_P_` | Lop chieu: gioi han field / association cho 1 BO context cu the. Thuong dung trong RAP. | `Z_P_Product`, `Z_P_SalesOrder` |
| **Abstract Entity** | `Z_A_` | Lop truu tuong: khong map vao database nao. Dung de dinh nghia kieu du lieu cho RAP actions / functions. | `Z_A_SearchCriteria`, `Z_A_ActionResult` |

**Moi quan he giua cac layer:**

```
Database Tables (MARA, VBAK, ...)
    ↓
Z_I_* (Interface Views)  ← basic, reusable
    ↓
Z_C_* (Consumption Views)  ← for UI / OData
    ↓
Z_P_* (Projection Views)  ← cho BO context
```

#### 4.2 Dat ten cho CDS fields (elements)

Khac voi ABAP (snake_case), CDS fields dung **CamelCase** (vi CDS la case-sensitive).

```ABAP
" ✅ Dep: CamelCase + mo ta
define view Z_I_Product as select from product {
  key product_id            as ProductId,
      product_type          as ProductType,
      creation_date         as CreationDate,
      stock_quantity        as StockQuantity,
      base_unit_of_measure  as BaseUnitOfMeasure,
      supplier_id           as SupplierId
}

" ❌ Khong dep: snake_case trong CDS hoac viet tat
@AbapCatalog.sqlViewName: 'ZPRD_BAD'
define view Z_I_Product_Bad as select from product {
  key product_id            as product_id,         " snake_case trong CDS
      pr_type               as pr_type,            " viet tat
      cre_date              as cre_date,           " viet tat
      stock_quantity        as stock_qty            " hon hop
}
```

**Pattern dat ten field:** `[Object][Property][Representation]`

```
Stock       + Availability    + Date    = StockAvailabilityDate
Product     + Type             + ID      = ProductTypeId
SalesOrder  + Creation         + Date    = SalesOrderCreationDate
Business    + Partner          + Name    = BusinessPartnerName
Customer    + Classification   + Code    = CustomerClassificationCode
```

**Field dat ten trong CDS view (alias):**

| Khi field tu bang SAP | Dung alias ro rang |
|------------------------|-------------------|
| `mara~matnr` | `as ProductId` |
| `mara~mtart` | `as ProductType` |
| `mara~meins` | `as BaseUnitOfMeasure` |
| `vbak~vbeln` | `as SalesOrderId` |
| `vbak~audat` | `as CreationDate` |
| `vbak~vkorg` | `as SalesOrganization` |

#### 4.3 Association naming

Associations trong CDS **bat buoc** bat dau bang dau gach duoi (`_`) de phan biet voi fields.

```ABAP
" ✅ Dep: association co tien to _
define view Z_I_SalesOrder as select from vbak
  association [0..1] to I_BusinessPartner as _BusinessPartner
    on vbak~kunnr = _BusinessPartner.BusinessPartner
  association [0..*] to I_Product as _Product
    on $projection.ProductId = _Product.ProductId
{
  key vbak~vbeln   as SalesOrderId,
      vbak~audat   as CreationDate,
      vbak~kunnr   as CustomerId,
      /* Associations */
      _BusinessPartner,
      _Product
}

" ❌ Khong dep: thieu tien to _
define view Z_I_SalesOrder_Bad as select from vbak
  association [0..1] to I_BusinessPartner as BusinessPartner  " thieu _
{
  ...
}
```

**Quy tac dat ten association:**

| Component | Convention | Vi du |
|-----------|-----------|-------|
| Ten association | `_<EntityName>` | `_Product`, `_BusinessPartner` |
| Nhieu association cung loai | `_<PhanBiet>` | `_ShipToParty`, `_BillToParty` |
| Association voi dieu kien phuc tap | `_<MucDich>` | `_PendingOrders`, `_ApprovedItems` |
| Composition | `_<ChildEntity>` | `_Item`, `_Attachment` |

**Vi du association phuc tap:**

```ABAP
define view Z_I_SalesOrder
  association [0..1] to I_BusinessPartner as _SoldToParty
    on vbak~kunnr = _SoldToParty.BusinessPartner
  association [0..*] to Z_I_SalesOrderItem as _Item
    on vbak~vbeln = _Item.SalesOrderId
  association [1..1] to Z_C_Customer as _Customer
    on vbak~kunnr = _Customer.CustomerId
{
  key vbak~vbeln     as SalesOrderId,
      vbak~audat     as CreationDate,
      vbak~kunnr     as CustomerId,
      _SoldToParty.BusinessPartnerName as SoldToPartyName,
      _Customer.CustomerCategory       as CustomerCategory,
      /* Children */
      _Item
}
```

#### 4.4 Annotation naming

Annotations trong CDS dung **dot notation** (vi du: `@UI.lineItem`). Cac annotation phai dung chinh xac ten SAP dinh nghia.

**Annotation theo nhom:**

```ABAP
@AbapCatalog.sqlViewName: 'ZPRD_APPROVED'          " SQL view name (bat buoc)
@AbapCatalog.compiler.compareFilter: true

@AccessControl.authorizationCheck: #CHECK          " NOT_REQUIRED / CHECK / PRIVILEGED_ONLY

@EndUserText.label: 'Approved Products'            " Label hien thi trong ADT

@Metadata.ignorePropagatedAnnotations: true

@UI: {                                            " Fiori UI annotations
  headerInfo: {
    typeName: 'Product',
    typeNamePlural: 'Products'
  },
  presentationVariant: [{ sortOrder: [{ by: 'ProductId', direction: #ASC }] }]
}

define view Z_C_ApprovedProduct
  as select from Z_I_Product
{
  @UI.lineItem: [{ position: 10 }]
  @UI.selectionField: [{ position: 10 }]
  key ProductId,

  @UI.lineItem: [{ position: 20 }]
  @UI.headerInfo: { typeName: 'Product Type' }
  ProductType,

  @UI.lineItem: [{ position: 30 }]
  @EndUserText.label: 'Stock'
  StockQuantity
}
```

**Cac nhom annotation chinh:**

| Annotation group | Muc dich | Vi du |
|-----------------|----------|-------|
| `@AbapCatalog` | Cau hinh ABAP Catalog (sqlViewName, compiler) | `@AbapCatalog.sqlViewName: 'ZVIEW'` |
| `@AccessControl` | Phan quyen (authorization check) | `@AccessControl.authorizationCheck: #CHECK` |
| `@EndUserText` | Label, description cho nguoi dung | `@EndUserText.label: 'My View'` |
| `@UI` | Fiori Elements UI annotations | `@UI.lineItem`, `@UI.selectionField` |
| `@OData` | OData publishing config | `@OData.publish: true` |
| `@ObjectModel` | Object model metadata | `@ObjectModel.readOnly`, `@ObjectModel.associationType` |
| `@Analytics` | Analytics / query | `@Analytics.query: true` |
| `@Semantics` | Data semantics (unit, currency) | `@Semantics.amount.currencyCode: 'Currency'` |
| `@MappingRole` | Mapping role for SAP Data Warehouse | — |
| `@Consumption` | Consumption layer annotations | `@Consumption.filter: { selectionType: #RANGE }` |
| `@Metadata` | Metadata extensions control | `@Metadata.ignorePropagatedAnnotations` |
| `@Search` | Full-text search config | `@Search.fuzzinessThreshold: 0.8` |

**Annotation tren field:**

```ABAP
define view Z_C_Product as select from Z_I_Product {
  @UI.hidden: true                              " An field trong UI
  key ProductId,

  @EndUserText.label: 'Product Name'
  @UI.lineItem: [{ position: 10, importance: #HIGH }]
  @UI.selectionField: [{ position: 10 }]
  @Search.defaultSearchElement: true
  ProductName,

  @Semantics.amount.currencyCode: 'Currency'    " Dinh dang tien te
  @UI.lineItem: [{ position: 50 }]
  Price,

  @Semantics.currencyCode: true                 " Don vi tien te
  Currency
}
```

#### 4.5 CDS Parameter naming

Tham so CDS dat ten co `p_` hoac `iv_` de phan biet voi fields:

```ABAP
" ✅ Dep: prefix p_ cho parameters
define view Z_I_ProductByType
  with parameters
    p_product_type : producttype,
    p_max_results  : abap.int2
  as select from product
  where product_type = $parameters.p_product_type
    and $parameters.p_max_results > 0
{
  key product_id   as ProductId,
      product_type as ProductType,
      description  as Description
}

" Goi: select * from Z_I_ProductByType(
"         p_product_type = 'FERT',
"         p_max_results  = 100 )
```

#### 4.6 CDS Table Function naming

Table functions (AMDP) dung prefix `Z_TF_`:

```ABAP
" ✅ Dep
@AbapCatalog.sqlViewName: 'ZPRD_STOCK_TF'
define table function Z_TF_ProductStock
  with parameters
    @Environment.systemField: #CLIENT
    p_client_id  : mandt,
    p_product_id : matnr
  returns
  (
    key ProductId : matnr,
        StockQty  : menge_d,
        StockDate : datum
  )
  implemented by method
    zcl_product_stock=>get_stock_data;
```

#### 4.7 CDS Abstract Entity naming

Abstract entities dung prefix `Z_A_` (hoac `Z_AE_`):

```ABAP
" ✅ Dep: Z_A_ cho Abstract Entity
@EndUserText.label: 'Product Search Criteria'
define abstract entity Z_A_ProductSearchCriteria
{
  product_id     : matnr;
  product_type   : mtart;
  max_results    : abap.int4;
}

" Dung trong RAP action:
" action validateProduct(
"   parameters Z_A_ProductSearchCriteria
" ) result Z_A_ValidationResult;
```

#### 4.8 CDS Projection View naming

Projection views trong RAP thuong dung suffix `TP` (Transactional Processing):

```ABAP
" ✅ Dep: suffix TP cho transaction processing
define view Z_C_ProductTP
  as projection on Z_I_Product
{
  key ProductId,
      ProductType,
      StockQuantity,
      /* Buoc association */
      _ProductType: redirected to composition child ProductType
}

" Cac suffix pho bien:
" TP  = Transactional Processing (RAP BO projection)
" QP  = Query Processing (read-only)
" DP  = Draft Processing
" API = API exposure
```

#### 4.9 Vi du CDS view hoan chinh (clean code)

**Interface View:**

```ABAP
@AbapCatalog.sqlViewName: 'ZPRD_INTERFACE'
@AbapCatalog.compiler.compareFilter: true
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Product - Interface View'

define view Z_I_Product
  as select from product
  association [0..1] to I_ProductType as _ProductType
    on product.product_type = _ProductType.ProductType
{
  key product_id               as ProductId,
      product_type              as ProductType,
      product_description       as Description,
      price_amount              as PriceAmount,
      currency_code             as CurrencyCode,
      creation_date             as CreationDate,
      created_by_user           as CreatedBy,
      stock_quantity            as StockQuantity,
      last_change_date          as LastChangedOn,
      _ProductType
}
```

**Consumption View:**

```ABAP
@AbapCatalog.sqlViewName: 'ZPRD_CONSUMPTION'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Product - Consumption View'
@UI: {
  headerInfo: {
    typeName: 'Product',
    typeNamePlural: 'Products'
  }
}

define view Z_C_Product
  as select from Z_I_Product
  association [0..1] to I_ProductType as _ProductType
    on $projection.ProductType = _ProductType.ProductType
{
  @UI.lineItem: [{ position: 10 }]
  @UI.selectionField: [{ position: 10 }]
  key ProductId,

  @UI.lineItem: [{ position: 20 }]
  ProductType,

  @EndUserText.label: 'Product Description'
  @UI.lineItem: [{ position: 30, importance: #HIGH }]
  Description,

  @UI.lineItem: [{ position: 40 }]
  @ObjectModel.readOnly: true
  CreationDate,

  @Semantics.amount.currencyCode: 'CurrencyCode'
  @UI.lineItem: [{ position: 50 }]
  PriceAmount,

  @Semantics.currencyCode: true
  CurrencyCode,

  _ProductType
}
```

#### 4.10 CDS naming cheat sheet

| Doi tuong | Convention | Vi du |
|-----------|-----------|-------|
| Interface View | `Z_I_<Entity>` | `Z_I_Product` |
| Consumption View | `Z_C_<Entity>` | `Z_C_Product` |
| Extension View | `Z_X_<Entity>` | `Z_X_Product` |
| Projection View | `Z_P_<Entity>` hoac `Z_C_<Entity>TP` | `Z_C_ProductTP` |
| Abstract Entity | `Z_A_<Entity>` | `Z_A_SearchCriteria` |
| Table Function | `Z_TF_<Entity>` | `Z_TF_ProductStock` |
| Association | `_<Entity>` | `_Product`, `_BusinessPartner` |
| Parameter | `p_<name>` | `p_product_type` |
| Field (alias) | `CamelCase` | `ProductId`, `StockQuantity` |
| Annotation | `@<Group>.<key>` | `@UI.lineItem`, `@Semantics.amount` |

### Naming cho RAP Business Objects

> Tat ca prefix deu bat dau bang `Z` (tuan thu ABAP Cloud rule).

```
Behavior Definition:      Z_BD_I_<Entity>       (vd: Z_BD_I_Product)
Behavior Implementation:  Z_BP_I_<Entity>       (vd: Z_BP_I_Product)
Service Definition:       Z_SD_<Entity>         (vd: Z_SD_Product)
Service Binding:          Z_SB_<Entity>_ODATA   (vd: Z_SB_Product_ODATA)
Metadata Extension:       Z_MDE_<Entity>        (vd: Z_MDE_Product)
```

## 5. Dat ten cho Field Symbols

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

## 6. Constants va Enums

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

## 7. Naming cho Exception Classes

```ABAP
" ✅ ABAP Cloud
CLASS cx_s4clean_not_found DEFINITION INHERITING FROM cx_static_check.
CLASS cx_s4clean_validation_error DEFINITION INHERITING FROM cx_static_check.
CLASS cx_s4clean_unauthorized DEFINITION INHERITING FROM cx_no_check.

" ❌ Legacy
CLASS zcx_material_not_found DEFINITION.
CLASS zcx_bapi_error DEFINITION.
```

## 8. Naming Pattern cho Dependency Injection / Testing

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

## 9. Clean Code Rules Quan Trong

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

## 10. ABAP Cloud Released APIs Checklist

ABAP Cloud yeu cau **Clean Core**: chi duoc su dung **released APIs** cua SAP. Day la quy dinh bat buoc, khong phai tuy chon.

### 10.1 Released API la gi?

Released API la nhung doi tuong phat trien (class, interface, CDS view, function module, BAPI, ...) ma SAP cam ket **on dinh** — khong thay doi signature hoac behavior trong cac ban upgrade.

- **C1 contract**: API duoc release on dinh, co the dung trong ABAP Cloud.
- **C0 contract**: Chi dung noi bo SAP, **KHONG duoc** dung tu code customer.
- **Unreleased**: Khong co stability contract, co the bi thay doi bat ky luc nao.

> **Luat bat buoc:** Trong ABAP Cloud language version, code **KHONG THE** goi truc tiep unreleased APIs. Trinh bien dich se bao loi.

### 10.2 Kiem tra API release status trong ADT

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

### 10.3 Nhung released APIs quan trong cho ABAP Cloud

| Loai | Vi du | Ghi chu |
|------|-------|---------|
| **CDS View** | `I_Product`, `C_SalesOrder`, `I_BusinessPartner` | CDS views la released APIs co ban nhat |
| **RAP BO** | `R_Product`, `R_SalesOrder` | RAP business objects |
| **Class** | `CL_ABAP_UNIT_ASSERT`, `CL_HTTP_CLIENT` | Kiem tra API state tung class |
| **Interface** | `IF_ABAP_UNIT_CONSTANTS` | Interface co the released hoac khong |
| **BAPI** | `BAPI_MATERIAL_GETLIST` | BAPI can kiem tra API release status |
| **Function** | `DDIF_FIELDINFO_GET` | Phan lon function modules cu la unreleased |
| **Data Element** | `MATNR`, `SPRAS` | Data elements thuong la released (C1) |

### 10.4 Checklist: Kiem tra code co dung released APIs khong

Truoc khi activate / commit, kiem tra:

- [ ] **ATC check ABAP_CLOUD_READINESS** — quet toan bo code tim unreleased APIs
- [ ] **Khong co goi** `CALL FUNCTION` vao function module cu (unreleased)
- [ ] **Khong co SELECT** truc tiep vao bang SAP (`MARA`, `VBAK`, ...) — phai qua CDS views
- [ ] **Khong co** `MODIFY`, `DELETE`, `INSERT` truc tiep vao bang SAP
- [ ] **Khong goi** class method unreleased (kien tra API State)
- [ ] **Khong su dung** `ABAP_SLEEP` hoac `WAIT UP TO` — dung `IF_ABAP_CLOUD_UTILITY` hoac `CL_ABAP_SLEEP` (released)
- [ ] **Cham deprecation notices** — neu API co trang thai Deprecated, can chuyen sang API moi
- [ ] **Custom wrapper** — neu that su can dung unreleased API, tao wrapper class va tu release (neu co quyen)

### 10.5 Cach xu ly khi can dung unreleased API

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

### 10.6 Resources

- [SAP Help: Released APIs](https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/released-apis)
- [SAP API Business Hub](https://api.sap.com/)
- [Cloudification Repository (ATC checks)](https://github.com/SAP/abap-atc-cr-cv-s4hc)
- [ABAP Cloud FAQ](https://pages.community.sap.com/topics/abap/abap-cloud-faq)
- Transaction `ATC` de chay ABAP Test Cockpit

## 11. ABAP Formatter & Auto-check

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

## 12. Code Inspector (SCI) & ATC Checks

### 12.1 Tong quan 2 cong cu

| Tinh nang | Code Inspector (SCI) | ABAP Test Cockpit (ATC) |
|-----------|----------------------|------------------------|
| **Cach goi** | Transaction `SCI` / `SCII` | Transaction `ATC` hoac trong ADT |
| **Muc dich** | Kiem tra tinh hop le, naming, syntax | Kiem tra tuan thu ABAP Cloud / Clean Core |
| **Naming** | Cau hinh duoc trong check variant | Ke thua tu SCI configuration |
| **Cloud check** | Khong ho tro cloud | `ABAP_CLOUD_READINESS` la chinh |
| **Giao dien** | SAP GUI (SE38) | ADT (Eclipse) & SAP BTP |

> **Khuyen nghi:** Dung **ATC trong ADT** cho ABAP Cloud. Tao check variant bao gom ca `ABAP_CLOUD_READINESS` + `Naming Conventions` tu SCI.

### 12.2 Cau hinh Code Inspector (SCI) cho Naming Conventions

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

### 12.3 ATC Check Variant cho ABAP Cloud

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

### 12.4 Cac ATC check ABAP Cloud quan trong

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

### 12.5 ATC Priority Levels

| Priority | Y nghia | Hanh dong |
|----------|---------|-----------|
| 🔴 **Error** | Vi pham nghiem trong (unreleased API, obsolete syntax) | **Khong duoc activate** code |
| 🟡 **Warning** | Can xem xet (performance, naming, security) | Nen sua truoc khi commit |
| 🔵 **Info** | Gay chu y (code mai quy uoc team) | Co the de lai neu co ly do chinh dang |

### 12.6 Cach chay ATC tu ADT

1. **Tren 1 object:** Right-click class/program → **ABAP Test Cockpit** → **Run**
2. **Tren project:** Right-click ABAP project → **ABAP Test Cockpit** → **Run**
3. **Tren transport (S/4HANA):** Trong ADT transport organizer → **Right-click** → **ATC Check**.
   > **Luu y:** Tren pure ABAP Cloud (BTP, Cloud Foundry), khong co transport organizer. Dung ADT project check (cach 2).
4. **Automation:** Kich hoat ATC tu dong khi activate:
   - **Window → Preferences → ABAP Development → ABAP Test Cockpit**
   - Tick: *"Run ATC checks after activation"*

### 12.7 Cac Code Inspector check khac nen dung

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

### 12.8 ABAP Cleaner (plugin ADT ben thu ba)

- [GitHub: ABAP Cleaner](https://github.com/HugoFara/abap-cleaner)
- Clean code tu dong: xoa Hungarian, reformat, collapse, optimize
- **Rieng biet** voi ABAP Formatter; ABAP Cleaner dung file config rieng (`.abapCleaner.json`)
- Ho tro ABAP Cloud clean naming (tu dong bo Hungarian prefixes)

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
