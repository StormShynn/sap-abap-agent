# Knowledge Pack — Phân hệ MM (Materials Management)

> Đọc trước khi tra catalog; ghi lại sau khi verify. Released phải verify riêng. Không bịa.

**Sub-components**: `MM-PUR-*` (purchasing), `MM-IM-*` (inventory management).
**Catalog gốc**: `docs/Phan_He_SAP_MD/MM.md` (346 views)

## Keyword → CDS candidate (cần verify released)
| Keyword FS | CDS candidate | Released |
|-----------|---------------|----------|
| đơn mua / purchase order | `I_PurchaseOrder`, `I_PurchaseOrderItem` | `[Unverified]` |
| purchase requisition / PR | `I_PurchaseRequisition` | `[Unverified]` |
| nhà cung cấp / supplier | `I_Supplier` (master: AP-MD-BP) | `[Unverified]` |
| vật tư / material / product | `I_Product` | `[Unverified]` |
| chứng từ kho / goods movement | `I_MaterialDocumentItem`, `I_MaterialStock` | `[Unverified]` |

## 1-4. *(điền dần khi verify — xem `_template.md`)*

## 5. Ghi chú
- Master data Supplier/BP thực ra ở `AP-MD-BP` (file `AP.md`); MM tham chiếu.

## Changelog
| Ngày | Đã thêm/verify | Bởi |
|------|----------------|-----|
| 2026-06-27 | Khởi tạo seed | thiết kế module-agent |
