# ABAP Cloud Specific Rules

Reference chi tiet cho skill `sap-clean-code` — quy tac dat ten rieng cho ABAP Cloud: development
object, CDS view (VDM 5-layer), field/association/annotation/parameter/table function/abstract
entity/projection naming, va RAP Business Object naming.

## Muc luc

- Development Object Naming
- Naming cho CDS Views (RAP) — VDM Layers, bien the ticket-based, field/association/annotation/parameter/table function/abstract entity/projection naming, vi du hoan chinh, cheat sheet
- Naming cho RAP Business Objects

## Development Object Naming

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

## Naming cho CDS Views (RAP)

CDS views trong ABAP Cloud tuan theo **Virtual Data Model (VDM)** cua SAP, chia thanh nhieu layer (lop). Moi layer co prefix rieng de phan biet vai tro.

> **Luu y 1:** Tat ca prefix phai bat dau bang `Z` (hoac namespace registered).
>
> **Luu y 2:** CDS views can annotation `@AbapCatalog.sqlViewName` de tao ten view ngan (toi da 30 ky tu) cho database compatibility.
>
> **Luu y 3:** Ten CDS view va `@AbapCatalog.sqlViewName` deu co gioi han **30 ky tu**. Vi du `ZPRD_APPROVED` (13 ky tu) OK, nhung `ZPRODUCT_STOCK_WITH_LONG_NAME` (30 ky tu) la toi da.
>
> **Luu y 4:** Gioi han do dai ten CDS view la **30 ky tu**, tinh ca prefix `Z_C_`. Khi dat ten, luon tinh ca prefix vao gioi han nay.

### VDM Layers — Cac lop CDS View

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

> ⚠️ **Bien the convention khac (khong co underscore sau Z)**: 1 so du an dung `ZI_*` / `ZR_*` /
> `ZC_*` (khong dau `_` giua `Z` va chu cai layer) thay vi `Z_I_*`/`Z_C_*`. Ca 2 kieu deu la quy
> uoc du an (project convention), KHONG phai chuan cung nhac cua SAP — **luon xac nhan voi tech
> lead/du an dang lam kieu nao truoc khi dat ten**, dung tron 2 kieu trong cung 1 package. Bang
> duoi la bien the pho bien thu 2 (thuong di kem cach dat `<OBJECT>` = ma ticket/bao cao, xem muc
> "Bien the: `<OBJECT>` = ma ticket/bao cao" ben duoi).

### Bien the: `<OBJECT>` = ma ticket/bao cao (khong phai ten mo ta)

Mot so du an quy uoc phan `<OBJECT>` sau prefix la **ma bao cao/ticket** (vd `ZSD01`), KHONG dung
ten nghiep vu mo ta:

```
✅ ZI_ZSD01, ZR_ZSD01, ZC_ZSD01, ZUI_ZSD01_O4 (service def + binding cung ten), ZBP_R_ZSD01
❌ ZI_PACKINGLIST, ZC_PACKINGLIST (ten mo ta — sai theo quy uoc nay)
```

Neu tach header/item: them hau to `_H` / `_IT` (vd `ZC_ZSD01_IT`, `ZR_ZSD01_H`). Object dung
chung/master cua nhieu ticket giu ten rieng theo domain (vd `ZI_COMPANY_CODE`). Quy uoc nay chi
ap dung neu du an chon theo huong "1 object = 1 ticket" — xac nhan voi tech lead truoc khi ap dung.

**Prefix bo sung cho bien the nay** (dung kem RAP service/behavior):

| Prefix | Loai object | Vi du |
|--------|-------------|-------|
| `ZBP_*` | Behavior implementation (behavior pool class) | `ZBP_R_ZSD01` — impl cho behavior definition |
| `ZUI_*` | Service def + binding cho **APP/UI** | `ZUI_ZSD01_O4` (OData V4 UI), `ZUI_ZSD01_O2` (V2) |
| `ZAPI_*` | Service def + binding cho **API machine-to-machine** | `ZAPI_ZSD01_O4` — API M2M rieng voi UI |

Service binding **trung ten** service definition (SRVD va SRVB la 2 object type khac nhau nen duoc
phep cung ten — khong can tach hau to `_SD` rieng).

**Gioi han do dai ten theo tung loai object** (nguon: ABAP Keyword Documentation – Names of
Repository Objects, ban Cloud):

| Loai object | Max ky tu | Ghi chu |
|-------------|-----------|---------|
| **Database table** (transparent, `ZTB*`) | **16** | Sinh physical DB object — chat nhat. Bay hay gap: ghep `ZTB_<MODULE>_<TICKET>_<SUB>_D` (draft) rat de vuot 16 — uu tien ma ticket + hau to ngan, bo tien to phan he neu can. |
| CDS view/class/service/structure/data element/domain | 30 | Nhu muc "Gioi han ky tu" o tren |
| **Message class** | **20** | Khac voi 30 — de y khi dat ten message class rieng |

**Mapping clause** (bat buoc khi ten CDS khac ten cot DB, vd dung 1 table generic cho nhieu report):

```abap
managed implementation in class zbp_<zr> unique;
strict ( 2 );

define behavior for ZR_<OBJECT> {
  action CreatePDF result [1..*] $self;
  mapping for ztb_shared_table          // BAT BUOC neu ten CDS != ten cot DB
    {
      Key        = object_id;
      Attachment = attachment;
    }
}
```

### Dat ten cho CDS fields (elements)

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

### Association naming

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

### Annotation naming

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

### CDS Parameter naming

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

### CDS Table Function naming

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

### CDS Abstract Entity naming

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

### CDS Projection View naming

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

### Vi du CDS view hoan chinh (clean code)

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

### CDS naming cheat sheet

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

## Naming cho RAP Business Objects

> Tat ca prefix deu bat dau bang `Z` (tuan thu ABAP Cloud rule).

```
Behavior Definition:      Z_BD_I_<Entity>       (vd: Z_BD_I_Product)
Behavior Implementation:  Z_BP_I_<Entity>       (vd: Z_BP_I_Product)
Service Definition:       Z_SD_<Entity>         (vd: Z_SD_Product)
Service Binding:          Z_SB_<Entity>_ODATA   (vd: Z_SB_Product_ODATA)
Metadata Extension:       Z_MDE_<Entity>        (vd: Z_MDE_Product)
```
