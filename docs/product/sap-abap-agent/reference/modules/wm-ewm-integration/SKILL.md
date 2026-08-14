---
name: wm-ewm-integration
description: Knowledge note tổng hợp **WM vs EWM**, integration patterns, side-by-side architecture trên S/4HANA Cloud. Khác với `sap-wm-cloud/SKILL.md` (seed knowledge cho WM consultant). Dùng khi cần quyết định dùng WM embedded, EWM decentralized, hay EWM trên BTP.
effort: low
model: haiku
---

# WM / EWM — Integration & Architecture Knowledge Note

Module con của plugin, tập trung vào **so sánh kiến trúc WM vs EWM** và pattern tích hợp với
MM/SD/PP/TM. Không thay thế:
- `sap-wm-cloud/SKILL.md` — knowledge consultant WM (SSCUI, Fiori app, scope item).
- `sap-ewm-cloud/SKILL.md` — knowledge consultant EWM.
- `sap-wm-consultant-cloud`, `sap-ewm-consultant-cloud` — agents consult thật.

## 1. Tổng quan: WM vs EWM

| Tiêu chí                | WM (Warehouse Management)       | EWM (Extended Warehouse Management)        |
|--------------------------|---------------------------------|---------------------------------------------|
| Kiến trúc                | Embedded trong S/4HANA          | Decentralized (riêng instance)             |
| Cloud availability       | ❌ (legacy, không trên Public Cloud) | ✅ (qua BTP hoặc S/4HANA EWM add-on)   |
| Warehouse task           | Transfer Order (TO)             | Warehouse Task (WT)                         |
| Storage bin              | Bin master                      | Bin master + storage section                |
| HU (Handling Unit)       | Hỗ trợ cơ bản                  | First-class citizen                          |
| Yard management          | Không                           | Có                                            |
| Labor management         | Không                           | Có                                            |
| Wave management          | Hạn chế                         | Full                                          |
| MFS (Material Flow Sys)  | Không                           | Có (PLC integration)                         |

**Tóm tắt**: WM trên Cloud = không có (cần on-prem hoặc Private Cloud). EWM là tương lai.

## 2. Cloud Public Edition — quyết định kiến trúc

```
S/4HANA Cloud Public Edition
  └─ Không có WM/EWM embedded
       └─ Cần EWM trên BTP (side-by-side) HOẶC SAP EWM Cloud add-on
```

Các option:

| Option                                  | Phù hợp với                              | Ghi chú                              |
|------------------------------------------|------------------------------------------|--------------------------------------|
| **EWM trên BTP**                         | New implementation, multi-tenant SaaS   | Subscription riêng, integration qua OData/RFC |
| **SAP EWM Cloud add-on**                  | Đã có EWM on-prem muốn migrate lên      | Cần license add-on                   |
| **SAP Business Network for Logistics**    | Yard / track & trace                      | External collaboration               |

## 3. EWM trên BTP — Architecture

```
┌────────────────────────────────────────┐
│ S/4HANA Cloud (MM/SD/PP)              │  ← Master + inbound/outbound posting
└────────────────────────────────────────┘
                ↕ (iDoc / OData / EWM Integration)
┌────────────────────────────────────────┐
│ EWM trên BTP                          │  ← Warehouse execution
│ - Inbound delivery → Put-away          │
│ - Outbound delivery → Pick + Pack       │
│ - HU management                        │
└────────────────────────────────────────┘
                ↕ (WebSocket / MQTT)
┌────────────────────────────────────────┐
│ MFS (Material Flow System)             │  ← PLC / Conveyor / Robot
└────────────────────────────────────────┘
```

## 4. Integration với MM

| Luồng                     | Vai trò MM              | Vai trò EWM                    |
|---------------------------|--------------------------|--------------------------------|
| Inbound delivery          | MM tạo Inbound Delivery  | EWM receive + put-away          |
| Outbound delivery         | MM tạo Outbound Delivery | EWM pick + pack                 |
| Goods receipt (GR)        | MM post GR                | EWM trigger GR event            |
| Goods issue (GI)          | MM post GI                | EWM trigger GI event            |
| Stock overview            | MM Stock Type             | EWM Bin + Stock status          |

Trên Cloud Public, **Stock Overview** trong Fiori app thấy stock tổng hợp từ cả S/4HANA + EWM
(khác bin-level).

## 5. Integration với SD

- **Outbound Delivery Order**: SD tạo delivery → EWM pick + pack → SD post goods issue.
- **Picking**: EWM tạo warehouse task → pick confirm → update delivery quantity.
- **Packing**: EWM HU management → reverse HU back to delivery.

## 6. Integration với TM (Transportation Management)

- **Shipping integration**: TM tạo freight order → EWM outbound delivery stage.
- **Yard**: TM yard logistics + EWM yard management (chỉ decentralized EWM).

## 7. Common EWM Configuration (qua SSCUI / Fiori)

| Khu vuc                    | Fiori app                              |
|----------------------------|----------------------------------------|
| Warehouse master           | Manage Warehouses                       |
| Storage bin                | Manage Bins                             |
| HU type                    | Manage Handling Unit Types              |
| Packaging spec             | Manage Packaging Specifications         |
| Wave                       | Manage Waves                            |
| Warehouse task              | Manage Warehouse Tasks                  |

## 8. Side-by-side Extension Patterns

| Pattern                | Dùng khi                              | Tool                |
|------------------------|----------------------------------------|---------------------|
| Custom field trên HU   | Thêm field business info               | SSCUI Custom Field  |
| Custom warehouse task  | Logic pick/pack custom                 | ABAP Cloud BAdI     |
| Custom print form      | Picking/Packing label format           | Adobe Form + Cloud BAdI |
| RAP integration        | Đọc EWM stock cho dashboard custom    | RAP + OData V4      |
| SAP Build             | Mobile scanner cho warehouse           | SAP Build           |

## 9. Anti-pattern

- ⚠️ Cố gắng dùng WM transaction (`LB01`, `LT01`) trên Cloud — không released.
- ⚠️ Hardcode bin location trong code — dùng storage section/search.
- ⚠️ Dùng EWM on-prem cho Public Cloud — kiến trúc không tương thích.
- ⚠️ Bypass HU nếu quy trình yêu cầu trace — mất nguồn gốc.

## 10. Liên kết với các skill khác

- **Consultant WM/EWM**: `sap-wm-consultant-cloud`, `sap-ewm-consultant-cloud`.
- **Seed knowledge**: `sap-wm-cloud/SKILL.md`, `sap-ewm-cloud/SKILL.md`.
- **Integration**: `sap-mm-consultant-cloud`, `sap-sd-consultant-cloud`, `sap-tm-consultant-cloud`.
- **Released class**: `sap-released-classes` mục EWM integration (nếu có).
- **BTP architecture**: `sap-btp-connectivity` (đọc từ module này).

## 11. Nguồn tham khảo

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — module WM/EWM.
- [`marianfoo/sap-ai-mcp-servers`](https://github.com/marianfoo/sap-ai-mcp-servers) — EWM MCP (nếu có).
- SAP Help: EWM trên BTP, S/4HANA EWM Integration.
