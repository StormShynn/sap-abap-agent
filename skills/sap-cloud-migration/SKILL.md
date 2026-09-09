---
name: sap-cloud-migration
description: Huong dan migration code ABAP tu on-prem/ECC len SAP S/4HANA Cloud Public Edition va BTP ABAP Environment (Steampunk) — Clean Core strategy, ATC check, released API replacement, code adaptation.
when_to_use: |
  "migration code len cloud", "chuyen ECC len S/4HANA cloud", "Clean Core migration",
  "ATC fix cho cloud", "thay the BAPI/report cung bang released API".
argument-hint: "[cau hoi ve migration / cloud readiness / code adaptation]"
effort: high
model: sonnet
---

# ABAP Cloud Migration Guide

## 1. Clean Core — 3 Tren Extensibility

Khi migration len S/4HANA Cloud Public Edition, **Clean Core** la bat buoc. Khong the modify standard
SAP object. Moi custom code phai o mot trong 3 tang:

```
┌─────────────────────────────────────┐
│  Tang 1: Key User Extensibility     │ ← SSCUI, Custom Fields, Cloud BAdI
├─────────────────────────────────────┤
│  Tang 2: Developer On-Stack         │ ← ABAP Cloud trong tenant dev (3-system)
├─────────────────────────────────────┤
│  Tang 3: Side-by-Side BTP           │ ← CAP/RAP tren BTP, goi S/4HANA APIs
└─────────────────────────────────────┘
```

## 2. ATC Check — Buoc Dau Tien

Truoc khi migration, chay ATC check tren code cua ban:

```bash
# Run ATC check
ATC_CHECK_PROGRAM → Input program/class → Run
# Hoac chay hang loat:
ATC_MAINTENANCE → Create checkpoint group → Run all custom code
```

### Cac loai loi ATC thuong gap

| Ma loi | Loai | Mo ta |
|--------|------|-------|
| `CLOUD_READINESS` | Error | Object chua released cho cloud |
| `CLOUD_READINESS_W` | Warning | Cu phap bi cam trong ABAP Cloud |
| `USE_RELEASED_OBJECT` | Error | Dung class/interface chua release |
| `USE_RELEASED_API` | Error | Dung BAPI/function module chua release |
| `SELECT_FROM_BANNED_TABLE` | Error | SELECT tu bang bi cam |
| `OBFUSCATED_OPERATIONS` | Warning | File I/O, dynpro, batch input |
| `PREFERRED_STATEMENTS` | Warning | Cu phap cu can thay the |

## 3. Replacement Strategy

| Code cu (on-prem) | Thay bang (Cloud) |
|-------------------|-------------------|
| `SELECT * FROM ekko` | `SELECT FROM i_purchaseorder` |
| `CALL FUNCTION 'BAPI_PO_CREATE'` | `POST /API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder` (OData) hoac EML |
| `CALL SCREEN 0100` | Fiori Elements + RAP BO |
| `sy-datum, sy-uzeit` | `cl_abap_context_info=>get_system_date( )` |
| `BREAK-POINT` | ADT debugger |
| `ENHANCEMENT-POINT` | Cloud BAdI |
| `SUBMIT report` | `cl_abap_parallel` hoac RAP action |
| `EXEC SQL` | AMDP SQLScript |

## 4. Migration Strategy

### Buoc 1: Inventory (2-4 tuan)
- Liet ke toan bo custom code (report, class, BAdI, user exit, BAPI)
- Phan loai: Cloud-compatible / Can sua / Can thay the

### Buoc 2: ATC Check + Plan (2-3 tuan)
- Chay ATC check
- Phan tich error va classification
- Lap ke hoach sua/tai cau truc

### Buoc 3: Code Adaptation (4-12 tuan)
- Sua code theo 3 tang (Key User / Developer / Side-by-side)
- Thay the banned statements
- Migrate BAPI to released API/EML

### Buoc 4: Test (4-6 tuan)
- Unit test (ABAP Unit)
- Integration test (Fiori app test)
- ATC re-run (0 error requirement)

### Buoc 5: Go-Live
- Dual maintenance trong transition period
- Song song chay old + new
- Cut-over migration plan

## 5. User Exit & Enhancement Migration

| Loai | Cloud Strategy |
|------|----------------|
| User exit (CMOD) | Cloud BAdI hoac side-by-side |
| Classic BAdI (SE18/19) | Cloud BAdI (neu release) hoac side-by-side |
| Enhancement point/section | Cloud BAdI |
| VOFM (pricing) | SAP has replacement? Check BAdI hoac side-by-side |
| Customer exit (MV45AFZZ) | Cloud BAdI trong SD |

## 6. Reporting Migration

| Report cu | Cloud thay the |
|-----------|----------------|
| ALV Report (REUSE_ALV_GRID_DISPLAY) | CDS view + Fiori Analytical app |
| WRITE report | `if_oo_adt_classrun` + CDS query |
| Interactive report | Fiori Elements List Report |
| HR report (RPY* / HCM*) | SuccessFactors ad-hoc reporting |

## 7. Common Gotchas

- **BAPI**: Nhieu BAPI chua duoc release. Kiem tra API Hub truoc. Thay bang EML hoac OData service.
- **Function Group**: `FUNCTION-POOL` thuong chua duoc release. Chuyen sang class.
- **Extension Index**: Z table co the can CDS view + DCL de expose.
- **FORM**: `PERFORM ... FORM` chuyen sang method.
- **ALV Grid**: Chuyen sang CDS + Fiori.
- **BDC/Batch Input**: Chuyen sang OData API + EML.

## Skill lien quan

- `sap-atc-review` — checklist ATC tu dong hoa (naming/released-API/clean-ABAP) chay SAU khi
  scaffold code moi; dung skill nay (`sap-cloud-migration`) khi PHAN TICH/lap ke hoach migration
  code CU co san, dung `sap-atc-review` khi review code MOI vua sinh — 2 skill cung doc chung
  1 nhom ma loi ATC (`CLOUD_READINESS`, `USE_RELEASED_OBJECT`...) tu 2 goc do khac nhau.

## Nguon tham khao

- SAP ATC documentation
- SAP Clean Core strategy guide
- SAP API Business Hub: `https://api.sap.com`
- SAP Community: Migration to ABAP Cloud
