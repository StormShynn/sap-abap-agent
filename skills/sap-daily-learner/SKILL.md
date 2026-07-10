---
name: sap-daily-learner
description: Skill tu dong hoa viec hoc SAP/ABAP moi ngay — tu dong tao skill, track tien do, goi y noi dung dua trinh do nguoi dung. Lay cam hung tu Hermes Agent (Nous Research).
effort: high
model: sonnet
---

# SAP Daily Learner — Skill Implementation

## 1. Persistent Knowledge Store

### File: `.sap-abap-agent/LEARNING_PROGRESS.md`

File nay duy tri trang thai hoc tap cua user. Cau truc:

```markdown
# 📚 SAP Learning Progress

Last updated: 2026-07-11
Session count: 1
Total skills created: 0

## Module Progress

| Module | Level | Topics Mastered | Topics Pending | Last Activity |
|--------|-------|----------------|----------------|---------------|
| SD | beginner | 0 | 5 | never |
| FI | beginner | 0 | 5 | never |
| MM | beginner | 0 | 5 | never |
| CO | beginner | 0 | 5 | never |
| PP | beginner | 0 | 5 | never |

## Recommended Next Module
> **Mới bắt đầu? Hãy học MM (Materials Management)** — module phổ biến nhất, dễ tiếp cận với quy trình procurement hàng ngày.

## Auto-Created Skills
*(chưa có skill nào)*
```

### Module Knowledge Matrix — Nội dung học cho từng module

Mỗi module có 5 topics, 3 levels:

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
1. Read LEARNING_PROGRESS.md
2. Find modules with lowest "Topics Mastered" count
3. Pick next topic from "Topics Pending" for that module
4. Determine user level from Module Progress
5. Generate appropriate tip template based on level
```

### Scheduling cơ chế

- **Mỗi session đầu tiên trong ngày**: Hiển thị 1 daily tip
- **Sau mỗi 3 câu hỏi được giải đáp**: Gợi ý 1 bài tập ngắn
- **Khi user hỏi "học gì hôm nay"**: Đề xuất learning path cá nhân hóa

## 3. Auto-Skill Creation Engine

### Trigger conditions

Tự động tạo skill khi:

1. **Problem complexity ≥ 3 steps**: Vấn đề cần ≥ 3 bước giải quyết
2. **Có cấu hình cụ thể**: Có SSCUI / Fiori app / API được đề cập
3. **User response positive**: User nói "cảm ơn", "hữu ích", "được rồi", "got it", "great"
4. **Không trùng lặp**: Kiểm tra `skills/sap-user-skills/` không có file tương tự

### Skill storage

- **Thư mục**: `skills/sap-user-skills/`
- **Naming**: `<module>-<topic-slug>.md` (vd: `mm-purchase-order-approval.md`)
- **Format**: YAML frontmatter + markdown content

### Ví dụ skill được tạo tự động:

```markdown
---
name: mm-purchase-order-approval
description: Hướng dẫn cấu hình approve workflow cho purchase order trên S/4HANA Cloud Public Edition
created: 2026-07-11
source: "User hỏi: làm sao để PO cần approval trước khi gửi supplier?"
tags: [MM, PO, workflow, approval, SSCUI]
---

# Purchase Order Approval Workflow

## Problem
PO cần được phê duyệt trước khi gửi supplier. Không có workflow mặc định.

## Solution

### Bước 1: Kích hoạt scope item
- Scope item: **BNS** (Operational Procurement)
- App: Manage Your Solution → check BNS đã active

### Bước 2: Cấu hình Release Strategy
- SSCUI: **101122** (Define Release Strategy for Purchasing Documents)
- Điều kiện: dựa trên giá trị PO (>= 5000 USD cần approve)

### Bước 3: Gán người phê duyệt
- SSCUI: **101123** (Assign Release Codes)
- Gán user/role cho từng release code

### Bước 4: Test
- Fiori app: Manage Purchase Orders → tạo PO > 5000 → kiểm tra status "To be released"

## SSCUI / Fiori App
- SSCUI 101122: Define Release Strategy for Purchasing Documents
- SSCUI 101123: Assign Release Codes
- Fiori: Manage Purchase Orders

## API (nếu có)
- `API_PURCHASEORDER_PROCESS_SRV`
- `API_RELEASESTRATEGY_SRV`

## Notes
- Release strategy cần active trước khi PO được tạo
- Có thể kết hợp nhiều điều kiện (value + material group)
- Phiên bản 2502+ có thêm condition "document type"
```

## 4. Tích hợp với sap-ask-consultant

Thêm daily-learner vào module routing:

| Trigger keywords | Dispatch |
|-----------------|----------|
| "hoc", "học", "learning", "daily", "tip", "bài tập", "lộ trình", "progress", "hermes" | `sap-daily-learner` |
| "hoc SD", "hoc FI", "hoc MM"... | `sap-daily-learner` + module tương ứng (song song) |

## 5. User Commands

| Command | Action |
|---------|--------|
| "hoc hom nay" | Hiển thị daily tip + đề xuất module |
| "hoc [module]" | Bắt đầu/bài tiếp theo của module |
| "progress" / "tien do" | Hiển thị LEARNING_PROGRESS.md |
| "skill list" / "danh sach skill" | Liệt kê skills/user-skills/ |
| "onboard [module]" | Tạo learning path cho module mới |
| "tip" | Random tip từ module user thích |
| "quiz [module]" | Câu hỏi trắc nghiệm về module |

## 6. Hermes-like Features Mapping

| Hermes Agent Feature | SAP Daily Learner Implementation |
|---------------------|--------------------------------|
| Automated Skill Creation | Tự sinh `skills/user-skills/<module>-<topic>.md` từ câu trả lời phức tạp |
| Persistent Memory | `LEARNING_PROGRESS.md` — module progress, mastered topics |
| Multi-Platform Integration | Hoạt động trong Claude Code, có thể dispatch qua `sap-ask-consultant` |
| Cron Scheduling | Daily tip mỗi session đầu ngày |
| Self-Improving | Càng học càng nhiều skill documents, knowledge base càng phong phú |
| Training Data Export | Có thể export LEARNING_PROGRESS + skill documents làm training data |
| Skill Reusability | Skill documents có thể dispatch lại cho user khác có cùng câu hỏi |

## 7. Progressive Learning Paths

### Beginner Path (cho người mới)
```
Tuần 1: MM (procurement cơ bản) → PO → GR → IR
Tuần 2: SD (sales cơ bản) → Sales Order → Delivery → Billing
Tuần 3: FI (kế toán cơ bản) → GL → AP → AR
Tuần 4: CO (controlling cơ bản) → Cost Center → Internal Order
```

### Intermediate Path (cho người đã biết SAP)
```
Chọn 1 module chuyên sâu + 2 module liên quan
Ví dụ: MM advanced + FI (valuation) + SD (stock transport)
```

### Expert Path (cho chuyên gia)
```
Cross-module integration patterns:
- Order-to-Cash (SD-FI-CO)
- Procure-to-Pay (MM-FI)
- Plan-to-Produce (PP-MM-QM)
- Maintain-to-Close (PM-MM-FI-CO)
- Project-to-Report (PS-SD-CO-FI)
```

## 8. Review Checklist

- [ ] `LEARNING_PROGRESS.md` được tạo/tìm thấy
- [ ] `skills/sap-user-skills/` thư mục tồn tại
- [ ] Daily tip phù hợp với level user
- [ ] Skill không trùng lặp
- [ ] Module coupling được tôn trọng khi gợi ý
- [ ] File YAML frontmatter đúng format
