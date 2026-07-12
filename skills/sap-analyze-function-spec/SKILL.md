---
name: sap-analyze-function-spec
description: |
  Phan tich Function Spec (file .docx cua khach hang) va sinh INTAKE.md chuan hoa -
  buoc 1 trong pipeline "FS -> INTAKE -> TECHNICAL_SPEC -> scaffold code -> review -> test".
  Dung khi user dua file .docx Function Spec (FS) SAP va can chuan hoa yeu cau thanh
  1 file de lam viec tiep (tim CDS nguon, viet Technical Spec, sinh code ABAP).
  KHONG dung de sinh code truc tiep - chi chuan hoa yeu cau. Sau buoc nay la
  skill sap-write-technical-spec.
when_to_use: |
  "phan tich FS nay", "tao INTAKE tu file X.docx", "chuan hoa function spec nay lai",
  "doc file FS va tom tat yeu cau".
argument-hint: "[duong dan file FS .docx, hoac ten ticket]"
model: sonnet
effort: medium
tools: [Bash, Read, Write, Glob, Grep]
---

# SAP Analyze Function Spec - FS.docx -> INTAKE.md

## Khi nao dung

- ✅ User dua file `.docx` Function Spec (FS) tu khach hang va noi "phan tich FS nay", "tao INTAKE tu file X".
- ✅ Bat ky khi nao nhan 1 FS moi truoc khi lam bat ky buoc code-gen nao.
- ❌ Khong dung khi da co INTAKE.md roi (di thang sang `sap-write-technical-spec`).
- ❌ Khong tu sinh code ABAP o buoc nay.

## Quy trinh

### Buoc 0: Mo session working memory (MOI, truoc khi convert)

FS lon (30+ trang, nhieu bang) khong the do full vao context 1 lan - context se phinh
(killed co hon 50K token), dan den mat attention o cac phan quan trong. Ap dung pattern
**filesystem-context** (xem skill `sap-context-tool-result-trim`):

```
Session dir: <agent-home>/sessions/<ticket>/
├── fs_full.md         # Toan bo FS convert sang markdown
├── chunks/            # 8 file, moi file la 1 section INTAKE
│   ├── 01_thong_tin_tai_lieu.md
│   ├── 02_quan_ly_thay_doi.md
│   ├── 03_pham_vi_thuat_ngu.md
│   ├── 04_mo_ta_chung.md
│   ├── 05_yeu_cau_nghiep_vu.md
│   ├── 06_edge_cases_questions.md
│   ├── 07_tai_lieu_tham_khao.md
│   └── 08_ghi_chu_agent.md
├── summary.md         # Tom tat toan bo FS (1-2 trang)
└── intake.md          # Output cuoi - INTAKE chinh
```

`<agent-home>` KHONG phai project dang mo (plugin cai va dung tren bat ky project SAP nao) - la
1 thu muc co dinh theo may, mac dinh `%USERPROFILE%\.sap-abap-agent\` (Windows) /
`~/.sap-abap-agent/` (macOS/Linux), override qua `SAP_ABAP_AGENT_HOME`. Session dir =
`<agent-home>/sessions/<ticket>`, resolve bang:
```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" sessions/<ticket>
```
Moi lenh Bash co the la 1 shell moi (shell state KHONG persist giua cac lan goi Bash) - lenh o
Buoc 1 duoi day tu resolve lai trong CUNG 1 block, KHONG dua vao bien tu block nay.

Neu user chi dinh ticket tu prompt (vd "ticket PROJECT_2024_Q1") -> dung ticket do; neu khong
-> tao ticket tu ten file FS (vd FS_KH01.docx -> ticket KH01).

### Buoc 1: Convert FS sang Markdown + luu vao session

Dung skill `sap-doc-to-md` (hoac truc tiep `reference/scripts/office_to_md.py`) de convert file
`.docx` sang `.md`. Hai output can tao:

**1a. Full text vao session**
```
Ghi: <session-dir>/fs_full.md
```

**1b. Summary vao session + context**
Chi doc `fs_full.md` qua tat ca section heading de sinh `summary.md`. Quick scan:
- Title + subtitle (de xac dinh ticket, version)
- Dem so heading H1 / H2 / H3
- Dem so table
- Dem so trang (tinh tu page break neu co)
- Trich 1-2 dong tu moi H1 lam one-liner
- Liet ke cac bang lon (>= 5 cot hoac >= 20 dong) - vi day la noi rat hay mat context

Ghi `summary.md` (1-2 trang) vao session. Trong CONTEXT hien tai, chi load `summary.md` -
KHONG load `fs_full.md`. Day la ky thuat **observation masking** ap dung cho FS.

**1c. Chunk theo 8 section INTAKE**
Ap dung pattern **context-decomposition**:
- Doc `fs_full.md` theo heading, cat thanh 8 file trong `chunks/` (mapping xem Buoc 2).
- Moi chunk chi load khi can (default KHONG load len context chi moi summary).
- Trong `summary.md`, ghi "Chi tiet section X: xem `chunks/0X_<ten>.md`".

Lenh mau (1 block duy nhat - cac bien chi dam bao ton tai trong cung 1 lan goi Bash nay):
```bash
SESSION_DIR="$(python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/agent_home.py" sessions/<ticket>)"
IN_DIR="$(python -c "from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())")"
# Tu office_to_md.py sinh markdown -> $IN_DIR/fs_full.md
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"
# Copy vao session
mkdir -p "$SESSION_DIR"
cp "$IN_DIR/fs_full.md" "$SESSION_DIR/fs_full.md"
```

### Buoc 2: Phan loai noi dung vao 8 section INTAKE (tu summary + chunks)

Doc summary + load chunks tu `chunks/` theo nhu cau. Phan loai vao cau truc INTAKE.md chuan
(xem mau ben duoi). Cac tieu de FS thuong gap va mapping tuong ung:

| Tieu de thuong gap trong FS | Section INTAKE | Chunk file tuong ung |
|---|---|---|
| "Thong tin tai lieu" | 1 | `01_thong_tin_tai_lieu.md` |
| "Quan ly thay doi" | 2 | `02_quan_ly_thay_doi.md` |
| "Pham vi tai lieu" | 3.1 | `03_pham_vi_thuat_ngu.md` |
| "Thuat ngu" | 3.2 | `03_pham_vi_thuat_ngu.md` |
| "Muc dich" | 4.1 | `04_mo_ta_chung.md` |
| "Cac qui dinh chung" | 4.2 | `04_mo_ta_chung.md` |
| "Man hinh chuc nang / Mau bao cao" | 5.1 | `05_yeu_cau_nghiep_vu.md` |
| "Mo ta tham so" | 5.2 | `05_yeu_cau_nghiep_vu.md` |
| "Man hinh trung gian" | 5.3 | `05_yeu_cau_nghiep_vu.md` |
| "Mo ta cac truong" | 5.4 | `05_yeu_cau_nghiep_vu.md` |
| "Tieu chi sap xep" | 5.5 | `05_yeu_cau_nghiep_vu.md` |
| "Yeu cau khac" | 5.6 | `05_yeu_cau_nghiep_vu.md` |
| (phat hien khi doc) | 6 - Cau hoi can lam ro | `06_edge_cases_questions.md` |
| "Tai lieu tham khao" | 7 | `07_tai_lieu_tham_khao.md` |

QUY TAC TAI SUC: section 5 (Yeu cau nghiep vu chi tiet) thuong chiem 50-70% tong FS. KHONG
load full section 5 vao context 1 lan - dung `chunks/05_yeu_cau_nghiep_vu.md` lam reference, doc
theo bang can thiet (5.1, 5.2, ...).

### Buoc 3: Nhan dien phan he & danh dau nguon du lieu

- Tu keyword nghiep vu, xac dinh phan he SAP lien quan (FI/MM/SD/CO/PP/PM/QM/WM...).
- Voi tung field/section 5.4, ghi "Nguon (App.Field)" theo dung text FS da co (vd `[App] Manage Sales
  Order.Field`). Neu FS khong ghi nguon ro rang -> ghi "N/A - can xac nhan KH", KHONG tu doan.
- Neu can tim CDS view/API chuan cho phan he do -> dung agent consultant tuong ung (vd
  `sap-mm-consultant-cloud` cho phan he MM) hoac `sap-docs-researcher` de tra cuu, o BUOC SAU
  (`sap-write-technical-spec`), khong lam o buoc nay.

### Buoc 4: Phat hien inconsistency & danh dau ambiguous

- So sanh section 5.2 (tham so) voi 5.3 (man hinh trung gian) - co khop khong.
- Field khong co "Nguon" -> ghi vao section 6.
- Logic phuc tap (goi API ngoai, sequence dac biet, tich hop he thong khac) -> ghi vao section 6.

### Buoc 5: Danh gia muc rui ro

| Muc | Dac diem |
|---|---|
| **Tiny** | 1 CDS view don gian, 1 method, khong save |
| **Normal** | 1 RAP business object day du, Fiori Elements, vai method, draft |
| **High-risk** | Unmanaged, custom save, tich hop module/he thong khac |

Ghi 1 cau ly do tai sao chon muc do.

### Buoc 6: Ghi file INTAKE.md

Output: ghi `<session-dir>/intake.md` (VA copy ra `out/<ticket>/INTAKE.md` neu can tinh nhat
quan voi pipeline cu). Bao user: "Da tao INTAKE.md tai `<path>`. Vui long review muc 6 (cau hoi
can lam ro) truoc khi tiep tuc."

### Buoc 7: Cleanup session

- `fs_full.md` chi giu trong session local, KHONG commit len repo public (bi mat noi dung FS).
- Ghi vao `LEARNING_PROGRESS.md` (skill `sap-daily-learner`): so chunk da tao, co hay khong
  summary bi thieu so voi full.
- Sau khi pipeline xong (INTAKE -> TECHNICAL_SPEC -> scaffold -> review -> test), co the
  cleanup `fs_full.md` de tiet kiem disk (giai doan sau chi can `intake.md`).

## Template INTAKE.md

```markdown
# INTAKE - <Ten du an/ticket> / <Ten chuc nang> / v<phien ban>

## 1. Thong tin tai lieu
- Ten du an / ticket: ...
- Phan he: ...
- Ten chuc nang: ...
- Nguoi thiet ke: ...
- Muc do uu tien: Cao / Trung binh / Thap
- Phien ban FS: ...
- Ngay cap nhat FS: ...
- Muc rui ro harness: Tiny / Normal / High-risk

## 2. Quan ly thay doi (tu FS)
| Ngay | Muc thay doi | Mo ta | T/S/X | Phien ban |
|---|---|---|---|---|

## 3. Pham vi & thuat ngu
### 3.1 Pham vi tai lieu
### 3.2 Thuat ngu (glossary)
| STT | Thuat ngu | Dinh nghia |
|---|---|---|

## 4. Mo ta chung
### 4.1 Muc dich
### 4.2 Quy dinh chung

## 5. Yeu cau nghiep vu chi tiet
### 5.1 Man hinh chuc nang / mau bao cao
### 5.2 Tham so dau vao
| STT | Tham so | Mo ta | Loai | Gia tri mac dinh | Bat buoc |
|---|---|---|---|---|---|
### 5.3 Man hinh trung gian (neu co)
### 5.4 Mo ta cac truong
| Ma | Ten | Mo ta | Nguon (App.Field) | Dinh dang |
|---|---|---|---|---|
### 5.5 Tieu chi sap xep
### 5.6 Yeu cau khac

## 6. Edge case & cau hoi can lam ro voi KH
-

## 7. Tai lieu tham khao
- FS goc: <duong dan>

## 8. Ghi chu agent
- <field/logic nao ambiguous, assumption nao da chon>
```

## Quy tac quan trong

1. **Khong bia field** neu FS khong noi ro - ghi vao section 6.
2. **Giu nguyen text goc** trong glossary, muc dich, yeu cau khac.
3. **Moi field phai co "Nguon"** - day la input quan trong nhat cho buoc sau tim CDS/API.
4. **Muc rui ro phai co ly do** - 1 cau giai thich.
5. **KHONG load full FS vao context** - chi load `summary.md`, doc chunks theo nhu cau
   (ky thuat observation masking + context decomposition).
6. **KHONG commit `fs_full.md` len repo** - luu trong session local, cleanup sau pipeline.

## Luu y

- ⚠️ Neu file FS co nhieu anh chup man hinh la noi dung chinh (khong co bang mo ta di kem) - bao
  user phan do co the mat ngu canh khi convert (xem `sap-doc-to-md`).
- 🔗 Sau khi co INTAKE.md, buoc tiep theo la skill `sap-write-technical-spec`.