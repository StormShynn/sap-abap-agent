---
name: tm-cloud-integration
description: Knowledge note tổng hợp **TM (Transportation Management)** trên Cloud — kiến trúc, integration với SD/EWM/IBP, B2B/B2C scenarios. Khác với `sap-tm-cloud/SKILL.md` (seed consultant TM) và `sap-tm-consultant-cloud`.
effort: low
model: haiku
---

# TM — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **kiến trúc SAP TM (Transportation Management)** trên
S/4HANA Cloud và side-by-side scenarios. Không thay thế:
- `sap-tm-cloud/SKILL.md` — seed knowledge TM consultant.
- `sap-tm-consultant-cloud` — agent consult thật.

## 1. TM trên Cloud có mấy variant?

| Variant                                    | Status                   | Use case                         |
|--------------------------------------------|--------------------------|----------------------------------|
| **SAP TM embedded trong S/4HANA Cloud Public Edition** | Limited       | Chỉ 1 số chức năng basic        |
| **SAP TM on S/4HANA Private Cloud**         | Active                   | Full TM                          |
| **SAP TM 9.x on-prem (legacy)**             | Maintenance              | Đã có sẵn, multi-country         |

**Quan trọng**: Public Cloud S/4HANA **không có full TM embedded**. Với B2C, multi-carrier,
hoặc compliance nghiêm ngặt, cần dùng **Private Cloud** hoặc side-by-side extension qua
**SAP Business Network for Logistics** (carrier integration).

## 2. Kiến trúc TM embedded (Private Cloud)

```
┌────────────────────────────────────────────────────┐
│ S/4HANA (Private Cloud)                           │
│ - SD (Sales Order)                                 │
│ - MM (Purchase Order)                              │
│ - EWM (Warehouse)                                  │
│ - TM (Transportation Management)                   │
│   ├─ Freight Order / Freight Booking              │
│   ├─ Carrier selection / Tendering                 │
│   ├─ Routing / Tendering / Settlement              │
│   └─ Cost allocation                               │
└────────────────────────────────────────────────────┘
```

## 3. Quy trình TM chính

### B2B (Inbound/Outbound planning)

```
Sales Order (SD)
  └─ Outbound Delivery
       └─ Freight Unit (TM) - grouping deliveries
            └─ Freight Request → Tender → Carrier
                 └─ Freight Order (executable)
                      └─ Execution (Pickup / In-transit / Delivery)
                           └─ Settlement (carrier invoice reconciliation)
```

### B2C (Parcel)

```
eCommerce Order
  └─ Outbound Delivery
       └─ Parcel (1 delivery = 1 parcel for B2C)
            └─ Carrier API integration (DHL, FedEx, UPS)
                 └─ Tracking events back to customer
```

## 4. Integration với SD

- **Outbound Delivery** (SD) → **Freight Unit** (TM) automatic.
- TM tạo **Freight Order**, chọn carrier, tính cost.
- Carrier execution xong → TM update delivery status (back to SD).
- Settlement cuối: TM reconcile carrier invoice.

## 5. Integration với MM (Inbound)

- **Inbound Delivery** (MM) → **Freight Unit** (TM).
- TM plan inbound transportation.
- GR cuối cùng trigger settlement.

## 6. Integration với EWM (xem `wm-ewm-integration`)

- EWM outbound delivery → TM freight unit (yard + transportation).
- Warehouse task complete → update TM in-transit status.

## 7. Integration với IBP (xem `ibp-cloud-integration`)

- IBP supply planning có thể dùng TM transportation cost để optimize supply allocation.
- IBP inventory target → TM transportation planning.

## 8. Carrier Integration

| Phương thức                 | Khi nào dùng                              |
|------------------------------|--------------------------------------------|
| **SAP Business Network for Logistics** | B2C / multi-carrier / parcel carrier |
| **Direct API integration**   | B2B / few carriers / EDI 856/214         |
| **SAP TM Tender integration** | RFP / competitive tendering              |
| **3PL providers**            | Multi-3PL warehousing + transport          |

## 9. Cost & Settlement

- **Freight Cost**: planned cost (TM tính).
- **Carrier Invoice**: actual cost từ carrier.
- **Settlement**: reconcile actual vs planned → variance report.
- **Cost allocation**: distribute freight cost theo delivery line, sales order, profit center.

## 10. Common Fiori apps (TM)

| Chức năng                  | Fiori app                                |
|----------------------------|------------------------------------------|
| Freight Order              | Manage Freight Orders                    |
| Tender                     | Manage Freight Tenders                   |
| Carrier selection          | Carrier Selection Worklist               |
| Settlement                 | Freight Settlement Worklist              |
| Cost analysis              | Transportation Cost Analysis             |
| Tracking                   | Track Shipments                          |

## 11. Side-by-side Extension Patterns

| Pattern                        | Dùng khi                              | Tool                |
|--------------------------------|----------------------------------------|---------------------|
| Custom carrier integration     | Local carrier không có sẵn             | BTP + CPI           |
| Custom cost rule               | Business logic riêng                   | Cloud BAdI          |
| Custom approval workflow       | Multi-level approval                   | SAP Build           |
| Track & trace dashboard        | Customer-facing tracking                | SAP Build / SAC     |
| Last-mile delivery              | Crowdsourced delivery                  | SAP Business Network|

## 12. Anti-pattern

- ⚠️ Dùng TM Public Cloud cho B2C multi-carrier — không đủ capability.
- ⚠️ Hardcode carrier ID — luôn dùng carrier master.
- ⚠️ Skip tendering — direct booking khiến mất negotiate power.
- ⚠️ Không reconcile carrier invoice với TM — chi phí ẩn lớn.
- ⚠️ Plan transportation 1 lần cuối ngày — không real-time.

## 13. Liên kết với các skill khác

- **Consultant**: `sap-tm-consultant-cloud`.
- **Seed knowledge**: `sap-tm-cloud/SKILL.md`.
- **Integration**: `sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`, `sap-ewm-consultant-cloud`,
  `sap-ibp-consultant-cloud`, `sap-cpi-consultant-cloud`.
- **Knowledge notes liên quan**: `wm-ewm-integration`, `ibp-cloud-integration`.

## 14. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module TM.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)
  — pattern carrier integration qua OData.
- SAP Help: SAP Transportation Management documentation.
- SAP Business Network for Logistics.
