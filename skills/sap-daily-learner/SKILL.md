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

**Noi luu (`<agent-home>`)**: KHONG phai project/workspace dang mo - plugin nay co the cai va
dung tren bat ky project SAP nao, nen KHONG dung duong dan tuong doi. `<agent-home>` la 1 thu
muc co dinh theo may: mac dinh `%USERPROFILE%\.sap-abap-agent\` (Windows) / `~/.sap-abap-agent/`
(macOS/Linux), override qua `SAP_ABAP_AGENT_HOME` (vd khi dev/test plugin ngay trong repo).
**Buoc 0 - khoi tao (BAT BUOC truoc khi doc file):**
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/bootstrap_memory.py"
```
Script idempotent: lan dau tao toan bo cay memory + LEARNING_PROGRESS.md + knowledge_graph.jsonl; cac lan sau chi skip, KHONG ghi de du lieu dang co.

Khi can them folder/file rieng (vd them skill-moi/ hoac notes/<concept>.md), truyen lap lai:
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/bootstrap_memory.py" \
  --ensure-dir memory/semantic/notes/custom \
  --ensure-file memory/semantic/notes/<concept>.md="# ghi chu"
```
Chi chap nhan duong dan tuong doi nam trong <agent-home>; tuy doi (`C:/Windows/...`) hoac
escape (`../`) se bi tu choi voi exit code 1.

Lay duong dan da resolve bang:
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory
```

```
<agent-home>/memory/
├── episodic/              # Tang 1 - lich su chat (append-only, log raw)
│   ├── 2026-07/
│   │   ├── 2026-07-11_session-001.md   # 1 file / session, gom chat + tool calls
│   │   └── 2026-07-11_session-002.md
│   └── index.jsonl        # append-only: 1 dong / turn (timestamp, session_id, role, brief)
├── semantic/              # Tang 2 - kien thuc da rut trich (file chinh, load default)
│   ├── LEARNING_PROGRESS.md   # module progress, level, mastered topics
│   ├── knowledge_graph.jsonl  # entity: concept/module/topic; relationship
│   ├── lessons/               # ACE-style lesson card, 1 file/module - xem muc 1
│   │   ├── FI.jsonl
│   │   └── MM.jsonl
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

### File chinh: `<agent-home>/memory/semantic/LEARNING_PROGRESS.md`

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

### Lesson Cards (ACE-style) — extraction + retrieval, bo sung cho Knowledge Graph

Khac voi Knowledge Graph (entity/relationship, on dinh, it thay doi), **Lesson Card** la 1
fact/kinh nghiem ngan (1-3 dong) rut ra tu 1 lan giai quyet van de cu the — itemized, khong phai
tong hop lai toan bo skill (tranh "context collapse": ghi de/tom tat lai toan bo lam mat kien thuc
cu). Pattern tu ACE (arXiv 2510.04618) — merge tang dan (deterministic, append-or-skip-duplicate),
khong bao gio wholesale-rewrite 1 file lesson.

**Luu tru**: `<agent-home>/memory/semantic/lessons/<MODULE>.jsonl` (1 file/module, moi dong 1
lesson card). Script: `reference/scripts/lesson_card_add.py` (them, tu dong bo qua neu trung —
Jaccard similarity >= 0.8 tren cung topic) va `reference/scripts/lesson_card_retrieve.py` (truy
xuat top-K). `<memory-root>` trong 2 lenh duoi day = `<agent-home>/memory/semantic`. Moi lenh
Bash co the la 1 shell moi (shell state KHONG persist giua cac lan goi Bash) nen phai tu resolve
`<memory-root>` ngay trong lenh, KHONG dua vao bien da set o lenh truoc:
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/semantic
```

**Khi nao extract 1 lesson card** (khong phai moi cau tra loi — chi khi co gia tri tai su dung):
- Cau tra loi dai (>5 turn) VA co ket luan cu the (khong phai chi giai thich chung chung).
- `sap-systematic-debugging` resolve xong 1 bug — extract dang "truoc day loi X do Y, fix la Z"
  (failure-driven extraction).
- User phai hoi lai lan 2 cung 1 van de trong session khac — dau hieu lan dau chua luu lai kien
  thuc dung cho.

**Cach extract** (Claude tu lam, KHONG phai script — day la judgment task, khong the tu dong hoa):
1. Tom tat fact thanh 1-3 dong, tu ngu cu the (ten field/API/SSCUI that, khong noi chung chung).
2. Xac dinh `module` + `topic` (topic la slug ngan, vd `acdoca`, `clearing`, khong phai ca cau).
3. Neu fact gan voi 1 SAP release cu the (vd hanh vi chi dung o release 2502) — dat `valid_until`
   la ngay uoc tinh release do het support/bi thay (tranh fact cu "poison" context sau khi SAP ra
   ban moi — SAP ra ~4 ban/nam).
4. Goi:
   ```bash
   echo '{"module":"FI","topic":"acdoca","fact":"...","source_session":"<session_id>","valid_until":"2027-01-01"}' \
     | python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/lesson_card_add.py" \
       "$(python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/semantic)"
   ```

**Cach retrieve** (truoc khi tra loi cau hoi thuoc module da co lesson card):
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/lesson_card_retrieve.py" \
  "$(python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" memory/semantic)" \
  FI "cau hoi user" --top-k 5
```
Script tu dong: loai fact het han (`valid_until` da qua — khong tra ve), diem theo
`0.5*keyword_overlap + 0.3*recency + 0.2*usage_frequency`, **bat buoc co it nhat 1 tu khoa trung**
(recency/usage khong the tu dua 1 fact khong lien quan len top — phat hien va fix qua thuc te
test truoc khi dung), va tu tang `usage_count` + `last_used` cho card duoc tra ve.

**Vi sao khong dung Mem0/Zep/Letta**: plugin nay uu tien **khong them dependency ngoai** (khong
vector store, khong service rieng) de giu dung trai nghiem cai dat "1 lenh pip install" hien tai.
Neu sau nay can temporal knowledge graph phuc tap hon (nhu Zep/Graphiti), co the danh gia lai —
hien tai JSONL + scoring script la du cho quy mo plugin.

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

File `<agent-home>/memory/episodic/<YYYY-MM>/<YYYY-MM-DD>_session-<id>.md`
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

- [ ] `bootstrap_memory.py` da chay (Buoc 0) truoc khi doc semantic tier - tranh loi
      "Failed to check existing learning progress and knowledge graph" khi first-run
- [ ] `LEARNING_PROGRESS.md` duoc tao/tim thay (semantic tier)
- [ ] `memory/procedural/skills/` (alias `skills/sap-user-skills/`) ton tai
- [ ] Chi load semantic tier default; episodic/procedural chi load khi user hoi
- [ ] Daily tip phu hop voi level user
- [ ] Skill khong trung lap
- [ ] Module coupling duoc ton trong khi goi y
- [ ] File YAML frontmatter dung format
- [ ] KHONG ghi thong tin da bi vao knowledge_graph (tranh over-engineer)
- [ ] Lesson card (neu extract) da qua `lesson_card_add.py` — KHONG ghi tay vao `.jsonl`
- [ ] Lesson card gan release cu the co dat `valid_until`
- [ ] Truoc khi tra loi cau hoi module da co lesson — da goi `lesson_card_retrieve.py` truoc