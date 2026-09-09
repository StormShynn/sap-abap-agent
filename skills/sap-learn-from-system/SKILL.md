---
name: sap-learn-from-system
description: |
  Hoc tu he thong SAP dang ket noi (MCP): doc table/class/CDS that, rut lesson card
  local (Hermes-like), roi dong bo pattern da scrub len Notion "SAP Skills" (opt-out
  private / fail-open). Dung khi "hoc tu he thong", kham pha Z* object.
  KHONG dung thay tip/quiz (sap-daily-learner) hay scaffold (sap-scaffold-*).
when_to_use: |
  "hoc tu he thong", "hoc tu SAP dang ket noi", "kham pha table Z", "doc class ZCL_ de hoc",
  "rut pattern tu package", "lesson tu object that", "explore system objects",
  "chia se lesson Notion", "dong bo lesson len Notion".
argument-hint: "[package | object name | module goi y]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Bash]
---

# SAP Learn From System — Hoc tu MCP SAP that + share Notion (scrub)

## Muc tieu

Khi user **da MCP vao SAP**, skill nay:

1. Xac nhan ket noi (ping).
2. Chon 1–5 object that (table / class / CDS / domain…).
3. Doc source/structure qua MCP — **khong doan**.
4. Viet **lesson card** vao `<agent-home>/memory/` (scrub: khong paste bulk source noi bo).
5. **Doc Notion truoc** (tranh trung) → **ghi Notion** page pattern (DB "SAP Skills") neu khong private.
6. In **checklist** ket thuc.

Lay cam hung Hermes + `sap-daily-learner` muc 3b — **khong** can Hermes Agent / `hermes mcp serve`.

## Khi nao dung

- ✅ User muon hoc / ghi nhan pattern tu **he thong dang ping**.
- ✅ Sau `mcp-sap-connect connect` / MCP Core san sang.
- ❌ Chi muon tip/quiz hang ngay → `sap-daily-learner`.
- ❌ Muon scaffold code → `sap-scaffold-*` / `sap-bootstrap-system-context`.
- ❌ Chua co MCP SAP → dung, huong dan `#cai-dat` / `#ket-noi` / GUI MCP Core.

## Pham vi ghi (BAT BUOC)

Giong `sap-daily-learner`:

- Chi `Write`/`Edit` duoi `<agent-home>` (`agent_home.py` / `SAP_ABAP_AGENT_HOME`).
- Duong dan hop le: `memory/semantic/lessons/`, `memory/semantic/notes/`, `memory/episodic/`.
- **KHONG** ghi source ABAP day du cua khach vao file hay Notion; chi tom tat pattern (ten object, 3–7 bullet).
- **KHONG** promote `reference/modules/` (dung `sap-daily-learner` muc 3c neu can).

Bootstrap neu can:

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/bootstrap_memory.py" \
  --ensure-dir memory/semantic/lessons/system \
  --ensure-dir memory/semantic/notes/system
```

## Scrub rules (local + Notion)

Cam trong lesson / page Notion:

- Toan bo method/source class, SELECT * ket qua, so lieu nghiep vu, user/password/token
- Ten khach hang / tenant id / URL day du neu user yeu cau an (mac dinh: chi hostname profile, khong secret)
- Doan code > ~5 dong — thay bang mo ta "pattern: ... (xem object tren he thong)"

Duoc: ten object, loai, package, 3–7 bullet pattern, module goi y, link ten CDS released (neu public).

## Quy trinh

### Buoc 0 — Gate ket noi

1. Goi MCP `sap_ping` (hoac CLI `mcp-sap-connect ping`) tren profile active / user chi dinh.
2. Fail → dung. Bao user chay `mcp-sap-connect connect` / `reauth`, khong bia lesson.
3. (Tuy chon) `sap_get_system_info` — ghi edition/profile vao phan meta lesson.

### Buoc 1 — Chon doi tuong hoc (toi da 5 / session)

Uu tien:

1. Object user **chi ro**.
2. Package user chi / package Z* (`sap_list_packages` / `sap_search`).
3. Mau Z*/Y*: TABLE, CLAS, DDLS/CDS — 2–5 object **khac loai** neu co the.

Checklist chon (in truoc khi doc nhieu):

- [ ] Da ping OK
- [ ] Co ten object / package muc tieu
- [ ] Gioi han ≤ 5 object
- [ ] User dong y doc object do (neu package lon / nhay cam)

### Buoc 2 — Doc that qua MCP

| Loai | Tool goi y |
|------|------------|
| Class / include | `sap_read_source` |
| Tim theo ten | `sap_search` |
| Package | `sap_list_packages` |
| CDS released | CDS KB `search_cds` / `get_cds_view` |

Doc dung muc can — **khong** dump class lon.

### Buoc 3 — Lesson card local (scrub)

```markdown
# Lesson — <OBJECT> (<TYPE>)
- Profile host (khong secret): ...
- Ngay: YYYY-MM-DD
- Package: ...
## Pattern rut ra
- ...
## Tai sao quan trong (1-3 cau)
- ...
## Lien quan
- Module goi y: SD/FI/... (neu co)
## Share
- Notion: pending | shared | skipped-private | skipped-error
```

Ghi:

- `memory/semantic/notes/system/<object-lower>.md`
- Append `memory/semantic/lessons/system/<MODULE-or-GENERAL>.jsonl`
- Cap nhat nhe `LEARNING_PROGRESS.md` neu topic moi (1 dong)

### Buoc 4 — Notion: doc truoc + ghi sau (SAP Skills)

Tai dung DB + resolve id giong `sap-daily-learner` muc 3b:

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/notion_skills_db.py" get
# --source → env|pin|default
```

Default shared: StormShynn `9d54b58613ad485f8b8f19909adbb219`. Override: env
`SAP_ABAP_AGENT_NOTION_SKILLS_DB` hoac `notion_skills_db.py set …`.
**CAM** `notion-create-database` im lang. **CAM** search DB theo ten.

Properties (cung schema "SAP Skills"):

| Property | Gia tri goi y |
|----------|----------------|
| `Topic` (title) | `[System] <OBJECT> — <pattern ngan>` |
| `Module` (select) | SD/FI/…/GENERAL neu khong ro |
| `Created` (date) | hom nay |
| `Source question` (text) | `Learn from system: <OBJECT> (<TYPE>) @ <package>` |
| `Tags` | **Bo qua** neu option chua co trong schema (gotcha Notion) |

Noi dung page = ban scrub cua lesson (chi Pattern + Tai sao + Lien quan). Khong dinh kem source.

#### 4a. Doc truoc (tranh trung)

1. Search MCP `notion` voi `data_source_url: "collection://<id>"` + tu khoa OBJECT / topic.
2. Chi `notion-fetch` page khop that — neu da co lesson tuong duong → dung lai, bao user,
   ghi local `source: "Dong bo tu Notion"` neu chua co file, **KHONG** tao page trung.

#### 4b. Kiem tra rieng tu (truoc khi ghi)

Bo qua Notion neu:

- Lesson / user co `<private>…</private>`, hoac
- User noi: "dung dong bo", "giu local", "rieng tu", "khong chia se"

Bao: "🔒 Lesson chi luu local — khong dong bo Notion."

#### 4c. Ghi sau (mac dinh khi khong private)

1. `notion_skills_db.py get` → `notion-fetch` lay data source.
2. `notion-create-pages` (ten tool theo session; xem danh sach tool server `notion`) voi
   properties + body scrub.
3. Cap nhat lesson local: `Share: shared` + 1 dong "☁️ Da dong bo Notion (SAP Skills)".
4. **Tu dong, khong hoi** (giong daily-learner 3b) — tru khi private.

#### 4d. Fail-open

Moi loi Notion (chua `/mcp`, OAuth, mang…) → **khong chan** luong local. Mot dong:
"Notion chua ket noi / loi — chi luu local." Cap nhat `Share: skipped-error`.

Ten tool: dung dung tool dang thay (`notion-search` / `notion-fetch` / `notion-create-pages`…) —
khong doan ten.

### Buoc 5 — Checklist ket thuc

In `skills/sap-learn-from-system/CHECKLIST.md` (tom tat + trang thai Share).

## Lien ket

- `sap-daily-learner` — tip, quiz, auto-skill, promote 3c, curator
- `sap-bootstrap-system-context` — do quy uoc truoc scaffold
- `reference/scripts/notion_skills_db.py` — resolve DB id
- MCP Core: `mcp-sap-connect`, dict-bridge, cds-kb, mcp-sap-docs-btp + MCP `notion`
