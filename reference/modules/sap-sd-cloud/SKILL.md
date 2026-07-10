---
name: sap-sd-cloud
description: Kien thuc SD (Sales & Distribution / order-to-cash) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong dung cho khi viet/review code ABAP Cloud lien quan sales order, pricing, delivery, billing. Dung khi user hoi ve cau hinh/tich hop/mo rong SD tren Public Cloud.
effort: medium
model: haiku
---

# SD (Order-to-Cash) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Learning (xem Nguon tham khao); so SSCUI/scope
item/Fiori app cu the thay doi theo tung release quy, luon nhac user xac minh lai truoc khi dua vao
san xuat. Dung ket hop voi skill `sap-extensibility` (bac thang extensibility chung)
va `sap-clean-code` (dat ten).]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---|---|---|
| Pricing | 101120 | Thiet lap condition type cho pricing trong sales |
| Order reason | (tu CE2202) | Gioi han/dat mac dinh ly do don hang duoc chon trong sales document |
| Item category determination | — | Gan item category linh hoat theo material type / sales org / distribution channel |
| Hieu suat order-to-cash | Scope item **BKN** | Da cai san tren Public Cloud (khac ban on-prem phai cai them) |
| App analytics cho Sales | Scope item **1BS** | Cac app phan tich: quotation, order fulfillment, customer return, back order, delivery performance |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app |
|---|---|
| Tao/sua/xem sales order | Manage Sales Orders |
| Sales order khong tinh tien | Manage Sales Orders Without Charge – Version 2 |
| Khach hang (customer master) | Manage Business Partner Master Data (Business Partner la model duy nhat) |
| Nhan thanh toan tu khach hang | Post Incoming Payments |
| Billing document so bo | Manage Preliminary Billing Documents – Services |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra ten/version chinh xac tren `api.sap.com` truoc khi dung) |
|---|---|
| CRUD sales order | `API_SALES_ORDER_SRV` (OData) |
| Sales order return | Returns order OData v4 API |
| Business Partner (khach hang) | `API_BUSINESS_PARTNER` |
| Billing | Cac OData service duoi scope Preliminary Billing Documents |

## 4. Huong mo rong (extensibility) cho SD

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho SD:
- **Custom Fields and Logic** — them field vao sales order / sales order item / delivery / billing document, hien qua Adaptation Mode tren app tuong ung.
- **Custom Business Objects** — chi dung khi can 1 doi tuong hoan toan moi (vd 1 loai thoa thuan rieng), khong dung de them field vao doi tuong co san.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho SD (pricing determination, output determination) truoc khi ket luan can side-by-side.
- Neu can 1 dang condition table/access sequence khong co san trong SSCUI, day thuong la dau hieu can side-by-side (hoac chua lam duoc) — khong tu bia ra cach cau hinh.

## 5. Khi viet/review code ABAP Cloud cho SD

- Doi tuong custom lien quan SD (CDS view, RAP BO) van theo naming convention chung o `sap-clean-code` (Z/Y namespace, `Z_I_`/`Z_C_` cho CDS...).
- Doc du lieu sales order/business partner/billing qua released CDS view API (`I_SalesOrder`, `I_BusinessPartner`...) hoac API tren, khong SELECT truc tiep bang chuan.
- Truoc khi de xuat 1 field/logic tich hop them vao sales order, xac dinh day la Custom Field (khong can dev) hay can 1 RAP BO rieng (can dev, side-by-side neu ngoai pham vi core).

## 6. Nguon tham khao

- [SAP S/4HANA Cloud: New Business Configuration (SSCUI) for Assign Sales Document Types and Sales Organizations to Order Reasons](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-s-4hana-cloud-new-business-configuration-sscui-for-assign-sales/ba-p/13511611)
- [Sales in SAP S/4HANA Cloud Public Edition 2508](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sales-in-sap-s-4hana-cloud-public-edition-2508/ba-p/14175916)
- [Describing SAP Fiori Analytical Apps for Sales (1BS) — SAP Learning](https://learning.sap.com/courses/implementing-sap-s-4hana-cloud-public-edition-sales-automation-analytics-and-configuration/describing-sap-fiori-analytical-apps-for-sales-1bs-_ab89c610-3ff1-4018-bf03-b8511c9b3b3f)
- SAP API Business Hub: `https://api.sap.com`
