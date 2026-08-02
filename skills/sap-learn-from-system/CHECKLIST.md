# Checklist — Học từ hệ thống SAP (MCP) + Notion

Dùng mỗi session `sap-learn-from-system`. In lại cho user khi kết thúc.

## Trước khi đọc

- [ ] MCP Core đã đăng ký (`mcp-sap-connect` / `sap-btp`, …)
- [ ] `sap_ping` hoặc `mcp-sap-connect ping` **OK**
- [ ] Đã chọn profile đúng (nếu multi-profile)
- [ ] Có mục tiêu: object cụ thể **hoặc** package / chủ đề hẹp
- [ ] Giới hạn **≤ 5** object / lần

## Trong lúc học

- [ ] Đọc object **thật** qua MCP — không đoán
- [ ] Ưu tiên đa dạng loại (table / class / CDS) nếu khám phá tự do
- [ ] Không dump toàn bộ source lớn vào chat hoặc file lesson

## Ghi nhận (local)

- [ ] Lesson card chỉ chứa **pattern** (bullet), meta package/profile/ngày
- [ ] File nằm dưới `<agent-home>/memory/semantic/notes/system/` và/hoặc `lessons/system/`
- [ ] Không ghi credential, client data, bulk ABAP khách hàng
- [ ] Trường `Share:` trên lesson: `pending` | `shared` | `skipped-private` | `skipped-error`

## Notion (SAP Skills)

- [ ] `python …/notion_skills_db.py get` đã resolve id (default / env / pin)
- [ ] Đã **search** trùng trước khi tạo page mới
- [ ] Không private / user không cấm share
- [ ] Page chỉ pattern đã scrub — Topic dạng `[System] OBJECT — …`
- [ ] Bỏ qua `Tags` nếu schema chưa có option
- [ ] Fail-open: lỗi Notion → vẫn xong local, ghi `skipped-error`
- [ ] Báo user: đồng bộ OK **hoặc** lý do bỏ qua

## Kết thúc

- [ ] Tóm tắt 3–7 điểm học được
- [ ] Gợi ý: tip/quiz (`sap-daily-learner`) hoặc hỏi module (`sap-ask-consultant`)
- [ ] (Tuỳ chọn) Session học object khác?

## Không làm

- [ ] ~~Dump source đầy đủ lên Notion~~
- [ ] ~~Tạo database Notion im lặng~~
- [ ] ~~Promote `reference/modules/`~~ (dùng daily-learner 3c nếu cần)
- [ ] ~~Bắt buộc Hermes Agent MCP~~
