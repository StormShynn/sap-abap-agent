# Knowledge Pack — Phân hệ CO (Controlling)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `CO-OM-CCA` (cost center), `CO-PC-OBJ-SRV` / `CO-PC-ACT` (product cost / actual costing).
**Catalog gốc**: `docs/Phan_He_SAP_MD/CO.md`

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released |
|-----------|---------------|----------|
| cost center / trung tâm chi phí | `I_CostCenter` | `[Unverified]` |
| profit center | `I_ProfitCenter` | `[Unverified]` |
| internal order | `I_InternalOrder` | `[Unverified]` |
| giá thành sản phẩm / cost estimate | `I_ProductCostEstimate` | YES — CO-PC-PCP-2CL |
| cost component split (planned) | `I_ProdCostEstCostCompRawDex` | YES — CO-PC-PCP-2CL |
| cost component name / value help | `I_CostComponentStdVH` | YES — CO-PC-PCP-2CL |
| actual costing / material ledger | `I_ActlCostGMatlValueChainItem` | YES — CO-PC-ACT-2CL |
| actual costing run result | `I_ActualCostingRunResult` | YES — CO-PC-ACT-2CL |

## 1. CDS view nền (CO-PC-PCP — Product Cost Planning)

### I_ProductCostEstimate
- **Released**: YES (state=released, ac=CO-PC-PCP-2CL, SAPSCORE)
- **Mô tả**: Header của Cost Estimate — tương đương CK13N header.
- **Key fields**: `CostEstimate` (NUMC), `Product`, `Plant`, `CostingVariant`, `CostingVersion` (NUMC), `CostingType`, `ValuationVariant`, `CostEstimateStatus` (= Costing Status, e.g. KA), `CostEstimateValidityStartDate`, `CostEstimateValidityEndDate`, `CostingLotSize` (QUAN), `CostComponentStructure`, `ControllingArea`, `CompanyCode`, `Ledger`
- **Filter FS**: `CostingVariant` ∈ {ZUTG1,ZUTG2,ZUTG3}, `CostingVersion` = 2, `CostEstimateStatus` = KA, `CostEstimateValidityEndDate` >= ValidOn >= `CostEstimateValidityStartDate`
- ⚠️ **`CostingVariant` là KLVAR = CHAR(4)**. Nhãn FS `ZUTG1/2/3` **dài 5 ký tự → KHÔNG khớp field**;
  ABAP strict SQL báo *"'ZUTG1' cannot be converted to CostingVariant"* khi `WHERE costingvariant IN (...)`.
  → `ZUTG1/2/3` là **nhãn chiến lược trong FS**, KHÔNG phải mã KLVAR thật. (verified ZCO04 activation 2026-07-06)
- 🟢 **GIÁ TRỊ THẬT (verified live client 100 project3, 2026-07-06)** — ACME dùng:
  - `CostingVariant = 'ZNFG'` (CHAR4, mã custom ACME; các variant SAP chuẩn: `P00L/P02L/4GL1`). ⚠️ FS ghi ZUTG1/2/3 **sai**.
  - `CostingVersion = '01'` (KHÔNG phải `'2'` như FS). Lọc `= '2'` → rớt sạch estimate.
  - `CostEstimateStatus`: thực tế có `KA` (costed, vd V041) **và** `FR` (released, vd V011) → lọc chỉ `KA` sẽ **loại** estimate FR. Hỏi KH lấy status nào.
  - Validity theo tháng (vd `20260701`–`20260731`). ⚠️ **Estimate validity thường NGẮN (1 tháng)** →
    báo cáo NĂM đừng khoá estimate theo "ngày cuối THÁNG báo cáo" (điểm ngoài tháng đó → trượt → rỗng).
    Chọn estimate có **validity GIAO với NĂM** (`validitystart <= 31/12 AND validityend >= 01/01`) để mọi
    tháng nhập đều tìm ra estimate của năm. (verified ZCO04 2026-07-06: nhập T1 rỗng vì estimate chỉ valid T7)
- **Assoc**: `_ProductCostEstimateItem` (item detail), `_CostingVariant`, `_CostingVersion`

### I_ProdCostEstCostCompRawDex
- **Released**: YES (state=released, ac=CO-PC-PCP-2CL, SAPSCORE)
- **Mô tả**: "Prod Cost Est Cost Comp Raw Data Ext" — Cost Component Split raw data của Cost Estimate. Fact view, join về `I_ProductCostEstimate` qua assoc `_ProductCostEstimate`.
- **Đặc điểm QUAN TRỌNG**: Không có field `CostComponentName` trực tiếp. Amount lưu theo pivot-column: `CostComponentCostField1Amt` ... `CostComponentCostField120Amt` (120 CURR columns), mỗi cột ứng với 1 cost component theo index (1-120). KHÔNG có cột `CostComponentNumber` hay `OverallAmount` dạng row-per-component.
- **Key non-amount fields**: `CostEstimate` (NUMC, FK → I_ProductCostEstimate), `CostingDate`, `CostingVersion` (NUMC), `CostingType`, `CostComponentSplitType`, `ValuationVariant`, `Currency` (CUKY), `IsCostComponentSplitLowerLevel`
- 🔴 **SAI LẦM hay mắc (verified ZCO04 client 100, 2026-07-06)**: vị trí cột `CostComponentCostField{N}Amt`
  (N=1..120) **KHÔNG bằng** số cost component thật. VD structure `Y1` có cost component **101,102,103,201,
  209,301,999** (>120) — không thể là index cột. Vị trí N = "element trong KEPH", còn số hiển thị (101…)
  là thuộc tính riêng; **mapping N→số nằm trong customizing TCKH3, SAP KHÔNG expose ra CDS released**
  (`I_CostComponent` từ TCKH3 bị chặn data-preview + không có field vị trí). → **Unpivot RawDex theo vị trí
  rồi join `I_CostComponentStdVH` = SAI số + trống tên.**
- 🟢 **CÁCH ĐÚNG lấy cost component split (số + tên + amount thật)**: gọi **FUNCTION read-only**
  `GetBreakdownByCompView` trên BO **`I_ProductCostEstimateTP`** (entity ProductCostEstimate). Param
  `CostComponentView` (vd `'01'` = COGM, xem `I_CostComponentView.CostCompIsForCOGM`). Result
  `D_CostEstGetBrkdwnByCompViewR` → assoc `_CostComponents` → `D_CostEstCostComponentR`
  { `CostComponent`, `CostComponentName`, `TotalAmountInCoCodeCrcy`, `FixedAmountInCoCodeCrcy`, …theo
  CtrlgArea }. Gọi qua EML (`... EXECUTE GetBreakdownByCompView FROM VALUE #( ( <7 key BO> +
  %param-CostComponentView ) )`). Key BO: CostingReferenceObject, CostEstimate, CostingType, CostingDate,
  CostingVersion, ValuationVariant, CostIsEnteredManually. ⚠️ Kết quả **phân cấp** → cách đọc `_CostComponents`
  qua EML cần **test trong ADT** (harness không parse EML).

### I_CostComponentStdVH
- **Released**: YES (state=released, ac=CO-PC-PCP-2CL, SAPSCORE)
- **Mô tả**: Value help cho Cost Component (dimension / master data).
- **Fields**: `CostComponent` (NUMC), `CostComponentName` (CHAR), `CostComponentStructure` (CHAR), assoc `_CostComponentText`
- **Dùng khi**: Cần mapping số CostComponent → tên để hiển thị.

## 2. CDS view nền (CO-PC-ACT — Actual Costing / Material Ledger)

### I_ActlCostGMatlValueChainItem
- **Released**: YES (state=released, ac=CO-PC-ACT-2CL, SAPSCORE)
- **Mô tả**: "Actual Costing Material Value Chain Item" — Fact view line item actual costing.
- **Fields có trong catalog**: `ControllingArea`, `ControllingValuationType`, `CostEstimate` (NUMC), `Currency` (CUKY), `CurrencyRole`, `ExchRateDiffAmtInDspCurrency` (CURR), `FiscalYearPeriod` (NUMC), `GLAccount`, `GLAccountName`, `GoodsMovementTypeName`, `InventoryAmtInDspCrcy` (CURR), `InventorySpecialStockType`, `InventoryValuationType`, `InvtryTransacAmtInDisplayCrcy` (CURR), `Ledger` (CHAR), `Material` (CHAR), `MaterialLedgerCategory`, `MatlLdgrDocIsCostingRelevant`, `MovementType`, `PriceDeterminationControl`, `PriceDiffAmtInDisplayCrcy` (CURR), `ProcessCategory`, `ProcurementAlternative`, `ProductionProcess` (NUMC), `SalesOrder`, `SalesOrderItem`, `Supplier`, `TotalVltdStockQuantity` (QUAN), `ValuationArea`, `ValuationQuantityUnit` (UNIT), `WBSElementExternalID`
- **Assoc**: `_Currency`, `_Ledger`, `_Plant`, `_Product`, `_QuantityUnit`
- **THIẾU trong catalog**: `ReceiptsAmount`, `ConsumptionsAmount` KHÔNG có trong field list của catalog. `CostingRunPeriodStatus`, `ValuationView`, `CurrencyType` (theo nghĩa Currency Type 10/20/30) cũng KHÔNG thấy. `CurrencyRole` có thể map tới currency type nhưng cần verify thực tế.
- **Plant**: KHÔNG có field `Plant` trực tiếp (có assoc `_Plant`); `ValuationArea` thường = Plant.

### I_ActualCostingRunResult
- **Released**: YES (state=released, ac=CO-PC-ACT-2CL, SAPSCORE)
- **Mô tả**: "Actual Costing Run Results" — Kết quả của Actual Costing Run (MR21 level).
- **Fields có trong catalog**: `ControllingArea`, `ControllingValuationType`, `CostEstimate` (NUMC), `Currency` (CUKY), `CurrencyRole`, `ExchRateDiffAmtInDspCurrency` (CURR), `FiscalYearPeriod` (NUMC — verify), `InventoryAmtInDspCrcy` (CURR), `InventorySpecialStockType`, `InventoryValuationType`, `InvtryTransacAmtInDisplayCrcy` (CURR), `Ledger` (CHAR), `Material` (CHAR), `MaterialLedgerCategory`, `PriceDiffAmtInDisplayCrcy` (CURR), `ProcessCategory`, `SalesOrder`, `SalesOrderItem`, `Supplier`, `TotalVltdStockQuantity` (QUAN), `ValuationArea`, `ValuationQuantityUnit` (UNIT), `WBSElementExternalID`
- **Assoc**: `_Currency`, `_Ledger`, `_Plant`, `_Product`, `_QuantityUnit`
- **THIẾU**: Tương tự `I_ActlCostGMatlValueChainItem` — KHÔNG có `ReceiptsAmount`, `ConsumptionsAmount`, `CostingRunPeriodStatus` (trạng thái đóng kỳ), `CostComponentSplit`, `ValuationView`.
- **Lưu ý**: Cả 2 view ACT đều KHÔNG có cost component split row-per-component.

## 3. Kết luận "Costing Run Period Status" và cost component split Actual

- Field `CostingRunPeriodStatus` (trạng thái "Closing Entry Completed") KHÔNG tìm thấy trong catalog của `I_ActlCostGMatlValueChainitem` hoặc `I_ActualCostingRunResult`. Có thể nằm ở view khác chưa được catalog hoặc ở `I_MaterialLedgerCube_Lit` (released status chưa verify).
- `ReceiptsAmount` / `ConsumptionsAmount` theo cost component: KHÔNG có field này trong 2 view trên. `I_MaterialLedgerCube_Lit` (CO-PC-ML) có `MaterialGroup` và amount fields nhưng cần verify released state và field structure thực tế.
- Khả thi thuần CDS qua 2 view trên: **HẠN CHẾ** — cần verify thêm `I_MaterialLedgerCube_Lit`.

## 4. MaterialGroup cho Product
- Field `MaterialGroup` (MATKL) của product KHÔNG có trong `I_Product` header (catalog LO.md). `I_Product` có `ProductGroup` (SPART = Division) và `PackagingMaterialGroup`, không phải MATKL.
- `I_ProductPlantBasic` và `I_ProductPlantCosting` cũng không có `MaterialGroup`.
- `MaterialGroup` xuất hiện trong BOM views (`I_BillOfMaterialItemBasic`) và `I_MaterialLedgerCube_Lit`.
- Để lọc material theo Material Group: join `I_Product` hoặc các view CO/ML với MARA trực tiếp là KHÔNG được trong ABAP Cloud (unreleased table). Cần tìm released CDS view có `MaterialGroup` + join với `Material`. `I_MaterialLedgerCube_Lit` (CO-PC-ML) có cả `Material` + `MaterialGroup` + `MaterialGroupName` — đây là candidate tốt nhất trong catalog CO.

## 5. OData API (CO-PC)
- SAP S/4HANA Cloud cung cấp OData API `API_PRODUCT_COST_ESTIMATE` cho CO-PC — cần verify released state riêng qua api.sap.com nếu cần REST approach.

## 6. Ghi chú
- CO liên quan chặt FI (`FI.md`) — số liệu actual từ journal entry.
- I_ProdCostEstCostCompRawDex dùng pivot-column design (120 cost fields) — KHÔNG dùng để filter theo CostComponentName trực tiếp trong CDS WHERE clause.
- Actual Costing views: `CurrencyRole` có thể phân biệt currency type (10=company code, 20=controlling area...) nhưng cần verify mapping thực tế.
### I_MaterialLedgerCube_Lit (CO-PC-ML, VERIFIED)
- **Released**: YES (state=released, ac=CO-PC-ML-2CL, SAPSCORE)
- **Mô tả**: "Line Item for Material Ledger - Cube" — Line item của Material Ledger document, là source cho actual costing movement data.
- **Fields quan trọng**: `Material` (CHAR), `MaterialGroup` (CHAR), `MaterialGroupName` (CHAR), `Plant` (CHAR), `Ledger` (CHAR), `FiscalYear` (NUMC), `FiscalPeriod` (NUMC), `FiscalYearPeriod` (NUMC), `ValuationArea` (CHAR), `InventoryValuationType` (CHAR), `BusinessTransactionType` (CHAR), `AmountInCompanyCodeCurrency` (CURR), `AmountInGroupCurrency` (CURR), `InventoryQty` (QUAN), `PostingDate` (DATS), `CompanyCode`, `ControllingArea`, `CostCenter`, `ProfitCenter`, `GLAccount`, `MaterialLedgerCategory`, `MaterialLedgerProcessType`
- **KHÔNG có**: `CostingRunPeriodStatus`, `ReceiptsAmount`, `ConsumptionsAmount` tên trực tiếp, `ValuationView` (theo nghĩa 0L/1L/2L), `CurrencyType` (10/20/30), cost component split.
- **Dùng cho**: Lọc actual movement amount theo `Material`, `Plant`, `MaterialGroup`, `Ledger`, `FiscalYearPeriod`. Phân biệt receipt vs consumption qua `BusinessTransactionType` hoặc `MaterialLedgerProcessType` (cần verify giá trị thực tế).
- **Assoc**: `_Material`, `_MaterialGroup`, `_Plant`, `_ProductPlant`, `_Ledger`, `_CostCenter`, `_ProfitCenter`, `_GLAccountInChartOfAccounts`

### Kết luận Actual Costing (Nhóm 2)
- `ReceiptsAmount` / `ConsumptionsAmount` tên field CHÍNH XÁC: KHÔNG có trong catalog của `I_ActlCostGMatlValueChainItem`, `I_ActualCostingRunResult`, hay `I_MaterialLedgerCube_Lit`. Cần verify thực tế trên hệ thống qua ADT.
- `CostingRunPeriodStatus` ("Closing Entry Completed"): KHÔNG tìm thấy trong bất kỳ view nào trong 3 catalog trên. Đây có thể là field trên header Actual Costing Run (MR21) chứ không phải trên line item view — cần tra view header run hoặc dùng BAPI_ACTUALCOSTINGRUN_READ (nếu released).
- Approach khả thi thuần CDS: `I_MaterialLedgerCube_Lit` GROUP BY `Material`, `Plant`, `MaterialGroup`, `FiscalYearPeriod`, `Ledger` + phân biệt receipt/consumption qua `BusinessTransactionType` — nhưng cần verify giá trị type trên hệ thống thực.
- Cost component split cho Actual Costing qua CDS released: KHÔNG có view released tìm thấy trong catalog. Đây là gap nghiêm trọng — Nhóm 2 theo cost component split có thể KHÔNG KHẢ THI thuần CDS released.
- **VERIFIED chính thức (2026-07-05)** qua SAP Community thread "the CDS of APP Display Actual Costing Result"
  (https://community.sap.com/t5/supply-chain-management-q-a/the-cds-of-app-display-actual-costing-result/qaq-p/14307686):
  câu trả lời SAP xác nhận nguyên văn **"If you are requesting data for cost component split for each
  material and its movements, no CDS view exists for this purpose."** → CONFIRMED đúng: 2602 KHÔNG có CDS
  released cho actual costing cost-component split (MLCD/MLDOCCCS). Table backend đổi tên MLCD → MLDOC/MLDOCCCS
  (S4TWL DM-ML) nhưng KHÔNG có VDM/CDS released expose MLDOCCCS. `[Unverified]` mức tenant cụ thể — verify qua
  cộng đồng + KBA, chưa test trên tenant ACME.
- **View bổ sung phát hiện (2026-07-05)**: `I_ActualCostingActivityResult` — released (CO-PC-ACT-2CL, SAPSCORE),
  cùng nhóm với `I_ActlCostGMatlValueChainItem`/`I_ActualCostingRunResult`. Theo mô tả cộng đồng: "fact view tập
  trung vào activity data (cost centers/activities) trong actual costing run" — dùng khi cần actual activity
  consumption (Cost Center/Activity Type) thay vì cost component split. Field list chưa có trong catalog
  `Phan_He_SAP_MD/CO.md` (catalog gốc thiếu record) — cần Read source qua ADT/vsp nếu cần field chi tiết.
- **Mitigation cho gap cost-component-split actual** (cây `missing-released-api-mitigation.md`):
  ① released alternative → KHÔNG có (đã verify). ② standard OData API → chưa tìm thấy OData API public
  riêng cho MLDOCCCS trong 2602 `[Unverified]`, cần kiểm tra thêm `API_MATERIAL_STOCK_SRV` hoặc CDS-based
  custom analytical query (key-user) tổng hợp từ `I_MaterialLedgerCube_Lit` + `I_ActlCostGMatlValueChainItem`
  (KHÔNG có breakdown NL chính/phụ/nhân công/khấu hao — chỉ tổng amount). ③ key-user extensibility: tạo
  Custom CDS View (key-user) join `I_MaterialLedgerCube_Lit` nếu MLDOCCCS lộ qua DB view chuẩn được phép
  đọc — cần xác nhận riêng, rủi ro cao vì bảng gốc có thể không thuộc whitelist key-user. ④ escalate: nếu FS
  bắt buộc breakdown cost component cho ACTUAL (không chỉ PLANNED), đây là **BLOCKER thật sự** — khuyến nghị
  báo khách hàng: report ZCO04/ZCO10 phần "Thực hiện" (actual) theo cost component KHÔNG khả thi thuần CDS
  released 2602; đề xuất downgrade scope actual về tổng amount (không breakdown) hoặc dùng Costing Run/
  Cost Estimate (`I_ProductCostEstimate` + `I_ProdCostEstCostCompRawDex`) như proxy cho "actual" nếu nghiệp
  vụ chấp nhận (đây là ESTIMATE, không phải actual thật).

## Cross-module: PIR (Planned Independent Requirements) — thuộc PP, không phải CO
- **`I_ActivePlndIndepRqmt`** (header) — released (`PP-VDM-2CL`, SAPSCORE). Key fields: `Product`, `Plant`,
  `PlndIndepRqmtVersion` (=VERSB, vd "00"/"ZA"), `RequirementPlan` (=PBDNR), `PlndIndepRqmtType`,
  `PlndIndepRqmtInternalID`, `MRPArea`. KHÔNG có field `PlanQty` ở header, KHÔNG có `ProductionVersion` trực tiếp.
- **`I_ActivePlndIndepRqmtItem`** (item, theo period) — released (`PP-VDM-2CL`). Fields: `PlannedQuantity` (QUAN),
  `WithdrawalQuantity`, `PeriodType`, `WorkingDayDate` (tháng/năm derive từ đây), `BaseUnit`,
  `PlndIndepRqmtInternalID` (FK → header), assoc `_ActivePlndIndepRqmtItem`.
- 🟢 **`PeriodType` THẬT = `'D'` (daily), KHÔNG phải `'M'` (verified live client 100, 2026-07-06)**. ACME lưu PIR
  theo NGÀY → muốn số theo tháng phải **SUM theo calendar month** từ `WorkingDayDate`. Lọc `PeriodType = 'M'` →
  **rớt sạch → report rỗng**. Quan sát thêm: chỉ có version `'00'` (FC); `'ZA'` (AOP/CK) chưa có data.
- **`I_PlndIndepRqmtByIntKey`** / **`I_PlndIndepRqmtItemByIntKey`** — released (`PP-VDM-2CL`), field tương tự
  header/item bản "by internal key" (có thêm `PlndIndepRqmtIsActive`, `PlndIndepRqmtIsToBeDeleted`,
  `PlannedIndepRqmtDeletionCode`).
- **Nguồn xác minh**: `docs/Phan_He_SAP_MD/PP.md` dòng 33-34, 313-317, 432-449, 6743-6782 +
  `released-objects-index.json` (`DDLS:I_ACTIVEPLNDINDEPRQMT`, `DDLS:I_ACTIVEPLNDINDEPRQMTITEM`,
  `DDLS:I_PLNDINDEPRQMTBYINTKEY`, `DDLS:I_PLNDINDEPRQMTITEMBYINTKEY` đều `state=released`).
- **Ghi chú cho ZCO04/ZCO10**: PIR không phải phân hệ CO — cross-module PP. `ProductionVersion` (Pver) không
  có trực tiếp trên PIR header/item; nếu FS cần join PIR ↔ Production Version, phải qua `Product` + `Plant`
  + MRP logic riêng (PIR không gắn trực tiếp 1 production version cụ thể theo thiết kế chuẩn SAP).

## Cross-module: Event-Based Production Costing (app "Analyze Production Costs – Event-Based")
- **`I_MfgOrderActlPlanTgtLdgrCost`** — **VERIFIED released** (`DDLS:I_MFGORDERACTLPLANTGTLDGRCOST`,
  ac=`CO-PC-OBJ-ORD-2CL`, sc=SAPSCORE, qua `released-objects-index.json`). Mô tả: "Manufacturing Order Actual Plan Target Ledger
  Specific Cost" — cube nền cho app "Analyze Production Costs". Xác nhận qua web search: view giới thiệu từ
  S/4HANA Cloud 2111, dùng để check target cost dựa trên order plan cost (param `P_TargetCostVariant`).
  Companion view `C_MfgOrderActlPlnTgtLdgrCost` (consumption layer, cần verify riêng).
  **Field chính**: `ActualQtyInCostSourceUnit`, `PlanQtyInCostSourceUnit`, `TargetQtyInCostSourceUnit`,
  `DebitActlCostInDspCrcy`, `CreditActlCostInDspCrcy`, `DebitActlFxdCostInDspCrcy`, `CrdtActlFxdCostInDspCrcy`,
  `PartnerCostCenter`, `PartnerCostCtrActivityType` (partner cost center/activity type — đúng nhu cầu FS),
  `Order`/`OrderItem`/`OrderOperation`, `Plant`, `Product`/`ProducedProduct`, `WorkCenter`.
  **KHÔNG có** field `CostComponent` — view này KHÔNG breakdown theo cost component, chỉ theo GL Account
  (`GLAccount`) + Order/Operation + Partner. Muốn cost component breakdown cho actual → quay lại gap đã nêu
  (không có CDS released).
  **Nguồn xác minh**: `docs/Phan_He_SAP_MD/CO.md` dòng 67, 740-813; `released-objects-index.json`
  (`DDLS:I_MFGORDERACTLPLANTGTLDGRCOST` state=released); WebSearch xác nhận view tồn tại từ 2111
  (SAP Community thread "Cannot access CDS views I_MfgOrderActlPlanTgtLdgrCost").
- Companion cubes cùng nhóm CO-PC-OBJ-ORD/PER: `I_MfgOrderEvtBsdWIPVariance`, `I_PCCActlTgtCostCube`,
  `I_PCCEvtBsdWIPVarianceCube` — đều có `PartnerCostCenter`/`OriginCostCenter`/`*ActivityType` nhưng tập
  trung WIP/Variance, không phải actual output cost theo cost component.

## Cross-module: Actual Activity Cost Rates (app "Manage Cost Rates – Actual")
- **`I_ServiceCostRate_2`** — **VERIFIED released** (`DDLS:I_SERVICECOSTRATE_2`, ac=`CO-OM-2CL`, SAPSCORE).
  Released-state OK nhưng **đúng nghiệp vụ hay không vẫn `[Unverified]`** — xem cảnh báo bên dưới. Fields:
  `ActivityType`, `CostCenter`, `ControllingArea`, `CostRateVarblAmount` (CURR), `CostCtrActivityTypeQtyUnit`,
  `ValidityStartDate`/`ValidityEndDate`. **CẢNH BÁO**: tên/mô tả "Service Cost Rate" + field
  `AccountingCostRateUUID`, `PersonnelNumber`, `TimesheetOvertimeCategory` gợi ý view này phục vụ
  **Service Cost Level** (nhân sự/dịch vụ), KHÔNG chắc đúng là nguồn cho app Fiori "Manage Cost Rates – Actual"
  (Activity Type Price/Fixed Rate theo Cost Center kiểu KP26/KSII cổ điển). `[Unverified]` — KHÔNG tìm được
  app ID chính xác qua Fiori Apps Library (web search không trả về "Manage Cost Rates - Actual" cụ thể, chỉ
  thấy "Manage Cost Rates – Plan" và "Manage Cost Rates – Services" F3161). **open_question**: cần verify
  trên tenant (ADT View Browser / vsp) xem app "Manage Cost Rates – Actual" dùng CDS nào — có thể là view
  chưa có trong catalog CO.md (catalog có thể thiếu record actual activity price CO-OM-CCA).
  Mitigation nếu `I_ServiceCostRate_2` sai: ① tra thêm `I_CostCenterActivityType` (master data, có Fixed
  Price field?) ② OData API activity price nếu có ③ key-user extensibility.

## Cross-module: Material Valuation / Actual-Standard Price (Material Price Analysis)
- **`I_InventoryPriceByKeyDate`** — **VERIFIED released** (`DDLS:I_INVENTORYPRICEBYKEYDATE`, ac=`CO-PC-ML-2CL`,
  SAPSCORE). Mô tả:
  "Inventory Price By KeyDate" — đúng khớp app "Display Actual Costing Result" phần price (xác nhận qua
  SAP Community: dùng cùng `I_ActlCostGMatlValueChainItem` cho movement, `I_InventoryPriceByKeyDate` cho
  price theo key date). **Field chính**: `ActualPrice` (CURR), `StandardPrice` (CURR), `InventoryPrice` (CURR),
  `MaterialPriceControl` (CHAR — S/V), `MaterialPriceUnitQty` (DEC), `Material`, `CompanyCode`,
  `ValuationArea`, `Currency`, `CurrencyRole`, `Ledger`, `FiscalYear`/`FiscalPeriod`/`FiscalYearPeriod`,
  `CostEstimate` (NUMC), `InventoryValuationType`, `AccountingValuationView`. **KHÔNG có** field tên
  `ValQuantityUnit` chính xác — chỉ có `MaterialPriceUnitQty` (DEC, không phải UNIT type) — cần verify field
  đơn vị đo qty riêng (có thể qua assoc `_Material`/`_QuantityUnit` không thấy trong catalog dòng này).
  **Nguồn xác minh**: `docs/Phan_He_SAP_MD/CO.md` dòng 594-624; WebFetch KBA 3097384 xác nhận
  `I_ML_BALANCE` + `I_InventoryPriceByKeyDate` là 2 view chính cho "check actual costs"/price info.

## Cross-module: Master data cho ZCO04/ZCO10
- **Material Document**: `I_MaterialDocumentItem_2` + `I_MaterialDocumentHeader_2` — **VERIFIED released**
  (`MM-IM-VDM-SGM-2CL`, SAPSCORE) qua `released-objects-index.json` — bằng chứng dùng thật trong GLB
  (`docs/sap-knowledge/pmc-reuse-by-module.md` dòng 76, 91, tần suất 43/5 lần). Movement type field cần tra
  field list chi tiết (`MovementType`) — assumed có (theo pattern MM-IM view chuẩn), field `MENGE` map tới
  `QuantityInEntryUnit`/`QuantityInBaseUnit` `[Unverified]` field name chính xác — cần Read source nếu cần.
- **Product Hierarchy**: `I_Product` có field `ProductHierarchy` (CHAR, single-level string chuẩn SAP —
  level 2/3 phải substring theo config độ dài hierarchy, KHÔNG có field riêng level2/level3) + assoc
  `_MDProductHierarchyNode` (multi-level, dùng `I_ProdUnivHierarchyNodeBasic`/`I_ProdUnivHierNodeText_2` —
  cả 2 released theo index). **VERIFIED**: `DDLS:I_PRODUCT` released (`LO-MD-MM-2CL`),
  `DDLS:I_PRODUNIVHIERARCHYNODEBASIC` released. Nguồn: `docs/Phan_He_SAP_MD/LO.md` dòng 3044, 4415.
  MaterialGroup (MATKL, khác Product Hierarchy) — KHÔNG có trên `I_Product` (đã ghi nhận mục 4 phía trên),
  chỉ có trên `I_MaterialLedgerCube_Lit` hoặc BOM views.
- **Production Version**: `I_ProductionVersion` — **VERIFIED released** (`DDLS:I_PRODUCTIONVERSION`,
  ac=`PP-VDM-MD-2CL`, SAPSCORE). Companion `I_ProductionVersionBasicStdVH` (value help, chưa lookup riêng).
- **Plant / Company Code + address**: `I_Plant` — **VERIFIED released** (`LO-MD-PL-2CL`).
  `I_CompanyCode` — **VERIFIED released** (`FI-GL-GL-N-2CL`). Address thường qua assoc `_Address` hoặc view
  `I_CompanyCodeAddress`/`I_AddressEmailAddress` riêng — pattern chuẩn ACME xem `nfg-company-master-cds`
  (memory) — 4 master view core company/bpartner/bankkey/plant có sẵn, ưu tiên reuse thay vì tra mới.

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
| 2026-06-30 | Verify released CO-PC views: I_ProductCostEstimate, I_ProdCostEstCostCompRawDex, I_CostComponentStdVH (CO-PC-PCP-2CL), I_ActlCostGMatlValueChainItem, I_ActualCostingRunResult (CO-PC-ACT-2CL), I_MaterialLedgerCube_Lit (CO-PC-ML-2CL). Field mapping đầy đủ. Gap: Actual Costing cost component split + ReceiptsAmount/ConsumptionsAmount + CostingRunPeriodStatus KHÔNG tìm thấy trong released CDS catalog. MaterialGroup trên Product: I_Product không có field này, chỉ có trong I_MaterialLedgerCube_Lit. | ZCO04 analysis |
| 2026-07-05 | Map nguồn dữ liệu cho ZCO04/ZCO10 (báo cáo giá thành theo cost component, Actual vs AOP/FC vs Cùng kỳ). VERIFIED chính thức qua SAP Community: KHÔNG có CDS released cho actual costing cost-component split (MLCD/MLDOCCCS) — trích dẫn nguyên văn từ SAP. Thêm view mới `I_ActualCostingActivityResult` (released CO-PC-ACT-2CL). Verify PIR thuộc PP (không phải CO): `I_ActivePlndIndepRqmt`/`Item`, `I_PlndIndepRqmtByIntKey`/`ItemByIntKey` — tất cả released PP-VDM-2CL. Verify Event-Based Production Costing: `I_MfgOrderActlPlanTgtLdgrCost` (từ 2111) — có PartnerCostCenter/ActivityType nhưng KHÔNG có CostComponent breakdown. Verify Material Valuation: `I_InventoryPriceByKeyDate` (ActualPrice/StandardPrice/MaterialPriceControl) qua KBA 3097384. Verify Master data: I_MaterialDocumentItem_2/Header_2 (MM-IM-VDM-SGM-2CL, dùng thật GLB), I_Product (ProductHierarchy field), I_Plant, I_CompanyCode — tất cả released. OPEN: `I_ServiceCostRate_2` cho "Manage Cost Rates – Actual" chưa chắc đúng view (cần verify tenant), `I_ProductionVersion` released state chưa lookup key JSON riêng. | ZCO04/ZCO10 analysis |
| 2026-07-07 | **VERIFY LIVE field/param (vsp read-only client 080) khi fix ZCO10 activation** — gotcha field-level cho báo cáo giá thành: (1) **`I_MfgOrderActlPlanTgtLdgrCost` là PARAMETERIZED cube** — 5 param bắt buộc `P_FromFiscalYearPeriod`,`P_ToFiscalYearPeriod` (`fins_fyearperiod`=YYYYPPP, vd '2026003'), `P_Ledger`, `P_CurrencyRole`(def '10'), `P_TargetCostVariant`(def '000'); **KHÔNG có PostingDate** (lọc kỳ qua param); đơn vị = **`UnitOfMeasure`** (không phải BaseUnit). (2) **`I_InventoryPriceByKeyDate` PARAMETERIZED** `P_CalendarDate` + **DEPRECATED** → dùng successor `I_InventoryPriceByKeyDate_2`. (3) **Cost rate "Manage Cost Rates – Actual"**: `I_CostCenterActivityType`=SAI (chỉ master data AT); `I_ActualCostRate` VÀ `I_AccountingCostRate_2` tồn tại + có `#PUBLIC_LOCAL_API` NHƯNG **KHÔNG released C1** (không nằm trong released-objects-index → ABAP Cloud báo "use not permitted"). ✅ ĐÚNG = **`I_ActualCostRateTP`** (RELEASED C1, CO-OM-2CL, có trong index; transactional_interface) — `CostCenter`/`ActivityType`/**`CostRateFixedAmount`**/`Currency`/`ValidityStartDate/EndDate`; view này VỐN là actual nên **KHÔNG cần lọc PlanningCategory**. ⚠️ **Bài học: `#PUBLIC_LOCAL_API` ≠ C1 released — LUÔN check `released-objects-index.json` (acme_lookup) mới chắc dùng được trong class ABAP Cloud.** (4) **`I_ProductText`** field mô tả = **`ProductName`** (không phải ProductDescription). (5) **`I_ProductionVersion`** key material = **`Material`** (Product chỉ là assoc). (6) **`I_ProductPlantCosting`** KHÔNG có ValuationQuantityUnit → dùng **`BaseUnit`**. Bài học: view CO-PC nhiều view parameterized — luôn `vsp source DDLS` check `with parameters` + `lifecycle.contract.type` (chỉ `#PUBLIC_LOCAL_API`/released mới dùng) TRƯỚC khi code. | ZCO10 activation fix |
