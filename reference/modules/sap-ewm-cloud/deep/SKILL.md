---
name: sap-ewm-cloud-deep
description: Kien thuc EWM (Extended Warehouse Management) chi tiet — warehouse process types, wave management, slotting, labor management, RF, yard, integration. Dung khi can thong tin chuyen sau ve EWM tren S/4HANA Cloud.
effort: high
model: haiku
---

# EWM (Extended Warehouse Management) — Deep Knowledge

## 1. Warehouse Process Types (Trung tam cua EWM)

Moi buoc trong xu ly kho deu co **Warehouse Process Type** quyet dinh huong xu ly:

| Process Type | Loai | Mo ta |
|-------------|------|-------|
| Inbound | GR (Goods Receipt) | Tiep nhan hang tu nha cung cap / san xuat |
| Inbound | Putaway | Cat hang vao Storage Bin |
| Outbound | Picking | Lay hang tu Storage Bin |
| Outbound | Packing | Dong goi tao Handling Unit |
| Outbound | GI (Goods Issue) | Xuat kho |
| Internal | Replenishment | Bo sung hang cho khu vuc picking |
| Internal | Posting Change | Chuyen doi trang thai stock (Quality → Unrestricted) |
| Internal | Ad-hoc Movement | Di chuyen tu do (manual) |
| Inventory | Cycle Counting | Kiem ke dinh ky |

## 2. Wave Management

| Tinh nang | Mo ta |
|-----------|-------|
| Wave Template | Dinh nghia tieu chi gom don (ship-to party, carrier, route, delivery priority) |
| Wave Type | Phan biet manual / automatic wave release |
| Wave Release | Picking tu dong tao Warehouse Task khi wave duoc release |
| Wave Monitoring | Dashboard kiem tra wave status, overdue wave |

## 3. Slotting

| Thong so | Mo ta |
|----------|-------|
| Product Dimension | Size, weight, stackability, turnover frequency |
| Storage Bin Profile | Max weight, max volume, allowed product groups |
| Slotting Rule | FIFO, FEFO, popularity-based (fast movers → front) |
| Slotting Monitor | Xu ly de xuat de xuat slotting tu dong / manual |

## 4. Labor Management

| Tinh nang | Mo ta |
|-----------|-------|
| **Engineered Labor Standards (ELS)** | Tinh toan thoi gian chuan cho tung tac vu (picking 1 item ~ 8 giay) |
| **Labor Activity Type** | Dinh nghia loai cong viec do luong (nhan, xuat, di chuyen) |
| **Performance Calculation** | `Thoi gian thuc te / Thoi gian tieu chuan * 100%` |
| Labor Dashboard | Theo doi performance tung nhan vien, warehouse manager |

## 5. RF Framework

| Thanh phan | Mo ta |
|-----------|-------|
| RF Device | Handheld scanner, wearable, forklift terminal |
| RF Menu | Tren so cau lenh cho tung giao dich (nhan hang, cat hang, lay hang, kiem ke) |
| RF Queue | Queue xu ly trinh tu cua RF device |
| RF UI (Fiori) | Giao dien RF tren Fiori thay cho menu text truyen thong |

## 6. Yard Management

- **Yard (San kho)**: Khu vuc quan ly xe tai, container, trailer trong/toi kho
- **Transportation Unit (TU)**: Dau keo / container trong yard
- **Check-in/-out**: Dang ky vao/ra cua xe tai (gate processing)
- **Appointment Booking**: Dat lich hen truoc cho xe tai (dock scheduling)

## 7. Kitting (Gom bo)

| Khai niem | Mo ta |
|-----------|-------|
| Kit-to-order | Gom bo khi co don hang KHACH HANG |
| Kit-to-stock | Gom bo truoc, cat kho cho ban sau |
| Production Kit | Gom cho san xuat (component → sub-assembly) |
| Handling Unit Kit | Bo gom dong goi cung nhau, duyet bang Hung |

## 8. VAS (Value-Added Services)

- **Labeling**: Dan nhan theo y cau khach hang
- **Repackaging**: D on goi lai theo quy cach rieng
- **Quality Check**: Kiem tra chat luong truoc khi xuat
- **Testing**: Chay thu / kiem dinh truoc xuat

## 9. Warehouse Monitor (Fiori)

App `Warehouse Monitor` cho phep:
- Dashboard thoi gian thuc: open WTs, active waves, overdue deliveries
- Search: delivery, HU, WT, product, bin
- Actions: release wave, create WT manual, cancel WT, assign bin
- KPI: throughput (receipts/shipments/hour), productivity, error rate

## 10. Released API

| API | Muc dich | Method |
|-----|----------|--------|
| `API_WAREHOUSE_TASK_SRV` | Tao/sua/huy Warehouse Task | CRUD |
| `API_WAREHOUSE_ORDER_SRV` | Tao/sua Warehouse Order | CRUD |
| `API_HANDLING_UNIT_SRV` | Quan ly Handling Unit | CRUD |
| `API_INBOUND_DELIVERY_SRV` | Quan ly inbound delivery | READ |
| `API_OUTBOUND_DELIVERY_SRV` | Quan ly outbound delivery | READ |
| `I_ProductStockQuantity` | Ton kho (CDS view) | RFM (Read) |
| `C_ProductStockQuantityHistory` | Lich su ton kho (CDS) | RFM (Read) |

## 11. Nguon tham khao

- [SAP EWM Help Portal](https://help.sap.com/docs/SAP_EXTENDED_WAREHOUSE_MANAGEMENT)
- [SAP EWM in S/4HANA Community](https://community.sap.com/topics/extended-warehouse-management)
- [SAP Best Practices Explorer — EWM](https://me.sap.com/processnavigator)
- [SAP Fiori Apps Ref Library](https://fioriappslibrary.hana.ondemand.com/)
- [Embedded EWM Scope Item BK9](https://me.sap.com/processnavigator/scopeitems/BK9)
