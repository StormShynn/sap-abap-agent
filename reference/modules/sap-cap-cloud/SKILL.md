---
name: sap-cap-cloud
description: Kien thuc SAP CAP (Cloud Application Programming Model) — CDS, service, Fiori, deployment, extension. Dung khi user hoi ve CAP, side-by-side extension, BTP development.
effort: low
model: haiku
---

# CAP (Cloud Application Programming Model) — CORE

> **Core layer**. Chi tiet nam o `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- **CAP la framework chinh thuc cho side-by-side extension** tren BTP. KHONG thay the ABAP RAP.
- **CAP CDS khac ABAP CDS** ve model, annotation, deployment (chi tiet so sanh: deep §2).
- **Node.js vs Java**: CAP support ca 2 runtime. Node.js pho bien hon cho POC, Java cho enterprise.

## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "CAP project structure" | deep §1 |
| "CDS entity/service, so sanh ABAP CDS" | deep §2 |
| "Fiori Elements / extension S/4HANA / deployment" | deep §4-6 |

## 3. Lenh goi
Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri); cross-check `cap.cloud.sap` neu can xac nhan version/API moi nhat; ap dung `sap-extensibility` truoc khi de xuat huong side-by-side.

## 4. Tich hop
- `sap-fiori-consultant-cloud` — Fiori + CAP annotation
- `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud`... — S/4HANA APIs
- `sap-btp-admin-consultant-cloud`, `sap-cpi-consultant-cloud` — CF/Kyma deploy, Event Mesh
