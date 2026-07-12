---
name: sap-ibp-cloud
description: Kien thuc IBP (Integrated Business Planning — demand, supply, inventory, S&OP, control tower) cho SAP IBP Cloud — planning area, key figure, algorithm, integration voi S/4HANA. Dung khi user hoi ve planning processes, du bao, toi uu chuoi cung ung.
effort: medium
model: haiku
when_to_use: Khi user hoi ve lap ke hoach chuoi cung ung (demand planning, supply planning, S&OP, inventory optimization) hoac tich hop IBP voi S/4HANA Cloud.
---

# IBP (Integrated Business Planning) — CORE — SAP Cloud

> Core layer — luon load khi dispatch IBP. Chi tiet planning area/Fiori/algorithm/API/extensibility nam o `deep/SKILL.md`.

## 1. Diem ky thuat bat buoc nho
- IBP la giai phap planning **standalone** (khong phai module S/4HANA), giao tiep voi S/4HANA qua SAP Integration Suite (CPI).
- IBP **KHONG** co SSCUI kieu S/4HANA (cau hinh qua IBP Admin Console/Excel Add-in) va **KHONG** phai MRP (MRP la execution planning trong S/4HANA — PP).
- 5 planning area chinh: S&OP, Demand, Supply, Inventory, Response — moi loai dung 1 nhom thuat toan rieng.
## 2. Route map
| Cau hoi user | Di den |
|---|---|
| "planning area / key figure / control tower / khai niem" | deep/SKILL.md §1, §2, §6, §8 |
| "Fiori app / Excel Add-in / cong cu" | deep/SKILL.md §7 |
| "thuat toan du bao / optimizer / heuristic" | deep/SKILL.md §3 |
| "master data / tich hop S/4HANA / SAP_COM" | deep/SKILL.md §4, §5 |
| "mo rong / custom key figure / side-by-side" | deep/SKILL.md §9 |
## 3. Lenh goi agent
1. Doc `deep/SKILL.md` theo section lien quan (dung `Grep` de vi tri).
2. Cross-check tren SAP Help/api.sap.com neu can xac nhan release.
3. Phan biet IBP (strategic/tactical planning) vs PP-MRP (execution) truoc khi tra loi.
## 4. Tich hop
- IBP co bac thang extensibility rieng (khong dung `sap-extensibility` 4-tier cua S/4HANA) — xem deep §9; `sap-docs-researcher` de xac minh release-specific tren SAP Help/Community.
