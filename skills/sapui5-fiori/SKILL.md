---
name: sapui5-fiori
description: Huong dan SAPUI5/Fiori development — UI5 framework, component, model, view, controller, i18n, theming, deployment, Fiori Tools, SAP Business Application Studio.
when_to_use: |
  "UI5 app development", "Fiori Tools", "SAP Business Application Studio trong Fiori",
  "UI5 component pattern", "UI5 model binding", "deploy Fiori app", "Fiori launchpad integration".
argument-hint: "[cau hoi ve SAPUI5 / Fiori development / UI5 framework]"
effort: medium
effort: medium
model: sonnet
---

# SAPUI5 & Fiori Development

## 1. Architecture

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

## 2. UI5 Framework Concepts

### Models

| Model | Dung khi | Vi du |
|-------|----------|-------|
| `JSONModel` | Client data | `new JSONModel({ name: 'John' })` |
| `ODataModel (V2)` | OData V2 service | `new ODataModel("/sap/opu/odata/")` |
| `ODataModel (V4)` | OData V4 service | `new ODataModel({ serviceUrl: "/odata/v4/" })` |
| `ResourceModel` | i18n | `new ResourceModel({ bundleUrl: "i18n/i18n.properties" })` |

### View Types

| Type | Dung khi | Vi du |
|------|----------|-------|
| XML | ✅ Mac dinh (khuyen dung) | ```` |
| JSON | Nho, don gian | `{ "type": "sap.m.Page" }` |
| JS | Legacy | `createContent: function() {}` |
| HTML | HTML fragment | ```` |

### Binding Types

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

## 3. Fiori Elements (Khuyen dung)

Fiori Elements = config-driven UI, khong can code UI5 view:

| Template | Dung khi |
|----------|----------|
| **List Report** | List + filter + detail (CRUD) |
| **Object Page** | Single object detail |
| **Overview Page** | Dashboard |
| **Analytical List** | Chart + table KPI |
| **Worklist** | Task list |

### Annotation-driven

```xml
<!-- annotation.xml -->
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

## 4. Fiori Tools (SAP Business Application Studio)

Fiori Tools la VS Code extension set trong SAP Business Application Studio:

| Tool | Chuc nang |
|------|-----------|
| **Fiori: Open Application Info** | App overview |
| **Fiori: Add Fiori Elements** | Create FE app |
| **Fiori: Add UI5 freestyle** | Create freestyle app |
| **Fiori: Generate Annotations** | Auto-annotations |
| **Fiori: Deploy** | Deploy to CF / ABAP |

### Commands

```bash
# Create new Fiori app (BAS)
# Fiori: Application -> Template -> Data source -> Config -> Deploy

# Deploy to Cloud Foundry
cf push my-fiori-app

# Deploy to ABAP (S/4HANA)
# SAP BTP Cockpit -> Work Zone -> Business Role -> Add App
```

## 5. Deployment Options

| Target | Method | Mo ta |
|--------|--------|-------|
| Cloud Foundry (BTP) | `cf push` | Fiori standalone app |
| S/4HANA (ABAP) | LREP (UI5 Deploy) | Deploy to ABAP server |
| SAP Build Work Zone | Site Manager | Fiori Launchpad |
| SAP NetWeaver Gateway | UI5 Repository | Legacy Gateway |

## 6. Fiori Launchpad Integration

```json
// manifest.json - SAP Cloud Platform configuration
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
        "sap.ushell": {}  // Fiori Launchpad
      }
    },
    "contentDensities": {
      "compact": true,
      "cozy": true
    }
  }
}
```

## 7. Testing

```javascript
// OPA Testing
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

## Nguon tham khao

- SAPUI5 Documentation: `https://sapui5.hana.ondemand.com/`
- Fiori Tools: `https://help.sap.com/docs/fiori-tools`
- SAP Fiori App Reference Library: `https://fioriappslibrary.hana.ondemand.com/`
- SAP Business Application Studio: `https://help.sap.com/docs/bas`
