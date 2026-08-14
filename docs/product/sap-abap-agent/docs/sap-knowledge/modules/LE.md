# Knowledge Pack — Phân hệ LE (Logistics Execution)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `LE-SHP-*` (shipping/delivery).
**Catalog gốc**: `docs/Phan_He_SAP_MD/LE.md`

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released |
|-----------|---------------|----------|
| giao hàng outbound / delivery | `I_OutboundDelivery`, `I_OutboundDeliveryItem` | `[Unverified]` |
| nhận hàng inbound | `I_InboundDelivery` | `[Unverified]` |
| handling unit / đóng gói | tra `LE-SHP` trong catalog | `[Unverified]` |

## 1-4. *(điền dần khi verify — xem `_template.md`)*

### Outbound Delivery (LE-SHP)
| CDS view | Mục đích | Released 2602 | Nguồn |
|---|---|---|---|
| `I_OutboundDelivery` | Outbound Delivery header | released (`ac=LE-SHP-GF-2CL`) | `released-objects-index.json` |
| `I_OutboundDeliveryItem` | Outbound Delivery item | released (`ac=LE-SHP-GF-2CL`) | `released-objects-index.json` |
| `I_OverallProofOfDelivSts` / `I_ProofOfDeliveryStatus` | Proof of Delivery status (header/item) | có trong catalog `Phan_He_SAP_MD/LE.md` LE-SHP-GF, released state **chưa verify field-level** | `Phan_He_SAP_MD/LE.md` dòng 101, 121 |
| Số tờ khai hải quan xuất khẩu trên delivery | — | **KHÔNG có field chuẩn released** trong catalog LE — cần custom field/note hoặc nhập tay | `[Unverified]` — chưa tìm thấy đối tượng chuẩn |

### Transportation Management (TM embedded, ac `TM-FRM*`) — KHÔNG thuộc catalog LE-SHP, tra riêng qua `released-objects-index.json`
| CDS view | Mục đích | Released 2602 | Application component | Ghi chú |
|---|---|---|---|---|
| `I_TransportationOrder_2` | Freight Order — plain read-only interface view (không expose action/event) | released | `TM-FRM-2CL` | Dùng cho reporting/read. Field carrier/vehicle/container **chưa verify tên field chính xác** — `[Unverified]` |
| `I_TransportationOrderItem_2` | Freight Order item | released | `TM-FRM-2CL` | |
| `I_TransportationOrderStop_2` | Freight Order stop (điểm dừng — có thể chứa Port/Location + Planned Arrival) | released | `TM-FRM-2CL` | Field tên chính xác `[Unverified]`, cần ADT/View Browser |
| `I_TransportationOrderStage_2` | Freight Order stage/leg | released | `TM-FRM-2CL` | |
| `I_TransportationOrderBP_2` | Freight Order business partner (khả năng chứa Carrier) | released | `TM-FRM-2CL` | Field tên chính xác `[Unverified]` |
| `I_TransportationOrderEvent` | Freight Order event (khả năng chứa timestamp check-in/out — biết trước field TM dạng event thường là `utclong`, xem memory `tm-timestamp-utclong-overflow`) | released | (chưa verify ac) | So sánh utclong trực tiếp, KHÔNG convert packed p8 (tràn số) |
| `I_FreightOrderTP` | Freight Order — behavior-enabled (RAP BDEF) projection, dùng khi cần action/event qua EML, KHÔNG chỉ đọc | released | `TM-FRM-FRO-2CL` | TP = transactional processing (khác `I_TransportationOrder_2` read-only) |
| `I_FreightOrderItemTP` | Freight Order item (behavior-enabled) | released | `TM-FRM-FRO-2CL` | |
| `I_FreightOrderStopTP` | Freight Order stop (behavior-enabled) | released | `TM-FRM-FRO-2CL` | |
| `I_FreightOrderStageTP` | Freight Order stage (behavior-enabled) | released | `TM-FRM-FRO-2CL` | |
| `I_FreightOrderBPTP` | Freight Order business partner (behavior-enabled) | released | `TM-FRM-FRO-2CL` | |
| `I_FreightOrderDocRefTP` | Freight Order document reference — **candidate** cho liên kết Freight Order ↔ Outbound Delivery, field/key **CHƯA verify** | released | `TM-FRM-FRO-2CL` | `[Unverified]` — cần đọc field list qua ADT (BDEF) hoặc api.sap.com |
| `I_FreightOrderItemDocRefTP` | Freight Order item document reference | released | `TM-FRM-FRO-2CL` | `[Unverified]` cùng lý do trên |
| Container ID | — | `[Unverified]` — chưa xác định thuộc Freight Order (`I_FreightOrderItemBatchTP`/`I_FreightOrderItemSealTP`?) hay Handling Unit (view LE riêng, chưa tìm thấy trong catalog LE.md) | cần tra thêm `I_HandlingUnit*` (chưa thấy trong index/catalog khi tra lần này) |
| Means of Transport / Vehicle (biển số xe) | — | `[Unverified]` — có thể nằm ở resource/equipment view TM (không nằm trong `Phan_He_SAP_MD/LE.md`, cần tra module TM riêng nếu core 8 mở rộng) | chưa tìm thấy view cụ thể |

**Lưu ý quan trọng**: TM (Transportation Management) embedded KHÔNG thuộc 8 module core hiện có
(`FI · CO · MM · SD · LE · PP · PM · QM`), và catalog `Phan_He_SAP_MD/LE.md` (LE-SHP) KHÔNG chứa view TM
(`ac=TM-FRM*`). Các view trên tra được qua `released-objects-index.json` (state=released xác nhận), nhưng
**field-level chi tiết KHÔNG có trong index này** (theo README: "Không có field-level info") → mọi tên field
cụ thể (Carrier, VehicleID, ContainerID, PlannedArrivalDateTime...) phải verify riêng qua Eclipse ADT View
Browser / api.sap.com trước khi dùng trong Technical Spec.

## 5. Ghi chú
- LE gắn SD (delivery từ sales order) và MM (goods movement).
- TM embedded (Freight Order) không thuộc LE-SHP nhưng liên quan chặt tới Outbound Delivery trong luồng
  vận chuyển xuất khẩu — xem bảng riêng ở trên. Nếu phát sinh nhiều nhu cầu TM, cân nhắc tạo pack riêng
  `docs/sap-knowledge/modules/TM.md` theo vòng "học phân hệ mới" (module-expert-process.md §Vòng học).

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
| 2026-07-04 | Verify view-level released (state) cho Outbound Delivery + TM Freight Order qua `released-objects-index.json`, cho FS ZAP06 (Bảng kê chứng từ vận chuyển XK). Field-level CHƯA verify — đánh `[Unverified]`, cần ADT/api.sap.com | module-agent LE |
