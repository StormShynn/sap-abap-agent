# 📋 Changelog — SAP ABAP Agent

All notable changes to this project will be documented in this file.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/) và [Semantic Versioning](https://semver.org/).

---

## [v0.9.2] — 2026-07-12

### Changed
- 🔙 **index.html: bo he thong tab** them o v0.9.1 (tab bar, `data-tab` attribute tren 47 section/
  nav-link/nav-section, CSS `.tab-bar`/`.tab-btn`, JS chuyen tab) — quay lai trang scroll don nhu
  truoc, theo phan hoi truc tiep cua nguoi dung. **Giu nguyen** toan bo noi dung da them cung dot
  (section `workflow-by-goal` + so do flowchart 3 nhanh Bao cao/API/Form, hang `sap-ask-consultant`
  2a/2b, hang `sap-deployment-target` 2c, dang ky `sap-scaffold-cds-analytics`, sua dem skill/
  version cu, fix bug `<tr>` lap doi trong bang MCP Tools) — chi bo phan co che tab, khong bo noi
  dung.
- File `out/sap-abap-codegen-pkg/mo-hinh-ai-codegen.html` (rieng, ngoai git) cung da duoc khoi
  phuc ve dung ban goc truoc do theo yeu cau tuong tu.

### Notes
- Da verify: HTML can bang the (0 loi qua checker Python `html.parser`), ca 2 script block con
  lai hop le qua `node --check` (dung 2 block nhu truoc khi co tab — dung 1 block them cho JS tab
  da bi xoa).

---

## [v0.9.1] — 2026-07-12

### Added
- 🗂️ **index.html: chia noi dung thanh 6 tab** (`tab-start`, `tab-usage`, `tab-consultant`,
  `tab-skills`, `tab-pipeline`, `tab-reference`) thay vi 1 trang scroll dai lien tuc (47 section).
  Tab bar moi o dau trang; sidebar/nav-link, hero CTA, ket qua search deu tu dong chuyen sang
  dung tab roi moi scroll toi section (thay vi anchor jump vao 1 section dang bi an). Tab hien
  tai duoc nho qua `localStorage`, deep-link qua `#section-id` van hoat dong (tu xac dinh tab
  chua section do khi tai trang).
- 📊 **Sơ đồ flowchart truc quan** cho 3 quy trinh Bao cao/API/Form trong `workflow-by-goal`:
  than cay chung (buoc 0 → 2c) roi re 3 nhanh mau khac nhau (xanh la/Bao cao, xanh duong/API,
  tim/Form), moi node la 1 the co ten skill + mo ta ngan, phan biet buoc bat buoc/tuy chon/
  milestone bang style rieng — thay the bang chi doc bang text de hinh dung tong quan nhanh hon
  (bang chi tiet van giu nguyen ben duoi de tra cuu).

### Fixed
- 🐛 **Bug co san (khong phai do phien nay gay ra), phat hien qua kiem tra HTML tu dong**: bang
  "MCP Tools" co 1 the `<tr>` bi lap doi (dong ngay truoc row `sap_activate`), thieu `</tr>` dong
  cho row truoc do — sua thanh 1 `<tr>` dung.
- Header/footer/hero con ghi **"v0.8.3"** (3 cho) du plugin da len toi v0.9.0 tu lau — cap nhat
  dong bo thanh version + so skill/agent hien tai (48 skill, 27 agent).

### Notes
- Da verify: chay `node --check` tren ca 3 script block (khong loi), tu viet 1 HTML tag-balance
  checker (Python `html.parser`) quet toan bo file — 0 loi mismatch sau khi sua. Load thu object
  `translations` qua `node`, spot-check nhieu entry moi deu resolve dung.
- ⚠️ [Unverified] **KHONG the mo trang that trong trinh duyet de xac nhan bang mat** — Playwright
  chua cai duoc trong moi truong nay (loi chung thuc SSL khi tai ve qua npm), nen moi kiem tra o
  tren chi la kiem tra CAU TRUC (HTML/CSS/JS hop le), KHONG phai kiem tra hien thi/tuong tac that.
  De nghi tu mo `index.html` (hoac ban GitHub Pages sau khi deploy) tren trinh duyet that de xac
  nhan: (1) 6 tab chuyen dung, (2) sidebar/search/hero link tu dong nhay tab dung, (3) so do
  flowchart hien thi dung ca 2 theme sang/toi va tren mobile, truoc khi coi la hoan tat.
- Da giu nguyen toan bo noi dung/section cu (khong xoa gi) — chi them thuoc tinh `data-tab` +
  CSS an/hien qua class, khong di chuyen/viet lai noi dung cac section da co.

---

## [v0.9.0] — 2026-07-12

### Added
- 🔒 **`hooks/zy_namespace_guard.py`** (PreToolUse) — backstop KY THUAT cho quy tac "khong tao/
  sua/xoa object ngoai Z/Y" (`sap-clean-code`/`sap-deployment-target`): tu dong CHAN (khong chi
  canh bao) bat ky tool call nao trong tinh (create/update/delete) x (domain/data element/table/
  structure/view/behavior definition/metadata extension/service definition) — bao gom ca
  `sap_create_domain`/`sap_create_data_element`/`sap_create_table` (native `sap-dict-bridge`) lan
  `CreateDomain`/`CreateTable`/... (ADT MCP fork) — neu tham so ten object khong bat dau `Z`/`Y`
  hoac `/namespace/` da dang ky. Fail-open tuyet doi: bat ky loi parse/khong nhan dien duoc field
  ten deu cho qua (KHONG chan nham), dung chung triet ly voi `verify_nudge.py` da co.
  Da test 8 case (block/allow/fail-open) qua stdin gia lap truoc khi wire vao `hooks.json`.

### Notes
- Nguoi dung dua 1 file hooks.json tham khao tu 1 plugin khac ("sc4sap") voi kien truc rat rong
  (12 loai hook event, ~20 script Node.js: UserPromptSubmit keyword-detector, SubagentStart/Stop
  tracking, PreCompact, SessionEnd...). **Khong copy nguyen** kien truc do — ly do: (1) toan bo
  hook script hien co cua repo nay dung Python, dua them Node.js/`.mjs` se tao 2 runtime song
  song khong can thiet; (2) da so cac hook event kia (UserPromptSubmit, SubagentStart/Stop,
  PreCompact, SessionEnd, PermissionRequest) chua co nhu cau cu the, tu them vao se thanh "lan
  man" (dung tu cua chinh nguoi dung) — chi rui ro moi ma khong giai quyet gap nao dang co that.
  Chi lay 1 y tuong CO GIA TRI RO RANG va khop truc tiep voi rao chan da thiet ke o
  `sap-deployment-target`/`sap-clean-code`: PreToolUse guard chan tao/sua/xoa object ngoai Z/Y —
  chuyen the sang Python, tu viet logic rieng (KHONG copy code cua sc4sap, chi lay y tuong ve loai
  hook event nen dung).
- ⚠️ [Unverified] Da test ky script `zy_namespace_guard.py` bang stdin gia lap (8 case) va xac
  nhan JSON hooks.json hop le — nhung CHUA the xac nhan Claude Code that su goi dung hook
  PreToolUse voi hinh dang `tool_name`/`tool_input` nhu gia dinh cho MCP tool call that (repo nay
  chua co vi du PreToolUse nao khac de doi chieu, chi co Stop/PostToolUse da chay that qua
  `verify_nudge.py`). Nen tu xac nhan bang 1 lan goi tool MCP that (vd thu tao object ten sai
  namespace) truoc khi tin tuong hoan toan vao backstop nay.

---

## [v0.8.9] — 2026-07-12

### Added
- 🆕 **sap-ask-before-guessing** (`skills/sap-ask-before-guessing`) — nguyen tac chung: khi thieu
  thong tin de lam dung 1 hanh dong anh huong that len he thong SAP (tao/sua/xoa object, chon
  CDS/package/pattern...), PHAI hoi lai user thay vi tu doan "phuong an hop ly". Tong quat hoa
  vien co R4 cua `sap-routing-discipline` (von chi ap dung cho routing module) ra MOI diem quyet
  dinh trong pipeline scaffold/deploy. Bom tu dong vao dau moi phien qua `hooks/hooks.json`
  (SessionStart) — cung co che voi `sap-routing-discipline`, 2 hook command doc lap.

### Notes
- Nguoi dung hoi truc tiep "lam sao de tao rule chung cho Claude, cho nao khong ro thi phai hoi
  lai het" — quyet dinh dung co che **bom qua SessionStart hook** (nhu `sap-routing-discipline`
  co san) thay vi CLAUDE.md, vi hooks.json cua plugin nay ap dung MOI khi plugin duoc dung (bat
  ke dang lam viec o project SAP nao), con CLAUDE.md dat trong repo plugin nay se KHONG duoc doc
  khi plugin duoc cai vao du an cua nguoi dung khac. Neu muon 1 rule that su toan cuc (moi phien
  Claude Code, khong lien quan SAP) thi phai dung `~/.claude/settings.json`/CLAUDE.md o may ca
  nhan — khac pham vi voi hooks.json cua plugin nay (chua lam, ngoai pham vi cau hoi lan nay).
- Da verify: JSON hooks.json hop le (`python -c "import json; json.load(...)"`), va lenh shell moi
  chay thu that (gia lap `CLAUDE_PLUGIN_ROOT`) tra ve dung JSON `hookSpecificOutput` mong doi,
  exit code 0.

---

## [v0.8.8] — 2026-07-12

### Added
- 🆕 **sap-deployment-target** (`skills/sap-deployment-target`) — skill moi, dung sau
  `sap-write-technical-spec` truoc khi scaffold: (1) hoi user deploy vao package nao tren he thong
  that (co san hoac tao moi package Z, hoi xac nhan ro rang truoc khi tao that); (2) rao chan an
  toan xuyen suot pipeline — tuyet doi khong tao/sua/xoa object ngoai namespace Z/Y hoac ngoai
  package da xac nhan; (3) gate cho moi buoc can thao tac thu cong (approve transport, dang nhap,
  activate khi chua noi MCP...) — dung lai, mo ta ro viec can lam, chi tiep tuc sau khi user xac
  nhan xong.

### Fixed
- `skills/sap-cloud-dictionary/SKILL.md`: thieu han **Buoc 0 (kiem tra reuse truoc khi tao moi)**
  — chi co quy trinh tao Domain/Data Element/Table, khong bat buoc kiem tra Data Element chuan SAP
  hoac object Z/Y co san (qua `sap-bootstrap-system-context`) truoc. Them Buoc 0 + cross-reference
  `sap-deployment-target`.
- `skills/sap-finish-ticket/SKILL.md` (Buoc 5): check "transport dung package" nhung khong doi
  chieu voi quyet dinh package nao da duoc xac nhan voi user — sua thanh doi chieu ro voi
  `sap-deployment-target`.
- `skills/sap-clean-code/SKILL.md`: co quy tac Z/Y namespace nhung chua co phat bieu ro rang
  "TUYET DOI KHONG tao/sua/xoa object chuan SAP" nhu 1 rao chan an toan doc lap — them doan canh
  bao ro rang + tro toi `sap-deployment-target`.
- `skills/sap-write-technical-spec/SKILL.md`: them cross-reference `sap-deployment-target` la
  buoc bat buoc tiep theo sau khi TECHNICAL_SPEC.md hoan tat.
- `index.html`: 3 quy trinh Bao cao/API/Form chua co buoc xac dinh package deploy + rao chan an
  toan. Them hang **2c** (`sap-deployment-target`) vao ca 2 bang Bao cao va API (Form ke thua) +
  1 doan giai thich muc dich ngay dau section. Sua lai 1 dict entry dich thuat rui ro (tu ngan
  chung "bắt buộc" dat o do uu tien cao co the ghi de len cac cau khac chua dich trong toan bo
  file 4000+ dong) — gop lai thanh 1 chuoi dai + duy nhat truoc khi them ban dich.

### Notes
- Phat hien tu phan hoi truc tiep cua nguoi dung: "xin thong tin package de deploy, tranh dung
  standard SAP, cho nao thu cong thi hoi xac nhan roi moi lam tiep" — chua co co che nao trong
  repo cover day du 3 y nay truoc ban nay.

---

## [v0.8.7] — 2026-07-12

### Fixed
- 🐛 **`skills/sap-write-technical-spec/SKILL.md` (Buoc 3)**: chi noi mo ho "hoi agent consultant
  tuong ung" — khong bat buoc di qua routing engine `sap-ask-consultant`, nen co the bo sot
  **module coupling** (ticket dung nhieu phan he cung luc, vd Sales Order can ca SD+FI) va de tu
  chon/tu doan sai consultant. Sua: Buoc 3 diem 1 gio **bat buoc** dispatch qua `sap-ask-consultant`.
- 🆕 **Them "xac nhan 2 chieu" vao cuoi Buoc 4**: sau khi liet ke xong object/field, phai gui lai
  danh sach cho **cung consultant** xac nhan lan 2 truoc khi chot TECHNICAL_SPEC.md — bat loi chon
  sai muc dich (grain CDS sai, thieu field nghiep vu, nham phan he) truoc khi scaffold code that,
  thay vi phat hien sau khi da activate ton kem hon.
- `index.html` (3 quy trinh Bao cao/API/Form them tu phien truoc): **thieu hoan toan buoc
  `sap-ask-consultant`** — chi ghi tat "tim CDS/Cube nguon da released" ben trong step 2, khong
  hien thi ro rang. Them 2 hang moi **2a** (dispatch chon CDS nguon) va **2b** (xac nhan lai danh
  sach object) vao ca bang Bao cao va API (Form ke thua tu bang API) + 1 doan giai thich muc dich
  ngay dau section.

### Notes
- Phat hien tu phan hoi truc tiep cua nguoi dung ve pipeline moi them — dung frontmatter cua
  `sap-write-technical-spec` (da co san "hoi agent consultant" nhung ghi qua mo ho) lam co so de
  sua chinh xac, khong doan lai tu dau.

---

## [v0.8.6] — 2026-07-12

### Added
- 📚 Ghi nhan chinh thuc trong CHANGELOG cho cong viec cua session song song (skill
  `sap-cloud-dictionary`, MCP server native **`sap-dict-bridge`** —
  `reference/mcp-server/sap_btp_agent/bridge_server.py` + `tools/dictionary.py`, 3 tool
  `sap_create_domain`/`sap_create_data_element`/`sap_create_table`, `client.py` them
  `put()`/`delete()` cho ADT REST workflow lock→PUT source→activate→unlock) — truoc day chua co
  entry rieng du code/skill da ton tai tu v0.8.4-0.8.5.

### Fixed
- `README.md`, `index.html`: Dem "45 skill implementations" thieu `sap-cloud-dictionary` (chi tinh
  skill cua session nay, quen skill cua session kia) — sua thanh **46** (dung tong so thu muc that
  trong `skills/`, tru `sap-user-skills` la placeholder rong).
- `README.md`: Them `sap-cloud-dictionary` vao cau truc thu muc `skills/` (thieu hoan toan).
- `index.html`: Them hang "2.6" (`sap-cloud-dictionary`) vao bang pipeline, them 2 dong
  `sap_create_domain`/`sap_create_data_element`/`sap_create_table` vao so do MCP tools.
- `skills/sap-cloud-dictionary/SKILL.md` (Buoc 8): Bang MCP server tao dictionary chi liet ke
  `fr0ster/mcp-abap-adt`/ARC-1/SAP Official — **thieu `sap-dict-bridge`** (server native da duoc
  xay dung thuc te trong chinh repo nay, thay the huong fr0ster ban dau). Them dong moi + danh dau
  khuyen dung.
- `skills/mcp-sap-adt/SKILL.md`: Them ghi chu o Option B (fr0ster) rang du an nay da chuyen sang
  `sap-dict-bridge` native — tranh nguoi doc tuong fr0ster van la huong dang dung thuc te.
- 🐛 **`reference/mcp-server/sap_btp_agent/tools/dictionary.py` (`_build_table_ddl`)**: tham so
  `fields[].key` truoc day chi quyet dinh co them `not null` hay khong, **KHONG** tu them tu khoa
  `key` vao truoc ten field trong DDL sinh ra — 2 field mac dinh (`"key client"`, `"key uuid"`)
  chay dung chi vi chu "key " da go san trong chuoi `name`, khong phai nho tham so `key`. Goi tool
  voi field moi kieu `{"name": "order_id", "key": "true"}` (dung theo mo ta tham so trong schema)
  truoc day se ra field **khong phai key** ma khong bao loi. Da sua: chuan hoa bo tien to "key "
  neu co san trong `name` roi tu quyet dinh them lai dua vao `key`, nen ca 2 kieu goi (ten da go
  san "key "/ten thuong + flag `key`) deu ra dung. Da verify qua goi `_build_table_ddl` truc tiep
  voi ca 2 kieu input, doi chieu DDL sinh ra dung nhu mong doi (xem `sap-cloud-dictionary` Buoc 8).
  Test script thu cong truoc day (`scripts/test_dict_bridge.py`) chi cover Domain + Data Element,
  chua cover Table nen khong bat duoc bug nay — script nay da bi don dep (xem muc duoi), chua co
  unit test tu dong rieng cho `sap_create_table`.

### Cleanup
- Da xac nhan `scripts/setup_mcp_fr0ster.py` la du dinh don dep (khong phai giu lam fallback) va
  don triet de toan bo dau vet huong fr0ster ban dau, gom ca phan NGOAI repo (khong nam trong git):
  - Go dang ky 2 MCP server chet o user scope (`mcp-abap-adt-my428100`, `mcp-abap-adt-my440301` —
    ca 2 deu bao "✘ Failed to connect" vi `.env` chua bao gio duoc dien SAP_USERNAME/PASSWORD that,
    xac nhan script cu tung chay nhung chua hoan tat setup).
  - Xoa `mcp-abap-adt.env` trong 2 profile folder + `mcp-abap-adt-config.yaml` dung chung tai
    `%USERPROFILE%\.sap-btp-agent\`.
  - `scripts/setup_mcp_fr0ster.py` va `scripts/test_dict_bridge.py` da khong con trong repo (thu
    muc `scripts/` da duoc don, co ve do chinh session song song tu xoa khi hoi tu).

---

## [v0.8.5] — 2026-07-12

### Added
- 🆕 **sap-bootstrap-system-context** (`skills/sap-bootstrap-system-context`) — Do he thong ABAP
  that qua MCP ADT (`mcp-sap-adt`) truoc khi scaffold lan dau tren 1 he thong la, lay dung quy uoc
  dat ten/field admin dang dung thay vi doan theo chuan chung. Ghi cache vao
  `<agent-home>/cache/system-context/` (het han 7 ngay). Dong co: chinh phien lam viec truoc do da
  doan sai ten data element + paradigm DDIC vi khong kiem tra truoc.
- 🆕 **sap-cds-unit-test** (`skills/sap-cds-unit-test`) — Test CDS view/RAP BO bang CDS Test Double
  Framework (`CL_CDS_TEST_ENVIRONMENT`, `CL_OSQL_TEST_ENVIRONMENT`,
  `CL_BOTD_TXBUFDBL_BO_TEST_ENV`/`CL_BOTD_MOCKEMLAPI_BO_TEST_ENV`) — mock data nguon thay vi dam
  vao DB that. Bo sung cho `sap-unit-test` (von chi test method/class thuong).
- 🆕 **sap-migrate-segw-to-rap** (`skills/sap-migrate-segw-to-rap`) — Quy trinh reverse-engineer 1
  SEGW OData V2 project da co sang RAP OData V4: doc Data Model + custom logic trong DPC_EXT, map
  bang sang RAP behavior/action, huong dan dual-maintenance truoc khi tat SEGW.

### Changed
- `skills/sap-unit-test/SKILL.md`, `skills/sap-scaffold-rap/SKILL.md`,
  `skills/sap-odata-service/SKILL.md`: Them cross-reference toi 3 skill moi.
- `README.md`, `index.html`: Dang ky 3 skill moi (cau truc thu muc, bang pipeline hang 2.5/5b,
  dem "45 skill implementations", ban dich EN).
- `.claude-plugin/plugin.json`: Bump version v0.8.4 → v0.8.5.

### Notes
- Ca 3 skill deu tu research GitHub (arc-1 skills: `generate-rap-service-researched`,
  `generate-cds-unit-test`, `migrate-segw-to-rap`, `bootstrap-system-context`) — chuyen the sang
  ngu canh/quy uoc cua repo nay, KHONG copy nguyen code (chua verify code goc cua arc-1). Cu phap
  CDS Test Double Framework trong `sap-cds-unit-test` co nguon SAP Help Portal + SAP Community rieng
  (xem muc Nguon tham khao trong skill), KHONG tu arc-1.

---

## [v0.8.4] — 2026-07-12

### Added
- 🆕 **sap-scaffold-cds-analytics** (`skills/sap-scaffold-cds-analytics`) — Sinh CDS Cube/
  Dimension/Text + Analytical Query cho bao cao embedded analytics (aggregate/multi-dimensional).
  Uu tien build Analytical Query tren CDS/Cube da released (theo huong dan co san trong
  `reference/modules/sap-bw-cloud/SKILL.md`) truoc khi tu tao Cube tu dau. Tu danh dau ro tinh
  trang "seed set" — noi dung tong hop tu tai lieu SAP, chua activate thu trong ADT that.

### Fixed
- 🐛 **`reference/templates/rap-boilerplate/managed/ztb_object.tabl.xml`**: Template table truoc
  day thieu han phan field list (`DD03P_TABLE`) — chi co header (`DD02V`/`DD09L`), khong du de tao
  table that co field. Bo sung field list mau (client/UUID key/business field + 4 field admin
  CreatedBy/CreatedAt/LastChangedBy/LastChangedAt tro dung data element chuan SAP
  `ABP_CREATION_USER`/`ABP_CREATION_TSTMPL`/`ABP_LOCINST_LASTCHANGE_USER`/
  `ABP_LOCINST_LASTCHANGE_TSTMPL`).
- `skills/sap-scaffold-rap/SKILL.md`: Them gotcha #8 — nhac kiem tra table co du 4 field admin
  truoc khi khai `etag master LastChangedAt` trong BDEF (thieu se loi luc save cho managed BO co
  draft/lock).

### Changed
- `README.md`: Them `sap-scaffold-cds-analytics` vao cau truc thu muc `skills/`.
- `index.html`: Them dong 3c vao bang pipeline "Buoc nao lam gi", cap nhat dem "42 skill
  implementations", them ban dich EN cho mo ta skill moi.
- `.claude-plugin/plugin.json`: Bump version v0.8.3 → v0.8.4.

### Notes
- Phien nay phat hien co 1 session Claude Code khac chay song song sua cung repo (them
  `skills/sap-cloud-dictionary`, cap nhat `skills/mcp-sap-adt/SKILL.md`, wiring MCP server
  `fr0ster/mcp-abap-adt` qua `.mcp.json`/`scripts/setup_mcp_fr0ster.py`) — cac thay doi do KHONG
  nam trong entry nay, se duoc ghi nhan rieng khi session do hoan tat.
- Da xoa 1 skill nhap nham `sap-scaffold-ddic` (dung cu phap DD01V/DD04V XML kieu on-premise) sau
  khi phat hien `skills/sap-cloud-dictionary` (cua session song song) dung dung cu phap ABAP Cloud
  (`define domain`/`define data element`/`define table`) — tranh 2 skill trung chuc nang, giu ban
  dung hon.

---

## [v0.8.3] — 2026-07-12

### Fixed
- 🏠 **State của plugin (memory/cache/sessions/handoff) chuyển từ project-relative sang
  `%USERPROFILE%\.sap-abap-agent\`** — các skill `sap-daily-learner`, `sap-context-tool-result-trim`,
  `sap-scaffold-context-summary`, `sap-analyze-function-spec`, `sap-routing-discipline`,
  `sap-handoff` trước đây ghi `<workspace>/.sap-abap-agent/...`, chỉ đúng khi dev ngay trong repo
  plugin (workspace tình cờ trùng plugin repo) — SAI khi plugin được cài thật và dùng trên 1
  project SAP khác (sẽ ghi lộn state cá nhân vào repo của client). Thêm
  `reference/scripts/agent_home.py` (tương đương `config/paths.py` của `sap_btp_agent`) để resolve
  `%USERPROFILE%\.sap-abap-agent\` mặc định, override qua `SAP_ABAP_AGENT_HOME` khi dev/test trong
  project.
- 🔧 **Script invocation dùng `${CLAUDE_PLUGIN_ROOT}`** thay vì đường dẫn tương đối
  (`reference/scripts/*.py`) trong các SKILL.md/command gọi `office_to_md.py`,
  `lesson_card_add.py`, `lesson_card_retrieve.py`, `sap_naming_lint.py`, `check_released_api.py`,
  `sync_skills.py` — đường dẫn tương đối chỉ đúng khi cwd là repo plugin (dev/test), sẽ báo lỗi
  "file not found" khi plugin cài thật và Claude Code đang mở project khác.
- Fix typo `sap-bap-agent` → `sap-abap-agent` trong `skills/sap-context-tool-result-trim/SKILL.md`.
- 🐛 **`sync_skills.py`: `REPO_DIR` tính sai 1 cấp thư mục** (`Path(__file__).resolve().parent.parent`
  trỏ vào `reference/` thay vì gốc repo, do file này nằm ở `reference/scripts/` chứ không phải
  `scripts/`) — khiến daemon LUÔN báo "không phải git repo" và bỏ qua, kể cả khi chạy đúng trong
  repo git thật (đã verify bằng cách chạy trực tiếp trước/sau fix). Tự-cập-nhật qua `/sync-skills`
  hoặc daemon nền coi như không hoạt động cho tới bản này. Sửa thành `.parent.parent.parent` +
  cập nhật các ví dụ đường dẫn trong docstring/help cho khớp; cũng fix `SyntaxWarning` do `\p`
  trong docstring (chuyển sang raw string).
- Shell variable không tồn tại xuyên các lần gọi Bash riêng biệt (`$MEMORY_ROOT` trong
  `sap-daily-learner`, `$SESSION_DIR` trong `sap-analyze-function-spec`) — mỗi lệnh giờ tự
  resolve lại qua command substitution lồng nhau thay vì dựa vào biến set ở lệnh trước. Tiện thể
  fix luôn cmdlet PowerShell (`New-Item`/`Copy-Item`) lẫn trong code fence `bash` của
  `sap-analyze-function-spec` (đổi sang `mkdir -p`/`cp` cho đúng Git Bash).

### Added
- 🧹 **`reference/scripts/cleanup_agent_home.py`** — dọn cache/log tích lũy trong `<agent-home>`
  để tránh phình thư mục local: (1) xóa file trong `<agent-home>/cache/` cũ hơn N ngày (mặc định
  7, đọc override từ `<agent-home>/cache/.retention` nếu có — đúng policy đã ghi trong
  `sap-context-tool-result-trim/SKILL.md` nhưng trước đây chưa có code triển khai), rồi ép tổng
  dung lượng dưới cap (mặc định 500MB, xóa tiếp từ file cũ nhất nếu còn vượt); (2) trim các dòng
  cũ hơn N ngày trong `sync_skills.log`. Có `--dry-run` để xem trước, đã test thực tế cả 2 nhánh
  (theo tuổi, theo dung lượng, đọc `.retention`, trim log).

### Changed
- `.gitignore`: thêm `.sap-abap-agent/memory/`, `.sap-abap-agent/cache/`,
  `.sap-abap-agent/sync_skills.lock` (thiếu từ trước, phát sinh khi dev/test đặt
  `SAP_ABAP_AGENT_HOME` trỏ vào project).
- `CONTRIBUTING.md`: cập nhật mục "File không nên push lên repo" + thêm mục giải thích
  `SAP_ABAP_AGENT_HOME` (khác `SAP_BTP_AGENT_HOME`/`SAP_BTP_AGENT_DEV_MIRROR` của `sap-btp-agent`).

---

## [v0.7.0] — 2026-07-11

### Added
- 🆕 **SAP IBP Consultant** (`sap-ibp-consultant-cloud`) — Supply Chain Planning agent: Demand
  Planning (forecast, AI/ML sensing), Supply Planning (heuristic/optimizer), Inventory Optimization,
  S&OP, Control Tower. Reference module 2-layer CORE+DEEP.
- 🆕 **SAP EWM Consultant** (`sap-ewm-consultant-cloud`) — Extended Warehouse Management agent:
  inbound/outbound, wave, slotting, kitting, VAS, labor, RF, yard. Embedded EWM (scope BK9) thay
  WM (EOL 2025). Reference module 2-layer CORE+DEEP.
- 🔀 **Routing Engine update**: The IBP + EWM vao keyword matrix + module coupling. Tong agent tu
  20 → 22 (20 module consultants + 1 researcher + 1 daily learner).

### Changed
- `skills/sap-ask-consultant/SKILL.md`: Routing matrix m rong them IBP + EWM keywords & coupling.
- `index.html`: Cap nhat version counts (22 agents, 23 files), them IBP/EWM vao module list, keyword
  matrix, coupling bang, agent directory feature cards.
- `.claude-plugin/plugin.json`: Bump version v0.6.5 → v0.7.0.
- `agents/sap-ibp-consultant-cloud.md`: Bo skill `sap-clean-code` + `sap-extensibility` (IBP la cloud
  service rieng, khong dung ABAP naming/extensibility ladder).

---

## [v0.6.5] — 2026-07-11

### Added
- 🧩 **ACE-style lesson cards** cho `sap-daily-learner` (bo sung cho Knowledge Graph, khong thay
  the auto-skill-creation) — thay vi luon tao ca 1 skill file cho cau tra loi phuc tap (de phinh,
  kho retrieve), extract 1-3 fact ngan (1-3 dong) va luu vao
  `.sap-abap-agent/memory/semantic/lessons/<MODULE>.jsonl`.
  - `reference/scripts/lesson_card_add.py` — append-or-skip-duplicate (Jaccard similarity >= 0.8
    tren cung topic), KHONG bao gio wholesale-rewrite (tranh "context collapse" kieu ACE mo ta,
    arXiv 2510.04618).
  - `reference/scripts/lesson_card_retrieve.py` — retrieval scoring
    `0.5*keyword_overlap + 0.3*recency + 0.2*usage_frequency`, top-K, tu tang `usage_count`.
  - **Temporal validity**: moi card co the co `valid_until` — card het han bi loai hoan toan khoi
    retrieval (fact gan release SAP cu, vd 2502, khong "poison" context sau khi SAP ra ban moi).
  - Da test 11 case that (add/dedup/expired/retrieve/module-isolation) truoc khi tich hop vao
    SKILL.md. Phat hien va fix 1 bug that qua test: recency+usage co the tu day 1 fact khong lien
    quan len tren nguong diem chi vi no "moi"/"hay duoc dung" — them dieu kien bat buoc co it nhat
    1 tu khoa trung truoc khi 1 card duoc coi la ung vien.
  - Quyet dinh kien truc: **khong dung Mem0/Zep/Letta** (framework memory ngoai) — giu kien truc
    filesystem/JSONL hien co, khong them dependency/vector-store de giu dung trai nghiem cai dat
    "1 lenh pip install".
  - Cap nhat `skills/sap-daily-learner/SKILL.md` (section moi "Lesson Cards") va
    `agents/sap-daily-learner.md` (duong dan `LEARNING_PROGRESS.md` dang tro sai cho cu, va them
    bang quyet dinh "lesson card vs skill file day du" — sua boi phien nay, khong phai phien dang
    thiet ke 3-tier memory).

---

## [v0.6.4] — 2026-07-11

### Fixed
- `index.html`: **244 doan text chua co ban dich EN** (phat hien bang script mo phong dung logic
  thay the VI→EN cua chinh trang, khong doan bang mat) — da dich va them vao `translations`.
  - Lan quet dau tien bao 336 doan; sau khi phat hien 1 loi trong chinh script kiem tra (`.strip()`
    truoc khi so sanh, trong khi thuat toan that dung whitespace nguyen ban) — sua lai va quet lai
    ra so chinh xac: **244**.
  - Da verify: mo phong tinh toan lai ra **0** con thieu; **test that qua trinh duyet Chromium
    that** (Playwright) — bam nut chuyen EN that, doc DOM that, xac nhan 4 doan mau (kem toan bo
    244) khong con xuat hien nguyen van tieng Viet.
  - **Phat hien phu (chua sua, ngoai pham vi lan nay)**: co che dich cua trang dung substring-replace
    tuan tu theo thu tu khai bao trong dict — 1 entry ngan/chung chung (vd `'Bắt đầu': 'Getting
    Started'`) co the chay truoc va lam hong 1 cau dai hon chua chinh no (vd `'⚡ Bắt đầu cài đặt':
    '⚡ Start Installation'`), de lai ket qua lai tieng ("⚡ Getting Started cài đặt"). Da xac nhan
    day la loi co tu truoc (test lai ban HEAD chua sua: **324** doan con loi kieu nay). Sau khi
    them 244 ban dich moi (dat truoc dict cu de uu tien full-match), so doan loi giam con **93** —
    cai thien that nhung chua giai quyet triet de kien truc thay the tuan tu nay.

---

## [v0.6.3] — 2026-07-11

### Added
- 🪝 **`hooks/verify_nudge.py`** + wiring moi trong `hooks/hooks.json`: nhac 1 lan (khong chan
  cung, khong lap) khi da sua file code (`.abap`/`.asddls`/`.asddlxs`/`.asbdef`/`.asdcls` hoac
  file trong `out/*/src/`) nhung chua chay lenh nao (`Bash`) truoc khi ket thuc luot — chi vao
  skill `sap-verification-before-completion`.
  - `PostToolUse` (`Edit|Write`): danh dau "cho verify" (sentinel file trong OS temp, khoa theo
    `session_id` — khong nam trong repo, khong anh huong git).
  - `PostToolUse` (`Bash`): xoa danh dau (coi nhu da verify — co tinh don gian, khong phan biet
    lenh test that hay khong, danh doi lay it false-positive/khong the treo session).
  - `Stop`: neu con "cho verify" — chan 1 lan (`{"decision":"block","reason":...}`), **tieu thu
    sentinel ngay lap tuc** nen khong the chan lan 2 cho cung 1 lan sua. Kiem tra `stop_hook_active`
    truoc (khong bao gio chan 2 lan lien tiep) — 2 lop an toan doc lap, tranh dung lap vo han
    (co that trong thuc te: GitHub issue #55754 cua anthropics/claude-code, 1 Stop hook loi da
    treo phien ~50 phut).
  - Fail-open tuyet doi: moi loi/parse-fail deu `exit 0` im lang, khong bao gio chan vi bug cua
    chinh script nay.
  - Da test 8 case rieng cho script + 4 case end-to-end qua dung lenh trong `hooks.json` (khong
    phai goi script truc tiep) truoc khi wire.

---

## [v0.6.1] — 2026-07-11

### Changed
- `skills/sap-clean-code/`: Tach tu 1 file 1244 dong (vuot ngưỡng chinh thuc 500 dong/SKILL.md
  cua Anthropic — [platform.claude.com/docs Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
  thanh progressive disclosure 4 file:
  - `SKILL.md` (202 dong): Tong quan + Naming co ban + Clean ABAP Naming Rules + Cheat Sheet +
    dieu huong toi 3 file reference.
  - `reference/name-conversion.md` (86 dong): Name Conversion Guide (class/method/variable/parameter).
  - `reference/abap-cloud-rules.md` (488 dong): Development Object Naming, CDS VDM 5-layer, RAP BO naming.
  - `reference/checklists.md` (509 dong): field symbol/constants/exception/DI naming, Clean Code
    Rules, Released APIs checklist, ABAP Formatter, Code Inspector/ATC.
  - Reference file chi load khi Claude chu dong doc (0 token neu khong dung toi) — dung dung
    pattern "Domain-specific organization" trong tai lieu chinh thuc noi tren.
  - Da verify khong mat noi dung: doi chieu dong (1244 → 1285 dong tren ca 4 file, phan tang la
    ToC + nav moi them), spot-check 7 tu khoa dai dien deu con nguyen.
  - Nhan tien dedup 1 doan "ABAP Cleaner" bi lap y het 2 lan trong file goc (muc 11 va 12.8) —
    gio chi con 1 ban trong `reference/checklists.md`.
- `.claude-plugin/plugin.json`: Bump version v0.6.0 → v0.6.1 (patch — thuan tuy reorganize noi
  bo, khong doi hanh vi/tinh nang cua skill).

---

## [v0.6.0] — 2026-07-11

### Added
- 🔒 **sap-routing-discipline** — meta-skill bom tu dong qua SessionStart hook
  (`hooks/hooks.json`), ep luon check routing qua `sap-ask-consultant` truoc khi tra loi, kem
  bang anti-rationalization (cung format R1-R7 da dung trong `sap-atc-review`).
- ✅ **sap-verification-before-completion** — nguyen tac bat buoc: phai co bang chung chay that
  truoc khi bao "xong"/"da fix", khong duoc suy tu "doc code thay hop ly".
- 🏁 **sap-finish-ticket** — buoc 6 (cuoi) trong pipeline codegen: checklist activation + ATC
  PASS + unit test xanh + transport + abapGit truoc khi dong ticket.
- 🐞 **sap-systematic-debugging** — quy trinh debug runtime ABAP co he thong (ST22/SAT/breakpoint),
  1 gia thuyet 1 lan, xac nhan truoc khi sua, regression test sau khi fix.
- 🪝 **SessionStart hook** (`hooks/hooks.json`): bom noi dung `sap-routing-discipline` vao dau
  moi phien (startup/clear/compact) qua `hookSpecificOutput.additionalContext`.

### Changed
- `skills/sap-scaffold-rap/SKILL.md`: Buoc 2-9 doi tu "sinh het roi activate 1 lan" sang sinh +
  activate + xac nhan tung layer theo thu tu dependency; Buoc 10 + Reference tro toi
  `sap-finish-ticket`/`sap-systematic-debugging`.
- `.claude-plugin/plugin.json`: Bump version v0.5.0 → v0.6.0.
- `README.md`: Cap nhat file-map + pipeline (them buoc 6) + highlights, them 4 skill moi vao
  cau truc.

### Fixed
- `hooks/hooks.json`: Hook `PostToolUse` (canh bao `SELECT *`) phu thuoc `jq` de doc
  `tool_input.file_path` tu stdin — xac nhan qua test that (`jq: command not found`, exit 127)
  la `jq` khong co tren PATH may nay, nen hook nay co kha nang **da im lang khong chay tu truoc
  gio**. Doi sang doc JSON bang `python` (dependency co san — toan bo `reference/mcp-server` da
  la Python package). Da test lai qua 4 case that (co/khong `SELECT *`, file khong phai `.abap`,
  payload thieu `tool_input`) — dung hanh vi mong doi ca 4.

---

## [v0.5.0] — 2026-07-11

### Added
- 🧠 **sap-daily-learner** — Hermes-like self-improving learning agent:
  - Agent definition (`agents/sap-daily-learner.md`)
  - Skill implementation (`skills/sap-daily-learner/SKILL.md`)
  - Reference module (`reference/modules/sap-daily-learner/SKILL.md`)
  - Auto-skill creation từ tương tác người dùng
  - Persistent memory qua `LEARNING_PROGRESS.md`
  - Progressive learning paths (Beginner → Intermediate → Expert)
- 🔀 **Routing Engine update**: Thêm Daily Learner vào keyword matrix (threshold ≥ 1)
- 🌐 **English translations**: ~80+ translation entries cho architecture, how-to-ask, daily learner sections
- 🏗️ **Architecture documentation**: Sơ đồ hệ thống + flow xử lý + file map
- 📚 **Hướng dẫn đặt câu hỏi**: Mẫu câu cho từng module, multi-module examples, skill usage guide
- 📝 **SKILL_TEMPLATE.md**: Template chuẩn cho skill, agent, reference module
- 🤝 **CONTRIBUTING.md**: Hướng dẫn đóng góp chi tiết (PR checklist, naming conventions, templates)

### Changed
- `skills/sap-ask-consultant/SKILL.md`: Cập nhật routing engine từ 19 → 20 agents
- `.claude-plugin/plugin.json`: Bump version v0.4.0 → v0.5.0
- `README.md`: Cập nhật danh sách agents + contributing links
- `index.html`: Thêm architecture docs + translations + daily learner section

---

## [v0.4.0] — 2026-07-11

### Added
- 🧠 **SAP Consultant System**: 18 module consultants + 1 researcher
  - `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-mm-consultant-cloud`
  - `sap-co-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-qm-consultant-cloud`
  - `sap-pm-consultant-cloud`, `sap-wm-consultant-cloud`, `sap-ps-consultant-cloud`
  - `sap-hcm-consultant-cloud`, `sap-bw-consultant-cloud`, `sap-basis-consultant-cloud`
  - `sap-tm-consultant-cloud`, `sap-tr-consultant-cloud`, `sap-ariba-consultant-cloud`
  - `sap-ca-consultant-cloud`, `sap-gts-consultant-cloud`, `sap-ehs-consultant-cloud`
  - `sap-docs-researcher` (CDS view & Docs Research)
- 🔀 **Auto-scoring Routing Engine**:
  - Keyword matrix (weight 3/2/1)
  - Module coupling (FI↔CO, PP→QM→MM...)
  - Explicit mention dispatch ("hoi SD")
  - Parallel dispatch
- 📚 **CDS Knowledge Base**: 7,355 released CDS views qua `cds-kb-mcp`
- 📖 **SAP Docs Research**: SAP Help, Community, API Hub, Fiori App Library qua `mcp-sap-docs`
- 🌐 **Bilingual support**: VI ↔ EN toggle trong index.html
- 🍪 **Cookie Auth + Web Popup Re-Auth**: SAP session cookies (`MYSAPSSO2`, `SAP_SESSIONID`)
- 🛡️ **Stampede Protection**: Chỉ 1 lần re-auth cho multiple 401 requests
- 🧹 **sap-clean-code** skill: ABAP Cloud naming conventions
- 🧩 **sap-extensibility** skill: Extensibility checklist
- 🛠️ **sap-key-user-toolkit** skill: Key User handbook
- ⚙️ **sap-btp-setup** skill: BTP connection manager
- 📄 `commands/sap-connect.md`: CLI command guide

### Changed
- `reference/mcp-server/`: MCP server Python với multi-profile support
- `index.html`: Thiết kế lại với sidebar, dark/light theme, copy buttons
- `.claude-plugin/plugin.json`: v0.3.0 → v0.4.0

---

## [v0.3.0] — 2026-07-10

> Version này là initial commit, toàn bộ dự án được tạo trong 1 commit.

### Added
- MCP server Python (`sap-btp-agent` CLI)
  - OAuth2 authentication (client_credentials, password, bearer)
  - Multi-profile support
  - Secret encryption (DPAPI Windows, AES-256-GCM macOS/Linux)
  - ABAP tools: `sap_search`, `sap_read_source`, `sap_syntax_check`, `sap_activate`
- Claude Code plugin structure
  - `.claude-plugin/plugin.json`
  - `hooks/hooks.json` (SELECT * warning)
  - `agents/`, `skills/`, `commands/`, `reference/` directories
- `abap-reviewer` agent
- `sap-clean-code` skill cơ bản
- `README.md` + `index.html` cơ bản
- Git ignore patterns

---

## [v0.8.0] — 2026-07-12

### Added
- 🆕 **SAP Fiori/UI5 Consultant** (`sap-fiori-consultant-cloud`) — Fiori Elements, Freestyle UI5,
  Adaptation Project, Launchpad (Business Role/Catalog/Group), SAP Build Work Zone.
- 🆕 **SAP CAP Consultant** (`sap-cap-consultant-cloud`) — Cloud Application Programming Model,
  side-by-side extension tren BTP, CDS (CAP) vs ABAP CDS, deployment (CF/Kyma), Fiori annotation.
- 🆕 **SAP CPI Consultant** (`sap-cpi-consultant-cloud`) — Cloud Platform Integration / Integration Suite,
  iFlow architecture, adapter config (OData/SOAP/SFTP/AMQP), mapping (XPath/Groovy), API Management.
- 🆕 **SAP SuccessFactors Consultant** (`sap-successfactors-consultant-cloud`) — Employee Central,
  Recruiting, Performance & Goals, Compensation, LMS, CPI integration with S/4HANA.
- 🆕 **SAP BTP Admin Consultant** (`sap-btp-admin-consultant-cloud`) — Cloud Foundry, Kyma, destinations,
  Cloud Connector, XSUAA/IAS security, CI/CD, service marketplace, MTA deployment.
- 📚 **Reference modules (CORE+DEEP 2-layer)** cho ca 5 agents: `sap-fiori-cloud`, `sap-cap-cloud`,
  `sap-cpi-cloud`, `sap-successfactors-cloud`, `sap-btp-admin-cloud`.
- 🔀 **Routing Engine update**: Them 5 agents moi vao keyword matrix + module coupling. Tong agent
  tu 22 → 27 (25 module consultants + 1 researcher + 1 daily learner).
- 📥 **Imported 11 skills from community repos**:
  - **Từ likweitan/abap-skills (8 skills)**: `sap-released-classes` (catalog ABAP Cloud classes),
    `sap-abap-sql` (ABAP SQL, AMDP, window functions), `sap-badi-enhancement` (Cloud BAdI),
    `sap-authorization` (DCL, RAP authorization, IAM), `sap-cloud-migration` (ECC→S/4HANA migration),
    `sap-odata-service` (RAP-based OData V4), `sap-rap-events` (RAP business events + Event Mesh),
    `sap-steampunk` (BTP ABAP Environment infrastructure).
  - **Từ secondsky/sap-skills (3 skills)**: `sap-btp-connectivity` (Cloud Connector, destination),
    `sap-btp-best-practices` (BTP development conventions, MTA, CI/CD),
    `sapui5-fiori` (SAPUI5, Fiori Elements, Fiori Tools).

### Changed
- `skills/sap-ask-consultant/SKILL.md`: Routing matrix mo rong them Fiori, CAP, CPI, SuccessFactors,
  BTP Admin keywords & coupling.
- Agents `sap-cap-consultant`, `sap-fiori-consultant`, `sap-cpi-consultant`, `sap-btp-admin-consultant`,
  `sap-daily-learner`: Da wire them skills moi vao YAML frontmatter.
- `.claude-plugin/plugin.json`: Bump version v0.7.0 → v0.8.0.

## [v0.8.1] — 2026-07-12

### Added
- 🔌 **MCP Server: mcp-sap-notes** (`skills/mcp-sap-notes`) — Tra cuu SAP Notes va KB articles truc
  tiep tu SAP Support Portal. 2 tools: `search` (keyword), `fetch` (full content + ABAP corrections).
- 🔌 **MCP Server: mcp-sap-gui** (`skills/mcp-sap-gui`) — SAP GUI Scripting automation cho Windows.
  57 tools: connection, navigation, field read/write, ALV/Grid/Tree tables, screenshots. Security:
  read-only mode, transaction whitelist/blocklist, audit logging.
- 🔌 **MCP Server: ADT MCP Integration** (`skills/mcp-sap-adt`) — 3 lua chon: SAP Official ADT MCP
  (VS Code, zero-config), ARC-1 (enterprise, 3000+ tests), mcp-abap-adt (community, de su dung).
  Tools: `abap_read_source`, `abap_search`, `abap_activate`, `abap_syntax_check`, `abap_atc_check`,
  `abap_transport_*`, `abap_unit_test`.
- 🧠 **Agent sap-docs-researcher updated**: Da wire them 6 MCP servers (cds-kb, mcp-sap-docs,
  mcp-sap-notes, mcp-sap-gui, ARC-1, mcp-abap-adt) vao mo ta agent.

### Changed
- `README.md`: Them 3 section huong dan cai dat cho 3 MCP servers moi (sap-notes, sap-gui, ADT).
- `agents/sap-docs-researcher.md`: Cap nhat danh sach 6 MCP servers, mo ta 6 toolsets day du.
- `.claude-plugin/plugin.json`: Bump version v0.8.0 → v0.8.1.

## [v0.8.2] — 2026-07-12

### Added
- 🔌 **MCP Server: mcp-sap-successfactors** (`skills/mcp-sap-successfactors`) — SAP SuccessFactors API
  connector. 2 options: sf-mcp (open-source, 62+ tools: employee info, RBP security, Time Off, Hiring,
  Position Management) + CData SF MCP (SQL-based read-only).
- 🔌 **MCP Server: mcp-sap-concur** (`skills/mcp-sap-concur`) — CData SAP Concur Travel &amp; Expense
  MCP Server. Query expense reports, travel requests, bookings, vendor data qua SQL.
- 🔌 **MCP Server: mcp-sap-fieldglass** (`skills/mcp-sap-fieldglass`) — CData SAP Fieldglass Services
  Procurement MCP Server. Query contingent workforce, SoW, timesheets, invoices qua SQL.
- 🧠 **Agent sap-docs-researcher updated**: Da wire them 3 MCP servers moi vao YAML frontmatter
  skills list + mo ta mo rong 9 MCP servers (tu 6).

### Changed
- `agents/sap-docs-researcher.md`: Them skills list, mo ta 9 MCP servers day du.
- `.claude-plugin/plugin.json`: Bump version v0.8.1 → v0.8.2.

## [Unreleased]

### Planned
- 🚀 **Thêm badges**: PRs welcome, GitHub stars
- 🚀 **Thêm agents còn thiếu**: SAP Concur, SAP Fieldglass
- 🚀 **Hoàn thiện reference modules**: Knowledge base cho 25 modules

### ✅ Đã hoàn thành gần đây
- ✅ **SECURITY.md**: Hướng dẫn báo cáo lỗi bảo mật
- ✅ **SECURITY.md badge**: Thêm Security Policy badge vào README.md header
- ✅ **Version badge (v0.5.0) + Python badge (3.10+)**: Thêm vào README.md header
- ✅ **CHANGELOG.md badge**: Thêm vào README.md header
- ✅ **Section Đóng góp trong index.html**: Thêm contributing section với bảng file (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SKILL_TEMPLATE)
- ✅ **Translations cho section Đóng góp**: 13 English translation entries cho sidebar, title, table headers, file descriptions
- ✅ **GitHub Issue templates**: Bug report + Feature request (`.github/ISSUE_TEMPLATE/`)
- ✅ **Background sync daemon**: `reference/scripts/sync_skills.py` + `install-task-scheduler.bat`
- ✅ **Open-source files**: `LICENSE` (MIT), `CODE_OF_CONDUCT.md`, `.github/PULL_REQUEST_TEMPLATE.md`
- ✅ **Skill sync command**: `commands/sync-skills.md` với hướng dẫn daemon background

---

## 📊 Version history

| Version | Date | Agents | Skills | Highlights |
|---------|------|--------|--------|------------|
| v0.5.0 | 2026-07-11 | 20 | 8 | Daily Learner, translations, open-source files |
| v0.4.0 | 2026-07-11 | 19 | 7 | Consultant System, routing engine, CDS KB, Docs |
| v0.3.0 | 2026-07-10 | 1 | 1 | Initial release, MCP server, basic structure |

---

*Changelog này được duy trì thủ công. Cập nhật khi có release mới.*
## [v0.6.2] - 2026-07-11

### Added
- 🧠 **sap-context-tool-result-trim** - ap dung ky thuat observation-masking (context-optimization)
  cho output MCP tool (cds-kb-mcp, sap-docs, sap-btp-agent). Pattern A (get_cds_view >30 field),
  B (search_cds 10+ items), C (batch ADT pull), D (ATC log 100+ dong). Rule: KHONG mask error
  trong debug loop; ghi full output vao `.sap-abap-agent/cache/<mcp>/<obj>_<hash>.{txt,json,log}`,
  chi paste compact summary + path vao context.
- 🧱 **sap-scaffold-context-summary** - quy tac compact giua cac layer scaffold (table -> I ->
  R -> behavior -> service binding). Snapshot full source ra `sessions/<ticket>/scaffold/`,
  chi paste summary + manifest vao context khi chuyen layer. Cho phep scaffold 3+ object
  cung ticket khong bi context phinh.
- 🧩 **sap-context-module-routing** - pattern 2-layer (CORE + DEEP) cho reference modules,
  giam ~60-70% token khi dispatch song song nhieu module consultant. Ap dung mau cho FI:
  `reference/modules/sap-fi-cloud/SKILL.md` (core, 2.4 KB) + `deep/SKILL.md` (full cu, 5.3 KB).
  17 module con lai tach theo lan, track trong LEARNING_PROGRESS.md.

### Changed
- `skills/sap-analyze-function-spec/SKILL.md`: Them Buoc 0 (mo session working memory),
  Buoc 1 sinh `summary.md` + chunked theo 8 section INTAKE trong
  `.sap-abap-agent/sessions/<ticket>/chunks/`. Ap dung ky thuat context-decomposition +
  observation masking - chi load summary, doc chunks theo nhu cau.
- `skills/sap-daily-learner/SKILL.md`: To chuc lai memory thanh 3 tier (theo memory-systems
  skill): EPISODIC (`memory/episodic/` - chat history, append-only) + SEMANTIC
  (`memory/semantic/` - LEARNING_PROGRESS + knowledge_graph.jsonl, default load) +
  PROCEDURAL (`memory/procedural/skills/` - alias sap-user-skills/). Cleanup rule cho
  episodic (>30 ngay archive).
- `skills/sap-routing-discipline/SKILL.md`: Them R6/R7/R8 + Tier 2 routing rules (4 muc):
  2-layer module routing, tool-result masking, working memory cho long session, memory
  tier routing. File nay van on dinh (khong timestamp, khong dynamic data) de giu KV-cache
  hit rate qua SessionStart hook.
- `reference/modules/sap-fi-cloud/`: Tach thanh 2 file (core 2.4 KB + deep 5.3 KB).
- `.claude-plugin/plugin.json`: Bump version v0.6.1 -> v0.6.2.

### Notes
- Pattern lay tu repo [muratcankoylan/agent-skills-for-context-engineering](https://github.com/muratcankoylan/agent-skills-for-context-engineering)
  (context-compression, filesystem-context, memory-systems, tool-design, context-optimization).
- Tong skill moi: 4 (sap-context-tool-result-trim, sap-scaffold-context-summary,
  sap-context-module-routing, + 0 net-new vi cac skill khac duoc update).
- Reference module FI da duoc mau 2-layer, 17 module con lai co the tach lan luot theo
  `sap-context-module-routing` skill.

---

