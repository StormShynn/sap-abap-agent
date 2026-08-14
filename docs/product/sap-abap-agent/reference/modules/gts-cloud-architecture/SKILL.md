---
name: gts-cloud-architecture
description: Knowledge note tổng hợp **kiến trúc GTS trên Cloud** (GTS on-prem vs SAP Global Trade Services trên BTP vs GTS embedded trong S/4HANA Cloud), integration patterns với MM/SD/FICO/EHS. Khác với `sap-gts-cloud/SKILL.md` (seed knowledge GTS). Dùng khi cần quyết định kiến trúc trade compliance.
effort: low
model: haiku
---

# GTS — Cloud Architecture Knowledge Note

Module con của plugin, tập trung vào **kiến trúc GTS trên Cloud** và pattern tích hợp với
S/4HANA. Không thay thế:
- `sap-gts-cloud/SKILL.md` — seed knowledge GTS consultant.
- `sap-gts-consultant-cloud` — agent consult thật.

## 1. Tổng quan: GTS trên Cloud có mấy variant?

| Variant                                  | Status                  | Use case                        |
|------------------------------------------|-------------------------|----------------------------------|
| **SAP GTS on-prem** (legacy)              | Maintenance mode        | Đã có sẵn, chưa migrate          |
| **SAP Global Trade Services trên BTP**    | Active                  | Side-by-side cho S/4HANA Cloud    |
| **GTS embedded trong S/4HANA Cloud Public Edition** | Limited     | Chỉ 1 số chức năng cơ bản       |

**Lưu ý quan trọng**: S/4HANA Cloud Public Edition **không có full GTS embedded**. Để có đầy
đủ Customs Management, SPL, Preference Processing, cần dùng **GTS trên BTP** (side-by-side).

## 2. GTS trên BTP — Architecture

```
┌──────────────────────────────────────────────┐
│ S/4HANA Cloud (Public Edition)              │
│ - Master data (Customer, Vendor, Material)  │
│ - Sales order / Purchase order              │
│ - MM/SD/FICO posting                        │
└──────────────────────────────────────────────┘
                ↕ (Integration Suite / OData / iDoc)
┌──────────────────────────────────────────────┐
│ SAP Global Trade Services trên BTP          │
│ - Customs declarations                      │
│ - Sanctioned Party List (SPL) screening     │
│ - Preference / FTA certificate              │
│ - Intrastat / Extrastat reporting           │
└──────────────────────────────────────────────┘
```

## 3. Decision Matrix: chọn variant nào?

| Tiêu chí                          | GTS on-prem | GTS trên BTP | Embedded S/4HANA Cloud |
|------------------------------------|-------------|---------------|-------------------------|
| Full SPL screening                | ✅           | ✅             | ❌                       |
| Customs declarations              | ✅           | ✅             | ❌                       |
| Preference processing             | ✅           | ✅             | Partial                 |
| Multi-country support             | ✅           | ✅             | Limited                 |
| Multi-tenant SaaS                 | ❌           | ✅             | N/A                     |
| CapEx / OpEx                      | CapEx        | OpEx          | Subscription            |
| Implementation effort              | Đã có sẵn   | Medium         | Low (limited scope)     |

**Khuyến nghị**: nếu đã có GTS on-prem → migrate lên **GTS trên BTP** theo SAP standard migration
path. Nếu dự án mới, chọn **GTS trên BTP** từ đầu.

## 4. Integration với MM (Procurement)

| Luồng                          | Vai trò MM              | Vai trò GTS                      |
|--------------------------------|--------------------------|----------------------------------|
| Vendor master                  | MM tạo vendor            | GTS check SPL lúc vendor create  |
| Purchase order                 | MM tạo PO                | GTS check embargo + license      |
| Goods receipt                  | MM post GR               | GTS trigger customs declaration  |
| Import declaration             | MM gửi GR data           | GTS file to khai hải quan        |

## 5. Integration với SD (Sales)

| Luồng                          | Vai trò SD              | Vai trò GTS                       |
|--------------------------------|-------------------------|-----------------------------------|
| Customer master                | SD tạo customer         | GTS check SPL lúc customer create |
| Sales order                    | SD tạo SO               | GTS check embargo + export license |
| Outbound delivery              | SD tạo delivery         | GTS check export compliance       |
| Billing                        | SD post billing         | GTS trigger preference calc       |

## 6. Integration với FICO

- **Tax declaration**: GTS gửi data tax → FI tạo tax posting.
- **Customs duty payment**: FI tạo vendor invoice cho customs → pay to authority.
- **Intrastat**: GTS generate Intrastat report → FI submit statistical declaration.

## 7. Integration với EHS

- **Dangerous goods**: EHS master data (UN number, hazard class) → GTS check shipment compliance.
- **Safety data sheet**: link SDS cho mỗi material → GTS check declaration required.

## 8. Common GTS Configuration (qua Fiori)

| Chức năng                  | Fiori app                              |
|----------------------------|----------------------------------------|
| SPL check                  | Sanctioned Party List Screening         |
| Customs declaration        | Manage Customs Declarations             |
| Preference                 | Manage Preference Documents             |
| License management         | Manage Export/Import Licenses           |
| Intrastat                  | Intrastat Declarations                  |
| Trade compliance dashboard | Global Trade Compliance Monitor         |

## 9. Side-by-side Extension Patterns

| Pattern                    | Dùng khi                              | Tool                |
|----------------------------|----------------------------------------|---------------------|
| Custom compliance check    | Rule riêng cho ngành (vd pharma, defense) | RAP + Cloud BAdI   |
| SPL enhancement            | List từ internal blacklist             | Custom table + RAP  |
| Custom reporting           | Compliance dashboard riêng              | SAP Analytics Cloud |
| Workflow approval          | Compliance approval custom             | SAP Build           |

## 10. Anti-pattern

- ⚠️ Cố gắng gọi GTS transaction từ code custom — không released, dùng API.
- ⚠️ Hardcode SPL list local — luôn dùng GTS central service.
- ⚠️ Skip SPL check cho "vendor nội địa" — vẫn cần check (risk re-export).
- ⚠️ Coi GTS embedded là full GTS — chỉ có 1 phần nhỏ.

## 11. Liên kết với các skill khác

- **Consultant**: `sap-gts-consultant-cloud`.
- **Seed knowledge**: `sap-gts-cloud/SKILL.md`.
- **Integration**: `sap-mm-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud`,
  `sap-ehs-consultant-cloud`.
- **BTP architecture**: `sap-btp-connectivity` (đọc từ knowledge note này).
- **Released class**: `sap-released-classes` (xem mục GTS integration nếu có).

## 12. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module GTS.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)
  — pattern consume OData từ GTS.
- SAP Help: SAP Global Trade Services on BTP, S/4HANA Cloud GTS integration.
- SAP Discovery Center: GTS service listing.
