---
name: sap-co-cloud
description: Kien thuc CO (Controlling — cost center, internal order, product costing, CO-PA / profitability analysis) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong dung cho khi viet/review code ABAP Cloud lien quan ke toan quan tri. Dung khi user hoi ve cau hinh/tich hop/mo rong CO tren Public Cloud.
effort: medium
model: haiku
---

# CO (Controlling) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help (xem Nguon tham khao); so SSCUI/scope item/Fiori app
cu the thay doi theo tung release quy, luon nhac user xac minh lai. Dung ket hop voi skill
`sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| Cost center co ban | Scope item **J54** | Cau hinh cost center accounting, phan bo chi phi |
| Product costing | Scope item **BJN** | Tinh gia thanh san xuat (standard cost est.) |
| Actual costing / Material Ledger | Scope item **33Q** | Gia thuc te (actual costing), Material Ledger |
| Profitability Analysis | Scope item **0KQ** | Phan tich loi nhuan tich hop tu Universal Journal |
| Phan bo chi phi | (SSCUI tuong ung) | Distribution / assessment cycles |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Ghi chu |
|-----------|-----------|---------|
| Quan ly cost center | Manage Cost Centers | Tao/sua/hien thi cost center master |
| Quan ly profit center | Manage Profit Centers | Tao/sua profit center |
| Tinh gia thanh san xuat | Product Cost Planning – Material Cost Estimate | Tinh standard cost |
| So sanh ke hoach / thuc te | Plan/Actual Report – Cost Centers | Phan tich PL/AC |
| Hien thi so cai chi phi | Display Financial Statement – CO Version | Drill-down tu so cai |
| Phan tich loi nhuan | Profitability Analysis – Actual Line Items | CO-PA tren Universal Journal (ACDOCA) |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra ten/version chinh xac tren `api.sap.com` truoc khi dung) |
|---------|-------------------------------------------------------------------------------|
| Cost center master | `API_COSTCENTER_CREATE_SRV` hoac CDS view `I_CostCenter` |
| Profit center master | `API_PROFITCENTER_SRV` hoac CDS view `I_ProfitCenter` |
| Internal order (neu duoc su dung) | `API_INTERNALORDER_SRV` |
| Product cost estimate (BOM) | `API_MATERIALCOSTESTIMATE_PROCESS_SRV` |
| Chi phi thuc te (ACDOCA) | CDS view `I_ActualCostForCostCenter_EL`, `I_ActualCostForWbsElement_EL` |
| Profitability Analysis line items | CDS view `I_ProfitabilityAnalysisLineItem` |

## 4. Huong mo rong (extensibility) cho CO

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho CO:

- **Custom Fields and Logic** — them field vao cost center master / cost estimate / CO document,
  hien tren Fiori app tuong ung.
- **Custom Business Objects** — hiem khi can cho CO (da so nhu cau la them field/logic vao doi tuong
  co san, khong phai tao doi tuong hoan toan moi).
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho CO (cost center allocation,
  product costing formula, plan data derivation) truoc khi ket luan can side-by-side.
- Khi yeu cau "can 1 cycle phan bo dac thu" — kiem tra SSCUI distribution/assessment truoc, khong
  mac dinh mo ta theo huong user exit cua ECC.

## 5. Luu y dac thu cho CO tren Public Cloud

- **Internal Orders**: Khong duoc ho tro day du nhu on-premise. Thuong duoc thay bang **Project
  Systems (WBS elements)** hoac cost objects. Kiem tra xem CO Internal Order da duoc release cho
  release hien tai tren Public Cloud chua.
- **CO-PA**: Khong con costing-based CO-PA rieng biet. Thay vao do la **Profitability Analysis (P&A)**
  tich hop san trong Universal Journal (ACDOCA). Khong can cau hinh rieng value fields.
- **Material Ledger**: Actual costing (scope item 33Q) ho tro Standard Price (type S) la chinh.
- **Tat ca bao cao CO** chay qua Fiori analytical apps — khong co menu transaction trinh bay cu dien
  (KSB1, KOB1...). Dung SAP Fiori Apps Reference Library de tim app thay the.

## 6. Khi viet/review code ABAP Cloud cho CO

- Doi tuong custom lien quan CO van theo naming convention chung o `sap-clean-code`.
- Doc du lieu cost center/profit center/chi phi thuc te qua released CDS view API
  (`I_CostCenter`, `I_ProfitCenter`, `I_ActualCostForCostCenter_EL`...), khong SELECT truc tiep
  vao ACDOCA hay bang chuan khac (COSS, CSSL, COEP).
- Bao cao CO-PA doc tu `I_ProfitabilityAnalysisLineItem` (ACDOCA-based) — khong dung bang KECA / KEKO.
- Luu y: ACDOCA la bang duy nhat cho CO-PA nen field list rat rong, dung filter can than.

## 7. Nguon tham khao

- [Cost Center Accounting (J54) — SAP Best Practices](https://me.sap.com/processnavigator)
- [Profitability Analysis in SAP S/4HANA Cloud](https://community.sap.com/t5/financial-management-blog-posts-by-sap/profitability-analysis-in-sap-s-4hana-cloud-public-edition/ba-p/13751517)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Controlling](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
