---
name: sap-wm-cloud
description: Kien thuc WM (Warehouse Management — warehouse structure, stock placement, stock removal, transfer order, cycle counting, bin management) rieng cho SAP S/4HANA Cloud Public Edition — SSCUI, Fiori app, released API, huong mo rong. Dung khi user hoi ve cau hinh/tich hop/mo rong WM tren Public Cloud.
effort: medium
model: haiku
---

# WM (Warehouse Management) tren SAP S/4HANA Cloud Public Edition

[Seed set — so SSCUI/scope item/Fiori app cu the thay doi theo tung release quy, luon nhac user
xac minh lai. Dung ket hop voi skill `sap-extensibility` va `sap-clean-code`.

**Luu y**: SAP S/4HANA Cloud Public Edition mac dinh dung **Embedded EWM** (Extended Warehouse
Management) thay vi WM co dien (LE-WM). Scope item cho EWM la **BK9**. Neu user noi "WM", kiem tra
xem ho muon EWM hay LE-WM. LE-WM van duoc ho tro nhung khong phai la chuan mac dinh cho Cloud.]

## 1. Cau hinh (SSCUI)

Mo tu app Fiori **Manage Your Solution**:

| Khu vuc | SSCUI / scope item | Mo ta |
|---------|-------------------|-------|
| EWM co ban | Scope item **BK9** | Cau hinh Embedded EWM co ban |
| Kho don gian (Stock Room Management) | — | Quan ly kho don gian bang batch + stock (khong can WM day du) |
| Cau truc kho (WM/EWM) | Trong Fiori app **Manage Warehouse** | Warehouse number, storage type, storage section, bin |
| Transfer order | Trong Fiori app **Create Transfer Order** | Tao TO cho stock placement / stock removal |
| Cycle counting | Scope item **BK7** | Kiem ke theo chu ky (cycle counting) |

## 2. Fiori app thay the cho tung nghiep vu

| Nghiep vu | Fiori app | Legacy transaction cu |
|-----------|-----------|----------------------|
| Quan ly kho (EWM) | Manage Warehouses (EWM) | /SCWM/LMON |
| Tao transfer order | Create Transfer Order (EWM) | LT01 / LT03 |
| Hien thi ton kho kho | Stock – Single Warehouse (EWM) | LB01 / LS24 |
| Kiem ke chu ky | Physical Inventory – Cycle Counting | MI07 / MI08 |
| Quan ly storage bin | Manage Storage Bins (EWM) | LS01 / LS02 |
| Huy / dong TO | Cancel Transfer Orders | LT09 / LT12 |
| Nhap hang vao kho | Putaway (EWM) | LT04 |
| Xuat hang khoi kho | Picking (EWM) | LT03 |
| Kiem tra kho | Monitor Warehouse (EWM) | /SCWM/MON |

## 3. Released API khi viet code tich hop

| Nhu cau | Released API (kiem tra tren `api.sap.com` truoc khi dung) |
|---------|---------------------------------------------------------|
| Warehouse order (EWM) | `API_WAREHOUSE_ORDER_SRV` |
| Warehouse task (EWM) | `API_WAREHOUSE_TASK_SRV` |
| Stock (EWM) | CDS view `I_ProductStockByWarehouse` |
| Physical inventory (cycle counting) | API Physical Inventory (EWM) |
| Transfer order (WM) | `API_TRANSFER_ORDER_SRV` (LE-WM) |
| Stock | CDS view `I_ProductStock`, `I_ProductStockByStorageBin` |
| Warehouse product | API Warehouse Product (EWM) |

## 4. Huong mo rong (extensibility) cho WM

Ap dung bac thang trong `sap-extensibility` muc 2. Vi du cu the cho WM:

- **Custom Fields and Logic** — them field vao warehouse order / warehouse task / stock, hien tren
  Fiori app EWM tuong ung.
- **Custom Business Objects** — khi can 1 loai kho dac thu hoac 1 quy trinh warehousing rieng.
- **Custom Logic (Cloud BAdI)** — kiem tra danh muc Cloud BAdI cho WM/EWM (putaway strategy,
  picking logic, storage bin determination) truoc khi ket luan can side-by-side.
- Khi can 1 heuristic dac thu cho EWM (warehouse order creation rule), thuong can developer
  extensibility (RAP) hoac side-by-side BTP.

## 5. Luu y dac thu cho WM tren Public Cloud

- **EWM la chuan**: SAP S/4HANA Cloud Public Edition khuyen dung **Embedded EWM** (scope BK9).
  LE-WM (WM co dien) chi dung cho khach hang da co WM truoc khi chuyen len Cloud.
- **Stock Room Management**: Neu kho don gian (khong can WM phuc tap), dung Stock Room Management
  (batch + stock) thay vi EWM.
- **RF / Mobile**: EWM ho tro RF (radio frequency) framework. Kiem tra Fiori Apps Reference Library
  cho app EWM Mobile.
- **Yard Management**: Neu can quan ly san / bai, scope item **BKX** (Yard Management).
- **Integration**: WM lien ket chat che voi MM (goods receipt/issue), SD (delivery), PP (production
  supply). Thuong xuyen dispatch song song.

## 6. Khi viet/review code ABAP Cloud cho WM

- Doc du lieu warehouse stock / warehouse order / warehouse task qua released API hoac CDS view,
  khong SELECT truc tiep bang chuan WM/EWM (LQUA, LTAP, /SCWM/...) — nhieu bang EWM ko nam trong
  ABAP Cloud release scope.
- Ton kho kho doc tu `I_ProductStockByWarehouse` hoac `I_StockByStorageBin`.
- WM documents (transfer order / warehouse order) doc qua released API (`API_TRANSFER_ORDER_SRV`,
  `API_WAREHOUSE_ORDER_SRV`), khong UPDATE truc tiep.

## 7. Cac scope item chinh cho WM

| Scope Item | Mo ta |
|------------|-------|
| **BK9** | Embedded EWM (Warehouse Management) |
| **BK7** | Physical Inventory (Cycle Counting) |
| **BKX** | Yard Management |
| **1D1** | Stock Room Management (don gian) |
| **BML** | Physical Inventory (truyen thong, MM) |

## 8. Nguon tham khao

- [SAP Best Practices Explorer — WM/EWM Scope Items](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Reference Library](https://fioriappslibrary.hana.ondemand.com/)
- SAP API Business Hub: `https://api.sap.com`
- [SAP Help Portal — Extended Warehouse Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD)
