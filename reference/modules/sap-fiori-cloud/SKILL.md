---
name: sap-fiori-cloud
description: Kien thuc SAP Fiori / UI5 — Fiori Elements, Freestyle UI5, Adaptation Project, Launchpad, SAP Build. Dung khi user hoi ve Fiori app, giao dien UI5, tuy chinh Fiori tren Public Cloud.
effort: low
model: haiku
---

# Fiori/UI5 — CORE — Public Cloud

> **Core layer**. Chi tiet SSCUI/app/API nam o `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- Fiori Elements la mac dinh — config-driven (CDS annotation), khong can code UI5; Freestyle UI5 chi dung khi Elements khong dap ung (complex UI, custom control).
- Adaptation Project tuy chinh Fiori app chuan (them/an field, sap xep) ma khong can modify app goc.
- Business Role + Catalog + Group + Target Mapping la 4 thanh phan cua Fiori Launchpad.
## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "Fiori app cho nghiep vu X" | deep §1 App Reference Library |
| "tuy chinh Fiori app" | deep §2 Adaptation Project |
| "annotation / them field UI" | deep §3 CDS Annotation |
| "Launchpad / role / catalog" | deep §4 Launchpad Config |
| "SAP Build / low-code UI" | deep §5 SAP Build |
| "UI5 custom control / freestyle" | deep §6 UI5 development |

## 3. Lenh goi agent
1. Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri).
2. Cross-check Fiori ID/API tren Fiori Apps Library / api.sap.com neu can.
## 4. Tich hop
- `sap-cap-consultant-cloud`, `sap-btp-admin-consultant-cloud`, `sap-docs-researcher`
