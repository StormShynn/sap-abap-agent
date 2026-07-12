---
name: sap-doc-to-md
description: |
  Convert file Word (.docx) hoac Excel (.xlsx/.xls) sang Markdown (.md), de lam ngu canh
  cho AI doc hieu tai lieu nghiep vu (Functional Spec, Business Process, test script,
  bang tinh du lieu...) va ho tro sinh code/xu ly logic ABAP.
  Dung khi user dua duong dan 1 file .docx/.xlsx/.xls (hoac ca thu muc chua nhieu file)
  va can convert sang .md, hoac hoi cach chuyen doi tai lieu Word/Excel thanh Markdown.
  Ban don gian: dung cong cu `markitdown` da cai san cho .docx (KHONG giu anh minh hoa/
  screenshot - chi con text + bang), va script "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py" cho
  .xlsx/.xls (bat buoc, vi markitdown lam sai dinh dang ma so SAP nhu Material/Order).
  KHONG dung cho file .pdf/.pptx (chua duoc test voi skill nay).
when_to_use: |
  "convert file FS.docx sang markdown", "chuyen doi file Word/Excel nay sang md",
  "doc file .docx nay giup toi".
argument-hint: "[duong dan file hoac thu muc .docx/.xlsx can convert]"
model: haiku
effort: low
tools: [Bash, Read, Glob, Edit]
---

# SAP Doc to Markdown — Convert Word/Excel sang .md

## Khi nao dung

- ✅ User dua file .docx/.xlsx/.xls (FS, BP, test script, bang tinh nghiep vu...) can convert sang .md.
- ✅ User hoi "lam sao convert Word/Excel sang Markdown".
- ❌ File .pdf/.pptx (chua test voi skill nay — markitdown ho tro nhung can kiem tra rieng).
- ❌ Tai lieu ma phan noi dung chinh nam trong anh chup man hinh (vd toan bo section chi co screenshot, khong co bang/text mo ta kem theo) — skill nay se lam mat phan do, phai bao truoc cho user.

## Yeu cau moi truong

Kiem tra da co `markitdown` chua truoc khi dung (dung cho `.docx`):

```bash
markitdown --help
```

Neu chua co: `pip install "markitdown[all]"`.

File `.xlsx`/`.xls` dung `"${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"`, can `mammoth`, `markdownify`,
`pandas`, `openpyxl` (`xlrd` neu co file `.xls`) — cai bang `pip install mammoth markdownify pandas openpyxl xlrd`.

## Quy trinh xu ly

### Buoc 1: Xac dinh input/output

- **`in/`/`out/` KHONG nam trong git repo** — day la thu muc local per-user duoi
  `%USERPROFILE%\.sap-btp-agent\` (Windows) / `~/.sap-btp-agent/` (macOS/Linux), **cung noi** luu
  profile/secrets ket noi SAP BTP (xem skill `sap-btp-setup`). Ly do: tai lieu FS/output sinh ra
  thuong la du lieu nghiep vu/khach hang thuc, khong nen nam chung voi source code plugin (dung
  se dan toi rui ro commit nham len repo public). Co the doi qua bien moi truong
  `SAP_BTP_AGENT_HOME`.
- Lay dung duong dan da resolve (tranh doan/hardcode sai) bang:
  ```bash
  python -c "from sap_btp_agent.config.paths import get_in_dir, get_out_dir; print(get_in_dir()); print(get_out_dir())"
  ```
  `"${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"` da tu dong dung 2 ham nay lam default — chi can goi script
  khong tham so la doc/ghi dung cho vao `in/`/`out/` local, khong can tu tinh duong dan.
- Input: duong dan file cu the user dua, hoac 1 thu muc (mac dinh: `in/` local o tren).
- Output: mac dinh thu muc `out/` local o tren, giu nguyen ten file goc, chi doi duoi thanh `.md`.
  Neu user chi dinh thu muc khac thi dung theo yeu cau.
- Neu input la thu muc: dung Glob tool tim file `*.docx`, `*.xlsx`, `*.xls` trong do, bo qua file lock tam cua Office (ten bat dau bang `~$`).

### Buoc 2: Convert — chon dung tool theo dinh dang

- **`.docx`** → dung `markitdown` CLI (don gian, du dung cho text + bang; anh se khong render duoc, xem Buoc 3). `markitdown` khong tu biet duong dan local (khac `office_to_md.py`), nen phai truyen full path lay tu Buoc 1:
  ```bash
  IN_DIR=$(python -c "from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())")
  OUT_DIR=$(python -c "from sap_btp_agent.config.paths import get_out_dir; print(get_out_dir())")
  markitdown "$IN_DIR/ten-file.docx" -o "$OUT_DIR/ten-file.md"
  ```
- **`.xlsx` / `.xls`** → **KHONG dung `markitdown` CLI truc tiep.** Da kiem chung: markitdown doc
  Excel qua pandas voi kieu du lieu tu suy dien, lam **mat so 0 dung dau va doi dinh dang so**
  (vd ma Material SAP dang so `000000001234567890` bi rut gon sai thanh `1234567890`, o trong
  hien chu thua `NaN` thay vi de trong). Dung script co san (da fix bang `dtype=str`) — khong
  tham so se tu dong doc/ghi dung `in/`/`out/` local:
  ```bash
  python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"
  ```

Voi nhieu file: goi khong tham so nhu tren se tu convert het file trong `in/`; hoac lap lai lenh
cho tung file cu the neu chi muon convert 1 vai file.

### Buoc 3: Kiem tra output truoc khi bao cao cho user

Dung Read doc lai file `.md` vua tao va kiem tra:

1. **Bang bieu / heading con nguyen** — doi chieu so luong dong bang (`grep -c '^|'`) co hop ly khong, khong bi cat cut giua chung.
2. **Anh nhung trong file Word van con dong `![](data:image/...;base64...)` nhung KHONG render duoc** (markitdown cat bo phan du lieu that, chi giu placeholder rong — data URI bi cat cut co chu `...` o cuoi). Neu thay 1 section co nhieu dong `![](data:image...)` lien tiep ma khong co bang/text mo ta di kem ngay sau — nghia la section do da mat het ngu canh (chi la anh, khong co chu), phai canh bao ro cho user (vd: "phan 'Man hinh chuc nang' chi co anh, khong render duoc khi convert — can xem file goc de biet giao dien that su").
3. **Voi file Excel** (da qua `office_to_md.py` nen ve nguyen tac da an toan) — doi chieu nhanh vai ma nghiep vu quan trong (Material, Order, Plant...) trong .md so voi file goc de chac chan khong bi doi dinh dang so.

### Buoc 4: Bao cao ket qua

Neu file .docx co gia tri nghiep vu quan trong nam trong screenshot (phat hien o Buoc 3.2), hoi user co muon giu lai anh khong — neu co, dung `python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"` (khong tham so se tu dung `in/`/`out/` local; script nay tach anh that ra thu muc `<ten-file>_assets/` thay vi luoc bo) thay cho markitdown CLI don gian o Buoc 2.

## Vi du

### Input
```text
User: convert file FS moi vua dat vao thu muc in/ sang md
```

### Output
```text
$ python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"
Dang convert: <path_local>/in/ten-file-FS.docx
  -> <path_local>/out/ten-file-FS.md (642 dong, 340 dong bang du lieu)
Luu y: section "Man hinh chuc nang" chi con vai dong `![](data:image/x-emf;base64...)`
khong render duoc (anh bi cat bo) — neu can xem giao dien that, mo file .docx goc hoac
yeu cau dung "${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py" (giu anh) thay vi markitdown CLI don gian.
```

## Luu y

- ⚠️ **File Excel: TUYET DOI khong dung `markitdown` CLI truc tiep.** Da kiem chung bang test
  thuc te: markitdown/pandas tu suy dien kieu du lieu, lam mat so 0 dung dau va doi dinh dang
  so (vd `000000001234567890` -> `1234567890`, `1000` -> `1000.0`) — sai lech du lieu nghiep vu
  SAP (Material, Plant, Order deu la ma dang so co the co so 0 dung dau). Luon dung
  `"${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"` cho `.xlsx`/`.xls`.
- ⚠️ Ban `.docx` don gian (qua `markitdown`) khong giu anh minh hoa — neu can giu anh (vd
  screenshot Fiori quan trong cho nghiep vu), dung `"${CLAUDE_PLUGIN_ROOT}/reference/scripts/office_to_md.py"` thay the
  (dung mammoth + markdownify, trich xuat anh that ra `_assets/`, xem chi tiet trong docstring
  cua script).
- 💡 markitdown con ho tro `.pdf`, `.pptx`, `.csv`, `.html`, `.msg`... neu can mo rong dung cho loai file khac (chua kiem chung trong skill nay).
- 🔗 Neu file la **Function Spec** va muc tieu la sinh code ABAP: buoc tiep theo la skill
  `sap-analyze-function-spec` (FS.md -> INTAKE.md), roi `sap-write-technical-spec` ->
  `sap-scaffold-rap`/`sap-scaffold-cds` -> `sap-atc-review` -> `sap-unit-test`. Xem pipeline day du
  trong README.md.
- 🔗 Voi tai lieu khac (khong phai FS de sinh code): ket hop voi agent SAP consultant tuong ung (vd
  `sap-pp-consultant-cloud`, `sap-mm-consultant-cloud`...) de doc va tu van tu noi dung tai lieu.

Task: {{ARGUMENTS}}
