@AbapCatalog: {
  sqlViewName: 'ZR_<OBJECT>',
  compiler.compareFilter: true
}
@AccessControl: {
  authorizationCheck: #CHECK
}
@EndUserText: {
  label: '<Object>'
}
@UI: {
  headerInfo: {
    typeName: '<Object>',
    typeNamePlural: '<Objects>',
    title: { type: #STANDARD, value: '<KeyField>' }
  }
}
define root view ZR_<OBJECT>
  as select from ZI_<OBJECT>
{
  key <KeyField>,
      <Field1>,
      <Field2>
}
