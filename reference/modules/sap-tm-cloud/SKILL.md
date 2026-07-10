---
name: sap-tm-cloud
description: Kien thuc TM (Transportation Management — transportation planning, freight order, carrier selection, freight settlement, shipment tracking, transportation charges) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong TM tren Public Cloud.
effort: medium
model: haiku
---

# TM (Transportation Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help. **Luu y**: SAP S/4HANA Cloud Public Edition co the
dung **Transportation Management (TM) embedded** trong S/4HANA hoac **TM side-by-side** tren BTP.
Scope item chinh la **BPL** (Transportation Management). Kiem tra tren Best Practices Explorer
cho release hien tai.]

## 1. Cau hinh (SSCUI)

| Khu vuc | Scope item | Mo ta |
|---------|-----------|-------|
| TM co ban | Scope item **BPL** | Cau hinh Transportation Management embedded |
| Freight order | — | Dinh nghia freight order type, number range |
| Carrier | — | Cau hinh carrier (supplier) selection, rate |
| Charge calculation | — | Freight charge calculation, rate table |
| Settlement | — | Freight cost settlement voi carrier |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao van don | Create Freight Orders | /SCMTMS/TOR_CREATE |
| Lap ke hoach van chuyen | Transportation Planning Board | /SCMTMS/PLB |
| Chon don vi van chuyen | Carrier Selection | — |
| Tinh cuoc van chuyen | Calculate Freight Charge | /SCMTMS/FRT_CALC |
| Tat toan cuoc phi | Freight Settlement | — |
| Theo doi van chuyen | Monitor Transportation | /SCMTMS/MON |
| Quan ly hop dong van chuyen | Manage Freight Agreements | — |
| Quan ly gia van chuyen | Manage Freight Rates | /SCMTMS/RATE |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| Freight order | `API_FREIGHT_ORDER_SRV` |
| Freight agreement | `API_FREIGHT_AGREEMENT_SRV` |
| Freight rate | `API_FREIGHT_RATE_SRV` |
| Transportation charge | `API_TRANSPORTATION_CHARGE_SRV` |
| Freight settlement | `API_FREIGHT_SETTLEMENT_SRV` |
| CDS views | `I_FreightOrder`, `I_FreightAgreement`, `I_TransportationCharge` |

## 4. Huong mo rong (extensibility)

- **Custom Fields and Logic** — them field vao freight order / freight agreement / rate table.
- Neu can heuristic tuyen duong dac thu, thuong can side-by-side BTP.

## 5. Luu y dac thu cho TM tren Public Cloud

- **Embedded TM**: Co san trong S/4HANA Cloud Public Edition (scope BPL). Khong can BTP.
- **TM side-by-side**: Neu can TM phuc tap (fleet management, yard logistics), co the can
  TM tren BTP (SAP Transportation Management).
- **Integration**: TM lien ket voi SD (delivery), MM (purchase order), FI (freight cost GL).
- **Freight settlement**: Tat toan cuoc phi cho carrier. Carrier la supplier (MM).

## 6. Khi viet/review code ABAP Cloud cho TM

- Doc du lieu freight order / charge qua released API (`API_FREIGHT_ORDER_SRV`...).
- Khong SELECT truc tiep bang chuan TM (/SCMTMS/TOR, /SCMTMS/FRT...).

## 7. Nguon tham khao

- SAP API Business Hub: `https://api.sap.com`
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- [SAP Help Portal — TM](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
