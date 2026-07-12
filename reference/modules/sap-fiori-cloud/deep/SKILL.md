---
name: sap-fiori-cloud
description: Kien thuc SAP Fiori / UI5 chi tiet — Fiori App Reference Library, Adaptation Project, CDS annotation cho Fiori Elements, Freestyle UI5 pattern, Launchpad config, SAP Build.
effort: medium
model: haiku
---

# Fiori/UI5 — DEEP — Public Cloud & BTP

[Seed set — kiem chung qua SAP Community; Fiori app ID va version thay doi theo tung release.]

## 1. Fiori App Reference Library

Tra cuu tai `https://fioriappslibrary.hana.ondemand.com/`:

| Semantic Object | App | Fiori ID |
|---|---|---|
| SalesOrder | Manage Sales Orders | F1234 |
| PurchaseOrder | Manage Purchase Orders | F1235 |
| BusinessPartner | Manage Business Partner | F0880A |
| JournalEntry | Post General Journal Entry | F0718 |

**Cach tra cuu**: Fiori ID -> role can -> OData service -> UI5 version -> app type (Element vs Freestyle).

## 2. Adaptation Project

**Tool**: SAPUI5 Visual Editor (VS Code extension + Web IDE)

| Kha nang | Gioi han |
|---|---|
| Them/an field | Khong the them logic moi phuc tap |
| Sap xep lai field/group | Khong the thay doi business logic cua app |
| Them fragment (custom section) | Can UI5 developer |

**Quy trinh**: 
1. Tao Adaptation Project trong SAP BTP Cockpit -> Work Zone
2. Mo Visual Editor
3. Tuy chinh (field, group, label, fragment)
4. Activate -> publish to role

## 3. Fiori Elements + CDS Annotation

| Annotation | Y nghia | Vi du |
|---|---|---|
| `@UI.selectionField` | Field trong filter bar | `[{value: "buyerParty"}]` |
| `@UI.lineItem` | Cot trong list | `[{position: 10, value: 'SalesOrder'}]` |
| `@UI.fieldGroup` | Nhom field trong form | `[{qualifier: 'General', value: 'SalesOrder'}]` |
| `@UI.identification` | Field trong object page | |

**Pattern**: CAP CDS vs ABAP CDS:
- ABAP CDS: `@Metadata.allowExtensions` + `@EndUserText.label`
- CAP CDS: `@title`, `@Common: {label: ''}`

## 4. Launchpad Config

| Thanh phan | Mo ta |
|---|---|
| **Business Role** | Gan quyen cho user, VD `SAP_BR_SALES_MANAGER` |
| **Catalog** | Nhom Fiori app, VD `SAP_SD_BC_SALES_ORDER_PROC` |
| **Group** | Nhom tile tren Launchpad, VD `Sales` |
| **Target Mapping** | Semantic Object + Action -> Fiori app |

**Cau hinh**: BTP Cockpit -> Subaccount -> Work Zone -> Business Roles.

## 5. SAP Build

| Product | Use case |
|---|---|
| **SAP Build Apps** | Low-code UI (drag-drop), khong can UI5 |
| **SAP Build Work Zone** | Fiori Launchpad + Site Manager + unified entry |
| **SAP Build Process Automation** | Workflow + automation |

## 6. Khi can UI5 development

- **Template**: SAP Fiori Application (freestyle) vs SAP Fiori Elements (annotations)
- **Framework**: SAPUI5 (OpenUI5), compatible with OData V2/V4
- **Pattern**: Component-based architecture (Component.js, manifest.json)
- **Deployment**: MTA archive -> Cloud Foundry

## 7. Nguon tham khao

- Fiori App Reference Library: `https://fioriappslibrary.hana.ondemand.com/`
- SAPUI5 Documentation: `https://sapui5.hana.ondemand.com/`
- SAP Build: `https://www.sap.com/products/technology-platform/build.html`
- SAP Community Fiori tag: `https://community.sap.com/t5/sap-fiori/`
