---
name: sap-hcm-cloud
description: Kien thuc HCM (Human Capital Management — personnel admin, organizational management, time management, payroll, recruiting, talent management) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong HCM tren Public Cloud.
effort: medium
model: haiku
---

# HCM (Human Capital Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.

**Luu quan trong**: SAP S/4HANA Cloud Public Edition chi bao gom **core HCM** (personnel admin,
organizational management, time management co ban). **SuccessFactors** la he thong HCM cloud chinh
cua SAP cho talent management, recruiting, performance, learning. Neu user hoi ve tuyen dung, dao
tao, performance review → can SuccessFactors (khong phai S/4HANA core).]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| To chuc nhan su (OM) | Scope item **J45** | Cau hinh organizational structure: org unit, job, position |
| Quan ly nhan su co ban | Scope item **J12** | Personnel admin: hiring, change, termination |
| Quan ly thoi gian | Scope item **J13** | Time management: absence, attendance, time recording |
| Luong co ban | Scope item **J14** | Payroll co ban (tich hop voi SuccessFactors) |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| HSDK nhan vien | Maintain Employee Data | PA30 / PA40 |
| So do to chuc | Manage Organizational Structure | PPOME / PPOSE |
| Chuc vu | Manage Positions | PO10 / PO13 |
| Ngay nghi | Record Employee Absences | PA30 (Absence) |
| Cham cong | My Timesheet | CAT2 / CATS |
| Dashboard nhan su | Employee Profile | — |
| Bao cao nhan su | Manager Dashboard – HR | — |
| Quy trinh HR | Manage Business Processes | — |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| Employee master | `API_EMPLOYEE_BASICINFO_SRV` |
| Organizational structure | `API_ORGANIZATIONAL_UNIT_SRV` |
| Position | `API_POSITION_SRV` |
| Job | `API_JOB_SRV` |
| Time recording | `API_TIMERECORDING_ENTRY_SRV` |
| Leave / absence | `API_EMPABSENCERECORD_SRV` |
| Timesheet | `API_TIMESHEET_SRV` |
| CDS views | `I_Employee`, `I_OrganizationalUnit`, `I_Position`, `I_Job` |

## 4. Huong mo rong (extensibility) cho HCM

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho HCM:

- **Custom Fields and Logic** — them field vao employee master / org unit / position / timesheet,
  hien tren Fiori app nhan su tuong ung.
- **Custom Business Objects** — khi can 1 loai HR statistic / report rieng.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho HCM (time evaluation,
  absence calculation, org structure derivation).
- **SuccessFactors**: Neu can talent management (recruiting, performance, learning, compensation),
  day la he thong rieng tren BTP. Khong phai module trong S/4HANA core.

## 5. Luu y dac thu cho HCM tren Public Cloud

- **S/4HANA HCM chi la core HR**: Personnel admin (PA), Organization Management (OM), Time Management.
  Khong co talent management, recruiting, learning, performance management trong S/4HANA core.
- **SuccessFactors la chuan**: SAP khuyen dung SuccessFactors cho toan bo HCM cloud. S/4HANA HCM
  chi la phan con lai cho payroll / time / org structure tich hop voi finance.
- **Employee Central (SuccessFactors)**: La employee master chinh neu khach hang dung SuccessFactors.
  S/4HANA nhan employee master tu Employee Central qua integration.
- **Time Management**: S/4HANA ho tro time recording (CATS) va absence management. Neu can time
  evaluation / time schema, kiem tra scope item **J13** truoc.
- **Payroll**: S/4HANA payroll (scope J14) co the dung, nhung nhieu khach hang chuyen sang
  Employee Central Payroll (SuccessFactors).
- **Integration**: HCM trong S/4HANA lien ket voi CO (cost center assignment), FI (payroll posting),
  PS (project timesheet). Dispatch song song khi can.

## 6. Khi viet/review code ABAP Cloud cho HCM

- Doc du lieu employee / org unit / position / timesheet qua released CDS view API
  (`I_Employee`, `I_OrganizationalUnit`, `I_Position`, `I_Timesheet`...), khong SELECT truc tiep
  bang chuan HCM (PA0000, PA0001, HRP1000, HRP1001, CATSDB).
- HCM data rat nhay cam. Luon dung filter chinh xac (employee ID, period) de tranh doc du thua.
- Timesheet doc tu CATS qua `I_Timesheet` hoac `API_TIMESHEET_SRV`.

## 7. Cac scope item chinh cho HCM

| Scope Item | Mo ta |
|------------|-------|
| **J12** | Personnel Administration |
| **J13** | Time Management |
| **J14** | Payroll |
| **J45** | Organizational Management |
| **J61** | HR Analytics |

## 8. Nguon tham khao

- [SAP Best Practices Explorer — HCM Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Human Capital Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SuccessFactors vs S/4HANA HCM](https://community.sap.com/t5/human-capital-management-blog-posts-by-sap/sap-successfactors-vs-sap-erp-hcm/ba-p/13534821)
