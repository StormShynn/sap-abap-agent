---
name: sap-ps-cloud
description: Kien thuc PS (Project Systems — project, WBS element, network, milestone, project budget, settlement, resource-related billing) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong PS tren Public Cloud.
effort: medium
model: haiku
---

# PS (Project Systems) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| Project co ban | Scope item **S4CORE > JBP** | Cau hinh project profile, WBS, network |
| Project budget | Scope item **3UC** | Quan ly project budget, phan bo va kiem soat |
| Resource-related billing | Scope item **3UY** | RRB cho project: tinh tien dua tren resource |
| Settlement | — | Cau hinh settlement rule, settlement profile |
| Milestone / Payment | Scope item **3UB** | Quan ly milestone, project payment |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao/sua project | Manage Projects | CJ20N |
| Hien thi project | Display Project - List | CJ03 |
| Tao WBS element | Manage WBS Elements | CJ11 / CJ12 |
| Network / activity | Manage Networks | CJ21 / CJ22 |
| Phan bo budget | Manage Project Budgets | CJ32 / CJ33 |
| Cham cong cho project | Post Confirmations – Project | CN21 / CN22 |
| Billing project (RRB) | Process Resource-Related Billing | DP90C |
| Hien thi project cost | Display Project Costs | CJI3 / CJI5 |
| Phan tich project | Project Profitability Analysis | CJ8A |
| Dashboard project | Project Manager Dashboard | — |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| CRUD project (WBS) | `API_PROJECT_SRV` |
| Network & activity | `API_PROJECT_NETWORK_SRV` |
| Project budget | `API_PROJECTBUDGET_SRV` |
| Resource-related billing (RRB) | `API_RESOURCERELBILLINGDOC_SRV` |
| Project actual costs | CDS view `I_ActualCostForProject_EL`, `I_PlanCostForProject_EL` |
| CDS views | `I_Project`, `I_WBSElement`, `I_Network`, `I_ProjectBudget` |

## 4. Huong mo rong (extensibility) cho PS

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho PS:

- **Custom Fields and Logic** — them field vao project / WBS element / network / project budget,
  hien tren Fiori app tuong ung.
- **Custom Business Objects** — khi can 1 loai project statistic / KPI rieng.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho PS (project status change,
  budget check, billing formula) truoc khi ket luan can side-by-side.
- Khi can 1 project template / workflow phuc tap ngoai scope item chuan, thuong can side-by-side BTP.

## 5. Luu y dac thu cho PS tren Public Cloud

- **Project Systems tren Public Cloud co pham vi hep hon on-premise.** Nhieu profile / WBS
  planning board khong co san. Kiem tra Fiori Apps Reference Library.
- **Internal Orders thay bang WBS elements**: Tren Cloud, Internal Orders khong duoc ho tro day du.
  Project Systems (WBS) la thay the chinh.
- **Project budget**: Co scope item **3UC** cho budget management. Kiem tra Budget Profile va
  Availability Control.
- **Resource-Related Billing (RRB)**: Scope item **3UY** cho billing dua tren resource (timesheet,
  expense). Dung cho project billing voi khach hang.
- **Integration**: PS lien ket voi CO (WBS element la cost object), FI (GL cho project cost),
  PP/PM (project activities), SD (RRB billing). Dispatch song song khi can.

## 6. Khi viet/review code ABAP Cloud cho PS

- Doc du lieu project / WBS / network qua released CDS view API (`I_Project`, `I_WBSElement`,
  `I_Network`, `I_ProjectBudget`...), khong SELECT truc tiep bang chuan (PROJ, PRPS, AFVC, COBL).
- Project cost doc tu ACDOCA qua `I_ActualCostForProject_EL` hoac `I_PlanCostForProject_EL`.
- Khi can settlement project cost, dung `API_PROJECT_SRV` thay vi CAPTAIN (PSST) truc tiep.

## 7. Cac scope item chinh cho PS

| Scope Item | Mo ta |
|------------|-------|
| **JBP** | Project Management (WBS, network) |
| **3UC** | Project Budget Management |
| **3UY** | Resource-Related Billing |
| **3UB** | Project Milestone and Payment |
| **J6N** | Project Capacity Planning |

## 8. Nguon tham khao

- [SAP Best Practices Explorer — PS Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Project Systems](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
