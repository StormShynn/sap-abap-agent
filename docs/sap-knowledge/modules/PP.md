# Knowledge Pack — Phân hệ PP (Production Planning)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `PP-VDM`, `PP-VDM-MD`, `PP-MP-DEM` (demand/PIR), `PP-VDM-2CL` (Cloud).
**Catalog gốc**: `docs/Phan_He_SAP_MD/PP.md`

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released (2602) |
|-----------|---------------|----------|
| lệnh sản xuất / production order | `I_ManufacturingOrder` | Cần verify |
| BOM / định mức nguyên vật liệu | `I_BillOfMaterial` | Cần verify |
| work center / routing | tra `PP-VDM-MD` trong catalog | Cần verify |
| PIR / Planned Independent Requirement (header) | `I_PlndIndepRqmtByIntKey` | RELEASED — ac=PP-VDM-2CL |
| PIR item + planned qty (current active) | `I_ActivePlndIndepRqmt` + `I_ActivePlndIndepRqmtItem` | RELEASED — ac=PP-VDM-2CL |
| PIR item + period (FORECASTYEARMONTH) — history/all versions | `I_PlndIndepRqmtItemHistory` | RELEASED — ac=PP-VDM-2CL |
| PIR item by internal key (flat item) | `I_PlndIndepRqmtItemByIntKey` | RELEASED — ac=PP-VDM-2CL |
| PIR type / Requirement Type text | `I_PlndIndepRqmtType`, `I_PlndIndepRqmtTypeText` | RELEASED — ac=PP-VDM-2CL |
| PIR RAP BO (transactional — write) | BDEF `I_PlndIndepRqmtTp` | RELEASED — ac=PP-MP-DEM-2CL |
| Production Version (master data) | `I_ProductionVersion` | RELEASED — ac=PP-VDM-MD-2CL |

## 1. PIR — Planned Independent Requirements (PBDNR / MD63 equivalent)

### View landscape (tất cả confirmed RELEASED 2602, ac=PP-VDM-2CL, sc=SAPSCORE)

| View | Mô tả | Dùng khi |
|------|-------|----------|
| `I_PlndIndepRqmtByIntKey` | Header PIR (ABAP key: PlndIndepRqmtInternalId) | Filter theo Version, RequirementPlan, Plant, Product |
| `I_PlndIndepRqmtItemByIntKey` | Item PIR (flat, WORKINGDAYDATE-based) | Lấy planned qty theo date; JOIN header để lấy Version |
| `I_PlndIndepRqmtItemHistory` | Item history dạng phẳng — tích hợp cả header fields | Query tốt nhất cho pivot theo tháng: có FORECASTYEARMONTH trực tiếp |
| `I_ActivePlndIndepRqmt` | Header PIR — chỉ active version | Chỉ đọc PIR đã activate |
| `I_ActivePlndIndepRqmtItem` | Item PIR — chỉ active version | Chỉ đọc item của PIR đã activate |

### Field mapping — FS requirement vs CDS field

| FS requirement | CDS field | View chứa field | Ghi chú |
|----------------|-----------|-----------------|---------|
| Material (mã vật tư) | `Product` | cả 5 view | CHAR — map tới MATNR |
| Plant | `Plant` | cả 5 view | CHAR |
| Version (VERSB) — AOP "ZA", FC "00" | `PlndIndepRqmtVersion` | `I_PlndIndepRqmtByIntKey`, `I_ActivePlndIndepRqmt` | CHAR(2). Trong `ItemHistory` phải đi qua assoc `_PlndIndepRqmt` |
| Version Active flag (lọc = Null / chưa active) | `PlndIndepRqmtIsActive` | `I_PlndIndepRqmtByIntKey`, `I_PlndIndepRqmtItemHistory` | CHAR — space = inactive, 'X' = active |
| Requirements Plan (PBDNR) — "M0526.V061" | `RequirementPlan` | cả 5 view | CHAR — giá trị raw từ PBDNR |
| Planned Quantity (số lượng kế hoạch) | `PlannedQuantity` | item views | QUAN |
| Period — tháng/năm (pivot column) | `ForecastYearMonth` (NUMC 6, format YYYYMM) | `I_PlndIndepRqmtItemHistory` | Dùng view này cho pivot theo tháng |
| Period — ngày làm việc cụ thể | `WorkingDayDate` | `I_PlndIndepRqmtItemByIntKey`, `I_ActivePlndIndepRqmtItem` | DATS — granularity ngày |
| Forecast period type (M=monthly, W=weekly) | `ForecastPeriodType` | `I_PlndIndepRqmtItemHistory` | lọc = 'M' cho monthly |
| Withdrawal qty | `WithdrawalQuantity` | item views | QUAN |
| Deletion flag | `PlndIndepRqmtIsToBeDeleted` | `I_PlndIndepRqmtByIntKey`, `I_PlndIndepRqmtItemHistory` | lọc = '' để bỏ qua deleted |
| UoM | `BaseUnit` | item views | UNIT |

### Gap quan trọng — Production Version

`ProductionVersion` (ABAP field VERID trong PLAF/MDTC) KHÔNG có trong bất kỳ PIR view nào.
PIR không gắn với production version tại data model. "SUM theo tất cả production version" trong FS
thực tế có nghĩa là SUM tất cả rows cùng Material+Plant+Period+Version (VERSB) — tức là
GROUP BY Product, Plant, ForecastYearMonth, PlndIndepRqmtVersion, RequirementPlan.

### Recommended query pattern cho ZCO04

Dùng `I_PlndIndepRqmtItemHistory` (phẳng — có cả header fields inline):
- Filter: `Plant IN @plant_range`, `Product IN @material_list` (từ Material Group)
- Filter: `PlndIndepRqmtVersion IN ('ZA', '00')` — qua `_PlndIndepRqmt\PlndIndepRqmtVersion` hoặc join header
- Filter: `PlndIndepRqmtIsActive = ''` (inactive — chưa active) HOẶC bỏ filter nếu muốn ALL
- Filter: `RequirementPlan LIKE 'M%'` cho FC (pattern M<MM><YY>.<Plant>)
- Filter: `ForecastPeriodType = 'M'` (monthly buckets)
- Aggregate: `SUM(PlannedQuantity)` GROUP BY `Product, Plant, ForecastYearMonth, PlndIndepRqmtVersion, RequirementPlan`
- Note: `PlndIndepRqmtVersion` và `PlndIndepRqmtIsActive` có sẵn trong `I_PlndIndepRqmtItemHistory` trực tiếp (không cần join), đã xác nhận tại catalog lines 6813, 6759 (header view).

QUAN TRONG: Catalog `I_PlndIndepRqmtItemHistory` KHÔNG liệt kê `PlndIndepRqmtVersion` là direct scalar field — field này ở header view. Cần xác nhận qua ADT View Browser hoặc join tường minh với `I_PlndIndepRqmtByIntKey` on `PlndIndepRqmtInternalId`.

## 5. Ghi chú
- PP gắn MM (material, goods movement) và QM (inspection).
- PIR read-only → dùng VDM interface views (không dùng table PBIM/MDTB trực tiếp).
- PIR write (tạo/sửa) → RAP BO `I_PlndIndepRqmtTp` (BDEF released PP-MP-DEM-2CL).
- `I_PlndIndepRqmtItemHistory` = view "phẳng" tốt nhất cho báo cáo vì có FORECASTYEARMONTH + header fields trong cùng 1 view.

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
| 2026-06-30 | PIR views — verify released 2602 toàn bộ; field mapping VERSB/PBDNR/IsActive/ForecastYearMonth; gap ProductionVersion; query pattern ZCO04 | AGENTS_PP (ZCO04 request) |
