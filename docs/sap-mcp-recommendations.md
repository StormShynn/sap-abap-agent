---
title: SAP MCP Server Recommendations
version: 1.0.0
last_updated: 2026-07-17
audience: contributors
---

# Khuyến nghị MCP Server cho SAP ABAP Agent

Tài liệu này **không thay đổi `.mcp.json`** — chỉ audit các MCP server hữu ích mà contributor có
thể bật thêm tùy nhu cầu. Mỗi MCP dưới đây đã được đối chiếu với cấu hình hiện tại (xem mục
"Audit `.mcp.json` hiện tại") để chắc chắn **không trùng** với những gì đã có.

## Audit `.mcp.json` hiện tại

| Server              | Type  | Endpoint / Command                                                  | Vai trò |
|---------------------|-------|---------------------------------------------------------------------|---------|
| `sap-btp`           | stdio | `sap-btp-agent`                                                     | Kết nối S/4HANA Cloud, ADT CRUD, multi-profile |
| `sap-dict-bridge`   | stdio | `python -m sap_btp_agent.bridge_server`                             | Tạo Domain / Data Element / Table qua cookie auth |
| `cds-kb`            | sse   | `https://cds-kb-mcp-kit-production.up.railway.app/sse`              | Tra cứu 7,355 CDS view released (semantic search) |
| `mcp-sap-docs-btp`  | sse   | `https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse`     | Tra cứu SAP Help / Community / API Hub |
| `notion`            | http  | `https://mcp.notion.com/mcp`                                        | Đồng bộ skill user lên Notion team |

Mọi MCP trong các bảng dưới đều **bổ sung**, không thay thế.

## MCP server được khuyến nghị (opt-in)

### Tier 1 — Nên cân nhắc bật

| Server | Repo | Lý do | Cách bật (ví dụ) |
|--------|------|-------|------------------|
| `mcp-abap-adt` | `fr0ster/mcp-abap-adt` | Wrap `abap-adt-api` cho cả Cloud và On-Prem, hỗ trợ JWT/XSUAA + service-key. Bổ sung CRUD đầy đủ khi muốn chạy song song với `sap-btp` cho hệ thống ECC on-prem. | `command: "uvx"`, `args: ["mcp-abap-adt"]` |
| `mcp-sap-notes` | `marianfoo/mcp-sap-notes` | Tìm & đọc SAP Notes. Bổ sung cho `sap-docs-research`. | `command: "npx"`, `args: ["-y", "mcp-sap-notes"]` |
| `hana-mcp-server` | `HatriGt/hana-mcp-server` | HANA-native MCP — query trực tiếp khi không qua ADT (debug nhanh CDS view). | `command: "npx"`, `args: ["-y", "hana-mcp-server"]` |

### Tier 2 — Tham khảo / tình huống đặc biệt

| Server | Repo | Dùng khi |
|--------|------|----------|
| `mcp-abap-abap-adt-api` | `mario-andreschak/mcp-abap-abap-adt-api` | Nhẹ hơn `mcp-abap-adt`, chỉ wrap `abap-adt-api` thuần. Dùng khi chỉ cần Cloud. |
| `btp-sap-odata-to-mcp-server` | `lemaiwo/btp-sap-odata-to-mcp-server` | BTP CloudFoundry MCP cho OData service. Bổ sung cho `sap-odata-service`. |
| `cap-mcp-plugin` | `gavdilabs/cap-mcp-plugin` | MCP plugin cho CAP NodeJS. Phù hợp khi consultant CAP cần thao tác service thật. |
| `mcp-sap-gui` | `mario-andreschak/mcp-sap-gui` | Cho test scenario không qua ADT (mô phỏng GUI). |

### Tier 3 — Chỉ tham khảo pattern

| Server | Repo | Ghi chú |
|--------|------|---------|
| `sap-ai-mcp-servers` | `marianfoo/sap-ai-mcp-servers` | Repo catalog — dùng để rà tiếp khi MCP mới xuất hiện, không cài. |

## Lưu ý khi thêm vào `.mcp.json`

1. **Profile local**: copy `.mcp.json` mẫu của repo (`reference/.mcp.example.json` nếu có) vào
   `~/.claude.json` của user để tránh đẩy credential lên git.
2. **SSE / HTTP URL**: kiểm tra rate-limit và CORS — nhiều public SSE MCP giới hạn request/phút.
3. **stdio vs http**: ưu tiên stdio cho tool cần auth local (`abap-adt`, `hana`) vì dễ truyền
   service-key qua env var.
4. **Đặt tên nhất quán** với convention hiện tại (`sap-*` prefix), tránh trùng tên cũ.

## Nguồn tham khảo

- Repo catalog: `marianfoo/sap-ai-mcp-servers`
- ABAP AI samples: `google/ai-abap-assistant-sample`, `microsoft/aisdkforsapabap`
- Released-Object MCP (tham khảo pattern cho skill `sap-released-classes`): `ClementRingot/ROSA`
- Curriculum tham khảo (cho `sap-daily-learner`): `anfisc/abap-rap-introduction`,
  `msg-CareerPaths/sap-abap-internship`
