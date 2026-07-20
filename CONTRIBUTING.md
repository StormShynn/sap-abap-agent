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

## 🚫 Khi nào KHÔNG nên tạo skill mới

`skills/` là bề mặt **SAP-consulting cho end user** — mỗi skill mới đều được load/quét bởi mọi
người cài plugin, kể cả khi họ không bao giờ dùng tới. Trước khi tạo 1 thư mục `skills/<tên>/`
mới, tự hỏi 3 câu sau (rút ra từ 1 lần tự sửa sai thật trong dự án — xem `CHANGELOG.md`):

1. **Đối tượng dùng là ai?** Nếu là người **phát triển/đóng góp cho chính plugin này** (chạy lint,
   kiểm tra tài liệu đồng bộ, audit MCP registration...) — đó là việc của contributor, không phải
   của SAP consultant dùng plugin để tư vấn/code ABAP. Việc đó nên nằm trong `CONTRIBUTING.md` +
   docstring của script trong `reference/scripts/`, **không cần** một `SKILL.md` riêng.
2. **Có thực sự là 1 khả năng độc lập, hay chỉ là 1 lệnh nữa của skill đã có?** Nếu logic mới chỉ
   là "thêm 1 việc tổng hợp/quản lý" gắn liền với 1 skill đã tồn tại (vd thêm lệnh "retro" vào
   `sap-daily-learner` — skill đó đã có sẵn cơ chế theo dõi tiến độ/lesson card), hãy thêm **1 dòng
   mới vào bảng "User Commands"/mục quy trình** của skill đó, đừng tạo file mới.
3. **Có phải chỉ là 1 wrapper mỏng quanh 1 script, không có quy trình/phán đoán riêng?** Nếu chạy
   xong script là hết việc (không có bước "loại trừ false-positive", "hỏi xác nhận trước khi ghi",
   "đối chiếu nhiều nguồn dữ liệu"...) thì bản thân docstring của script + 1 dòng trong
   `CONTRIBUTING.md`/PR checklist là đủ.

**Ví dụ đã tự sửa trong dự án này**: lúc đầu tạo riêng `skills/sap-document-sync` (wrapper mỏng
quanh `validate_plugin.py`, đối tượng dùng là contributor) và `skills/sap-retro` (chỉ là 1 lệnh
tổng hợp, đã có chỗ hợp lý trong `sap-daily-learner`) — cả 2 đều **không cần** là skill riêng theo
đúng 3 câu hỏi trên, nên đã gộp lại (xem PR/CHANGELOG liên quan). `skills/sap-security-review`
được giữ lại làm skill riêng vì ngược lại: đối tượng dùng là SAP developer review code (end user
thật), có checklist + quy trình phán đoán riêng đáng kể, và đúng khuôn mẫu đã có của
`sap-clean-code`/`sap-extensibility` (skill riêng được `abap-reviewer` gọi tới).

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
- [ ] Đã chạy `python reference/scripts/validate_plugin.py` (hoặc `check_all.py` để chạy kèm
      `security_scan.py`/`check_site.py`) — xác nhận không FAIL, xem qua WARN nếu có

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

State cá nhân của các skill (`sap-daily-learner` memory, `reference/process/sap-context-tool-result-trim.md` cache,
`reference/process/sap-scaffold-context-summary.md`/`sap-analyze-function-spec`/`sap-handoff` sessions & handoff)
**mặc định KHÔNG còn ghi vào project nữa** — ghi vào `%USERPROFILE%\.sap-abap-agent\` (xem mục
"🏠 SAP_ABAP_AGENT_HOME" ngay dưới đây), nên bình thường không có gì để lo push nhầm. Các dòng
dưới đây chỉ phát sinh trong project khi bạn tự đặt `SAP_ABAP_AGENT_HOME` trỏ vào đây để
dev/test (đã có sẵn trong `.gitignore`):

```
.sap-abap-agent/LEARNING_PROGRESS.md   # Path cu (da thay bang memory/semantic/LEARNING_PROGRESS.md)
skills/sap-user-skills/                # Auto-created skills (cá nhân), KHÔNG push
.sap-abap-agent/memory/                # sap-daily-learner: episodic/semantic/procedural
.sap-abap-agent/cache/                 # reference/process/sap-context-tool-result-trim.md: cache full output
.sap-abap-agent/sessions/              # Handoff/scaffold working state (cá nhân)
.sap-abap-agent/handoff/               # Handoff docs (cá nhân)
.sap-abap-agent/sync_skills.lock       # Lock file của daemon sync_skills.py
.sap-abap-agent/dev-mirror/            # Dev mirror của sap-btp-agent profiles (xem dưới)
_*.py                                  # Script Python tạm (VD: _add_trans.py)
nul                                    # File tạm trên Windows
```

### 🏠 `SAP_ABAP_AGENT_HOME` cho state của plugin sap-abap-agent (khác `sap-btp-agent` bên dưới)

Các skill kể trên ghi state cá nhân qua `reference/scripts/agent_home.py` — mặc định
`%USERPROFILE%\.sap-abap-agent\` (Windows) / `~/.sap-abap-agent/` (macOS/Linux), **không phải**
project đang mở: plugin có thể cài và dùng trên bất kỳ project SAP nào, nên project/workspace
không phải là 1 vị trí ổn định để lưu state lâu dài (chỉ ổn định khi bạn đang dev ngay trong repo
plugin này — lúc đó workspace tình cờ trùng plugin repo). Muốn dev/test ngay trong project này
thay vì mở `%USERPROFILE%`:

```powershell
setx SAP_ABAP_AGENT_HOME "D:\__StormShyn\sap-abap-agent\.sap-abap-agent"
```

Khác với `SAP_BTP_AGENT_DEV_MIRROR` bên dưới (ghi thêm 1 bản, vẫn giữ bản chính ở
`%USERPROFILE%`), `SAP_ABAP_AGENT_HOME` là **override hẳn** (không mirror) — khi đặt biến này,
state chỉ ghi vào project, không ghi vào `%USERPROFILE%` nữa. Đừng đặt biến này khi dùng plugin
thật (không phải dev/test) — end user thật không bao giờ đặt biến này nên hành vi của họ không đổi.

Đây là cơ chế RIÊNG, KHÁC với `SAP_BTP_AGENT_HOME`/`SAP_BTP_AGENT_DEV_MIRROR` ngay dưới đây
(dùng cho `sap-btp-agent` - MCP server kết nối SAP BTP, không liên quan skill/memory của plugin).

### 🪞 Dev mirror cho `sap-btp-agent` (chỉ dành cho người đang build plugin này)

Mặc định `sap-btp-agent` chỉ ghi profile vào `%USERPROFILE%\.sap-btp-agent\` (hoặc
`SAP_BTP_AGENT_HOME` nếu bạn override) — đúng như hành vi end user thật sẽ gặp. Nếu bạn đang
sửa code MCP server và muốn tiện xem `config.json`/`profiles.json` ngay trong project thay vì
mở `%USERPROFILE%`, đặt thêm biến môi trường:

```powershell
setx SAP_BTP_AGENT_DEV_MIRROR "D:\__StormShyn\sap-abap-agent\.sap-abap-agent\dev-mirror"
```

Sau khi mở terminal/Claude Code mới, mọi lần ghi `config.json`/`profiles.json` sẽ được ghi
**thêm** (không thay thế) một bản sao vào `.sap-abap-agent/dev-mirror/` bên trong project —
hành vi ghi vào `%USERPROFILE%` vẫn giữ nguyên như cũ, chỉ là ghi thêm 1 chỗ nữa.

`secrets.json` (client_secret/token đã mã hóa) **mặc định KHÔNG** được mirror dù có bật biến
trên — muốn bật thêm (không khuyến khích, vì dữ liệu nhạy cảm nhân đôi chỗ lưu) thì đặt thêm
`SAP_BTP_AGENT_DEV_MIRROR_SECRETS=1`.

Cùng biến `SAP_BTP_AGENT_DEV_MIRROR` này cũng áp dụng cho `reference/scripts/office_to_md.py`
(skill `sap-doc-to-md`): khi bật, file `.md` + ảnh trong `<ten-file>_assets/` sinh ra từ
`in/`→`out/` sẽ được ghi thêm 1 bản vào `<mirror>/out/...` bên trong project — vẫn giữ nguyên
`%USERPROFILE%\.sap-btp-agent\out\` là nơi ghi chính. Lưu ý tài liệu FS là dữ liệu nghiệp vụ
khách hàng — chỉ bật mirror này khi đang test bằng tài liệu giả/không nhạy cảm.

Biến `SAP_BTP_AGENT_DEV_MIRROR`/`SAP_BTP_AGENT_DEV_MIRROR_SECRETS` không bao giờ được đặt mặc
định — end user cài plugin thật sự sẽ không bao giờ bật tính năng này, hành vi của họ không đổi.

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

## 🧠 Thêm Knowledge Note (cross-module / pattern)

Từ v1.11.1, plugin phân biệt 2 loại file trong `reference/modules/`:

| Loại | Đường dẫn chuẩn | Mục đích | Đối tượng dùng |
|------|-----------------|-----------|------------------|
| **Module reference** | `reference/modules/sap-<module>-cloud/SKILL.md` | Knowledge chuyên sâu cho **1 module consultant** cụ thể (SD/FI/MM/...). Bắt buộc có khi tạo agent mới (xem section "Thêm Agent mới"). | SAP consultant (end user) |
| **Knowledge note** (cross-module / pattern) | `reference/modules/<tên-rõ-ràng>/SKILL.md` | Knowledge về **kiến trúc, integration pattern, hoặc chủ đề không thuộc 1 module consultant nào**. VD: `abap-rap-cloud/`, `fiori-elements-cloud/`, `cap-cloud/`, `sap-btp-connectivity/`, `pm-integration-patterns/`, `wm-ewm-integration/`, `gts-cloud-architecture/`. | Contributor + consultant đọc tham khảo |

### Khi nào tạo Knowledge Note (không phải module reference)?

Tạo knowledge note khi knowledge **không thuộc 1 module consultant nào** trong 28 modules
hiện có, hoặc khi cần cross-module view (PM ↔ FICO, WM vs EWM, GTS vs S/4HANA, ...).

**KHÔNG tạo knowledge note mới** nếu:
- Knowledge thuộc 1 module consultant đã có → thêm vào `reference/modules/sap-<module>-cloud/SKILL.md`.
- Knowledge quá ngắn (< 5 section, < 100 dòng) → thêm vào section "Tích hợp với skill khác" của
  module tương ứng.
- Knowledge chỉ là 1 command workflow → thêm vào `skills/<tên-skill>/SKILL.md` (xem section
  "Khi nào KHÔNG nên tạo skill mới").

### Template

```markdown
---
name: <ten-knowledge-note>
description: Knowledge note tổng hợp từ <repo1>, <repo2> — <mô tả ngắn>. Khác với
  `sap-<module>-cloud/SKILL.md` (knowledge consultant). Dùng khi <use case>.
effort: low
model: haiku
---

# <Tiêu đề> — Knowledge Note

## 1. Tổng quan / bối cảnh
## 2. Kiến trúc / pattern chính
## 3. Integration với module khác (nếu có)
## 4. Anti-pattern
## 5. Liên kết với các skill/agent khác
## 6. Nguồn tham khảo
```

### Quy tắc đặt tên

- **KHÔNG** dùng prefix `sap-<module>-cloud/` cho knowledge note — đó là convention của module
  reference (consultant), gây nhầm lẫn với routing.
- Dùng tên **gợi ý nội dung**: `<topic>-integration-patterns/`, `<topic>-architecture/`,
  `<topic>-best-practices/`, hoặc technology name: `abap-rap-cloud/`, `cap-cloud/`,
  `fiori-elements-cloud/`.
- Mô tả (description) trong YAML frontmatter PHẢI ghi rõ "khác với `sap-<X>-cloud/SKILL.md`"
  để contributor đọc biết nó không phải module reference.

### Khai báo trong frontmatter (knowledge note gốc)

Khác với **module reference**, knowledge note thường chỉ cần 4 fields:
`name`, `description`, `effort`, `model` — KHÔNG cần `when_to_use`, `argument-hint`,
`tools`. Đây là knowledge note để tra cứu, không phải instruction skill để dispatch/execute
(xem thêm phân biệt trong `SKILL_TEMPLATE.md` mục 3 — Reference Module).

### Quy trình tạo

1. **Kiểm tra trùng**: `ls reference/modules/` để chắc chắn không có folder cùng tên.
2. **Tạo file**: `mkdir reference/modules/<ten-knowledge-note>` → tạo `SKILL.md` theo template.
3. **Mô tả nguồn tham khảo**: cuối file có mục "Nguồn tham khảo" — ghi rõ repo open-source nào
   đã tham khảo, kèm link GitHub.
4. **Update CI**: nếu thêm URL GitHub mới trong "Nguồn tham khảo", workflow
   `.github/workflows/lint-inspired-by-links.yml` sẽ HEAD-check tự động — không cần làm gì.
5. **Update CHANGELOG.md** với entry version mới.
6. **Update `README.md`** mục "Cảm hứng (Inspired by)" nếu reference repo lần đầu xuất hiện.

### Không thêm MCP server mới vào `.mcp.json` khi tạo knowledge note

Knowledge note thường tham khảo các MCP server open-source (`mcp-abap-adt`, `hana-mcp-server`,
v.v.) — **KHÔNG tự động** thêm vào `.mcp.json`. Contributor muốn dùng phải tự bật opt-in theo
hướng dẫn trong `docs/sap-mcp-recommendations.md` (Tier 1/2/3). Lý do: bảo toàn triết lý
"observation masking" của plugin + cài đặt nhẹ cho end-user.

## ✅ Validate Inspired-by Links (tự động trong CI)

Từ v1.11.2, plugin có script `reference/scripts/validate_inspired_by_links.py` quét mọi GitHub
URL trong README/CHANGELOG/SKILL.md và HEAD-check còn resolve được không. Workflow
`.github/workflows/lint-inspired-by-links.yml` chạy tự động:

- **Mỗi push/PR**: fail job nếu có URL trả về 404 (chặn 404 leak vào main).
- **Cron hằng ngày 06:00 UTC**: retry các link từng bị "network fail" lúc PR.
- **`workflow_dispatch`**: chạy tay khi cần.

### Khi CI fail vì URL 404

1. Workflow sẽ **comment lên PR** với danh sách URL GONE.
2. Mở file chứa URL (thường là README.md hoặc file knowledge note) → sửa hoặc xoá URL.
3. Push lại → CI chạy lại tự động.

### Chạy local

```bash
python reference/scripts/validate_inspired_by_links.py --strict
```

- Mặc định (`--concurrency 8`): in báo cáo, **không** exit non-zero khi GONE.
- `--strict`: exit non-zero khi có URL GONE (giống CI). Dùng trong pre-commit hook.
- Output: `[OK] / [GONE (404)] / [UNCHECKED (network fail)]` + summary số file đã quét.

### Khi thêm URL GitHub mới vào project

Không cần làm gì — workflow tự pick up. Chỉ cần đảm bảo:
- URL ở dạng `https://github.com/<owner>/<repo>` (root, không sub-path).
- Repo công khai, license cho phép tham khảo (MIT / Apache-2.0 / BSD...).

Nếu repo ở private hoặc bị rate-limit GitHub HEAD, URL sẽ rơi vào `[UNCHECKED]` — không fail CI.

## 🪝 Pre-commit Hook (tự chạy khi `git commit`)

Từ v1.12.0, plugin có 6 check tự động chạy trước khi commit — giống CI nhưng ở local:

| Check                          | Time   | Fail khi                                |
|--------------------------------|--------|------------------------------------------|
| `validate_plugin.py`           | < 1s   | Frontmatter lỗi, doc drift, Python syntax|
| `validate_inspired_by_links.py --strict` | < 5s | URL GitHub 404 trong README/CHANGELOG/SKILL.md |
| `pytest tests/`                | < 2s   | Unit test fail                          |
| `ruff check --fix`             | < 1s   | Lint error (E/W/F/I/B/UP/SIM) trong `.py` |
| `ruff format`                  | < 1s   | Format mismatch (auto-fix)               |
| `pre-commit-hooks`             | < 1s   | trailing-whitespace, EOF fixer, large files |

### Cài đặt (2 cách)

#### Cách A: Git hook built-in (đơn giản, không cần framework)

```bash
# Copy script co san
cp reference/scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### Cách B: Pre-commit framework (khuyến nghị, contributor-friendly)

```bash
pip install pre-commit
pre-commit install
```

Config nằm ở `.pre-commit-config.yaml`.

### Skip hook (khẩn cấp)

Thêm `[skip hooks]` vào commit message:

```bash
git commit -m "fix: ... [skip hooks]"
```

Hook sẽ tự động skip và vẫn cho commit. CI sẽ chạy lại check đầy đủ — không có cách nào
"thoát" check vĩnh viễn, đây là escape hatch cho trường hợp khẩn cấp.

### License header (SPDX / REUSE 3.0)

Tu v1.13.0, plugin tu thu [REUSE 3.0](https://reuse.software/) de khai bao license
cho moi file. Hai cach:

1. **SPDX header** trong file (uu tien cho source code):
   ```python
   # SPDX-FileCopyrightText: 2026 <contributor>
   # SPDX-License-Identifier: MIT
   ```
2. **`REUSE.toml`** o root: them rule neu file/pattern khong phu hop header
   (vd binary file, file tu gen).

File KHONG co license se bi `reuse lint` warning. CI chua enforce - chi canh bao.
Doc `REUSE.toml` o root de xem rules hien tai.

### Không có Python?

Hook tự detect — nếu không tìm thấy `python`/`python3`/`py` thì in warning và skip, **không
block commit**. Tương thích cả WSL/Git Bash/Cygwin (script bash POSIX).

### Ruff (linter + formatter)

Tu v1.12.0, pre-commit hook con chay ruff de:

- **Lint** (`ruff check`): bat loi pyflakes/pycodestyle/isort/bugbear/pyupgrade/simplify
  - Config o root `pyproject.toml` section `[tool.ruff]`
  - Ignore mot so warning cho code cu (E501, B008, SIM108)
- **Format** (`ruff format`): tu dong sua indent/style
- **Chay local** (khong can pre-commit framework):
  ```bash
  pip install ruff
  ruff check --fix .
  ruff format .
  ```
- **Tat ruff** trong pre-commit (khi can push nhanh):
  ```bash
  SKIP=ruff git commit -m "..."
  ```

### Pre-commit hooks (chuan)

Ngoai ruff, con co cac standard check:

- `trailing-whitespace`: xoa space cuoi dong (giu line break cho Markdown)
- `end-of-file-fixer`: them newline cuoi file
- `check-merge-conflict`: chan commit conflict marker `<<<<<<<`
- `check-yaml/json/toml`: validate syntax cac config file
- `mixed-line-ending --fix=lf`: chuan hoa EOL = LF (tru `.bat`/`.ps1` da config rieng trong `.editorconfig`)
- `check-added-large-files`: chan file > 1MB (loai tru `released-objects-index.json` da duoc annotate)
