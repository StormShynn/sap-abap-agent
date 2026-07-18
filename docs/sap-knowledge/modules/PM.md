# Knowledge Pack — Phân hệ PM (Plant Maintenance)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `PM-EQM-*` (equipment / technical objects).
**Catalog gốc**: `docs/Phan_He_SAP_MD/PM.md`

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released |
|-----------|---------------|----------|
| thiết bị / equipment | `I_Equipment` | `[Unverified]` |
| functional location | `I_FunctionalLocation` | `[Unverified]` |
| lệnh bảo trì / maintenance order | `I_MaintenanceOrder` | `[Unverified]` |
| thông báo bảo trì / notification | `I_MaintenanceNotification` | `[Unverified]` |

## 1-4. *(điền dần khi verify — xem `_template.md`)*

## 5. Ghi chú
- PM equipment gắn tài sản cố định FI-AA khi cần.

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
