---
name: sap-systematic-debugging
description: |
  Quy trinh debug co he thong cho loi runtime ABAP (dump, sai ket qua, activation fail) —
  tai hien truoc, 1 gia thuyet 1 lan, xac nhan bang cong cu (ST22/SAT/breakpoint) truoc khi sua,
  them regression test sau khi fix. Dung khi co bug/loi that, KHONG dung de review code tinh
  (dung sap-atc-review) hoac tu van nghiep vu (dung sap-ask-consultant).
when_to_use: |
  "sao chuc nang nay bi loi/dump", "debug ho action nay", "ket qua sai o buoc X",
  "activate bi fail khong ro tai sao".
argument-hint: "[mo ta loi] [duong dan object/log]"
model: sonnet
effort: medium
tools: [Read, Bash, Grep, Glob]
---

# SAP Systematic Debugging

## Khi nao dung

- ✅ Co loi/dump/ket qua sai that (khong phai review code tinh truoc khi chay).
- ✅ Da thu sua 1-2 lan ma khong het loi (dau hieu dang doan mo, can he thong lai).
- ❌ Review code chua chay (dung `sap-atc-review`).
- ❌ Cau hoi "nen thiet ke sao" (dung `sap-ask-consultant`/`sap-write-technical-spec`).

## Nguyen tac

**1 gia thuyet — xac nhan — roi moi sua.** Khong sua nhieu cho cung luc roi doan cho nao het
loi. Neu gia thuyet sai, quay lai buoc 2 voi gia thuyet khac — khong chong gia thuyet.

## Quy trinh

### Buoc 1: Tai hien loi

Ghi lai: input chinh xac, buoc chinh xac, ket qua mong doi vs ket qua that. Neu chua tai hien
duoc — dung tai day, xin them thong tin tu user (log, screenshot ST22, buoc lam).

### Buoc 2: Thu thap bang chung tho (truoc khi doan)

Theo loai loi:

| Trieu chung | Cong cu | Lay gi |
|---|---|---|
| Short dump (ABAP runtime error) | ST22 | Exception class, ABAP call stack, dong loi, gia tri bien luc dump |
| Sai ket qua / logic | Breakpoint (`/h` hoac external breakpoint trong ADT) | Gia tri bien tung buoc, re-check truoc khi ket luan |
| Cham / hang | SAT (ABAP Trace) | Method/statement ton nhieu thoi gian nhat, so lan goi DB |
| Activation fail | Log activate trong ADT (khong chi doc lai code) | Thong bao loi chinh xac + object/dong lien quan |
| RAP behavior loi runtime | Business Object Test Tool hoac Fiori Elements Preview + F12 network tab | HTTP response body (thuong co chi tiet hon UI hien) |

### Buoc 3: Dat 1 gia thuyet

Tu bang chung buoc 2, phat bieu ro: "Toi nghi loi la do X, vi bang chung Y cho thay Z." Khong
dat nhieu gia thuyet cung luc.

### Buoc 4: Xac nhan gia thuyet TRUOC khi sua

Kiem tra gia thuyet bang cach re-check bang chung (vd doc lai dong code X, hoac dat breakpoint
dung cho do) — KHONG sua code roi chay thu de "xem co het loi khong" (do la doan, khong phai
xac nhan). Gia thuyet sai -> quay lai buoc 3.

### Buoc 5: Sua toi thieu

Sua dung phan gay loi (theo gia thuyet da xac nhan), khong sua lan sang cho khac "cho chac".

### Buoc 6: Xac nhan het loi — chay that

Tai hien lai chinh xac buoc o Buoc 1, xac nhan ket qua dung mong doi. Ap dung skill
`sap-verification-before-completion`: phai la ket qua chay that.

### Buoc 7: Regression test

Them test case (skill `sap-unit-test`) cover dung case vua fix, de bug khong quay lai am tham.

## Vien co thuong gap

| # | Vien co | Phai lam |
|---|---|---|
| D1 | "Sua dai roi chay thu xem het loi chua" | Dat gia thuyet ro truoc, xac nhan roi moi sua (Buoc 3-4) |
| D2 | "Dump/log dai qua, doan dai la du" | Doc dung dong loi + call stack that trong ST22/SAT |
| D3 | "Sua xong khong dump nua la xong" | Phai tai hien dung case ban dau de xac nhan, khong chi "khong thay loi nua" |
| D4 | "Bug nho, khong can regression test" | Van them test — bug tung xay ra co the xay ra lai |
| D5 | "Sua luon nhieu cho nghi co the sai" | 1 gia thuyet 1 lan; sua nhieu cho cung luc se khong biet cho nao thuc su fix |

## Reference

- Skill `sap-verification-before-completion` — nguyen tac xac nhan bang chay that.
- Skill `sap-unit-test` — sinh regression test sau khi fix.
- Skill `sap-atc-review` — review code tinh (khac voi debug runtime).
