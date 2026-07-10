---
name: sap-qm-cloud
description: Kien thuc QM (Quality Management — quality inspection, inspection plan, QC results, certificates, non-conformance) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong QM tren Public Cloud.
effort: medium
model: haiku
---

# QM (Quality Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| Kiem tra chat luong co ban | Scope item **BH2** / **BMW** | Cau hinh quality inspection engine, inspection type |
| Inspection plan | Scope item **BME** | Dinh nghia plan cho kiem tra: specs, method, sampling |
| Quality certificate | Scope item **BHC** | Quan ly certificate cho vat tu / san pham |
| Non-conformance / PN (Problem Notification) | Scope item **BH7** | Quy trinh xu ly khong phu hop / yeu cau khac phuc |
| Quality level / sampling | — | Cau hinh dynamic modification rule, sampling procedure |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao lenh kiem tra | Create Inspection Lot (tu dong) | QA01 / QA02 |
| Ghi ket qua kiem tra | Record Inspection Results | QE01 / QE02 |
| Quyet dinh su dung lo | Use Decision – Inspection Lot | QA32 |
| Tao inspection plan | Manage Inspection Plans | QP01 / QP02 |
| Xu ly khong phu hop | Manage Non-Conformance | QN01 / QN02 |
| Huy / dong inspection lot | Close/Cancel Inspection Lots | QA33 |
| Certificate | Manage Quality Certificates | QCC0 / QCC5 |
| Thong ke nang luc QC | Quality Control Chart | QM01 (SPC) |
| Danh gia nha cung cap | Supplier Evaluation | QM02 |
| Kiem tra hang nhap | Inspection of Incoming Goods – MRP | QA11 |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| Inspection lot | `API_INSPECTION_LOT_SRV` |
| Inspection result | `API_INSPECTION_RESULT_SRV` |
| Inspection plan | `API_INSPECTION_PLAN_SRV` |
| Quality certificate | `API_QUALITY_CERTIFICATE_SRV` |
| Non-conformance | CDS view `I_NonConformance` |
| Supplier evaluation | `API_SUPPLIER_EVALUATION_SRV` |
| Usage decision | `API_INSPECTION_USAGE_DECISION_SRV` |
| CDS views | `I_InspectionLot`, `I_QualityCertificate`, `I_NonConformance` |

## 4. Huong mo rong (extensibility) cho QM

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho QM:

- **Custom Fields and Logic** — them field vao inspection lot / inspection plan / quality certificate /
  non-conformance, hien tren Fiori app tuong ung.
- **Custom Business Objects** — khi can 1 loai certificate moi hoac 1 bang check sheet rieng.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho QM (inspection lot creation,
  result calculation formula, certificate control) truoc khi ket luan can side-by-side.
- Khi can 1 loai sampling / AQL (Acceptable Quality Level) dac thu ngoai chuan, kiem tra truoc
  trong SSCUI co san khong.

## 5. Luu y dac thu cho QM tren Public Cloud

- **Inspection lots** thuong duoc tao **tu dong** tu goods receipt (hang nhap), goods issue (hang xuat),
  hoac tu production order confirmation. Khong can tao manual Inspection Lot trong da so truong hop.
- **QM in procurement**: Khi mua hang, quality check dien ra tai goods receipt, duoc dieu khien boi
  inspection setup cho material + supplier.
- **QM in production**: Quality check dien ra tai production order operation.
- **Certificate**: Co the dung quality certificate cho inbound (supplier cert) va outbound (customer cert).
- **Non-conformance (PN)**: Tich hop voi MM (purchase order) va PP (production order) de xu ly
  khong phu hop.
- **QM chi la 1 module nho trong Public Cloud**, khong co QM menu đo sâu nhu on-premise (QST03, QMR3...).
  Fiori app coverage cho QM co the chua day du, kiem tra tren Fiori Apps Reference Library.

## 6. Khi viet/review code ABAP Cloud cho QM

- Doc du lieu inspection lot / certificate / non-conformance qua released CDS view API
  (`I_InspectionLot`, `I_QualityCertificate`, `I_NonConformance`...), khong SELECT truc tiep
  bang chuan (QALS, QAMR, QMEL, QEQL).
- QM data thuong duoc luu trong bang QALS (inspection lot) va QAMR (results). Chi doc qua API
  hoac CDS view da duoc release.
- Kiem tra non-conformance: khi can cap nhat status, dung `API_NON_CONFORMANCE_SRV` thay vi UPDATE
  truc tiep bang QMEL.

## 7. Cac scope item chinh cho QM

| Scope Item | Mo ta |
|------------|-------|
| **BH2** | Quality Management in Procurement |
| **BH7** | Non-Conformance Management |
| **BHC** | Quality Certificates |
| **BMW** | Quality Management in Production (trong REM) |
| **BD9** | Quality Management in Discrete Manufacturing |

## 8. Nguon tham khao

- [SAP Best Practices Explorer — QM Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Quality Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
