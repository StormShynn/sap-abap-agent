---
name: sap-fi-cloud
description: FI (Financial Accounting - GL/Universal Journal, AP, AR, Asset) cho SAP S/4HANA Cloud Public Edition. CORE LAYER (luôn load khi dispatch FI). Chi chua route map, diem ky thuat can nho, va link den DEEP layer neu can chi tiet SSCUI/API/Fiori.
effort: low
model: haiku
---

# FI (Financial Accounting) — CORE — Public Cloud

> Core layer — luôn load khi dispatch FI. Chi tiet SSCUI/Fiori/API/gotcha: `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- Universal Journal (ACDOCA) la GL duy nhat, khong co classic/new GL — moi doc/ghi qua released API.
- Business Partner la model duy nhat cho customer/supplier.
- Ledger & chuan ke toan (local GAAP/IFRS song song) quyet dinh cau truc — doi sau go-live rui ro cao.

## 2. Route map
| Cau hoi user | Di den |
|---|---|
| Hach toan GL / journal entry | deep §2 (Fiori) + §3 (API) |
| Invoice AP/AR, doi tac kinh doanh | deep §3 (Released API) |
| Asset accounting / khau hao | deep §3 + §4 |
| Them field / custom logic / validation hach toan | deep §4 (Extensibility) |
| Dong so ky/nam/closing, ledger | deep §1 |

## 3. Lenh goi
Load `deep/SKILL.md` theo section lien quan (`Grep` de vi tri) → cross-check `api.sap.com` neu can → ap dung `sap-extensibility` bac thang truoc khi de xuat side-by-side.

## 4. Tich hop
Skill lien quan: `sap-extensibility`, `sap-clean-code`, `sap-docs-research`, `sap-cds-kb`.
