---
description: Chay het pipeline dac ta -> code cho BAT KY loai object nao (RAP/CDS/report/Adobe Form/class thuong) - sap-write-technical-spec tu chon dung pattern, khong can nho command rieng cho tung loai
argument-hint: "[duong dan file .md/.docx/.xlsx dac ta] hoac [tiep tuc <ten-ticket>]"
---

# /sap-new-object — Dac ta → Code (tu chon dung pattern, moi loai object)

Lenh **tong quat** cho toan bo Codegen Pipeline — khong gioi han 1 loai object nhu
`/sap-generate-report` hay `/sap-generate-adobe-form`. `sap-write-technical-spec` tu doc
dac ta va **quyet dinh pattern nao phu hop** (xem "Bang chon pattern nhanh" cua skill do):
RAP Managed/Unmanaged, CDS 3-layer, CDS Analytics, Report (CDS+Fiori hoac classical ALV theo
edition), Adobe Form (in PDF), hoac ABAP class thuong. Dung lenh nay khi chua chac chan
truoc pattern nao se ap dung, hoac muon 1 diem vao duy nhat cho moi loai ticket.

## Cach dung

```text
/sap-new-object examples/FS_quan-ly-hop-dong-thue.docx
```

Neu da lam do dang truoc do (co san `INTAKE.md`/`TECHNICAL_SPEC.md`), goi:

```text
/sap-new-object tiep tuc ZCTR01
```

Claude se doc lai `out/ZCTR01/` de biet da xong buoc nao, tiep tuc tu do thay vi lam lai tu dau.

## Quy trinh (Claude thuc hien tuan tu, dung lai hoi user o moi diem "BAT BUOC hoi")

1. **Convert dau vao** (neu la `.docx`/`.xlsx`): chay skill `sap-doc-to-md`.
2. **Sinh INTAKE.md**: chay skill `sap-analyze-function-spec`. Neu INTAKE muc 6 (cau hoi can
   lam ro) con muc CRITICAL chua tra loi → **BAT BUOC hoi user truoc khi di tiep**.
3. **Xac dinh edition** (neu chua biet trong phien nay): doc
   `reference/process/sap-service-type-context.md`. Khong xac dinh duoc tu config → **BAT BUOC
   hoi user**: "He thong dang lam viec la `s4hc_(public)` / `s4hc_(private)` / `btp` /
   `onprem`?"
4. **Sinh TECHNICAL_SPEC.md**: chay skill `sap-write-technical-spec` — day la buoc **quyet dinh
   pattern**, ap dung dung "Bang chon pattern nhanh" cua chinh skill do:

   | Nhu cau (tu FS) | Pattern | Skill scaffold |
   |---|---|---|
   | Bao cao/list, doc du lieu | CDS+Fiori (cloud) hoac classical ALV OOP (on-prem) | `sap-scaffold-report` |
   | In PDF (invoice, phieu xuat kho...) | Class goi Adobe Document Services | `sap-scaffold-adobe-form` |
   | List/Detail don gian, khong save | 3-layer CDS + Service Definition | `sap-scaffold-cds` |
   | Cube/Dimension/KPI dashboard | CDS Analytics | `sap-scaffold-cds-analytics` |
   | Form CRUD co ban | RAP Managed + Fiori Elements | `sap-scaffold-rap` |
   | Form CRUD save theo sequence custom | RAP Unmanaged (**bat buoc co ADR**) | `sap-scaffold-rap --unmanaged` |
   | Khong can OData, chi logic noi bo | ABAP class thuong | `reference/templates/abap-class/` |

   **KHONG tu chon pattern truoc khi doc xong FS** — de `sap-write-technical-spec` chay het
   decision tree cua no (bao gom Buoc 3/4 xac nhan 2 chieu qua `sap-ask-consultant`), roi moi
   biet dung cot nao trong bang tren.
5. **Xac nhan package + rao chan an toan**: chay skill `sap-deployment-target` — **BAT BUOC hoi
   user** package deploy tren he thong that.
6. **Bootstrap quy uoc thuc te** (lan dau tren he thong moi): chay skill
   `sap-bootstrap-system-context`.
7. **Sinh code**: chay dung skill scaffold theo cot cuoi bang o Buoc 4.
8. **Review + Test**: chay `sap-atc-review` roi `sap-unit-test`/`sap-cds-unit-test` tuy pattern.
9. **Dong ticket**: chay `sap-finish-ticket`.

## Danh sach BAT BUOC hoi user (khong tu doan duoi moi hinh thuc)

- Edition he thong that (neu chua biet trong phien).
- Pattern kien truc — chi chot sau khi `sap-write-technical-spec` xac nhan 2 chieu voi module
  consultant, khong tu chon truoc.
- Package deploy + xac nhan rao chan Z/Y.
- Neu ra nhanh Adobe Form: ten form template `.xdp` da upload chua (xem
  `sap-scaffold-adobe-form` — dung lai neu chua co, khong tu bia).
- Neu ra nhanh RAP Unmanaged: ly do chon Unmanaged phai co ADR trong `docs/decisions/`.

## Luu y

- 🔗 Day la ban tong quat cua `/sap-generate-report` va `/sap-generate-adobe-form` — 2 lenh do
  van con vi da biet chac pattern tu dau (bo qua buoc quyet dinh o day), dung khi muon nhanh
  hon cho dung 2 truong hop do.
- 💡 Neu chi can 1 buoc rieng le (vd chi doi package, hoac chi sinh unit test cho code da co) —
  goi truc tiep skill tuong ung thay vi chay het lenh nay.
- 📖 Xem `docs/architecture.md` muc 2 (so do Mermaid pipeline day du) va
  `skills/sap-write-technical-spec/SKILL.md` (decision tree + bang pattern goc) de biet chi
  tiet tung nhanh.
