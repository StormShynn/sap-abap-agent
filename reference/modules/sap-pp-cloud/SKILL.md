---
name: sap-pp-cloud
description: Kien thuc PP (Production Planning & Manufacturing — production order, BOM, routing, MRP, capacity, production execution) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong PP tren Public Cloud.
effort: medium
model: haiku
---

# PP (Production Planning & Manufacturing) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| Production order type | Scope item **BD9** / **BH1** | Dinh nghia order type cho san xuat (manufacturing) |
| MRP (Material Requirements Planning) | Scope item **BMA** | Cau hinh MRP: MRP type, lot sizing, procurement type |
| BOM (Bill of Materials) | — | Quan ly BOM, alternative BOM, BOM usage |
| Routing / Bill of Process | Scope item **BME** | Routing cho san xuat, work center, task list |
| Capacity planning | Scope item **BMD** | Danh gia va can bang nang luc san xuat |
| Repetitive manufacturing | Scope item **BMW** | San xuat hang loat (repetitive / REM) |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao/sua lenh san xuat | Manage Production Orders | CO01 / CO02 |
| Huy lenh san xuat | Close/Cancel Production Orders | CO04 |
| Giai phong lenh san xuat | Release Production Orders | CO05 |
| Xac nhan san xuat | Post Confirmations – Production Orders | CO11N |
| Hien thi lenh san xuat | Display Production Orders – List | CO03 |
| MRP live | Schedule MRP Runs / Monitor Material Coverage | MD01 / MD04 |
| BOM | Manage Bill of Materials | CS01 / CS02 |
| Routing | Manage Routings | CA01 / CA02 |
| Work center | Manage Work Centers | CR01 / CR02 |
| Capacity | Monitor Capacity Evaluation | CM01 / CM02 |
| Nhap/xuat kho cho san xuat | Post Goods Movement – Production | MIGO + production |
| Kiem tra san xuat | Production Order Confirmation List | CO15 |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| CRUD production order | `API_PRODUCTION_ORDER_SRV` (OData) |
| Production order confirmation | `API_PRODORDERCONFIRMATION_SRV` |
| BOM | `API_MATERIAL_BOM_SRV` |
| Routing / Bill of Process | `API_ROUTING_SRV` / `API_BILLOFPROCESS_SRV` |
| Work center | CDS view `I_WorkCenter`, `I_WorkCenterCapacity` |
| MRP | `API_MRP_PLANNINDEPREQ_SRV` (planned independent req.) |
| Material coverage | CDS view `I_MaterialCoverage` |
| Production order CDS views | `I_ProductionOrder`, `I_ProductionOrderComponent`, `I_ProductionOrderOperation` |

## 4. Huong mo rong (extensibility) cho PP

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho PP:

- **Custom Fields and Logic** — them field vao production order / production order component /
  BOM item / routing operation, hien tren Fiori app tuong ung.
- **Custom Business Objects** — khi can 1 doi tuong moi (vd 1 bang tinh toan san xuat rieng),
  khong dung de them field vao doi tuong co san.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho PP (production order
  status change, BOM explosion, MRP formula) truoc khi ket luan can side-by-side.
- Khi can MRP heuristic / planning strategy dac thu ngoai scope item BMA, day thuong la dau hieu
  can side-by-side BTP.

## 5. Luu y dac thu cho PP tren Public Cloud

- **Repetitive Manufacturing (REM)** va **Discrete Manufacturing** la 2 phuong thuc san xuat chinh.
  Discrete: Production Orders (scope BD9). REM: scope BMW.
- **MRP Live** la MRP chinh tren Public Cloud — MRP truyen thong (classic MRP) khong duoc dung.
- **PP/DS (Advanced Planning)** khong co trong Public Cloud mac dinh — can BTP + SAP IBP neu can
  advanced planning / heuristics phuc tap.
- **Kanban** duoc ho tro qua scope item **BMF** (Kanban Manufacturing).
- **Lean Manufacturing** / **JIT** — dung scope item tuong ung tren Best Practices Explorer.

## 6. Khi viet/review code ABAP Cloud cho PP

- Doc du lieu production order / BOM / routing qua released CDS view API (`I_ProductionOrder`,
  `I_MaterialBOM`, `I_Routing`...), khong SELECT truc tiep bang chuan (AFKO, AFPO, MAST, STPO, CRHD, PLKO).
- Khi can thong tin nguyen vat lieu cho lenh san xuat, dung `I_ProductionOrderComponent`.
- Khi can tinh toan san xuat (backflush, component consumption), dung released API thay vi
  UPDATE truc tiep bang RESB.

## 7. Cac scope item chinh cho PP

| Scope Item | Mo ta |
|------------|-------|
| **BD9** | Discrete Manufacturing – Production Orders |
| **BH1** | Process Manufacturing |
| **BMA** | Material Requirements Planning (MRP) |
| **BMD** | Capacity Evaluation |
| **BME** | Routing / Master Recipe |
| **BMF** | Kanban Manufacturing |
| **BMW** | Repetitive Manufacturing (REM) |
| **1Y2** | Manufacturing Analytics |

## 8. Nguon tham khao

- [SAP S/4HANA Cloud Public Edition — Manufacturing Overview](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-s-4hana-cloud-public-edition-manufacturing-overview/ba-p/13720412)
- [SAP Best Practices Explorer — PP Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Production Planning](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
