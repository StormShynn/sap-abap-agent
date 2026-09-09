---
name: end-to-end-order-to-cash
description: End-to-end cookbook cho quy trình **Order-to-Cash (O2C)** tren S/4HANA Cloud - tu quotation den payment. Cross-module (SD -> MM -> FI -> TR -> CO). Dung khi contributor can hieu flow toan dien hoac scaffold scenario O2C moi. Khac voi cac module reference rieng (sap-sd-cloud, sap-fi-cloud...) vi tap trung vao **integration touchpoint** giua cac module.
effort: low
model: haiku
---

# End-to-End Cookbook - Order-to-Cash (O2C)

Knowledge note cookbook di tu **quotation -> payment** xuyen qua SD/FI/MM/TR/CO. Khac voi
knowledge notes khac (tap trung vao 1 module), cookbook nay tap trung vao **integration
touchpoint** giua cac module va **sequence ID** cua tung document.

## 1. Tong quan quy trinh

```
[Quotation] -> [Outbound SO] -> [Delivery + GI] -> [Billing] -> [Payment] -> [Bank Reconcile]
   SD step 1    SD step 2       SD/MM step 3    SD/FI step 4     TR/FI step 5    TR step 6
```

## 2. Chi tiet tung step

### Step 1: Sales Quotation (SD)

**Module**: SD
**Document**: `VBAK-VBELN` (quotation number)
**Fiori app**: `Create Sales Quotations`
**Released API**: `API_SALES_QUOTATION_2` (OData V4)

```
Tao quotation (VD-Q-2026-001)
  |- Item (1+ items, link toi Material MARA-MATNR)
  |- Customer (BP role Customer)
  |- Pricing procedure (tinh gia)
  |- Inco terms (delivery conditions)
  |- Validity date (expiry)
```

**Integration touchpoint**:
- **MM**: check material availability (`MARC-MMSTD`).
- **FI**: customer credit check (qua `UKM_*` tables).

**Common errors**:
- Material khong released cho BP/Customer -> fail khi save.
- Pricing procedure khong co cho country/region.
- Customer bi credit block -> quotation van tao nhung khong convert duoc sang SO.

### Step 2: Sales Order (SD)

**Module**: SD
**Document**: `VBAK-VBELN` (sales order)
**Fiori app**: `Create Sales Orders` / `Manage Sales Orders`
**Released API**: `API_SALES_ORDER_2` (OData V4)

```
Tao sales order (SO-2026-001) - convert tu quotation
  |- Reference quotation (VD-Q-2026-001)
  |- Item (copy tu quotation, co the sua qty)
  |- Delivery date (schedule line)
  |- Payment terms (terms of payment key)
  |- Inco terms
  |- Plant (cho delivery)
```

**Integration touchpoint**:
- **MM**: plant stock check (`MARD-LABST`).
- **PP**: availability check qua ATP (Available-to-Promise).
- **FI**: credit check lai (neu customer balance doi).

**Trigger output**:
- Order confirmation (email/print cho customer) - qua Output Management.

### Step 3: Outbound Delivery (SD + MM)

**Module**: SD (delivery doc) + MM (goods issue)
**Document**: `LIKP-VBELN` (delivery) + `MSEG-MBLNR` (material document)
**Fiori app**: `Create Outbound Deliveries` / `Manage Outbound Deliveries`
**Released API**: `API_OUTBOUND_DELIVERY_SRV_2`

```
Tao outbound delivery (DL-2026-001) tu sales order
  |- Reference SO (SO-2026-001)
  |- Pick quantity (default = SO qty)
  |- Batch (neu material co batch management)
  |- Storage location
  |- Ship-to address
|
| Goods Issue (PGI - Post Goods Issue)
  |- Trigger MM document (MSEG-MBLNR)
  |- Update stock (MARD / MCHB)
  |- Trigger FI posting (cost of goods sold)
```

**Integration touchpoint**:
- **MM**: stock decrement (`MARD-LABST`).
- **EWM** (neu decentralized): warehouse task execution.
- **FI**: COGS (Cost of Goods Sold) posting tu dong.
- **CO**: settlement ve profitability segment (qua CO-PA).

### Step 4: Billing (SD + FI)

**Module**: SD (billing doc) + FI (accounting doc)
**Document**: `VBRK-VBELN` (billing) + `BKPF-BELNR` (accounting)
**Fiori app**: `Create Billing Documents`
**Released API**: `API_BILLING_DOCUMENT_SRV_2`

```
Tao billing (BL-2026-001) tu outbound delivery
  |- Reference delivery (DL-2026-001)
  |- Pricing (re-run tu SO procedure)
  |- Tax code (automatic tu country + BP tax category)
  |- Payment terms (copy tu SO)
  |- Output (PDF invoice -> customer email)
|
| Accounting document (FI document) auto-post
  |- Dr. Customer (sub-ledger, BP role Customer)
  |- Cr. Revenue (FI revenue account)
  |- Dr/Cr. Tax (depending on input/output tax)
  |- Cr. Cost of Goods Sold (neu da PGI o step 3)
```

**Integration touchpoint**:
- **FI**: auto-posted AR + revenue + tax (3-line standard).
- **CO-PA**: profitability segment update (revenue + COGS).
- **TR**: cash discount calculation (terms of payment).
- **Output Mgmt**: PDF invoice qua Adobe Form.

**Common errors**:
- Tax code khong tim thay cho combination country + tax category.
- Customer tax number invalid -> block billing.
- Revenue account khong configured cho sales org / division.

### Step 5: Customer Payment (FI + TR)

**Module**: FI (AR) + TR (bank reconciliation)
**Document**: `BKPF-BELNR` (clearing document)
**Fiori app**: `Manage Customer Payments` / `Reconciliation`
**Released API**: khong co released API public cho payment upload (security-sensitive)

```
Customer pays invoice (qua bank transfer, cheque, etc.)
  |- Bank statement upload (SWIFT MT940 / EBICS)
  |- Bank reconciles voi open AR items
  |- Manual clear (neu auto-match fail)
  |- Auto-write-off discount neu trong discount period
|
| Accounting document (FI clearing)
  |- Dr. Bank (BSL bank account)
  |- Cr. Customer (AR)
  |- Cr/Cr. Cash discount (income)
```

**Integration touchpoint**:
- **TR**: bank statement auto-import.
- **FI-AR**: customer balance reduce.
- **CO-PA**: cash discount anh huong profitability.

### Step 6: Bank Reconciliation (TR + FI)

**Module**: TR (bank statement) + FI (reconcile)
**Fiori app**: `Reconciliation Worklist`
**Released API**: khong public (noi bo SAP)

```
Daily bank statement received
  |- Match payment voi open AR/AP items
  |- Manual assign neu ambiguous
  |- Post unmatched items (suspense account)
|
| Reconciliation report
  |- Cleared items
  |- Open items
  |- Discrepancies (alert)
```

## 3. Touchpoint matrix tong hop

| Step   | SD      | MM      | FI      | TR     | CO-PA   |
|--------|---------|---------|---------|--------|---------|
| 1. Quotation | create   | check stock | credit check | - | - |
| 2. SO         | create   | ATP check | credit recheck | - | plan |
| 3. Delivery  | create   | GI posting | COGS post | - | settlement |
| 4. Billing    | create   | - | AR + revenue + tax | - | actual |
| 5. Payment    | -        | - | clear AR | bank import | discount |
| 6. Reconcile  | -        | - | close open item | statement match | - |

## 4. Fiori apps lien quan

| Step | Fiori app                                |
|------|------------------------------------------|
| 1    | Create Sales Quotations                   |
| 2    | Create Sales Orders / Manage Sales Orders |
| 3    | Create Outbound Deliveries / PGI          |
| 4    | Create Billing Documents                  |
| 5    | Manage Customer Lines                     |
| 6    | Reconciliation Worklist                   |

## 5. Key tables (custom field/extension)

| Table         | Mo ta                              |
|---------------|--------------------------------------|
| `VBAK` / `VBAP` | Sales order header / item            |
| `LIKP` / `LIPS` | Delivery header / item              |
| `VBRK` / `VBRP` | Billing header / item               |
| `BKPF` / `BSEG` | Accounting doc header / line         |
| `ACDOCA`      | Universal Journal (S/4HANA)           |
| `MSEG`        | Material document                     |
| `MARD`        | Storage location stock                |

**Luu y S/4HANA**: nhieu bang aggregate vao `ACDOCA` (Universal Journal) de consolidate FI + CO.

## 6. Skeleton RAP cho custom O2C extension

Khi can extend O2C (vd custom approval, custom field, custom logic), dung RAP:

```abap
" CDS - Interface View
define root view ZI_SO_EXT as select from I_SalesOrder
  association [0..1] to I_Customer as _Customer
    on $projection.SoldToParty = _Customer.Customer
{
  key SalesOrder,
      SoldToParty,
      _Customer
}
```

```abap
" Behavior Definition
managed with unmanaged save
define behavior for ZI_SO_EXT alias SalesOrderExt
{
  create;
  update;
  delete;
  field ( readonly ) SalesOrder;
  validation validateCustom on save { field CustomField; }
}
```

## 7. Common pitfalls

- Quen **credit check** khi convert quotation -> SO (sales van OK, payment sau fail).
- Hardcode plant ma khong check storage location -> fail khi GI.
- Tax code thieu cho combination moi -> billing block.
- Output form sai template -> customer nhan invoice sai format.
- Skip PGI (gia lap delivery complete) -> stock report sai.
- Bank reconciliation manual hoan toan -> de miss payment.

## 8. Anti-pattern

- Tao custom table cho O2C thay vi extend standard -> drift sau nay.
- Hardcode document type theo plant -> config change = code change.
- Skip CO-PA settlement -> profitability report sai.
- Output email direct tu code -> khong qua Output Mgmt = khong audit.
- Bypass customer credit check khi sales force yeu cau.

## 9. Lien ket voi skill khac

- **Module consultants**: `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud`,
  `sap-mm-consultant-cloud`, `sap-tr-consultant-cloud`.
- **Integration knowledge notes**: `ca-integration-patterns` (Output Mgmt, BRF+), `tr-cloud-integration`
  (bank reconciliation).
- **Foundation**: `sap-extensibility`, `sap-clean-code`, `sap-authorization`, `sap-abap-sql`.
- **Released API**: `sap-released-classes` muc "RAP Runtime" + "Email & Communication".

## 10. Nguon tham khao

- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) - SD/FI/MM module.
- [`oisee/zllm`](https://github.com/oisee/zllm) - LangChain-lite for ABAP (custom AI workflow).
- [`google/ai-abap-assistant-sample`](https://github.com/google/ai-abap-assistant-sample) - Genie
  for SAP (AI-assisted code).
- SAP Help: O2C scenario, S/4HANA Universal Journal (ACDOCA).
