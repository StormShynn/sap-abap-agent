---
name: sap-fi-cloud
description: FI (Financial Accounting - GL/Universal Journal, AP, AR, Asset) cho SAP S/4HANA Cloud Public Edition. CORE LAYER (luôn load khi dispatch FI). Chi chua route map, diem ky thuat can nho, va link den DEEP layer neu can chi tiet SSCUI/API/Fiori.
effort: low
model: haiku
---

# FI (Financial Accounting) — CORE — Public Cloud

> Day la **core layer**. Khi user hoi FI, agent chi load file nay (~20 dong). Chi tiet SSCUI/Fiori
> app/API/deep gotcha nam o `deep/SKILL.md` — agent doc khi user hoi cu the (vd "SSCUI dong so
> ke toan") hoac khi can cross-reference.

## 1. Diem ky thuat bat buoc nho

- **Universal Journal (ACDOCA)** la GL duy nhat — KHONG co classic/new GL. Moi doc/ghi deu qua released API hoac CDS view API (`I_JournalEntryItem`, ...).
- **Business Partner la model duy nhat** cho customer/supplier — KHONG co XD01/XK01 rieng.
- **Ledger** quan trong cho dong so: so luong ledger, chuan ke toan (local GAAP / IFRS song song) la quyet dinh cau truc. Doi sau go-live = rui ro cao.

## 2. Route map

| Cau hoi user | Di den |
|---|---|
| "hach toan GL", "post journal entry" | deep/SKILL.md §2 Fiori + §3 API |
| "customer invoice / supplier invoice / payable / receivable" | deep/SKILL.md §3 Released API (BP + Journal Entry API) |
| "asset accounting / khau hao" | deep/SKILL.md §3 + §4 (neu can mo rong) |
| "them field vao journal entry / business partner" | deep/SKILL.md §4 (Custom Field and Logic - bac 1) |
| "can validation luc hach toan" | Custom Logic (Cloud BAdI), KHONG validation kieu cu |
| "dong so ky / nam / closing" | deep/SKILL.md §1 (Ledger), nhac release-specific |

## 3. Lenh goi agent

Khi user cau hoi FI ma khong nam trong core nay, agent:
1. Load `deep/SKILL.md` voi line range theo section lien quan (dung `Grep` de vi tri section).
2. Cross-check voi `api.sap.com` neu can xac nhan release cu the (rule §6 deep).
3. Ap dung `sap-extensibility` bac thang truoc khi de xuat side-by-side.

## 4. Tich hop

- Skill `sap-extensibility` — bac thang mo rong (uu tien bac 1, 2, 3 truoc side-by-side).
- Skill `sap-clean-code` — naming convention cho custom FI object.
- `sap-docs-researcher` — xac minh release cu the tren SAP Help/Community/API Hub.
- Skill `sap-cds-kb` — tra cuu CDS view released (`I_JournalEntryItem`, `I_BusinessPartner`).