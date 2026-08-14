# Knowledge Pack — Phân hệ SD (Sales & Distribution)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `SD-SLS` (sales), `SD-BIL` (billing), `SD-ANA-*` (analytics).
**Catalog gốc**: `docs/Phan_He_SAP_MD/SD.md`
**LE catalog**: `docs/Phan_He_SAP_MD/LE.md` (Outbound Delivery: I_OutboundDelivery, I_OutboundDeliveryItem)

## Keyword → CDS candidate (cần verify released)

| Keyword FS | CDS candidate | Catalog component | Released |
|-----------|---------------|-------------------|----------|
| đơn bán / sales order header | `I_SalesOrder` | SD-SLS-SO | [Unverified — verify qua View Browser ADT] |
| đơn bán / sales order item | `I_SalesOrderItem` | SD-SLS-SO | [Unverified] |
| document flow SO item | `I_SalesOrderItmSubsqntProcFlow` | SD-SLS-SO | [Unverified] |
| document flow SO header | `I_SalesOrderSubsqntProcFlow` | SD-SLS-SO | [Unverified] |
| hoá đơn / billing document | `I_BillingDocument`, `I_BillingDocumentItem` | SD-BIL | [Unverified] |
| khách hàng / customer | `I_BusinessPartner` + `ZI_ACME_BPARTNER` | AP-MD-BP | ACME custom verified |
| công ty / company | `ZI_ACME_COMPCODE` | PUB_ACME_CODE | ACME custom verified |
| vận chuyển / outbound delivery | `I_OutboundDelivery`, `I_OutboundDeliveryItem` | LE-SHP-GF | [Unverified] |
| freight order / TM / vận chuyển | `I_TransportationOrder_2`, `I_TransportationOrderItem_2`, `I_TranspOrdDocRef_2` | TM-FRM | [Unverified released — verify View Browser] |
| link delivery ↔ freight order | `I_TranspOrdDocRef_2.TranspOrdDocReferenceID` = Delivery number | TM-FRM | [Unverified] — P_OutbDelivFrtOrdrLtn KHÔNG dùng (Private) |

## Fields đã verify từ catalog

### I_SalesOrder (SD-SLS-SO, Dimension)
- Key: `SalesOrder`
- Confirmed fields: `SalesOrganization`, `SoldToParty`, `RequestedDeliveryDate`, `ShippingType`, `SalesOffice`, `CreatedByUser`
- Associations: `_SalesOrganization`, `_SoldToParty`, `_ShippingType`, `_SalesOffice`, `_CreatedByUser`

### I_SalesOrderItem (SD-SLS-SO, Dimension)
- Key: `SalesOrder`, `SalesOrderItem`
- Confirmed fields: `Material`, `Plant`, `OrderQuantity`, `OrderQuantityUnit`, `RequestedDeliveryDate`, `ShipToParty`, `SalesOrganization`
- Associations: `_Material`, `_Plant`, `_SalesOrder`, `_ShipToParty`, `_OrderQuantityUnit`

### I_SalesOrderItmSubsqntProcFlow (SD-SLS-SO)
- Key: `SalesOrder`, `SalesOrderItem`, `DocRelationshipUUID`
- Fields: `SubsequentDocument`, `SubsequentDocumentCategory`, `SubsequentDocumentItem`
- Dùng để trace SO item → Outbound Delivery

### I_OutboundDelivery (LE-SHP-GF, Dimension)
- Key: `OutboundDelivery`
- Confirmed fields: `ActualGoodsMovementDate`, `ActualGoodsMovementTime`, `ShipToParty`, `SoldToParty`, `SalesOrganization`, `SalesOffice`, `ShippingType`, `ProofOfDeliveryDate`, `PlannedGoodsIssueDate`, `TransportationPlanningDate`, `MeansOfTransport`, `MeansOfTransportType`, `RouteSchedule`
- Associations: `_ShipToParty`, `_ActualDeliveryRoute`, `_SalesOrganization`
- NOTE: `ProofOfDeliveryDate` = ngày KH xác nhận nhận hàng (POD)

### I_OutboundDeliveryItem (LE-SHP-GF, Dimension)
- Key: `OutboundDelivery`, `OutboundDeliveryItem`
- Confirmed fields: `ActualDeliveredQtyInBaseUnit`, `ActualDeliveryQuantity`, `Material`, `Plant`, `GoodsMovementStatus`, `ReferenceSdDocument` (= SO number), `ReferenceSdDocumentItem`, `ReferenceSdDocumentCategory`
- Associations: `_Material`, `_Plant`, `_GoodsMovementStatus`, `_ReferenceSalesDocumentItem`

### Freight Order / Freight Unit (SAP TM) — chi tiết: docs/Phan_He_SAP_MD/TM.md §ZSD18 Knowledge

SAP TM dùng khái niệm Transportation Order (TOR). Catalog TM.md (79 views, TM-FRM) có đủ views:
- `I_TransportationOrder_2`: header FO — `Carrier`, `TransportationOrderExecSts`, `TranspMeansOfTransport`, `CreatedByUser`, `TransportationOrder`
- `I_TransportationOrderItem_2`: item — `TranspEquipmentPlateNumber` (biển số xe)
- `I_TransportationOrderBP_2`: Business Partners của FO (carrier/shipper/consignee)
- `I_TransportationOrderEvent`: events — `TranspOrdEvtActualDateTime`, `TranspOrdEventCode` (arrived/check-in)
- `I_TransportationOrderStop_2`: stops — `TranspOrdStopApptEndDteTme` (planned arrival), `TranspStopCarrConfEndDteTme` (actual confirmed)
- `I_TranspOrdDocRef_2`: link FO ↔ Delivery (`TranspOrdDocReferenceID` = Delivery number)
- **P_OutbDelivFrtOrdrLtn**: Private view (P_*) — KHÔNG dùng trong ABAP Cloud.
- **CE_FREIGHTORDER_0001**: OData V4, tồn tại trên api.sap.com — [Unverified] released state.
- **Released state tất cả I_TransportationOrder*_2**: [Unverified] — phải verify View Browser ADT.

## ACME Custom Views (PUB_ACME_CODE — read-only)

| [App] | View | Mô tả | Key field | Trường chính |
|-------|------|--------|-----------|--------------|
| ZCOMPANY | `ZI_ACME_COMPCODE` | Company Code master | `CompanyCode` | `TenCtyVN`, `TenCtyEN`, `DiaChiVN`, `MST`, `Phone` |
| ZPARTNER | `ZI_ACME_BPARTNER` | Business Partner master | `BusinessPartner` | `BPName`, `BPAddress`, `BPTaxNumber`, `BPTelephone` |
| ZPLANT | `ZI_ACME_PLANT` | Plant master | `Plant` | `PlantName`, `PlantAddress`, `CompanyCode` |

Join: `I_SalesOrder._SalesOrganization` → không phải CompanyCode trực tiếp.
CompanyCode lấy từ `I_SalesOrg` → `.CompanyCode` → join `ZI_ACME_COMPCODE.CompanyCode`.

## 5. Ghi chú

- Print invoice/packing list → kết hợp AGENTS_PDF (mẫu `ZSD02`).
- ZSD18 cần dữ liệu SO + OD + Freight Order (TM). Phần TM có I_TransportationOrder*_2 trong catalog TM.md nhưng released state [Unverified] — verify View Browser ADT.
- Freight Order → xem `docs/Phan_He_SAP_MD/TM.md` §ZSD18 Knowledge cho field mapping + join path đầy đủ.
- `I_ProductDescription` (MM) chứa `Product`, `Language`, `ProductDescription` — dùng cho tên sản phẩm.
- **TM Freight Order — GHI execution/check-in-out (Public Cloud) — VERIFIED LIVE** (ZSD07, tenant project3
  client 100, MCP read-only 2026-07-04): dùng **EML action `ReportEvent`** trên released BO **`I_FreightOrderTP`**
  (package **`RAP_TM_FO_API`**, ac TM-FRM-FRO-2CL, EML-capable), entity root **FreightOrder**.
  - **Action `ReportEvent`** deep param **`D_TranspOrdReportEventP`**: `TranspOrdEventCode` (`/scmtms/tor_event`),
    `TransportationOrderStopUUID` (optional, `/scmtms/torstopuuid`), `TranspOrdEvtActualDateTime`
    (`/scmtms/vdm_event_actl_dtetme` — **built-in CHƯA xác minh: ADT reject cả `utclong` LẪN `timestampl`;
    verify F2 ADT trước khi CONVERT, ĐỪNG đoán**), `TranspOrdEvtEstimatedDateTime`.
  - **Event code** (view released `I_TranspOrdEventCode_2`): **`EP_CHECK_IN`** (stop cat I) = Set to Checked In;
    **`EP_CHECK_OUT`** (stop cat O) = Set to Checked Out. (Còn EP_ARRIVAL/EP_DEPARTURE/EP_LOAD_*/EP_UNLOAD_*.)
  - **Key EML** root = **`TransportationOrderUUID`** (raw16), KHÔNG phải số FO → SELECT `I_TransportationOrder_2`
    (field `TransportationOrder` = số FO CHAR10, `/scmtms/vdm_tor_id`) để map number → UUID.
  - **datetime TM = `timestamp` (domain `TZNTSTMPS`, DEC 15,0) — VERIFIED (user F2 ADT 2026-07-04)**:
    `/scmtms/vdm_event_actl_dtetme` (event) + `/scmtms/vdm_tor_order_datetime` (header order). KHÔNG phải
    `utclong` (ADT reject), KHÔNG phải `timestampl` DEC21,7 (ADT reject). → Type biến ABAP = **`timestamp`**;
    tách date/time = `CONVERT TIME STAMP ts TIME ZONE tz INTO DATE d TIME t` (ZSD07 `ZCL_ZSD07_O_PUSH.split_ts`).
    Field giờ/ngày payload phải built-in `t`/`d` — **data element `TIMS`/`DATS` KHÔNG được phép trong ABAP Cloud class**.
    Bài học quy trình: kiểu này ban đầu bị ĐOÁN (utclong→timestampl→…) sai 3 lần vì tin memory chưa verify →
    chỉ chốt khi F2 data element (nguồn authoritative). (memory `tm-timestamp-utclong-overflow` đã sửa.)
  - **⚠ Cross-BO + RAP phase**: `MODIFY ENTITIES` + `COMMIT ENTITIES` sang `I_FreightOrderTP` (BO khác) KHÔNG
    được gọi trong save-phase (`BEHAVIOR_STATEMENT_ILLEGAL` + cấm COMMIT) → chạy ở **LUW riêng post-commit**
    (background/async); determination chỉ validate SELECT-only (memory `rap-doc-number-late-numbering`).
  - On-prem `REPORT_EVENT` (`/SCMTMS/CL_TOR_A_EXI_REP_EVENT`) **KHÔNG dùng được** (cấm `/SCMTMS/`); fallback
    OData A2X `CE_FREIGHTORDER_0001` không cần. Chi tiết + code: ADR-0024, `source code/ACME_SAP_2026_TH_ZSD07`.
- **TM Freight Order — ĐỌC/FLATTEN cho report/outbound (pattern app view `C_FrtOrdManagement`)** ⭐: khi cần
  1 dòng/FO với các field ở stop/item khác node (Plant, ngày dự kiến, biển số), tham khảo cách app *Manage
  Freight Orders* làm — view `C_FrtOrdManagement` (KHÔNG released → replicate bằng view released, KHÔNG select
  trực tiếp). Assoc **to-one FILTER** (chấp nhận cardinality [0..1]):
  - `_SourceStop` = `I_TransportationOrderStop_2` on `TransportationOrderUUID` + `TranspOrdStopSequencePosition = 'F'` (stop đầu); `_DestinationStop` = `= 'L'` (stop cuối) → `LocationId` = Plant xuất/nhận; `TranspOrdStopPlanTranspDteTme` = ngày/giờ dự kiến.
  - `_AvrItem` = `I_TransportationOrderItem_2` on UUID + `TranspOrdItemCategory = 'AVR'` (Active Vehicle Resource = xe chính) → `TranspEquipmentPlateNumber` = **biển số (Registration Number)**. (PVR=rơ-moóc, DRI=tài xế.)
  - **Split timestamp trong CDS bằng `tstmp_to_dats` / `tstmp_to_tims` — 4 PARAM** (TM datetime = timestamp TZNTSTMPS): `tstmp_to_dats( ts, abap_user_timezone( $session.user, $session.client, 'NULL' ), $session.client, 'NULL' )` (ts, tzone, clnt, on_error). ⚠️ 2-param báo lỗi "parameters 2 <> 4". Sạch hơn CONVERT trong ABAP.
  - Carrier name: SAP dùng `_Carrier.BusinessPartnerFullName`; ACME dùng `ZI_ACME_BPARTNER.BPName` (reference). WHERE `TransportationOrderCategory = 'TO'`. Verified ZSD07 outbound 2026-07-04 (MCP read-only client 080).

## Changelog

| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
| 2026-06-28 | Bổ sung ZSD18 research: SO/OD fields từ catalog, TM risk, ACME views, doc flow | AGENTS_SD |
| 2026-06-28 | Verify TM: tìm I_TransportationOrder*_2 trong TM.md catalog, cập nhật TM.md §ZSD18, P_OutbDelivFrtOrdrLtn kết luận KHÔNG dùng, CE_FREIGHTORDER_0001 tồn tại nhưng [Unverified] released | AGENTS_SD |
| 2026-07-04 | ZSD07: TM FO write execution ưu tiên EML released BO I_FreightOrderTP (BDEF released TM-FRM-FRO-2CL, update-only), fallback OData A2X CE_FREIGHTORDER_0001; action Set Checked In/Out + entity đích [Unverified] cần verify BDEF trong ADT; on-prem REPORT_EVENT /SCMTMS/ không dùng được. ADR-0024 | AGENTS_API |
| 2026-07-04 | ZSD07 (web research bổ sung): key EML I_FreightOrderTP = TransportationOrderUUID (không phải số FO, cần map); cross-BO EML phải ở LUW riêng ngoài save-phase (BEHAVIOR_STATEMENT_ILLEGAL); check-in/out chưa có nguồn public demo qua released API/EML, check-out có thể qua business event goods-issue của delivery | AGENTS_API |
| 2026-07-04 | ZSD07 **RESOLVED (verified live project3 client 100, MCP read-only)**: EML action **ReportEvent** trên **I_FreightOrderTP** (RAP_TM_FO_API), deep param **D_TranspOrdReportEventP**, event code **EP_CHECK_IN/EP_CHECK_OUT** (I_TranspOrdEventCode_2), key TransportationOrderUUID, datetime utclong. BLOCKER đóng, code ráp thật. ADR-0024 | AGENTS_API |
