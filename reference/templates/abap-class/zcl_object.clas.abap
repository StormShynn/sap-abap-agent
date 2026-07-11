"! <p>Class <Ten class>.</p>
"!
"! Package: <package>
"! Author:  <Your Name>
"! Date:    <YYYY-MM-DD>
CLASS zcl_<object> DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS <method_name>
      IMPORTING
        <param_1>     TYPE <type_1>
      RETURNING
        VALUE(result) TYPE <return_type>
      RAISING
        cx_static_check.

ENDCLASS.

CLASS zcl_<object> IMPLEMENTATION.

  METHOD <method_name>.
    " TODO: implement logic tu TECHNICAL_SPEC.md
  ENDMETHOD.

ENDCLASS.
