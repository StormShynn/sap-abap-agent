# RAP Events boilerplate (publish + CAP consume stub)

Copy into a Z* package after `sap-scaffold-rap` when TECHNICAL_SPEC needs business events.

## Objects (rename Z* to project prefix)

| File | Role |
|------|------|
| `z_so_eventparams.ddls.asddls` | Event parameter structure |
| `zr_object.bdef.asbdef` | BDEF fragment with `event … category communication` |
| `zbp_object_events.clas.locals_imp.abap` | Sample `RAISE ENTITY EVENT` |
| `cap-consumer/srv/event-handler.js` | CAP subscribe stub |

## Ops

1. Communication Arrangement `SAP_COM_0109` (Enterprise Event Enablement)
2. Event Mesh channel + topic bind
3. ADT Event Queue — verify outbound

See skill `sap-rap-events` checklist.
