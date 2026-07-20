---
name: sap-security-review
description: |
  Quet bao mat cho code ABAP Cloud (SQL/CDS injection, thieu authorization check, hardcode
  credential, RFC/destination khong auth chuan, log lo du lieu nhay cam, XSS trong custom UI5,
  method public thua, thieu validate input tren OData/API). Thiet ke "zero-noise" (chi bao cao
  finding du tin cay, moi finding kem kich ban khai thac cu the) - khong phai skill "cach lam dung"
  (dung sap-authorization cho viec do).
  Bo sung cho agent `abap-reviewer` (goi tu do, khong tu dung rieng le nhu 1 diem vao).
when_to_use: |
  "review bao mat code nay", "co lo hong SQL injection khong", "kiem tra security cho ABAP nay",
  "co thieu authorization check khong".
argument-hint: "[duong dan file/class/CDS view]"
model: sonnet
effort: medium
tools: [Read, Grep, Glob, WebFetch, WebSearch]
disallowedTools: [Write, Edit]
---

# SAP Security Review — Quet bao mat ABAP Cloud

## Khi nao dung

- ✅ Duoc goi tu `abap-reviewer` nhu 1 buoc trong quy trinh review toan dien (mac dinh).
- ✅ User hoi rieng ve bao mat 1 doan code/class/CDS view cu the.
- ❌ KHONG dung de hoc "cach lam auth cho dung" — dung skill `sap-authorization` (skill nay chi
  PHAT HIEN thieu sot, khong day cach sua chi tiet, tranh trung noi dung).
- ❌ KHONG thay the `reference/scripts/security_scan.py` — cai do quet ma nguon CUA CHINH PLUGIN
  nay (Python/TS/JS), con skill nay quet code ABAP CUA KHACH HANG.

## Trieu hoc nguyen: vi sao can rieng 1 skill

`abap-reviewer` truoc day chi kiem tra naming (`sap-clean-code`) + kien truc/extensibility
(`sap-extensibility`) + dung dan chuc nang chung chung — KHONG co khung bao mat co he thong
(OWASP-style). `sap-atc-review`/`check_released_api.py` chi cam vai statement (`AUTHORITY-CHECK`,
`SELECT *`) vi ly do Cloud-release, khong phai vi ly do bao mat duoc phan tich rieng. Day la
khoang trong that, khong trung voi bat ky skill nao da co (da xac nhan qua grep toan repo truoc
khi tao skill nay).

## Checklist (cu the cho ABAP Cloud, khong chung chung)

| # | Nguy co | Dau hieu trong code | Vi du kich ban khai thac |
|---|---------|---------------------|--------------------------|
| S1 | SQL/CDS injection | Dynamic WHERE qua string concat trong Open SQL (`WHERE (lv_dynamic)`); CDS `WHERE` nhan tham so khong qua dung cu phap CDS parameter (`:param`) | Attacker (hoac user noi bo ac y) truyen input vao field bi ghep chuoi truc tiep vao cau SQL -> doc/sua du lieu ngoai pham vi duoc phep |
| S2 | Thieu authorization check | RAP behavior (`get_instance_authorizations`) khong co, hoac DCL thieu dieu kien loc dung | User co the CRUD instance ma ho khong duoc phep truy cap qua API/Fiori app |
| S3 | Hardcode credential/secret | Literal password/API key/client secret trong constant hoac string ABAP | Bat ky ai doc duoc source (abapGit, transport) deu lay duoc credential that |
| S4 | RFC/destination khong auth chuan | Goi RFC/HTTP destination khong qua co che auth (basic/OAuth) da cau hinh, hoac dung destination scope qua rong | Lo credential he thong dich, hoac cho phep goi tiep cac he thong khac ngoai pham vi can |
| S5 | Log/message lo du lieu nhay cam | `MESSAGE`/application log ghi full gia tri field chua PII/tai chinh | Nguoi co quyen xem log (khong nhat thiet quyen xem du lieu goc) doc duoc thong tin nhay cam |
| S6 | XSS trong custom UI5 | Input user render thang vao DOM khong qua encode (`innerHTML`, binding khong sanitize) | Attacker chen script qua field input, chay khi nguoi khac xem trang |
| S7 | Method PUBLIC thua | Method noi bo khong can thiet duoc khai bao PUBLIC | Mo rong be mat goi duoc tu ben ngoai class khong can thiet |
| S8 | Thieu validate input OData/API | Parameter service khong kiem tra do dai/dinh dang/range truoc khi xu ly | DoS qua request qua lon, hoac logic loi khi nhan gia tri ngoai du kien |

## Thiet ke "zero-noise" (bat buoc cho moi finding)

1. **Nhan muc do**: dung DUNG 1 trong 6 nhan co san cua `abap-reviewer` (Blocking/Important/Nit/
   Suggestion/Learning/Praise) — KHONG bay them he nhan rieng cho security, giu nhat quan toan
   plugin. SQL injection/thieu auth check -> Blocking. Log lo du lieu nhe/method public thua ->
   Important hoac Nit tuy muc do nghiem trong thuc te.
2. **Kich ban khai thac cu the**: moi finding phai tra loi duoc "attacker/nguoi dung noi bo co the
   lam gi, bang cach nao" — khong ghi chung chung "co the khong an toan".
3. **Chi bao cao khi du tin cay**: neu khong chac chan day co phai loi that hay khong (vd 1 cau
   Open SQL nhin giong dynamic nhung thuc ra dung tham so binding an toan), **KHONG bao cao nhu
   Blocking/Important** — ha xuong Suggestion kem ghi chu "can xac nhan them", hoac bo qua neu ro
   rang la false positive (xem danh sach duoi).
4. **Danh sach KHONG phai loi** (tranh false positive quen thuoc):
   - CDS view co `WHERE` clause dung dung cu phap CDS parameter (`:param`) — AN TOAN, khong phai
     injection du nhin co ve dong (khac voi string concat truc tiep).
   - RAP behavior dung `AUTHORITY-CHECK` qua DCL published dung cach — day la co che chuan, khong
     phai lo hong.
   - Method PUBLIC nhung co doc ro la released API danh cho consumer ben ngoai (co muc dich ro
     rang, khac voi "thua khong ly do").

## Quy trinh

1. Doc toan bo code lien quan (khong doan tu ten bien/method — cung nguyen tac voi `abap-reviewer`).
2. Doi chieu tung muc S1-S8 trong checklist.
3. Voi tung nghi van, kiem tra co nam trong danh sach "KHONG phai loi" khong truoc khi ket luan.
4. Neu nghi van lien quan authorization (S2) — sau khi flag xong, **tro nguoi dung sang skill
   `sap-authorization`** de biet cach sua dung (khong tu day chi tiet cach implement o day).
5. Tong hop theo dung Output_Format cua `abap-reviewer` (dung chung 1 report, khong tach rieng).

## Output (hoa vao report chung cua abap-reviewer)

Khong co format rieng — moi finding cua skill nay la 1 dong trong dung 6 muc cua
`agents/abap-reviewer.md` (Blocking/Important/Nit/Suggestion/Learning/Praise), chi khac o **noi
dung** (luon kem kich ban khai thac) so voi finding ve naming/extensibility.

## Checklist truoc khi tra loi

- Da doi chieu du 8 muc S1-S8 chua, hay moi kiem tra 1-2 muc quen thuoc?
- Moi finding co kich ban khai thac cu the chua, hay chi noi chung chung "khong an toan"?
- Da loai tru dung danh sach "khong phai loi" truoc khi ket luan Blocking/Important chua?
- Neu lien quan authorization, da tro sang skill `sap-authorization` de huong dan cach sua chua?
- Neu khong chac chan, da ha nhan xuong Suggestion + ghi ro "can xac nhan them" thay vi khang dinh
  nhu that chua?

## Reference

- `sap-authorization` — cach implement DCL/instance-based auth dung (skill nay chi phat hien
  thieu, khong day cach lam).
- `sap-clean-code`, `sap-extensibility` — 2 tang review khac da co san trong `abap-reviewer`.
- `sap-atc-review` — checklist tu dong hoa (naming/released-API/clean-ABAP), khac tang voi review
  bao mat chu quan o day.
- `reference/scripts/security_scan.py` — quet ma nguon Python/TS/JS cua CHINH PLUGIN nay (khac
  hoan toan pham vi skill nay, la code ABAP cua khach hang).
