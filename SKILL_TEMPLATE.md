# 📝 Skill Template — SAP ABAP Agent

Dùng file này làm **template** khi tạo skill, agent, hoặc reference module mới cho dự án. Copy section phù hợp và điền thông tin.

---

## 📋 Mục lục

- [1. Skill Implementation (`skills/<tên>/SKILL.md`)](#1-skill-implementation)
- [2. Agent Definition (`agents/<tên>.md`)](#2-agent-definition)
- [3. Reference Module (`reference/modules/<tên>/SKILL.md`)](#3-reference-module)
- [4. Cheatsheet](#4-cheatsheet)

---

## 1. Skill Implementation

> **Đường dẫn:** `skills/<tên-skill>/SKILL.md`
> 
> **Mục đích:** Skill là reusable instructions cho Claude Code. File này chứa toàn bộ logic xử lý.
> 
> **Ví dụ thực tế:** `skills/sap-daily-learner/SKILL.md`, `skills/sap-clean-code/SKILL.md`

```markdown
---
name: <tên-skill>
description: |
  <1-3 câu mô tả ngắn gọn>
  Ghi rõ: KHI NÀO dùng, KHÔNG dùng khi nào.
when_to_use: |
  <cụm từ/câu hỏi mẫu người dùng hay gõ, cách nhau bằng dấu phẩy — vd:
  "hoi SD ve pricing", "tao INTAKE tu file X.docx">
argument-hint: "[cau hoi]"
model: haiku
effort: medium
tools: [Read, Write, Edit, WebSearch]
disallowedTools: [Bash]
---
```

### Fields

| Field | Bắt buộc | Giá trị | Mô tả |
|-------|----------|---------|-------|
| `name` | ✅ | `sap-<tên>` | Tên skill, khớp với tên thư mục |
| `description` | ✅ | Text | Mô tả ngắn, rõ ràng: skill làm gì + khi nào dùng. **Đưa use case chính lên đầu** — Claude Code hiển thị field này trong danh sách skill (gõ `/`), và cắt bớt nếu quá dài (giới hạn cứng 1.536 ký tự tính chung với `when_to_use`; ngoài ra còn 1 ngân sách tổng cho toàn bộ danh sách skill, v.d skill ít dùng có thể bị rút gọn còn mỗi tên — xem `/doctor` để kiểm tra). |
| `when_to_use` | ❌ | Text | Câu hỏi/cụm từ mẫu người dùng hay gõ (trigger phrase). Tách riêng khỏi `description` cho gọn, nhưng vẫn tính chung vào giới hạn 1.536 ký tự. |
| `argument-hint` | ❌ | `"[cau hoi]"` | Gợi ý argument khi dùng skill |
| `model` | ❌ | `haiku` / `sonnet` | `haiku` cho đơn giản, `sonnet` cho phức tạp |
| `effort` | ❌ | `low` / `medium` / `high` | Độ phức tạp tính toán |
| `tools` | ❌ | `[Read, Write, Edit, ...]` | Tools được phép (mặc định: tất cả) |
| `disallowedTools` | ❌ | `[Bash]` | Tools bị cấm |

> 💡 Claude Code **không có UI hover/click để xem trước nội dung skill** — chỉ có dòng mô tả rút gọn khi gõ `/` (hoặc lệnh `/skills`). Viết `description`/`when_to_use` sao cho phần đầu đã đủ rõ "dùng khi nào" là cách duy nhất để tận dụng tốt phần hiển thị có sẵn.

### Template nội dung

```markdown
# <Tên Skill> — <Mô tả ngắn>

## Khi nào dùng

- ✅ <Trường hợp nên dùng>
- ✅ <Trường hợp nên dùng>
- ❌ <Trường hợp KHÔNG nên dùng>

## Quy trình xử lý

### Bước 1: <Bước 1>
<mô tả>

### Bước 2: <Bước 2>
<mô tả>

### Bước 3: <Bước 3>
<mô tả>

## Cấu hình chi tiết (nếu có)

| Tham số | Giá trị | Ghi chú |
|---------|---------|---------|
| ... | ... | ... |

## SSCUI / Fiori App (nếu có)

| Mã SSCUI | Mô tả | Ghi chú |
|----------|-------|---------|
| ... | ... | ... |

## API Released (nếu có)

| API | Mô tả | Endpoint |
|-----|-------|----------|
| ... | ... | ... |

## Ví dụ

### Input
```text
<Câu hỏi mẫu>
```

### Output
```text
<Câu trả lời mẫu>
```

## Lưu ý

- ⚠️ <Cạm bẫy / edge case>
- 💡 <Best practice>
- 🔗 <Tích hợp với skill/agent khác>
```

### Ví dụ hoàn chỉnh (rút gọn)

```markdown
---
name: sap-clean-code
description: |
  Kiem tra va sua code ABAP theo ABAP Cloud naming conventions & clean code.
  Dung khi user nho review code ABAP, hoac can refactor code cho dung standard.
  KHONG dung cho cau hoi nghiep vu SAP.
argument-hint: "[code ABAP can review]"
model: haiku
effort: low
---

# SAP Clean Code — ABAP Cloud Review

## Khi nào dùng
- ✅ User hỏi "review code ABAP này"
- ✅ User hỏi "sửa naming convention"
- ❌ User hỏi nghiệp vụ SAP

## Quy trình
1. Nhận code ABAP từ user
2. Check naming rules (prefix Z/Y, CamelCase...)
3. Check clean code patterns
4. Trả về danh sách issues + code fixed

## Naming Rules
| Pattern | Đúng | Sai |
|---------|------|-----|
| Class | ZCL_* / YCL_* | ZCL* |
| Interface | ZIF_* | ZIF* |
| Method | camelCase | snake_case |
```

---

## 2. Agent Definition

> **Đường dẫn:** `agents/<tên-agent>.md`
> 
> **Mục đích:** Mỗi agent là một Claude Code agent với system prompt riêng. File này định nghĩa tính cách, phạm vi kiến thức, behavior.
> 
> **Ví dụ thực tế:** `agents/sap-sd-consultant-cloud.md`, `agents/sap-daily-learner.md`

```markdown
---
name: <tên-agent>
description: |
  <2-4 câu mô tả chi tiết agent này là ai, làm gì.
  Dùng để routing engine hiểu và dispatch đúng.>
model: sonnet
tools: [Read, Grep, Glob, Write, Edit, WebFetch, WebSearch]
skills: [<tên-skill-1>, <tên-skill-2>]
---

# <Tên Agent> — <Vai trò>

Bạn là **<tên>**, <mô tả tính cách, chuyên môn>.

## Kiến thức chuyên môn

- Module: <module>
- Version: S/4HANA Cloud Public Edition
- Scope: <scope>

## Hành vi

1. <Behavior 1>
2. <Behavior 2>
3. <Behavior 3>

## Ví dụ tương tác

**User:** <câu hỏi mẫu>
**Bạn:** <câu trả lời mẫu>

## Giới hạn

- KHÔNG <gì đó không được làm>
- KHÔNG <gì đó không được làm>

## Tích hợp

- Kết hợp với <agent khác> khi <điều kiện>
- Dùng skill <tên skill> cho <mục đích>
```

### Agent naming convention

| Module | Agent name | Ví dụ |
|--------|-----------|-------|
| SAP functional | `sap-<module>-consultant-cloud` | `sap-sd-consultant-cloud` |
| Cross-module | `sap-<tên>` | `sap-daily-learner` |
| Research | `sap-docs-researcher` | `sap-docs-researcher` |
| Code review | `abap-reviewer` | `abap-reviewer` |

---

## 3. Reference Module

> **Đường dẫn:** `reference/modules/<tên>/SKILL.md`
> 
> **Mục đích:** Knowledge base cho từng module SAP — cấu hình, business process, integration. Agent dùng file này làm nguồn kiến thức nền tảng.
> 
> **Ví dụ thực tế:** `reference/modules/sap-fi-cloud/SKILL.md`, `reference/modules/sap-daily-learner/SKILL.md`

```markdown
---
name: sap-<tên>-cloud
description: Kien thuc chuyen sau ve module <Tên> trong SAP S/4HANA Cloud Public Edition
effort: medium
model: haiku
---

# <Tên> Module — <Mô tả>

## 1. Tổng quan

<1-2 đoạn giới thiệu module>

## 2. Business Processes chính

| Process | Mô tả | Scope Item |
|---------|-------|-----------|
| <Process 1> | <Mô tả> | <Mã scope> |
| <Process 2> | <Mô tả> | <Mã scope> |

## 3. Cấu hình quan trọng (SSCUI)

| Mã SSCUI | Mô tả | Business Process |
|----------|-------|-----------------|
| <SSCUI ID> | <Mô tả> | <Process> |

## 4. Fiori Apps chính

| App | App ID | Mục đích |
|-----|--------|----------|
| <Tên app> | F<XXXX> | <Mô tả> |

## 5. Released APIs

| API | Mô tả | Endpoint |
|-----|-------|----------|
| <Tên API> | <Mô tả> | `/sap/opu/odata/...` |

## 6. Integration với modules khác

| Module | Integration Point | Business Process |
|--------|------------------|------------------|
| <Module A> | <Điểm tích hợp> | <Process> |

## 7. Best Practices

- 💡 <Mẹo>
- ⚠️ <Cạm bẫy>

## 8. Tham khảo

- [SAP Help Portal](https://help.sap.com/)
- [SAP Community](https://community.sap.com/)
```

---

## 4. Cheatsheet

### So sánh 3 loại file

| | Skill | Agent | Reference Module |
|---|---|---|---|
| **Đường dẫn** | `skills/<tên>/SKILL.md` | `agents/<tên>.md` | `reference/modules/<tên>/SKILL.md` |
| **Mục đích** | Instructions xử lý | System prompt cho Claude | Knowledge base |
| **Ai dùng** | Claude Code | Routing engine → Claude | Agent |
| **YAML name** | `sap-<tên>` | `sap-<module>-consultant-cloud` | `sap-<tên>-cloud` |
| **Model** | `haiku` (mặc định) | `sonnet` (mặc định) | `haiku` (mặc định) |
| **Tools** | Optional | Recommended | Optional |
| **Skills** | ❌ | ✅ (list skills agent có thể dùng) | ❌ |

### File structure checklist

Khi thêm 1 module consultant mới, cần tạo **3 file**:

```
agents/sap-<module>-consultant-cloud.md         # Agent definition (BẮT BUỘC)
skills/sap-<module>-<topic>/SKILL.md            # Skill implementation (optional)
reference/modules/sap-<module>-cloud/SKILL.md   # Reference module (BẮT BUỘC)
```

Và cập nhật **5 file**:

```
skills/sap-ask-consultant/SKILL.md              # Routing engine (BẮT BUỘC) — thêm keyword matrix + coupling
README.md                                       # Cập nhật danh sách agents
index.html                                      # Thêm vào table + sidebar + translations VI/EN
.claude-plugin/plugin.json                      # Bump version
```

### YAML frontmatter fields quick reference

```
name:           # string - Tên (bắt buộc)
description:    | # string - Mô tả (bắt buộc). Đưa use case chính lên đầu — bị cắt cùng
                #   ngân sách với when_to_use (giới hạn cứng 1.536 ký tự/skill)
when_to_use:    | # string - Câu hỏi/trigger phrase mẫu (tuỳ chọn, chỉ dùng trong skill)
model:          # string - haiku | sonnet (mặc định: haiku)
effort:         # string - low | medium | high
tools:          # array - [Read, Write, Edit, ...]
disallowedTools:# array - [Bash, ...]
skills:         # array - [sap-xxx, sap-yyy] (chỉ dùng trong agent)
argument-hint:  # string - "[cau hoi]" (chỉ dùng trong skill)
```

---

## 5. Bonus: Mini Templates cho Commands & Hooks

### Command (`commands/<tên>.md`)

```markdown
---
name: <tên-command>
description: >
  <Mô tả ngắn gọn command này làm gì>
---

# /<tên-command> — <Mô tả>

Hướng dẫn chi tiết cho command.
```

### Hook (`hooks/hooks.json`)

```json
{
  "//": "Mô tả hook này làm gì",
  "<event-name>": {
    "command": "<lệnh hoặc script>",
    "description": "<mô tả ngắn>"
  }
}
```

Ví dụ:
```json
{
  "BeforeExecute": {
    "command": "grep -n 'SELECT \\* FROM' /dev/stdin && echo '⚠️ Warning: SELECT * detected!' || true",
    "description": "Cảnh báo khi dùng SELECT * trong ABAP"
  }
}
```

---

*Template này được tạo bởi Freebuff Coding Assistant cho dự án SAP ABAP Agent.*
