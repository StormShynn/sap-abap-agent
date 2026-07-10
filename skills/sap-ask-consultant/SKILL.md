---
name: sap-ask-consultant
description: Hoi truc tiep 1 "chuyen gia" SAP theo phan he (SD, FI...) cho SAP S/4HANA Cloud Public Edition. Tu dong chon dung agent tu van theo module, chay song song neu cau hoi dung nhieu module, roi tong hop cau tra loi. Dung khi user hoi "hoi SD", "hoi FI", hoac cau hoi nghiep vu ro module (sales order, GL, AP...).
argument-hint: "[cau hoi]"
model: haiku
---

# SAP Ask Consultant

Entry point de hoi 1 chuyen gia SAP theo phan he. Skill nay KHONG tu tra loi — no doc cau hoi, chon
dung agent tu van (module consultant), dispatch, roi tra ve cau tra loi cua agent do (hoac tong hop
neu nhieu agent cung tra loi).

## Khi nao dung

- User can tu van cau hinh/mo rong tren **SAP S/4HANA Cloud Public Edition** — routing tu dong dua
  tren keyword scoring, dispatch song song nhieu module neu can.
- User hoi "tra cuu CDS view", "tim tai lieu", "SAP note", "SAP Help", "Fiori app", "API hub".
- KHONG dung skill nay cho cau hoi thuan ve viet/review code (dung `abap-reviewer`).

## Module routing — Auto-scoring Engine

Day la routing **tu dong hoa hoan toan**: khong match-first-stop-first, ma la **scoring + dispatch
song song**. Moi module co 1 ma tran tu khoa co trong so. User cang nhieu tu khoa → score cang cao →
module cang chac chan duoc dispatch.

### Buoc 1: Xay dung Keyword Matrix cho tung module

Doc cau hoi user, ap dung ma tran duoi day. Moi keyword co **weight** (1-3). Module nao co
**score >= threshold (2)** thi dispatch.

| Module | Agent | Keywords (weight 3) | Keywords (weight 2) | Keywords (weight 1) | Threshold |
|--------|-------|--------------------|--------------------|--------------------|-----------|
| **SD** | `sap-sd-consultant-cloud` | sales order, pricing, billing, delivery, SD | don hang, gia, giao hang, hoa don ban, credit, quotation | chiết khấu, vận chuyển, xuất kho bán, availability check | ≥ 2 |
| **FI** | `sap-fi-consultant-cloud` | GL, journal entry, AP, AR, asset, FI | sổ cái, công nợ, khấu hao, thuế, dồn số, dòng tiền | bank, ngân hàng, clearing, reconciliation, đối chiếu | ≥ 2 |
| **MM** | `sap-mm-consultant-cloud` | purchase order, requisition, PO, goods receipt, MM | inventory, tồn kho, nhập kho, vật tư, supplier invoice | material master, kiểm kê, valuation, đơn mua, stock transfer | ≥ 2 |
| **CO** | `sap-co-consultant-cloud` | cost center, product costing, CO-PA, profitability, CO | giá thành, phân bổ chi phí, profit center, cost estimate | material ledger, actual costing, distribution, assessment | ≥ 2 |
| **PP** | `sap-pp-consultant-cloud` | production order, MRP, BOM, routing, PP | sản xuất, work center, capacity, manufacturing, bill of materials | discrete, REM, repetitive, kanban, planning strategy, task list | ≥ 2 |
| **QM** | `sap-qm-consultant-cloud` | inspection lot, quality certificate, non-conformance, QM | kiểm tra chất lượng, inspection plan, QC, quality inspection | supplier evaluation, sampling, certificate, non conformance, usage decision | ≥ 2 |
| **PM** | `sap-pm-consultant-cloud` | maintenance order, work order, equipment, functional location, PM | bảo trì, maintenance plan, notification, spare parts, breakdown | corrective, preventive, refurbishment, asset management, technical object | ≥ 2 |
| **WM** | `sap-wm-consultant-cloud` | warehouse, EWM, transfer order, putaway, WM | kho, stock placement, stock removal, picking, cycle counting, storage bin | storage type, warehouse order, yard management, RF, bin management | ≥ 2 |
| **PS** | `sap-ps-consultant-cloud` | project, WBS, network, milestone, PS | du an, project budget, settlement, resource-related billing, RRB | WBS element, availability control, project cost, milestone billing | ≥ 2 |
| **HCM** | `sap-hcm-consultant-cloud` | employee, HR, org unit, position, payroll, HCM | nhan su, personnel, timesheet, cham cong, org structure | absence, recruiting, talent, organizational management, time recording | ≥ 2 |
| **BW** | `sap-bw-consultant-cloud` | analytics, data warehouse, SAC, BW, BI | bao cao, query, analytical, reporting, dashboard, KPI | embedded analytics, CDS query, key figure, data extraction, planning | ≥ 2 |
| **Basis** | `sap-basis-consultant-cloud` | basis, role, transport, user admin, authorization | phan quyen, job, scheduling, tenant, system admin | software collection, certificate, launchpad, monitoring, Fiori admin | ≥ 2 |
| **TM** | `sap-tm-consultant-cloud` | transportation, freight order, carrier, TM | van chuyen, shipment, freight charge, freight settlement | freight agreement, rate, transportation planning, vehicle, carrier selection | ≥ 2 |
| **TR** | `sap-tr-consultant-cloud` | treasury, cash management, bank account, payment | ngan hang, dong tien, bank statement, liquidity | cash position, payment run, F110, bank reconciliation, zero balance | ≥ 2 |
| **Ariba** | `sap-ariba-consultant-cloud` | ariba, business network, sourcing, supplier collaboration | supplier management, procurement collaboration, contract management | ariba network, catalog, procurement, buyer, supplier lifecycle, CPI | ≥ 2 |
| **CA** | `sap-ca-consultant-cloud` | business partner, document management, workflow, output management | BP, DMS, WF, archiving, number range, output control | cross-application, flexible workflow, ILM, printing, forms, report painter | ≥ 2 |
| **GTS** | `sap-gts-consultant-cloud` | customs, global trade, sanctioned party list, SPL | hai quan, xuat nhap khau, preference, embargo | intrastat, bonded warehouse, export control, FTA, certificate of origin | ≥ 2 |
| **EHS** | `sap-ehs-consultant-cloud` | environment, health, safety, hazardous substance, waste | moi truong, an toan, hoa chat, MSDS, incident | product safety, industrial hygiene, occupational health, disposal, PPE | ≥ 2 |
| **Research** | `sap-docs-researcher` | CDS view, SAP note, SAP Help | Fiori app, API hub, documentation, ABAP syntax | release note, clean core, community, tra cuu, feature matrix | ≥ 2 |
| **Daily Learner** 🧠 | `sap-daily-learner` | hoc, learning, tip, hermes, quiz, progress | bai tap, lộ trình, track, tien do, on tap, practice | daily, skill, test, cau hoi, trac nghiem, study, beginner, advanced | ≥ 1 |

**Luu y**: Daily Learner co threshold thap hon (≥ 1) de dam bao user luon co the nhan duoc goi y hoc tap.

**Cach tinh score**:
- Moi ky tu dong tim kiem khong phan biet hoa thuong. Keyword weight 3 → score +3, weight 2 → +2,
  weight 1 → +1.

### Buoc 2: Xu ly explicit mention (ghi de score)

Neu user noi "hoi X" / "X tu van" / "nho X" voi X la ten module, dispatch module do **mac dinh**
(bo qua threshold), kem theo bat ky module nao khac co score >= 2:

| Explicit mention | Dispatch mac dinh |
|-----------------|------------------|
| "hoi X" cho bat ky module nao o tren | Module tuong ung |

### Buoc 3: Xu ly module coupling (dispatch nhom)

| Module A | Module coupling | Ly do |
|----------|----------------|-------|
| **CO** | `sap-fi-consultant-cloud` | CO lam viec tren ACDOCA (FI document) |
| **FI** | `sap-co-consultant-cloud` | GL/thue thuong lien quan cost accounting |
| **MM** (stock transfer, valuation) | `sap-sd-consultant-cloud` | Stock transport order lien quan SD |
| **PP** | `sap-qm-consultant-cloud`, `sap-mm-consultant-cloud` | QM inspection, BOM/component |
| **QM** | `sap-pp-consultant-cloud`, `sap-mm-consultant-cloud` | Production inspection, non-conformance |
| **PM** | `sap-mm-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-co-consultant-cloud` | Spare parts, equipment, chi phi |
| **WM** | `sap-mm-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-pp-consultant-cloud` | GR, delivery, production supply |
| **PS** | `sap-co-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-hcm-consultant-cloud` | Cost object, RRB billing, network, timesheet |
| **HCM** | `sap-co-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-ps-consultant-cloud` | Cost center, payroll, timesheet |
| **Ariba** | `sap-mm-consultant-cloud`, `sap-fi-consultant-cloud` | Procurement (MM), invoice (FI) |
| **CA** | `sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`, `sap-fi-consultant-cloud` | Business Partner thuong di kem SD (customer), MM (supplier), FI (GL) |
| **GTS** | `sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`, `sap-tm-consultant-cloud` | Sales export (SD), procurement import (MM), van chuyen (TM) |
| **EHS** | `sap-mm-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-wm-consultant-cloud` | Hoa chat = material (MM), safety in production (PP), kho hoa chat (WM) |

### Buoc 4: Tong hop dispatch

- **0 agent**: hoi lai user.
- **1 agent**: dispatch duy nhat.
- **≥2 agent**: dispatch **tat ca song song** trong 1 message.

**Da co agent**: SD, FI, MM, CO, PP, QM, PM, WM, PS, HCM, BW, Basis, TM, TR, Ariba, CA, GTS, EHS, Research, **Daily Learner**
**Tong cong**: 18 modules consultant + 1 researcher + 1 daily learner = **20 agents**.

## Quy trinh — Automated Routing Engine

1. **Phan tich cau hoi user**: normalize (lowercase, loai bo dau), trich xuat keyword.
2. **Tinh score tung module** theo Keyword Matrix o Buoc 1.
3. **Kiem tra explicit mention** (Buoc 2).
4. **Ap dung module coupling** (Buoc 3).
5. **Tong hop danh sach agent can dispatch** (Buoc 4).
6. **Dispatch** song song.
7. **Tong hop cau tra loi**: 1 agent → nguyen van; ≥2 agent → 1 doan tong hop + tung agent.
8. **Goi y buoc tiep theo**: `abap-reviewer`, `sap-docs-researcher`, `sap-daily-learner` (cho cau hoi hoc tap).

## Output format

```
🧭 Tu van: <danh sach agent da goi> | Auto-routing: <diem score tung module>
[neu ≥2 agent: doan tong hop ngan truoc]
### SD
...
### FI
...
```

Task: {{ARGUMENTS}}
