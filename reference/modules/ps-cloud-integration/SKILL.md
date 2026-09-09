---
name: ps-cloud-integration
description: Knowledge note tổng hợp **PS (Project System) trên S/4HANA Cloud** + pattern tích hợp với CO/FI/PM/SD. Khác với `sap-ps-cloud/SKILL.md` (seed knowledge consultant PS). Dùng khi cần quyết định dùng PS hay không, hoặc khi scaffold project integration.
effort: low
model: haiku
---

# PS (Project System) — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **PS trên S/4HANA Cloud Public Edition** và integration
patterns với CO/FI/PM/SD/PP. Không thay thế:
- `sap-ps-cloud/SKILL.md` — knowledge consultant PS.
- `sap-ps-consultant-cloud` — agent consult thật.

## 1. PS trên Cloud — status

| Chức năng                | Status (S/4HANA Cloud Public Edition) |
|---------------------------|----------------------------------------|
| Project / WBS element     | ✅ Có (qua Fiori apps)                 |
| Network / Activity        | ✅ Có                                   |
| Milestone                 | ✅ Có                                   |
| Project planning (Gantt)  | Limited — chủ yếu qua Fiori            |
| Project settlement        | ✅ Có                                   |
| Project reporting         | ✅ Có (qua Fiori + SAC)                |
| PS classic on-prem features| ❌ Nhiều tính năng on-prem không có    |

**So với on-prem**: PS trên Cloud bị giới hạn nhiều (đặc biệt custom development, PS user-exits,
project versions). Với dự án lớn cần custom nặng, đánh giá dùng **BTP Steampunk** (RAP) hoặc
**third-party** (Oracle Primavera, MS Project Online).

## 2. PS architecture trên Cloud

```
Project (PRJ)
  └─ WBS Element (hierarchy)
       ├─ Network (NET)
       │    └─ Activity (ACT)
       │         └─ Material/Service component
       └─ Milestone (MS)
```

- **Project definition** (`PROJ`): root.
- **WBS element** (`PRPS`): work breakdown — phân cấp tùy ý.
- **Network** (`VBELN`-like): activity network cho task execution.
- **Activity** (`AFVV`-like): smallest unit of work, có thể gán cost/plan hours.
- **Milestone**: event marker trên WBS hoặc network.

## 3. Integration với CO (Controlling)

| Luồng                         | Vai trò PS               | Vai trò CO               |
|-------------------------------|--------------------------|--------------------------|
| Cost planning                 | PS plan cost             | CO tổng hợp              |
| Actual cost posting           | PS ghi nhận actual       | CO cost element          |
| Settlement                    | PS settlement rule       | CO settlement receiver   |
| Result analysis               | PS WBS element           | CO-PA profitability      |

## 4. Integration với FI (Financial Accounting)

- **Down payment**: PS tạo down payment request → FI vendor down payment.
- **Vendor invoice**: PS gắn vendor invoice vào WBS/network.
- **Asset settlement**: PS WBS settle sang FI Asset (qua settlement rule).

## 5. Integration với PM (Plant Maintenance)

PM order có thể **assign vào PS project / WBS**:

```
Project
  └─ WBS Element (PS)
       └─ Network
            └─ Maintenance Order (PM)
                 └─ Activity / Material component
```

Khi đó:
- Cost của PM order tính vào WBS.
- Settlement cuối kỳ từ PM sang PS hoặc ngược lại.

## 6. Integration với SD (Sales)

- **Sales order với project reference**: SD tạo SO có tham chiếu project → billing dựa trên PS.
- **Billing plan** theo milestone: SD billing dựa trên PS milestone achieved.

## 7. Integration với PP (Production Planning)

- **Production order gắn vào PS**: cost của production order tính vào project.
- **MRP chạy theo project**: PS tạo planned order → PP convert sang production order.

## 8. Common Fiori apps

| Chức năng                  | Fiori app                                  |
|----------------------------|--------------------------------------------|
| Manage Projects            | Manage Projects                             |
| WBS Element                | Manage WBS Elements                         |
| Network / Activity         | Manage Networks / Manage Activities         |
| Milestone                  | Manage Milestones                           |
| Settlement                 | Project Settlement                          |
| Reporting                  | Project Cost Reports / Project Progress     |

## 9. Side-by-side Extension Patterns

| Pattern                    | Dùng khi                              | Tool                |
|----------------------------|----------------------------------------|---------------------|
| Custom field trên WBS      | Thêm business info                     | SSCUI Custom Field  |
| Custom settlement logic    | Rule settlement riêng                 | ABAP Cloud BAdI     |
| Custom milestone workflow  | Approval milestone custom              | SAP Build           |
| Project dashboard          | Custom analytics                       | SAP Analytics Cloud |
| Mobile time entry          | Activity time tracking                 | SAP Build           |

## 10. Anti-pattern

- ⚠️ Dùng PS classic transaction (`CJ20N`, `CN21`...) trên Cloud — không released, dùng Fiori.
- ⚠️ Tạo project version cũ (chỉ on-prem) — không có trên Cloud.
- ⚠️ Dùng PS user-exit (on-prem) — chuyển sang Cloud BAdI hoặc extension field.
- ⚠️ Hardcode project ID trong code — dùng input parameter.
- ⚠️ Skip settlement cuối dự án — sẽ không đóng được cost.

## 11. Liên kết với các skill khác

- **Consultant**: `sap-ps-consultant-cloud`.
- **Seed knowledge**: `sap-ps-cloud/SKILL.md`.
- **Integration**: `sap-co-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-pm-consultant-cloud`,
  `sap-sd-consultant-cloud`, `sap-pp-consultant-cloud`.
- **BTP architecture**: `sap-btp-connectivity`.

## 12. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module PS.
- [`marcellourbani/vscode_abap_remote_fs`](https://github.com/marcellourbani/vscode_abap_remote_fs)
  — extension pattern cho PS + RAP.
- SAP Help: Project System trên S/4HANA Cloud Public Edition.
