---
name: sap-finish-ticket
description: |
  Checklist dong ticket sau khi scaffold + review + test xong: activate het object khong loi,
  sap-atc-review PASS, ABAP Unit test xanh het, transport san sang release, abapGit push.
  Buoc 6 (cuoi) trong pipeline "FS -> INTAKE -> TECHNICAL_SPEC -> scaffold -> review -> test -> finish".
  Dung sau khi co ATC_REVIEW.md (PASS) va test class da chay.
  KHONG dung neu ATC_REVIEW.md con FAIL hoac chua chay unit test.
when_to_use: |
  "dong ticket X", "checklist truoc khi release transport", "san sang push abapGit chua",
  "tong ket lai ticket nay lam xong chua".
argument-hint: "[ten ticket] [duong dan out/<ticket>/]"
model: sonnet
effort: medium
tools: [Read, Bash, Glob, Grep, Write]
---

# SAP Finish Ticket — Checklist dong ticket

## Khi nao dung

- ✅ Da co `ATC_REVIEW.md` (buoc 4) va test class da sinh (buoc 5).
- ✅ Truoc khi bao user "ticket xong", truoc khi release transport / push abapGit.
- ❌ `ATC_REVIEW.md` con FAIL — quay lai sua, chua duoc dong ticket.
- ❌ Chua chay `sap-unit-test` — chay truoc.

## Nguyen tac

Ap dung skill `sap-verification-before-completion`: moi muc duoi day can **bang chung chay
that**, khong phai "code nhin on la xong".

## Quy trinh

### Buoc 1: Doc lai out/<ticket>/

Lay: `TECHNICAL_SPEC.md` (danh sach object phai co), `ATC_REVIEW.md` (ket qua PASS/FAIL),
danh sach test class da sinh.

### Buoc 2: Activation check (bang chung that)

Voi tung object trong danh sach TECHNICAL_SPEC — xac nhan da activate trong ADT khong loi:
table -> CDS interface (I) -> CDS reuse/consumption (R/C) -> behavior definition -> behavior
implementation -> service definition/binding. Thu tu nay quan trong vi object sau phu thuoc
object truoc (xem skill `sap-scaffold-rap` muc checkpoint). Neu chua activate het — DUNG, bao
user object nao con loi.

### Buoc 3: Re-check ATC_REVIEW.md

Neu co FAIL trong report — DUNG, khong duoc qua buoc 4. Neu chi WARN — ghi chu lai, tiep tuc.

### Buoc 3b: Xac dinh review nao thuc su can (smart routing)

Khong phai ticket nao cung can du 3 tang review cua `abap-reviewer` (naming/extensibility/bao mat)
o cung 1 muc do — tuy loai object da scaffold:

| Loai object | Naming/Extensibility | Bao mat (`sap-security-review`) |
|---|---|---|
| CDS view read-only (khong RAP behavior) | Bat buoc | Nhe — chi can S1 (injection qua parameter) |
| RAP behavior CO create/update/delete action | Bat buoc | Bat buoc day du S1-S8, dac biet S2 (authorization) |
| Class/method thuan logic (khong truy cap DB truc tiep) | Bat buoc | Tap trung S3 (hardcode credential), S7 (method public) |

Neu bo qua 1 muc nao do, **ghi ro ly do trong `FINISH_CHECKLIST.md`** (vd "khong co RAP behavior
nen bo qua kiem tra authorization chi tiet") — khong duoc im lang bo qua ma khong ghi chu, tranh
nham lan sau nay "quen kiem tra" voi "co chu dinh bo qua vi khong lien quan".

### Buoc 4: Unit test — chay that, khong doan

Yeu cau ket qua that tu ABAP Unit runner (Eclipse ADT `Ctrl+Shift+F10` hoac CI pipeline) cho
tung test class. Bat ky test nao FAIL/khong chay duoc -> DUNG.

### Buoc 5: Transport check

- Transport request dung **package da xac nhan voi user o skill `sap-deployment-target`** (doi
  chieu voi muc "Package deploy" trong TECHNICAL_SPEC.md) — KHONG phai package tu doan hoac package
  chuan SAP. Neu TECHNICAL_SPEC.md chua co muc nay (ticket cu truoc khi co skill nay) — dung lai,
  hoi user xac nhan package truoc khi release transport.
- Dung mo ta (ticket ID trong text).
- Khong lan object khong lien quan ticket nay (kiem tra object list trong transport khop voi
  TECHNICAL_SPEC.md).
- Neu co ADR (`docs/decisions/`) cho quyet dinh kien truc — da tao chua.

### Buoc 6: abapGit push readiness

- `abapgit.xml`/`package.devc.xml` khop cau truc that.
- Khong commit file `in/`/`out/` (du lieu khach hang/local, xem skill `sap-doc-to-md`).

### Buoc 7: Ghi bao cao

Output `out/<ticket>/FINISH_CHECKLIST.md`:

```markdown
# Finish Checklist — <ticket>

**Ngay**: <YYYY-MM-DD>
**Ket qua**: READY / NOT READY

| Muc | Trang thai | Bang chung |
|---|---|---|
| Activation (tat ca object) | ✅/❌ | <cach xac nhan: ADT screenshot/log> |
| ATC Review | ✅/❌ | out/<ticket>/ATC_REVIEW.md |
| Unit test | ✅/❌ | <so test PASS/FAIL that> |
| Transport | ✅/❌ | <so transport, object list> |
| abapGit | ✅/❌ | |

## Con thieu (neu NOT READY)
-
```

Neu **NOT READY**: liet ke ro con thieu gi, khong dong ticket.

## Vien co thuong gap

| # | Vien co | Phai lam |
|---|---|---|
| F1 | "ATC WARN thi chac khong sao" | WARN duoc phep tiep tuc nhung phai ghi vao report, khong lo qua |
| F2 | "Test da sinh la coi nhu pass" | Phai chay that, dan ket qua that |
| F3 | "Activate duoc 1 object dau la cac object sau cung on" | Check tung object, loi activation thuong o object sau (behavior/service) |
| F4 | "Transport co object la du, khong can check thua" | Object thua/thieu so voi TECHNICAL_SPEC deu la loi |

## Reference

- Buoc truoc: `sap-atc-review` (buoc 4), `sap-unit-test` (buoc 5).
- Skill `sap-verification-before-completion` — nguyen tac bang chung chay that ap dung xuyen suot.
- Skill `sap-scaffold-rap` — thu tu dependency activation.
- Skill `sap-deployment-target` — noi package deploy duoc xac nhan voi user (Buoc 5 doi chieu lai
  quyet dinh nay, khong tu doan package moi).
