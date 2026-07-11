---
name: sap-scaffold-context-summary
description: |
  Quy tac sinh summary compact giua cac layer (table -> I -> R -> behavior -> service) trong pipeline
  scaffold (sap-scaffold-rap, sap-scaffold-cds, sap-scaffold-rap-managed-unmanaged). Mooi layer
  generate ra full source nhung chi summary + cache path dua vao context de layer tiep theo xu ly.
  Dung khi scaffolding 3-layer RAP/CDS ma context dang phinh (full source cua nhieu object trong
  cung layer bi mat attention).
  KHONG dung cho layer don le (<4 object) - full source OK.
when_to_use: |
  "context scaffold phinh", "scaffold RAP nhieu object bi chong context",
  "sau khi generate xong layer X can compact de sang layer Y".
argument-hint: "[ticket-name]"
model: haiku
effort: low
---

# SAP Scaffold Context Summary - Compact giua cac layer scaffold

## Khi nao dung

- ✅ Dang scaffold 3-layer (table/I/R/behavior/service binding) cho >= 3 object cung ticket.
- ✅ Context phinh (>50% window) sau khi generate full source layer truoc.
- ✅ Can chuyen tiep tu layer N sang layer N+1 ma KHONG mat context cua source da generate.
- ❌ Scaffold 1 object don le (<3 layer phu thuoc) - full source vua du.
- ❌ Dang debug activation fail - GIU NGUYEN source de sua (uu tien 1, giong pattern trim).

## Quy tac kim (nguon: context-compression + filesystem-context)

> Sau moi layer scaffold, TRUOC KHI qua layer tiep theo, phai compact full source thanh summary
> + ghi ra cache file. Layer tiep theo chi load summary + reference, doc cache file chi tiet khi can.

AP dung 4 buoc theo thu tu, moi buoc la checkpoint:

### Buoc 1: Snapshot source objects da generate

Voi moi object vua generate (table, CDS view, behavior, class, service) trong layer N:

```
Ghi: <workspace>/.sap-abap-agent/sessions/<ticket>/scaffold/layer_<N>_<object>_<hash>.abap
```

`<hash>` = SHA1 8 char dau content. KHONG dung timestamp.

### Buoc 2: Sinh compact summary (KHONG paste full source)

Cho moi object trong layer, summary luon theo schema:

```
[Layer N] <object_name>
- Loai: [table | interface_view | consumption_view | mde | behavior | class | service_def | service_binding]
- File: <path_relative_to_session_dir>/layer_<N>_<object>_<hash>.abap
- Activate: <YES | NO | PENDING>
- Key field(s): <list_key_field>
- Fields (semantic): <3-10 field business-relevant, KHONG liet ke technical>
- Associations: <list_association_to_other_objects_this_layer_depends_on>
- Foreign references: <list_object_khac_can_tham_chieu_cai_nay>
- Notes: <1-2 dong dac biet (vd "strict(2)", "with draft", "alias X", "use association data")>
```

**Quy tac lua chon field "semantic"** (tu skill `sap-context-tool-result-trim`):
- Chi lay field co `@Semantics.*`, `@ObjectModel.*`, hoac la key
- BO annotation technical (`@AbapCatalog.foreignKey.specificationPosition`)
- BO field system (`CreatedBy`, `LastChangedBy`, khi co 1 object rieng cho ho so)

**Quy tac lua chon "foreign references"**: chi ghi khi layer N+1 can tham chieu field nay
(vd layer R can biet I view expose field X de map `mapping for`).

### Buoc 3: Ghi session manifest

Sau moi layer, ghi/cap nhat `sessions/<ticket>/scaffold/manifest.yaml`:

```yaml
ticket: <ticket_name>
session_dir: <absolute_path>
last_layer: 4  # 1=table, 2=I, 3=R, 4=C behavior, 5=service, 6=DCL
layers:
  - layer: 1
    objects:
      - name: ZTB_SUPPLIER
        type: table
        file: layer_1_ztb_supplier_a3f8b21c.abap
        activated: true
        summary: |
          [Layer 1] ZTB_SUPPLIER
          - Loai: table
          - File: ...
          - Fields semantic: SupplierKey, SupplierName, Country, ...
          - Foreign references: (none)
  - layer: 2
    objects:
      - name: ZI_SUPPLIER
        type: interface_view
        file: layer_2_zi_supplier_91a4b3cd.abap
        activated: true
        summary: |
          ...
      - name: ZR_SUPPLIER
        type: consumption_view
        file: layer_2_zr_supplier_87e6f1aa.abap
        activated: true
        summary: |
          ...
```

### Buoc 4: Tiep tuc layer N+1 chi load summary

Khi sinh layer N+1:
- Chi load `manifest.yaml` (toan bo summary) + summary inline cua moi object vao context.
- KHONG load full source cua object nao.
- Khi can field/annotation cu the -> doc `layer_<N>_<object>_<hash>.abap` voi line range.

## Vi du

### Scaffold 3 object (Supplier, PurchaseOrder, POItem) qua 6 layer

Sau khi xong layer 2 (I + R view cho 3 object), context co:
```
- 3 source ABAP (I view): ~600 token moi cai -> 1800 token
- 3 source ABAP (R view): ~800 token moi cai -> 2400 token
- Tom tat intermediate: ~200 token
- Full source KHONG load len context, da snapshot vao session
```

Manifest summary (~150 token):
```
[Layer 2] ZI_SUPPLIER       | Loai: interface_view | Activate: YES | Field semantic: SupplierKey,SupplierName,Country | Asso: _Address | Ref: (none)
[Layer 2] ZR_SUPPLIER       | Loai: consumption_view | Activate: YES | Field semantic: (ke thua ZI + UI annotations) | Asso: (ke thua) | Ref: ZBP_PO
[Layer 2] ZI_PURCHASEORDER  | Loai: interface_view | Activate: YES | Field semantic: POKey,VendorKey,PODate,NetAmount,Currency | Asso: _Item,_Vendor | Ref: ZI_SUPPLIER
[Layer 2] ZR_PURCHASEORDER  | Loai: consumption_view | Activate: YES | Field semantic: (ke thua ZI + @UI.lineItem...) | Asso: _Item (composition) | Ref: ZBP_PO
[Layer 2] ZI_POITEM         | Loai: interface_view | Activate: YES | Field semantic: ItemKey,POKey,MaterialKey,Quantity,UoM,NetAmount | Asso: _PO,_Material | Ref: ZI_PURCHASEORDER
[Layer 2] ZR_POITEM         | Loai: consumption_view | Activate: YES | ... | Asso: (ke thua) | Ref: ZBP_PO
```

Sang layer 3 (behavior R), chi can summary tren + doc cache khi can.

## Quy tac quan trong

1. **KHONG paste full source vao context** khi chuyen layer.
2. **Activate status la bat buoc** trong summary - agent layer N+1 can biet layer N da active hay chua.
3. **Foreign references giup layer N+1 biet can tham chieu gi** - chi ghi khi that su can.
4. **Hash phai on dinh** - cung source -> cung hash -> dedup tu dong.
5. **Khi fail activation**, GHI LAI source day du (khong summary) de debug - giong gotcha #4
   cua context-optimization (debug loop GIU NGUYEN error context).

## Tich hop

- Skill `sap-scaffold-rap` (cac buoc 2-9) - ap dung sau moi buoc sinh source.
- Skill `sap-scaffold-cds` (cac buoc 1-3) - ap dung sau moi buoc.
- Skill `sap-write-technical-spec` - summary co the reference tu TECHNICAL_SPEC de cross-check field.
- Skill `sap-context-tool-result-trim` - ket hop: trim full source output, ghi snapshot + summary.

## Luu y

- ⚠️ Tong disk cho session scaffold co the len 5-20MB (file .abap raw + manifest). Cleanup sau khi ticket xong (xem `sap-finish-ticket`).
- 💡 Nen dinh `<ticket>` consistent voi `out/<ticket>/` de cross-reference pipeline (INTAKE, TECHNICAL_SPEC, scaffold).
- 🔗 Ghi vao `LEARNING_PROGRESS.md` (skill `sap-daily-learner`): co can giam summary khi ticket nho (1-2 object) khong.