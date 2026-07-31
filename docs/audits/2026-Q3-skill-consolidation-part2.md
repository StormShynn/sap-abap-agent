# Skill Consolidation — Part 2 (2026-07-31)

> Tiếp nối `2026-Q3-skill-rationalization.md` (14/07/2026). Audit này thực hiện 2 việc mà
> audit trước đề xuất nhưng chưa thực thi (hợp nhất BTP, tiếp tục đưa skill setup-1-lần sang
> `reference/mcp-guides/`), cộng thêm riêng biệt 4 skill mới đã thêm SAU audit trước mà chưa
> qua rà soát lần nào (`sap-multi-system-context`, `sap-service-type-context`,
> `sap-security-review`, `sap-package-backup`).

## Scope

Yêu cầu ban đầu: rà soát toàn bộ 45 skill trong `skills/` (cảm giác "quá nhiều"), xác định
tập "chính" nên giữ auto-discover toàn cục, phần còn lại chuyển sang cơ chế đã có sẵn
(`reference/modules/`, `reference/mcp-guides/`, `reference/process/`) để vẫn dùng được khi
skill/agent khác gọi tới bằng tên, không cần xóa năng lực nào.

Thực thi Phase 1 (rủi ro thấp, đã xác nhận với người dùng trước khi sửa) — xem
`docs/plans/completed/skill-consolidation-2026-07-31.md` cho chi tiết plan/risk/validation.
Phase 2 (gộp nhóm "technical knowledge" — `sap-abap-sql`/`sap-authorization`/`sap-rap-events`/
`sap-released-classes`/`sap-badi-enhancement`/`sap-key-user-toolkit`/`sap-odata-service`) —
**chưa thực thi**, chỉ nghiên cứu và đề xuất, xem kết luận ở cuối file.

## Kết quả đạt được

`skills/` giảm từ **45 xuống 38** (không tính placeholder `sap-user-skills`).

| Skill (cũ) | Vị trí mới | Loại thay đổi |
|---|---|---|
| `sap-multi-system-context` | `reference/process/sap-multi-system-context.md` | Di chuyển nguyên vẹn, bỏ YAML frontmatter |
| `sap-service-type-context` | `reference/process/sap-service-type-context.md` | Di chuyển nguyên vẹn, bỏ YAML frontmatter |
| `mcp-sap-notes` | `reference/mcp-guides/mcp-sap-notes.md` | Di chuyển nguyên vẹn |
| `mcp-sap-concur` | `reference/mcp-guides/mcp-sap-concur.md` | Di chuyển nguyên vẹn (đã sẵn có pointer sang `mcp-sap-cdata-setup.md`) |
| `mcp-sap-fieldglass` | `reference/mcp-guides/mcp-sap-fieldglass.md` | Di chuyển nguyên vẹn |
| `sap-btp-connectivity` | `reference/modules/sap-btp-connectivity/SKILL.md` | **Hợp nhất** vào knowledge note có sẵn cùng tên (xem Phát hiện #1) |
| `sap-btp-best-practices` | `reference/modules/sap-btp-admin-cloud/deep/SKILL.md` | **Hợp nhất**, phần trùng security/CI-CD gộp lại thay vì lặp |

## Phát hiện mới (audit 14/07 chưa có, hoặc tự báo cáo chưa đúng thực tế)

1. **Xung đột tên 3 chiều với `sap-btp-connectivity`, audit trước không phát hiện**: trước
   khi sửa, tồn tại ĐỒNG THỜI `skills/sap-btp-connectivity/SKILL.md` (skill instruction, sẽ bị
   xóa) VÀ `reference/modules/sap-btp-connectivity/SKILL.md` (knowledge note, tự nhận trong
   chính nó là "Không thay thế skill sap-btp-connectivity" — nội dung khác nhau nhưng TRÙNG
   tên). 8 file `reference/modules/*-integration/SKILL.md` khác (HCM, GTS, CA, Fiori role, BW,
   PS, TR, WM-EWM) đã trỏ về knowledge note này ở mục "BTP architecture" từ trước — vì giữ
   nguyên tên/vị trí knowledge note làm nơi hợp nhất, cả 8 file này KHÔNG cần sửa gì.
2. **Audit 14/07 tự báo cáo "đã hợp nhất Destination pattern giữa sap-btp-best-practices/
   sap-btp-connectivity" nhưng xác minh trực tiếp cho thấy chưa hợp nhất thật** — chỉ có 1
   đoạn ở `sap-btp-best-practices` §6 trỏ sang `sap-btp-connectivity` thay vì lặp lại JSON,
   cả 2 skill vẫn còn đầy đủ, độc lập. Đã hợp nhất thật trong đợt này.
3. **`tests/test_skill_multi_system_context.py` hard-code đường dẫn `skills/
   sap-multi-system-context`** và assert các field frontmatter kiểu skill (`tools`,
   `argument-hint`, `effort`, `model: sonnet`) — di chuyển file đòi hỏi viết lại test, không
   chỉ đổi đường dẫn. Đã viết lại, giữ nguyên các assertion nội dung (routingHints, 5 edition,
   3 backend, TTL 7 ngày), bỏ các assertion frontmatter không còn áp dụng, thêm 1 assertion
   mới xác nhận `sap-ask-consultant` trỏ đúng về vị trí mới.
4. **Bug có sẵn (không liên quan trực tiếp phần này) trong `reference/scripts/
   mcp_inventory.json`**: entry `sap-fieldglass` có field `doc` trỏ sai
   `skills/sap-fieldglass/SKILL.md` (thư mục thật là `skills/mcp-sap-fieldglass/`, có tiền tố
   `mcp-`). Đã sửa tiện thể trong lúc cập nhật đường dẫn cho di chuyển này.
5. **`validate_plugin.py::skill_exists()` đã được cập nhật từ trước** (không còn là TODO như
   audit 14/07 ghi) — đã biết cả 4 đường dẫn (`skills/`, `reference/modules/`,
   `reference/mcp-guides/`, `reference/process/`) trước khi đợt này bắt đầu. Xác nhận bằng
   cách chạy `validate_plugin.py` trước khi sửa (PASS, 1 warning version-drift có sẵn không
   liên quan) rồi đối chiếu source `skill_exists()` trực tiếp.
6. **`CLAUDE.md` ghi số skill là "43"** trong khi thực tế (trước đợt này) là 45 — lệch do 2
   skill mới nhất thêm vào mà chưa cập nhật file này. Đã sửa thành 38 (con số thật sau đợt
   này), không còn lệch.

## Nguyên tắc áp dụng khi hợp nhất/di chuyển

- **Không xóa năng lực** — chỉ đổi từ "auto-discover qua từ khóa" sang "đọc khi được trỏ tới
  bằng tên", giống hệt pattern đã chứng minh của audit 14/07 (`mcp-sap-adt`/`mcp-sap-gui`/
  `mcp-sap-successfactors`, `sap-context-module-routing`/`sap-context-tool-result-trim`/
  `sap-scaffold-context-summary`).
- **Nếu tên vẫn còn tồn tại ở nơi khác** (vd `sap-btp-connectivity` qua `reference/modules/`),
  KHÔNG cần sửa frontmatter `skills:` của agent đang khai báo nó — `skill_exists()` vẫn
  resolve đúng. Chỉ sửa frontmatter khi tên thực sự biến mất hoàn toàn (vd `sap-btp-best-
  practices`, gộp vào 1 file KHÁC tên).
- **Đọc toàn bộ nội dung cả 2 file trước khi hợp nhất**, không tóm tắt/đoán — hợp nhất BTP
  đòi hỏi đọc đầy đủ 3 file nguồn (2 skill + 1 knowledge note có sẵn) để tránh mất thông tin
  hoặc lặp lại.

## Follow-up còn lại (chưa làm)

### Nhóm "technical knowledge" — đã nghiên cứu, ĐỀ XUẤT GIỮ NGUYÊN (không hợp nhất)

Đã đọc toàn bộ nội dung 7 skill (`sap-abap-sql` 157 dòng, `sap-authorization` 173 dòng,
`sap-rap-events` 167 dòng, `sap-released-classes` 150 dòng, `sap-odata-service` 162 dòng,
`sap-badi-enhancement` 138 dòng, `sap-key-user-toolkit` 188 dòng) và đếm số agent khai báo
từng tên qua `grep` trực tiếp trên `agents/*.md` (không suy đoán). Kết luận: **không nên hợp
nhất**, vì 3 lý do có bằng chứng cụ thể:

1. **Không trùng lặp nội dung thật** (khác hoàn toàn trường hợp BTP vừa sửa ở trên) — 6 skill
   đầu (trừ `sap-key-user-toolkit`) mỗi skill 1 chủ đề kỹ thuật riêng biệt (SQL/AMDP, DCL/IAM,
   RAP event, danh mục class released, OData V2/V4, Cloud BAdI) không lặp nội dung với nhau,
   hầu như không tham chiếu chéo (chỉ 1 cặp `sap-badi-enhancement` <-> `sap-key-user-toolkit`
   đã được audit 14/07 xử lý xong, cross-reference thay vì lặp lại).
2. **`sap-released-classes` và `sap-key-user-toolkit` khác SHAPE với 5 skill còn lại**:
   `sap-released-classes` là bảng tra cứu thuần túy (giống `sap-cds-kb` — một skill catalog đã
   được giữ riêng có chủ đích), không phải hướng dẫn "cách làm". `sap-key-user-toolkit` phục
   vụ **khác đối tượng hoàn toàn** — key user/functional consultant KHÔNG cần ABAP — trong khi
   6 skill còn lại đều dành cho developer. Gộp chung sẽ là lỗi phân loại sai đối tượng đọc.
3. **Blast radius quá lớn so với lợi ích**: đếm qua grep, **24/25 agent `sap-*-consultant-
   cloud.md`** khai báo **6/7 tên này** (trừ `sap-key-user-toolkit` — không agent developer
   nào khai báo nó, đúng như kỳ vọng vì khác đối tượng) trong frontmatter `skills:`. Hợp nhất
   sẽ đòi sửa frontmatter cả 24-25 file chỉ để đổi tên tham chiếu, cho 1 lợi ích chỉ là giảm
   con số top-level từ 38 xuống ~33 — không giảm được tổng lượng kiến thức agent phải biết
   (vẫn là từng đó nội dung, chỉ đổi chỗ lưu). Ngoài ra, gộp nhiều chủ đề vào 1
   `description`/`when_to_use` để dùng chung 1 ngân sách 1.536 ký tự (xem `SKILL_TEMPLATE.md`
   dòng 46) sẽ làm mỗi trigger phrase kém chính xác hơn so với hiện tại (mỗi skill có
   `when_to_use` riêng, sát đúng 1 chủ đề) — có nguy cơ làm GIẢM chất lượng auto-discover thay
   vì cải thiện, đi ngược lại chính mục tiêu ban đầu.

**Không hành động** — giữ nguyên cả 7 skill này ở `skills/`. Nếu sau này muốn giảm tiếp,
hướng khả thi hơn là áp dụng pattern nội bộ của chính `sap-clean-code` (tách `reference/` NỘI
BỘ trong thư mục của nó) cho TỪNG skill riêng lẻ (giảm độ dài file, không giảm SỐ LƯỢNG
skill), chứ không phải gộp nhiều skill lại.

### Các follow-up khác (chưa làm, ngoài phạm vi đợt này)

- **Mẫu CData MCP chung** (`mcp-sap-cdata-setup.md`) đã tồn tại và đã được `mcp-sap-concur`/
  `mcp-sap-fieldglass`/`mcp-sap-successfactors` dùng — không còn follow-up nào ở đây.
- **`reference/modules/sap-fi-cloud/deep/SKILL.md` chưa được làm giàu** (audit 14/07, mục
  10) — ngoài phạm vi đợt này, vẫn còn nguyên trạng.
- **5 module thiếu cross-reference `sap-extensibility`/`sap-clean-code`** (audit 14/07, mục
  9: `sap-bw-cloud`, `sap-basis-cloud`, `sap-tm-cloud`, `sap-tr-cloud`, `sap-ca-cloud`) —
  ngoài phạm vi đợt này, vẫn còn nguyên trạng.
