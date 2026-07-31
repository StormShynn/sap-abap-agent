---
description: Sinh full code Adobe Form (in PDF) tu file dac ta (md/docx/xlsx), tu dong theo edition, hoi package/form template - khong tu doan
argument-hint: "[duong dan file .md/.docx/.xlsx dac ta form]"
---

# /sap-generate-adobe-form — Dac ta → Adobe Form (full code, theo dung edition)

Lenh nay noi cac skill co san lai voi nhau de sinh **class ABAP in PDF qua Adobe Document
Services**. KHONG tu doan thong tin he thong that, va **KHONG tu ve duoc layout hinh anh cua
form** — phan do bat buoc lam bang Adobe LiveCycle Designer (cong cu GUI rieng), lenh nay chi
sinh phan class ABAP.

## Cach dung

```text
/sap-generate-adobe-form examples/FS_in-phieu-xuat-kho.docx
```

Neu khong truyen duong dan, hoi user file dac ta o dau.

## Quy trinh (Claude thuc hien tuan tu, dung lai hoi user o moi diem "BAT BUOC hoi")

1. **Convert dau vao** (neu la `.docx`/`.xlsx`): chay skill `sap-doc-to-md`.
2. **Sinh INTAKE.md**: chay skill `sap-analyze-function-spec`.
3. **Xac dinh edition** (neu chua biet trong phien nay): doc
   `reference/process/sap-service-type-context.md` — **BAT BUOC hoi user** neu khong xac dinh
   duoc tu config.
4. **Kiem tra form template `.xdp` da co chua** — **BAT BUOC hoi user**: "File `.xdp` cho form
   nay da duoc thiet ke bang Adobe LiveCycle Designer va upload vao he thong chua? Ten form
   template la gi?".
   - **Chua co** → DUNG LAI o day, huong dan user thiet ke form truoc (khong tu bia cau truc
     XDP de sinh code "cho co"). Quay lai lenh nay sau khi co form template.
   - **Da co** → tiep buoc 5.
5. **Sinh TECHNICAL_SPEC.md**: chay skill `sap-write-technical-spec` (ghi ro pattern la
   data-layer-read-only + goi Adobe Form o buoc 7).
6. **Xac nhan package + rao chan an toan**: chay skill `sap-deployment-target` — **BAT BUOC hoi
   user**, khong tu chon package mac dinh.
7. **Sinh class ABAP goi render**: chay skill `sap-scaffold-adobe-form` — sinh
   `ZCL_<TEN>_PRINT` (chuan bi data + goi `CL_FP_ADS_UTIL=>RENDER_PDF`), theo dung ten form
   template da xac nhan o buoc 4.
8. **Neu can data layer rieng** (report/list truoc khi in): chay `sap-scaffold-report` truoc
   buoc 7 de co nguon du lieu.
9. **Review + Test**: chay `sap-atc-review` roi `sap-unit-test` (mock `prepare_context`, khong
   goi ADS that trong unit test).
10. **Dong ticket**: chay `sap-finish-ticket`.

## Danh sach BAT BUOC hoi user (khong tu doan duoi moi hinh thuc)

- Edition he thong that (neu chua biet trong phien).
- Ten form template `.xdp` da upload — **neu chua co, dung lai o buoc 4, khong di tiep**.
- Package deploy + xac nhan rao chan Z/Y.
- Kenh output (gui email / dinh kem BO / download qua Fiori action).

## Luu y

- ⚠️ Lenh nay **khong bao gio tu sinh noi dung file `.xdp`** — day la gioi han cong cu (Adobe
  LiveCycle Designer la GUI rieng, khong phai code text). Neu user hoi "ve form giup toi", tra
  loi ro day la gioi han, khong nhan lam duoc.
- ⚠️ Chu ky method `CL_FP_ADS_UTIL=>RENDER_PDF` trong skill `sap-scaffold-adobe-form` la
  best-effort tu tai lieu cong khai (`[Unverified]`) — xac nhan lai qua ADT class browser hoac
  SAP Help truoc khi dung that tren tenant.
- 🔗 Xem `docs/architecture.md` muc 2 va skill `sap-scaffold-adobe-form` de biet chi tiet ranh
  gioi giua 2 edition (Public Cloud dung Developer Extensibility → Form Objects; Private/On-prem
  dung Adobe Forms co dien hoac cung co che ADS).
