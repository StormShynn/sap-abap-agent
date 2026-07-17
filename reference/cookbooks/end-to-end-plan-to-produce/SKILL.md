---
name: end-to-end-plan-to-produce
description: End-to-end cookbook cho quy trinh **Plan-to-Produce (P2P-PP)** tren S/4HANA Cloud - tu MPS/MRP den Goods Receipt cho production order. Cross-module (PP -> MM -> QM -> CO/PS). Dung khi contributor can hieu flow manufacturing toan dien. Khac voi `sap-pp-cloud/SKILL.md` (seed consultant PP) vi tap trung vao **integration touchpoint** giua cac module.
effort: low
model: haiku
---

# End-to-End Cookbook - Plan-to-Produce (P2P-PP)

Cookbook di tu **MRP run -> production order complete**. Manufacturing scenario dien hinh:
demand (SO/forecast) -> MRP -> Planned Order -> Production Order -> Goods Issue -> Production
-> Goods Receipt -> CO settlement.

## 1. Tong quan quy trinh

```
[Demand   ] -> [MRP     ] -> [Planned   ] -> [Production] -> [Goods  ] -> [Production] -> [Goods  ]
[Forecast ]    [Run     ]    [Order     ]    [Order     ]    [Issue   ]    [Execute  ]    [Receipt ]
   step 1        step 2        step 3        step 4         step 5       step 6        step 7
                                                                      |
                                                       [Quality       ]
                                                       [Inspection    ]
                                                       step 6b        ]
```

## 2. Chi tiet tung step

### Step 1: Demand (forecast + sales orders)

**Module**: PP / IBP / SD
**Master data**: Material master (MARA), BOM (BOM as MAST-STPO), Routing (PLKO-PLPO), Work center (CRHD)

```
Demand sources
  |- Sales Order (SD - Make-to-Stock hoac Make-to-Order)
  |- Forecast (PP - MPS hoac IBP neu integrated)
  |- Stock transfer requirement
  |- Manual planned order (planner tu tao)
```

**Integration touchpoint**:
- **SD**: SO demand flows to MRP neu material co MRP type = 'VB' (Make-to-Stock) hoac 'VV' (Make-to-Order).
- **IBP**: IBP planning result write back demand vao S/4HANA.
- **MM**: safety stock level (MARM-EISBE) contributing to MRP.

### Step 2: MRP Run

**Module**: PP (MRP)
**Output**: Planned orders (PLAF-PLNUM)
**Fiori app**: `Manage MRP Plans` / `Run MRP`

```
MRP run (background job)
  |- Net requirement calculation (gross - stock - in-transit)
  |- Lot sizing (EX, FX, HB, TB, etc.)
  |- Lead time scheduling (in-house production time)
  |- Output: Planned order (PLAF)
       |- Material
       |- Quantity
       |- Start date / End date
       |- Plant
       |- MRP controller
```

**Integration touchpoint**:
- **MM**: read stock from MARD, MCHB, MKOL (special stock).
- **PP**: read BOM + Routing for lead time.
- **PS**: neu production order gan project -> read project dates.

**Common errors**:
- Material khong co BOM/Routing -> MRP khong the tinh lead time.
- Plant/storage location sai -> MRP tao planned order sai noi.
- MRP controller khong assign -> planned order khong co owner.

### Step 3: Planned Order -> Production Order

**Module**: PP
**Document**: `PLAF-PLNUM` (planned order) -> `AUFK-AUFNR` (production order)
**Fiori app**: `Convert Planned Orders to Production Orders` / `Manage Production Orders`

```
Convert planned order
  |- Selection: top N planned orders (theo date + priority)
  |- Production order (AUFK) tao tu planned order
  |- BOM explosion (component items tu STPO)
  |- Routing copy (operations tu PLPO)
  |- Release (status REL)
       |- Trigger Material staging (backflush neu auto)
```

**Integration touchpoint**:
- **PP**: BOM + Routing explosion.
- **MM**: component availability check.
- **CO**: production cost collector / product cost by period (phuong phap tinh gia thanh).

### Step 4: Production Order (released)

**Module**: PP
**Document**: `AUFK-AUFNR`
**Fiori app**: `Manage Production Orders` / `Production Order Cockpit`
**Released API**: `API_PRODUCTION_ORDER_2` (OData V4)

```
Production order (released, status REL)
  |- Header (plant, material, qty, dates)
  |- Components (from BOM)
  |- Operations (from routing)
       |- Work center
       |- Standard values (setup, machine, labor time)
       |- Control key (backflush, manual)
  |- Account assignment (cost center / WBS)
```

**Integration touchpoint**:
- **CO**: production cost collector tao ngay khi release.
- **PS** (neu project): link to WBS element.
- **QM**: neu material co inspection plan -> inspection lot tao o step 6b.

### Step 5: Goods Issue to Production Order (backflush)

**Module**: PP + MM
**Document**: `MSEG-MBLNR` (material doc with movement type 261)
**Fiori app**: `Post Goods Issue` / auto-backflush trong order confirmation

```
Goods Issue (GI) cho production order
  |- Movement type 261 (GI to order)
  |- Components consumed theo BOM + actual qty
  |- Stock decrement (MARD)
  |- Trigger FI posting (consumption to COGM)
       Dr. COGM (Cost of Goods Manufactured)
       Cr. Inventory (BSL)
```

**Integration touchpoint**:
- **MM**: stock decrement, batch tracking.
- **FI**: COGM posting (real-time cost tracking).
- **QM**: neu co batch / inspection, batch master update.

### Step 6: Production execution + Confirmation

**Module**: PP (HR neu co worker tracking)
**Document**: Production order operations confirmations

```
Production execution (factory floor)
  |- Operation start (status PRCSD)
  |- Time confirmation (actual time vs standard)
       |- Setup time
       |- Machine time
       |- Labor time
  |- Activity confirmation (yield, scrap, rework)
  |- Operation complete (status CNF)
  |- Order complete (status TECO neu complete, DLV neu delivered to stock)
```

**Integration touchpoint**:
- **CO**: actual cost tich luy theo operation (activity type posting).
- **HR** (SuccessFactors): neu co integration -> labor time back to SF.
- **EHS**: neu production co hazmat -> EHS incident logging.

### Step 6b: Quality Inspection (optional)

**Module**: QM
**Document**: Inspection lot (`QALS-PRUEFLOS`)
**Fiori app**: `Manage Quality Inspection Lots`

```
Neu material QMM-managed (QM active)
  |- Inspection lot auto-create (khi GR)
  |- Sample draw (qua inspection plan)
  |- Inspection results (record characteristics)
  |- Usage decision (UD)
       |- Accept (go to unrestricted stock)
       |- Reject (go to blocked stock)
       |- Accept with deviation
```

**Integration touchpoint**:
- **QM**: inspection plan from material master.
- **MM**: stock type update (unrestricted vs blocked vs quality).
- **PP**: production order can release blocked neu inspection fail.

### Step 7: Goods Receipt from Production (backflush)

**Module**: PP + MM
**Document**: `MSEG-MBLNR` (movement type 101)
**Fiori app**: `Post Goods Receipt for Production Order` / auto khi order DLV

```
Goods Receipt (GR) tu production order
  |- Movement type 101 (GR from production)
  |- Yield quantity (default = order qty, co the partial)
  |- Scrap (vao scrap warehouse neu co)
  |- Stock increment (MARD)
  |- Batch create (neu material batch-managed)
  |- Trigger FI posting:
       Dr. Inventory (BSL)
       Cr. COGM (Cost of Goods Manufactured)
```

**Integration touchpoint**:
- **MM**: stock increment, batch master create.
- **QM**: neu QMM -> inspection lot link to GR.
- **FI-AR** (Make-to-Order): trigger billing neu day la MTO production.

### Step 8 (optional): Variance + Settlement

**Module**: CO
**Document**: Settlement rule
**Fiori app**: `Production Order Settlement`

```
Cuoi ky (period-end)
  |- Variance calculation (target vs actual cost)
       |- Production variance
       |- Scrap variance
       |- Lot size variance
       |- Mix variance
  |- Settlement to:
       |- Cost center (default)
       |- Profitability segment (CO-PA)
       |- WBS element (neu project)
       |- Material (WIP transfer to inventory)
```

**Integration touchpoint**:
- **CO-PA**: variance anh huong profitability.
- **MM**: inventory cost update theo actual.

## 3. Touchpoint matrix tong hop

| Step   | PP      | MM      | FI      | CO      | QM     | HR/SF  |
|--------|---------|---------|---------|---------|--------|--------|
| 1. Demand        | read    | read stock | - | - | - | - |
| 2. MRP run       | create planned | read stock | - | - | - | - |
| 3. Convert       | create prod order | read components | - | cost collector | - | - |
| 4. PO released   | status  | - | - | setup cost collector | inspection plan | - |
| 5. Goods issue   | - | stock decrement | COGM post | consumption | batch | - |
| 6. Confirmation  | time posting | - | actual cost | activity posting | - | labor time |
| 6b. Inspection   | - | stock type | - | - | inspection lot | - |
| 7. Goods receipt | TECO/DLV | stock increment | COGM clear | variance calc | UD link | - |
| 8. Settlement    | - | - | cost clear | variance settle | - | - |

## 4. Fiori apps lien quan

| Step | Fiori app                                |
|------|------------------------------------------|
| 1    | Manage Demand                          |
| 2    | Run MRP / Manage MRP Plans              |
| 3    | Convert Planned Orders                  |
| 4    | Production Order Cockpit                 |
| 5    | Post Goods Issue                         |
| 6    | Record Time / Confirm Operations        |
| 6b   | Manage Inspection Lots                   |
| 7    | Post Goods Receipt (Production)         |
| 8    | Production Order Settlement              |

## 5. Key tables

| Table         | Mo ta                              |
|---------------|--------------------------------------|
| `PLAF`        | Planned order                       |
| `AUFK`        | Production order header              |
| `AFPO`        | Production order item                |
| `AFVV`        | Production order operation           |
| `MAST` / `STPO` | BOM header / item                   |
| `PLKO` / `PLPO` | Routing header / operation          |
| `CRHD` / `CRVS` | Work center                        |
| `MSEG` / `MKPF` | Material document                   |
| `ACDOCA`      | Universal Journal (WIP, COGM, variance)|
| `COEP`        | CO line items (legacy - thay ACDOCA trong S/4) |
| `QALS` / `QAVE` | Inspection lot / UD                |

## 6. Skeleton RAP cho custom P2P-PP extension

Khi can custom logic trong production (vd custom approval, custom field on order):

```abap
" CDS - Custom view cho production order extension
define root view ZI_PROD_ORD_EXT as select from I_ProductionOrder
  association [0..1] to I_Material as _Material
    on $projection.Material = _Material.Material
{
  key ManufacturingOrder,
      Material,
      ProductionPlant,
      MfgOrderPlannedStartDate,
      MfgOrderPlannedEndDate,
      TotalQuantity,
      _Material
}
```

```abap
" Behavior Definition
managed with unmanaged save
define behavior for ZI_PROD_ORD_EXT alias ProdOrderExt
{
  create;
  update;
  delete;
  field ( readonly ) ManufacturingOrder, TotalQuantity;
  validation validateYield on save { field ActualYield; }
  action releaseOrder parameter ZA_RELEASE result [1] $self;
}
```

## 7. Common pitfalls

- BOM khong hieu luc (validity date khong khop production order date) -> production order khong lay duoc components.
- Routing khong co cho plant -> MRP khong tinh duoc lead time.
- Production order release truoc khi components available -> GI fail vi stock khong du.
- Backflush mode sai (fully-automatic vs manual) -> consume components sai qty.
- Inspection lot khong UD (usage decision) -> stock bi blocked, khong the su dung.
- Settlement rule missing -> production cost khong clear, WIP account imbalance.

## 8. Anti-pattern

- Tao custom table cho production order thay vi extend standard -> drift.
- Hardcode routing/work center trong code -> config change = code change.
- Skip time confirmation -> actual cost = zero, variance = phantom.
- Skip quality inspection (neu material QMM) -> quality audit fail.
- Manual GI (bo qua backflush) -> consumption khong chinh xac.
- Skip CO settlement -> WIP account accumulation, balance sheet sai.

## 9. Lien ket voi skill khac

- **Module consultants**: `sap-pp-consultant-cloud`, `sap-mm-consultant-cloud`,
  `sap-co-consultant-cloud`, `sap-qm-consultant-cloud`, `sap-ps-consultant-cloud`.
- **Integration knowledge notes**: `pm-integration-patterns` (production vs maintenance), `hcm-cloud-integration` (labor time).
- **Cookbook lien quan**: `end-to-end-order-to-cash` (MTO demand), `end-to-end-procure-to-pay` (external procurement).
- **Foundation**: `sap-extensibility`, `sap-clean-code`, `sap-authorization`, `sap-abap-sql`.
- **Released class**: `sap-released-classes` muc "RAP Runtime".

## 10. Nguon tham khao

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) - PP/MM/QM module.
- [`oisee/zllm`](https://github.com/oisee/zllm) - LangChain-lite for ABAP (custom AI workflow).
- [`google/ai-abap-assistant-sample`](https://github.com/google/ai-abap-assistant-sample) - Genie for SAP.
- SAP Help: MRP, Production Order, Quality Inspection, CO Settlement.
