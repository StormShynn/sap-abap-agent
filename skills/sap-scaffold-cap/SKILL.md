---
name: sap-scaffold-cap
description: |
  Scaffold du an CAP (Node.js) side-by-side tren BTP — cds init, db/srv/app, mta.yaml,
  handler mau. Dung khi can sinh skeleton CAP (khong thay the tu van kien truc
  sap-cap-consultant-cloud).
when_to_use: |
  "scaffold CAP", "cds init", "tao project CAP", "mta.yaml CAP", "side-by-side BTP CAP",
  "CAP consume RAP event", "CAP GenAI Hub stub".
argument-hint: "[ten project / use-case CAP]"
effort: medium
model: sonnet
tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Scaffold CAP (side-by-side BTP)

## Phan biet

| Skill / agent | Vai tro |
|---------------|---------|
| `sap-cap-consultant-cloud` | Tu van kien truc — **khong** Write code |
| **`sap-scaffold-cap` (skill nay)** | Sinh skeleton file tu template |
| `sap-rap-events` | Event publish/consume design |
| `sap-generative-ai` | AI Hub / prompt patterns trong CAP |

Neu cau hoi chi “CAP la gi / nen dung CAP hay RAP?” → dispatch consultant, **dung** scaffold.

## Buoc 0 — Hoi truoc khi doan

1. Node.js vs Java? (template mac dinh = **Node**)
2. Standalone hay extension S/4 (can Destination / remote service)?
3. Can Event Mesh consumer? GenAI Hub?
4. Target deploy: CF (MTA) hay Kyma?

## Buoc 1 — Copy boilerplate

Copy `reference/templates/cap-boilerplate/` → thu muc project user (doi ten).

Hoac (neu co CDS CLI):

```bash
cds init <app-name>
cd <app-name>
cds add hana,mta,xsuaa
```

Roi merge file mau tu boilerplate (service.cds, handler, mta stubs).

## Buoc 2 — Dien noi dung

1. `db/schema.cds` — entity nghiep vu toi thieu.
2. `srv/service.cds` + `srv/service.js` — projection + handler.
3. Neu Event Mesh: bat `srv/event-handler.js` (xem rap-events-boilerplate consumer).
4. Neu GenAI: stub goi Hub qua destination — **khong** hardcode API key (`sap-generative-ai`).
5. `mta.yaml` — module `srv`, resources HANA/XSUAA theo landscape.

## Buoc 3 — Kiem tra local

```bash
npm install
cds watch
```

Bao user smoke: OData `$metadata` + 1 GET entity.

## Buoc 4 — Handoff

- Kien truc / API S/4 / Fiori Elements annotation sau → `sap-cap-consultant-cloud`.
- Deploy CF/Kyma / Connectivity → `sap-btp-admin-consultant-cloud`.
- RAP in-app thay vi CAP → `sap-scaffold-rap` + `sap-extensibility`.

## Cam

- Khong scaffold CAP khi van de giai bang RAP in-app (Clean Core).
- Khong commit secret / `.env` co key.
- Khong claim “da deploy” neu chua co evidence CF/Kyma log.
