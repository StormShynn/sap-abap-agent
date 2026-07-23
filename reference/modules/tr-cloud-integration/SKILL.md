---
name: tr-cloud-integration
description: Knowledge note tổng hợp **TR (Treasury & Risk Management)** trên Cloud — kiến trúc, integration với FI/CO, bank connectivity. Khác với `sap-tr-cloud/SKILL.md` (seed consultant) và `sap-tr-consultant-cloud`.
effort: low
model: haiku
---

# TR (Treasury) — Cloud Integration Knowledge Note

Module con của plugin, tập trung vào **kiến trúc SAP Treasury & Risk Management** trên
S/4HANA Cloud. Không thay thế:
- `sap-tr-cloud/SKILL.md` — seed knowledge TR consultant.
- `sap-tr-consultant-cloud` — agent consult thật.

## 1. TR trên Cloud có mấy variant?

| Variant                                              | Status               | Use case                  |
|------------------------------------------------------|----------------------|---------------------------|
| **Treasury embedded trong S/4HANA Cloud Public Edition** | Limited (basic only) | Cash management đơn giản  |
| **SAP Treasury & Risk Management on S/4HANA Private Cloud** | Active       | Full TR (most common)     |
| **FSCM (Legacy on-prem)**                           | Maintenance          | Đã có sẵn, Banking services|

**Quan trọng**: Public Cloud **chỉ có cash management** cơ bản. Full Treasury (cash
positioning, in-house bank, liquidity planning, hedge accounting, market risk) cần
**Private Cloud** hoặc legacy on-prem.

## 2. Cash Management (cả Public & Private Cloud)

```
┌────────────────────────────────────────────────┐
│ Cash Management                                │
│ - Cash Position (real-time)                     │
│ - Liquidity Forecast                            │
│ - Bank Account Management                       │
│ - Cash Flow Analyzer                            │
└────────────────────────────────────────────────┘
                    ↕ (Bank integration)
┌────────────────────────────────────────────────┐
│ Banks (qua SAP Multi-Bank Connectivity)         │
│ - SWIFT, EBICS (German), HOST-TO-HOST           │
│ - 100+ banks worldwide                          │
└────────────────────────────────────────────────┘
```

## 3. Full Treasury (chỉ Private Cloud)

| Sub-module                     | Mục đích                              |
|--------------------------------|----------------------------------------|
| **Cash & Liquidity Management**| Cash positioning, short-term forecasting |
| **In-House Bank (Cash Concentration)** | Cash pooling giữa entities         |
| **Treasury & Risk (Deal Management)** | FX deal, IR deal, commodity deal      |
| **Hedge Accounting & Hedge Management** | IFRS 9 / ASC 815 hedge accounting      |
| **Market Risk Analyzer**        | VaR, stress testing                    |
| **Credit Risk Analyzer**       | Counterparty exposure                   |
| **Investment Management**       | Securities portfolio                    |
| **Debt & Capital Management**   | Loan portfolio                         |

## 4. Integration với FI

| Luồng                         | Vai trò TR                | Vai trò FI            |
|-------------------------------|---------------------------|-----------------------|
| Bank statement upload         | TR reconcile cash position| FI post bank subledger |
| Incoming payment               | TR cash position update   | FI clear customer/vendor|
| Outgoing payment               | TR cash position forecast | FI post vendor payment |
| FX deal booking               | TR manage FX exposure     | FI valuation posting   |
| Hedge accounting              | TR designate hedging relationship | FI accounting booking |

## 5. Integration với CO

- **Cost of capital** cho investment decision (multi-currency).
- **Profit center / segment reporting** cho FX gain/loss.

## 6. Integration với Bank (Multi-Bank Connectivity)

```
Bank Communication Mgmt
  ├─ SWIFT MT940/950/103 (international)
  ├─ EBICS (Germany)
  ├─ HOST-TO-HOST (proprietary)
  ├─ File-based (local bank format)
  └─ API (modern banks)
```

SAP Multi-Bank Connectivity (MBC) là cloud service của SAP giúp kết nối bank mà không cần
implement từng protocol.

## 7. Common Fiori apps

| Chức năng                  | Fiori app                                |
|----------------------------|------------------------------------------|
| Cash Position               | Cash Position                            |
| Liquidity Forecast          | Liquidity Planner                        |
| Bank Account Management     | Bank Account Management                  |
| Cash Flow Analyzer          | Cash Flow Analyzer                       |
| Manage Deal                 | Treasury Deal Worklist                   |
| Hedge Accounting            | Hedge Accounting Worklist                |

## 8. Side-by-side Extension Patterns

| Pattern                        | Dùng khi                              | Tool                |
|--------------------------------|----------------------------------------|---------------------|
| Custom cash forecast rule      | Logic business riêng                   | Cloud BAdI          |
| Custom bank integration        | Bank ngoài SAP MBC                     | BTP + CPI           |
| Treasury dashboard             | CFO real-time view                     | SAP Analytics Cloud |
| Approval workflow              | Multi-level deal approval              | SAP Build           |

## 9. Anti-pattern

- ⚠️ Dùng Treasury on-prem cho Public Cloud project — không compatible.
- ⚠️ Manual FX deal entry thay vì automate — dễ sai với hedge accounting.
- ⚠️ Không đối chiếu bank statement hàng ngày — mất control cash position.
- ⚠️ Skip hedge accounting test — IFRS 9 / ASC 815 audit fail.
- ⚠️ Lưu bank detail nhạy cảm (IBAN, BIC) trong custom table — PCI/PII risk.

## 10. Liên kết với các skill khác

- **Consultant**: `sap-tr-consultant-cloud`.
- **Seed knowledge**: `sap-tr-cloud/SKILL.md`.
- **Integration**: `sap-fi-consultant-cloud`, `sap-co-consultant-cloud`, `sap-cpi-consultant-cloud`.
- **BTP architecture**: `sap-btp-connectivity`.

## 11. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module TR.
- [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)
  — pattern bank integration qua OData.
- SAP Help: SAP Treasury and Risk Management documentation.
- SAP Multi-Bank Connectivity (MBC) docs.
