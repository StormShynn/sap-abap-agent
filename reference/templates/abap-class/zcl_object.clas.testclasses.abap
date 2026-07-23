*"* use this source file for your ABAP unit test classes

CLASS ltc_<object> DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    METHODS:
      test_<method_name>_ok FOR TESTING RAISING cx_static_check,
      setup.
ENDCLASS.

CLASS ltc_<object> IMPLEMENTATION.
  METHOD setup.
    " Setup test data
  ENDMETHOD.

  METHOD test_<method_name>_ok.
    DATA(result) = zcl_<object>=>new( )->method_name( <param_1> = '<gia_tri_hop_le>' ).
    cl_abap_unit_assert=>assert_not_initial( result ).
  ENDMETHOD.
ENDCLASS.
