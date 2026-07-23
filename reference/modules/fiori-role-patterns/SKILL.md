---
name: fiori-role-patterns
description: Knowledge note tổng hợp **Fiori / UI5 theo 3 role cụ thể** — Solution Architect (Fiori Elements vs Custom UI5), UX Designer (Fiori Design Guidelines, SAP Build Work Zone), ABAP / Frontend Developer (RAP, Annotations, Freestyle UI5). Khác với `sap-fiori-cloud/SKILL.md` (seed consultant) và `fiori-elements-cloud/SKILL.md` (RAP-pattern knowledge note).
effort: low
model: haiku
---

# Fiori / UI5 — Role-based Patterns Knowledge Note

Module con của plugin, tập trung vào **cách làm Fiori/UI5 khác nhau theo 3 role** chính trong
team dự án. Không thay thế:
- `sap-fiori-cloud/SKILL.md` — seed knowledge Fiori consultant (general).
- `fiori-elements-cloud/SKILL.md` — knowledge note về Fiori Elements (technology).
- `sap-fiori-consultant-cloud` — agent consult thật.

## 1. Tại sao chia theo role?

Cùng 1 dự án Fiori, **mỗi role cần quan tâm khía cạnh khác nhau**:

| Role                 | Quan tâm chính                              | Output chính           |
|----------------------|---------------------------------------------|--------------------------|
| **Solution Architect** | Chọn technology (Elements vs Custom), governance, integration | Architecture document  |
| **UX Designer**       | User journey, wireframe, Fiori Design Guidelines | Mockup, prototype       |
| **Frontend Developer** | Code UI5, RAP annotation, freestyle vs Elements | Working app              |

## 2. Role 1: Solution Architect

### Decision framework

```
                              ┌──────────────────────┐
                              │  Need standard CRUD? │
                              └──────┬───────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
            ┌───────────────┐                 ┌───────────────┐
            │  YES          │                 │  NO           │
            │ (table + form)│                 │ (complex UI)  │
            └───────┬───────┘                 └───────┬───────┘
                    ▼                                 ▼
            ┌───────────────┐                 ┌───────────────┐
            │ Fiori Elements │                 │ Free-style UI5│
            │ (List Report + │                 │ (XML/JS view) │
            │ Object Page)   │                 │               │
            └───────────────┘                 └───────────────┘
```

### Câu hỏi architect cần trả lời

1. **CRUD-only hay custom UI**: 
   - CRUD-only → Fiori Elements.
   - Custom workflow, complex UI (canvas, custom widget) → Free-style UI5.

2. **Reuse có sẵn hay build mới**:
   - SAP Fiori Reference Apps (vd "Build Apps" của SAP) có thể match → dùng.
   - Không match → build mới (Elements hoặc Custom).

3. **Multi-app workspace hay single-app**:
   - Multi-app → **SAP Build Work Zone** (launchpad + integration).
   - Single-app → embed trực tiếp.

4. **Mobile cần không**:
   - Cần offline/mobile → **SAP Build Apps** (low-code) hoặc **SAP Mobile Start**.
   - Desktop only → UI5 standard.

5. **Extension model**:
   - Extend Fiori app có sẵn → dùng **Fiori Elements flexibility** ho�c **UI5 extension point**.
   - Build mới từ đầu → Fiori Elements hoặc Custom.

### Architecture deliverables

- **Architecture Decision Record (ADR)**: tại sao chọn Elements vs Custom.
- **App map**: tất cả Fiori apps + dependencies.
- **Integration map**: app nào gọi OData nào.
- **Security model**: role-based access (qua IAM / DCL).
- **Performance budget**: response time < 1s, payload < 100KB.

### Common mistakes

- ⚠️ Chọn Custom UI5 cho use case có thể giải bằng Elements (tốn effort).
- ⚠️ Không check Fiori Reference Apps trước — reinvent wheel.
- ⚠️ Bỏ qua SAP Build Work Zone — multi-app launch rất quan trọng.
- ⚠️ Plan single-page app cho enterprise — quá tải, dùng multi-app.

## 3. Role 2: UX Designer

### Fiori Design Guidelines (FDG) — Bắt buộc đọc

SAP Fiori Design Guidelines là **rule book** cho mọi Fiori app:
- 5 principles: Role-based, Coherent, Simple, Delightful, Adaptive.
- Layout: List Report, Object Page, Analytical List Page, Overview Page.
- Component library: card, form, table, chart, smart filter bar.
- Color: SAP Belize / SAP Horizon theme.
- Accessibility: WCAG 2.1 AA level.

### Workflow UX Designer

```
1. Understand user (Persona)
   └─ "Senior accountant phải đối chiếu 200 invoice/ngày"
2. Define user journey
   └─ Mở app → Filter theo status → Drill down → Approve
3. Sketch wireframe (Figma / Sketch)
   └─ List Report với filter + action button + table
4. Validate với Fiori Design Guidelines
   └─ Component dùng đúng chỗ? Color đúng?
5. Build prototype (Fiori Elements demo data)
   └─ User test trước khi code thật
6. Handoff cho developer
   └─ Mockup + annotation + edge case
```

### Tool UX Designer nên biết

| Tool                    | Use case                              |
|-------------------------|------------------------------------------|
| **Figma + SAP UI5 Kit** | Mockup chuẩn Fiori Design              |
| **SAP Build Work Zone** | Preview launchpad + tile               |
| **SAPUI5 SDK Demo Kit** | Xem component thật                      |
| **Fiori Reference Apps**| Inspiration cho app structure          |
| **SAP Build Apps**      | Prototype interactive (low-code)        |
| **User Testing Toolkit** | Test thực với user                     |

### Common UX mistakes

- ⚠️ Bỏ qua FDG — design không consistent với SAP ecosystem.
- ⚠️ Quá nhiều action trên 1 screen — overwhelm user.
- ⚠️ Không test accessibility — WCAG fail, không dùng được cho disabled user.
- ⚠️ Hardcode label tiếng Anh — SAP app global, cần i18n.
- ⚠️ Bỏ qua empty state — khi list rỗng, user confused.

### Accessibility checklist

- [ ] Color contrast >= 4.5:1 (WCAG AA).
- [ ] All controls keyboard navigable.
- [ ] Screen reader friendly (ARIA labels).
- [ ] Form error announce to screen reader.
- [ ] No time-based interaction bắt buộc.

## 4. Role 3: Frontend Developer (UI5 + RAP)

### Skill set cần có

| Skill                  | Mức cần                                |
|------------------------|-----------------------------------------|
| **SAPUI5 / OpenUI5**   | Bắt buộc (XML view, controller, manifest)|
| **JavaScript / TypeScript** | Bắt buộc (ES6+, async/await)         |
| **OData V4**           | Bắt buộc (binding, batch, deep insert)   |
| **Fiori Elements**     | Bắt buộc (annotation, List Report)      |
| **CDS + Annotations**  | Khuyến nghị (UI annotation)              |
| **CAP / Steampunk RAP**| Khuyến nghị (cho custom OData)          |
| **Git + abapGit**      | Bắt buộc (versioning, transport)         |
| **Fiori tooling**      | Khuyến nghị (VS Code extension)         |

### Workflow developer

```
1. Setup dev environment
   ├─ VS Code + SAP Fiori Tools extension
   ├─ BAS (Business Application Studio) - cloud IDE
   └─ Local Node.js + UI5 CLI
2. Generate app skeleton
   ├─ `yo easy-ui5` (generator)
   └─ Hoặc từ template (List Report / Object Page)
3. Connect to backend
   ├─ Mock server (local)
   └─ Real SAP system (qua destination)
4. Implement UI
   ├─ View (XML/JS)
   ├─ Controller (JS)
   ├─ Fragment (reusable)
   └─ i18n (properties file)
5. Test
   ├─ Unit test (QUnit)
   ├─ E2E test (OPA5 / wdi5)
   └─ Manual (browser)
6. Build + Deploy
   ├─ `npm run build` (output to dist/)
   └─ Deploy lên SAP BTP hoặc on-prem
```

### Code convention quan trọng

#### Manifest (`manifest.json`)

```json
{
  "_version": "1.12.0",
  "sap.app": {
    "id": "com.example.zsalesorder",
    "type": "application",
    "i18n": "i18n/i18n.properties"
  },
  "sap.ui5": {
    "dependencies": {
      "libs": {
        "sap.m": {},
        "sap.fe": {}  // Fiori Elements
      }
    },
    "routing": {
      "routes": [...]
    }
  },
  "sap.cloud": {
    "public": true
  }
}
```

#### Controller (ES6 class)

```javascript
import Controller from "sap/ui/core/mvc/Controller";
import JSONModel from "sap/ui/model/json/JSONModel";

export default class Main extends Controller {
  onInit() {
    const oModel = new JSONModel({ busy: true });
    this.getView().setModel(oModel, "view");
  }

  async onRefresh() {
    // Gọi OData service
  }
}
```

### Fiori Elements — extension point

Khi Fiori Elements không đủ, thêm extension point:

```javascript
// Customer.controller.js (extension cho Object Page)
sap.ui.define([
  "sap/ui/core/mvc/ControllerExtension"
], function(ControllerExtension) {
  "use strict";
  return ControllerExtension.extend("customer.ext.Customer", {
    override: {
      onAfterRendering: function() {
        // Custom logic sau khi Object Page render
      }
    }
  });
});
```

Manifest config:
```json
"extends": {
  "extensions": {
    "sap.ui.controllerExtensions": {
      "sap.suite.ui.generic.template.ObjectPage.view.Details": {
        "controllerName": "customer.ext.Customer"
      }
    }
  }
}
```

### Common developer mistakes

- ⚠️ Bind trực tiếp vào model default — dùng named model.
- ⚠️ Không dùng i18n — hardcode text, không localize được.
- ⚠️ Skip linter (`@ui5/linter`) — inconsistent code style.
- ⚠️ Dùng `sap.ui.define` cũ (ES5) — code trộn.
- ⚠️ Quên cleanup trong `onExit()` — memory leak.
- ⚠️ Bundle quá lớn (> 2MB) — performance issue.

## 5. Cross-role collaboration

### Handoff checklist

- [ ] **Architect → UX Designer**: ADR + user persona + integration map.
- [ ] **UX Designer → Developer**: Mockup + annotation + edge case + empty state.
- [ ] **Developer → QA**: Build artifact + test data + acceptance criteria.
- [ ] **All → Business**: Demo session trước go-live.

### Common tool

- **Figma** (mockup) → **VS Code / BAS** (code) → **Fiori Launchpad** (deploy).
- **Jira / Azure DevOps** để track user story → test case → bug.

## 6. Side-by-side Extension Patterns

| Pattern                    | Dùng khi                              | Tool                |
|----------------------------|----------------------------------------|---------------------|
| Extend Fiori Reference App | App gần giống có sẵn                  | Extension project   |
| Custom app from scratch    | Use case unique                        | Fiori Elements / UI5|
| Mobile-first app            | Field worker                           | SAP Build Apps      |
| Dashboard / analytics      | KPI monitoring                         | SAP Analytics Cloud |
| Workflow-driven UI         | Multi-step approval                   | SAP Build           |

## 7. Liên kết với các skill khác

- **Consultant**: `sap-fiori-consultant-cloud`.
- **Seed knowledge**: `sap-fiori-cloud/SKILL.md`.
- **Knowledge notes liên quan**: `fiori-elements-cloud` (technology deep-dive).
- **RAP + Cloud-side**: `abap-rap-cloud` (cho backend integration).
- **Build / extensibility**: `sap-extensibility` (xem `sap-cloud-dictionary` cho custom field).
- **BTP**: `sap-btp-connectivity`, `sap-btp-admin-consultant-cloud`.

## 8. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — Fiori module.
- [`marcellourbani/vscode_abap_remote_fs`](https://github.com/marcellourbani/vscode_abap_remote_fs) —
  Fiori + RAP extension pattern.
- [`skalmodiya/sap-ai-core-launchpad`](https://github.com/skalmodiya/sap-ai-core-launchpad) —
  FastAPI + React frontend pattern.
- SAP Fiori Design Guidelines (help.sap.com).
- SAPUI5 SDK Demo Kit.
- Fiori Reference Apps: fioriappslibrary.hana.ondemand.com.
