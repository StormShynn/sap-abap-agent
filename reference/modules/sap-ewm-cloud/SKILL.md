---
name: sap-ewm-cloud
description: Kien thuc EWM (Extended Warehouse Management — inbound, outbound, internal, inventory, slotting, kitting, labor, RF) cho SAP S/4HANA Cloud Public Edition — Embedded EWM, SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve quan ly kho nang cao thay cho WM.
effort: high
model: haiku
when_to_use: Khi user hoi ve warehouse management nang cao (EWM thay vi WM co dien) tren S/4HANA Cloud Public Edition, hoac khi can biet ve Embedded EWM scopeBK9.
---

# EWM (Extended Warehouse Management) — CORE — Public Cloud

> Day la **core layer**. Chi tiet SSCUI/Fiori app/API/scope item nam o `deep/SKILL.md` — agent
> doc khi user hoi cu the hoac can cross-reference.

## 1. Diem ky thuat bat buoc nho

- **EWM thay the hoan toan WM** (WM EOL cuoi 2025) — Public Edition dung **Embedded EWM** lam kien truc chuan.
- Cau truc kho phan cap: Warehouse Number → Storage Type → Storage Section → Storage Bin → Quant.
- 4 nhom quy trinh chinh: **Inbound**, **Outbound**, **Internal**, **Inventory** (chi tiet o deep §1).
- Phan biet **Basic EWM** (trong license S/4HANA) vs **Advanced EWM** (can license bo sung).

## 2. Route map

| Cau hoi user | Di den |
|---|---|
| "EWM khac WM the nao", "cau truc kho" | deep/SKILL.md §11–§12 |
| "inbound/outbound/wave/picking/packing" | deep/SKILL.md §13, §1–§2 |
| "slotting/labor/RF/yard/kitting/VAS" | deep/SKILL.md §3–§8 |
| "Fiori app / SSCUI / scope item / released API" | deep/SKILL.md §9–§10, §14–§15 |
| "them field / mo rong" | deep/SKILL.md §16 |

## 3. Lenh goi agent

1. Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri).
2. Cross-check SSCUI/Fiori/API tren `api.sap.com` hoac Manage Your Solution neu can.
3. Ap dung `sap-extensibility` bac thang truoc khi de xuat side-by-side.

## 4. Tich hop

- Skill `sap-extensibility` — bac thang mo rong.
- Skill `sap-clean-code` — naming convention custom object.
- `sap-docs-researcher` — xac minh SSCUI/API/scope item con dung tren release hien tai.
