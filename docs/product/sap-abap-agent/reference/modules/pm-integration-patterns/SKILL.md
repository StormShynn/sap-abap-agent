---
name: pm-integration-patterns
description: Knowledge note tổng hợp **integration pattern** giữa PM (Plant Maintenance) với FICO, MM, PS, HR — khác với `sap-pm-cloud/SKILL.md` (seed knowledge cho module consultant). Dùng khi contributor cần tra nhanh pattern tích hợp để scaffold extension.
effort: low
model: haiku
---

# PM — Integration Patterns Knowledge Note

Module con của plugin, tập trung vào **integration patterns** của PM với các module khác.
Không thay thế:
- `sap-pm-cloud/SKILL.md` — knowledge consultant PM (SSCUI, Fiori app, scope item).
- `sap-pm-consultant-cloud` — agent consult thật.

## 1. PM ↔ FICO (Settlement)

Maintenance order / WBS element có thể settle sang Cost Center / WBS / Profit Center / Order
để tính giá thành.

```
Maintenance Order (PM)
  └─ Settlement rule (CO)
       ├─ Settlement receiver: Cost Center / WBS / Order
       ├─ Settlement type: PER (period), FUL (full), PRV (proportional)
       └─ Distribution rule (cho multi-receiver)
```

Trên Cloud Public Edition:
- Settlement rule được expose qua **Manage Maintenance Orders** Fiori app.
- CO objects (cost center, WBS) tạo qua Fiori apps tương ứng.
- Released API cho settlement: `cl_pm_order_ops`, `IF_PM_ORDER_MGMT_RT` (xem
  `sap-released-classes` mục "RAP Runtime" + extensions).

## 2. PM ↔ MM (Material & Service)

| Luồng                         | Vai trò PM               | Vai trò MM                  |
|-------------------------------|--------------------------|------------------------------|
| Material withdrawal (Goods issue) | PM ghi nhận vật tư tiêu hao | MM giảm stock                |
| Service entry sheet          | PM accept dịch vụ        | MM accept PO service line    |
| Purchase requisition từ PM order | PM tạo PR tự động     | MM convert PR → PO           |
| Subcontracting                | PM outsource component    | MM xử lý PO subcontracting    |

Trên Cloud Public Edition, **service entry sheet** thường dùng Fiori app
**Manage Service Entries** (không có IW41/IW42 on-prem).

## 3. PM ↔ PS (Project System)

Maintenance order có thể là **network** (PMWO) hoặc **WBS element** (PS):

```
Project (PS-PRJ)
  └─ WBS element
       └─ Network (PMWO) — Maintenance Order thuộc PS
            ├─ Activity (Maintenance activity)
            └─ Material component
```

Dùng khi dự án bảo trì lớn cần phân bổ chi phí theo WBS hierarchy.

## 4. PM ↔ HR (Maintenance Worker)

PM gắn **personnel number** cho maintenance order (người thực hiện):

- Personnel master: HR module.
- Skill / qualification: HR-OM infotype 163.
- Capacity planning: tích hợp với PP / PS cho resource scheduling.

## 5. Equipment ↔ Functional Location

```
Functional Location (FL) ← hierarchy phân cấp theo vị trí thực tế
  └─ Equipment (EQ) ← thiết bị lắp đặt tại FL
       └─ Sub-equipment (optional)
            └─ Object link (object link to FI asset, sales bom, ...)
```

**Best practice** trên Cloud:
- Tạo FL theo cấu trúc phân cấp `ZFL_<area>_<line>_<machine>` (vd `ZFL_A1_L2_M01`).
- Equipment đặt tại 1 FL, có thể move giữa các FL qua **Install/Deinstall**.
- Object link sang FI Asset: tự động qua integration.

## 6. Maintenance Plan Patterns

| Pattern              | Mô tả                              | Use case                       |
|----------------------|------------------------------------|--------------------------------|
| **Time-based**       | Lập kế hoạch theo chu kỳ thời gian  | Bảo trì định kỳ hàng tháng    |
| **Performance-based**| Lập kế hoạch theo meter (counter)   | Bảo trì sau N giờ chạy         |
| **Multi-counter**    | Kết hợp counter & thời gian       | Maintenance strategy phức tạp  |
| **Strategy-based**   | Strategy = package các task        | Task list thay đổi theo loại   |

Tạo maintenance plan qua Fiori app **Manage Maintenance Plans**.

## 7. Side-by-side Extension Patterns

Khi cần mở rộng PM trên Cloud:

| Pattern                | Dùng khi                              | Tool                |
|------------------------|----------------------------------------|---------------------|
| Custom fields          | Thêm 1-3 field business info           | SSCUI Custom Fields |
| Custom business object | Cần entity riêng                      | SSCUI CBO            |
| Cloud BAdI             | Logic validation/defaulting           | ABAP Cloud BAdI     |
| RAP + Side-by-side     | UI custom trên dữ liệu PM             | RAP + Steampunk     |
| SAP Build Process Automation | Workflow approval               | SAP Build           |

Xem skill `sap-extensibility` + `sap-cloud-migration` cho decision matrix.

## 8. Anti-pattern

- ⚠️ Hardcode equipment/FL ID trong code — dùng input parameter.
- ⚠️ Modify PM order sau khi settlement — không cho phép.
- ⚠️ Dùng `IW31`/`IW32` legacy transaction — không released trên Cloud.
- ⚠️ Bypass approval workflow qua direct status change — luôn qua Fiori app hoặc released API.

## 9. Liên kết với các skill khác

- **Module consultant**: `sap-pm-consultant-cloud`.
- **Seed knowledge**: `sap-pm-cloud/SKILL.md`.
- **Integration**: `sap-mm-consultant-cloud`, `sap-co-consultant-cloud`, `sap-ps-consultant-cloud`.
- **Released class**: `sap-released-classes`.
- **Extensibility**: `sap-extensibility`, `sap-cloud-migration`.

## 10. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module PM.
- [`marcellourbani/vscode_abap_remote_fs`](https://github.com/marcellourbani/vscode_abap_remote_fs) —
  extension pattern cho PM.
- SAP Help: PM trên S/4HANA Cloud Public Edition, Settlement Guide.
