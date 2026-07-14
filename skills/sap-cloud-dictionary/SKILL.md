---
name: sap-cloud-dictionary
description: |
  Tao Domain, Data Element, Database Table cho ABAP Cloud (S/4HANA Cloud, BTP Steampunk).
  Dung khi can tao moi dictionary objects (SE11-style) trong ADT, hoac sinh code DEFINE TABLE/
  DEFINE DOMAIN/DEFINE DATA ELEMENT ABAP Cloud. KHONG dung cho CDS Table Entity (dung sap-scaffold-cds),
  KHONG dung de sua object standard SAP.
when_to_use: |
  "tao domain moi", "tao data element", "tao bang DB ABAP Cloud",
  "DEFINE TABLE syntax", "DEFINE DOMAIN syntax", "DEFINE DATA ELEMENT syntax",
  "dictionary object ABAP Cloud", "tao table co admin field", "DDIC ABAP Cloud".
argument-hint: "[loai object: domain|data-element|table + ten + field list]"
model: sonnet
effort: high
tools: [Read, Write, Edit, Glob, Bash]
---
# SAP Cloud Dictionary — Tao Domain, Data Element, Database Table

## Khi nao dung

- ✅ Can tao **Domain** moi (dinh nghia kieu du lieu + value range).
- ✅ Can tao **Data Element** moi (semantic label + kieu cho field).
- ✅ Can tao **Database Table** (transparent table) trong ABAP Cloud.
- ✅ Can tao table co **administrative fields** (draft-enabled cho RAP).
- ❌ Read-only CDS view -> dung `sap-scaffold-cds`.
- ❌ Full RAP BO (table + CDS + behavior) -> dung `sap-scaffold-rap`.
- ❌ Sua table standard SAP -> khong duoc phep tren ABAP Cloud.

## Output

Moi object la 1 file source code ABAP Cloud duoc sinh ra trong `out/<ticket>/src/`
(`out/` la thu muc local per-user, KHONG nam trong repo):

```
out/<ticket>/src/
├── package.devc.xml            — Package definition (bat buoc cho abapGit)
├── abapgit.xml                 — abapGit manifest
└── zdict/
    ├── zdom_<ten>.asdom        — Domain
    ├── zde_<ten>.asde          — Data Element
    └── ztb_<ten>.tabl.xml      — Database Table (abapGit XML format)
```

Neu dung **CDS Table Entity** (khuyen nghi cho ABAP Cloud moi):
```
    └── ztb_<ten>.asddls        — CDS Table Entity (DDL source)
```

---

## Quy trinh

### Buoc 0: Kiem tra reuse TRUOC khi tao moi (bat buoc)

DUNG tao Domain/Data Element/Table moi khi chua kiem tra co the tai su dung object chuan SAP hoac
object Z/Y da co san hay khong:

1. **Data Element chuan SAP**: tra ADT (Data Element search) hoac hoi agent consultant phan he
   tuong ung (qua `sap-ask-consultant`) — uu tien Data Element chuan (khong prefix `Z`/`Y`) neu
   khop dinh dang/nghiep vu (vd `MATNR`, `KUNNR`).
2. **Object Z/Y co san trong he thong**: neu da chay `sap-bootstrap-system-context`, doi chieu
   ket qua cache (`system-context.md`) xem co Domain/Data Element cung nghiep vu da ton tai chua —
   tranh tao trung (vd 2 Domain khac ten nhung cung dinh nghia "trang thai Active/Inactive").
3. Chi tao moi khi ca 2 buoc tren deu khong tim thay object phu hop.

### Buoc 1: Xac dinh loai object can tao

| Tinh huong | Loai object | Khuyen nghi |
|------------|-------------|-------------|
| Can reusable value range (enum) | **Domain** (+ Data Element) | Bat buoc khi co `fixedValues` tu 2+ Data Element dung chung |
| Can field label + doc trong UI | **Data Element** (co/khong Domain) | Uu tien built-in type (`abap.int4`, `abap.char(40)`) neu khong can Domain |
| Can persist data | **Database Table** (classic DDIC) | Cach cu, van co hieu luc |
| Can persist cho RAP managed BO | **CDS Table Entity** | Cach moi, SAP khuyen nghi |
| Can projection/consumption | CDS View (I/C/R) | Xem `sap-scaffold-cds` hoac `sap-scaffold-rap` |

### Buoc 2: Domain

Domain = loai ky thuat co ban: kieu du lieu, do dai, value range.

#### Source code ABAP Cloud (`define domain`)

```abap
@EndUserText.label : 'Domain Name - Description'
define domain zdom_<ten> {
  type abap.char( 1 );
  value range:
    'A'  : 'Active',
    'I'  : 'Inactive',
    'S'  : 'Suspended';
}
```

**Cac kieu ABAP built-in type cho Domain (`type ...`):**

| Kieu | Mo ta | Vi du |
|------|-------|-------|
| `abap.char( <n> )` | Chuoi ky tu | `abap.char( 40 )` |
| `abap.numc( <n> )` | Chuoi so | `abap.numc( 10 )` |
| `abap.int4` | So nguyen 4 byte | `abap.int4` |
| `abap.int8` | So nguyen 8 byte | `abap.int8` |
| `abap.dec( <len>, <dec> )` | So thap phan | `abap.dec( 16, 2 )` |
| `abap.dats` | Ngay (YYYYMMDD) | `abap.dats` |
| `abap.tims` | Gio (HHMMSS) | `abap.tims` |
| `abap.utclong` | Timestamp (UTC) | `abap.utclong` |
| `abap.string` | Chuoi dai | `abap.string` |
| `abap.xstring` | Hex binary | `abap.xstring` |
| `abap.clnt` | Client | `abap.clnt` |
| `abap.lang` | Language key | `abap.lang` |
| `abap_boolean` | Boolean (X/space) | `abap_boolean` |

**Luu y**: Tren ABAP Cloud, cac kieu `abap_boolean`, `abap.char`, `abap.numc` la built-in,
KHONG can Domain rieng neu chi dung 1-2 field. Domain chi can khi co value range dung chung.

### Buoc 3: Data Element

Data Element = kieu ngon ngu: label + kieu ky thuat (domain/built-in).

#### Cach 1: Dung built-in type (khong Domain)

```abap
@EndUserText.label : 'Material Number (40 char)'
@DataClassification.level : #BUSINESS_INFORMATION
define data element zde_matnr {
  type abap.char( 40 );
}
```

#### Cach 2: Dung Domain

```abap
@EndUserText.label : 'Status Value'
@DataClassification.level : #BUSINESS_INFORMATION
define data element zde_status {
  type zdom_status;     // Domain da tao o Buoc 2
}
```

#### Annotations bat buoc cho Data Element

| Annotation | Mo ta | Gia tri thuong dung |
|------------|-------|---------------------|
| `@EndUserText.label` | **Bat buoc** — Mo ta field | `'Material Number'` |
| `@DataClassification.level` | **Bat buoc** — Phan loai bao mat | `#BUSINESS_INFORMATION`, `#CRITICAL`, `#PERSONAL`, `#NONE` |
| `@AbapCatalog.enhancement.category` | Cho phep enhancement | `#EXTENSIBLE_ANY`, `#NOT_EXTENSIBLE` |

> ⚠️ `@DataClassification.level` la **bat buoc** tren ABAP Cloud. Thieu -> ATC bao loi.

#### Vi du day du

```abap
@EndUserText.label : 'Currency Amount'
@DataClassification.level : #BUSINESS_INFORMATION
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
define data element zde_amount {
  type abap.dec( 23, 2 );
}
```

### Buoc 4: Database Table (classic DDIC)

#### Source code (`define table`)

```abap
@EndUserText.label : 'Table Description'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table ztb_<ten> {
  key client          : abap.clnt not null;
  key uuid            : sysuuid_x16 not null;
  name                : zde_<ten>;
  description         : abap.char( 100 );
  currency            : abap.cuky;
  amount              : zde_amount;
  quantity            : abap.quan( 13, 3 );
  unit                : abap.unit( 3 );
  created_by          : abp_creation_user;
  created_at          : abp_creation_tstmpl;
  last_changed_by     : abp_locinst_lastchange_user;
  last_changed_at     : abp_locinst_lastchange_tstmpl;
}
```

#### Cac annotation table quan trong

| Annotation | Gia tri | Mo ta |
|------------|---------|-------|
| `@EndUserText.label` | string | **Bat buoc** — Mo ta table |
| `@AbapCatalog.tableCategory` | `#TRANSPARENT` | Transparent table (duy nhat tren ABAP Cloud) |
| `@AbapCatalog.deliveryClass` | `#A` | `#A`: app, `#C`: customer, `#L`: system |
| `@AbapCatalog.dataMaintenance` | `#RESTRICTED` | `#ALLOWED` hoac `#RESTRICTED` (recommend) |
| `@AbapCatalog.enhancement.category` | `#NOT_EXTENSIBLE` | `#NOT_EXTENSIBLE`, `#EXTENSIBLE_ANY` |
| `@AbapCatalog.buffering` | `#OFF` | Buffer: `#OFF`, `#ALLOWED` |

#### Reuse Data Elements (SAP-release cho ABAP Cloud)

| Data Element | Kieu | Mo ta | Bat buoc cho RAP? |
|-------------|------|-------|-------------------|
| `sysuuid_x16` | raw(16) | UUID key | ✅ Key cho RAP managed |
| `abp_creation_user` | char(12) | Created by | ✅ |
| `abp_creation_tstmpl` | utclong | Created at (UTC) | ✅ |
| `abp_locinst_lastchange_user` | char(12) | Last changed by | ✅ |
| `abp_locinst_lastchange_tstmpl` | utclong | Last changed at | ✅ |
| `abp_lastchange_tstmpl` | utclong | Global last changed | ✅ |
| `abp_locale` | char(2) | Language | Khi can multi-language |

> ⚠️ `key client : abap.clnt not null` LUON la key dau tien. KHONG dung `MANDT`.

### Buoc 5: CDS Table Entity (khuyen nghi cho ABAP Cloud 2024+)

CDS Table Entity la cach SAP khuyen nghi de dinh nghia persistent table trong ABAP Cloud,
thay the classic DDIC table cho RAP managed BO.

```abap
@EndUserText.label : 'Business Object Entity'
@AbapCatalog.enhancement.category : #EXTENSIBLE_ANY
define root view entity ztb_<ten>
  as select from root table
{
  key client          : abap.clnt not null;
  key uuid            : sysuuid_x16 not null;
      name            : abap.char( 40 );
      description     : abap.char( 100 );
      created_by      : abp_creation_user;
      created_at      : abp_creation_tstmpl;
      last_changed_by : abp_locinst_lastchange_user;
      last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

**Khi nao dung CDS Table Entity:**
- ✅ Tao RAP managed BO moi.
- ✅ Can draft-enabled persistence.
- ✅ Can full CDS annotation support.
- ❌ Can classic ABAP read/write (SELECT ... INTO TABLE) — dung classic DDIC table.

### Buoc 6: Transport Request

Khi tao moi dictionary object tren ABAP Cloud, **bat buoc gan vao transport request**:

1. Mo ADT Eclipse, vao **Project Explorer**.
2. Right-click package -> **New** -> **ABAP Repository Object** -> chon loai (Domain/Data Element/Table).
3. Trong wizard, ADT tu dong tao transport request hoac cho phep chon transport request co san.
4. Nhap source code (dung template o Buoc 2-5 ben tren).
5. Save + Activate (F8) — object se duoc them vao transport request.

**Dung MCP tools de tao + activate + transport:**
Neu dung MCP server (`fr0ster/mcp-abap-adt`, `ARC-1`), cac tool se tu dong:
- Lock object → tao → activate → unlock → gan transport.
- Xem `reference/mcp-guides/mcp-sap-adt.md` de biet chi tiet.

### Buoc 7: Deploy qua abapGit

Sau khi sinh code, can tao `package.devc.xml` va `abapgit.xml` de import vao ADT:

```
out/<ticket>/src/
├── package.devc.xml      — Package dinh nghia
├── abapgit.xml           — abapGit manifest
└── zdict/
    └── ... (cac object da tao)
```

**Cau truc `package.devc.xml` co ban:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<abapGit version="v1.0.0">
  <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
    <asx:values>
      <DEVC>
        <CTEXT>Package Description</CTEXT>
      </DEVC>
    </asx:values>
  </asx:abap>
</abapGit>
```

Tham khao template co san: `reference/templates/` trong project.

### Buoc 8: Dung MCP ADT Tools de tao tu dong (optional)

Neu da cai dat MCP server, co the tao truc tiep tu AI:

| MCP Server | Tools tao dictionary | Cach dung |
|------------|---------------------|-----------|
| **`sap-dict-bridge`** (khuyen dung — native cua repo nay) | `sap_create_domain`, `sap_create_data_element`, `sap_create_table` | Tai su dung cookie auth co san cua `sap-btp-agent` (khong can basic auth/config rieng nhu fr0ster). Dang ky: `claude mcp add --transport stdio sap-dict-bridge -- python -m sap_btp_agent.bridge_server`. Test: `python scripts/test_dict_bridge.py [profile_id]`. |
| `fr0ster/mcp-abap-adt` | `CreateDomain`, `CreateDataElement`, `CreateTable` | Prompt: "Tao domain + data element + table". [Da thu trong du an nay roi thay bang `sap-dict-bridge` o tren de tai su dung cookie auth co san — xem `reference/mcp-guides/mcp-sap-adt.md` neu van muon dung ban goc.] |
| `ARC-1` | `abap_create_object` | Prompt + XML payload |
| SAP Official ADT MCP | Qua extension ADT MCP | Zero-config trong VS Code ADT |

✅ **Da fix (2026-07-12)**: `sap_create_table` truoc day co bug — tham so `fields[].key` khong tu
them tu khoa `key` vao truoc ten field trong DDL sinh ra (chi quyet dinh co `not null` hay khong).
Da sua trong `_build_table_ddl` (`reference/mcp-server/sap_btp_agent/tools/dictionary.py`): field
moi truyen `{"name": "<ten>", "key": "true"}` (khong can go san chu "key " trong ten) gio sinh dung
`key <ten> : ...` — da verify qua goi ham truc tiep, doi chieu output ca 2 kieu goi (ten da co "key
" san / ten thuong + flag `key`) deu ra dung DDL.

**Example prompt (cho AI agent):**
```
Tao domain ZDOM_STATUS, type abap.char(1), value range:
  'O' = Open, 'C' = Closed, 'A' = Approved.
Sau do tao data element ZDE_STATUS dung domain ZDOM_STATUS, label 'Status'.
Cuoi cung tao table ZTB_HEADER:
  - key client : abap.clnt not null
  - key uuid   : sysuuid_x16 not null
  - status     : zde_status
  - created_by : abp_creation_user
  - created_at : abp_creation_tstmpl
```
---

## Buoc tiep theo

- Neu da tao table cho RAP: dung `sap-scaffold-rap` de sinh CDS + behavior.
- Neu chi tao table cho read-only: dung `sap-scaffold-cds` de sinh CDS views.
- Kiem tra syntax/ATC: dung `sap-atc-review`.
- Chay unit test: dung `sap-unit-test`.
- Dong ticket: dung `sap-finish-ticket`.

---

## Gotcha & Luu y quan trong

### 1. Key `client` LUON la field dau tien
```abap
key client : abap.clnt not null;    // DUNG
key mandt : abap.clnt not null;     // SAI -> ATC reject
```

### 2. UUID `sysuuid_x16` vs `abap.int4`

| UUID (`sysuuid_x16`) | Integer (`abap.int4`) |
|-----------------------|----------------------|
| ✅ Dung cho RAP managed BO | ❌ Khong dung cho RAP managed (framework can UUID) |
| ✅ Dung cho distributed system | ✅ Dung cho local/custom logic |
| Data element release-san | Tu tao data element |

### 3. `not null` — chi dung cho key fields
Non-key fields KHONG can `not null`. Chi `client` + `uuid` la `not null`.

### 4. `@DataClassification.level` bat buoc
Thieu annotation nay tren Data Element -> ATC bao loi.
```abap
@DataClassification.level : #BUSINESS_INFORMATION
// #CRITICAL | #PERSONAL | #NONE | #BUSINESS_INFORMATION
```

### 5. `abap.dec( total, decimals )`: total BAO GOM decimal
VD: `abap.dec( 16, 2 )` = 14 so nguyen + 2 so thap phan.

### 6. Quy uoc dat ten

| Object | Prefix | Vi du |
|--------|--------|-------|
| Domain | `ZDOM_` / `YDOM_` | `ZDOM_STATUS` |
| Data Element | `ZDE_` / `YDE_` | `ZDE_DESCRIPTION` |
| Database Table (DDIC) | `ZTB_` / `YTB_` | `ZTB_ORDER` |
| CDS Table Entity | `ZT_` / `YT_` | `ZT_ORDER` |

### 7. Classic Table vs CDS Table Entity

| Aspect | Classic DDIC (`define table`) | CDS Table Entity (`define root view entity ... as select from root table`) |
|--------|-------------------------------|---------------------------------------------------------------------------|
| Cu phap | `define table ztb_xxx { ... }` | `define root view entity zt_xxx as select from root table { ... }` |
| RAP managed | ✅ (van duoc) | ✅ ✅ SAP khuyen nghi |
| Fiori Elements | ✅ (qua CDS view) | ✅ (truc tiep) |
| Draft | ✅ (qua CDS view) | ✅ (tu dong) |
| Classic SELECT | ✅ truc tiep | ✅ (CDS select) |
| Annotation support | Co ban | **Day du** (Fiori, planning, semantic) |

---

## Tham khao

- Skill `sap-deployment-target` — **bat buoc chay truoc** de xac dinh package deploy + rao chan
  an toan (khong tao/sua/xoa object ngoai Z/Y hoac ngoai package da xac nhan) truoc khi tao object
  tren he thong that.
- Skill `sap-bootstrap-system-context` — do he thong that de biet object Z/Y nao da co san (dung
  o Buoc 0).
- `reference/mcp-guides/mcp-sap-adt.md` — cai dat MCP server de tao dictionary tu dong.
- Skill `sap-scaffold-rap` — sinh RAP BO tu table (CDS + behavior).
- Skill `sap-scaffold-cds` — sinh CDS view cho table (read-only).
- Skill `sap-clean-code` — naming conventions, clean code ABAP.
- Skill `sap-extensibility` — rang buoc ABAP Cloud, clean core.
- Agent `sap-btp-admin-consultant-cloud` (`reference/modules/sap-steampunk-cloud`) — package structure, ADT setup, deploy tren BTP (Steampunk).
- Skill `sap-abap-sql` — ABAP SQL, query table da tao.
- SAP ABAP Keyword Documentation (Cloud): `https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/index.html`
- SAP DEFINE TABLE: `https://help.sap.com/doc/abapdocu_cp_index_htm/CLOUD/en-US/abenddl_define_table.htm`
- SAP RAP Generator (open-source): `https://github.com/SAP-samples/cloud-abap-rap`
- ABAP Cheat Sheets (GitHub): `https://github.com/SAP-samples/abap-cheat-sheets`
