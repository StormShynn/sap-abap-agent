---
name: sap-unit-test
description: |
  Sinh ABAP Unit test class cho method/behavior da scaffold. Dung sau khi scaffold code
  (sap-scaffold-rap/cds) va co method public can test, hoac INTAKE.md co edge case o muc 6.
when_to_use: |
  "sinh ABAP Unit test cho class X", "viet test case cho behavior nay",
  "test edge case tu INTAKE muc 6".
argument-hint: "[duong dan source file ABAP] [duong dan INTAKE.md]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Glob]
---

# SAP Unit Test — Sinh ABAP Unit test class

## Khi nao dung

- ✅ Sau khi scaffold code (`sap-scaffold-rap`).
- ✅ Co method public can test.
- ✅ INTAKE.md co edge case o muc 6.

## Output

File `*.clas.testclasses.abap` (cung ten class + `.testclasses.abap`).

## Quy trinh

### Buoc 1: Phan tich method can test

Tu source code, liet ke method public: validate, action (approve/reject...), determination, CRUD
(managed thi SAP tu test; unmanaged can test rieng).

### Buoc 2: Liet ke test case

Cho moi method: happy path (input hop le -> output mong doi), edge case tu INTAKE muc 6, negative
case (input khong hop le -> expect exception/return false).

### Buoc 3: Viet test class

```abap
*"* use this source file for your ABAP unit test classes

CLASS ltc_<object>_helper DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS:
      test_validate_ok FOR TESTING RAISING cx_static_check,
      test_validate_empty FOR TESTING RAISING cx_static_check,
      setup.
ENDCLASS.

CLASS ltc_<object>_helper IMPLEMENTATION.
  METHOD setup.
    " Setup test data
  ENDMETHOD.

  METHOD test_validate_ok.
    DATA(ls_data) = VALUE zi_<object>( <field> = '<gia_tri_hop_le>' ).
    DATA(lv_valid) = zcl_<object>_helper=>validate( ls_data ).
    cl_abap_unit_assert=>assert_equals( act = lv_valid exp = abap_true ).
  ENDMETHOD.

  METHOD test_validate_empty.
    DATA(ls_data) = VALUE zi_<object>( <field> = '' ).
    DATA(lv_valid) = zcl_<object>_helper=>validate( ls_data ).
    cl_abap_unit_assert=>assert_equals( act = lv_valid exp = abap_false ).
  ENDMETHOD.
ENDCLASS.
```

### Buoc 4: Pattern test cho RAP

- **Managed**: dung `CL_ABAP_TESTDOUBLE` de gia lap behavior.
- **Unmanaged**: test truc tiep qua local handler class, hoac Fiori Elements test runner.

## Quy tac

- 1 test method cho 1 case, ten mo ta ro case: `test_<method>_<condition>`.
- Dung `cl_abap_unit_assert` (released).
- `DURATION SHORT`, `RISK LEVEL HARMLESS` (khong update DB production).
- Test phai doc lap (khong phu thuoc test khac).

## Reference

- Test framework: ABAP Unit trong Eclipse ADT (`Ctrl+Shift+F10`).
- Skill `sap-clean-code` — clean code convention.
- Skill `sap-atc-review` — check test coverage sau khi sinh test.
