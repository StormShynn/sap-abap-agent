---
name: sap-cds-unit-test
description: |
  Sinh ABAP Unit test cho CDS view/RAP BO dung Test Double Framework (CL_CDS_TEST_ENVIRONMENT,
  CL_OSQL_TEST_ENVIRONMENT, CL_BOTD_*_BO_TEST_ENV) — mock data source de test logic KHONG dam vao
  DB that. Dung khi can test CDS view co logic (association, aggregation) hoac RAP BO qua EML.
  KHONG dung cho test method/class thuong (dung sap-unit-test).
when_to_use: |
  "test CDS view nay", "mock data cho CDS test", "test RAP BO khong dam DB that",
  "CDS Test Double Framework", "unit test cho analytical query".
argument-hint: "[ten CDS view hoac RAP BO can test]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Glob]
---

# SAP CDS Unit Test — Test Double Framework

## Khi nao dung

- ✅ CDS view co logic dang test duoc (join/association/aggregation/case) can mock data nguon.
- ✅ RAP BO can test khong dam vao persistence that (dung EML qua test double).
- ❌ Test method/class ABAP thuong (validate/action helper) — dung `sap-unit-test`.

## 3 loai Test Double — chon dung loai

| Can mock | Class | Dung khi |
|---|---|---|
| CDS view / CDS table entity | `CL_CDS_TEST_ENVIRONMENT` | Test CDS view co logic (join, agg, case) |
| ABAP SQL tren table/CDS entity | `CL_OSQL_TEST_ENVIRONMENT` | Test class doc qua `SELECT` (khong phai CDS view logic) |
| RAP BO qua EML (transactional buffer) | `CL_BOTD_TXBUFDBL_BO_TEST_ENV` / `CL_BOTD_MOCKEMLAPI_BO_TEST_ENV` | Test action/determination goi EML toi BO khac |

## Buoc 1: CDS Test Double (`CL_CDS_TEST_ENVIRONMENT`)

```abap
CLASS ltc_<view>_test DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA go_environment TYPE REF TO if_cds_test_environment.
    METHODS: test_<scenario> FOR TESTING RAISING cx_static_check.
    CLASS-METHODS: class_setup, class_teardown.
ENDCLASS.

CLASS ltc_<view>_test IMPLEMENTATION.
  METHOD class_setup.
    go_environment = cl_cds_test_environment=>create(
      i_for_entity      = 'Z<VIEW>'
      i_dependency_list = VALUE #( ( name = 'ZTB_<OBJECT>' type = 'TABLE' ) ) ).
  ENDMETHOD.

  METHOD test_<scenario>.
    DATA(lt_test_data) = VALUE ztb_<object>_type( ( <field> = '<gia_tri>' ) ).
    go_environment->insert_test_data( i_data = lt_test_data ).

    SELECT * FROM z<view> INTO TABLE @DATA(lt_result).

    cl_abap_unit_assert=>assert_not_initial( lt_result ).
  ENDMETHOD.

  METHOD class_teardown.
    go_environment->destroy( ).
  ENDMETHOD.
ENDCLASS.
```

**Luu y quan trong** (nguon: SAP Help Portal + SAP Community, xem Tham khao):

- Phai co key field hop le trong test data — thieu key co the lam framework raise exception.
- Khuyen nghi **disable DCL** khi test (tranh test flaky vi authorization that ap dung) — tim
  tham so tuong duong (kieu `DISABLE_DCL`) trong signature `create` cua ban ABAP dang dung, co the
  khac ten/vi tri theo version — kiem tra F1/ADT truoc khi dung.
- `i_dependency_list` phai liet ke MOI table/CDS view ma view dang test SELECT tu — thieu 1 cai se
  khong mock duoc field do, van dam vao data that trong bang goc.

## Buoc 2: (Neu can) Mock RAP BO qua EML

Dung `CL_BOTD_MOCKEMLAPI_BO_TEST_ENV` / `CL_BOTD_TXBUFDBL_BO_TEST_ENV` khi 1 action/determination
trong BO dang test goi EML (`MODIFY ENTITIES`) toi BO KHAC — tranh test that dam vao persistence
cua BO kia.

⚠️ [Unverified — chua tim duoc vi du code chi tiet cho 2 class nay luc soan skill nay, chi xac
nhan ten class ton tai va dung muc dich qua tim kiem] Tra cuu truc tiep `help.sap.com` hoac F1
trong ADT de lay cu phap chinh xac truoc khi dung — KHONG dung code mau vi khong co san o day.

## Luu y

- ⚠️ Test double **khong thay the** integration test that qua Fiori Elements/OData truoc khi dong
  ticket (van can quy trinh `sap-finish-ticket`).
- 🔗 Test method/class thuong (khong phai CDS/EML) → `sap-unit-test`.
- 🔗 Sau khi sinh test: `sap-atc-review` de check test coverage.

## Nguon tham khao

- SAP Help Portal: "ABAP CDS Test Double Framework"
  (`help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/abap-cds-test-double-framework`),
  "ABAP SQL Test Double Framework", "CDS Unit Tests: Creating the Test Class".
- SAP Community: "Introduction to CDS Test Double Framework — How to write unit tests for ABAP
  CDS", "CDS Doubles - Writing Unit Tests for ABAP CDS" (blogs.sap.com, 2018).
