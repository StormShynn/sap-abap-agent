# Mở rộng tra cứu Notion ra 25 agent tư vấn (qua routing trung tâm)

## Context

Phiên trước đã xây "đọc trước/ghi sau" Notion **chỉ trong `sap-daily-learner`** (theo lựa chọn user
lúc đó). Giờ user muốn mở rộng phần **đọc** (tra Notion) ra cả 25 agent tư vấn module (SD/FI/MM/...),
với yêu cầu rõ: local = bản offline, Notion = bản online, nếu local mất thì tự lấy lại từ Notion khi
cần — và hỏi việc lưu trữ kiểu này có nặng ổ cứng không, đã có hướng giải quyết chưa.

Đã verify (không đoán) 2 fact kiến trúc quan trọng, quyết định cách làm:

1. **27 agent file** (25 module consultant + `sap-docs-researcher` + `abap-reviewer`) đều có
   `disallowedTools: [Write, Edit]` trong frontmatter (grep xác nhận toàn bộ) — KHÔNG thể tự ghi
   file. Chỉ `agents/sap-daily-learner.md` có `Write, Edit`. => Không thể/không nên copy logic ghi
   file vào 25 agent riêng lẻ.
2. **`skills/sap-ask-consultant/SKILL.md`** (routing trung tâm, dispatch TẤT CẢ 27 agent — đã đọc
   toàn bộ file) là 1 **skill**, không phải agent — frontmatter của nó **không có** `tools:`/
   `disallowedTools:` nên chạy full quyền (kể cả Write) trong context chính, TRƯỚC khi dispatch
   xuống agent con qua Agent tool. => Đây là **đúng 1 chỗ duy nhất** cần sửa để mọi agent hưởng lợi,
   không cần đổi quyền của agent nào, không cần sửa 25 file.
3. `reference/scripts/cleanup_agent_home.py` **cố tình loại trừ** `memory/` khỏi việc dọn cache
   (docstring: "kien thuc lau dai, khong phai log") — đúng, vì skill là kiến thức lâu dài, không nên
   xoá theo tuổi như cache/log.

## Thiết kế

### Đọc (mở rộng ra 27 agent, qua routing trung tâm — KHÔNG sửa 25 file agent)

Thêm 1 bước mới trong `skills/sap-ask-consultant/SKILL.md`, chèn giữa "Bước 4: Tổng hợp dispatch"
và "Bước 6: Dispatch song song" (đổi số các bước sau nó thành 5→6, 6→7...):

**Bước 5 (mới) — Tra cứu kiến thức có sẵn cho từng module sắp dispatch:**
1. **Local trước (offline, luôn làm, rẻ)**: `Glob`/`Grep` `memory/procedural/skills/*<module>*`
   (đường dẫn qua `agent_home.py`, xem SKILL.md `sap-daily-learner` mục 1). Thấy → dùng luôn, đưa
   vào context khi dispatch, **không gọi Notion** (tránh round-trip mạng cho câu đã có sẵn local).
2. **Notion khi local miss (online, chỉ khi cần)**: gọi tool search của MCP `notion` theo
   module + từ khoá. Thấy → tool fetch lấy nội dung, đưa vào context khi dispatch, **đồng thời tự
   ghi 1 bản local cache** vào `memory/procedural/skills/` (`sap-ask-consultant` tự làm được vì
   không bị giới hạn Write — đây là copy cơ học nội dung đã có sẵn/đã duyệt trên Notion, KHÔNG phải
   phán đoán "có nên tạo skill mới" — việc đó vẫn thuộc riêng `sap-daily-learner`).
3. Không thấy ở cả 2 → dispatch bình thường như hiện tại, không có gì thay đổi.
4. **Fail-open bắt buộc**: lỗi ở bước 1 hoặc 2 (Notion chưa connect, mất mạng...) → bỏ qua, dispatch
   bình thường, không chặn routing — cùng triết lý các nơi khác trong repo.

"Clone online về" khi mất local: **xảy ra tự nhiên theo lazy fetch ở bước 2** — không cần tool/lệnh
resync hàng loạt riêng. Lần đầu hỏi lại 1 chủ đề sau khi mất local, bước 2 tự fetch lại từ Notion +
tự cache lại, không cần thao tác gì thêm.

**Ghi (viết skill mới) — GIỮ NGUYÊN, không mở rộng lần này**: vẫn chỉ `sap-daily-learner` (đúng chỗ
duy nhất có quyền Write + có logic điều kiện kích hoạt ≥3 bước/config cụ thể/phản hồi tích cực đã
được kiểm chứng). Không thêm auto co-dispatch daily-learner sau mỗi câu trả lời của 25 consultant
lần này — user không yêu cầu, và sẽ tốn thêm 1 lượt agent cho mỗi câu hỏi dù đơn giản. Có thể làm
sau nếu user muốn.

### Đánh giá dung lượng ổ cứng

Tính cụ thể: mỗi skill doc ~2-5KB text (theo ví dụ thực tế trong SKILL.md mục 3). Kịch bản nặng
— 10,000 skill tích luỹ qua nhiều năm, cả team — vẫn chỉ ~30-50MB. **Không phải rủi ro thật** ở quy
mô nội dung này (text markdown), không cần cơ chế giải quyết phức tạp.

Vẫn thêm 1 phần nhẹ cho yên tâm (đúng tinh thần user hỏi "có hướng giải quyết chưa"): mở rộng
`cleanup_agent_home.py` in thêm 1 dòng báo cáo tổng dung lượng hiện tại của
`memory/procedural/skills/` — **chỉ hiển thị, không tự xoá** (tôn trọng đúng nguyên tắc đã ghi trong
chính docstring file này: kiến thức lâu dài không xoá theo tuổi/dung lượng như cache).

## Thay đổi

1. **`skills/sap-ask-consultant/SKILL.md`** — thêm Bước 5 (Tra cứu kiến thức) như thiết kế trên,
   đánh số lại các bước sau, cập nhật "Output format" nếu cần ghi chú khi có context từ local/Notion.
2. **`reference/scripts/cleanup_agent_home.py`** — thêm hàm nhỏ báo cáo dung lượng
   `memory/procedural/skills/` (read-only, không xoá), in thêm 1 dòng trong `main()`.
3. **`skills/sap-daily-learner/SKILL.md`** mục 3b — thêm 1 câu cross-reference: giờ
   `sap-ask-consultant` cũng đọc/ghi chung kho local + Notion này cho 25 agent tư vấn khác.
4. **`README.md` / `index.html` / `CHANGELOG.md`** — cập nhật ngắn gọn phạm vi (giờ 25 agent tư vấn
   cũng hưởng lợi, không chỉ Daily Learner), theo đúng quy trình verify HTML đã dùng các lần trước.

## Verification

- Đọc lại `skills/sap-ask-consultant/SKILL.md` sau khi sửa — đối chiếu số thứ tự bước không bị lệch,
  không phá vỡ logic keyword scoring/coupling/dispatch hiện có (chỉ thêm 1 bước, không sửa các bước
  khác).
- HTML: tag-balance checker + `node --check` + mô phỏng `translatePage()` cho chuỗi VI mới trong
  `index.html`, đúng quy trình 2 lần trước.
- Không thể test thật lệnh gọi Notion (chưa authenticate trong phiên này) — nêu rõ giới hạn.
- Trả lời rõ cho user phần tính toán dung lượng (không chỉ ghi trong plan, nói thẳng trong phản hồi).

---

# Auto-Skill Creation đồng bộ 2 chiều với Notion (team-shared) — ĐÃ HOÀN THÀNH (tham khảo)

## Context

Phiên trước đã thêm MCP server `notion` (hosted OAuth, auto-bundle trong `.mcp.json`) để team
dùng chung 1 workspace Notion làm nơi ghi/tra skill notes. User giờ muốn khép kín vòng lặp: khi
`sap-daily-learner` **tự sinh 1 skill mới** (Auto-Skill Creation Engine đã có sẵn — SKILL.md mục
3), ngoài lưu local như hiện tại thì **đẩy luôn lên Notion** để cả team thấy; ngược lại, trước khi
tự giải quyết 1 vấn đề từ đầu, **tra Notion trước** — nếu một thành viên khác đã hỏi/tạo skill
tương tự rồi thì lấy ra dùng lại thay vì làm lại từ đầu. "Đóng góp qua lại" giữa các user qua 1
kho tri thức chung.

Đã xác nhận với user 2 quyết định thiết kế (AskUserQuestion):
- **Phạm vi**: chỉ trong `sap-daily-learner` (gắn vào đúng chỗ đã có cơ chế dedup cục bộ — Auto-Skill
  Creation Engine điều kiện 4 "không trùng lặp"), KHÔNG áp dụng cho 25 agent tư vấn khác — tránh
  thêm round-trip MCP cho mọi câu hỏi.
- **Đẩy lên Notion**: tự động, KHÔNG hỏi xác nhận trước (khác đề xuất ban đầu của mình là nên hỏi
  trước vì nội dung giờ hiển thị cho cả team — user chọn ưu tiên mượt/tự động).

Đã research thực tế (không đoán):
- Tool thật của Notion hosted MCP (`mcp.notion.com/mcp`, theo
  [developers.notion.com/guides/mcp/mcp-supported-tools](https://developers.notion.com/guides/mcp/mcp-supported-tools)):
  `notion-search` (semantic search toàn workspace), `notion-fetch` (lấy full content 1 page/database
  theo URL/ID), `notion-create-pages` (tạo page, có thể dưới 1 database qua `data_source_id`),
  `notion-create-database`, `notion-update-page`. Quy ước: **phải `fetch` database trước** để lấy
  `data_source_id` + schema, rồi mới `create-pages` dưới đúng data source đó.
- Đã kiểm tra `agents/sap-docs-researcher.md` (agent tích hợp nhiều MCP server nhất repo) — frontmatter
  `tools:` của agent **KHÔNG liệt kê tên tool MCP cụ thể** (chỉ có Read/Grep/Glob/WebFetch/WebSearch),
  MCP tool được gọi thẳng qua tên (`search_cds`, `fetch`...) trong phần mô tả nhiệm vụ. => **Không cần
  sửa `tools:` trong `agents/sap-daily-learner.md`** để "cấp quyền" gọi Notion — quyền gọi MCP tool
  không đi qua field này trong repo này.
- Chưa verify được TÊN TOOL CHÍNH XÁC sẽ hiển thị trong Claude Code cho server `notion` (có thể có
  tiền tố `mcp__notion__...`) vì MCP server này chưa được authenticate trong phiên hiện tại (không
  thấy qua ToolSearch). SKILL.md sẽ mô tả theo Ý ĐỊNH (gọi tool search/fetch/create-pages của MCP
  `notion`) thay vì hard-code 1 chuỗi tên tool chưa kiểm chứng được — Claude tại thời điểm chạy thật
  sẽ tự khớp đúng tên tool đang có trong session.
- Không cần script Python mới (khác lesson cards — vốn cần thuật toán scoring/dedup riêng trong
  `lesson_card_retrieve.py`): việc search/dedup ở đây dùng thẳng semantic search có sẵn của Notion,
  chỉ cần mô tả quy trình gọi tool trong SKILL.md.

## Thiết kế

### Cấu trúc Notion

1 database tên cố định **"SAP Skills"** (tạo 1 lần, idempotent — giống tinh thần
`bootstrap_memory.py`: tìm trước qua `notion-search`, nếu không thấy thì `notion-create-database`).
Properties: `Module` (select, dùng đúng mã module hiện có: SD/FI/MM/CO/PP/.../BTP Admin), `Topic`
(title), `Tags` (multi-select), `Created` (date), `Source question` (text). Nội dung trang = y hệt
format skill local hiện tại (Problem/Solution/SSCUI-Fiori/API/Notes — SKILL.md mục 3).

### Đọc trước (mở rộng điều kiện 4 "không trùng lặp")

Khi 1 vấn đề đủ điều kiện có thể thành skill (SKILL.md mục 3, điều kiện 1-3 đã đạt), **trước khi**
tự giải từ đầu:
1. `notion-search` theo module + từ khoá topic.
2. Nếu tìm thấy page khớp → `notion-fetch` lấy nội dung, dùng luôn để trả lời user (không tự suy
   luận lại từ đầu), đồng thời lưu 1 bản local vào `memory/procedural/skills/` (đánh dấu
   `source: "Đồng bộ từ Notion (do <ai đó> hỏi trước)"`) để lần sau không cần gọi Notion nữa.
3. Nếu không thấy → tiến hành giải quyết như quy trình hiện tại, rồi sang bước "Ghi sau" dưới đây.

### Ghi sau (mở rộng "Quy trình tạo skill")

Sau khi tạo xong skill local như hiện tại (bước 1-3 không đổi), thêm bước:
4. `notion-fetch` database "SAP Skills" lấy `data_source_id` (tạo mới qua `notion-create-database`
   nếu đây là lần đầu, chưa từng có).
5. `notion-create-pages` dưới đúng `data_source_id` đó, điền properties + nội dung y hệt skill local
   vừa tạo. **Tự động, không hỏi xác nhận** (theo lựa chọn của user).
6. Thông báo cho user thêm 1 dòng: "☁️ Đã đồng bộ lên Notion (SAP Skills) — cả team dùng được."

### Fail-open (bắt buộc)

Nếu bất kỳ lệnh gọi MCP `notion` nào lỗi (chưa `/mcp` connect, chưa OAuth, mất mạng...): bỏ qua
bước đó, tiếp tục quy trình local như hiện tại KHÔNG thay đổi hành vi cũ, chỉ 1 dòng ghi chú ngắn
(không phải lỗi to, không chặn). Cùng triết lý fail-open đã dùng cho các hook trong repo này
(`zy_namespace_guard.py`, `verify_nudge.py`).

## Thay đổi

1. **`skills/sap-daily-learner/SKILL.md`** (file chính, chi tiết đầy đủ) — thêm 1 mục mới ngay sau
   mục "3. Auto-Skill Creation Engine": "3b. Đồng bộ Notion (team-shared)" với đúng nội dung thiết
   kế ở trên (cấu trúc DB, đọc trước, ghi sau, fail-open). Cập nhật Review Checklist (mục 9) thêm
   2 dòng: đã tra Notion trước khi tự giải + đã đẩy Notion sau khi tạo skill (hoặc ghi rõ lý do bỏ
   qua nếu Notion không kết nối).
2. **`agents/sap-daily-learner.md`** — cập nhật ngắn gọn (khớp phong cách đã cô đọng sẵn của file
   này, model `haiku` nên tránh dài dòng): thêm 1-2 câu vào mục "Auto-Skill Creation" trỏ về SKILL.md
   mục 3b, và sửa bước 4 của "Quy trình tương tác" ("Tạo skill: Nếu đủ điều kiện...") thêm
   "+ đồng bộ Notion".
3. **`README.md`** — bổ sung ngắn vào subsection Notion đã thêm trước đó: 1 đoạn nói rõ
   `sap-daily-learner` tự dùng Notion làm kho skill chung 2 chiều (không cần thao tác thủ công gì
   thêm ngoài `/mcp` đã làm 1 lần).
4. **`index.html`** — thêm 1 đoạn ngắn (không rewrite lại cả section Daily Learner) trong section
   `daily-learner` mô tả tính năng 2 chiều này, kèm bản dịch EN. Verify lại bằng đúng quy trình đã
   dùng ở phiên trước: tag-balance checker (html.parser) + `node --check` + mô phỏng
   `translatePage()` cho chuỗi mới.
5. **`CHANGELOG.md`** — entry mới ở đầu file, version dự đoán kế tiếp (patch/minor tuỳ commit type).

## Không làm (và lý do)

- Không mở rộng ra 25 agent tư vấn khác (theo lựa chọn user) — chỉ sap-daily-learner.
- Không thêm approval-gate trước khi đẩy Notion (theo lựa chọn user) — tự động hoàn toàn, chỉ có
  thông báo sau khi đã đẩy.
- Không viết script Python mới cho search/dedup — dùng thẳng semantic search có sẵn của Notion MCP.
- Không sửa `tools:` trong frontmatter agent — không cần thiết theo đúng convention đã kiểm chứng.

## Verification

- Đọc lại `skills/sap-daily-learner/SKILL.md` mục 3b sau khi viết — đối chiếu với format/style các
  mục khác trong cùng file (đặc biệt mục Lesson Cards, cũng có nhịp "extract/retrieve" tương tự).
- HTML: tag-balance checker (html.parser) + `node --check` + mô phỏng `translatePage()` cho mọi
  chuỗi VI mới trong `index.html`, giống hệt quy trình đã áp dụng thành công ở phiên Notion MCP
  trước (đã bắt được 1 lỗi collision dịch thật ở phiên đó — áp dụng lại quy trình này).
- Không thể test thật end-to-end việc gọi `notion-search`/`notion-create-pages` trong phiên này vì
  MCP `notion` chưa được user authenticate (`/mcp`) — sẽ nêu rõ giới hạn này, đề nghị user tự thử
  bằng 1 câu hỏi thật sau khi merge + connect Notion, thay vì khẳng định đã "chạy thật" khi chưa
  chạy được.
