---
name: sap-migrate-segw-to-rap
description: |
  Reverse-engineer 1 SEGW OData V2 service da co sang RAP OData V4 — doc Data Model (entity/
  association) + custom logic trong DPC_EXT, map sang RAP (CDS + behavior + service).
  Dung khi can nang cap service SEGW cu len chuan ABAP Cloud/RAP. KHONG dung de tao service moi tu
  dau (dung sap-scaffold-rap truc tiep).
when_to_use: |
  "migrate SEGW nay sang RAP", "nang cap OData V2 len V4", "chuyen doi service SEGW cu",
  "RAP thay the SEGW project X".
argument-hint: "[ten SEGW project can migrate]"
model: sonnet
effort: high
tools: [Read, Write, Edit, Glob]
---

# SAP Migrate SEGW → RAP

## Khi nao dung

- ✅ Co SEGW project dang chay tren he thong, can chuyen sang RAP (chuan ABAP Cloud, OData V4).
- ✅ Ly do thuc day: `sap-odata-service` da khuyen nghi RAP-based OData V4 cho moi du an moi; SEGW
  van chay duoc nhung khong phai chuan ABAP Cloud.
- ❌ Tao service moi tu dau (chua co SEGW) — dung thang `sap-scaffold-rap`.

## Buoc 1: Doc Data Model cua SEGW project

Mo SEGW (giao dien classic hoac qua ADT), ghi lai:

- **Entity Type** + field list + key.
- **Entity Set**.
- **Association** (cardinality, referential constraint) → se thanh CDS association/composition.
- **Deep Entity** (neu co) → thanh composition RAP (parent-child create 1 lan).

## Buoc 2: Doc custom logic trong DPC_EXT

Class `<SERVICE>_DPC_EXT` la noi chua toan bo logic custom (redefine tu `*_DPC`). Cac method hay
gap va huong RAP tuong duong:

| Method DPC_EXT (SEGW) | Muc dich | RAP tuong duong |
|---|---|---|
| `<ENTITYSET>_GET_ENTITYSET` | Doc list (co the co filter/sort custom) | CDS view SELECT + (neu logic phuc tap) custom query provider (`IF_RAP_QUERY_PROVIDER`) |
| `<ENTITYSET>_GET_ENTITY` | Doc 1 record | CDS view (RAP tu dong ho tro qua key) |
| `<ENTITYSET>_CREATE_ENTITY` | Tao moi + validate | Behavior `create` + `validation ... on save` |
| `<ENTITYSET>_UPDATE_ENTITY` | Sua + validate | Behavior `update` + validation |
| `<ENTITYSET>_DELETE_ENTITY` | Xoa | Behavior `delete` |
| Custom function import | Logic nghiep vu rieng (khong CRUD chuan) | RAP `action` |

⚠️ [Unverified — ten method chinh xac phu thuoc ban SEGW da generate cho project cu the] Luon doi
chieu voi class `DPC_EXT` that cua project dang migrate truoc khi ap dung bang tren, KHONG gia
dinh giong 100% cho moi project.

## Buoc 3: Map sang RAP — dung sap-scaffold-rap

Sau khi co bang mapping Buoc 1-2, chuyen sang quy trinh chuan:

1. Table: neu SEGW da dua tren table/CDS co san, tai su dung; neu SEGW tu tao cau truc rieng
   (khong persist ro rang), can `sap-cloud-dictionary` tao table moi truoc.
2. Chay `sap-scaffold-rap` voi field list + logic da map o Buoc 2 lam input cho
   `TECHNICAL_SPEC.md`.
3. Logic trong `GET_ENTITYSET` co filter/sort custom phuc tap → dung custom query provider (xem
   gotcha #5 trong `sap-scaffold-rap`).

## Buoc 4: Chay song song (dual-maintenance) truoc khi tat SEGW

- Giu SEGW service chay song song voi RAP service moi trong giai doan chuyen tiep.
- So sanh output 2 service (field tuong duong, edge case) truoc khi chuyen consumer (Fiori app,
  integration) sang endpoint RAP.
- Chi deactivate SEGW service sau khi xac nhan KHONG con consumer nao goi toi no (kiem tra qua
  API Gateway/usage log **that**, khong doan).

## Luu y

- ⚠️ OData V2 (SEGW) vs V4 (RAP) khac ve `$batch`, deep insert, delta token — Fiori app phia
  client co the can dieu chinh (annotation, `manifest.json`) khi doi endpoint, khong chi doi
  backend.
- 🔗 So sanh chi tiet SEGW vs RAP: skill `sap-odata-service` (muc 2).
- 🔗 Sau khi scaffold: `sap-atc-review`, `sap-unit-test`/`sap-cds-unit-test`, `sap-finish-ticket`.

## Nguon tham khao

- SAP Help Portal: tim "Service Builder (Transaction SEGW)" va tai lieu migration OData V2 → V4
  tren `help.sap.com` — chua fetch full noi dung luc soan skill nay, doc truc tiep truoc khi ap
  dung cho du an that.
