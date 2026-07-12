---
name: sap-write-technical-spec
description: |
  Tu INTAKE.md (da chuan hoa tu Function Spec), quyet dinh kien truc va sinh TECHNICAL_SPEC.md —
  buoc 2 trong pipeline "FS -> INTAKE -> TECHNICAL_SPEC -> scaffold code -> review -> test".
  Dung sau khi co INTAKE.md (tu skill sap-analyze-function-spec), truoc khi chay
  sap-scaffold-rap / sap-scaffold-cds.
  KHONG dung khi chua co INTAKE.md.
when_to_use: |
  "tu INTAKE.md tao technical spec", "chon pattern RAP hay CDS cho chuc nang nay",
  "quyet dinh kien truc cho ticket X".
argument-hint: "[duong dan INTAKE.md]"
model: sonnet
effort: high
tools: [Read, Write, Glob, Grep, WebSearch, WebFetch]
---

# SAP Write Technical Spec — INTAKE.md → TECHNICAL_SPEC.md

## Khi nao dung

- ✅ Da co INTAKE.md (xong skill `sap-analyze-function-spec`).
- ✅ Truoc khi chay `sap-scaffold-rap` / `sap-scaffold-cds`.
- ❌ Chua co INTAKE.md — chay `sap-analyze-function-spec` truoc.

## Quy trinh

### Buoc 1: Doc INTAKE.md

Focus vao: muc 1 (muc rui ro), muc 5 (yeu cau nghiep vu — pattern nao phu hop), muc 6 (cau hoi can
lam ro — CHAN neu con cau hoi CRITICAL chua tra loi).

### Buoc 2: Ap decision tree kien truc

Hoi tuan tu (chi tiet xem skill `sap-extensibility` cho phan mo rong, va bang duoi cho code moi):

1. Co can expose du lieu qua OData cho UI/tich hop khac khong?
   - Khong -> ABAP class thuong (`ZCL_*`) + function module (`ZF_*`) neu can. Dung template
     `reference/templates/abap-class/`.
   - Co -> tiep buoc 2.
2. Co can create/update/delete (CRUD) tu UI khong?
   - Khong (chi read) -> 3-layer CDS (I + R + C), service definition expose. Skill:
     `sap-scaffold-cds`.
   - Co (CRUD) -> RAP 3-layer + behavior. Tiep buoc 3.
3. Co can custom save logic (validate phuc tap, goi API ben ngoai) khong?
   - Khong -> **RAP Managed** tren R layer. Skill: `sap-scaffold-rap` (mac dinh managed).
   - Co -> **RAP Unmanaged**. Skill: `sap-scaffold-rap --unmanaged`. **Bat buoc co ADR**
     (`docs/decisions/`) giai thich ly do.
4. UI: Fiori Elements (annotation-driven, mac dinh) hay Custom SAPUI5 (chi khi KH yeu cau layout
   rieng)?

Ghi lai cau tra loi + ly do trong TECHNICAL_SPEC.md.

### Bang chon pattern nhanh

| Use case | Pattern | Skill |
|---|---|---|
| Bao cao in (PDF/Word), chi read | 3-layer CDS (I+R+C) | `sap-scaffold-cds` |
| List/Detail don gian, khong save | 3-layer CDS + Service Definition | `sap-scaffold-cds` |
| Form CRUD co ban | RAP Managed + Fiori Elements | `sap-scaffold-rap` |
| Form CRUD co validate custom | RAP Managed + validation trong behavior class | `sap-scaffold-rap` |
| Form CRUD save theo sequence custom | RAP Unmanaged | `sap-scaffold-rap --unmanaged` + ADR |
| Tich hop he thong ngoai (inbound/outbound API) | RAP Unmanaged/Managed + service binding | `sap-scaffold-rap` |

### Buoc 3: Chon CDS/API nguon (theo phan he) — BAT BUOC qua sap-ask-consultant

Cho tung entity/field trong INTAKE muc 5.4:

1. Xac dinh phan he (da ghi o INTAKE) -> dispatch qua skill `sap-ask-consultant` (routing engine —
   KHONG tu chon 1 agent consultant thu cong bang doan tu ten module). Ly do bat buoc qua routing
   engine thay vi tu chon: tu dong phat hien **module coupling** khi ticket dung nhieu phan he cung
   luc (vd Sales Order dung ca SD+FI, Purchase Order dung ca MM+FI — xem bang coupling trong
   `sap-ask-consultant`) va dispatch song song, tranh bo sot goc nhin 1 phan he. Cau hoi mau: "CDS
   view/field nao chuan cho nghiep vu <trich muc 5.4 INTAKE>". Ket hop `sap-docs-researcher` /
   skill `sap-cds-kb` de tra cuu ky thuat (field/association) sau khi da co huong tu consultant.
2. Uu tien CDS `I_*` (VDM interface) da released, khop field FS yeu cau, theo dung goi y cua
   consultant — KHONG tu doan CDS view khi consultant chua tra loi.
3. **Verify released** cho dung version S/4HANA Cloud dang dung (SAP ra 4 ban/nam — ten/API doi
   theo release) — dung `sap-docs-researcher` (tool `sap_search_objects`) hoac View Browser trong
   Eclipse ADT.
4. Neu view **chua released** hoac **thieu field** -> tra `api.sap.com`/`help.sap.com`, hoi
   `sap-docs-researcher`. Neu van khong co -> ghi `[Unverified]` va dua vao "can lam ro".
5. Ghi vao TECHNICAL_SPEC: CDS base + released state + nguon. KHONG bia ten view/field.

### Buoc 4: Liet ke object can tao

Theo pattern da chon, liet ke (dung dung quy uoc trong skill `sap-clean-code`):
- Database table(s): `ZTB_*`
- CDS interface view: `ZI_*`
- CDS consumption/reuse view: `ZR_*` / `ZC_*`
- Behavior definition + implementation: `ZBP_*`
- Service definition/binding: `ZUI_*` (UI) hoac `ZAPI_*` (API machine-to-machine)
- ABAP class helper (neu co): `ZCL_*`
- ABAP Unit test class(es)
- Metadata extension (Fiori): `.MDE`

Checklist nay phai cover **TAT CA** field trong INTAKE muc 5.4.

**Xac nhan 2 chieu (bat buoc, khong duoc bo qua)**: Sau khi liet ke xong object/field o tren, gui
lai TOAN BO danh sach CDS/field/object du kien cho **cung consultant** da hoi o Buoc 3 (qua
`sap-ask-consultant`, ghi ro day la buoc xac nhan tiep noi cho ticket dang lam, khong hoi lai tu
dau) de hoi: "danh sach nay co dung y nghia nghiep vu <phan he> khong, co thieu/thua field nao so
voi nghiep vu that khong". **Chi chot TECHNICAL_SPEC.md sau khi consultant xac nhan.** Day la buoc
"2 AI trao doi voi nhau" (technical-spec-writer <-> module consultant) de bat loi chon sai muc
dich — vd chon nham grain CDS (header thay vi item), thieu field bat buoc theo nghiep vu, dung
nham CDS view khac phan he — TRUOC khi scaffold code that (sua sau khi da scaffold ton kem hon
nhieu vi phai sua lai Table/CDS/Behavior da activate).

### Buoc 5: Dinh nghia behavior chi tiet (neu la RAP)

- **Draft**: co/khong (mac dinh co neu la List/Object Page).
- **Authorization**: instance-based hay role-based.
- **Numbering**: internal (SAP tu sinh — nho khai `field ( numbering : managed )` neu key la UUID)
  hay external (KH cap).
- **Validation**: field bat buoc + rule.
- **Determination**: field nao auto-fill khi save/create.
- **Action**: action nao (approve, reject, print...).

### Buoc 6: UI design (neu co Fiori Elements)

List Report: cot nao, sort mac dinh, filter nao. Object Page: facet nao, field group nao.

### Buoc 7: Test plan

Tu edge case trong INTAKE muc 6 + 5.6: happy path (tao/sua/xoa), validation tung field mandatory,
action (approve/reject), authorization (role khac nhau thay action khac nhau).

### Buoc 8: Ghi file

Output: `out/<ten-ticket>/TECHNICAL_SPEC.md` (`out/` la thu muc local per-user, KHONG nam trong
repo — xem skill `sap-doc-to-md` de biet duong dan day du). Neu co quyet dinh kien truc quan
trong (managed vs unmanaged, released object moi, Fiori vs custom UI5...) -> de xuat tao ADR
trong `docs/decisions/`.

## Template TECHNICAL_SPEC.md

```markdown
# TECHNICAL_SPEC: <ten ticket> / <ten BO> / v<phien ban>

## Quyet dinh kien truc
| Cau hoi | Tra loi | Ly do |
|---|---|---|
| Co OData? | Co/Khong | |
| Pattern | RAP Managed/Unmanaged/Class thuong | |
| UI | Fiori Elements/Custom SAPUI5/Khong | |
| Draft | Co/Khong | |
| Numbering | Internal/External | |
| Authorization | Instance-based/Role-based/Ca hai | |

## Object can tao
| Object | Ten | Loai | File path (abapGit) |
|---|---|---|---|

## Behavior definition (pseudo)
\`\`\`abap
managed;
implementation in class zbp_<object> unique;
...
\`\`\`

## Test plan
-

## ADR can tao
- [ ] ADR-XXXX: <ly do chon pattern nay>

## Reference
- INTAKE.md: out/<ticket>/INTAKE.md
```

## Reference

- Skill `sap-extensibility` — bac thang extensibility chung.
- Skill `sap-clean-code` — quy uoc dat ten 3-layer CDS.
- Skill `sap-scaffold-rap` / `sap-scaffold-cds` — buoc tiep theo.
- Skill `sap-abap-sql` — ABAP SQL, window functions, AMDP cho quyet dinh kien truc.
- Skill `sap-odata-service` — OData V4/V2 patterns, RAP service binding quyet dinh.
- Skill `sap-badi-enhancement` — Cloud BAdI patterns khi can custom logic.
- Skill `sap-rap-events` — RAP business events cho event-driven architecture.
- Skill `sap-ask-consultant` — **bat buoc** dung o Buoc 3 (chon CDS/API nguon) va Buoc 4 (xac nhan
  2 chieu) thay vi tu chon/tu doan agent consultant.
- Skill `sap-deployment-target` — **buoc tiep theo bat buoc** sau khi TECHNICAL_SPEC.md hoan
  tat: xac dinh package deploy tren he thong that + rao chan an toan, TRUOC khi chay
  `sap-scaffold-rap`/`sap-scaffold-cds`/`sap-cloud-dictionary`.
