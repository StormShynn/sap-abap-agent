---
name: sap-pm-cloud
description: Kien thuc PM (Plant Maintenance & Asset Management — maintenance order, maintenance plan, equipment, functional location, breakdown, corrective & preventive maintenance) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong PM tren Public Cloud.
effort: medium
model: haiku
---

# PM (Plant Maintenance & Asset Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| Maintenance order type | Scope item **BM2** / **BH3** | Dinh nghia order type cho bao tri (corrective/preventive) |
| Maintenance plan | Scope item **BM4** | Cau hinh maintenance strategy, scheduling (time-based / meter-based) |
| Equipment / Functional location | Scope item **BM0** | Quan ly thiet bi (equipment) va vi tri chuc nang (functional location) |
| Notification (PM notification) | Scope item **BM1** | Quy trinh bao hong / yeu cau bao tri |
| Refurbishment | Scope item **BZ3** | Tai san xuat / refurbishment cua equipment |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Tao lenh bao tri | Manage Maintenance Orders | IW31 / IW32 |
| Giai phong lenh bao tri | Release Maintenance Orders | IW35 |
| Xac nhan bao tri | Post Confirmations – Maintenance Order | IW41 / IW42 |
| Huy / dong lenh bao tri | Close Maintenance Orders | IW49 |
| Quan ly thiet bi | Manage Equipment | IE01 / IE02 |
| Quan ly vi tri chuc nang | Manage Functional Locations | IL01 / IL02 |
| Bao hong / yeu cau bao tri | Manage Maintenance Notifications | IW21 / IW22 |
| Ke hoach bao tri | Manage Maintenance Plans | IP01 / IP02 |
| Lenh bao tri dinh ky | Schedule Maintenance Plans (list) | IP10 |
| Lich su bao tri | Display Maintenance History | IW3 |
| Quan ly vat tu bao tri | Manage Spare Parts | MM02 + MMSC |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| CRUD maintenance order | `API_MAINTENANCE_ORDER_SRV` (OData) |
| Maintenance notification | `API_MAINTENANCE_NOTIFICATION_SRV` |
| Equipment | `API_EQUIPMENT_SRV` |
| Functional location | `API_FUNCTIONALLOCATION_SRV` |
| Maintenance plan | `API_MAINTENANCE_PLAN_SRV` |
| Maintenance item | `API_MAINTITEM_BY_PLANDT_SRV` |
| CDS views | `I_MaintenanceOrder`, `I_MaintenanceNotification`, `I_Equipment`, `I_FunctionalLocation`, `I_MaintenancePlan` |

## 4. Huong mo rong (extensibility) cho PM

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho PM:

- **Custom Fields and Logic** — them field vao maintenance order / notification / equipment /
  functional location / maintenance plan, hien tren Fiori app tuong ung.
- **Custom Business Objects** — khi can 1 loai check sheet / form bao tri rieng.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho PM (status change, notification
  derivation, scheduling formula) truoc khi ket luan can side-by-side.
- Khi can 1 strategy bao tri dac thu (phuc hop time-based + meter-based + condition-based),
  day thuong la dau hieu can side-by-side BTP.

## 5. Luu y dac thu cho PM tren Public Cloud

- **Equipment vs Functional Location**: Equipment la thiet bi co the di chuyen. Functional Location
  la vi tri lap dat co dinh. Tren Public Cloud, ca 2 deu quan trong cho PM.
- **Corrective vs Preventive**: Corrective (su co) → Maintenance Notification + Maintenance Order.
  Preventive (dinh ky) → Maintenance Plan → Maintenance Order.
- **Capacity planning**: Maintenance order co the can capacity (bo tri tho / ky thuat vien).
  Dung scope item **BMD** (Capacity Evaluation) neu can.
- **Spare parts**: Vat tu thay the duoc quan ly boi MM (material master, stock). PM consultant
  co the can dispatch MM consultant.
- **Integration**: PM lien ket voi PP (production equipment), MM (spare parts), FI (chi phi bao tri).
  Thuong xuyen dispatch song song.

## 6. Khi viet/review code ABAP Cloud cho PM

- Doc du lieu maintenance order / notification / equipment qua released CDS view API
  (`I_MaintenanceOrder`, `I_MaintenanceNotification`, `I_Equipment`...), khong SELECT truc tiep
  bang chuan (AUFK, AFIH, EQUI, IFLO, T356, T352).
- Quan ly vat tu bao tri (spare parts) doc tu `I_MaterialDocument` (MM) hoac `I_MaintenanceOrderComponent`.
- Chi phi bao tri doc tu ACDOCA qua CO-PA hoac FI — dispatch FI consultant.

## 7. Cac scope item chinh cho PM

| Scope Item | Mo ta |
|------------|-------|
| **BM0** | Equipment and Technical Object Management |
| **BM1** | Maintenance Notification Processing |
| **BM2** | Maintenance Order Processing |
| **BM4** | Preventive Maintenance Planning |
| **BH3** | Maintenance Order Completion and Confirmation |
| **BZ3** | Refurbishment Processing |
| **BMD** | Capacity Evaluation (cho maintenance capacity) |

## 8. Nguon tham khao

- [SAP Best Practices Explorer — PM Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Plant Maintenance](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
