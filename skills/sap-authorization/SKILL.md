---
name: sap-authorization
description: Huong dan Authorization & IAM trong SAP S/4HANA Cloud Public Edition va BTP ABAP Environment — DCL (Data Control Language), CDS access control, RAP instance-based authorization, PFCG role, IAM app.
when_to_use: |
  "phan quyen cho RAP BO", "DCL CDS view", "IAM app trong cloud",
  "instance-based authorization trong RAP", "Business Role vs PFCG role cloud",
  "restrict data access bang authorization".
argument-hint: "[cau hoi ve authorization / IAM / DCL / role]"
effort: medium
model: sonnet
---

# Authorization & IAM — ABAP Cloud

## 1. Kien truc Authorization tren ABAP Cloud

Tren S/4HANA Cloud, authorization co 3 tang:

```
Business Role (app layer)
  └─ IAM App (technical role definition)
       └─ Authorization Object (ABAP layer)
            └─ DCL (CDS access control)
            └─ RAP instance-based authorization
```

**Tang tren cung** (Business User -> Business Role) do **Basis admin** cau hinh qua Fiori.
**Tang duoi** (DCL, RAP) do **developer** implement.

## 2. DCL — Data Control Language

DCL (Data Control Language) gioi han quyen truy cap **dulieu** trong CDS view:

```cds
@EndUserText.label: 'Access control for SalesOrder'
@MappingRole: true
define role Z_I_SalesOrder {
  grant select on Z_I_SalesOrder
    where ( org ) = aspect pfcg_auth( 'Z_SALES_ORG', 'ORG', 'ACTVT='03' );
}
```

| Thanh phan | Y nghia |
|------------|---------|
| `grant select` | Quyen doc du lieu |
| `aspect pfcg_auth()` | Dinh danh authorization object + field |
| `where ( org )` | Dieu kien filter tren CODV view field |
| `'ACTVT=03'` | Activity (03 = display, 02 = change) |

### DCL Patterns

```cds
" 1. Gioi han theo organizational unit
define role Z_I_PurchaseOrder {
  grant select on Z_I_PurchaseOrder
    where ( purchasing_org ) = aspect pfcg_auth( 'Z_PURCH_ORG', 'PURCH_ORG', 'ACTVT='03' );
}

" 2. Gioi han theo company code
define role Z_I_JournalEntry {
  grant select on Z_I_JournalEntry
    where ( company_code ) = aspect pfcg_auth( 'Z_COMP_CODE', 'BUKRS', 'ACTVT='03' );
}
```

## 3. RAP Instance-Based Authorization

RAP BO co **instance-based authorization** — moi hang co the co quyen khac nhau:

```abap
" Behavior definition
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique;

  determine action ValidateAddress on modify { validate; }
  determination setInitialStatus on modify { create; }

  " Instance authorization
  instance authorization;
}

" Behavior implementation
CLASS zbp_salesorder DEFINITION PUBLIC ABSTRACT FINAL
  FOR BEHAVIOR OF zi_salesorder.

  " Kiem tra quyen
  METHOD get_instance_authorizations FOR INSTANCE AUTHORIZATION
    IMPORTING keys REQUEST requested_authorizations FOR SalesOrder
    RESULT result.

    " Doc authorization object
    AUTHORITY-CHECK OBJECT 'Z_SALES_ORG'
      ID 'ACTVT' FIELD '03'  " Display
      ID 'ORG' FIELD ls_salesorder-sales_org.

    IF sy-subrc <> 0.
      INSERT VALUE #( %key = keys[ 1 ]-%key
                      %action-Edit = if_abap_behv=>fc-o-disabled )
        INTO TABLE result.
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

**Instance authorization cho phep**:
- 1 user chi thay duoc sales order cua org minh
- 1 user chi sua duoc purchase order cua phong minh
- 1 user co quyen duyet nhung khong sua

## 4. IAM App (Identity & Access Management)

IAM App dinh nghia **technical role collection**:

```
IAM App: ZIAM_SALES_PROCESSOR
  ├─ Authorization Object: Z_SALES_ORG (ORG, ACTVT)
  ├─ Authorization Object: Z_TCode_Access (S_TCODE)
  └─ Service Binding: Z_SALES_ORDER_SB (OData V4)
```

Cau hinh trong Fiori: **Maintain IAM Apps** -> **Custom IAM App** -> gan Authorization Object.

## 5. Business Role vs PFCG Role

| Tren Cloud (Business Role) | Tren On-Prem (PFCG) |
|---------------------------|---------------------|
| Cau hinh qua Fiori app | Cau hinh qua PFCG |
| IAM App thay authorization object | Transaction code + auth object |
| Business Catalog thay menu | Menu tree |
| Business Role gom Catalog + IAM App | PFCG role gom menu + auth + org |
| User gan Business Role | User gan PFCG role |

Tren Public Cloud, chi Business Role duoc dung. PFCG/KHOL khong ton tai.

## 6. Authorization Object — Tao moi

Tren BTP Steampunk, co the tu tao authorization object:

```abap
" Khi can tao authorization object moi cho custom app
" Dung trong BTP ABAP Environment (Steampunk)
" Tren S/4HANA Cloud, chi dung object SAP release san hoac custom object da cau hinh

AUTHORITY-CHECK OBJECT 'Z_CUSTOM_AUTH'
  ID 'ACTVT' FIELD '01'  " Create
  ID 'FIELD1' FIELD lv_value1
  ID 'FIELD2' FIELD lv_value2.
```

## 7. DCL Debugging

Khi user thay du lieu sai hoac thieu, debug DCL:

1. Kiem tra **Business Role** cua user co IAM App can thiet khong
2. Kiem tra **IAM App** co authorization object dung khong
3. Kiem tra **DCL role** co grant dung field + auth object khong
4. Kiem tra **user PFCG value** co match field value trong DCL khong

## 8. Checklist

- [ ] IAM App da duoc cau hinh va gan Business Role?
- [ ] DCL grant dung field trong CDS view?
- [ ] RAP instance-based authorization da implement?
- [ ] PFCG field value match DCL condition?
- [ ] Khong dung direct SELECT bypass DCL?
- [ ] Activity (01/02/03) dung cho use case?

## Nguon tham khao

- SAP Help Portal: CDS Access Control, RAP Authorization
- ABAP Cloud Dev Guide: Authorization Concept
- SAP Community: DCL best practices, IAM app setup
