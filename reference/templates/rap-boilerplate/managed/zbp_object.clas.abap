"! <p>Behavior implementation class for ZI_<OBJECT>.</p>
"!
"! Package: <package>
"! Author:  <Your Name>
"! Date:    <YYYY-MM-DD>
CLASS zbp_<object> DEFINITION PUBLIC ABSTRACT BEHAVIOR FOR ZI_<OBJECT>.

  PUBLIC SECTION.
    METHODS validate<Field1> FOR VALIDATE ON SAVE
      IMPORTING keys FOR <Object>~validate<Field1>.

ENDCLASS.

CLASS zbp_<object> IMPLEMENTATION.

  METHOD validate<Field1>.
    " Read full data for keys
    READ ENTITIES OF ZI_<OBJECT> IN LOCAL MODE
      ENTITY <Object>
        FIELDS ( <Field1> )
        WITH CORRESPONDING #( keys )
      RESULT DATA(lt_records).

    LOOP AT lt_records INTO DATA(ls_record).
      IF ls_record-<Field1> IS INITIAL.
        append value #( %tky = ls_record-%tky
                        %msg = new_message_with_text(
                          severity = if_abap_behv_message=>severity-error
                          text = '<Field1> is required' )
                        ) to failed-<Object>.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
