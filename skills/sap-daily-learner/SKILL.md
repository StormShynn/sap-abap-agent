---
name: sap-daily-learner
description: Skill tu dong hoa viec hoc SAP/ABAP moi ngay - tu dong tao skill, track tien do, goi y noi dung dua trinh do nguoi dung. Lay cam hung tu Hermes Agent (Nous Research).
when_to_use: |
  "hoc SAP hom nay", "quiz MM cho toi", "progress hoc tap cua toi", "hoc tiep module PP".
effort: high
model: sonnet
---

# SAP Daily Learner - Skill Implementation

## 0. Memory Hierarchies (3 tang - ap dung tu memory-systems skill)

He thong persistent memory cua skill nay duoc to chuc thanh 3 tang (theo pattern memory-systems
trong repo agent-skills-for-context-engineering). Mac dinh chi tang SEMANTIC la load len
context; 2 tang con lai chi load theo nhu cau.

```
<workspace>/.sap-abap-agent/memory/
├── episodic/              # Tang 1 - lich su chat (append-only, log raw)
│   ├── 2026-07/
│   │   ├── 2026-07-11_session-001.md   # 1 file / session, gom chat + tool calls
│   │   └── 2026-07-11_session-002.md
│   └── index.jsonl        # append-only: 1 dong / turn (timestamp, session_id, role, brief)
├── semantic/              # Tang 2 - kien thuc da rut trich (file chinh, load default)
│   ├── LEARNING_PROGRESS.md   # module progress, level, mastered topics
│   ├── knowledge_graph.jsonl  # entity: concept/module/topic; relationship
│   └── notes/
│       ├── fi-acdoca.md       # concept-level note, viet khi user "explain ACDOCA"
│       └── mm-stock-valuation.md
└── procedural/            # Tang 3 - skill/cach lam (auto-created tu success cases)
    └── skills/                # alias cho skills/sap-user-skills/
        └── <module>-<topic>.md
```

**Quy tac su dung**:
- Tang SEMANTIC: luon load khi goi skill (chi LEARNING_PROGRESS.md + knowledge_graph.jsonl - gioi han <100KB).
- Tang EPISODIC: chi load khi user hoi "hom qua chung ta thao luan gi" / "session truoc toi da hoi gi" - doc qua index.jsonl de biet session nao can doc.
- Tang PROCEDURAL: giong auto-skill creation hien tai - khong load, chi dispatch khi relevant.

## 1. Persistent Knowledge Store (tang SEMANTIC)

### File chinh: `.sap-abap-agent/memory/semantic/LEARNING_PROGRESS.md`

Cau truc (giu nguyen format hien tai, chi them metadata cho memory-tier):

```markdown
# SAP Learning Progress

Last updated: 2026-07-11
Session count: 1
Total skills created: 0
Memory tier loaded: semantic

## Module Progress

| Module | Level | Topics Mastered | Topics Pending | Last Activity |
|--------|-------|----------------|----------------|---------------|
| SD | beginner | 0 | 5 | never |
| FI | beginner | 0 | 5 | never |
| MM | beginner | 0 | 5 | never |
| CO | beginner | 0 | 5 | never |
| PP | beginner | 0 | 5 | never |

## Recommended Next Module
> **Moi bat dau? Hay hoc MM (Materials Management)** - module pho bien nhat, de tiep can voi quy trinh procurement hang ngay.

## Auto-Created Skills
*(chua co skill nao)*
```

### Knowledge Graph (knowledge_graph.jsonl - moi line la 1 entity hoac relationship)

```jsonl
{"type":"entity","id":"fi-acdoca","name":"Universal Journal (ACDOCA)","module":"FI","tags":["gl","fundamental","public-cloud"]}
{"type":"entity","id":"mm-po","name":"Purchase Order","module":"MM","tags":["procurement"]}
{"type":"entity","id":"sd-pricing","name":"Pricing Condition","module":"SD","tags":["sales"]}
{"type":"relationship","from":"fi-acdoca","to":"mm-po","rel":"referenced-by","note":"IR (Invoice Receipt) posts to ACDOCA"}
{"type":"relationship","from":"sd-pricing","to":"fi-acdoca","rel":"posts-to","note":"Billing writes FI doc via ACDOCA"}
```

Quy tac ghi:
- Moi khi user noi "explain X" hoac "Y la gi", tao 1 entity neu chua co.
- Moi khi consultant agent noi "X lien quan Y", tao 1 relationship.
- KHONG ghi nhan thong tin da bi (rule gotcha #3 cua memory-systems: tranh over-engineer early).

### Module Knowledge Matrix - Noi dung hoc cho tung module

Moi module co 5 topics, 3 levels:

| Module | Beginner | Intermediate | Advanced |
|--------|----------|-------------|----------|
| **SD** | sales order, pricing, delivery, billing, customer master | credit memo, rebate, availability check, output, EDI | consignment, stock transfer, SD-FI integration, revenue recognition, condition contract |
| **FI** | GL, AP, AR, bank, business partner | asset, closing, tax, dunning, payment run | consolidation, special GL, document splitting, financial closing cockpit, IFRS vs local GAAP |
| **MM** | PO, PR, GR, IR, material master | inventory, sourcing, contract, output, valuation | stock transport, consignment, subcontracting, batch management, serial number |
| **CO** | cost center, internal order, activity type, primary cost, secondary cost | product costing, CO-PA, profit center, assessment, distribution | material ledger, actual costing, PCA, segment reporting, margin analysis |
| **PP** | production order, BOM, routing, work center, MRP | discrete mfg, REM, repetitive, capacity, kanban | PP/DS, variant configuration, MTO/ETO, production campaign, PI sheet |
| **QM** | inspection lot, inspection plan, MIC, sample, usage decision | quality certificate, non-conformance, supplier eval, QM in procurement | QM in production, QM integration PP-PI, audit management, stability study |
| **PM** | maintenance order, equipment, FL, notification, task list | maintenance plan, spare parts, maintenance schedule, cost | EAM, asset analytics, predictive maintenance, mobile maintenance, IoT integration |
| **WM** | warehouse, storage bin, TR, TO, stock placement | picking, putaway, cycle counting, physical inventory | EWM, yard management, VAS, RF, warehouse monitor |
| **PS** | project, WBS, network, milestone, budget | settlement, RRB, availability control, cost planning | resource-related billing, project portfolio, SAP PS-SD-PP integration, claim mgmt |
| **HCM** | org unit, position, employee master, PA, payroll | timesheet, TM, training, recruiting | SuccessFactors integration, payroll control, OM, ESS/MSS |
| **BW** | query, report, KPI, data source, provider | composite provider, BW extractor, analytics, SAC | embedded analytics, CDS analytics, planning, BW bridge |
| **Basis** | user admin, role, transport, client, job | system admin, monitoring, Fiori admin, patches | tenant management, BTP, IAS, SSE, cloud connector |
| **TM** | freight order, carrier, shipment, freight unit | freight agreement, rate, settlement, planning | transportation network, vehicle scheduling, TM-EWM integration, GTS integration |
| **TR** | bank account, payment run, F110, bank statement | cash management, liquidity, bank reconciliation | treasury, hedge management, debt management, SEPA |
| **Ariba** | Ariba Network, sourcing, supplier, catalog, PO | contract, invoicing, guided buying, approval workflow | SAP Business Network, procurement integration, Ariba-MM integration, Ariba-FI integration |
| **CA** | business partner, DMS, output, number range, WF | flexible workflow, forms, archiving, ILM | BTP integration, CA-SD integration, CA-MM integration, document info record |
| **GTS** | customs, export, import, SPL, preference | Intrastat, FTA, bonded warehouse, embargo | compliance management, GTS-SD integration, GTS-MM integration, GTS-TM integration |
| **EHS** | hazardous sub, MSDS, waste mgmt, incident, PPE | product safety, industrial hygiene, occupational health | EHS-PP integration, EHS-WM integration, EHS-MM integration, sustainability |

## 2. Daily Tip Engine

### Tip Selection Algorithm

```
1. Read LEARNING_PROGRESS.md (semantic tier, default load)
2. Xac dinh module user dang hoc (Level cao nhat, gan nhat)
3. Chon topic trong module do chua mastered
4. Tao tip 1-3 dong + link den notes/<concept>.md neu co (semantic tier)
5. Neu user hoi them -> load notes/<concept>.md (cung semantic tier, nhu chi load 1 file)
```

### Scheduling co che

Mac dinh tip khi session dau trong ngay (kiem tra `episodic/index.jsonl` ngay hom nay).

## 3. Auto-Skill Creation Engine (tang PROCEDURAL)

Tu dong tao skill khi:

1. **Problem complexity >= 3 steps**: Van de can >= 3 buoc giai quyet
2. **Co cau hinh cu the**: Co SSCUI / Fiori app / API duoc de cap
3. **User response positive**: User noi "cam on", "huu ich", "duoc roi", "got it", "great"
4. **Khong trung lap**: Kiem tra `procedural/skills/` (alias `skills/sap-user-skills/`) khong co file tuong tu

### Skill storage (tang PROCEDURAL)

- **Thu muc**: `memory/procedural/skills/` (alias `skills/sap-user-skills/` - giu compat)
- **Naming**: `<module>-<topic-slug>.md` (vd: `mm-purchase-order-approval.md`)
- **Format**: YAML frontmatter + markdown content

### Vi du skill duoc tao tu dong:

```markdown
---
name: mm-purchase-order-approval
description: Huong dan cau hinh approve workflow cho purchase order tren S/4HANA Cloud Public Edition
created: 2026-07-11
source: "User hoi: lam sao de PO can approval truoc khi gui supplier?"
tags: [MM, PO, workflow, approval, SSCUI]
---

# Purchase Order Approval Workflow

## Problem
PO can duoc phe duyet truoc khi gui supplier. Khong co workflow mac dinh.

## Solution

### Buoc 1: Kich hoat scope item
- Scope item: **BNS** (Operational Procurement)
- App: Manage Your Solution -> check BNS da active

### Buoc 2: Cau hinh Release Strategy
- SSCUI: **101122** (Define Release Strategy for Purchasing Documents)
- Dieu kien: dua tren gia tri PO (>= 5000 USD can approve)

### Buoc 3: Gan nguoi phe duyet
- SSCUI: **101123** (Assign Release Codes)
- Gan user/role cho tung release code

### Buoc 4: Test
- Fiori app: Manage Purchase Orders -> tao PO > 5000 -> kiem tra status "To be released"

## SSCUI / Fiori App
- SSCUI 101122: Define Release Strategy for Purchasing Documents
- SSCUI 101123: Assign Release Codes
- Fiori: Manage Purchase Orders

## API (neu co)
- `API_PURCHASEORDER_PROCESS_SRV`
- `API_RELEASESTRATEGY_SRV`

## Notes
- Release strategy can active truoc khi PO duoc tao
- Co the ket hop nhieu dieu kien (value + material group)
- Phien ban 2502+ co them condition "document type"
```

## 4. Episodic tier - chat history

File `<workspace>/.sap-abap-agent/memory/episodic/<YYYY-MM>/<YYYY-MM-DD>_session-<id>.md`
ghi lai session (user prompt, agent response, tool calls). Dinh dang append-only - KHONG sua
sau khi ghi (dinh ly audit trail).

Header moi file:
```markdown
# Session <id> - <YYYY-MM-DD>
Started: <timestamp>
Ended: <timestamp>
User: <user_id_or_alias>
Topics: <list_module_topics>
Outcome: <success | partial | failed>
```

Dong cuoi file luon la 1 dong JSON append vao `index.jsonl`:
```json
{"session_id":"<id>","date":"<YYYY-MM-DD>","topics":["FI","MM"],"outcome":"success","turns":12}
```

**Quy tac cleanup episodic**:
- Giu 30 ngay gan nhat (hoac 100 session, lay gia tri nho hon).
- Sau do archive vao `episodic/archive/<YYYY>/` (zip), KHONG xoa (audit).

## 5. Tich hop voi sap-ask-consultant

Them daily-learner vao module routing (giu nguyen):

| Trigger keywords | Dispatch |
|-----------------|----------|
| "hoc", "learning", "daily", "tip", "bai tap", "lo trinh", "progress", "hermes" | `sap-daily-learner` |
| "hoc SD", "hoc FI", "hoc MM"... | `sap-daily-learner` + module tuong ung (song song) |

## 6. User Commands

| Command | Action |
|---------|--------|
| "hoc hom nay" | Hien thi daily tip + de xuat module (semantic tier) |
| "hoc [module]" | Bat dau/bai tiep theo cua module |
| "progress" / "tien do" | Hien thi LEARNING_PROGRESS.md |
| "skill list" / "danh sach skill" | Liet ke memory/procedural/skills/ |
| "onboard [module]" | Tao learning path cho module moi |
| "tip" | Random tip tu module user thich |
| "quiz [module]" | Cau hoi trac nghiem ve module |
| "hom qua chung ta noi gi" | Load episodic tier ngay gan nhat (rule gotcha: chi khi user hoi) |

## 7. Hermes-like Features Mapping (cap nhat)

| Hermes Agent Feature | SAP Daily Learner Implementation |
|---------------------|--------------------------------|
| Automated Skill Creation | Tu sinh `memory/procedural/skills/<module>-<topic>.md` tu cau tra loi phuc tap |
| Persistent Memory (3-tier) | semantic (default load) + episodic (chat history) + procedural (skills) |
| Multi-Platform Integration | Hoat dong trong Claude Code, co the dispatch qua `sap-ask-consultant` |
| Cron Scheduling | Daily tip moi session dau ngay |
| Self-Improving | Cang hoc cang nhieu skill documents, knowledge graph cang day |
| Training Data Export | Co the export LEARNING_PROGRESS + knowledge graph + skills lam training data |
| Skill Reusability | Skill documents co the dispatch lai cho user khac co cung cau hoi |
| Memory Consolidation | Periodic cleanup episodic (>30 ngay) + archive, KHONG xoa |

## 8. Progressive Learning Paths

### Beginner Path (cho nguoi moi)
```
Tuan 1: MM (procurement co ban) -> PO -> GR -> IR
Tuan 2: SD (sales co ban) -> Sales Order -> Delivery -> Billing
Tuan 3: FI (ke toan co ban) -> GL -> AP -> AR
Tuan 4: CO (controlling co ban) -> Cost Center -> Internal Order
```

### Intermediate Path (cho nguoi da biet SAP)
```
Chon 1 module chuyen sau + 2 module lien quan
Vi du: MM advanced + FI (valuation) + SD (stock transport)
```

### Expert Path (cho chuyen gia)
```
Cross-module integration patterns:
- Order-to-Cash (SD-FI-CO)
- Procure-to-Pay (MM-FI)
- Plan-to-Produce (PP-MM-QM)
- Maintain-to-Close (PM-MM-FI-CO)
- Project-to-Report (PS-SD-CO-FI)
```

## 9. Review Checklist

- [ ] `LEARNING_PROGRESS.md` duoc tao/tim thay (semantic tier)
- [ ] `memory/procedural/skills/` (alias `skills/sap-user-skills/`) ton tai
- [ ] Chi load semantic tier default; episodic/procedural chi load khi user hoi
- [ ] Daily tip phu hop voi level user
- [ ] Skill khong trung lap
- [ ] Module coupling duoc ton trong khi goi y
- [ ] File YAML frontmatter dung format
- [ ] KHONG ghi thong tin da bi vao knowledge_graph (tranh over-engineer)