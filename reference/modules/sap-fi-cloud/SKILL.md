---
name: sap-fi-cloud
description: Kien thuc FI (Financial Accounting — General Ledger/Universal Journal, AP, AR, Asset) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong dung cho khi viet/review code ABAP Cloud lien quan ke toan tai chinh. Dung khi user hoi ve cau hinh/tich hop/mo rong FI tren Public Cloud.
effort: medium
model: haiku
---

# FI (Financial Accounting) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community (xem Nguon tham khao); so SSCUI/API cu the thay doi
theo tung release quy, luon nhac user xac minh lai. Dung ket hop voi skill
`sap-extensibility` va `sap-clean-code`.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI | Mo ta |
|---|---|---|
| Chuyen & sap xep cong no phai thu/phai tra | 100297 | Financial Accounting → General Ledger Accounting → Transfer and Sort Receivables and Payables |
| Profit center mac dinh cho tai khoan doi ung | 102529 | Kiem soat co tach profit center cho tai khoan clearing ngan hang/company code hay khong |

**Ledger**: So luong ledger va chuan ke toan ap dung (local GAAP / IFRS song song) la quyet dinh mang
tinh cau truc, thuong chi thay doi giai doan dau trien khai — coi bat ky yeu cau doi ledger/nguyen
tac ke toan sau go-live la rui ro cao, can xac minh quy trinh SSCUI hien hanh truoc khi tu van.

Chi co **Universal Journal (ACDOCA)** — khong co khai niem "new G/L vs classic G/L" can kiem tra nhu
mot so he thong khac; ACDOCA la mo hinh GL duy nhat.

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app |
|---|---|
| Hach toan but toan GL | Post General Journal Entry |
| Tong quan chung tu / quy trinh AP | Display Process Flow – Accounts Payable |
| Doi tac kinh doanh (khach hang/nha cung cap) | Manage Business Partner Master Data (Business Partner la model duy nhat) |
| Clear tai khoan GL | Clear G/L Account |
| Bao cao Balance Sheet / P&L | Balance Sheet & P&L Statement (drill duoc toi dong GL/khach hang/nha cung cap) |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra ten/version chinh xac tren `api.sap.com` truoc khi dung) |
|---|---|
| Doc/ghi journal entry | Journal Entry API tren ACDOCA (xac nhan ten/version hien hanh) |
| Doi tac kinh doanh | `API_BUSINESS_PARTNER` |
| Hach toan chung tu ke toan | Successor duoc release cho cloud cua BAPI hach toan co dien — xac minh truoc khi dung, dung mac dinh BAPI ECC van goi duoc |

**Luu y**: FI la khu vuc de nham nhat vi ACDOCA nghe quen thuoc — nhung tren Public Cloud **khong co
cach doc bang truc tiep**, moi so lieu deu phai qua released API/CDS view API hoac Fiori app.

## 4. Huong mo rong (extensibility) cho FI

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho FI:
- **Custom Fields and Logic** — them field vao journal entry line item / G/L account master / doi tuong chi phi, kem logic derive don gian.
- **Custom Business Objects** — hiem khi can cho FI (da so nhu cau la them field/logic vao doi tuong co san, khong phai tao doi tuong hoan toan moi).
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho hook hach toan/validation truoc khi ket luan can side-by-side.
- Khi yeu cau nghe giong "can 1 rule validate luc hach toan" — kiem tra Custom Logic/Cloud BAdI truoc, khong mac dinh mo ta theo huong validation/substitution kieu cu.

## 5. Khi viet/review code ABAP Cloud cho FI

- Doi tuong custom lien quan FI van theo naming convention chung o `sap-clean-code`.
- Doc du lieu journal entry/business partner qua released CDS view API (`I_JournalEntryItem`,
  `I_BusinessPartner`...), khong SELECT truc tiep vao ACDOCA hay bang chuan khac.
- Truoc khi de xuat 1 sub-ledger hay bao cao ke toan rieng, xac dinh ro day la Custom Field/Custom
  Business Object (khong can dev) hay can 1 RAP BO/side-by-side (can dev).

## 6. Nguon tham khao

- [SAP S/4HANA Cloud Public Edition - Finance-General Ledger Accounting FAQ](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/sap-s-4hana-cloud-public-edition-finance-general-ledger-accounting/ba-p/13721608)
- [Ledger Configuration in SAP S/4HANA Public Edition — SAP Community](https://community.sap.com/t5/financial-management-blog-posts-by-sap/ledger-configuration-in-sap-s-4hana-public-edition-find-essential/ba-p/14250655)
- [These Fiori apps will get your financial accounting on track](https://www.ibsolution.com/academy/blog_en/smart-enterprise/sap-s4hana/these-fiori-apps-will-get-your-financial-accounting-on-track)
- SAP API Business Hub: `https://api.sap.com`
