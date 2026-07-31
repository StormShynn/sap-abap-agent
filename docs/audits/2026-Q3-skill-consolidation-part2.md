# Skill Consolidation — Part 2 (2026-07-31)

> Tiep noi `2026-Q3-skill-rationalization.md` (14/07/2026). Audit do thuc hien 2 viec ma audit
> truoc de xuat nhung chua thuc thi (hop nhat BTP, tiep tuc dua skill setup-1-lan sang
> `reference/mcp-guides/`), cong them rieng biet 4 skill moi da them SAU audit truoc ma
> chua qua ra soat lan nao (`sap-multi-system-context`, `sap-service-type-context`,
> `sap-security-review`, `sap-package-backup`).

## Scope

Yeu cau ban dau: rà soát toàn bộ 45 skill trong `skills/` (cảm giác "quá nhiều"), xác định
tập "chính" nên giữ auto-discover toàn cục, phần còn lại chuyển sang cơ chế đã có sẵn
(`reference/modules/`, `reference/mcp-guides/`, `reference/process/`) để vẫn dùng được khi
skill/agent khác gọi tới bằng tên, không cần xoá năng lực nào.

Thực thi Phase 1 (rủi ro thấp, đã xác nhận với người dùng trước khi sửa) — xem
`docs/plans/completed/skill-consolidation-2026-07-31.md` cho chi tiết plan/risk/validation.
Phase 2 (gộp nhóm "technical knowledge" — `sap-abap-sql`/`sap-authorization`/`sap-rap-events`/
`sap-released-classes`/`sap-badi-enhancement`/`sap-key-user-toolkit`/`sap-odata-service`) —
**chưa thực thi**, chỉ nghiên cứu và đề xuất, chờ quyết định riêng.

## Ket qua dat duoc

`skills/` giam tu **45 xuong 38** (khong tinh placeholder `sap-user-skills`).

| Skill (cu) | Vi tri moi | Loai thay doi |
|---|---|---|
| `sap-multi-system-context` | `reference/process/sap-multi-system-context.md` | Di chuyen nguyen ven, bo YAML frontmatter |
| `sap-service-type-context` | `reference/process/sap-service-type-context.md` | Di chuyen nguyen ven, bo YAML frontmatter |
| `mcp-sap-notes` | `reference/mcp-guides/mcp-sap-notes.md` | Di chuyen nguyen ven |
| `mcp-sap-concur` | `reference/mcp-guides/mcp-sap-concur.md` | Di chuyen nguyen ven (da san co pointer sang `mcp-sap-cdata-setup.md`) |
| `mcp-sap-fieldglass` | `reference/mcp-guides/mcp-sap-fieldglass.md` | Di chuyen nguyen ven |
| `sap-btp-connectivity` | `reference/modules/sap-btp-connectivity/SKILL.md` | **Hop nhat** vao knowledge note co san cung ten (xem Phat hien #1) |
| `sap-btp-best-practices` | `reference/modules/sap-btp-admin-cloud/deep/SKILL.md` | **Hop nhat**, phan trung security/CI-CD gop lai thay vi lap |

## Phat hien moi (audit 14/07 chua co, hoac tu bao cao chua dung thuc te)

1. **Xung dot ten 3 chieu voi `sap-btp-connectivity`, audit truoc khong phat hien**: truoc
   khi sua, ton tai DONG THOI `skills/sap-btp-connectivity/SKILL.md` (skill instruction, se bi
   xoa) VA `reference/modules/sap-btp-connectivity/SKILL.md` (knowledge note, tu nhan trong
   chinh no la "Khong thay the skill sap-btp-connectivity" — noi dung khac nhau nhung TRUNG
   ten). 8 file `reference/modules/*-integration/SKILL.md` khac (HCM, GTS, CA, Fiori role, BW,
   PS, TR, WM-EWM) da tro ve knowledge note nay o muc "BTP architecture" tu truoc — vi giu
   nguyen ten/vi tri knowledge note lam noi hop nhat, ca 8 file nay KHONG can sua gi.
2. **Audit 14/07 tu bao cao "da hop nhat Destination pattern giua sap-btp-best-practices/
   sap-btp-connectivity" nhung xac minh truc tiep cho thay chua hop nhat that** — chi co 1
   doan o `sap-btp-best-practices` §6 tro sang `sap-btp-connectivity` thay vi lap lai JSON,
   ca 2 skill van con day du, doc lap. Da hop nhat that trong dot nay.
3. **`tests/test_skill_multi_system_context.py` hard-code duong dan `skills/
   sap-multi-system-context`** va assert cac field frontmatter kieu skill (`tools`,
   `argument-hint`, `effort`, `model: sonnet`) — di chuyen file doi hoi viet lai test, khong
   chi doi duong dan. Da viet lai, giu nguyen cac assertion noi dung (routingHints, 5 edition,
   3 backend, TTL 7 ngay), bo cac assertion frontmatter khong con ap dung, them 1 assertion
   moi xac nhan `sap-ask-consultant` tro dung ve vi tri moi.
4. **Bug co san (khong lien quan truc tiep phan nay) trong `reference/scripts/
   mcp_inventory.json`**: entry `sap-fieldglass` co field `doc` tro sai
   `skills/sap-fieldglass/SKILL.md` (thu muc that la `skills/mcp-sap-fieldglass/`, co tien to
   `mcp-`). Da sua tien the trong luc cap nhat duong dan cho di chuyen nay.
5. **`validate_plugin.py::skill_exists()` da duoc cap nhat tu truoc** (khong con la TODO nhu
   audit 14/07 ghi) — da biet ca 4 duong dan (`skills/`, `reference/modules/`,
   `reference/mcp-guides/`, `reference/process/`) truoc khi dot nay bat dau. Xac nhan bang
   cach chay `validate_plugin.py` truoc khi sua (PASS, 1 warning version-drift co san khong
   lien quan) roi doi chieu source `skill_exists()` truc tiep.
6. **`CLAUDE.md` ghi so skill la "43"** trong khi thuc te (truoc dot nay) la 45 — lech do 2
   skill moi nhat them vao ma chua cap nhat file nay. Da sua thanh 38 (con so that sau dot
   nay), khong con lech.

## Nguyen tac ap dung khi hop nhat/di chuyen

- **Khong xoa nang luc** — chi doi tu "auto-discover qua tu khoa" sang "doc khi duoc tro toi
  bang ten", giong het pattern da chung minh cua audit 14/07 (`mcp-sap-adt`/`mcp-sap-gui`/
  `mcp-sap-successfactors`, `sap-context-module-routing`/`sap-context-tool-result-trim`/
  `sap-scaffold-context-summary`).
- **Neu ten van con ton tai o noi khac** (vd `sap-btp-connectivity` qua `reference/modules/`),
  KHONG can sua frontmatter `skills:` cua agent dang khai bao no — `skill_exists()` van
  resolve dung. Chi sua frontmatter khi ten thuc su bien mat hoan toan (vd `sap-btp-best-
  practices`, gop vao 1 file KHAC ten).
- **Doc toan bo noi dung ca 2 file truoc khi hop nhat**, khong tom tat/doan — hop nhat BTP
  doi hoi doc day du 3 file nguon (2 skill + 1 knowledge note co san) de tranh mat thong tin
  hoac lap lai.

## Follow-up con lai (chua lam)

### Nhom "technical knowledge" — da nghien cuu, DE XUAT GIU NGUYEN (khong hop nhat)

Da doc toan bo noi dung 7 skill (`sap-abap-sql` 157 dong, `sap-authorization` 173 dong,
`sap-rap-events` 167 dong, `sap-released-classes` 150 dong, `sap-odata-service` 162 dong,
`sap-badi-enhancement` 138 dong, `sap-key-user-toolkit` 188 dong) va dem so agent khai bao
tung ten qua `grep` truc tiep tren `agents/*.md` (khong suy doan). Ket luan: **khong nen hop
nhat**, vi 3 ly do co bang chung cu the:

1. **Khong trung lap noi dung that** (khac hoan toan truong hop BTP vua sua o tren) — 6 skill
   dau (tru `sap-key-user-toolkit`) moi skill 1 chu de ky thuat rieng biet (SQL/AMDP, DCL/IAM,
   RAP event, danh muc class released, OData V2/V4, Cloud BAdI) khong lap noi dung voi nhau,
   hau nhu khong tham chieu cheo (chi 1 cap `sap-badi-enhancement` <-> `sap-key-user-toolkit`
   da duoc audit 14/07 xu ly xong, cross-reference thay vi lap lai).
2. **`sap-released-classes` va `sap-key-user-toolkit` khac SHAPE voi 5 skill con lai**:
   `sap-released-classes` la bang tra cuu thuan tuy (giong `sap-cds-kb` — mot skill catalog da
   duoc giu rieng co chu dich), khong phai huong dan "cach lam". `sap-key-user-toolkit` phuc
   vu **khac doi tuong hoan toan** — key user/functional consultant KHONG can ABAP — trong khi
   6 skill con lai deu danh cho developer. Gop chung se la loi phan loai sai doi tuong doc.
3. **Blast radius qua lon so voi loi ich**: dem qua grep, **24/25 agent `sap-*-consultant-
   cloud.md`** khai bao **6/7 ten nay** (tru `sap-key-user-toolkit` — khong agent developer
   nao khai bao no, dung nhu ky vong vi khac doi tuong) trong frontmatter `skills:`. Hop nhat
   se doi sua frontmatter ca 24-25 file chi de doi ten tham chieu, cho 1 loi ich chi la giam
   con so top-level tu 38 xuong ~33 — khong giam duoc tong luong kien thuc agent phai biet
   (van la tung do noi dung, chi doi cho luu). Ngoai ra, gop nhieu chu de vao 1
   `description`/`when_to_use` de dung chung 1 ngan sach 1.536 ky tu (xem `SKILL_TEMPLATE.md`
   dong 46) se lam moi trigger phrase kem chinh xac hon so voi hien tai (moi skill co
   `when_to_use` rieng, sat dung 1 chu de) — co nguy co lam GIAM chat luong auto-discover thay
   vi cai thien, di nguoc lai chinh muc tieu ban dau.

**Khong hanh dong** — giu nguyen ca 7 skill nay o `skills/`. Neu sau nay muon giam tiep, huong
kha thi hon la ap dung pattern noi bo cua chinh `sap-clean-code` (tach `reference/` NOI BO
trong thu muc cua no) cho TUNG skill rieng le (giam do dai file, khong giam SO LUONG skill),
chu khong phai gop nhieu skill lai.
- **Mau CData MCP chung** (`mcp-sap-cdata-setup.md`) da ton tai va da duoc `mcp-sap-concur`/
  `mcp-sap-fieldglass`/`mcp-sap-successfactors` dung — khong con follow-up nao o day.
- **`reference/modules/sap-fi-cloud/deep/SKILL.md` chua duoc lam giau** (audit 14/07, muc
  10) — ngoai pham vi dot nay, van con nguyen trang.
- **5 module thieu cross-reference `sap-extensibility`/`sap-clean-code`** (audit 14/07, muc
  9: `sap-bw-cloud`, `sap-basis-cloud`, `sap-tm-cloud`, `sap-tr-cloud`, `sap-ca-cloud`) —
  ngoai pham vi dot nay, van con nguyen trang.
