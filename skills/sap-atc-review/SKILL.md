---
name: sap-atc-review
description: |
  Review code ABAP da scaffold theo checklist: naming Z*, released API, clean ABAP, test coverage.
  Output bao cao PASS/FAIL/WARN kem file:line. Dung sau khi scaffold xong (sap-scaffold-rap/cds),
  truoc khi commit/push abapGit.
  Bo sung cho agent abap-reviewer (agent do la persona-based review sau/method cu the; skill nay
  la pass kiem tra co script tu dong + checklist may moc truoc do).
when_to_use: |
  "review code ABAP vua scaffold", "chay ATC check", "kiem tra naming truoc khi commit",
  "co pass duoc released API check khong".
argument-hint: "[duong dan src/] [--skip=lint,released]"
model: sonnet
effort: medium
tools: [Bash, Read, Glob, Grep]
---

# SAP ATC Review — Naming + Released API + Clean ABAP checklist

## Khi nao dung

- ✅ Sau khi scaffold xong (`sap-scaffold-rap`/`sap-scaffold-cds`).
- ✅ Truoc khi commit/push len abapGit.
- 🔗 Dung cung agent `abap-reviewer` cho phan review sau/logic nghiep vu — skill nay tap trung vao
  cac check co the tu dong hoa (naming, released API, clean ABAP, test coverage).

## Output

Report dang markdown, ghi vao `out/<ticket>/ATC_REVIEW.md` (`out/` la thu muc local per-user,
KHONG nam trong repo — xem skill `sap-doc-to-md` de biet duong dan day du):

```markdown
# ATC Review — <ticket>

**Ngay**: <YYYY-MM-DD>
**Ket qua**: PASS / FAIL

## Summary
- ✅ PASS: 25
- ⚠ WARN: 3
- ❌ FAIL: 2

## Chi tiet
### ❌ Naming
- `src/zrap/zc_object.bdef.asbdef` — line 1: prefix Z* thieu underscore.
```

## Quy trinh

### Buoc 1: Naming lint (tu dong)

```bash
python reference/scripts/sap_naming_lint.py out/<ticket>/src/
```

Check theo skill `sap-clean-code`: table `ZTB*` (≤16 ky tu), interface view `ZI*`, reuse view
`ZR*`, consumption view `ZC*`, behavior implementation `ZBP*`, service `ZUI*`/`ZAPI*`, class
`ZCL_*`, function module `ZF_*` (≤30 ky tu, tru table/message class co gioi han rieng).

### Buoc 2: Released API check (tu dong)

```bash
python reference/scripts/check_released_api.py out/<ticket>/src/
```

Check: khong dung `CL_GUI*` (tru class released), khong co `CALL TRANSACTION`/`CALL DIALOG`,
khong co `AUTHORITY-CHECK` (dung CDS DCL thay the), khong co `SELECT *` / `SELECT...ENDSELECT`.

### Buoc 3: Clean ABAP check

- Khong co `SELECT *`.
- Khong co magic value (string so sanh truc tiep khong qua constant).
- Ten bien co y nghia (khong phai `lv_x`, `lt_tab` — xem skill `sap-clean-code`).
- Moi method co header comment ro rang muc dich.

### Buoc 4: Test coverage check

- Moi behavior co class test.
- Moi method public co it nhat 1 test case (`sap-unit-test`).
- Test class prefix `ltc_*` (LOCAL FRIENDS).

### Buoc 5: Anti-rationalization review (kiem "cat goc")

Bat loi phan doan/cat goc ma script tu dong khong thay duoc. Nhung "vien co" hay gap nhat, cot
"phai lam" la yeu cau thuc te:

| # | Vien co | Phai lam |
|---|---|---|
| R1 | "Chac released roi, khoi verify" | Verify qua `sap-docs-researcher` hoac View Browser ADT; chua chac -> `[Unverified]` |
| R2 | "Khong thay view thi bia gan dung" | Ghi vao INTAKE muc 6 "can lam ro", KHONG bia ten view/field |
| R3 | "Bo test / test sau" | Moi behavior/method BAT BUOC co ABAP Unit test |
| R4 | "Sua nhanh trong code chuan/core cua he thong (neu co repo read-only)" | Read-only tuyet doi — reference/copy ra ngoai, khong sua tai cho |
| R5 | "Gen lai toan bo cho nhanh" | Sua incremental, giu lai fix da co tu truoc |
| R6 | "Dung object on-prem quen thuoc (BAPI/transaction cu)" | Phai la released object cho ABAP Cloud — verify, khong doan |
| R7 | "Object chua released thi bo qua/bia" | Tim nguon released thay the (CDS/API chuan khac), hoac de xuat Key User Extensibility, KHONG dead-end |

Ghi vi pham vao report muc "🚩 Anti-rationalization" (file:line + ma R).

### Buoc 6: Hanh dong

Neu co FAIL: dung, yeu cau user fix. Neu chi WARN: bao user, khong block.

## Reference

- Scripts: `reference/scripts/sap_naming_lint.py`, `reference/scripts/check_released_api.py`.
- Naming: skill `sap-clean-code`. Extensibility: skill `sap-extensibility`.
- Agent `abap-reviewer` — review sau/logic nghiep vu chi tiet hon.
