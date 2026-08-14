---
name: sap-successfactors-cloud
description: Kien thuc SuccessFactors (HXM Cloud) — Employee Central, Recruiting, Performance, Compensation, LMS, tich hop S/4HANA. Dung khi user hoi ve SuccessFactors, SF, HXM, HR cloud.
effort: low
model: haiku
---

# SuccessFactors — CORE (chi tiet: `deep/SKILL.md`)

## 1. Diem ky thuat bat buoc nho

- **SuccessFactors la HXM cloud rieng** (KHONG phai module S/4HANA core) — phan biet voi S/4HANA HCM (PA/OM/time/payroll core).
- **Employee Central**: Core HR qua MDF, Foundation Object, Business Rule; cau hinh qua Admin Center, KHONG co SSCUI.
- **Tich hop S/4HANA** qua CPI (employee master, org structure, cost center sync).

## 2. Route map

| Cau hoi user | Di den |
|---|---|
| "Employee Central / MDF / Foundation Object" | deep §1 |
| "Recruiting / talent" | deep §2 |
| "Performance & Goals / calibration" | deep §3 |
| "Compensation / variable pay" | deep §4 |
| "Tich hop S/4HANA / CPI" | deep §5 |
| "Learning / LMS" | deep §6 |

## 3. Lenh goi & Tich hop

Agent load `deep/SKILL.md` (Grep theo section §) khi user hoi cu the API/config; phoi hop `sap-hcm-consultant-cloud` (PA/OM/payroll), `sap-cpi-consultant-cloud` (iFlow), `sap-co-consultant-cloud` (cost center).
