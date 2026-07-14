---
name: sap-ewm-cloud
description: Kien thuc EWM (Extended Warehouse Management — inbound, outbound, internal, inventory, slotting, kitting, labor, RF) cho SAP S/4HANA Cloud Public Edition — Embedded EWM, SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve quan ly kho nang cao thay cho WM.
effort: high
model: haiku
---

# EWM (Extended Warehouse Management) — CORE — Public Cloud

> Core layer — luôn load khi dispatch EWM. Chi tiet SSCUI/Fiori/API/gotcha: `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- **EWM thay the hoan toan WM** (WM EOL cuoi 2025) — Public Edition dung **Embedded EWM** chuan.
- Cau truc kho phan cap: Warehouse Number → Storage Type → Storage Section → Storage Bin → Quant.
- 4 nhom quy trinh chinh: Inbound/Outbound/Internal/Inventory (chi tiet o deep §1); phan biet **Basic EWM** (trong license S/4HANA) vs **Advanced EWM** (can license bo sung).

## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "EWM khac WM the nao", "cau truc kho" | deep §11–§12 |
| "inbound/outbound/wave/picking/packing" | deep §13, §1–§2 |
| "slotting/labor/RF/yard/kitting/VAS" | deep §3–§8 |
| "Fiori app / SSCUI / scope item / released API" | deep §9–§10, §14–§15 |
| "them field / mo rong" | deep §16 |

## 3. Lenh goi
Doc `deep/SKILL.md` theo section lien quan (`Grep` de vi tri) → cross-check SSCUI/Fiori/API tren `api.sap.com` hoac Manage Your Solution neu can → ap dung `sap-extensibility` bac thang truoc khi de xuat side-by-side.

## 4. Tich hop
Skill lien quan: `sap-extensibility`, `sap-clean-code`, `sap-docs-researcher`.
