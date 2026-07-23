---
name: sap-mm-cloud
description: Kien thuc MM (Materials Management — procurement, inventory, material master, valuation, physical inventory) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong dung cho khi viet/review code ABAP Cloud lien quan mua hang va quan ly kho. Dung khi user hoi ve cau hinh/tich hop/mo rong MM tren Public Cloud.
effort: medium
model: haiku
---

# MM (Materials Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help (xem Nguon tham khao); so SSCUI/scope item/Fiori app
cu the thay doi theo tung release quy, luon nhac user xac minh lai. Dung ket hop voi skill
`sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| To chuc mua hang (Purchasing org, plant) | (trong Central Business Configuration) | Setup cau truc to chuc cho procurement |
| Kiem tra gia mua (pricing) | 101120 | Thiet lap condition type cho purchasing |
| Khoa vat tu tu dong / manual | — | Cau hinh khoa vat tu cho tung plant |
| Kiem ke vat tu (Physical Inventory) | Scope item **BML** | Quy trinh kiem ke dinh ky / thuang xuyen |
| Gia vat tu (Material Valuation) | Scope item **BJN** | Phan gia vat tu: standard price / moving average price |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao/sua don mua hang | Manage Purchase Orders | ME21N / ME22N |
| Tao/sua yeu cau mua hang | Manage Purchase Requisitions | ME51N / ME52N |
| Nhap hang / xuat kho | Post Goods Movement | MIGO |
| Kiem ke vat tu | Physical Inventory Documents | MI01 / MI02 / MI04 |
| Vat tu ton kho | Manage Stock | MMBE |
| Danh muc vat tu (Material Master) | Manage Material Master Data | MM01 / MM02 |
| Danh sach don mua hang | Display Purchase Orders - List | ME2L / ME2M / ME2N |
| Hoa don mua hang | Manage Supplier Invoices | MIRO |
| Hop dong mua hang | Manage Purchasing Contracts | ME31K |
| Thoa thuan gia | Manage Purchasing Info Records | ME11 / ME12 |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra ten/version chinh xac tren `api.sap.com` truoc khi dung) |
|---------|-------------------------------------------------------------------------------|
| CRUD purchase order | `API_PURCHASEORDER_PROCESS_SRV` (OData V2) |
| CRUD purchase requisition | `API_PURCHASEREQ_PROCESS_SRV` |
| Supplier invoice | `API_SUPPLIERINVOICE_PROCESS_SRV` |
| Material document (goods movement) | `API_MATERIAL_DOCUMENT_SRV` |
| Material master | `API_MATERIAL_SRV` |
| Business Partner (supplier) | `API_BUSINESS_PARTNER` |
| Supplier quotation | `API_SUPPLIERQUOTATION_PROCESS_SRV` |

## 4. Huong mo rong (extensibility) cho MM

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho MM:

- **Custom Fields and Logic** — them field vao purchase order / purchase requisition / supplier invoice /
  material master, hien qua Adaptation Mode tren Fiori app tuong ung.
- **Custom Business Objects** — dung khi can 1 doi tuong hoan toan moi (vd 1 bang thoa thuan mua hang
  dac thu), khong dung de them field vao doi tuong co san.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho MM (pricing determination trong
  purchasing, output determination, approval workflow) truoc khi ket luan can side-by-side.
- Khi can 1 loai condition table/access sequence khong co san trong SSCUI, day thuong la dau hieu
  can side-by-side (hoac chua lam duoc) — khong tu bia ra cach cau hinh.

## 5. Khi viet/review code ABAP Cloud cho MM

- Doi tuong custom lien quan MM van theo naming convention chung o `sap-clean-code` (Z/Y namespace).
- Doc du lieu purchase order/purchase requisition/supplier invoice/material document qua released CDS
  view API (`I_PurchaseOrder`, `I_MaterialDocument`, `I_SupplierInvoice`...) hoac API tren, khong
  SELECT truc tiep bang chuan (EKKO, EKPO, MSEG, MKPF...).
- Truoc khi de xuat 1 field/logic tich hop them vao purchase order, xac dinh day la Custom Field
  (khong can dev) hay can 1 RAP BO rieng (can dev, side-by-side neu ngoai pham vi core).

## 6. Cac scope item chinh cho MM

| Scope Item | Mo ta |
|------------|-------|
| **BML** | Physical Inventory (Kiem ke vat tu) |
| **BJN** | Product Cost Planning (Gia vat tu) |
| **BNS** | Operational Procurement (Mua hang tac nghiep) |
| **J45** | Sourcing & Contract Management |
| **1NC** | Invoice Management (Hoa don mua hang) |

## 7. Nguon tham khao

- [SAP S/4HANA Cloud Public Edition — Procurement Overview](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-s-4hana-cloud-public-edition-procurement-overview/ba-p/13720411)
- [SAP Best Practices Explorer — MM Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Materials Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
