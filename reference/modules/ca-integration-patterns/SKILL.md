---
name: ca-integration-patterns
description: Knowledge note tổng hợp **CA (Cross-Application) integration patterns** — Business Partner master data sync, Workflow, Output Management, DMS, BRFplus rules, Document Management. Khác với `sap-ca-cloud/SKILL.md` (seed knowledge CA) và `sap-ca-consultant-cloud`.
effort: low
model: haiku
---

# CA — Cross-Application Integration Patterns

Module con của plugin, tập trung vào **integration patterns** của các chức năng Cross-Application
với module khác. Không thay thế:
- `sap-ca-cloud/SKILL.md` — seed knowledge CA consultant.
- `sap-ca-consultant-cloud` — agent consult thật.

## 1. Tổng quan CA components

| Component                       | Mục đích                                  |
|---------------------------------|--------------------------------------------|
| **Business Partner (BP)**       | Master data duy nhất cho Customer/Supplier/Employee |
| **Document Management (DMS)**   | Lưu trữ file liên kết object              |
| **Workflow**                    | Approval workflow generic                  |
| **Output Management**           | Output (email/print/EDI) từ business event |
| **Number Ranges**               | Sinh ID cho nhiều object                   |
| **BRFplus (Rules)**             | Decision table / rule engine                |
| **Archiving**                   | Data aging & storage tiering                |
| **Reporting Framework**         | Drill-down reports từ CDS view              |

## 2. Business Partner (BP) — Integration patterns

### BP là master data duy nhất

Trên S/4HANA Cloud, **không có Customer/Supplier riêng** - cả hai đều là BP với role tương ứng.

```
Business Partner (BP)
  ├─ Role: Customer (FLCU00... FLCU02) → FI customer master (BUT000-BP linked to KNA1)
  ├─ Role: Supplier (FLVN00... FLVN02) → FI vendor master
  └─ Role: Employee (BUP003)           → HCM personnel number (nếu hybrid)
```

### BP Integration với module khác

| Module       | Integration Point                        | Ghi chú                  |
|--------------|-------------------------------------------|---------------------------|
| SD           | BP role Customer → Sales Order            | Customer ID = BP number  |
| MM           | BP role Supplier → Purchase Order          | Vendor ID = BP number    |
| FI           | BP → Customer/Vendor master (auto-sync)   | Sync qua standard task   |
| HCM          | BP role Employee → Personnel number        | Hybrid với SuccessFactors|
| RE           | BP role Business Partner (real estate)    | Property owner/tenant    |
| PS           | BP → Project sponsor / responsible         | Reference tới BP         |

### BP API Released

- **OData V4**: `API_BUSINESS_PARTNER` — read/write BP master data.
- **Released class**: `cl_bupa_helper`, `cl_bupa_central_data` (xem `sap-released-classes`).

## 3. Document Management (DMS) — Integration

DMS lưu trữ file liên kết với business object (Material, Equipment, Sales Order, ...).

```
Object (vd Material MAT-001)
  └─ Document Info Record (DIR)
       └─ Original file (PDF, JPEG, ...)
       └─ Version history
       └─ Authorization check
```

### DMS vs External DMS

| Aspect             | SAP DMS (embedded)             | External (SharePoint, OpenText)       |
|--------------------|---------------------------------|----------------------------------------|
| Storage            | Content Server / ArchiveLink    | External repository                    |
| Search             | Via SAP GUI / Fiori             | Native search                          |
| Workflow           | Via SAP Workflow               | Native workflow                        |
| Suitability        | Simple attachment need          | Heavy document collaboration           |

Trên Public Cloud, DMS embedded **giới hạn** — cho collaboration phức tạp, đánh giá dùng
**SAP Build Work Zone** hoặc **OpenText** integration.

### DMS Integration

- **Material**: DIR liên kết qua `MARA-MATNR` → spec sheet, MSDS.
- **Equipment**: DIR cho maintenance manual.
- **Sales Order**: DIR cho customer-signed contract.

## 4. Workflow — Generic Approval

SAP Workflow cho phép:
- Multi-step approval (kế tiếp / song song).
- Approval based on role (manager hierarchy từ SF/BP).
- Timeout/escalation.
- Substitute approver.

```
Workflow Definition (WS)
  ├─ Task (TS)
  │    ├─ Standard task (WS_PREFIX)
  │    └─ Custom task (Z_...)
  ├─ Trigger (event/condition)
  └─ Notification (email / Fiori inbox)
```

### Trên Cloud Public Edition

Workflow cho Cloud dùng **Fiori Inbox** làm frontend thay vì SAP Business Workplace.
Một số loại workflow:
- **Release strategy** cho PR/PO (qua Fiori app).
- **Invoice approval** (qua Fiori app).
- **Generic Workflow** cho custom business object — dùng
  **SAP Business Workflow trên Public Cloud** + Fiori Inbox.

### Custom Workflow

Nếu cần workflow phức tạp (multi-level, dynamic approvers, condition-based), dùng:
- **SAP Build Process Automation** (low-code).
- **BPMN 2.0 modeling** (qua Steampunk / CAP).

## 5. Output Management

Output Management = cách SAP gửi output (email/print/EDI) khi có business event.

```
Business Event (vd SO created)
  └─ Output Rule
       ├─ Channel: Email / Print / EDI / XML
       ├─ Form: Adobe Form / Smart Form / Word doc
       ├─ Recipient: dynamic (BP email / printer)
       └─ Trigger: synchronous / scheduled
```

### Output Channel

| Channel   | Khi nào dùng                            |
|-----------|------------------------------------------|
| Email     | Customer-facing (PO confirmation, invoice)|
| Print     | Pick list, shipping label               |
| EDI       | B2B (despatch advice, invoice via VAN)  |
| XML       | E-document hóa đơn điện tử (Việt Nam, EU)|
| BRF+ rule | Conditional output based on rule         |

Trên Cloud Public Edition, **Adobe Form** là standard cho PDF output (thay Smart Form).

## 6. BRFplus — Rule Engine

BRFplus (Business Rules Framework plus) cho phép define rule qua UI không cần code:
- Decision tables.
- Expressions.
- Lookup tables.
- Composite rules.

### Use case cho BRFplus

- Output channel selection (email vs print dựa trên BP country).
- Tax code selection (cho multi-country).
- Discount approval (automatic approve < $1000, manual otherwise).
- Pricing rule overrides (cho special customer group).

### So sánh BRFplus vs Cloud BAdI vs custom code

| Approach       | Pros                          | Cons                              |
|----------------|-------------------------------|-----------------------------------|
| BRFplus        | Business user maintainable    | Limited logic                     |
| Cloud BAdI     | Full ABAP flexibility         | Need developer                    |
| Custom code    | Any logic                     | Hard to maintain                  |

**Khuyến nghị**: BRFplus cho rule business thường thay đổi (tax, discount). Cloud BAdI cho
rule cần ABAP. Custom code cho rule stable.

## 7. Number Ranges

Sinh ID tự động cho object (Material, Sales Order, PO, BP, ...).

```
Number Range Object (TNRO)
  ├─ Element: element name trong table
  ├─ Range: 0000001 - 9999999
  ├─ Interval: sub-range theo năm / plant
  └─ External: cho phép gán số ngoài
```

### Number Range trên Cloud Public Edition

- Default range được SAP set khi system được tạo.
- Có thể extend range (qua Fiori app **Manage Number Range Intervals**).
- KHÔNG được reset range khi đang dùng (audit trail).
- KHÔNG được overlap range giữa 2 system.

## 8. Archiving & Data Aging

Dữ liệu cũ (> 2 năm) có thể move sang storage tier rẻ hơn hoặc archive.

```
S/4HANA Hot Store (HANA memory)
  └─ S/4HANA Warm Store (HANA disk)
       └─ Archived (separate file)
```

### Data Aging vs Archiving

| Approach      | Mục đích                            | Reverse           |
|---------------|--------------------------------------|-------------------|
| Data Aging    | Move data sang warm store           | Hot → warm auto   |
| Archiving     | Move sang archive file (outside HANA)| Cần reload        |

Cloud Public Edition: **Data Aging** available, **Archiving** cũng có (qua Fiori app).

## 9. Reporting Framework

Generic reporting từ CDS view + OData:

```
CDS View (analytical)
  └─ Annotation (@UI.*)
       └─ OData V4 Service (auto-generated)
            └─ Fiori Elements app (List Report / Analytical)
```

### Common Fiori apps

- **Custom Analytical Queries** (qua Fiori app Query Designer).
- **KPI tiles** cho dashboard.
- **Overview Page** (Fiori Elements multi-card).

## 10. Side-by-side Extension Patterns

| Pattern                        | Dùng khi                              | Tool                |
|--------------------------------|----------------------------------------|---------------------|
| Custom field on BP             | Industry-specific BP data              | SSCUI Custom Field  |
| Custom workflow                | Multi-level approval                   | SAP Build / BPMN    |
| Custom output form             | PDF custom cho region                  | Adobe Form + Cloud BAdI |
| Custom BRF rule                | Business rule change often             | BRFplus             |
| Custom number range            | Multi-entity ID                        | SSCUI               |

## 11. Anti-pattern

- ⚠️ Tạo Customer/Supplier riêng (legacy custom) — luôn dùng BP.
- ⚠️ Dùng SAP Business Workplace trên Cloud — không available, dùng Fiori Inbox.
- ⚠️ Hardcode number range trong code — luôn qua TNRO.
- ⚠️ Skip BRFplus cho rule business thường đổi — sẽ khó maintain.
- ⚠️ Lưu PII trong custom field BP không có authorization — GDPR risk.
- ⚠️ Attach document lớn vào DMS không scan virus — security risk.

## 12. Liên kết với các skill khác

- **Consultant**: `sap-ca-consultant-cloud`.
- **Seed knowledge**: `sap-ca-cloud/SKILL.md`.
- **Integration**: `sap-fi-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`,
  `sap-successfactors-consultant-cloud`, `sap-pm-consultant-cloud`.
- **Released class**: `sap-released-classes` mục "RAP Runtime" + tìm `cl_bupa_*` (BP API).
- **BTP architecture**: `sap-btp-connectivity`.

## 13. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module CA.
- [`marcellourbani/vscode_abap_remote_fs`](https://github.com/marcellourbani/vscode_abap_remote_fs) —
  workflow + RAP extension pattern.
- SAP Help: Business Partner, Document Management, Workflow, Output Management, BRFplus.
