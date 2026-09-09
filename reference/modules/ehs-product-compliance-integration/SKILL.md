---
name: ehs-product-compliance-integration
description: Knowledge note tổng hợp **EHS (Environment, Health & Safety) + Product Compliance trên BTP** — kiến trúc, integration với MM/SD/GTS/PLM, MSDS workflow, hazardous substance tracking. Khác với `sap-ehs-cloud/SKILL.md` (seed knowledge EHS).
effort: low
model: haiku
---

# EHS + Product Compliance — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **kiến trúc EHS trên Cloud** (EHS embedded vs Product
Compliance on BTP) và integration patterns với MM/SD/GTS/PLM. Không thay thế:
- `sap-ehs-cloud/SKILL.md` — seed knowledge EHS consultant.
- `sap-ehs-consultant-cloud` — agent consult thật.

## 1. EHS trên Cloud có mấy variant?

| Variant                                              | Status                | Use case                  |
|------------------------------------------------------|-----------------------|---------------------------|
| **EHS embedded trong S/4HANA Cloud Public Edition**  | Limited                | Chỉ Product Safety cơ bản|
| **SAP Product Compliance trên BTP**                   | Active (cloud)         | Full Product Safety, REACH, hazmat |
| **EHS on S/4HANA Private Cloud**                    | Active                 | Full EHS                  |
| **SAP EHS on-prem (legacy)**                         | Maintenance            | Đã có sẵn                 |

**Quan trọng**: S/4HANA Cloud Public Edition **chỉ có Product Safety cơ bản** (MSDS, label).
Để có full EHS (Waste, Industrial Hygiene, Incident Mgmt), cần **Product Compliance trên BTP**
hoặc Private Cloud.

## 2. Kiến trúc Product Compliance trên BTP

```
┌────────────────────────────────────────────────────┐
│ SAP Product Compliance (BTP)                      │
│ - Substance / Material master (composition)        │
│ - MSDS generation (multi-region)                   │
│ - Label generation                                  │
│ - Compliance check (REACH, TSCA, GHS)              │
│ - Hazardous substance tracking                      │
└────────────────────────────────────────────────────┘
                    ↕ (Integration qua BTP/CPI)
┌────────────────────────────────────────────────────┐
│ S/4HANA Cloud                                       │
│ - Material master (basic + industry sector)        │
│ - Sales (customer-facing MSDS request)             │
│ - Purchasing (incoming material safety check)      │
│ - GTS (export compliance check)                    │
└────────────────────────────────────────────────────┘
```

## 3. So sánh Variant

| Component              | Embedded S/4HANA Cloud | Product Compliance BTP |
|------------------------|-------------------------|-------------------------|
| Material Safety Data Sheet (MSDS) | Basic         | Full (16-section GHS)   |
| Label generation       | Basic                   | Multi-language          |
| REACH compliance       | ❌                       | ✅                       |
| Hazardous substance    | Limited                 | Full + inventory        |
| Waste management       | ❌                       | ✅                       |
| Industrial hygiene     | ❌                       | ✅                       |
| Incident management    | ❌                       | ✅                       |
| Audit trail            | Standard                | Enhanced                |

## 4. Common Use Cases

### 4.1 MSDS theo yêu cầu khách hàng

```
Customer (SD Sales Order)
  └─ Request MSDS for material X
       └─ Trigger qua OData tới Product Compliance
            └─ Generate MSDS (PDF, 16-section GHS)
                 └─ Return cho sales rep / customer portal
```

### 4.2 REACH / TSCA / GHS compliance check

```
Material master update (MMR)
  └─ Trigger compliance check
       ├─ REACH (EU): substance listed in SVHC?
       ├─ TSCA (US): substance on TSCA inventory?
       ├─ GHS classification updated?
       └─ Result: ✅ / ⚠️ / ❌ + action items
```

### 4.3 Hazardous substance tracking

```
Material received (MM Goods Receipt)
  └─ Hazardous? → quarantine → safety check
       └─ Storage location restriction
            └─ Disposal tracking (waste management)
```

### 4.4 Incident management

```
Worker reports incident (Fiori mobile app)
  └─ EHS module creates incident record
       └─ Investigation workflow
            └─ Root cause analysis
                 └─ Corrective action
                      └─ Regulatory reporting (OSHA / EU-OSHA)
```

## 5. Integration với MM (Procurement)

| Luồng                          | Vai trò MM              | Vai trò EHS/PC          |
|--------------------------------|--------------------------|--------------------------|
| Material master creation       | MM tạo material          | EHS enrich substance data |
| Purchase order                  | MM create PO             | EHS check incoming safety|
| Goods receipt                   | MM post GR               | EHS update inventory hazmat|
| Vendor compliance               | MM vendor master         | EHS vendor safety rating  |

## 6. Integration với SD (Sales)

| Luồng                          | Vai trò SD              | Vai trò EHS/PC          |
|--------------------------------|-------------------------|---------------------------|
| Sales order                     | SD create SO            | EHS auto-attach MSDS nếu customer yêu cầu |
| Outbound delivery               | SD delivery             | EHS check hazmat shipping constraint |
| Export sales                    | SD billing              | EHS export compliance check |

## 7. Integration với GTS (xem `gts-cloud-architecture`)

- **Export compliance**: GTS check licensed/non-licensed destination + EHS check hazmat
  shipment restrictions (qua IMDG/IATA).
- **Customs**: GTS file customs declaration + EHS attach MSDS to customs paperwork.

## 8. Integration với PLM / Recipe Development

- **Recipe/BOM master**: PLM tạo recipe → EHS tự tính composition.
- **Substance impact**: Change material → propagate EHS classification update.
- **New product introduction**: PLM workflow + EHS safety assessment trước go-live.

## 9. Common Fiori apps

| Chức năng                  | Fiori app                                |
|----------------------------|------------------------------------------|
| Material safety check       | Manage Material Safety                   |
| MSDS request                | Request Safety Data Sheet                 |
| Compliance check            | Compliance Check                         |
| Incident report             | Report Incident                          |
| Waste disposal              | Manage Waste Disposal                    |
| Hazmat inventory            | Hazardous Substance Inventory            |

## 10. Side-by-side Extension Patterns

| Pattern                        | Dùng khi                              | Tool                |
|--------------------------------|----------------------------------------|---------------------|
| Custom compliance rule         | Industry-specific regulation           | Product Compliance API |
| Custom MSDS layout             | Customer-specific format                | Adobe Form + BAdI    |
| Custom incident report         | Form custom cho plant                   | SAP Build Forms     |
| EHS analytics                  | Safety KPI dashboard                   | SAP Analytics Cloud  |
| Mobile incident reporting      | Field worker                            | SAP Build + mobile |

## 11. Anti-pattern

- ⚠️ Hardcode hazmat classification trong code — luôn qua Product Compliance.
- ⚠️ Dùng EHS on-prem cho dự án cloud — không compatible.
- ⚠️ Skip MSDS attach cho export customer — sẽ fail audit/customs.
- ⚠️ Lưu detailed composition cho substance cấm — IP risk.
- ⚠️ Bypass incident reporting workflow — OSHA/EU compliance fail.

## 12. Liên kết với các skill khác

- **Consultant**: `sap-ehs-consultant-cloud`.
- **Seed knowledge**: `sap-ehs-cloud/SKILL.md`.
- **Integration**: `sap-mm-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-gts-consultant-cloud`,
  `sap-pp-consultant-cloud` (cho recipe integration), `sap-cpi-consultant-cloud` (BTP integration).
- **Knowledge notes liên quan**: `gts-cloud-architecture` (export compliance).

## 13. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module EHS.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)
  — pattern consume Product Compliance qua OData.
- SAP Help: SAP Product Compliance, REACH, GHS, EHS documentation.
