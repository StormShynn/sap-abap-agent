---
name: sap-ariba-cloud
description: Kien thuc SAP Ariba / SAP Business Network — procurement collaboration, supplier management, sourcing, contract management, procurement analytics. Tich hop voi SAP S/4HANA Cloud Public Edition. Dung khi user hoi ve mua hang qua Ariba, supplier collaboration, sourcing.
effort: medium
model: haiku
---

# SAP Ariba (Procurement Collaboration) — tich hop voi S/4HANA Cloud

[Seed set — kiem chung qua SAP Community/Help. **Luu quan trong**: Ariba la **he thong rieng**
(SAP Business Network / Ariba Solutions) tren cloud, KHONG phai module trong S/4HANA core.
Tich hop voi S/4HANA qua integration (OData API, CPI).]

## 1. Ariba la gi?

Ariba la bo giai phap procurement cloud cua SAP, gom:

| Giai phap | Mo ta |
|-----------|-------|
| **SAP Ariba Procurement** | Mua hang: requisitioning, ordering, invoicing (Buyer Side) |
| **SAP Ariba Sourcing** | Dau thau, sourcing events, supplier negotiation |
| **SAP Ariba Contracts** | Quan ly hop dong mua hang |
| **SAP Ariba Supplier Lifecycle & Performance** | Quan ly vong doi nha cung cap |
| **SAP Business Network** | Ket noi nha cung cap tren mang luoi Ariba |
| **Ariba Discovery** | Tim nha cung cap moi |

**Ariba KHONG phai module trong S/4HANA**. No la 1 bo san pham rieng, chay tren BTP / Ariba Cloud.

## 2. Tich hop Ariba voi S/4HANA Cloud

| Tich hop | Cach thuc | Ghi chu |
|----------|-----------|---------|
| Master data (material, supplier) | A2X / OData tu S/4HANA → Ariba | Supplier, material, org data |
| Purchase requisition | S/4HANA → Ariba (CPI) | Requisition gui sang Ariba de xu ly |
| Purchase order | S/4HANA → Ariba (CPI) | PO gui sang Ariba Network |
| PO confirmation | Ariba → S/4HANA | Supplier xac nhan PO |
| Invoice | Ariba → S/4HANA | Invoice tu Ariba vao S/4HANA (Supplier Invoice API) |
| Catalog | Ariba → S/4HANA | Product catalog tu Ariba vao S/4HANA |
| SAP Integration Suite (CPI) | Middleware | Cau hinh CPI flows giua S/4HANA va Ariba |

## 3. Cac trang thai cua Ariba

**Ariba co 2 "phien ban" chinh**:

1. **SAP Ariba Procurement (buyer side)**: Day la giao dien cho nguoi mua hang trong doanh nghiep
   dung de:
   - Tao requisition
   - Tao purchase order (sau khi phe duyet)
   - Quan ly hop dong, sourcing
   - Supplier management

2. **SAP Business Network / Ariba Network (supplier side)**: Day la mang luoi noi voi nha cung cap,
   cho phep:
   - Supplier nhan PO tu doanh nghiep
   - Supplier xac nhan PO
   - Supplier gui invoice dien tu
   - Supplier gui catalog

**Khi user hoi ve Ariba, can phan biet ro ho muon noi ve buyer side hay supplier side.**

## 4. Luu y dac thu cho Ariba

- **Ariba la he thong rieng**: Cau hinh Ariba KHONG qua SSCUI / Manage Your Solution. Cau hinh
  qua Ariba Admin Console.
- **Integration**: Tich hop Ariba-S/4HANA thuong qua **CPI (Cloud Platform Integration)**.
  Can cau hinh CPI flows cho master data, PO, invoice.
- **Khong co ABAP code**: Ariba la Java-based. Khong co ABAP trong Ariba.
- **Supplier master**: Supplier master trong S/4HANA (Business Partner) va Ariba can duoc dong bo.
- **Catalog**: Product catalog thuong duoc quan ly trong Ariba, khong phai S/4HANA.
- **Phe duyet**: Workflow phe duyet co the chay trong Ariba hoac S/4HANA tuy cau hinh.

## 5. Khi user hoi ve Ariba

- **Neu cau hoi ve cau hinh Ariba**: Khong the tra loi qua kien thuc S/4HANA. Huong dan user
  dung Ariba Admin Console hoac SAP Help cho Ariba.
- **Neu cau hoi ve tich hop**: Mo ta luong integration qua CPI, can dispatch MM consultant
  (purchase process), FI consultant (invoice/GL).
- **Neu cau hoi ve supplier management**: Dispatch MM consultant cho supplier master.

## 6. Nguon tham khao

- [SAP Ariba — Procurement](https://www.ariba.com/)
- [SAP Business Network](https://www.sap.com/products/supply-chain/business-network.html)
- [SAP Ariba Integration with S/4HANA Cloud](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SAP Integration Suite (CPI)](https://www.sap.com/products/technology-platform/integration-suite.html)
