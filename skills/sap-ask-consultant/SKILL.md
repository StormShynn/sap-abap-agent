---
name: sap-ask-consultant
description: Hoi truc tiep 1 "chuyen gia" SAP theo phan he (SD, FI...) — noi dung 25 module
  consultant viet cho SAP S/4HANA Cloud Public Edition (SSCUI/Fiori app cu the). Tu dong chon
  dung agent tu van theo module, chay song song neu cau hoi dung nhieu module, roi tong hop
  cau tra loi. Neu edition da biet (qua sap-service-type-context) khac s4hc_(public), tu dong
  chen canh bao SSCUI/API co the khac tren he thong that. Dung khi user hoi "hoi SD", "hoi FI",
  hoac cau hoi nghiep vu ro module (sales order, GL, AP...).
when_to_use: |
  "hoi SD: cau hinh pricing", "hoi FI ve dong so ky", "tu van MM ve purchase order",
  "cau hinh cost center va GL" (nhieu module cung luc).
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

### Buoc 0: Kiem tra edition da biet chua (khong tu chay lai neu da co)

25 module consultant agent (`sap-*-consultant-cloud`) viet noi dung SSCUI/Fiori app/API cu the
cho **`s4hc_(public)`**. Neu edition cua phien nay **da duoc xac dinh truoc do** (qua
`sap-service-type-context`, vd tu 1 luot hoi truoc trong cung phien) va **khac** `s4hc_(public)`
— ghi nho de chen canh bao o Buoc 4 (Tong hop dispatch). KHONG chu dong chay
`sap-service-type-context` o day chi de tu van thuan tuy nghiep vu don gian (tranh lam cham
routing cho cau hoi khong thuc su can) — chi ap dung canh bao NEU da biet san tu ngu canh phien.

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
| **WM** | `sap-wm-consultant-cloud` | Stock Room Management, LE-WM, classic WM, legacy WM | kho don gian, WM co dien, he thong WM cu | batch stock, non-EWM, migrate WM len Cloud | ≥ 2 |
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
| **IBP** 🆕 | `sap-ibp-consultant-cloud` | demand planning, supply planning, S&OP, inventory optimization, IBP | du bao, planning, control tower, forecast, cung cap, chuoi cung ung | safety stock, time-series, optimizer, heuristic, key figure, alert | ≥ 2 |
| **EWM** 🆕 | `sap-ewm-consultant-cloud` | warehouse, EWM, inbound, outbound, picking, packing, wave, slotting | kho, warehouse order, RF, handling unit, yard, labor | kitting, VAS, cycle counting, putaway, replenishment, storage bin | ≥ 2 |
| **Fiori/UI5** 🆕 | `sap-fiori-consultant-cloud` | Fiori, UI5, Fiori Elements, Adaptation Project, Launchpad | giao dien, frontend, UX, tile, semantic object | Fiori app, role, catalog, group, SAP Build, Work Zone | ≥ 2 |
| **CAP** 🆕 | `sap-cap-consultant-cloud` | CAP, cloud application programming, CDS (CAP), extension, BTP dev | side-by-side, BTP, Node.js, Java, OData V4 | MTA, CF deploy, CAP project, srv, annotation | ≥ 2 |
| **CPI** 🆕 | `sap-cpi-consultant-cloud` | CPI, iFlow, integration flow, adapter, interface | tich hop, integration, API management, mapping, message | SOAP, OData adapter, SFTP, Event Mesh, Groovy | ≥ 2 |
| **SuccessFactors** 🆕 | `sap-successfactors-consultant-cloud` | SuccessFactors, SF, HXM, Employee Central, recruiting, talent | HR cloud, performance, compensation, LMS | MDF, business rule, integration SF, onboarding, CPI | ≥ 2 |
| **BTP Admin** 🆕 | `sap-btp-admin-consultant-cloud` | BTP admin, CF, Cloud Foundry, Kyma, destination | cockpit, subaccount, Cloud Connector, XSUAA | role collection, service marketplace, MTA deploy, CI/CD | ≥ 2 |
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

**Dieu kien dispatch** (tranh dispatch thua, ton token): module coupling KHONG tu dong dispatch
toan bo danh sach duoi day. Chi dispatch module ghep cap neu module do **cung dat score >= 1**
tren Keyword Matrix (Buoc 1) — tuc cau hoi user co it nhat 1 tu khoa lien quan module do. Neu
module ghep cap dat 0 diem (khong co tu khoa lien quan trong cau hoi), KHONG dispatch — chi neu
ten trong output o muc "Co the hoi them" (xem Buoc 4).

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
| **IBP** 🆕 | `sap-sd-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-mm-consultant-cloud` | S&OP can sales forecast (SD), supply planning (PP), procurement (MM) |
| **EWM** 🆕 | `sap-mm-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-tm-consultant-cloud` | Inbound (MM), outbound (SD), production supply (PP), yard (TM) |
| **Fiori/UI5** 🆕 | `sap-cap-consultant-cloud`, `sap-btp-admin-consultant-cloud` | CAP + Fiori annotation, BTP Work Zone deployment |
| **CAP** 🆕 | `sap-fiori-consultant-cloud`, `sap-btp-admin-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud` | Fiori UI, CF/Kyma deploy, S/4HANA APIs |
| **CPI** 🆕 | `sap-sd-consultant-cloud`, `sap-mm-consultant-cloud`, `sap-ariba-consultant-cloud`, `sap-successfactors-consultant-cloud` | S/4HANA APIs (SD/MM), Ariba Network, SF integration |
| **SuccessFactors** 🆕 | `sap-hcm-consultant-cloud`, `sap-cpi-consultant-cloud`, `sap-co-consultant-cloud` | S/4HANA HCM core (PA/OM/time), CPI integration, cost center |
| **BTP Admin** 🆕 | `sap-cap-consultant-cloud`, `sap-basis-consultant-cloud`, `sap-cpi-consultant-cloud`, `sap-fiori-consultant-cloud` | CAP deploy, S/4HANA system admin, CPI Cloud Connector, Work Zone |

### Buoc 4: Tong hop dispatch

- **0 agent**: hoi lai user.
- **1 agent**: dispatch duy nhat.
- **2-3 agent**: dispatch **tat ca song song** trong 1 message.
- **>3 agent** (hiem gap, thuong do nhieu module coupling cung dat score sau Buoc 3): dispatch
  **top 3 theo score cao nhat**, cac module con lai KHONG dispatch — chi liet ke ten trong output
  ("Co the hoi them: <module>") de user tu quyet dinh hoi tiep, tranh chay song song qua nhieu
  agent cho 1 cau hoi.
- **Canh bao edition** (chi khi Buoc 0 da xac dinh edition != `s4hc_(public)`): them 1 dong dau
  output (xem muc Output format) — "⚠️ Noi dung agent duoi day viet cho Public Edition (SSCUI/
  Fiori app cu the) — he thong ban dang lam viec la `<edition>`, ten SSCUI/transaction tuong
  ung co the khac. Xem `sap-service-type-context` de biet dieu chinh." KHONG chan dispatch, chi
  canh bao.

### Buoc 5: Tra cuu kien thuc co san (local + Notion) truoc khi dispatch

Voi tung module sap dispatch (danh sach tu Buoc 4), tra xem da co skill/kien thuc lien quan chua
truoc khi giao han cho agent tu van tra loi tu dau — cac agent tu van (25 module + Research +
abap-reviewer) deu KHONG co quyen Write/Edit, nen buoc tra cuu + cache nay lam o day (skill dieu
phoi, khong bi gioi han quyen), khong sua tung agent:

1. **Local truoc (offline, luon lam, re)**: `Glob`/`Grep` tren `memory/procedural/skills/` (duong
   dan qua `python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/procedural/skills`
   — xem skill `sap-daily-learner` muc 1) tim file khop `<module>-*`. Thay -> dua noi dung vao
   context khi dispatch agent, **KHONG goi Notion** (tranh round-trip mang cho cau da co san local),
   **dong thoi ghi nhan usage cho Skill Curator** (xem `sap-daily-learner` muc 3d — skill it
   dung dan bi danh dau `stale` roi `archived`, dung lai thi tinh la con gia tri):
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/skill_curator.py" record-use \
     "$(python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/procedural)" \
     "<ten-file-skill>.md"
   ```
2. **Notion khi local mien (online, chi khi can)**: goi tool search cua MCP `notion` theo module +
   tu khoa cau hoi — **chi search truoc** (index gon, re token), **KHONG fetch tat ca ket qua**.
   Da test that (2026-07-16): search toan workspace van tra dung ket qua top-1 nhung lan noise
   voi cac trang mac dinh cua Notion (VD "Getting Started") o workspace nho co it noi dung — neu
   trong phien da biet data source id cua database "SAP Skills" (VD tu 1 lan `notion-fetch`/tao
   database truoc do trong cung phien), uu tien truyen `data_source_url: "collection://<id>"`
   cho tool search de gioi han pham vi, ket qua sach hon (da xac nhan qua test). Neu chua biet id
   (lan dau trong phien) thi search toan workspace nhu binh thuong, khong sao.
   Trong ket qua, chon dung page khop chu de roi moi goi tool fetch lay noi dung day du cho page
   do. Thay page khop -> dua vao context khi dispatch, **dong thoi tu ghi 1 ban local cache** vao
   `memory/procedural/skills/` (copy co hoc noi dung da co/da duyet tren Notion — khac voi viec
   "tao skill moi", van la viec rieng cua `sap-daily-learner` qua Auto-Skill Creation Engine cua no).
   Ngoai ra tang property `Lan dung lai` cua page do them 1 (best-effort, khong can atomic — xem
   `sap-daily-learner` muc "3c. Promote skill" de biet vi sao: dung lai du nhieu lan la dieu kien
   de 1 skill duoc de xuat dua vao `reference/modules/` cho moi nguoi dung, khong chi rieng team).
3. Khong thay o ca 2 -> dispatch binh thuong nhu hien tai, khong co gi thay doi.
4. **Fail-open bat buoc**: loi o buoc 1 hoac 2 (Notion chua connect qua `/mcp`, mat mang...) -> bo
   qua, dispatch binh thuong, KHONG chan routing.

**"Clone lai tu Notion khi mat local"**: xay ra tu nhien theo lazy-fetch o buoc 2 — lan dau hoi lai
1 chu de sau khi mat local (vd xoa `%USERPROFILE%\.sap-abap-agent\`), buoc 2 tu fetch lai tu Notion
+ tu cache lai, khong can thao tac resync rieng nao.

**Ve dung luong o cung**: moi skill doc ~2-5KB text — ngay ca kich ban nang (10,000 skill tich luy
qua nhieu nam, ca team dung chung) van chi ~30-50MB, khong dang lo o quy mo noi dung text nay. Xem
bao cao dung luong hien tai (chi hien thi, KHONG tu xoa `memory/`):
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/cleanup_agent_home.py"
```

**Da co agent**: SD, FI, MM, CO, PP, QM, PM, WM, PS, HCM, BW, Basis, TM, TR, Ariba, CA, GTS, EHS, **IBP**, **EWM**, **Fiori/UI5**, **CAP**, **CPI**, **SuccessFactors**, **BTP Admin**, Research, **Daily Learner**
**Tong cong**: 25 modules consultant + 1 researcher + 1 daily learner = **27 agents**.

## Quy trinh — Automated Routing Engine

0. **Kiem tra edition da biet chua** (Buoc 0) — chi ghi nho de canh bao neu khac `s4hc_(public)`,
   khong chu dong chay `sap-service-type-context`.
1. **Phan tich cau hoi user**: normalize (lowercase, loai bo dau), trich xuat keyword.
2. **Tinh score tung module** theo Keyword Matrix o Buoc 1.
3. **Kiem tra explicit mention** (Buoc 2).
4. **Ap dung module coupling co dieu kien** (Buoc 3) — chi giu module coupling nao cung dat score >= 1.
5. **Tong hop danh sach agent can dispatch, cap toi da 3** (Buoc 4) — du ra chuyen thanh goi y.
6. **Tra cuu kien thuc co san** (Buoc 5) — local truoc, Notion khi local mien, fail-open neu loi.
7. **Dispatch** song song, kem context da tra cuu duoc (neu co) cho tung agent.
8. **Tong hop cau tra loi**: 1 agent → nguyen van; ≥2 agent → 1 doan tong hop + tung agent.
9. **Goi y buoc tiep theo**: `abap-reviewer`, `sap-docs-researcher`, `sap-daily-learner` (cho cau hoi hoc tap).

## Output format

```
[neu edition da biet != s4hc_(public): dong canh bao SSCUI/API o Buoc 4]
🧭 Tu van: <danh sach agent da goi> | Auto-routing: <diem score tung module>
[neu ≥2 agent: doan tong hop ngan truoc]
[neu bi cap o Buoc 4: them dong "Co the hoi them: <module bi cap>"]
[neu tim thay kien thuc co san o Buoc 5: them dong "📚 Da dung kien thuc co san (<local|Notion>)"]
### SD
...
### FI
...
```

Task: {{ARGUMENTS}}
