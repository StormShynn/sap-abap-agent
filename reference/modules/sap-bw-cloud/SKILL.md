---
name: sap-bw-cloud
description: Kien thuc BW (Business Warehouse / Analytics — data modeling, extraction, reporting, analytics, SAP Analytics Cloud, BW/4HANA) lien quan den SAP S/4HANA Cloud Public Edition. Dung khi user hoi ve bao cao, analytics, data warehouse, extraction S/4HANA data.
effort: medium
model: haiku
---

# BW (Analytics & Data Warehouse) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help (xem Nguon tham khao). Luu y: BW tren Cloud
thuong la **side-by-side** (BW/4HANA hoac SAP Analytics Cloud) thay vi trong S/4HANA core.]

## 1. To canh BW tren Public Cloud

SAP S/4HANA Cloud Public Edition co 3 cach lam analytics:

1. **Embedded Analytics (in-app)**: CDS view + Fiori analytical app — khong can BW. Day la chinh la
   cach mac dinh cho analytics trong S/4HANA Cloud. Dung **CDS view** + **KVF (Key Figure View)**
   + **Analytical Query**.
2. **SAP Analytics Cloud (SAC)**: Side-by-side tren BTP. Ket noi S/4HANA qua live data connection
   (CDS view) hoac import. La giai phap BI/planning chinh cho Cloud.
3. **BW/4HANA (side-by-side)**: He thong BW rieng tren BTP hoac on-prem. Cho analytics phuc tap,
   data warehouse, large data volumes.

**Embedded Analytics la mac dinh.** Chi can SAC/BW/4HANA khi vuot qua gioi han cua embedded.

## 2. Cau hinh Embedded Analytics (SSCUI)

| Khu vuc | Mo ta |
|---------|-------|
| Extend CDS view for query | Dung Custom Analytical Queries (Fiori app) |
| Enable analytical query | Kich hoat query bang annotation `@Analytics.query: true` |
| Key Figure View (KVF) | Din nghia Key Figure tu Custom Field |

## 3. Fiori app cho Analytics

| Nghiep vu | Fiori app |
|-----------|-----------|
| Phan tich tu do | Create Analytical Query (Custom Analytical Queries) |
| Bao cao nhieu chieu | Multi-Dimensional Report |
| Dashboard cau hinh | SAP Fiori Launchpad + Analytical Apps |
| Khai pha du lieu | Smart Insights (ML) |
| SAP Analytics Cloud | SAC Fiori app (neu duoc cau hinh) |
| Khai thac CDS view | View Browser |

## 4. Cach lay du lieu tu S/4HANA Cloud

| Cach | Mo ta | Gioi han |
|------|-------|----------|
| OData CDS view | Doc CDS view truc tiep qua OData | Du lieu thoi gian thuc, gioi han so dong |
| OData Analytical Query | Analytical query qua OData | Hieu qua cho aggregate data |
| SAC Live Connection | SAC doc truc tiep tu CDS view | Toi uu cho SAC |
| SDI / SLT | Replicate du lieu sang BW/4HANA | Co do tre, phuc tap |
| Extractor | Extractor cho BW (OLTP -> BW) | Chi cho BW on-prem |

## 5. Luu y dac thu cho Analytics tren Public Cloud

- **Embedded Analytics la du cho da so nhu cau.** Truoc khi de xuat BW/SAC, kiem tra xem CDS
  view + Analytical Query co dap ung duoc khong.
- **Custom Analytical Query**: Fiori app **Custom Analytical Queries** cho phep tao query tu
  CDS view da release. Key user co the tu lam.
- **SAP Analytics Cloud**: La giai phap SAP chinh cho BI, planning, predictive. Ket noi live
  vao S/4HANA CDS view.
- **BW/4HANA**: Chi can khi co data warehouse phuc tap, data từ nhieu nguon, hoac large data volumes.
- **Extraction**: S/4HANA Cloud chi cho phep extract qua OData / CDS view. Khong co extraco
  truyen thong (LBWQ, RSO...) nhu trong BW on-prem.

## 6. Khi viet/review code ABAP Cloud cho Analytics

- Analytical query xay dung tu CDS view co annotation `@Analytics.query: true`. Them `@EndUserText.label`
  de dua vao truy van duoc.
- CDS view cho analytical query can co `@AnalyticsDetails: true` va `@Consumption: true`.
- Key Figure dinh nghia bang annotation:
  ```abap
  @Semantics.amount.currencyCode: 'Currency'
  @DefaultAggregation: #SUM
  net_amount;
  ```

## 7. Nguon tham khao

- [SAP Analytics Cloud](https://www.sap.com/products/technology-platform/cloud-analytics.html)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- [SAP Help Portal — Embedded Analytics](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [BW/4HANA on BTP](https://help.sap.com/docs/BW4HANA_CLOUD)
