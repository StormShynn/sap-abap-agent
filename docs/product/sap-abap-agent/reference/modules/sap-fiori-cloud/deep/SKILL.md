---
name: sap-fiori-cloud
description: Kien thuc SAP Fiori / UI5 chi tiet — Fiori App Reference Library, Adaptation Project, CDS annotation cho Fiori Elements, Freestyle UI5 pattern, Launchpad config, SAP Build, Fiori Tools/BAS.
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

### 3.1 Template (khi tao Fiori Elements app)

| Template | Dung khi |
|----------|----------|
| **List Report** | List + filter + detail (CRUD) |
| **Object Page** | Single object detail |
| **Overview Page** | Dashboard |
| **Analytical List Page** | Chart + table KPI |
| **Worklist** | Task list |

### 3.2 Annotation

| Annotation | Y nghia | Vi du |
|---|---|---|
| `@UI.selectionField` | Field trong filter bar | `[{value: "buyerParty"}]` |
| `@UI.lineItem` | Cot trong list | `[{position: 10, value: 'SalesOrder'}]` |
| `@UI.fieldGroup` | Nhom field trong form | `[{qualifier: 'General', value: 'SalesOrder'}]` |
| `@UI.identification` | Field trong object page | |

**Pattern**: CAP CDS vs ABAP CDS:
- ABAP CDS: `@Metadata.allowExtensions` + `@EndUserText.label`
- CAP CDS: `@title`, `@Common: {label: ''}`

**Vi du annotation.xml** (annotation ngoai, khong sua duoc CDS goc):

```xml
<Annotations Target="SAP_Z_SALES_ORDER_SRV.SalesOrderType">
  <Annotation Term="UI.LineItem">
    <Collection>
      <Record Type="UI.DataField">
        <PropertyValue Property="Value" Path="SalesOrderID"/>
        <PropertyValue Property="Label" String="Sales Order"/>
      </Record>
      <Record Type="UI.DataField">
        <PropertyValue Property="Value" Path="NetAmount"/>
        <PropertyValue Property="Label" String="Net Amount"/>
      </Record>
    </Collection>
  </Annotation>
</Annotations>
```

## 4. Launchpad Config

| Thanh phan | Mo ta |
|---|---|
| **Business Role** | Gan quyen cho user, VD `SAP_BR_SALES_MANAGER` |
| **Catalog** | Nhom Fiori app, VD `SAP_SD_BC_SALES_ORDER_PROC` |
| **Group** | Nhom tile tren Launchpad, VD `Sales` |
| **Target Mapping** | Semantic Object + Action -> Fiori app |

**Cau hinh**: BTP Cockpit -> Subaccount -> Work Zone -> Business Roles.

**manifest.json** (dang ky app vao Launchpad):

```json
{
  "sap.cloud": {
    "public": true,
    "service": "my-fiori-app.service"
  },
  "sap.ui5": {
    "dependencies": {
      "libs": {
        "sap.m": {},
        "sap.ui.core": {},
        "sap.ushell": {}
      }
    },
    "contentDensities": {
      "compact": true,
      "cozy": true
    }
  }
}
```

## 5. SAP Build

| Product | Use case |
|---|---|
| **SAP Build Apps** | Low-code UI (drag-drop), khong can UI5 |
| **SAP Build Work Zone** | Fiori Launchpad + Site Manager + unified entry |
| **SAP Build Process Automation** | Workflow + automation |

## 6. Fiori Tools (SAP Business Application Studio)

Fiori Tools la VS Code extension set trong SAP Business Application Studio (BAS):

| Tool | Chuc nang |
|------|-----------|
| **Fiori: Open Application Info** | App overview |
| **Fiori: Add Fiori Elements** | Create FE app |
| **Fiori: Add UI5 freestyle** | Create freestyle app |
| **Fiori: Generate Annotations** | Auto-annotations |
| **Fiori: Deploy** | Deploy to CF / ABAP |

```bash
# Tao Fiori app moi (BAS): Fiori: Application -> Template -> Data source -> Config -> Deploy

# Deploy len Cloud Foundry
cf push my-fiori-app

# Deploy len ABAP (S/4HANA): SAP BTP Cockpit -> Work Zone -> Business Role -> Add App
```

## 7. Freestyle UI5 Development

Chi dung khi Fiori Elements khong dap ung (complex UI, custom control can UI5 developer).

**Kien truc app**:

```
Fiori App
  ├─ Component.js (entry point)
  ├─ manifest.json (app descriptor)
  ├─ i18n/i18n.properties (translations)
  ├─ view/App.view.xml (XML view)
  ├─ controller/App.controller.js
  ├─ model/ (JSON/OData model)
  └─ util/ (helpers)
```

**Model**:

| Model | Dung khi | Vi du |
|-------|----------|-------|
| `JSONModel` | Client data | `new JSONModel({ name: 'John' })` |
| `ODataModel (V2)` | OData V2 service | `new ODataModel("/sap/opu/odata/")` |
| `ODataModel (V4)` | OData V4 service | `new ODataModel({ serviceUrl: "/odata/v4/" })` |
| `ResourceModel` | i18n | `new ResourceModel({ bundleUrl: "i18n/i18n.properties" })` |

**View type**:

| Type | Dung khi | Vi du |
|------|----------|-------|
| XML | Mac dinh (khuyen dung) | `<mvc:View>...</mvc:View>` |
| JSON | Nho, don gian | `{ "type": "sap.m.Page" }` |
| JS | Legacy | `createContent: function() {}` |
| HTML | HTML fragment | `<div>...</div>` |

**Binding**:

```javascript
// Property binding
<Text text="{/firstName}" />

// Element binding
<Input value="{path: '/name', type: 'sap.ui.model.type.String'}" />

// Expression binding
<Text text="{= ${/total} > 1000 ? 'High' : 'Low' }" />

// Formatter
<Text text="{path: '/date', formatter: '.formatDate'}" />
```

**Deployment**:

| Target | Method | Mo ta |
|--------|--------|-------|
| Cloud Foundry (BTP) | `cf push` | Fiori standalone app, dong goi MTA archive |
| S/4HANA (ABAP) | LREP (UI5 Deploy) | Deploy to ABAP server |
| SAP Build Work Zone | Site Manager | Fiori Launchpad |
| SAP NetWeaver Gateway | UI5 Repository | Legacy Gateway |

**Testing (OPA)**:

```javascript
sap.ui.require([
  "sap/ui/test/Opa5"
], function(Opa5) {
  Opa5.extendConfig({
    arrangements: new Arrangement(),
    actions: new Actions(),
    assertions: new Assertions()
  });

  // Wait for app
  Opa5.iStartMyAppInAFrame("/index.html");
});
```

## 8. Nguon tham khao

- Fiori App Reference Library: `https://fioriappslibrary.hana.ondemand.com/`
- SAPUI5 Documentation: `https://sapui5.hana.ondemand.com/`
- Fiori Tools: `https://help.sap.com/docs/fiori-tools`
- SAP Business Application Studio: `https://help.sap.com/docs/bas`
- SAP Build: `https://www.sap.com/products/technology-platform/build.html`
- SAP Community Fiori tag: `https://community.sap.com/t5/sap-fiori/`
