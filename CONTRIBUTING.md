# 🧠 Hướng dẫn đóng góp — SAP ABAP Agent

Cảm ơn bạn đã quan tâm đến việc đóng góp cho **SAP ABAP Agent**! Dự án này sống nhờ cộng đồng — mỗi skill mới, mỗi agent mới, mỗi bản fix đều giúp hệ sinh thái SAP AI ngày càng mạnh mẽ hơn.

---

## 📋 Mục lục

- [Cách đóng góp](#cách-đóng-góp)
- [Yêu cầu](#yêu-cầu)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Thêm Skill mới](#thêm-skill-mới)
- [Thêm Agent mới](#thêm-agent-mới)
- [Cập nhật Routing Engine](#cập-nhật-routing-engine)
- [Thêm Reference Module](#thêm-reference-module)
- [Yêu cầu về code](#yêu-cầu-về-code)
  - [YAML Skills Format Convention](#yaml-skills-format-convention)
- [Quy trình Pull Request](#quy-trình-pull-request)
- [Ý tưởng đóng góp](#ý-tưởng-đóng-góp)
- [Test local trước khi submit](#test-local-trước-khi-submit)
- [Tài nguyên](#tài-nguyên)

---

## 🤝 Cách đóng góp

| Hình thức | Mô tả |
|-----------|-------|
| **🐛 Bug report** | Mở issue với mô tả lỗi, cách reproduce, môi trường |
| **💡 Feature request** | Mở issue đề xuất skill/agent mới |
| **📝 Skill mới** | Fork repo → thêm skill → Pull Request |
| **🧑‍💻 Agent mới** | Fork repo → thêm agent & reference module → Pull Request |
| **📖 Documentation** | Sửa index.html, README.md, hoặc thêm hướng dẫn |
| **🌐 Translation** | Thêm/bổ sung bản dịch trong translations object |
| **🔧 Bug fix** | Fork repo → fix → Pull Request |

---

## ✅ Yêu cầu

Trước khi đóng góp, hãy đảm bảo bạn đã:

- [ ] Đọc [README.md](README.md) để hiểu tổng quan dự án
- [ ] Có kiến thức cơ bản về SAP S/4HANA Cloud Public Edition
- [ ] Biết YAML frontmatter và Markdown
- [ ] (Không bắt buộc) Có Claude Code để test local

---

## 📁 Cấu trúc dự án

```
sap-abap-agent/
├── .claude-plugin/plugin.json     # Manifest (version, description)
├── agents/                         # Agent definitions (.md YAML frontmatter)
│   ├── sap-sd-consultant-cloud.md
│   ├── sap-fi-consultant-cloud.md
│   ├── ...
│   └── sap-daily-learner.md
├── skills/                         # Skill implementations
│   ├── sap-ask-consultant/         # Routing engine (TRUNG TÂM)
│   │   └── SKILL.md
│   ├── sap-btp-setup/
│   ├── sap-cds-kb/
│   ├── sap-docs-research/
│   ├── sap-clean-code/
│   ├── sap-extensibility/
│   ├── sap-key-user-toolkit/
│   └── sap-daily-learner/
├── reference/modules/              # Knowledge base cho từng module
│   ├── sap-fi-cloud/SKILL.md
│   ├── sap-mm-cloud/SKILL.md
│   └── ...
├── commands/                       # Custom commands (/sap-connect)
├── hooks/                          # Event hooks (SELECT * warning)
├── index.html                      # Trang hướng dẫn song ngữ
├── README.md                       # Tổng quan dự án
└── CONTRIBUTING.md                 # Bạn đang đọc đây!
```

---

## 🆕 Thêm Skill mới

Skill là reusable instructions cho Claude Code. Mỗi skill là một thư mục chứa file `SKILL.md`.

### Các bước

#### Bước 1: Tạo thư mục skill

```bash
mkdir skills/<tên-skill>/
```

Tên skill nên:
- Bắt đầu bằng `sap-` (cho SAP-specific) hoặc tên module (VD: `abap-reviewer`)
- Dùng dash (`-`) thay vì underscore
- Ngắn gọn, mô tả (VD: `sap-clean-code`, `sap-daily-learner`)

#### Bước 2: Tạo `SKILL.md` với YAML frontmatter

```markdown
---
name: <tên-skill>
description: |
  <1-2 câu mô tả ngắn gọn skill này làm gì. 
  Ghi rõ khi nào nên dùng và khi nào không.>
argument-hint: "[cau hoi]"
model: haiku
---
```

**Fields:**

| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| `name` | ✅ | Tên skill (khớp với tên thư mục) |
| `description` | ✅ | Mô tả ngắn gọn, rõ ràng |
| `argument-hint` | ❌ | Gợi ý cách dùng argument |
| `model` | ❌ | Model preference (`haiku` / `sonnet`) |
| `effort` | ❌ | Độ phức tạp (`low` / `medium` / `high`) |
| `tools` | ❌ | Tools được phép dùng (`[Read, Write, Edit]`) |
| `disallowedTools` | ❌ | Tools bị cấm dùng |

#### Bước 3: Viết nội dung

Mỗi SKILL.md nên có:
- **Mô tả chi tiết**: Skill làm gì, khi nào dùng
- **Quy trình**: Các bước xử lý (dạng checklist hoặc numbered list)
- **Ví dụ**: Câu lệnh mẫu + kết quả mẫu
- **Lưu ý**: Cạm bẫy, giới hạn, edge cases
- **Tích hợp**: Cách skill này kết nối với các skill/agent khác

#### Bước 4: (Optional) Cập nhật Routing Engine

Nếu skill mới cần được dispatch tự động, thêm vào `skills/sap-ask-consultant/SKILL.md`:
- Thêm dòng trong Keyword Matrix
- Cập nhật module coupling nếu cần
- Cập nhật total agent count

#### Bước 5: Cập nhật documentation

- `README.md`: Thêm skill vào file tree
- `index.html`: Thêm vào section "Hướng dẫn sử dụng" + "Câu hỏi cho từng skill"

---

## 🆕 Thêm Agent mới

Agent là Claude Code agent có system prompt riêng. Mỗi agent là một file `.md` trong `agents/`.

### Các bước

#### Bước 1: Tạo file `agents/<tên-agent>.md`

```markdown
---
name: <tên-agent>
description: |
  <1-2 câu mô tả agent này làm gì.
  Càng chi tiết càng tốt cho routing.>
model: sonnet
tools: [Read, Grep, Glob, Write, Edit, WebFetch, WebSearch]
skills:
  - <skill-1>
  - <skill-2>
  - <skill-3>
---
```

**Fields:**

| Field | Bắt buộc | Mô tả |
|-------|----------|-------|
| `name` | ✅ | Tên agent (VD: `sap-mm-consultant-cloud`) |
| `description` | ✅ | Mô tả chi tiết, dùng để routing |
| `model` | ❌ | Model (`sonnet` cho phức tạp, `haiku` cho đơn giản) |
| `tools` | ❌ | List tools được phép |
| `skills` | ❌ | List skills agent này có thể dùng |

#### Bước 2: Viết system prompt

Agent file nên có:
- **Role**: Agent là ai (chuyên gia SAP module nào)
- **Behavior**: Cách agent tương tác với user
- **Knowledge scope**: Module nào, version nào, cloud hay on-prem
- **Examples**: Ví dụ câu hỏi và cách trả lời
- **Limitations**: Những gì agent KHÔNG làm

#### Bước 3: Tạo Reference Module (bắt buộc)

Mỗi agent cần có knowledge base riêng tại `reference/modules/<tên-module>/SKILL.md`:

```markdown
---
name: <tên-module>
description: Kien thuc chuyen sau ve module SAP
effort: medium
model: haiku
---
```

Nội dung nên có:
- **Cấu hình chính**: SSCUI, scope items quan trọng
- **Business process**: Flow chính của module
- **Integration**: Module này kết nối với module nào
- **Fiori Apps**: Ứng dụng Fiori chính
- **Released APIs**: APIs cho public cloud
- **Best Practices**: Mẹo, cạm bẫy, lưu ý

#### Bước 4: Thêm vào Routing Engine

Cập nhật `skills/sap-ask-consultant/SKILL.md`:
- Thêm dòng keyword matrix cho module mới
- Cập nhật module coupling nếu cần
- Cập nhật số lượng agents

#### Bước 5: Cập nhật tất cả docs

- [ ] `README.md`: Thêm vào danh sách agents
- [ ] `.claude-plugin/plugin.json`: Cập nhật `version` và `description`
- [ ] `index.html`: Thêm vào consultant system table
- [ ] `index.html`: Cập nhật sidebar + routing examples
- [ ] `index.html`: Thêm translations (VI → EN)
- [ ] `skills/sap-ask-consultant/SKILL.md`: Thêm vào routing

---

## 🔀 Cập nhật Routing Engine

`skills/sap-ask-consultant/SKILL.md` là trái tim của hệ thống. Khi thêm module mới:

### 1. Keyword Matrix

Thêm 1 dòng vào bảng Keyword Matrix:

```markdown
| **<MODULE>** | `<agent-name>` | keywords (weight 3) | keywords (weight 2) | keywords (weight 1) | ≥ 2 |
```

**Nguyên tắc chọn keywords:**
- **Weight 3**: Từ khóa tiếng Anh đặc trưng nhất của module (VD: `purchase order`, `sales order`)
- **Weight 2**: Từ khóa tiếng Việt hoặc từ đồng nghĩa
- **Weight 1**: Từ khóa chung, dễ xuất hiện ở nhiều module
- **Threshold**: Mặc định `≥ 2`. Chỉ hạ xuống `≥ 1` nếu module cần dễ dispatch hơn (VD: Daily Learner)

### 2. Module Coupling

Thêm coupling rules nếu module mới thường đi kèm module khác:

```markdown
| **<Module A>** | `<agent-B>`, `<agent-C>` | <lý do coupling> |
```

### 3. Cập nhật tổng

- Số agents: `**Tổng cộng**: <N> agents`

---

## 📚 Thêm Reference Module

Mỗi module consultant cần một reference module tại `reference/modules/sap-<tên>-cloud/SKILL.md`.

Template:

```markdown
---
name: sap-<tên>-cloud
description: Kien thuc chuyen sau ve module <Tên> trong SAP S/4HANA Cloud
effort: medium
model: haiku
---

# <Tên> Module — Kiến thức nền tảng

## 1. Tổng quan

## 2. Business Processes chính

## 3. Cấu hình quan trọng (SSCUI / Scope Items)

| Scope Item | Mô tả | SSCUI |
|-----------|-------|-------|
| ... | ... | ... |

## 4. Fiori Apps chính

| App | App ID | Mục đích |
|-----|--------|----------|
| ... | ... | ... |

## 5. Released APIs

| API | Mô tả | Endpoint |
|-----|-------|----------|
| ... | ... | ... |

## 6. Integration với các module khác

| Module | Integration Point | Business Process |
|--------|------------------|------------------|
| ... | ... | ... |

## 7. Best Practices & Lưu ý

## 8. Tham khảo

- [SAP Help Portal](https://help.sap.com/)
- [Community](https://community.sap.com/)
```

---

## ✏️ Yêu cầu về code

### Format

- **YAML frontmatter**: Phải có `---` mở đầu và kết thúc
- **Markdown**: Dùng headings `##`, `###` (không dùng `#` ngoài title)
- **Tables**: Dùng `|` pipe tables
- **Code blocks**: Dùng ``` với language hint
- **Line breaks**: 1 dòng trống giữa các section

### YAML Skills Format Convention

Danh sách skills trong YAML frontmatter của agent files **bắt buộc** dùng multi-line format (mỗi skill 1 dòng, thụt lề 2 spaces):

```yaml
# ✅ ĐÚNG — multi-line, 2 spaces indent
skills:
  - sap-sd-cloud
  - sap-extensibility
  - sap-clean-code
  - sap-abap-sql

# ❌ SAI — inline array (không được dùng)
skills: [sap-sd-cloud, sap-extensibility, sap-clean-code, sap-abap-sql]
```

**Lý do:**
- Dễ đọc hơn, đặc biệt khi danh sách skills dài (có agent tới 12 skills)
- Dễ maintain hơn (thêm/bớt skill không cần chỉnh dấu phẩy)
- Dễ diff trong code review (mỗi thay đổi là 1 dòng riêng)
- Tuân thủ YAML best practices cho list items

**Quy tắc:**
- Thụt lề **2 spaces** (không dùng tab) — dấu `-` nằm ở vị trí indent 2
- Mỗi skill 1 dòng: `  - <skill-name>` (space + dash + space + name)
- Không dùng dấu phẩy, không dùng dấu ngoặc vuông
- Giữ thứ tự: skill chính của module (VD: `sap-sd-cloud`) → skill chung (`sap-extensibility`, `sap-clean-code`) → skill kỹ thuật (`sap-abap-sql`, `sap-authorization`) → skill MCP nếu có

### Naming conventions

| Item | Convention | Ví dụ |
|------|-----------|-------|
| Agent file | `sap-<module>-consultant-cloud.md` | `sap-sd-consultant-cloud.md` |
| Skill folder | `sap-<tên>/` | `sap-clean-code/` |
| Reference module | `sap-<module>-cloud/SKILL.md` | `sap-fi-cloud/SKILL.md` |
| Agent name (YAML) | `sap-<module>-consultant-cloud` | `sap-mm-consultant-cloud` |

### Translation support

Nếu bạn thêm text mới vào `index.html`, hãy thêm cả:

```javascript
// Trong translations object:
'<Tiếng Việt>': '<English>',
```

Các text cần dịch:
- Sidebar nav links (không bao gồm emoji icon — icon nằm trong `<span>` riêng)
- Section headings (bao gồm emoji nếu emoji trong text node)
- Feature cards
- Mọi text hiển thị trong giao diện

---

## 🔄 Quy trình Pull Request

### Step-by-step

```bash
# 1. Fork repo trên GitHub

# 2. Clone fork về local
git clone https://github.com/<your-username>/sap-abap-agent.git
cd sap-abap-agent

# 3. Tạo branch mới
git checkout -b feature/<tên-ngắn-gọn>

# 4. Làm thay đổi
#   - Thêm skill/agent/docs
#   - Commit từng phần

# 5. Kiểm tra
#   - Đọc lại file .md xem có lỗi markdown không
#   - Mở index.html xem có render đúng không
#   - Test với Claude Code (nếu có)

# 6. Commit
git add <các-file-thay-đổi>
git commit -m "<type>: <mô tả ngắn>"

# 7. Push
git push origin feature/<tên-ngắn-gọn>

# 8. Mở Pull Request trên GitHub
```

### Commit message format

```
<type>: <mô tả ngắn>

Types:
- feat:   Tính năng mới (skill/agent mới)
- fix:    Sửa lỗi
- docs:   Documentation (README, index.html)
- refactor: Cải thiện code/skill không thay đổi chức năng
- i18n:   Translations
- chore:  Cấu hình, CI, dependencies
```

**Ví dụ:**
```
feat: add sap-tr-consultant-cloud agent for Treasury & Cash Management
docs: update index.html with TR module routing examples
i18n: add English translations for architecture section
fix: correct keyword weight for 'bank statement' in FI module
```

### PR Checklist

Khi mở Pull Request, hãy đảm bảo:

- [ ] Skill/Agent mới hoạt động (đã test với Claude Code)
- [ ] YAML frontmatter đúng format
- [ ] `skills/sap-ask-consultant/SKILL.md` đã được cập nhật routing
- [ ] `README.md` đã được cập nhật
- [ ] `index.html` đã được cập nhật (table, sidebar, translations)
- [ ] `.claude-plugin/plugin.json` version đã được bump
- [ ] Không có file tạm, file nhạy cảm trong commit
- [ ] Translations object không có key trùng lặp

### Sau khi merge

Sau khi PR được merge, các contributor có thể:
```bash
git pull origin main
claude --plugin-dir ./sap-abap-agent
```

Claude Code sẽ tự động load tất cả agents + skills mới.

---

## 💡 Ý tưởng đóng góp

### Ưu tiên cao

| Task | Mô tả | Kiến thức cần |
|------|-------|--------------|
| **Thêm agent còn thiếu** | TM, TR, Ariba, CA, GTS, EHS chưa có agent file | Module expertise |
| **Thêm reference modules** | Hoàn thiện knowledge base cho 18 modules | Module expertise |
| **Route examples** | Thêm ví dụ routing cho từng module | SAP domain knowledge |
| **Translations** | Hoàn thiện English translations | Song ngữ VI-EN |

### Ưu tiên trung bình

| Task | Mô tả |
|------|-------|
| **Thêm skill mới** | `sap-migration`, `sap-testing`, `sap-fi-close`, `sap-sd-pricing` |
| **Improve routing accuracy** | Fine-tune keyword weights, coupling rules |
| **Add CDS view mapping** | Map SAP module → CDS views từ CDS KB |

### Ưu tiên thấp

| Task | Mô tả |
|------|-------|
| **UI/UX improvements** | Cải thiện index.html responsive, animations |
| **Auto-generate skill** | Cải thiện sap-daily-learner auto-skill-creation |
| **Analytics** | Track skill usage patterns (opt-in) |

---

## 🧪 Test local trước khi submit

Sau khi thêm skill/agent mới, hãy test với Claude Code:

```bash
# Từ thư mục dự án
claude --plugin-dir ./sap-abap-agent
```

**Test checklist:**

- [ ] Mở Claude Code với plugin: `claude --plugin-dir ./sap-abap-agent`
- [ ] Gửi prompt test → kiểm tra dispatch đúng module. VD:
  - `"hoi <module>: test"` → explicit mention hoạt động
  - `"<keyword-weight-3>"` → auto-scoring hoạt động
- [ ] Nếu thêm skill mới: kiểm tra skill instruction có được Claude load không
- [ ] `index.html` mở được trong browser, không lỗi JavaScript
- [ ] Language toggle (VI ↔ EN) hoạt động cho text mới

### ⚠️ File không nên push lên repo

```
.sap-abap-agent/LEARNING_PROGRESS.md   # Progress cá nhân, mỗi user 1 bản riêng
skills/sap-user-skills/                # Auto-created skills (cá nhân), KHÔNG push
_*.py                                  # Script Python tạm (VD: _add_trans.py)
nul                                    # File tạm trên Windows
```

### Hooks convention

Nếu bạn thêm hook mới (`hooks/hooks.json`):

```json
{
  "<event-name>": {
    "command": "<lệnh>",
    "description": "<mô tả ngắn>"
  }
}
```

Xem `hooks/hooks.json` hiện tại làm mẫu.

## 📖 Tài nguyên

| Tài nguyên | URL |
|-----------|-----|
| **SAP Learning** | [`learning.sap.com`](https://learning.sap.com/) |
| **SAP Help Portal** | [`help.sap.com`](https://help.sap.com/) |
| **SAP Community** | [`community.sap.com`](https://community.sap.com/) |
| **SAP Best Practices** | [`me.sap.com/processnavigator`](https://me.sap.com/processnavigator) |
| **CDS Knowledge Base** | [`cds-kb.vercel.app`](https://cds-kb.vercel.app/) |
| **Claude Code Docs** | [`docs.anthropic.com/claude-code`](https://docs.anthropic.com/en/docs/claude-code/overview) |
| **MCP Specification** | [`modelcontextprotocol.io`](https://modelcontextprotocol.io/) |
| **Code of Conduct** | (Tạo file `CODE_OF_CONDUCT.md` sau nếu cần) |

---

## 🙏 Cảm ơn

Mỗi đóng góp, dù nhỏ (sửa lỗi chính tả, thêm ví dụ, cải thiện docs), đều giúp cộng đồng SAP AI phát triển. Cảm ơn bạn đã dành thời gian!

**— StormShynn & cộng đồng SAP ABAP Agent**
