---
name: sap-ewm-cloud
description: Kien thuc EWM (Extended Warehouse Management — inbound, outbound, internal, inventory, slotting, kitting, labor, RF) cho SAP S/4HANA Cloud Public Edition — Embedded EWM, SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve quan ly kho nang cao thay cho WM.
effort: high
model: haiku
when_to_use: Khi user hoi ve warehouse management nang cao (EWM thay vi WM co dien) tren S/4HANA Cloud Public Edition, hoac khi can biet ve Embedded EWM scopeBK9.
---

# EWM (Extended Warehouse Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — kiem chung qua SAP Community/Help. EWM thay the hoan toan cho WM (WM EOL 2025).
Embedded EWM (scope BK9) la chuan tren Public Edition. Khi ko chac ve 1 chi tiet/SSCUI/socpe item,
luon nhac user xac minh tren release hien tai.]

## 1. Phan biet EWM vs WM

| Tieu chi | WM (Legacy) | EWM (Modern) |
|----------|------------|--------------|
| Kien truc | Trong R/3 / ECC | Embedded trong S/4HANA hoac Decentralized |
| Kha nang | Co ban, gioi han | C ao, tuong hoa |
| Tinh nang | Nhap/xuat/ton co ban | Slotting, Kitting, VAS, Labor Mgmt, Wave, MFS |
| Trang thai | **EOL cuoi 2025** | **Chuan hien tai** |

## 2. Kien truc kho (Warehouse Structure)

| Cap | Vi du | Mo ta |
|-----|-------|-------|
| Warehouse Number | `W001` | Kho cap cao nhat |
| Storage Type | `0001` (Raw), `0002` (Finished), `0004` (Goods Receipt) | Vung trong kho |
| Storage Section | `A01`, `B02` | Phan vung trong Storage Type |
| Storage Bin | `01-01-01` | Vi tri chua hang cu the |
| Quant | `Q0000012345` | Don vi ton kho nho nhat |

## 3. Xu ly Inbound (Nhap kho)

1. Inbound Delivery (tu MM purchase order)
2. Warehouse Task cho GR (Goods Receipt)
3. Putaway (c at vao Storage Bin)
4. Xac nhan Warehouse Task

## 4. Xu ly Outbound (Xuat kho)

1. Outbound Delivery (tu SD sales order)
2. Wave Management (gom nhieu don)
3. Picking (lay hang, RF / Paper)
4. Packing (dong goi, Handling Unit)
5. Goods Issue (xuat kho)

## 5. Fiori apps chinh

| Nghiep vu | Fiori app |
|-----------|-----------|
| Dashboard warehouse | Warehouse Monitor |
| Inbound processing | Change Inbound Deliveries |
| Outbound processing | Run Outbound Process - Deliveries |
| Kiem ke | Physical Inventory Documents |
| Handling Unit | Maintain Handling Units |
| RF | RF UI (Fiori-based) |

## 6. SSCUI / Scope items

| Scope Item | Mo ta |
|------------|-------|
| **BK9** | Embedded EWM (chuan) |
| **BW1** | Warehousing & Shipping |
| **BW2** | Physical Inventory |
| **BW5** | Wave Management |
| **BW7** | Kitting |

## 7. Released API

| Nhu cau | API (kiem tra tren `api.sap.com`) |
|---------|----------------------------------|
| Warehouse Order | `API_WAREHOUSE_ORDER_SRV` |
| Warehouse Task | `API_WAREHOUSE_TASK_SRV` |
| Handling Unit | `API_HANDLING_UNIT_SRV` |
| Stock | `I_ProductStockQuantity` (CDS) |

## 8. Huong mo rong

- **Custom Fields** — them field vao warehouse task/order/delivery
- **Custom Logic (Cloud BAdI)** — kiem tra Cloud BAdI cho EWM truoc khi side-by-side
- **Side-by-side BTP** — Warehouse Control System (WCS), ASRS integration, robot

## 9. Nguon tham khao

- [SAP EWM Overview](https://www.sap.com/products/scm/extended-warehouse-management.html)
- [SAP Help Portal — EWM](https://help.sap.com/docs/SAP_EXTENDED_WAREHOUSE_MANAGEMENT)
- [SAP Best Practices Explorer — EWM](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Ref Library](https://fioriappslibrary.hana.ondemand.com/)
- [SAP API Business Hub](https://api.sap.com)

> 📚 Xem `deep/SKILL.md` (trong cung thu muc) de biet chi tiet ve storage control, process types,
> wave templates, slotting rules, labor standards, RF menus, yard management va integration
> scenarios cho EWM.
