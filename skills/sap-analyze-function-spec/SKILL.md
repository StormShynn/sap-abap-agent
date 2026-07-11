---
name: sap-analyze-function-spec
description: |
  Phan tich Function Spec (file .docx cua khach hang) va sinh INTAKE.md chuan hoa —
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

# SAP Analyze Function Spec — FS.docx → INTAKE.md

## Khi nao dung

- ✅ User dua file `.docx` Function Spec (FS) tu khach hang va noi "phan tich FS nay", "tao INTAKE tu file X".
- ✅ Bat ky khi nao nhan 1 FS moi truoc khi lam bat ky buoc code-gen nao.
- ❌ Khong dung khi da co INTAKE.md roi (di thang sang `sap-write-technical-spec`).
- ❌ Khong tu sinh code ABAP o buoc nay.

## Quy trinh

### Buoc 1: Convert FS sang Markdown

Dung skill `sap-doc-to-md` (hoac truc tiep `reference/scripts/office_to_md.py`) de convert file
`.docx` sang `.md` truoc — tan dung bang bieu/heading da duoc parse san, khong can parse XML tay:

```bash
python reference/scripts/office_to_md.py
```

`in/`/`out/` **khong nam trong repo** — la thu muc local per-user (xem skill `sap-doc-to-md` de
biet duong dan day du va cach lay dung duong dan da resolve). Doc lai file `.md` vua tao trong
`out/` thay vi doc `.docx` truc tiep.

### Buoc 2: Phan loai noi dung vao 8 section INTAKE

Doc noi dung `.md`, phan loai vao cau truc INTAKE.md chuan (xem mau ben duoi). Cac tieu de FS
thuong gap va mapping tuong ung:

| Tieu de thuong gap trong FS | Section INTAKE |
|---|---|
| "Thong tin tai lieu" | 1 |
| "Quan ly thay doi" | 2 |
| "Pham vi tai lieu" | 3.1 |
| "Thuat ngu" | 3.2 |
| "Muc dich" | 4.1 |
| "Cac qui dinh chung" | 4.2 |
| "Man hinh chuc nang / Mau bao cao" | 5.1 |
| "Mo ta tham so" | 5.2 |
| "Man hinh trung gian" | 5.3 |
| "Mo ta cac truong" | 5.4 |
| "Tieu chi sap xep" | 5.5 |
| "Yeu cau khac" | 5.6 |
| (phat hien khi doc) | 6 — Cau hoi can lam ro |
| "Tai lieu tham khao" | 7 |

### Buoc 3: Nhan dien phan he & danh dau nguon du lieu

- Tu keyword nghiep vu, xac dinh phan he SAP lien quan (FI/MM/SD/CO/PP/PM/QM/WM...).
- Voi tung field/section 5.4, ghi "Nguon (App.Field)" theo dung text FS da co (vd `[App] Manage Sales
  Order.Field`). Neu FS khong ghi nguon ro rang -> ghi "N/A - can xac nhan KH", KHONG tu doan.
- Neu can tim CDS view/API chuan cho phan he do -> dung agent consultant tuong ung (vd
  `sap-mm-consultant-cloud` cho phan he MM) hoac `sap-docs-researcher` de tra cuu, o BUOC SAU
  (`sap-write-technical-spec`), khong lam o buoc nay.

### Buoc 4: Phat hien inconsistency & danh dau ambiguous

- So sanh section 5.2 (tham so) voi 5.3 (man hinh trung gian) — co khop khong.
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

Output mac dinh: `out/<ten-ticket>/INTAKE.md` (tao thu muc neu chua co). Bao user: "Da tao INTAKE.md
tai `<path>`. Vui long review muc 6 (cau hoi can lam ro) truoc khi tiep tuc."

## Template INTAKE.md

```markdown
# INTAKE — <Ten du an/ticket> / <Ten chuc nang> / v<phien ban>

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

1. **Khong bia field** neu FS khong noi ro — ghi vao section 6.
2. **Giu nguyen text goc** trong glossary, muc dich, yeu cau khac.
3. **Moi field phai co "Nguon"** — day la input quan trong nhat cho buoc sau tim CDS/API.
4. **Muc rui ro phai co ly do** — 1 cau giai thich.

## Luu y

- ⚠️ Neu file FS co nhieu anh chup man hinh la noi dung chinh (khong co bang mo ta di kem) — bao
  user phan do co the mat ngu canh khi convert (xem `sap-doc-to-md`).
- 🔗 Sau khi co INTAKE.md, buoc tiep theo la skill `sap-write-technical-spec`.
