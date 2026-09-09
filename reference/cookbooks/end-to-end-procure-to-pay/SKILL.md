---
name: end-to-end-procure-to-pay
description: End-to-end cookbook cho quy trinh **Procure-to-Pay (P2P)** tren S/4HANA Cloud - tu PR den payment cho vendor. Cross-module (MM -> FI -> TR -> CO). Dung khi contributor can hieu flow procurement toan dien hoac scaffold scenario P2P moi. Khac voi cac module reference rieng (sap-mm-cloud, sap-fi-cloud...) vi tap trung vao **integration touchpoint**.
effort: low
model: haiku
---

# End-to-End Cookbook - Procure-to-Pay (P2P)

Cookbook di tu **purchase requisition -> vendor payment** xuyen qua MM/FI/TR/CO. Tuong tu
cookbook O2C nhung nguoc huong: hang di vao kho (inbound), tien di ra (vendor payment).

## 1. Tong quan quy trinh

```
[Purchase  ] -> [Purchase  ] -> [Goods    ] -> [Invoice  ] -> [Vendor  ] -> [Bank
[Requisition]    [Order    ]    [Receipt   ]    [Receipt   ]    [Payment ]    [Reconcile]
   MM step 1     MM step 2      MM step 3     FI step 4       TR step 5    TR step 6
```

## 2. Chi tiet tung step

### Step 1: Purchase Requisition (MM)

**Module**: MM
**Document**: `EBAN-BANFN` (PR number)
**Fiori app**: `Create Purchase Requisitions`
**Released API**: `API_PURCHASE_REQUISITION_SRV_2`

```
Tao PR (PR-2026-001)
  |- Item (1+ items, Material MARA-MATNR + qty)
  |- Delivery date (requested)
  |- Plant + Storage location
  |- Source list / quota arrangement (optional)
  |- Account assignment (cost center / WBS / asset)
  |- Requestor (employee)
```

**Integration touchpoint**:
- **MM**: source list / info record lookup (`EINA` / `EORD`).
- **PM**: trigger neu la spare part cho equipment (optional).
- **PS/CO**: account assignment validate.

**Auto trigger** (optional):
- Neu qty < threshold -> tu dong convert sang PO (configurable).
- Neu co source list -> suggest vendor.

### Step 2: Purchase Order (MM)

**Module**: MM
**Document**: `EKKO-EBELN` (PO number)
**Fiori app**: `Manage Purchase Orders`
**Released API**: `API_PURCHASE_ORDER_SRV_2`

```
Tao PO (PO-2026-001) - convert tu PR hoac direct
  |- Reference PR (PR-2026-001)
  |- Vendor (BP role Supplier)
  |- Item (Material + qty + price)
  |- Inco terms (vd DAP - Delivered at Place)
  |- Payment terms
  |- Shipping instructions
  |- Confirmation control (vendor confirm schedule)
  |- Output (email PO cho vendor)
```

**Integration touchpoint**:
- **MM**: vendor info record (`LFA1`/`EINA`).
- **FI**: vendor master (BP role Supplier).
- **Output Mgmt**: PDF PO qua Adobe Form cho vendor.

**Approval workflow**:
- Release strategy (qua workflow app).
- Auto-approve neu value < threshold.

### Step 3: Goods Receipt (MM)

**Module**: MM
**Document**: `MSEG-MBLNR` (material document) + `MKPF-MBLNR`
**Fiori app**: `Post Goods Receipt` / `Post Goods Receipt for Purchase Order`
**Released API**: `API_GOODS_RECEIPT_SRV` (nếu có)

```
Tao GR (GR-2026-001) tu PO
  |- Reference PO (PO-2026-001)
  |- Delivery note (vendor's delivery note number)
  |- Quantity (co the < PO qty - partial)
  |- Batch (neu material co batch management)
  |- Storage location (co the khac PO neu vendor confirm truoc)
|
| Material document (MSEG)
  |- Update stock (MARD-LABST)
  |- Quality inspection (neu material QMM-managed)
  |- Batch master update
  |- Trigger FI posting:
      Dr. Inventory (BSL inventory account)
      Cr. GR/IR (Goods Receipt / Invoice Receipt clearing account)
```

**Integration touchpoint**:
- **FI**: GR/IR clearing account update.
- **QM**: neu material co inspection plan -> quality inspection task.
- **EHS**: neu material la hazardous -> EHS compliance check.
- **EWM** (decentralized): warehouse task (nhan hang vao bin).

### Step 4: Invoice Receipt (FI + MM)

**Module**: FI (AP) + MM (invoice verification)
**Document**: `BKPF-BELNR` (accounting doc) + `RSEG-BELNR` (invoice doc MM)
**Fiori app**: `Create Supplier Invoice` / `Post Supplier Invoices`
**Released API**: `API_SUPPLIER_INVOICE_SRV_2`

```
Tao invoice (INV-2026-001) tu PO
  |- Reference PO (PO-2026-001)
  |- Vendor invoice number (vendor's invoice)
  |- Amount + tax
  |- Quantity (verify match voi GR)
  |- Payment terms (copy tu PO)
  |- G/L account (neu khong match PO)
|
| 3-way match (MM + FI):
  |- PO qty == GR qty == Invoice qty?
  |- PO price == Invoice price?
  |- Neu khong match -> blocking reason
|
| Accounting document (auto-post)
  |- Dr. GR/IR clearing (balance lai)
  |- Dr/Cr. Tax input (input tax)
  |- Cr. Vendor (AP, BP role Supplier)
  |- Cr. Price variance (neu khong match PO)
```

**Integration touchpoint**:
- **FI-AR/AP**: vendor balance increase.
- **MM**: invoice history update.
- **TR**: payment terms + cash discount calculate.
- **QM**: neu material o inspection -> block invoice.

**Common errors**:
- Quantity mismatch (3-way match fail).
- Price different from PO (vendor changed price).
- Missing GR -> GR/IR account imbalance.
- Vendor tax number invalid.

### Step 5: Vendor Payment (FI + TR)

**Module**: FI (AP clear) + TR (bank)
**Document**: `BKPF-BELNR` (clearing doc)
**Fiori app**: `Manage Supplier Payments` / `Payment Proposal`
**Released API**: khong co public (security-sensitive)

```
Payment run (auto scheduled hoac manual)
  |- Tao proposal (chon vendor + invoice + bank)
  |- Bank file (XML/CSV theo format bank)
  |- Bank process payment (SWIFT / local)
  |- Bank statement (upload)
  |- Auto-clear invoice (payment - cash discount)
|
| Accounting document (clearing)
  |- Dr. Vendor (AP, BP role Supplier)
  |- Cr. Bank (BSL bank account)
  |- Cr/Cr. Cash discount (expense)
```

**Integration touchpoint**:
- **TR**: bank connectivity (file-based / API / SAP MBC).
- **FI-AP**: vendor balance reduce.
- **CO**: cash discount impact expense.

### Step 6: Bank Reconciliation (TR + FI)

Tuong tu O2C step 6 - match bank statement voi payment file.

## 3. Touchpoint matrix tong hop

| Step   | MM      | FI      | TR     | CO/PS   | QM     |
|--------|---------|---------|--------|---------|--------|
| 1. PR         | create   | - | - | acc assn | - |
| 2. PO         | create   | vendor master | - | - | - |
| 3. GR         | GR posting | GR/IR update | - | - | inspection |
| 4. Invoice    | 3-way match | AP + tax | terms of pmt | - | block nếu QM |
| 5. Payment    | - | clear AP | bank file | - | - |
| 6. Reconcile  | - | close open item | statement match | - | - |

## 4. Fiori apps lien quan

| Step | Fiori app                                |
|------|------------------------------------------|
| 1    | Create Purchase Requisitions              |
| 2    | Create Purchase Orders / Manage PO       |
| 3    | Post Goods Receipt for PO                |
| 4    | Create Supplier Invoice                  |
| 5    | Manage Supplier Payments / Payment Run   |
| 6    | Reconciliation Worklist                  |

## 5. Key tables

| Table         | Mo ta                              |
|---------------|--------------------------------------|
| `EBAN` / `EBKN` | PR header + account assignment      |
| `EKKO` / `EKPO` | PO header + item                    |
| `MSEG` / `MKPF` | Material document                   |
| `RSEG` / `RBKP` | Vendor invoice (MM-side)            |
| `BKPF` / `BSEG` | Accounting doc                       |
| `LFA1` / `LFB1` | Vendor master                       |
| `ACDOCA`      | Universal Journal                    |
| `ACDOCA` (GR/IR sub-ledger) | GR/IR clearing account |

## 6. Skeleton RAP cho custom P2P extension

```abap
" CDS - Custom approval cho PO
define root view ZI_PO_APPR as select from I_PurchaseOrder
  association [0..1] to I_Supplier as _Vendor on $projection.Supplier = _Vendor.Supplier
{
  key PurchaseOrder,
      Supplier,
      TotalAmount,
      OverallStatus,
      _Vendor
}
```

```abap
" Behavior - Approval workflow
managed implementation in class ZBP_I_PO_APPR unique;
define behavior for ZI_PO_APPR alias POAppr
{
  create ( precheck );
  update;
  delete;
  field ( readonly ) PurchaseOrder, TotalAmount;
  action approve parameter ZA_APPROVE result [1] $self;
  action reject parameter ZA_REJECT result [1] $self;
  determination setDefaultApproval on modify { create; }
}
```

## 7. Common pitfalls

- 3-way match fail (quantity/price mismatch) - block invoice.
- Vendor master khong co payment terms -> payment run fail.
- GR/IR account khong cleared -> balance sheet imbalance.
- Output PO sai format -> vendor khong hieu.
- Skip approval workflow -> spend drift.

## 8. Anti-pattern

- Tao custom table cho P2P thay vi extend standard -> drift.
- Direct GR/IR posting (bo qua MM standard) -> inventory sai.
- Skip quality inspection (neu material QMM) -> quality audit fail.
- Hardcode vendor bank detail trong PO -> vendor change bank = sai.
- Manual payment (khong qua payment run) -> bank file sai format.

## 9. Lien ket voi skill khac

- **Module consultants**: `sap-mm-consultant-cloud`, `sap-fi-consultant-cloud`,
  `sap-tr-consultant-cloud`, `sap-pm-consultant-cloud` (spare parts).
- **Integration knowledge notes**: `ca-integration-patterns` (BP vendor master), `tr-cloud-integration`
  (bank payment).
- **Cookbook lien quan**: `end-to-end-order-to-cash` (outbound, doi xung P2P).
- **Foundation**: `sap-extensibility`, `sap-clean-code`, `sap-authorization`, `sap-abap-sql`.

## 10. Nguon tham khao

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) - MM/FI module.
- SAP Help: P2P scenario, S/4HANA Universal Journal (ACDOCA).
