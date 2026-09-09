---
name: ibp-cloud-integration
description: Knowledge note tổng hợp **IBP (Integrated Business Planning)** — kiến trúc, integration với S/4HANA & ECC, planning models. Khác với `sap-ibp-cloud/SKILL.md` (seed consultant IBP) và `sap-ibp-consultant-cloud`.
effort: low
model: haiku
---

# IBP — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **kiến trúc IBP (Integrated Business Planning for Supply
Chain)** trên Cloud. Không thay thế:
- `sap-ibp-cloud/SKILL.md` — seed knowledge IBP consultant.
- `sap-ibp-consultant-cloud` — agent consult thật.

## 1. IBP là gì?

IBP = **SAP Integrated Business Planning for Supply Chain**. Cloud-native successor của SAP
APO (Advanced Planning and Optimization). Chạy trên SAP HANA Cloud, không embedded trong S/4HANA.

**Use case**:
- Demand planning (forecast).
- Supply planning (áp dụng cho cả S/4HANA live + on-prem ECC).
- Inventory optimization.
- S&OP (Sales & Operations Planning).
- Response & supply balancing.

## 2. Architecture

```
┌────────────────────────────────────────────────────┐
│ SAP IBP (BTP / HANA Cloud)                       │
│ - Planning models (time series, attributes)        │
│ - Planning operators (heuristics, optimizers)      │
│ - Excel UI / Web UI                                │
│ - Pre-built integration content cho S/4HANA        │
└────────────────────────────────────────────────────┘
                    ↕ (Integration via HCI / CPI / OData)
┌────────────────────────────────────────────────────┐
│ S/4HANA Cloud hoặc ECC on-prem                   │
│ - Master data (Material, Customer, Supplier)       │
│ - Transactional data (SO, PO, Inventory)            │
└────────────────────────────────────────────────────┘
```

## 3. IBP Modules chính

| Module                                | Mục đích                                |
|---------------------------------------|------------------------------------------|
| **IBP for Demand**                    | Statistical forecasting, demand sensing   |
| **IBP for Supply**                    | Heuristic + optimizer-based supply       |
| **IBP for Inventory**                 | Multi-echelon inventory optimization      |
| **IBP for S&OP**                      | Sales & Operations Planning               |
| **IBP for Response & Balancing**      | Real-time demand-supply matching          |
| **IBP for Driver-based Planning**     | Driver-based forecasting                  |

## 4. Planning Models

Cấu trúc chính:

- **Planning Areas**: top-level container (1 cho Demand, 1 cho Supply, ...).
- **Planning Levels**: hierarchy như `Product`, `Customer`, `Location`, `Week`.
- **Key Figures**: numerical measures (Sales Order Forecast, Inventory Days, ...).
- **Attributes**: master-data-like dimensions (Product ID, Customer Region, ...).
- **Time Profiles**: calendar (Day/Week/Month, từ 2024-2030).

Mỗi key figure có:
- **Calculation**: simple aggregation, copied, calculated, stored.
- **Disaggregation**: cách rã từ aggregate → detail (proportional, equal, ...).
- **Version**: current / previous / baseline / consensus.

## 5. Integration với S/4HANA

| Luồng                          | Tool                       | Ghi chú                       |
|--------------------------------|-----------------------------|--------------------------------|
| Master data sync               | SAP HCI / CPI              | Material, Customer, BOM        |
| Transactional data extract     | OData / SOAP                | Sales order, Purchase order    |
| Inventory snapshot             | OData CDS view              | Real-time                      |
| Forecast write-back             | OData / SOAP                | Plannning → S/4HANA demand    |

**Quan trọng**: IBP KHÔNG embedded trong S/4HANA — cần **CPI / BTP Integration Suite** để
sync data, hoặc accept latency (batch mode overnight).

## 6. Integration với ECC on-prem

Cũ (APO) workflow:
- ECC chạy APO add-on → nâng cấp lên IBP → retire APO.
- Tool: SAP IBP Migration Cockpit.
- Thường multi-year project.

## 7. Common Fiori apps (IBP web UI)

| Chức năng            | App                                   |
|----------------------|----------------------------------------|
| Planning Dashboard   | IBP for S&OP                          |
| Forecast accuracy    | IBP Demand - Accuracy                  |
| Supply heuristics    | IBP Supply - Run Operator              |
| Inventory analytics  | IBP for Inventory Analysis             |

## 8. Side-by-side Extension Patterns

| Pattern                        | Dùng khi                              | Tool                |
|--------------------------------|----------------------------------------|---------------------|
| Custom key figure              | Metric custom                          | Planning model API  |
| Custom disaggregation rule     | Business logic riêng                   | Custom operator     |
| Custom UI / dashboard          | Visualization riêng                    | SAP Analytics Cloud |
| External master data source    | SAP + non-SAP                          | CPI custom iFlow    |
| Excel-based planner extension  | Power user custom                      | SAP Analysis Office |

## 9. Anti-pattern

- ⚠️ Dùng IBP cho simple single-echelon forecasting — overkill.
- ⚠️ Hardcode key figure ID trong code — luôn reference qua metadata.
- ⚠️ Skip integration test giữa IBP ↔ S/4HANA trước go-live — thường fail.
- ⚠️ Dùng IBP thay SAP S/4HANA planning board cho scenario đơn giản.
- ⚠️ Plan cho version 5 năm liền không review — forecast không update thực tế.

## 10. Liên kết với các skill khác

- **Consultant**: `sap-ibp-consultant-cloud`.
- **Seed knowledge**: `sap-ibp-cloud/SKILL.md`.
- **Integration**: `sap-cpi-consultant-cloud`, `sap-sd-consultant-cloud`,
  `sap-mm-consultant-cloud`, `sap-pp-consultant-cloud`.
- **Analytics**: `sap-bw-cloud` (xem knowledge note `bw-cloud-analytics`).

## 11. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module IBP.
- [`marianfoo/sap-ai-mcp-servers`](https://github.com/marianfoo/sap-ai-mcp-servers) — IBP MCP
  (nếu có).
- SAP Help: SAP Integrated Business Planning documentation.
