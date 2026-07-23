---
name: hcm-cloud-integration
description: Knowledge note tổng hợp **HCM (Human Capital Management) + SuccessFactors** — kiến trúc hybrid, integration patterns với FI/CO/PM, luồng employee data. Khác với `sap-hcm-cloud/SKILL.md` (seed consultant) và SuccessFactors consultant agent.
effort: low
model: haiku
---

# HCM + SuccessFactors — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **kiến trúc HCM trên Cloud** (HCM on-prem vs SuccessFactors
vs hybrid). Không thay thế:
- `sap-hcm-cloud/SKILL.md` — seed knowledge HCM consultant.
- `sap-successfactors-cloud/SKILL.md` — seed knowledge SuccessFactors consultant.
- `sap-hcm-consultant-cloud`, `sap-successfactors-consultant-cloud` — agents consult thật.

## 1. Tổng quan: HCM có mấy variant trên Cloud?

| Variant                              | Status                  | Use case                          |
|--------------------------------------|-------------------------|-----------------------------------|
| **SAP HCM on-prem / S/4HANA Private Cloud** | Còn dùng (legacy) | Đã có HCM, chưa migrate           |
| **SAP SuccessFactors Employee Central (EC)** | Active (cloud)    | New implementation, full SaaS HR   |
| **Hybrid — SuccessFactors EC + on-prem payroll** | Common          | Multi-country, transition phase   |

**Lưu ý quan trọng**: Public Cloud S/4HANA **không có HCM embedded**. HR data phải đến từ
SuccessFactors (qua integration) hoặc từ hệ thống bên ngoài.

## 2. Kiến trúc Hybrid (SuccessFactors + S/4HANA Cloud)

```
┌──────────────────────────────────────────┐
│ SuccessFactors Employee Central (BTP)   │
│ - Employee master                       │
│ - Time-off / Time sheet                 │
│ - Recruiting / Onboarding               │
│ - Performance / Learning                │
└──────────────────────────────────────────┘
                ↕ (Integration Suite / Boomi / SAP HCI)
┌──────────────────────────────────────────┐
│ S/4HANA Cloud (Finance / Logistics)     │
│ - Cost center / WBS gắn employee ID     │
│ - Project time recording                │
│ - Finance posting                       │
└──────────────────────────────────────────┘
```

## 3. Employee Data Replication

| Field                      | Source                            | Sync to S/4HANA?   |
|----------------------------|------------------------------------|---------------------|
| Employee ID                | SuccessFactors Employee Central   | ✅ (qua integration) |
| Personal data (name, dob)  | SuccessFactors                    | Partial             |
| Address / Phone / Email    | SuccessFactors                    | ✅                   |
| Cost center assignment     | SuccessFactors + on-prem          | ✅                   |
| Manager hierarchy          | SuccessFactors                    | ✅                   |
| Bank details               | SuccessFactors                    | ✅ (qua EC Payroll) |
| Compensation / Salary      | EC Payroll hoặc on-prem payroll   | Limited              |
| Time records               | SuccessFactors Time Sheet          | ✅ cho project      |

## 4. Integration với FICO (Finance)

- **Cost center assignment**: employee org unit → cost center trong FICO.
- **Travel expense**: employee nộp expense → FI trả tiền về bank account SF.
- **Vendor master linking**: employee ID link sang vendor master cho one-time payment.

## 5. Integration với PM (Plant Maintenance)

- **Maintenance worker**: PM order gắn personnel number → check valid qua SF.
- **Capacity planning**: PM lấy availability từ SF Time Sheet.

## 6. Integration với PS (Project System)

- **Project time sheet**: employee ghi giờ vào project/WBS/activity → sync về S/4HANA → tính cost.
- **Network activity performer**: person gắn vào network activity.

## 7. Integration với SD/MM (Approver)

- **Approval workflow**: PR/PO/SO dùng manager hierarchy từ SF làm approver.
- **Substitution rule**: dùng SF substitution cho approval khi manager vắng mặt.

## 8. Common Integration Tools

| Tool                                          | Mục đích                              |
|-----------------------------------------------|----------------------------------------|
| **SAP Integration Suite** (BTP)               | Pre-built integration content for SF   |
| **SAP Boomi**                                 | Third-party iPaaS                       |
| **SAP SuccessFactors Employee Central Payroll**| Payroll engine                           |
| **MDF (Meta Data Framework)**                 | Custom field trong SF                   |
| **Integration Center** (BizX)                 | SF integration user interface           |

## 9. Fiori apps (cho user)

| Chức năng                  | Fiori app                                |
|----------------------------|------------------------------------------|
| Time recording             | My Timesheet / Record Working Times       |
| Leave request              | My Time Off / Request Time Off            |
| Travel expense             | Manage Travel Expenses                   |
| Approvals (PR/PO/leave)    | My Inbox                                 |
| Org chart                  | Company Directory                        |

## 10. Side-by-side Extension Patterns

| Pattern                    | Dùng khi                              | Tool                |
|----------------------------|----------------------------------------|---------------------|
| Custom field trên MDF       | Thêm business info trong SF             | MDF (no-code)        |
| Custom integration scenario | Luồng SF ↔ S/4HANA custom              | Integration Suite    |
| Custom approval workflow    | Multi-level approval riêng              | SAP Build            |
| Employee portal            | Self-service custom                    | SAP Build Work Zone  |

## 11. Anti-pattern

- ⚠️ Sync toàn bộ compensation data S/4HANA Cloud — không cần (chỉ sync EC Payroll output).
- ⚠️ Hardcode employee ID trong code — luôn qua input field.
- ⚠️ Skip manager hierarchy update — cascade phê duyệt sai.
- ⚠️ Dùng HCM transaction on-prem (`PA30`, `PT60`) từ Cloud — không released.
- ⚠️ Lưu personal data nhạy cảm trong custom table — GDPR/PII risk.

## 12. Liên kết với các skill khác

- **Consultant**: `sap-hcm-consultant-cloud`, `sap-successfactors-consultant-cloud`.
- **Seed knowledge**: `sap-hcm-cloud/SKILL.md`, `sap-successfactors-cloud/SKILL.md`.
- **Integration**: `sap-co-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-pm-consultant-cloud`,
  `sap-ps-consultant-cloud`, `sap-cpi-consultant-cloud` (integration rất quan trọng).
- **BTP architecture**: `sap-btp-connectivity`, `sap-btp-admin-consultant-cloud`.

## 13. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module SF + HCM.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)
  — pattern consume SF OData.
- SAP Help: SAP SuccessFactors Employee Central, Hybrid integration guides.
