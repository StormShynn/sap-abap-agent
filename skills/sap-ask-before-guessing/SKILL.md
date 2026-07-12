---
name: sap-ask-before-guessing
description: |
  Nguyen tac: khi thieu thong tin quan trong de lam dung (package deploy, CDS/object nguon, quy
  uoc rieng cua du an, pattern kien truc, gia tri field khong co trong FS...), PHAI hoi lai user
  thay vi tu doan/chon phuong an "nghe hop ly". Duoc bom tu dong vao dau moi phien qua SessionStart
  hook (hooks/hooks.json) - khong can goi thu cong.
when_to_use: |
  Tu dong ap dung dau moi phien khi lam viec voi scaffold/deploy code ABAP. Doc lai khi ban dinh
  "chon dai" 1 gia tri/CDS view/package/pattern ma khong chac chan 100%.
model: haiku
effort: low
---

# SAP Ask Before Guessing

## Quy tac

Trong pipeline scaffold/deploy ABAP Cloud (tu FS.docx den transport/abapGit push), khi gap 1
diem quyet dinh **anh huong thuc te len he thong** (tao/sua/xoa object, chon CDS/API nguon, chon
package, chon pattern kien truc, dien gia tri field khong co trong FS...) ma thong tin hien co
**khong du de chac chan**, PHAI dung lai va hoi user — KHONG tu chon phuong an "nghe hop ly nhat"
roi lam luon. Ly do: sai o day nghia la object/table/CDS da tao that tren he thong, sua lai ton
kem hon nhieu so voi hoi truoc 1 cau.

Nguyen tac nay **hep hon** "Auto Mode" mac dinh cua Claude Code (uu tien tu quyet dinh, han che
hoi) — CHI ap dung cho hanh dong co that anh huong len he thong SAP (tao/sua/xoa object that,
chon sai se ton kem sua), KHONG ap dung cho cau hoi thong thuong/tim hieu/doc code (van tra loi
truc tiep binh thuong nhu Auto Mode mac dinh).

## Vien co thuong gap

| # | Vien co | Phai lam |
|---|---|---|
| A1 | "FS khong ghi ro field nay, nhung doan duoc kieu du lieu hop ly" | Ghi vao INTAKE muc 6 (can lam ro) + hoi user, KHONG tu dien gia tri |
| A2 | "Co 2 CDS view co ve deu hop, chon dai 1 cai" | Hoi consultant (`sap-ask-consultant`) hoac hoi user, KHONG tu chon |
| A3 | "Chua ro deploy package nao nhung cu tao o package test tam" | Dung `sap-deployment-target`, hoi truoc khi tao bat ky object nao |
| A4 | "User khong noi ro managed hay unmanaged, nhung managed pho bien hon" | Ap decision tree `sap-write-technical-spec`; neu van khong ro, hoi thang |
| A5 | "Object nay co ve thuoc Z/Y that nhung ten nam ngoai quy uoc" | DUNG - hoi lai truoc khi tao/sua/xoa, xem `sap-deployment-target`/`sap-clean-code` |
| A6 | "User da noi ro huong xu ly cu the (vd 'cu tao di, khong can hoi')" | Uu tien instruction ro rang cua user hon quy tac nay |

## Khac biet voi cac skill lien quan (tranh trung lap)

- `sap-routing-discipline` (vien co R4) — pham vi hep: khi score routing module duoi threshold
  thi hoi, khong tu suy dien module nao. Skill nay TONG QUAT hon: ap dung cho MOI diem quyet dinh
  trong pipeline scaffold/deploy, khong chi routing module.
- `sap-verification-before-completion` — noi ve **bang chung SAU khi lam xong** (da chay that
  chua). Skill nay noi ve **quyet dinh TRUOC khi lam** (co du thong tin de lam dung khong).
- `sap-deployment-target` — ap dung cu the nguyen tac nay cho 2 tinh huong: chon package deploy +
  gate cac buoc can thao tac thu cong.

## Ngoai le - khong can hoi

- Tac vu **khong anh huong that len he thong** (doc code, giai thich, tra cuu tai lieu, viet nhap
  TECHNICAL_SPEC.md ban nhap chua chot) — van lam truc tiep, khong can hoi tung buoc nho.
- User da noi ro huong xu ly ("neu khong ro thi cu chon X mac dinh", "khong can hoi lai nua cho
  ticket nay") — instruction ro rang cua user luon uu tien hon quy tac nay.

## Tich hop

- `hooks/hooks.json` (SessionStart) — bom noi dung file nay vao dau phien, dung chung co che voi
  `sap-routing-discipline` (2 hook command doc lap, cung matcher `startup|clear|compact`).
- Skill `sap-deployment-target`, `sap-ask-consultant`, `sap-write-technical-spec` — noi ap dung
  cu the nguyen tac nay trong pipeline.
