---
name: sap-successfactors-cloud
description: Kien thuc SuccessFactors chi tiet — Employee Central MDF, Recruiting, Performance, Compensation, LMS, CPI integration, RCM (Recruiting Management), ONB (Onboarding).
effort: medium
model: haiku
---

# SuccessFactors — DEEP

[Seed set — kiem chung qua SAP Help Portal, SAP Community SuccessFactors tag.]

## 1. Employee Central (EC) Configuration

### MDF (Multi-Data-File) Object
- Extend employee data voi custom object
- Config trong Admin Center -> Manage Business Configuration
- VD: Them field "Emergency Contact" vao employee master

### Foundation Object
- Cau truc to chuc: Company -> Division -> Department -> Location -> Cost Center
- Object: `Country`, `Region`, `Department`, `CostCenter`, `JobClass`

### Business Rule
- Logic: triggers, conditions, actions
- VD: "If employee is in US -> enable W4 form"
- Rule types: Validation, Derived, Default, Triggered

### Provisioning
- **Provisioning** la tool admin cap cao (SAP can config)
- VD: Enable module, set feature flag

## 2. Recruiting

| Module | Chuc nang |
|---|---|
| **Recruiting Marketing** | Careers site, candidate outreach |
| **Recruiting Management** | Job requisition -> posting -> candidate -> interview -> offer |

### Key Objects
- `JobRequisition` — Yeu cau tuyen dung
- `Candidate` — Ho so ung vien
- `JobApplication` — Don ung tuyen
- `OfferLetter` — Thu moi nhan viec

## 3. Performance & Goals

| Module | Chuc nang |
|---|---|
| **Goal Management** | Goal creation, alignment, tracking |
| **Performance Forms** | Form template, routing, rating |
| **Calibration** | Manager calibration meeting |
| **360 Reviews** | Multi-rater feedback |

## 4. Compensation

| Module | Chuc nang |
|---|---|
| **Compensation (Base)** | Merit increase, promotion |
| **Variable Pay** | Bonus, commission |
| **Long-Term Incentive** | Stock, equity |
| **Compensation Statement** | Employee communication |

## 5. Integration with S/4HANA

### Employee Master Sync (CPI)
```
SF EC -> CPI -> S/4HANA HCM (PA)
```
- Fields: Personal data, org assignment (cost center, position)
- Frequency: Real-time (OData) / Batch (SFTP)

### Org Structure Sync
```
SF EC -> CPI -> S/4HANA OM
```
- Company code, cost center, department mapping

### Payroll Integration
```
S/4HANA Payroll -> CPI -> SF (EC)
```
- Payroll results push to SF

## 6. Learning Management System (LMS)

- Course, certification, compliance training
- Integration with S/4HANA for training material sync
- SAP Jam collaboration integration

## 7. Nguon tham khao

- SAP Help Portal — SuccessFactors: `https://help.sap.com/docs/successfactors`
- SAP Community: `https://community.sap.com/t5/sap-successfactors/`
- API Reference: `https://api.sap.com/shell/discover/contentpackage/SAPSuccessFactors`
