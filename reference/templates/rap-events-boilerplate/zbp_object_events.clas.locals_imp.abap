*"* use this source file for the definition and implementation of
*"* local helper classes, interface definitions and type
*"* declarations
CLASS lhc_object DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS create FOR MODIFY
      IMPORTING entities FOR CREATE object.
ENDCLASS.

CLASS lhc_object IMPLEMENTATION.
  METHOD create.
    " After successful create mapping — raise communication event
    RAISE ENTITY EVENT zr_object~ObjectCreated
      FROM VALUE #(
        FOR key IN keys (
          %key-salesorderid = key-salesorderid
          %param-salesorderid = key-salesorderid
          %param-createdby = cl_abap_context_info=>get_user_technical_name( )
        )
      ).
  ENDMETHOD.
ENDCLASS.
