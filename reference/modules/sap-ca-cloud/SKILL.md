---
name: sap-ca-cloud
description: Kien thuc CA (Cross-Application Functions — Business Partner, Document Management (DMS), Workflow, Archiving, Output Management, Number Ranges, reporting framework) cho SAP S/4HANA Cloud Public Edition. Dung khi user hoi ve cac chuc nang dung chung, khong thuoc module cu the.
effort: medium
model: haiku
---

# CA (Cross-Application Functions) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Help. CA la tap hop cac chuc nang ngang, khong phai 1 module nhat
nhieu nhu SD/FI. Moi chuc nang co the thuoc pham vi cua nhieu module khac nhau.]

## 1. Cac chuc nang Cross-Application chinh

### 1.1 Business Partner (BP)

Business Partner la **model duy nhat** cho khach hang, nha cung cap, nhan vien tren Public Cloud.
Khach hang va Supplier deu la BP.

| Fiori app | Legacy cu | Mo ta |
|-----------|-----------|-------|
| Manage Business Partner Master Data | XD01 / XK01 / BP | Tao/sua/xem BP |
| Manage Business Partner Relationships | — | Quan ly quan he giua cac BP |
| Manage Business Partner Roles | — | Gan role cho BP: khach hang, supplier |

**API**: `API_BUSINESS_PARTNER` (OData) — Released API chinh cho BP.

### 1.2 Document Management (DMS)

Quan ly tai lieu (file, ban ve, spec) gan vien vao cac doi tuong (material, equipment, sales order...).

| Fiori app | Legacy cu | Mo ta |
|-----------|-----------|-------|
| Manage Documents | CV01 / CV02 | Tao/sua document info record |
| Document Search | CV04 | Tim kiem tai lieu |
| Document Approval | — | Workflow phe duyet tai lieu |

**API**: `API_DOCUMENT_SRV`, CDS view `I_Document`.

### 1.3 Workflow (SAP Business Workflow)

Phe duyet, thong bao, quy trinh tu dong. Tren Cloud dung **Flexible Workflow** (Fiori app).

| Fiori app | Mo ta |
|-----------|-------|
| Manage Workflows | Dinh nghia workflow template |
| My Inbox | Xu ly cac task phe duyet |
| Monitor Workflows | Theo doi trang thai workflow |

**Note**: Standard Workflows (PO approval, invoice approval) co san theo scope item.

### 1.4 Output Management

Quan ly output (in, email, EDI, fax) cho cac business document.

| Fiori app | Legacy cu | Mo ta |
|-----------|-----------|-------|
| Maintain Output Parameters | NACE | Cau hinh output determination |
| Output Control | — | Kiem soat va gui lai output |
| Manage Output | — | Quan ly output da tao |

**API**: `API_OUTPUT_SRV`.

### 1.5 Archiving / ILM

Quan ly vong doi du lieu, archive, retention.

| Fiori app | Mo ta |
|-----------|-------|
| Manage Archiving Sessions | Chay archive job |
| Data Retention Manager | Cau hinh ILM rules |

### 1.6 Number Ranges

Cau hinh number range (su dung trong SAP Central Business Configuration).

| SSCUI | Mo ta |
|-------|-------|
| Number Range Maintenance | Gan number range cho object: sales order, PO, material... |

### 1.7 Reporting Framework

| Fiori app | Legacy cu | Mo ta |
|-----------|-----------|-------|
| Report Painter / Report Writer | GRR1 / GRW1 | Bao cao tai chinh, chi phi (tuy chon) |
| Custom Analytical Queries | — | CDS-based analytical query |

## 2. Luu y dac thu cho CA tren Public Cloud

- **Business Partner la bat buoc**: Moi doi tac (khach hang, supplier, personnel) deu la BP.
  Khong con phan biet Customer/Vendor master truyen thong.
- **Flexible Workflow**, SAP build workflows (PO, invoice). Standard co. Custom co qua extensibility.
- Output determination = dung **Output Control** Fiori app (thay vi NACE truyen thong).

## 3. Khi viet/review code ABAP Cloud cho CA

- Business Partner doc qua `I_BusinessPartner` CDS view hoac `API_BUSINESS_PARTNER`.
- Documents doc qua `I_Document` CDS view.
- Ouput doc qua `I_Output` CDS view.

## 4. Nguon tham khao

- [SAP Help — Business Partner](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SAP Help — Flexible Workflow](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
- [SAP API Business Hub](https://api.sap.com)
