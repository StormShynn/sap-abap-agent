---
name: bw-cloud-analytics
description: Knowledge note tổng hợp **BW (Business Warehouse) + Datasphere + SAC** — kiến trúc analytics trên Cloud, integration với S/4HANA. Khác với `sap-bw-cloud/SKILL.md` (seed consultant BW) và các skill Datasphere/SAC riêng.
effort: low
model: haiku
---

# BW + Datasphere + SAC — Cloud Analytics Knowledge Note

Module con của plugin, tập trung vào **kiến trúc analytics trên Cloud** (BW/4HANA on-prem vs
SAP Datasphere vs SAP Analytics Cloud). Không thay thế:
- `sap-bw-cloud/SKILL.md` — seed knowledge BW consultant.
- `sap-bw-consultant-cloud` — agent consult thật.

## 1. Tổng quan: Analytics trên Cloud có mấy variant?

| Variant                                | Status                   | Use case                          |
|----------------------------------------|--------------------------|-----------------------------------|
| **SAP BW/4HANA on-prem / Private Cloud** | Còn dùng                | Đã có BW, multi-source integration |
| **SAP Datasphere** (formerly SAP Data Warehouse Cloud) | Active (cloud)  | New cloud DWH, federation        |
| **SAP Analytics Cloud (SAC)**          | Active (cloud)           | Planning + BI + augmented analytics |
| **Embedded BW trong S/4HANA Cloud**    | Limited                  | CDS-based, operational analytics  |

**Xu hướng**: SAP đang chuyển khuyến nghị từ BW/4HANA sang **SAP Datasphere** (DWH cloud) +
**SAC** (BI/planning). BW vẫn được support nhưng không có investment lớn cho cloud-native.

## 2. Kiến trúc Analytics Cloud-native

```
┌────────────────────────────────────────────────┐
│ SAP Analytics Cloud (SAC)                     │
│ - Stories (dashboard)                         │
│ - Planning models                             │
│ - Augmented Analytics (smart insights)        │
│ - SAP BusinessObjects migration path          │
└────────────────────────────────────────────────┘
                    ↕ (live connection / import)
┌────────────────────────────────────────────────┐
│ SAP Datasphere                                │
│ - Spaces (tenant container)                   │
│ - Data Builder (CDS-like modeling)            │
│ - Business Builder (semantic layer)           │
│ - Data Flow (replication / transformation)   │
└────────────────────────────────────────────────┘
                    ↕ (federation / replication)
┌────────────────────────────────────────────────┐
│ Data Sources                                  │
│ - S/4HANA Cloud (qua CDS view / OData)       │
│ - SuccessFactors                              │
│ - Concur                                      │
│ - Ariba                                       │
│ - External DB (BigQuery, Snowflake, ...)      │
└────────────────────────────────────────────────┘
```

## 3. So sánh chi tiết

| Tiêu chí                | BW/4HANA on-prem        | SAP Datasphere              | SAC Embedded BW (S/4)   |
|--------------------------|--------------------------|------------------------------|---------------------------|
| Runtime                  | on-prem / Private Cloud | BTP (multi-cloud)           | S/4HANA embedded          |
| Data modeling            | InfoObject / ADSO        | CDS-like (semantic)          | CDS view                  |
| Data volume              | TB-PB                    | TB-PB (with HANA Cloud)      | Limited (operational)     |
| Federation               | Qua ODP / SLT             | Native federation             | Native CDS                |
| Planning                 | BW-IP (deprecated)        | Native SAC Planning          | ❌                        |
| Augmented analytics      | ❌                        | ✅ (qua SAC)                  | ❌                        |
| Investment direction     | Maintenance                | Active development           | Active development        |

## 4. Khi nào dùng cái nào?

| Use case                                            | Khuyến nghị                                |
|-----------------------------------------------------|--------------------------------------------|
| Đã có BW/4HANA on-prem, muốn migrate lên cloud      | SAP Datasphere + SAC (migration tool)      |
| New DWH cho công ty cloud-native                    | SAP Datasphere + SAC                       |
| Operational analytics ngay trên S/4HANA              | Embedded BW + CDS view + Fiori analytic    |
| Planning / Forecast chuyên sâu                      | SAC Planning                               |
| Self-service BI cho business user                   | SAC Stories                                |
| Data federation giữa nhiều source                   | Datasphere (federation native)             |

## 5. Integration với S/4HANA Cloud

| Luồng                           | Tool                | Ghi chú                          |
|---------------------------------|---------------------|----------------------------------|
| Extract CDS view từ S/4HANA    | CDS view + OData V4 | Operational analytics             |
| Replicate master data            | Datasphere Data Flow| Material / Customer / Vendor      |
| Replicate transactional          | Datasphere Replication| Sales order / Purchase order    |
| Real-time query                  | Datasphere Federation| Cross-source query               |
| Embedded analytics               | Fiori Apps trên CDS | Lightweight, real-time            |

## 6. Common Fiori apps (S/4HANA Embedded Analytics)

| App                                              | Mục đích                          |
|--------------------------------------------------|------------------------------------|
| Overview Page (Fiori Elements)                    | Multi-card dashboard               |
| Analytical List Page                              | Báo cáo với chart                  |
| KPI Tiles                                         | Real-time KPI                       |
| Custom Analytical Query (CDS + OData)            | Query-based dashboard              |

## 7. Side-by-side Extension Patterns

| Pattern                    | Dùng khi                              | Tool                |
|----------------------------|----------------------------------------|---------------------|
| Custom CDS analytical query| Dashboard trên Fiori                  | CDS + Annotation     |
| Custom SAC story           | BI custom                             | SAC                  |
| Custom planning model      | Forecast riêng                         | SAC Planning         |
| Embedded ML                | Predictive analytics                  | SAP AI Core + SAC    |
| Data federation            | Cross-DWH query                       | Datasphere           |

## 8. Anti-pattern

- ⚠️ Dùng BW IP (Integrated Planning) on-prem cho cloud project — chuyển sang SAC Planning.
- ⚠️ Replicate toàn bộ S/4HANA database lên Datasphere — dùng federation cho real-time.
- ⚠️ Hardcode query trong SAC story — dùng data model trong Datasphere.
- ⚠️ Dùng SAP BusinessObjects mới cho dự án cloud — SAP đã recommend SAC thay thế.
- ⚠️ Lưu PII / personal data trong Datasphere layer mà không có governance — GDPR risk.

## 9. Liên kết với các skill khác

- **Consultant**: `sap-bw-consultant-cloud`.
- **Seed knowledge**: `sap-bw-cloud/SKILL.md`.
- **Integration**: `sap-cpi-consultant-cloud` (dùng cho ETL phức tạp), `sap-successfactors-consultant-cloud`,
  `sap-ariba-consultant-cloud`.
- **AI/ML**: `sap-btp-admin-consultant-cloud` (cho SAP AI Core).
- **BTP architecture**: `sap-btp-connectivity`.

## 10. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module BW / Datasphere.
- [`marianfoo/sap-ai-mcp-servers`](https://github.com/marianfoo/sap-ai-mcp-servers) — analytics
  MCP (nếu có).
- SAP Help: SAP Datasphere documentation, SAC Learning.
- SAP Discovery Center: Datasphere service catalog.
