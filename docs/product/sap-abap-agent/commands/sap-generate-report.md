---
description: Sinh full code bao cao tu file dac ta (md/docx/xlsx), tu dong chon kien truc theo edition, hoi package - khong tu doan
argument-hint: "[duong dan file .md/.docx/.xlsx dac ta bao cao]"
---

# /sap-generate-report — Dac ta → Bao cao (full code, theo dung edition)

Lenh nay chay het 1 luot pipeline "dac ta → code" cho 1 **bao cao/report** (doc du lieu, khong
CRUD), noi cac skill co san lai voi nhau. KHONG tu doan bat ky thong tin nao lien quan he thong
that (edition, package, ten field) — luon hoi user neu chua ro.

## Cach dung

```text
/sap-generate-report examples/FS_bao-cao-ton-kho.docx
```

Neu khong truyen duong dan, hoi user file dac ta o dau (hoac mo ta bang loi neu chua co file).

## Quy trinh (Claude thuc hien tuan tu, dung lai hoi user o moi diem "BAT BUOC hoi")

1. **Convert dau vao** (neu la `.docx`/`.xlsx`): chay skill `sap-doc-to-md`.
2. **Sinh INTAKE.md**: chay skill `sap-analyze-function-spec`. Neu INTAKE muc 6 (cau hoi can lam
   ro) con muc CRITICAL chua tra loi → **BAT BUOC hoi user truoc khi di tiep**.
3. **Xac dinh edition** (neu chua biet trong phien nay): doc
   `reference/process/sap-service-type-context.md`. Neu khong xac dinh duoc tu config → **BAT
   BUOC hoi user**: "He thong dang lam viec la `s4hc_(public)` / `s4hc_(private)` / `btp` /
   `onprem`?"
4. **Sinh TECHNICAL_SPEC.md**: chay skill `sap-write-technical-spec` (hang "bao cao/list" trong
   bang chon pattern cua skill do se tro dung ve buoc 5).
5. **Xac nhan package + rao chan an toan**: chay skill `sap-deployment-target` — **BAT BUOC hoi
   user** package deploy tren he thong that, KHONG tu chon package mac dinh.
6. **Sinh code bao cao**: chay skill `sap-scaffold-report` — skill nay tu re nhanh:
   - Public Cloud/BTP → giao cho `sap-scaffold-cds` hoac `sap-scaffold-cds-analytics`.
   - Private Cloud/On-prem → sinh classical report OOP (`CL_SALV_TABLE`, khong PERFORM/FORM).
7. **Neu FS co yeu cau in PDF**: chay tiep skill `sap-scaffold-adobe-form` (sau khi da co data
   layer tu buoc 6) — **BAT BUOC hoi** ten form template `.xdp` da upload chua, KHONG tu bia.
8. **Review + Test**: chay `sap-atc-review` roi `sap-unit-test` (hoac `sap-cds-unit-test` neu
   nguon la CDS).
9. **Dong ticket**: chay `sap-finish-ticket`.

## Danh sach BAT BUOC hoi user (khong tu doan duoi moi hinh thuc)

- Edition he thong that (neu chua biet trong phien).
- Package deploy + xac nhan rao chan Z/Y.
- Field/entity nguon khi INTAKE con [Unverified] hoac chua chon dung phan he — dispatch qua
  `sap-ask-consultant`, khong tu chon agent tu van thu cong.
- Ten form template `.xdp` (neu co buoc 7) — neu chua co san, dung lai va huong dan user thiet
  ke bang Adobe LiveCycle Designer truoc, KHONG tu tao ten gia dinh.

## Luu y

- ⚠️ Tren `s4hc_(public)`, classical ALV report KHONG duoc released — luon la CDS + Fiori
  Elements List Report (skill `sap-scaffold-report` tu xu ly re nhanh nay, khong can nguoi dung
  tu biet truoc).
- 💡 Neu chi can 1 buoc rieng le (vd chi cai package, hoac da co TECHNICAL_SPEC.md roi) — goi
  truc tiep skill tuong ung thay vi chay het lenh nay tu dau.
- 🔗 Xem `docs/architecture.md` muc 2 (Quy trinh chinh) de biet toan bo pipeline va cac skill
  lien quan.
