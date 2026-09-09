@EndUserText.label: 'Sales Order Event Parameters (template)'
define abstract entity Z_SO_EventParams
{
  salesorderid   : abap.char(10);
  createdby      : abap.char(12);
  totalnetamount : abap.curr(15,2);
}
