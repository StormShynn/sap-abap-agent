---
name: sap-scaffold-cds-analytics
description: |
  Sinh CDS analytics (Cube/Dimension/Text) + Analytical Query — dung khi bao cao can
  aggregate/multi-dimensional (KPI, dashboard) thay vi list/detail don gian.
  Uu tien build Analytical Query TREN CDS view/cube da released truoc; chi scaffold Cube/Dimension
  tu dau khi khong co base phu hop (custom fact table).
  KHONG dung cho list/detail don gian khong aggregate (dung sap-scaffold-cds).
when_to_use: |
  "tao KPI dashboard cho X", "sinh analytical query", "bao cao multi-dimensional",
  "custom cube cho Y", "embedded analytics tu bang Z".
argument-hint: "[duong dan TECHNICAL_SPEC.md hoac field list + measure/dimension]"
model: sonnet
effort: medium
tools: [Read, Write, Edit, Glob]
---

# SAP Scaffold CDS Analytics — Cube/Dimension/Text + Analytical Query

## ⚠️ Tinh trang xac minh noi dung

[Seed set — cung tinh trang voi `reference/modules/sap-bw-cloud/SKILL.md`]. Cu phap duoi day tong
hop tu SAP Help/blog chinh thuc (xem Nguon tham khao) — **chua activate thu trong ADT that**. Annotation
co ban (`@Analytics.dataCategory`, `@DefaultAggregation`, `@Analytics.query`) trung khop voi noi
dung da co san trong `sap-bw-cloud/SKILL.md` nen do tin cay tot hon; phan Cube/Dimension/Text tu
scaffold la **noi dung moi**, chua doi chieu — kiem tra ky truoc production.

## Khi nao dùng

- ✅ Bao cao can aggregate (SUM/AVG/COUNT) theo nhieu chieu (thoi gian, san pham, khach hang...).
- ✅ Dashboard KPI, Fiori Analytical List Page / Overview Page can key figure.
- ❌ List/Detail don gian khong aggregate — dung `sap-scaffold-cds`.
- ❌ Bao cao vuot kha nang embedded analytics (data warehouse, nhieu nguon, planning) — can SAC/
  BW/4HANA, xem `reference/modules/sap-bw-cloud/SKILL.md`.

## Buoc 0: Uu tien base co san — ĐỪNG tu xay Cube tu dau neu khong can

Theo `reference/modules/sap-bw-cloud/SKILL.md`: cach mac dinh cho analytics tren S/4HANA Cloud la
**Custom Analytical Query TREN CDS view da released** (Fiori app "Custom Analytical Queries" — key
user tu lam duoc, khong can code), KHONG phai tu dung Cube/Dimension tu dau. Chi lam Buoc 1-2
(custom Cube) khi:

- Nghiep vu dua tren **custom table** (khong CDS/Cube chuan SAP nao khop), HOAC
- Can annotation/association ma Fiori app Custom Analytical Query khong cho chinh.

Tim Cube/CDS chuan SAP truoc qua `sap-cds-kb` hoac hoi `sap-bw-consultant-cloud`. Neu co base khop
→ nhay thang Buoc 3 (Analytical Query tren base co san).

## Buoc 1: (Chi khi can custom) Tao Cube view

```abap
@Analytics.dataCategory: #CUBE
@VDM.viewType: #BASIC
@EndUserText.label: '<Object> Cube'
define view ZI_<OBJECT>_CUBE
  as select from ZI_<OBJECT>
  association [0..1] to ZI_<OBJECT>_DIM as _Dimension
    on $projection.DimensionKey = _Dimension.DimensionKey
{
  key DocumentID,
  key DocumentItem,
      DimensionKey,
      @Semantics.amount.currencyCode: 'Currency'
      @DefaultAggregation: #SUM
      NetAmount,
      @Semantics.quantity.unitOfMeasure: 'Unit'
      @DefaultAggregation: #SUM
      Quantity,
      Currency,
      Unit,
      _Dimension
}
```

## Buoc 2: (Chi khi can custom) Tao Dimension + Text view

Dimension: chi characteristic field lam key (KHONG duoc co key figure lam key).

```abap
@Analytics.dataCategory: #DIMENSION
define view ZI_<OBJECT>_DIM
  as select from ztb_<dimension_table>
  association [0..1] to ZI_<OBJECT>_TEXT as _Text
    on  $projection.DimensionKey = _Text.DimensionKey
    and _Text.Language           = $session.system_language
{
  key DimensionKey,
      DimensionType,
      _Text.DimensionText as DimensionText,   // scalar projection — hop le vi _Text la to-one
      _Text
}
```

Text (ngon ngu-phu thuoc, dung cho F4/hien thi mo ta):

```abap
@Analytics.dataCategory: #TEXT
define view ZI_<OBJECT>_TEXT
  as select from ztb_<dimension>_t
{
  key DimensionKey,
  key Language,
      DimensionText
}
```

## Buoc 3: Tao Analytical Query (tren Cube/CDS da co — custom hoac released)

Annotation dung dung y het `reference/modules/sap-bw-cloud/SKILL.md` muc 6 (da co trong repo):

```abap
@Analytics.query: true
@AnalyticsDetails: true
@Consumption: true
@EndUserText.label: '<Object> Query'
define view entity ZC_<OBJECT>_QUERY
  as select from ZI_<OBJECT>_CUBE
{
  @Consumption.filter: { selectionType: #INTERVAL, mandatory: true }
  CalendarYear,

  DimensionKey,

  @DefaultAggregation: #SUM
  NetAmount,

  @DefaultAggregation: #SUM
  Quantity
}
```

Neu query don gian tren base **da released** — uu tien publish qua Fiori app **Custom Analytical
Queries** (key user, khong can code). Chi viet CDS thu cong o tren khi can annotation/association
ma Fiori app khong ho tro, hoac base la Cube custom tu Buoc 1.

## Naming (de xuat — repo nay chua co quy uoc chinh thuc truoc skill nay)

| Object | Prefix de xuat | Ghi chu |
|---|---|---|
| Cube | `ZI_<NAME>_CUBE` | Interface layer, VDM basic/composite |
| Dimension | `ZI_<NAME>_DIM` | Characteristic-only, khong key figure |
| Text | `ZI_<NAME>_TEXT` | Key + Language + text field |
| Analytical Query | `ZC_<NAME>_QUERY` | Consumption layer, `@Analytics.query: true` |

## Luu y

- ⚠️ Key figure (measure) phai la kieu so + co `@DefaultAggregation` — thieu annotation nay, app
  Fiori Analytical se khong cho chon field do lam key figure de aggregate.
- ⚠️ Dimension KHONG duoc co key figure field lam key — chi characteristic field.
- ⚠️ [Unverified] Mot so annotation nang cao cho BW extraction/hierarchy co the CHI danh cho
  on-premise, khong released cho ABAP Cloud restricted development — luon thu activate tren he
  Cloud that, khong gia dinh annotation nao cung released chi vi co trong tai lieu chung (dung
  chung on-premise + Cloud).
- 💡 Currency/quantity field don vi (`Currency`/`Unit`) phai co mat trong SELECT list ngang hang
  key figure — thieu se loi "currency/unit field not found" khi activate hoac hien thi sai.
- 🔗 Neu chua chac can Cube rieng hay du dung Custom Analytical Query tren base co san: hoi agent
  `sap-bw-consultant-cloud` truoc khi scaffold.
- 🔗 Buoc tiep theo: `sap-atc-review`; publish qua Fiori "Custom Analytical Queries" hoac Service
  Definition/Binding neu expose OData.

## Nguon tham khao

- `reference/modules/sap-bw-cloud/SKILL.md` (co san trong repo — cung "seed set", cung tinh trang
  xac minh nhu skill nay).
- SAP Blog: "Embedded Analytics with ABAP Cloud – The Multidimensional Cube" (tim qua
  `blogs.sap.com`, phan 1+2) — fetch truc tiep bi chan HTTP 403 luc soan skill nay; doc qua trinh
  duyet that de xac nhan chi tiet truoc khi dung production.
- SAP Help Portal: "ABAP CDS — Analytics Annotations", Custom Analytical Queries (Fiori app, key
  user extensibility).
