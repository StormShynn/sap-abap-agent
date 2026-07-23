---
name: sap-tr-cloud
description: Kien thuc TR (Treasury & Cash Management — cash management, bank account management, payment processing, liquidity management, debt management) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong Treasury tren Public Cloud.
effort: medium
model: haiku
---

# TR (Treasury & Cash Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help. **Luu y**: S/4HANA Cloud ho tro **Cash Management**
scope item **BFC**, **Bank Account Management** scope item **BGM**, va **Liquidity Management**
scope item **BFL**. Treasury (cong cu tai chinh, derivatives) co pham vi hep hon on-premise.
Dung ket hop voi skill `sap-extensibility` (bac thang extensibility chung) va `sap-clean-code`
(dat ten).]

## 1. Cau hinh (SSCUI)

| Khu vuc | Scope item | Mo ta |
|---------|-----------|-------|
| Cash Management | **BFC** | Quan ly dong tien: bank statement, cash position, cash concentration |
| Bank Account Management | **BGM** | Quan ly tai khoan ngan hang, hierarchy |
| Liquidity Management | **BFL** | Quan ly thanh khoan: liquidity forecast, planning |
| Thanh toan (Payment) | **2PS** | Payment run, AP/AR payment processing |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Quan ly tai khoan NH | Manage Bank Accounts | FI12 / FI13 |
| Sao ke ngan hang | Import Bank Statements | FF_5 / FF_7 |
| Vi tri tien mat | Cash Position – Company Code | FF7A |
| Du bao dong tien | Liquidity Forecast | FFDL |
| Lenh thanh toan AP | Process Payment Proposals – AP | F110 |
| Lenh thanh toan AR | Process Payment Proposals – AR | F110 |
| Trinh dinh quy | Payment Medium (Check/Wire/Bank Transfer) | F110 + payment medium |
| Hoa gia tri (ZBA) | Manage Zero Balance Accounts | — |
| Phan tich dong tien | Cash Management Overview | — |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| Bank account | `API_BANK_ACCOUNT_SRV` |
| Bank statement | `API_BANK_STATEMENT_SRV` |
| Cash management | CDS view `I_CashManagementOverview`, `I_CashPosition` |
| Liquidity forecast | `API_LIQUIDITY_FORECAST_SRV` |
| Payment medium | `API_PAYMENT_MEDIUM_SRV` |
| Bank | `API_BANK_SRV` |
| CDS views | `I_BankAccount`, `I_BankStatement`, `I_CashManagementOverview` |

## 4. Huong mo rong (extensibility)

- **Custom Fields and Logic** — them field vao bank account / bank statement / cash position.
- Neu can treasury phuc tap (cong cu tai chinh, derivatives, hedge accounting), co the can
  side-by-side BTP hoac SAP Treasury (ba EN).

## 5. Luu y dac thu cho TR tren Public Cloud

- **Cash Management la co ban**: Bank statement, cash position, liquidity forecast — scope BFC/BFL.
  Day la phan co san cho moi khach hang.
- **Bank Account Management**: Scope BGM — quan ly account hierarchy, signatories, bank relationship.
- **Payment**: F110 van co nhung qua Fiori app Process Payment Proposals.
- **Treasury phuc tap**: Derivatives, hedge, loan management co pham vi hep. Can kiem tra tren
  Best Practices Explorer cho release hien tai.
- **Integration**: TR lien ket voi FI (GL bank account), AR/AP (payment processing), SD/MM
  (incoming/outgoing payment), CO (bank charge GL).

## 6. Khi viet/review code ABAP Cloud cho TR

- Doc bank account / bank statement qua released API (`API_BANK_ACCOUNT_SRV`,
  `API_BANK_STATEMENT_SRV`...) hoac CDS view.
- Khong SELECT truc tiep bang chuan (BNKA, REGUH, REGUP, FEBEP, FDZD).
- Payment proposal / payment run doc qua API (khong doc bang REGUH truc tiep).

## 7. Nguon tham khao

- SAP API Business Hub: `https://api.sap.com`
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- [SAP Help Portal — Treasury & Cash Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
