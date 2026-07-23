---
name: sap-rap-events
description: Huong dan RAP Business Events — event-driven architecture trong SAP S/4HANA Cloud, RAP behavior events, SAP Event Mesh integration, event publishing and consuming.
when_to_use: |
  "RAP business events trong ABAP Cloud", "SAP Event Mesh voi RAP",
  "publish event tu RAP BO", "event-driven ABAP", "consume event tu RAP".
argument-hint: "[cau hoi ve RAP events / Event Mesh / event-driven]"
effort: medium
model: sonnet
---

# RAP Business Events — Event-Driven ABAP

## 1. Kien truc Event-Driven

RAP Business Events cho phep RAP Business Object publish event khi co thay doi trang thai:

```
S/4HANA Cloud (RAP BO)
  │
  │  Event: SalesOrder.Created
  │  Event: SalesOrder.Changed
  │  Event: SalesOrder.Cancelled
  │
  ▼
Event Mesh (Enterprise Messaging)
  │
  ├──> CPI iFlow -> Receiver (non-SAP)
  ├──> CAP Consumer (BTP)
  └──> Another RAP BO (S/4HANA)
```

## 2. Dinh nghia Event trong RAP

```abap
" Behavior definition — khai bao event
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique;

  create; update; delete;

  " Business event
  event SalesOrderCreated parameter Z_SO_EventParams;
  event SalesOrderChanged parameter Z_SO_EventParams;
  event SalesOrderCancelled parameter Z_SO_EventParams;
}

" Behavior implementation — raise event
CLASS zbp_salesorder DEFINITION PUBLIC ABSTRACT FINAL
  FOR BEHAVIOR OF zi_salesorder.

  METHOD create FOR MODIFY.
    RAISE ENTITY EVENT z_i_salesorder~SalesOrderCreated
      FROM VALUE #(
        ( %key = keys[ 1 ]-%key
          %param-salesorderid = keys[ 1 ]-salesorderid
          %param-createdby    = cl_abap_context_info=>get_user_technical_name( ) )
      ).
  ENDMETHOD.
ENDCLASS.
```

## 3. Cau hinh Event Metadata

```abap
" Behavior definition — khai bao event metadata
define behavior for Z_I_SalesOrder alias SalesOrder
  implementation in class zbp_salesorder unique
  lock master
  etag master <timestamp>
  authorization master ( global ) ( instance );

  create; update; delete;

  event SalesOrderCreated parameter Z_SO_EventParams
    description 'Sales Order Created'
    category communication;
  event SalesOrderChanged parameter Z_SO_EventParams
    description 'Sales Order Changed'
    category communication;
}
```

**Category**: `communication` (ra ngoai) / `internal` (chi trong S/4HANA).

## 4. Structure Parameter

```abap
" Structure cho event parameter (CDS view)
@EndUserText.label: 'Sales Order Event Parameters'
define structure Z_SO_EventParams {
  salesorderid : abap.char( 10 );
  createdby    : abap.char( 12 );
  totalnetamount : abap.curr( 15, 2 );
}
```

## 5. Publish Event

```abap
" Trong RAP handler
RAISE ENTITY EVENT z_i_salesorder~SalesOrderCreated
  FROM VALUE #(
    ( %key-%param = keys[ 1 ]-%param
      %param-salesorderid = keys[ 1 ]-salesorderid
      %param-createdby = lv_user )
  ).

" Kiem tra event da duoc publish
" ADT -> Event Queue -> Xem pending events
" /IWBEP/CM_CLIENT_CNT -> Kiem tra outgoing events
```

## 6. Consume Event

### Trong CPI:
1. Tao iFlow voi Event Mesh receiver adapter
2. Subscribe vao topic: `SAP/SCM/BO/SALESORDER/*`
3. Mapping event payload -> target format

### Trong CAP:
```js
// CAP consumer
const s4 = await cds.connect.to('S4HANA')
s4.on('SalesOrderCreated', async (req) => {
  const { salesorderid } = req.data
  // Process event
})
```

## 7. Event Mesh Integration

### Cau hinh Event Mesh trong S/4HANA Cloud:

1. **Tao Communication Arrangement**: `SAP_COM_0109` (Enterprise Event Enablement)
2. **Cau hinh Channel**: Event Mesh -> Topic
3. **Subscribe**: Subcribe event tu RAP BO
4. **Kich hoat**: Activate event publishing

### Cac topic pattern:

```
SAP/SCM/BO/SALESORDER/Created
SAP/SCM/BO/SALESORDER/Changed
SAP/SCM/BO/SALESORDER/Cancelled
SAP/MM/BO/PURCHASEORDER/Created
SAP/MM/BO/PURCHASEORDER/Changed
SAP/FI/BO/JOURNALENTRY/Created
```

## 8. Khi nao dung Event?

| Tinh huong | Dung Event? | Thay bang |
|------------|-------------|-----------|
| Realtime integration (S/4HANA -> non-SAP) | ✅ Event + CPI | |
| Async business process (Order -> Invoice) | ✅ Event | |
| Audit trail | ❌ | Custom table + log |
| Synchronous API (request-response) | ❌ | OData service |
| Trigger workflow | ✅ Event | |
| Delay processing (<=5s) | ❌ | EML direct |

## Nguon tham khao

- SAP Help Portal: RAP Business Events
- SAP Community: Event-driven RAP
- SAP Event Mesh documentation
- `https://api.sap.com` — Event topics catalog
