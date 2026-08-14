# Knowledge Pack — Phân hệ QM (Quality Management)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `QM-IM-*` (inspection / inventory management quality).
**Catalog gốc**: `docs/Phan_He_SAP_MD/QM.md`

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released |
|-----------|---------------|----------|
| lô kiểm tra / inspection lot | `I_InspectionLot` | `[Unverified]` |
| kết quả kiểm / inspection result | tra `QM-IM` trong catalog | `[Unverified]` |
| thông báo chất lượng / QN / claim | `I_QltyNotification` (header) + `I_QualityNotificationItem` (item) | ✅ verified (ZSD04C, GLB ZQM01) |

> ⚠️ Tên view THẬT là **`I_QltyNotification`** (viết tắt "Qlty"), KHÔNG phải `I_QualityNotification`.

## 1. Quality Notification — field name THẬT (verified, KHÔNG đoán)

Verified từ report đã activate trên tenant: `PUB_GLB_CODE/.../src/zfpt_report/zqm/zqm01/zi_qm_zqm01.ddls.asddls`
(đọc file này khi cần thêm field QM — nguồn sự thật chạy thật).

**`I_QltyNotification` (header)** — field có thật:
- Key/loại: `QualityNotification` (key), `NotificationType`
- Đối tượng: `Material`, `Batch`, `Customer`, `Supplier`, `ProductionOrder`, `OrderDocument`
  (số order tham chiếu — dùng làm link tới `I_SalesOrder`)
- Người/ngày: `CreatedByUser`, `CreationDate`, `LastChangedByUser`, `LastChangedDate`,
  `NotificationReportingDate`, `NotificationRequiredStartDate`, `NotificationRequiredEndDate`,
  `NotificationCompletionDate` (rỗng = chưa hoàn thành → suy status DONE/OPEN)
- Text/phân loại: `NotificationText` (short text), `NotificationCodeGroup`/`NotificationCodeID`/
  `NotificationCatalog`, `NotificationPriority`/`NotificationPriorityType`
- Số lượng: `NotificationComplaintQuantity`/`NotificationReferenceQuantity`/
  `NotificationInternalQuantity`/`NotifReturnDeliveryQuantity` + `NotificationQuantityUnit`
- Assoc header: `_QltyNotificationHdrTask`

**`I_QualityNotificationItem` (item)**: `QualityNotification`, `NotificationItem`, `NotificationItemText`,
`Material`, `Batch`, `Plant`, `CompanyCode`, `PurchaseOrder`, `OrderID`… Assoc: `_QltyNotificationCause`/
`_QltyNotificationTask`/`_QltyNotificationActivity`/`_NotifItmObjectPartCode`.

- Item là **to-many** theo QualityNotification → KHÔNG select scalar field item ở view grain=header (gây
  fan-out → OData V4 "Duplicate key predicate"); lấy field header-level hoặc qua assoc to-one.

**❌ Field SAI hay đoán nhầm (KHÔNG tồn tại — đừng dùng):**
`QualityNotificationType`, `QualityNotificationStatus`, `NotificationCreationDate`,
`MalfunctionStartDate`, `QualityNotificationCodeGroup/Code`, `ReportedByUser`, `SalesOrder` (trên noti).

- Product text: dùng `I_ProductText.ProductName` + `Language = $session.system_language`
  (KHÔNG phải `I_ProductDescription`/'E').

*(memory: qm-quality-notification-fields; ZSD04C scaffold ban đầu đoán field → pull báo "column unknown",
ZI không activate)*

## 2-4. *(điền dần khi verify — xem `_template.md`)*

## 5. Ghi chú
- QM gắn MM (goods receipt) và PP (production order inspection).
- Field chưa rõ → placeholder cast (xem `cds-annotations.md` §CAST NUMC), KHÔNG đoán.

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
| 2026-07-03 | Verified field `I_QltyNotification`/`I_QualityNotificationItem` + list field SAI (từ ZSD04C/GLB ZQM01) | sync memory→pack |
