@AbapCatalog: {
  sqlViewName: 'ZI_<OBJECT>',
  compiler.compareFilter: true
}
@AccessControl: {
  authorizationCheck: #CHECK
}
@EndUserText: {
  label: '<Object> Interface View'
}
define view ZI_<OBJECT>
  as select from ztb_<object>
{
  key <key_field> as <KeyField>,
      <field_1>   as <Field1>,
      <field_2>   as <Field2>,
      /* TODO: add field from INTAKE section 5.4 */
      created_by  as CreatedBy,
      created_at  as CreatedAt,
      changed_by  as ChangedBy,
      changed_at  as ChangedAt
}
