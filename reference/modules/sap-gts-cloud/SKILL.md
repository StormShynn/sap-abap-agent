---
name: sap-gts-cloud
description: Kien thuc GTS (Global Trade Services — customs management, import/export, sanctioned party list, preference processing, bonded warehouse) cho SAP S/4HANA Cloud Public Edition. Dung khi user hoi ve xuat nhap khau, hai quan, compliance, trade.
effort: low
model: haiku
---

# GTS (Global Trade Services) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Help. **Luu y**: GTS co the la SAP GTS on-prem hoac **SAP
Global Trade Services tren BTP** (cloud version). Tren Public Cloud, GTS thuong la side-by-side
qua BTP, khong embedded trong S/4HANA core.]

## 1. Cac chuc nang chinh cua GTS

| Chuc nang | Mo ta |
|-----------|-------|
| **Customs Management** | Khai bao hai quan, to khai, tinh thue XNK, bonded warehouse |
| **Sanctioned Party List (SPL)** | Check doi tac co nam trong danh sach cam khong |
| **Preference Processing** | Chung nhan xuat xu (CO), uu dai thue (FTA) |
| **Embargo Control** | Kiem tra co cam xuat khau sang nuoc do khong |
| **Intrastat / Extrastat** | Bao cao thong ke thuong mai |

## 2. Fiori app

| Chuc nang | Fiori app |
|-----------|-----------|
| Khai bao hai quan | Manage Customs Documents |
| Check SPL | Sanctioned Party List Check |
| Uu dai thue | Manage Preference Documents |
| Thong ke XNK | Intrastat Declaration |
| Quan ly bonded warehouse | Manage Bonded Warehouse |

## 3. Tich hop GTS voi S/4HANA

| Tich hop | Cach thuc |
|----------|-----------|
| Purchasing (MM) | PO purchased from abroad → GTS customs check |
| Sales (SD) | Sales order export → GTS check customs + SPL + embargo |
| Material master | Check HS code (Customs Tariff Number) tren material |
| Batch management | GTS can batch tracking cho bonded warehouse |

## 4. API

- `API_CUSTOMS_DOCUMENT_SRV`
- `API_SPL_CHECK_SRV`
- CDS view `I_CustomsDocument`, `I_ProductCustomsTariffNumber`

## 5. Nguon tham khao

- SAP API Business Hub
- [SAP Help — GTS](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
