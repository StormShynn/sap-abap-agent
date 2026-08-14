---
name: sap-scaffold-adobe-form
description: |
  Sinh class ABAP in PDF qua Adobe Document Services (chuan bi data + goi CL_FP_ADS_UTIL) cho
  bao cao/chung tu can xuat PDF (invoice, PO confirmation, phieu xuat kho...). KHONG ve duoc
  layout hinh anh cua form (.xdp) — phan do bat buoc thiet ke bang Adobe LiveCycle Designer,
  cong cu GUI rieng ngoai pham vi sinh code. Hoi edition/package/ten form truoc khi sinh,
  KHONG tu doan.
  KHONG dung khi chi can hien thi du lieu tren UI (dung sap-scaffold-report/sap-scaffold-cds).
when_to_use: |
  "tao Adobe Form cho...", "in PDF ...", "xuat PDF bao cao/hoa don...",
  "PDF output qua Adobe Form", "print form cho purchase order/invoice".
argument-hint: "[mo ta noi dung form / duong dan TECHNICAL_SPEC.md]"
model: sonnet
effort: high
tools: [Read, Write, Edit, Glob, Grep, WebFetch]
---

# SAP Scaffold Adobe Form — Sinh class in PDF qua ADS

## Khi nao dung

- ✅ Can in PDF (invoice, PO confirmation, phieu xuat kho, phieu ke toan...) qua Adobe Form.
- ❌ Chi can hien thi du lieu tren UI, khong in PDF → dung `sap-scaffold-report` /
  `sap-scaffold-cds`.
- ❌ Can **ve/thiet ke layout hinh anh** cua form (vi tri field, logo, bang bieu tren trang PDF)
  → day la viec cua **Adobe LiveCycle Designer** (cong cu GUI rieng, ngoai ABAP/ADT) — skill
  nay KHONG lam duoc, chi sinh phan class ABAP goi render sau khi da co file `.xdp`.

## Gioi han quan trong (doc truoc khi bat dau, dung nhan vo nang luc khong co)

Da xac minh qua SAP Community/SAP Help (khong suy doan — xem muc Nguon tham khao):

- Form template (`.xdp`) **phai thiet ke bang Adobe LiveCycle Designer**, roi upload vao he
  thong qua ADT (Eclipse) hoac qua **Developer Extensibility → Form Objects** (Public Cloud).
  "Khong co tuy chon maintain form qua ADT" theo dung nghia sinh/sua layout — ADT chi dung de
  **upload** file da thiet ke san.
- Skill nay **chi sinh duoc**: class ABAP chuan bi data (context structure) + goi ham render
  PDF. **Khong sinh duoc** noi dung file `.xdp` (dinh dang nhi phan/XML phuc tap cua Adobe,
  khong phai thu sinh dang code text don gian va dang tin cay).
- Neu user chua co san form template (`.xdp`) da thiet ke — dung lai o Buoc 0, huong dan user
  tao truoc bang LiveCycle Designer (hoac nho nguoi co cong cu do), **KHONG tu bia** cau truc
  XDP de "cho co".

## Buoc 0: Xac dinh ngu canh (BAT BUOC, KHONG tu doan)

1. Neu FS con dang `.docx`/`.xlsx` → chay `sap-doc-to-md` truoc.
2. Neu chua co `INTAKE.md`/`TECHNICAL_SPEC.md` → chay `sap-analyze-function-spec` +
   `sap-write-technical-spec` truoc.
3. **Edition**: doc `reference/process/sap-service-type-context.md` neu chua biet he thong dang
   lam viec trong phien nay (anh huong den co che upload form — xem bang Buoc 4).
4. **Package**: chay `sap-deployment-target` neu chua xac nhan.
5. **Form template da co chua?** Hoi thang user: "File `.xdp` cho form nay da duoc thiet ke va
   upload vao he thong chua? Ten form template la gi?" — NEU CHUA CO, dung lai, huong dan user
   thiet ke truoc bang Adobe LiveCycle Designer (khong tu tao gia dinh ten form).

## Buoc 1: Thu thap yeu cau (hoi, KHONG doan)

- Data can trong form: field header (vd so PO, ngay, nha cung cap), field item/table (dong chi
  tiet), field tong hop (tong tien, thue).
- Ten form template da upload (tu Buoc 0.5).
- Output: gui email, cho download qua Fiori action, hay dinh kem vao BO?
- Ngon ngu form (mac dinh `sy-langu`, hay co dieu kien nhieu ngon ngu).

## Buoc 2: Sinh class ABAP (phan chung, giong nhau phan lon giua cac edition)

```abap
CLASS zcl_<ten>_print DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS render_pdf
      IMPORTING iv_<key>      TYPE <kieu key, vd so chung tu>
      RETURNING VALUE(rv_pdf) TYPE xstring
      RAISING   cx_fp_runtime cx_fp_facade cx_fp_no_data.

  PRIVATE SECTION.
    METHODS prepare_context
      IMPORTING iv_<key>          TYPE <kieu key>
      RETURNING VALUE(rs_context) TYPE <structure khop field cua form template>.

ENDCLASS.

CLASS zcl_<ten>_print IMPLEMENTATION.

  METHOD render_pdf.
    DATA(ls_context) = prepare_context( iv_<key> ).

    " [Unverified] — xac nhan lai chu ky method CL_FP_ADS_UTIL=>RENDER_PDF that qua ADT class
    " browser hoac trang SAP Help "Runtime API for ADS Rendering Calls" (xem Nguon tham khao)
    " truoc khi dung — ten tham so duoi day la best-effort tu tai lieu cong khai, chua tu tay
    " xac nhan tren 1 tenant that.
    cl_fp_ads_util=>render_pdf(
      EXPORTING
        i_formname = '<TEN_FORM_TEMPLATE_DA_UPLOAD>'   " tu Buoc 0.5, KHONG tu bia
        i_language = sy-langu
        i_data     = ls_context
      IMPORTING
        e_pdf      = rv_pdf ).
  ENDMETHOD.

  METHOD prepare_context.
    " Doc du lieu that qua released CDS view/API (da xac nhan qua sap-ask-consultant) —
    " tren ABAP Cloud KHONG SELECT bang chuan truc tiep (xem sap-abap-sql muc 7).
    " Map ket qua vao dung cau truc field cua form template (KHONG tu doan ten field neu chua
    " biet cau truc that cua form — hoi user hoac doc lai file .xdp qua ADT).
  ENDMETHOD.

ENDCLASS.
```

Luu y khi sinh:

- Tach `prepare_context` rieng khoi `render_pdf` de test duoc (`sap-unit-test` mock du lieu qua
  `CL_ABAP_TESTDOUBLE`, khong can goi ADS that trong unit test).
- Naming theo `sap-clean-code`: `ZCL_<TEN>_PRINT` — pattern nay khop voi tien le da dung that
  trong du an truoc (xem `docs/sap-knowledge/reusable-team-assets.md` muc 2, class dang
  `zcl_<x>_print`) — **neu du an hien tai da co san framework tuong tu** (vd class dung chung
  `render_pdf`/`get_template_by_tcode` cho nhieu form), **uu tien reuse** thay vi tao class goi
  `CL_FP_ADS_UTIL` truc tiep tu dau — grep `source code/`/`PUB_ACME_CODE/` truoc khi viet moi
  (xem `reusable-team-assets.md` muc 11).

## Buoc 3: Xu ly PDF output (theo Buoc 1)

- **Gui email**: `cl_bcs_mail_message` (xem `sap-released-classes` muc Email & Communication) —
  attach `rv_pdf` qua `cl_bcs_convert`.
- **Dinh kem vao BO**: pattern BO attachment (kieu `ZR_ATTACHMENT` neu du an da co, xem
  `reusable-team-assets.md` muc 2) hoac released API attachment cua BO tuong ung.
- **Download qua Fiori action**: RAP action tra ve `xstring`, UI xu ly download (ngoai pham vi
  ABAP class, thuoc annotation Fiori Elements — xem `sap-odata-service`).

## Buoc 4: Khac biet theo edition

| | Public Cloud (`s4hc_(public)`) | Private/On-prem |
|---|---|---|
| Co che | Developer Extensibility → Form Objects | Adobe Forms co dien (SFP) hoac cung `CL_FP_ADS_UTIL` |
| Upload form template (`.xdp`) | Qua ADT (Eclipse), sau khi thiet ke bang LiveCycle Designer | Qua SFP transaction hoac ADT |
| Class goi render | `CL_FP_ADS_UTIL=>RENDER_PDF` (Buoc 2, giong nhau) | Tuong tu, co the co class rieng theo he thong — [Unverified], can xac nhan tren tenant that |
| `[Unverified]` | Chi tiet chinh xac "Form Object" type + quy trinh dang ky trong Developer Extensibility can xac nhan qua SAP Help/tenant that truoc khi lam that | |

## Nguon tham khao (da xac minh qua WebSearch — khong suy doan)

- [Custom Adobe Forms in SAP S/4 HANA Public Cloud using Developer Extensibility (SAP Community)](https://community.sap.com/t5/technology-blog-posts-by-members/custom-adobe-forms-in-sap-s-4-hana-public-cloud-using-developer/ba-p/14344179)
- [SAP KBA 3566687 — Adobe Form Services Integration with S/4 Hana Public Cloud](https://userapps.support.sap.com/sap/support/knowledge/en/3566687)
- [Runtime API for ADS Rendering Calls — SAP Help Portal](https://help.sap.com/docs/SAP_S4HANA_CLOUD/6aa39f1ac05441e5a23f484f31e477e7/3d8686d312bc426d8b2aa323473996b0.html)
- [Generate PDF forms in S/4 HANA Public Cloud (Developer extensibility) using BTP Adobe Forms service](https://community.sap.com/t5/technology-blog-posts-by-members/generate-pdf-forms-in-s-4-hana-public-cloud-developer-extensibility-using/ba-p/13885649)
- `docs/sap-knowledge/reusable-team-assets.md` muc 2 — pattern that da dung trong du an truoc
  (neu du an hien tai co framework tuong tu, uu tien reuse).
- `reference/modules/ca-integration-patterns/SKILL.md` muc 5 (Output Management) — Adobe Form
  la chuan PDF output tren Cloud Public Edition, thay Smart Form.

## Lien ket skill khac

- `sap-scaffold-report` / `sap-scaffold-cds` — cung cap data layer nguon cho form.
- `sap-released-classes` — `cl_bcs_mail_message` (gui email).
- `reference/process/sap-service-type-context.md`, `sap-deployment-target` — bat buoc truoc khi
  sinh code that.
- `sap-authorization` — neu form/action can gioi han quyen truy cap.
