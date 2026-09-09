---
name: sap-scaffold-report
description: |
  Sinh bao cao (report) doc du lieu, tu dong chon dung kien truc theo edition dang lam viec —
  CDS + Fiori Elements List Report cho Public Cloud/BTP (giao lai cho sap-scaffold-cds /
  sap-scaffold-cds-analytics), ABAP classical report kieu OOP (CL_SALV_TABLE, khong
  PERFORM/FORM) cho Private Cloud/On-prem. Hoi edition + package + field truoc khi sinh code,
  KHONG tu doan.
  KHONG dung cho form CRUD (dung sap-scaffold-rap) hay in PDF (dung sap-scaffold-adobe-form
  sau khi co data layer tu skill nay).
when_to_use: |
  "tao bao cao cho...", "sinh report liet ke...", "can 1 report doc du lieu ve...",
  "list report cho module X", "bao cao ALV".
argument-hint: "[mo ta bao cao hoac duong dan TECHNICAL_SPEC.md]"
model: sonnet
effort: high
tools: [Read, Write, Edit, Glob, Grep]
---

# SAP Scaffold Report — Sinh bao cao theo dung edition

## Khi nao dung

- ✅ User can 1 report/list doc du lieu (khong CRUD, khong tao/sua/xoa).
- ✅ Chua biet report nen la CDS+Fiori hay classical ABAP — skill nay tu hoi edition roi quyet dinh.
- ❌ Can form CRUD (tao/sua/xoa) → dung `sap-scaffold-rap`.
- ❌ Can in PDF/Adobe Form → dung skill nay TRUOC de co data layer, roi dung
  `sap-scaffold-adobe-form` cho phan render PDF (2 skill khac nhau, khong lam chung).

## Buoc 0: Xac dinh ngu canh (BAT BUOC, KHONG tu doan)

Thu tu, dung lai o buoc nao da biet trong phien nay:

1. Neu FS con dang `.docx`/`.xlsx` → chay `sap-doc-to-md` truoc.
2. Neu chua co `INTAKE.md` → chay `sap-analyze-function-spec` truoc.
3. Neu chua co `TECHNICAL_SPEC.md` → chay `sap-write-technical-spec` truoc (bang "Bang chon
   pattern nhanh" cua skill do da tro ve day cho hang "bao cao/list").
4. **Edition**: doc `reference/process/sap-service-type-context.md` neu chua biet he thong dang
   lam viec la `s4hc_(public)` / `s4hc_(private)` / `onprem` / `btp` trong phien nay. Day la
   dieu kien re nhanh o Buoc 2 — KHONG tu gia dinh Public Cloud.
5. **Package**: chay `sap-deployment-target` neu chua xac nhan package deploy tren he thong that.

## Buoc 1: Thu thap yeu cau report (hoi user neu FS chua du, KHONG tu doan)

- Nguon du lieu: entity/CDS view nao (da xac nhan qua `sap-ask-consultant` neu chua ro phan he).
- Cot hien thi: field nao, thu tu nao.
- Field loc (selection screen / filter bar): field nao bat buoc, field nao optional, kieu range
  hay single value.
- Sort mac dinh / group / subtotal (neu co).
- Co can export Excel khong? Neu co, dung rieng `sap-released-classes` muc File Handling (XCO)
  hoac (neu du an co) `docs/sap-knowledge/reusable-team-assets.md` muc 3 — KHONG lam trong skill
  nay.
- Co can in PDF khong? Neu co, ghi nho de goi `sap-scaffold-adobe-form` SAU khi xong Buoc 2.

## Buoc 2: Re nhanh theo edition

### Nhanh A — Public Cloud (`s4hc_(public)`) hoac BTP

ABAP Cloud KHONG released ALV Grid Display / classical report. Bao cao = CDS view + Fiori
Elements List Report. Skill nay KHONG lap lai co che scaffold CDS — chi quyet dinh nhanh nao va
ban giao field list tu Buoc 1:

| Yeu cau | Skill dung |
|---|---|
| Chi list/filter don gian, khong tong hop | `sap-scaffold-cds` |
| Can Cube/Dimension/aggregate/KPI dashboard | `sap-scaffold-cds-analytics` |

Sau khi 2 skill do sinh xong CDS 3-layer, quay lai Buoc 3 cua skill nay.

### Nhanh B — Private Cloud / On-prem — Classical Report kieu OOP

Day la phan **chua co skill nao cover truoc day**. Tren Private Cloud (neu du an chon compat
scope classic) hoac On-prem, classical report van dung duoc — sinh theo mau OOP (khong
PERFORM/FORM cu, logic nam trong method cua 1 class):

```abap
REPORT z<ten_report>.

" --- Selection screen: dien field da thu thap o Buoc 1 ---
PARAMETERS:
  p_werks TYPE werks_d OBLIGATORY.          " vi du: field bat buoc
SELECT-OPTIONS:
  s_matnr FOR mara-matnr.                   " vi du: field range optional

CLASS lcl_report DEFINITION FINAL.
  PUBLIC SECTION.
    METHODS run.
  PRIVATE SECTION.
    METHODS select_data
      RETURNING VALUE(rt_data) TYPE STANDARD TABLE.   " thay bang type thuc te theo field Buoc 1
    METHODS display_alv
      IMPORTING it_data TYPE STANDARD TABLE.
ENDCLASS.

CLASS lcl_report IMPLEMENTATION.

  METHOD run.
    DATA(lt_data) = select_data( ).
    IF lt_data IS INITIAL.
      MESSAGE 'Khong co du lieu phu hop dieu kien loc' TYPE 'S' DISPLAY LIKE 'W'.
      RETURN.
    ENDIF.
    display_alv( lt_data ).
  ENDMETHOD.

  METHOD select_data.
    " Query tren he thong onprem/private duoc SELECT bang chuan truc tiep (khac ABAP Cloud) —
    " van uu tien released CDS view neu da co san, chi fallback bang chuan khi khong co view
    " phu hop (xem reference/process/sap-service-type-context.md muc 4).
    SELECT *
      FROM mara                              " thay bang nguon du lieu that da xac nhan Buoc 1
      WHERE werks = @p_werks
        AND matnr IN @s_matnr
      INTO TABLE @rt_data.
  ENDMETHOD.

  METHOD display_alv.
    cl_salv_table=>factory(
      IMPORTING r_salv_table = DATA(lo_alv)
      CHANGING  t_table      = it_data ).
    lo_alv->get_functions( )->set_all( abap_true ).
    lo_alv->display( ).
  ENDMETHOD.

ENDCLASS.

START-OF-SELECTION.
  NEW lcl_report( )->run( ).
```

Luu y khi sinh nhanh nay:

- **Local class `lcl_report`** du cho report don gian. Neu logic phuc tap (nhieu method, can
  ABAP Unit test rieng) → tach thanh **global class** `ZCL_<TEN>_REPORT` va goi tu report
  program (de test duoc qua `sap-unit-test`/`CL_ABAP_TESTDOUBLE`).
- **KHONG dung `REUSE_ALV_GRID_DISPLAY`** (function module cu, khong khuyen dung code moi) —
  luon dung `CL_SALV_TABLE` (OOP, theo dung yeu cau "uu tien code OOP").
- Day la **classical ABAP, khong phai ABAP Cloud** — chi tao duoc tren he thong/compat scope cho
  phep classical development. Xac nhan lai voi `reference/process/sap-service-type-context.md`
  truoc khi bat dau, dung tu gia dinh la duoc phep chi vi la Private Cloud (con tuy compat scope
  du an chon).
- Naming: `Z<ten_report>` cho program, theo dung quy uoc trong `sap-clean-code`.

## Buoc 3: Sau khi sinh code

1. `sap-atc-review` — check naming/clean code (ap dung ca 2 nhanh).
2. `sap-unit-test` (neu tach global class) — test method `select_data`, mock nguon du lieu qua
   `CL_ABAP_TESTDOUBLE` hoac `CL_OSQL_TEST_ENVIRONMENT` (xem `sap-cds-unit-test` neu nguon la
   CDS).
3. `sap-finish-ticket`.

## Luu y

- ⚠️ Khong tu gia dinh edition/package — luon hoi neu chua biet trong phien nay (nguyen tac
  `sap-ask-before-guessing`).
- ⚠️ Nhanh B chi hop le khi he thong/compat scope cho phep classical ABAP — KHONG dung cho
  `s4hc_(public)` thuan tuy.
- 💡 Neu FS ghi "ALV" nhung he thong la Public Cloud, day chinh la truong hop can re nhanh A —
  xem tien le da ghi trong `docs/sap-knowledge/customer-landscape.md` va bang mapping trong
  `skills/sap-cloud-migration/SKILL.md` ("ALV Report (REUSE_ALV_GRID_DISPLAY) → CDS view + Fiori
  Analytical app").

## Nguon tham khao

- `docs/sap-knowledge/customer-landscape.md`, `skills/sap-cloud-migration/SKILL.md` — co so cho
  quyet dinh "ALV → CDS+Fiori" tren Public Cloud, da dung that trong du an truoc.
- SAP Help: `CL_SALV_TABLE` (OO ALV factory class).

## Lien ket skill khac

- `sap-scaffold-cds` / `sap-scaffold-cds-analytics` — nhanh A (Public Cloud/BTP).
- `sap-scaffold-adobe-form` — neu report can xuat PDF, chay skill do SAU khi co data layer.
- `sap-write-technical-spec` — buoc truoc, quyet dinh kien truc tong the.
- `reference/process/sap-service-type-context.md` — xac dinh edition, BAT BUOC truoc Buoc 2.
- `sap-deployment-target` — xac nhan package, BAT BUOC truoc khi sinh code that.
- `sap-clean-code` — quy uoc dat ten Z/Y, OOP style.
