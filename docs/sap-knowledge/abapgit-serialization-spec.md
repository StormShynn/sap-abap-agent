# Bộ quy tắc serialize/deserialize abapGit — spec cho code generator SAP Cloud

> **Nguồn**: verify trực tiếp source `abapGit/abapGit` (pin commit `4ad2d9718395e1e89ffb06682332b25f381008b5`,
> fetch 2026-07-17) + đọc thật corpus `PUB_ACME_CODE` (Acme, S/4HANA Cloud Public Edition 2602, xem
> `docs/PUB_ACME_CODE_README.md`). Không suy đoán field/API nào chưa thấy trong source thật — phần chưa
> verify được đánh **[Unverified]**.
>
> **Mục đích**: cho AI sinh THẲNG file đúng format abapGit từ mô tả (docx/excel/FS...), bỏ bước "convert
> harness format → abapGit format" hiện đang làm tay/chưa hoàn chỉnh theo
> [0020-abapgit-staging-workflow.md](../decisions/0020-abapgit-staging-workflow.md) — để 1 lần abapGit
> pull vào `ACME_LOCAL` là tạo xong toàn bộ object của 1 project (report/API/form/app), không cần sửa tay.
>
> **Không phải mục đích**: đây KHÔNG phải spec để tự viết lại API tạo object bằng Python/ADT REST (đó là
> việc của [dictionary.py](../../../../reference/mcp-server/sap_btp_agent/tools/dictionary.py) — 1 cơ chế
> khác hẳn, xem §1.4). Mục tiêu ở đây là sinh file cho **abapGit thật** (đã cài trong hệ thống SAP) tự lo
> phần pull/tạo object.

---

## 0. Khung chung — áp cho MỌI object

Mọi file `.xml` metadata dùng đúng 1 khung, giống nhau 100% giữa các loại (verify byte-level qua
PUB_ACME_CODE + fixture `test/src/zabapgit.msag.xml` của chính abapGit):

```xml
<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_<TYPE>" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <!-- payload riêng từng loại, xem §2 -->
  </asx:values>
 </asx:abap>
</abapGit>
```

- **Indent = 1 space/cấp** (không phải 2 hay 4) — giữ đúng nếu muốn diff sạch với file abapGit thật.
- **Tên file** = `to_lower(obj_name).to_lower(obj_type)[.<extra>][.<ext>]` (verify từ
  `zcl_abapgit_filename_logic=>object_to_file`). `<extra>` chỉ xuất hiện với vài loại có nhiều file phụ
  (vd `.clas.locals_imp.abap`).
- `serializer`/`serializer_version` = tên+version của **handler class bên abapGit**, KHÔNG phải metadata
  nghiệp vụ — cứ ghi cố định theo bảng ở §2, đừng tự bịa version khác.
- Boolean encode **khác nhau theo họ**: DDIC-classic/OO/CDS dùng kiểu ABAP cổ điển (`X` = true, tag vắng
  = false); SRVB (nhóm RAP/Service) lại dùng literal JSON-style `true`/`false`. Sinh sai kiểu cho sai
  loại là lỗi âm thầm (XML vẫn hợp lệ nhưng giá trị sai).

---

## 1. Quy tắc cross-cutting — bắt buộc cho mọi object hướng SAP Cloud

### 1.1 ABAP Language Version — **bắt buộc**, sai là abapGit reject ngay

Mọi object có mã nguồn (CLAS/INTF/BDEF/PROG/FUGR/FUGS/TYPE — verify từ
`get_default_abap_language_vers`) mang 1 field mã hoá ABAP Language Version:
- Field `UNICODE` (kiểu `UCCHECK`) trong `VSEOCLASS`/`VSEOINTERF` (CLAS/INTF)
- Field `ABAP_LANGUAGE_VERSION` (DDLS/DDLX/DCLS, và `ABAP_LANGU_VERSION` cho SRVB/BDEF-metadata — 2 cách
  đánh vần khác nhau tuỳ file, xem ghi chú từng loại ở §2)

Giá trị xác nhận (`zif_abapgit_aff_types_v1=>co_abap_language_version_src`): `X`=Standard,
`2`=ABAP for Key Users, **`5`=ABAP for Cloud Development**.

Repo `.abapgit.xml` (ở mức repo, không phải từng object) cũng khai `abap_language_version`. Hàm
`check_abap_language_version` **raise exception nếu object và repo lệch nhau**
(`"Object {type} {name} has {desc A} but repository is set to {desc B}"`). abapGit tự mặc định
`cloud_development` khi chạy trên BTP (comment nguồn: *"On BTP, default to ABAP for Cloud Development"*).

**→ Áp dụng**: mọi object sinh ra nhắm S/4HANA Cloud Public phải set `5` (hoặc field tương đương) VÀ
`ACME_LOCAL/.abapgit.xml` phải khai cùng `abap_language_version = cloud_development`. Lệch 1 object là cả
lần pull đó fail ngay tại object đó.

### 1.2 Activate luôn bị delay + gom batch — generator không cần tự sắp thứ tự

Mọi `deserialize()` của mọi loại đều kết thúc bằng `zcl_abapgit_objects_activation=>add_item(ms_item)` —
chỉ **enqueue**, KHÔNG activate ngay tại chỗ. abapGit tự activate 1 lần cuối cho toàn bộ object vừa pull,
theo đúng 5 step cố định (`zcl_abapgit_objects=>get_deserialize_steps`, sort theo `order`):

`EARLY(1) → DDIC(2) → ABAP(3) → LATE(4) → LXE(5)`

Xác nhận tham gia từng step (per-type, verify từ mỗi handler):

| Step | Object tham gia |
|---|---|
| EARLY | CLAS/INTF (tạo stub trước, để object khác phụ thuộc không fail lúc activate) |
| DDIC | DOMA, TABL, MSAG, **DDLS** (DDLS activate qua `DD_MASS_ACT_C3`, cùng nhóm với DDIC cổ điển — DDLX/DCLS KHÔNG nằm nhóm này) |
| ABAP | CLAS/INTF (source đầy đủ), **DDLX** |
| LATE | DOMA (fix conversion-exit), CLAS/INTF (fix category exception), **DCLS** |
| LXE | mọi loại có translation |

**→ Kết luận quan trọng cho generator**: 1 lần abapGit pull, DDLS luôn activate trước DDLX trước DCLS —
đúng thứ tự 3-layer CDS (interface → metadata extension → access control) mà project này đang theo. Generator
**chỉ cần sinh đủ và đúng file**, KHÔNG cần tự gọi activate theo thứ tự tay — đây cũng là lý do lỗi
LA020 (xem ADR-0020 §Troubleshooting) không phải do thứ tự file trong 1 lần pull, mà do object bị lạc
sang package khác software component.

### 1.3 Package (DEVC) — không có field tự tham chiếu tên

`package.devc.xml` (verify từ 2 file thật + source) **chỉ có đúng 3 field**: `CTEXT`, `LANGUAGE`,
`MASTERLANG`. Tên package do **folder path** trong repo quyết định (theo `FOLDER_LOGIC` trong
`.abapgit.xml` của repo, không nằm trong nội dung XML của DEVC).

- **Sai hiện tại trong ADR-0020 §"Convert format"**: dòng "Package" ghi harness sinh `<PACKAGE>` rồi bảo
  ACME_LOCAL "chỉ `<CTEXT>`" — đúng hướng (bỏ field tên) nhưng thiếu: phải giữ **cả `LANGUAGE` và
  `MASTERLANG`**, không chỉ `CTEXT` một mình. 2 file thật đều có đủ 3 field.

### 1.4 4 "họ" API tạo object khác nhau — generator KHÔNG cần quan tâm cái này

| Họ API | Object | Cơ chế xác nhận từ source |
|---|---|---|
| `DDIF_*_PUT` cổ điển (+ Open SQL thuần cho MSAG) | DOMA, DTEL, TABL, MSAG | `DDIF_DOMA_PUT`, `DDIF_DTEL_PUT`; TABL: `DD_TABL_EXPAND` rồi mới `DDIF_TABL_PUT` (+`DDIF_INDX_PUT` riêng cho index); **MSAG không gọi FM nào** — `MODIFY t100/t100a/t100t/t100u` trực tiếp (comment nguồn: `RPY_MESSAGE_ID_INSERT` không ổn định qua bản cũ) |
| `SEO_*_CREATE_COMPLETE` (FM, tạo shell) + `CL_OO_*_SOURCE_SCANNER`/`CL_OO_*_SECTION_SOURCE` (class, đẩy source) | CLAS, INTF | `SEO_CLASS_CREATE_COMPLETE`/`SEO_INTERFACE_CREATE_COMPLETE`; source qua `CL_OO_SOURCE_SCANNER_CLASS`+`CL_OO_CLASS_SECTION_SOURCE` (tương tự bên INTF). INTF có nhánh riêng hoàn toàn nếu là proxy interface (`CLSPROXY=X`) → đi qua `CL_PXN_FACTORY`, không dùng SEO_* |
| `CL_WB_OBJECT_OPERATOR` (framework "blue"/Workbench chung) | BDEF, SRVD, SRVB | `CL_WB_OBJECT_OPERATOR=>CREATE_INSTANCE` + `IF_WB_OBJECT_OPERATOR~CREATE/UPDATE`. SRVB thêm side-effect: tự publish/unpublish OData qua `/IWFND/CL_V4_PUBLISHING_CONFIG` |
| Factory + handler riêng **từng loại, không giống nhau** | DDLS, DDLX, DCLS | `CL_DD_DDL_HANDLER_FACTORY` (DDLS) / `CL_DDLX_ADT_OBJECT_PERSIST`+`CL_DDLX_WB_OBJECT_DATA` (DDLX) / `CL_ACM_DCL_HANDLER_FACTORY` (DCLS) |

**Không có 1 API chung nào cho "tạo object SAP"** — đây chính là lý do nên đi theo hướng **abapGit-staging**
(sinh đúng file, để abapGit thật trong hệ thống SAP tự pull) thay vì tự viết lại 4 họ API này bằng
Python/ADT REST. Approach hiện có ([dictionary.py](../../../../reference/mcp-server/sap_btp_agent/tools/dictionary.py))
đi đường ADT REST (`create→lock→PUT source→unlock→activate` qua HTTP) — là 1 cơ chế **hoàn toàn khác**,
không liên quan 4 họ trên, và mới cover 1 phần nhỏ (thiếu CREATE cho Domain/DataElement, Class chưa hỗ
trợ locals/testclasses, chưa có BDEF/DOMA/DTEL/MSAG/INTF/DEVC).

---

## 2. Chi tiết từng loại object

Ký hiệu: 🟢 = đã verify từ ví dụ thật (PUB_ACME_CODE) + source abapGit. 🟡 = chỉ verify từ source (chưa có
ví dụ thật). ⚠️ = có [Unverified]/rủi ro cần biết.

### DOMA — Domain 🟢
- File: `<name>.doma.xml` (không có source phụ, trừ nhánh AFF/JSON — xem dưới).
- Payload: `DD01V` (header) + `DD07V_TAB` (bọc nhiều `DD07V` — **wrapper = tên field + `_TAB`**).
- Field thật (từ `zdo_auth_mode.doma.xml`): `DOMNAME`, `DATATYPE`, `LENG` (zero-pad 6 số, vd `000050`),
  `OUTPUTLEN`, `VALEXI` (`X` nếu có fixed values), `DDTEXT`, `DOMMASTER`, `DDLANGUAGE`; mỗi `DD07V`:
  `VALPOS` (`0001`, `0002`...), `DOMVALUE_L`, `DDTEXT`.
- Push: `DDIF_DOMA_PUT` (`name`, `dd01v_wa`, tables `dd07v_tab`).
- ⚠️ Có nhánh JSON thay XML (`is_supported_object_type('DOMA')`) nhưng đây là **experimental, tắt mặc
  định** (feature flag `'AFF'`) — generator dùng nhánh XML mặc định, KHÔNG dùng JSON.
- ⚠️ Fixed values kế thừa từ enhancement bị loại khi serialize (`appval=X`) — generator chỉ nên emit
  fixed values gốc của domain, không emit fixed values "thừa hưởng".
- ⚠️ **`LENG` ≠ `OUTPUTLEN` là bình thường, không phải lỗi** — verify từ rà soát ~40 domain thật thêm
  (2026-07-18, cả 5 project trong `tests/__Du_an`): `DATS` có `LENG=000008`/`OUTPUTLEN=000010` (thêm 2
  ký tự phân cách ngày); `CURR(11,2)` có `LENG=000011`/`OUTPUTLEN=000014`. Domain kiểu `RSTR`/`STRG`
  (binary lớn) **hoàn toàn không có `LENG`/`OUTPUTLEN`/`DECIMALS`** — chỉ `DOMNAME`/`DATATYPE`/`DDTEXT`/
  `DOMMASTER`. Generator không nên tự suy `OUTPUTLEN = LENG` hay ép buộc set 3 field này cho mọi kiểu.

### DTEL — Data Element 🟢
- File: `<name>.dtel.xml`, payload flat `DD04V`.
- Field thật (từ `zde_auth_mode.dtel.xml`): `ROLLNAME`, `DOMNAME` (tham chiếu domain), `HEADLEN`,
  `SCRLEN1/2/3`, `DDTEXT`, `REPTEXT`, `SCRTEXT_S/M/L`, `DTELMASTER`, `REFKIND` (`D`=Domain, khác nếu
  tham chiếu built-in type trực tiếp).
- Push: `DDIF_DTEL_PUT` (`name`, `dd04v_wa`) — verify trực tiếp source, gọi 2 lần (chính + per-language
  trong `deserialize_texts`).
- ⚠️ **~1/3 data element thật KHÔNG tham chiếu domain nào cả** — verify qua rà soát 155 file `.dtel.xml`
  thật (2026-07-18): 106/155 có `REFKIND`, **49/155 hoàn toàn KHÔNG có tag `REFKIND`** (không phải giá
  trị khác — vắng mặt hẳn). Trường hợp này `DOMNAME` cũng vắng, thay vào bằng `DATATYPE`+`LENG`+
  `OUTPUTLEN` chèn thẳng (vd `zde_auth_token.dtel.xml`: `DATATYPE=CHAR`, `LENG=000050`, không `DOMNAME`/
  `REFKIND`). Generator cần hỗ trợ CẢ 2 nhánh: data element gắn domain (`REFKIND=D`+`DOMNAME`) VÀ data
  element kiểu trực tiếp (`DATATYPE`+`LENG`+`OUTPUTLEN`, không `REFKIND`/`DOMNAME`).
- ⚠️ **`DOMNAME` thường trỏ domain CHUẨN của SAP, không chỉ Z-domain tự tạo** — thấy &gt;40 lượt dùng
  domain built-in (`CHAR1/CHAR10/CHAR20/CHAR40/CHAR50/CHAR80/CHAR100/CHAR200/CHAR255`, `TEXT20/TEXT30/
  TEXT40/TEXT50/TEXT100/TEXT255`, `DATS`, `DATUM`, `MATNR`...) làm `DOMNAME`. Generator KHÔNG nên bắt
  buộc domain phải tồn tại trong namespace Z/phải tự tạo trước — domain chuẩn SAP dùng thẳng được.

### TABL — Table 🟢
- File: `<name>.tabl.xml`, KHÔNG có source phụ (nhánh DDL-text `zcl_abapgit_object_tabl_ddl` có tồn tại
  trong source nhưng **không được gọi từ serialize/deserialize thật** — chỉ dùng nội bộ cho test, đừng
  dựa vào nó).
- Payload (đúng thứ tự add): `DD02V`, `DD09L`, `DD03P_TABLE` (bọc nhiều `DD03P` = field list), `DD05M_TABLE`
  (foreign keys), `DD08V_TABLE` (search help), `DD12V`/`DD17V` (index — KHÔNG đi qua `DDIF_TABL_PUT`, xem
  dưới), `DD35V_TALE` (nguyên văn — abapGit tự gõ sai "TABLE" thành "TALE", giữ đúng typo này khi generate
  vì đây là tag thật abapGit đọc/viết), `DD36M`, `TABL_EXTRAS` (bọc `TDDAT` + `abap_language_version`).
- Field thật (từ `ztb_srv_api.tabl.xml`, 21 field mẫu): `DD02V.TABNAME/TABCLASS/CLIDEP/DDTEXT/MASTERLANG/
  CONTFLAG/EXCLASS`; `DD09L.AS4LOCAL/TABKAT/TABART/BUFALLOW`; mỗi `DD03P`: `FIELDNAME`, `KEYFLAG`,
  `ROLLNAME` (hoặc `DATATYPE`+`LENG`+`INTTYPE`+`INTLEN`+`MASK` nếu không có data element), `COMPTYPE`,
  `SHLPORIGIN`. Field admin RAP chuẩn luôn có ở cuối: `CREATED_BY`(`ABP_CREATION_USER`)/`CREATED_AT`
  (`ABP_CREATION_TSTMPL`)/`LOCAL_LAST_CHANGED_BY`/`LOCAL_LAST_CHANGED_AT`/`LAST_CHANGED_AT`.
- Push: **2 bước** `DD_TABL_EXPAND` (mở rộng từ field list) rồi `DDIF_TABL_PUT` (`name`, `dd02v_wa`,
  `dd09l_wa`, tables `dd03p_tab`/`dd05m_tab`/`dd08v_tab`/`dd35v_tab`/`dd36m_tab`). **Index KHÔNG nằm
  trong lệnh trên** — xử lý riêng qua `DDIF_TABL_GET`(diff)→`DD_INDX_DEL`(index cũ)→`DDIF_INDX_PUT`
  (index mới/sửa).
- ⚠️ Nếu object là IDoc segment đã đăng ký (`edisegment`), toàn bộ luồng trên bị thay bằng
  `SEGMENT_READ/CREATE/MODIFY` — không áp dụng cho bảng Z thường, chỉ ghi chú để biết có ngoại lệ.
- ⚠️ Field/FK/search-help kế thừa từ `.INCLUDE` bị loại khi serialize — generator chỉ emit field khai
  trực tiếp trong bảng, không emit field thừa hưởng từ include.
- ⚠️ **`DD05M` (foreign key) — `FORTABLE` chưa xác định được quy tắc chắc chắn**: đọc 2 bảng thật có FK
  (2026-07-18) cho kết quả KHÔNG nhất quán — 1 bảng cả 2 entry `DD05M` đều `FORTABLE=<chính bảng đó>`;
  bảng kia entry #1 lại `FORTABLE=<bảng cha>` còn entry #2 mới `FORTABLE=<chính bảng đó>`. Dữ liệu thật
  quan sát được nguyên văn nhưng **[Unverified] đâu là quy tắc đúng** — generator chưa nên tự sinh
  `DD05M_TABLE`, cần verify thêm trên tenant thật trước khi cứng hoá logic này. `DD08V` (search help)
  cũng thấy 2 biến thể thật khác nhau (`CARD=CN` không `CHECKFLAG`, vs `CARD=N`+`CHECKFLAG=X`).
- Xác nhận thêm (âm tính, củng cố ghi chú index ở trên): rà soát toàn bộ 202 file `.tabl.xml` thật (cả 5
  project) — **không file nào có `DD12V`/`DD17V` (secondary index)** populated.

### MSAG — Message Class 🟢
- File: `<name>.msag.xml`, payload `T100A` (header) + `T100` (**wrapper và child cùng tên `T100`** —
  khác DD07V_TAB/DD03P_TABLE ở trên, không có suffix `_TAB`/`_TABLE`).
- Field thật (từ `zmess_srv_api.msag.xml`): `T100A.ARBGB/MASTERLANG/STEXT`; mỗi `T100`: `SPRSL`, `ARBGB`,
  `MSGNR` (3 số, `001`.."999"), `TEXT`.
- **Escape XML 2 quy tắc bắt buộc** (verify từ nội dung message thật): `&` trong message-variable
  (`&1`/`&2`/`&3`) → `&amp;1`; `'` trong text → `&apos;`, dù đang ở text content thường (không phải
  attribute) — nhiều generator XML mặc định chỉ escape `'` trong attribute, phải chỉnh riêng cho case này.
- Push: **KHÔNG có function module** — `MODIFY t100/t100a/t100t/t100u FROM ...` trực tiếp (Open SQL). Đây
  là loại DUY NHẤT trong nhóm DDIC-classic không dùng FM.
- `get_deserialize_steps` = `ABAP` + `LXE` (KHÔNG phải `DDIC` như DOMA/TABL) — vì không đi qua DDIF_*.
- ⚠️ **Xác nhận (2026-07-18): không tìm thấy bất kỳ cơ chế/API nào để GHI message text qua ADT REST**,
  ở cả 4 nguồn open-source đã tra (marcellourbani/abap-adt-api chỉ có 1 entry registry chưa test, chưa
  từng ported đi đâu) lẫn rà soát toàn bộ 5 project SAP thật trong `tests/__Du_an` (9 file `.msag.xml`
  thật, `git log --all --grep="message"` = 0 kết quả ở cả 5 repo, không README/script/tooling nào nhắc
  tới SE91/T100 programmatic). Đây là thao tác **chỉ làm được thủ công qua Eclipse ADT UI** — [dictionary.py](../../../../reference/mcp-server/sap_btp_agent/tools/dictionary.py)
  cố tình KHÔNG có tool `sap_create_message_class` vì lý do này (tạo shell rỗng không kèm được message
  nào thì không có giá trị thực dụng). Ví dụ thật `zmess_flatx_so.msag.xml` (bản rỗng, trước khi thêm
  message) xác nhận: chỉ có `T100A`, hoàn toàn KHÔNG có node `T100` nào (không phải rỗng, mà vắng mặt).

### CLAS — ABAP Class 🟢
- File chính: `<name>.clas.abap` (luôn có) + `<name>.clas.xml` (luôn có). File phụ **có điều kiện** (chỉ
  sinh nếu include tương ứng có nội dung):
  | Đuôi | Điều kiện |
  |---|---|
  | `.clas.locals_def.abap` | local types/classes định nghĩa có nội dung |
  | `.clas.locals_imp.abap` | local classes implementation có nội dung — **đây là nơi chứa logic behavior pool thật** (vd `lhc_*` handler class), KHÔNG phải trong `.clas.abap` chính |
  | `.clas.macros.abap` | macro include có nội dung |
  | `.clas.testclasses.abap` | test class có nội dung VÀ `VSEOCLASS-WITH_UNIT_TESTS = X` |

  Tần suất thật (rà soát 5 project, 2026-07-18): `.clas.locals_imp.abap` rất phổ biến (119 file thật).
  `.clas.testclasses.abap` **có tồn tại thật** (2 file, ABAP Unit test class chuẩn `FOR TESTING DURATION
  SHORT RISK LEVEL HARMLESS` + `cl_abap_unit_assert=>...`). `.clas.locals_def.abap` VÀ `.clas.macros.abap`
  **0 file nào tìm thấy** trong toàn bộ 5 project — abapGit source vẫn hỗ trợ (đừng bỏ 2 dòng này khỏi
  spec), nhưng thực tế rất hiếm gặp.
- Payload `.clas.xml`: root `VSEOCLASS` — `CLSNAME`, `LANGU`, `DESCRIPT`, `STATE`, `CATEGORY` (`40` =
  exception class; `06` = behavior pool — verify từ `zbp_r_srv_api.clas.xml` có `CATEGORY=06` +
  `CLSDEFINT=ZR_SRV_API` lưu tên root entity "for behavior of"), `CLSCCINCL`, `FIXPT`, `UNICODE` (= ABAP
  Language Version, xem §1.1), `WITH_UNIT_TESTS`.
- ⚠️ **Superclass/interface KHÔNG nằm trong XML** — hoàn toàn round-trip qua text `.clas.abap`
  (`INHERITING FROM`/`INTERFACES` trong source), abapGit tự parse lại bằng
  `CL_OO_SOURCE_SCANNER_CLASS` khi deserialize. Generator không cần (và không nên) tự thêm field kiểu
  "superclass" vào XML.
- Push: hybrid — shell qua `SEO_CLASS_CREATE_COMPLETE` (FM, có fallback bỏ `suppress_dialog` cho hệ
  thống cũ báo `cx_sy_dyn_call_param_not_found`), source qua `CL_OO_SOURCE_SCANNER_CLASS`→
  `CL_OO_CLASS_SECTION_SOURCE` (đẩy từng section public/protected/private).
- ⚠️ **Chưa xác nhận được** `SEO_CLASS_CREATE_COMPLETE` có nằm trong danh sách API released cho ABAP
  Cloud/S4HANA Cloud Public runtime hay không — [Unverified], không tìm thấy trong source abapGit cũng
  không tìm thấy qua search. Vì đây là việc của abapGit-thật-đã-cài-trong-hệ-thống chạy (không phải
  generator tự gọi FM này), rủi ro này KHÔNG chặn hướng abapGit-staging — chỉ là điểm cần biết nếu sau
  này có ai định tự gọi FM này trực tiếp (vd mở rộng approach ADT-REST).

### INTF — Interface 🟢
- File: `<name>.intf.abap` + `<name>.intf.xml` (mặc định) **hoặc** `<name>.intf.json` (+ file i18n) nếu
  feature flag `AFF` bật — ⚠️ **AFF cho INTF được đánh dấu experimental, TẮT mặc định** → generator dùng
  nhánh XML.
- Payload `.intf.xml`: root `VSEOINTERF` — `CLSNAME`, `LANGU`, `DESCRIPT`, `EXPOSURE` (`2`=public — verify
  từ `zif_api.intf.xml`), `STATE`, `UNICODE`. Không có `FIXPT`/`CLSCCINCL` (2 field đó chỉ CLAS mới có).
- ⚠️ Field `CLSPROXY=X` (proxy interface, sinh từ Enterprise Service/WSDL) → toàn bộ push đi nhánh khác
  hẳn (`CL_PXN_FACTORY`, quản lý qua SPRX) — generator cho custom Z-interface thường thì luôn để trống/`
  false`, không set field này.
- Push: `SEO_INTERFACE_CREATE_COMPLETE` (cùng pattern FM như CLAS) + `CL_OO_SOURCE_SCANNER_INTERFACE`→
  `CL_OO_INTERFACE_SECTION_SOURCE`.

### DDLS — CDS View (Data Definition) 🟢
- File: `<name>.ddls.asddls` (DDL source, luôn có) + `<name>.ddls.xml` + `<name>.ddls.baseinfo`
  (JSON, **có điều kiện** — chỉ khi `is_baseinfo_supported()`, tức hệ thống ≥ NW 751; verify: baseinfo
  **là do chính abapGit sinh/đọc**, KHÔNG phải artifact riêng của Eclipse ADT như từng nghi ngờ).
- Payload `.ddls.xml`: type `DDDDLSRCV` — field xác nhận: `SOURCE` (bị xoá khỏi XML sau khi tách ra
  `.asddls`, KHÔNG double-lưu), `AS4USER/AS4DATE/AS4TIME/ACTFLAG/CHGFLAG` (đều bị clear trước serialize —
  generator không cần set các field admin này), `ABAP_LANGUAGE_VERSION`.
  - **Không tìm thấy `DDTEXT`/description/`SOURCE_TYPE` là field riêng trong class handler** — khác với
    ví dụ thật PUB_ACME_CODE cho thấy `.ddls.xml` CÓ `DDLNAME`/`DDLANGUAGE`/`DDTEXT`/`SOURCE_TYPE` (verify
    từ `zi_nfg_bankkey.ddls.xml`). ⚠️ Nghĩa là các field này thuộc phần `DDDDLSRCV` mà agent verify-source
    không lấy được full danh sách (type hệ thống, không nằm trong repo abapGit) — **dùng ví dụ thật
    PUB_ACME_CODE làm chuẩn cho các field text/mô tả này**, dùng verify-source làm chuẩn cho field nào bị
    clear/xử lý đặc biệt.
  - Baseinfo (JSON): `{"BASEINFO":{"FROM":[...], "ASSOCIATED":[...], "BASE":[...], ...}}` — danh sách
    nguồn (`FROM`) ghi **UPPERCASE** dù DDL source dùng mixed-case (vd source viết `I_Bank_2`, baseinfo
    ghi `I_BANK_2`).
- Push: **KHÔNG DDIF_*, KHÔNG SEO_***. Factory `CL_DD_DDL_HANDLER_FACTORY=>CREATE` → `IF_DD_DDL_HANDLER~
  SAVE` (`name`, `put_state='N'`, `ddddlsrcv_wa`, `baseinfo_string`, `save_language_version=X`) rồi
  `IF_DD_DDL_HANDLER~WRITE_TADIR`. Delete (thật, không phải lúc lỗi) lại dùng FM cổ điển `DD_MASS_ACT_C3`
  trực tiếp — comment nguồn giải thích: `IF_DD_DDL_HANDLER->DELETE` không xoá được view có view khác
  tham chiếu.
- Step activate: `DDIC` (cùng nhóm DOMA/TABL/MSAG, KHÁC DDLX/DCLS — xem §1.2).

### DDLX — Metadata Extension 🟢
- File: `<name>.ddlx.asddlxs` + `<name>.ddlx.xml`. Không có baseinfo.
- Payload `.ddlx.xml` **nested 1 cấp** (khác DDLS/DCLS phẳng): `<DDLX><METADATA><NAME>.../<DESCRIPTION>...
  <MASTER_LANGUAGE>EN</MASTER_LANGUAGE></METADATA></DDLX>` — chú ý `MASTER_LANGUAGE` 2 ký tự (`EN`) khác
  `DDLANGUAGE` 1 ký tự (`E`) của DDLS, dù cùng ý nghĩa "ngôn ngữ gốc".
- Push: `CL_DDLX_ADT_OBJECT_PERSIST` (persistence) + `CL_DDLX_WB_OBJECT_DATA` (data model) →
  `set_data()`+`save()` (interface call thuần, không qua FM hay dynamic CALL METHOD).
- ⚠️ **Annotation cấp ENTITY phải đặt NGOÀI khối `annotate ... with { }`, TRƯỚC từ khoá `annotate`** —
  xác nhận qua ví dụ thật (`zc_zco02.ddlx.asddlxs`) kèm nguyên văn comment của dev gốc: *"@UI.presentation
  Variant la annotation cap ENTITY -&gt; PHAI dat NGOAI {} (truoc "annotate entity")"*. Annotation cấp
  FIELD (`@UI.identification`, `@UI.lineItem`...) mới đặt trong `{}` như bình thường. Sai chỗ này là lỗi
  cú pháp DDL thật, không phải chỉ style.
- ⚠️ **Bug thật trong source abapGit** (không phải lỗi của generator, chỉ cần biết để không bị bối rối
  khi debug): `deserialize()` đọc field `METADATA-ABAP_LANGU_VERSION` (thiếu "AGE") nhưng
  `clear_fields()` lúc serialize lại xoá `METADATA-ABAP_LANGUAGE_VERSION` (đủ "AGE") — 2 tên khác nhau,
  cả 2 đều bọc `IF sy-subrc = 0` nên lệch tên không gây lỗi ngay, chỉ khiến field không round-trip đúng.
- `METADATA-VERSION` bị **force = `'inactive'`** khi deserialize (comment nguồn: luôn lưu inactive rồi để
  bước activate chuẩn phía sau xử lý, tránh tự tạo transport request lúc save).
- Step activate: `ABAP`.

### DCLS — Access Control (DCL) 🟢
- File: `<name>.dcls.asdcls` + `<name>.dcls.xml`. Không có baseinfo.
- Payload `.dcls.xml` **phẳng** (khác DDLX): `DCLNAME`, `DCL_TYPE` (`ROLE`), `MASTERLANG`, `LANGUAGE`,
  `SHORT_TEXT`, `ABAP_LANGUAGE_VERSION` (verify từ `zc_nfg_bankkey.dcls.xml`).
- Push: `CL_ACM_DCL_HANDLER_FACTORY=>CREATE` → `SAVE` (`iv_dclname`, `iv_put_state='I'`, `is_dclsrc`,
  `iv_devclass`, `iv_access_mode='INSERT'` — **luôn hardcode `INSERT`**, ⚠️ chưa xác nhận được hành vi
  khi DCLS đã tồn tại/pull lại nhiều lần vì không thấy nhánh `UPDATE`/`MODIFY` nào trong source đã đọc).
  Khác DDLS/DDLX: `tadir_insert` gọi **trước** SAVE, không phải sau.
- Step activate: `LATE` — luôn sau DDLS(`DDIC`)/DDLX(`ABAP`) trong 1 lần pull.
- ⚠️ Cú pháp `aspect pfcg_auth(...)` xác nhận qua 2 ví dụ thật ĐANG hoạt động (2026-07-18, phân biệt với
  nhiều file khác chỉ có pattern này dạng comment/TODO chưa bật): (1) tham số theo VỊ TRÍ, auth-object
  dạng token trần: `aspect pfcg_auth(F_BKPF_BUK, BUKRS, ACTVT = '03')`; (2) tham số theo TÊN, auth-object
  dạng string literal, `where()` HOÀN TOÀN RỖNG (không map field nào): `where ( ) = ASPECT pfcg_auth (
  'S_TABU_NAM', ACTVT = '03', TABLE = 'ZI_TABLETEMPLATEEXPORT' )`. Cả 2 dạng đều là DDL hợp lệ thật.

### BDEF — RAP Behavior Definition 🟢 (verify source + 21 ví dụ thật, 2026-07-18)
- File: `<name>.bdef.asbdef` (source) + `<name>.bdef.xml`.
- Payload `.bdef.xml` thật (đọc 17 file `zr_*`/`zc_*` trong PUB_ACME_CODE + GLB_FlatX/GLB_MasterData, cùng
  1 shape 100%, khớp khung chung §0): root `<BDEF>` phẳng — `NAME`, `TYPE` (luôn `BDEF/BDO`),
  `DESCRIPTION`, `DESCRIPTION_TEXT_LIMIT` (luôn `60`), `LANGUAGE`/`MASTER_LANGUAGE` (luôn `EN`), `LINKS`
  (boilerplate), `ABAP_LANGU_VERSION` (luôn `5`), `SOURCE_URI` (`./<name_lower>/source/main`),
  `SOURCE_TYPE` (`ABAP_SOURCE`), `SOURCE_FIXED_POINT_ARITHMETIC`/`SOURCE_UNICODE_CHECKS_ACTIVE` (luôn
  `true`). Không có `RESPONSIBLE`/`PACKAGE` (như mọi loại khác, abapGit không serialize 2 field này).
- Push: cùng framework `CL_WB_OBJECT_OPERATOR`/`CL_BLUE_WB_UTILITY` như SRVD/SRVB (§1.4) — object loại
  "atomic" (category 1) dùng 1 lệnh CREATE/UPDATE; "compound" (category 2) tách 2 bước CREATE rồi UPDATE.
- ⚠️ **Field/cơ chế "implementation_type" — VẪN [Unverified]**: 17 file `.bdef.xml` thật đọc được là
  chiều SERIALIZE (đọc object đã activate ra) — **không đâu chứa** field/giá trị "implementation_type"/
  "Managed"/"Unmanaged" (loại behavior chỉ nằm trong TEXT source, không phải metadata riêng). Vì đây là
  chiều đọc, KHÔNG thể xác nhận hay phủ nhận cơ chế tạo (chiều ngược lại, dùng
  `<adtcore:adtTemplate><adtcore:adtProperty adtcore:key="implementation_type">`) — vẫn cần 1 test tạo
  thật để chốt.
- **Cú pháp DDL thật (`.asbdef`) — xác nhận 3 loại `managed`/`unmanaged`/`projection`, ví dụ thật**:
  - Projection **CÓ** class: `projection implementation in class ZBP_C_SRV_API unique; strict ( 2 );
    extensible; use draft; define behavior for ZC_SRV_API alias ServiceApi extensible use etag { use
    create; use update; use delete; use action Edit; }`
  - Projection **KHÔNG** class (rất phổ biến — `ZC_ZCM01_PHIEUTHU001`, `ZC_QM_ZQM03`, `ZC_INT_BILLING`...):
    `projection; strict ( 2 ); use side effects; define behavior for ZC_QM_ZQM03 alias zqm03 { use action
    printPDF; }` — **generator PHẢI cho phép BDEF không có implementation class** (case này rất thật, chỉ
    có 1 dòng "projection;" đầu tiên, không "implementation in class").
  - Managed root đầy đủ tính năng: `managed implementation in class ZBP_R_SRV_API unique; strict ( 2 );
    with draft; define behavior for ZR_SRV_API alias ServiceApi persistent table ztb_srv_api extensible
    draft table ztbsrv_api_d etag master LocalLastChangedAt lock master total etag LastChangedAt
    authorization master ( global ) { field ( readonly ) ServiceID; field ( numbering : managed )
    ServiceID; create; update; delete; action healthCheck; determination setIsClouddest on modify {
    field IsCloudDest; } validation checkMandatory on save { create; field ServiceName; } side effects {
    field IsCloudDest affects field IsCommArr; } draft action Activate optimized; mapping for
    ztb_srv_api corresponding extensible { ServiceID = service_id; } }`.
  - Unmanaged (không `persistent table`, không `mapping`, dùng cho nguồn proxy/không-DB):
    `unmanaged implementation in class zbp_r_int_billing unique; strict ( 2 ); define behavior for
    ZR_INT_BILLING alias Billing lock master authorization master ( instance ) { create ( authorization
    : global ); update; delete; field ( readonly ) BillingDocument; action SyncFlatX result[0..*] $self; }`.
  - Fragment khác xác nhận thật: `static action createMultiple deep parameter ZD_WEIGH_REC_IMPORT;`,
    `action ( features : instance ) print parameter zi_footer result [0..*] $self;`,
    `action postAllRecords;` (bare, không result clause), `update ( precheck );`,
    `with additional save and cleanup`, `draft action Edit with additional implementation;`. Class name
    sau `implementation in class` chấp nhận cả UPPERCASE lẫn lowercase (ABAP không phân biệt hoa/thường).
  - Code thật production KHÔNG "sạch" — thấy cả khối `mapping for`/`action` bị comment `//` dở dang trong
    file thật (WIP), generator không cần bắt chước việc này nhưng đừng ngạc nhiên khi thấy trong ví dụ.
- ⚠️ **Đây từng là object type BỊ THIẾU hoàn toàn trong bảng convert của ADR-0020** — hiện ADR-0020 không
  có dòng nào cho BDEF, nhưng BDEF là artifact bắt buộc cho MỌI kịch bản "RAP Managed/Unmanaged" trong
  [ARCHITECTURE.md](../ARCHITECTURE.md) (tức là mọi app CRUD/report có save, và projection-không-class
  cho report thuần). Cần bổ sung vào ADR-0020.

### SRVD — Service Definition 🟢
- File: `<name>.srvd.srvdsrv` (source) + `<name>.srvd.xml`.
- Field thật (từ `zui_nfg_bankkey_o4.srvd.xml`, khớp đúng field verify-source yêu cầu): `NAME`, `TYPE`
  (`SRVD/SRV`), `DESCRIPTION`, `LANGUAGE`/`MASTER_LANGUAGE` (2 ký tự, `EN`), `SOURCE_URI`
  (`./<name>/source/main`), `SOURCE_TYPE` (`ABAP_SOURCE`), `SRVD_SOURCE_TYPE` (`S`).
- ⚠️ **Validate cứng khi deserialize** (raise exception nếu sai): `DESCRIPTION` không được rỗng;
  `LANGUAGE` và `MASTER_LANGUAGE` phải **đúng 2 ký tự**. Generator phải tự check 2 điều kiện này trước
  khi ghi file, tránh abapGit reject.
- Push: `CL_WB_OBJECT_OPERATOR`/blue framework (§1.4), có thêm lớp `TRY/CATCH cx_static_check` xử lý
  trường hợp "ghost WB entry" (exists() trả false nhưng CREATE vẫn báo đã tồn tại) — tự fallback sang
  UPDATE, generator không cần lo việc này (abapGit tự xử lý).

### SRVB — Service Binding 🟢
- File: **chỉ** `<name>.srvb.xml`, không có source phụ.
- Field thật (từ `zui_nfg_bankkey_o4.srvb.xml`): `METADATA{NAME, TYPE(SRVB/SVB), DESCRIPTION, LANGUAGE,
  MASTER_LANGUAGE, ABAP_LANGU_VERSION}` + `CONTENT{BIND_TYPE_IMPL/NAME, BIND_TYPE(ODATA), BIND_TYPE_VERSION
  (V4), SERVICES/item/{SERVICE_NAME, SERVICE_CONTENT/item/{SERVICE_VERSION(0001), RELEASE_STATE
  (NOT_RELEASED), SRVD_REF{URI, TYPE, NAME}}}}` + phẳng `CONTRACT(C1), RELEASE_SUPPORTED, PUBLISHED,
  BINDING_CREATED, ALLOWED_ACTION`.
- ⚠️ **Boolean ở đây là `true`/`false` literal (JSON-style), KHÔNG phải `X`/rỗng** — khác mọi loại còn
  lại trong spec này. Field `PUBLISHED` đặc biệt quan trọng: nó **gate side-effect thật** — deserialize
  tự gọi `/IWFND/CL_V4_PUBLISHING_CONFIG=>PUBLISH_GROUP`/`DELETE_GROUP` dựa theo giá trị này. Set sai =
  service không được publish (hoặc bị unpublish ngoài ý muốn) sau khi pull.
- Push: `CL_WB_OBJECT_OPERATOR`/blue framework, luôn `unpublish()` trước khi create/update, `publish()`
  sau khi thành công (nếu `PUBLISHED=true`).
- ⚠️ **Không tìm thấy tên field cụ thể cho "loại/version binding" hay "tham chiếu service definition"**
  trong chính source class xử lý (nó chỉ truyền `METADATA`/`CONTENT` nguyên khối qua `GET_DATA`/
  `SET_DATA`, không đọc field con theo tên) — field list ở trên lấy từ **ví dụ thật PUB_ACME_CODE**, không
  phải từ verify-source. Coi ví dụ thật là chuẩn cho loại này.

### DEVC — Package 🟢
Xem §1.3 — chỉ 3 field `CTEXT`/`LANGUAGE`/`MASTERLANG`, tên package = folder path.

---

## 3. Map sang "loại project" — object nào cần cho report/API/form/app

Dựa theo cây quyết định trong [ARCHITECTURE.md](../ARCHITECTURE.md) và mô tả từng function-agent trong
[CLAUDE.md](../../CLAUDE.md)/[HARNESS.md](../HARNESS.md):

| Loại project (agent) | Object bắt buộc (theo spec ở §2) | Object có điều kiện |
|---|---|---|
| **Report/App read-only** (AGENTS_APP, không CRUD) | DDLS×2-3 (ZI+ZC, có thể bỏ ZR nếu không cần behavior), DDLX (ZC), SRVD, SRVB | DCLS nếu cần access control riêng; TABL/DTEL/DOMA nếu có bảng Z hỗ trợ |
| **App CRUD** (AGENTS_APP có save) | DDLS×3 (ZI+ZR+ZC) + **BDEF×2** (ZR managed/unmanaged + ZC projection) + DCLS×2 (ZR+ZC) + DDLX (ZC) + SRVD + SRVB + TABL (bảng lưu) | DTEL/DOMA cho field custom, MSAG cho message lỗi custom |
| **Form/in PDF** (AGENTS_PDF) | = App CRUD, thêm: TABL riêng cho PDF draft (`ztb_*_pdf`, field `attachment TYPE xstring` + `@Semantics.largeObject`), Action `CreatePDF` trong BDEF, CLAS helper (`zcl_*_print`) | INTF nếu tách interface cho helper |
| **API tích hợp** (AGENTS_API) | = App CRUD (inbound cần BDEF unmanaged thường gặp hơn managed), + CLAS/INTF cho logic tích hợp, TABL riêng cho `zint_log`, MSAG cho message lỗi | DTEL/DOMA cho field custom của payload |
| **Excel upload** (AGENTS_Excel) | = App CRUD, + CLAS cho logic đọc XLSX | — |

**Nhận xét quan trọng**: hầu hết loại project đều cần **toàn bộ 12 loại object** trong spec này ở mức độ
nào đó — không có loại project nào chỉ cần 1-2 loại. Đây là lý do phải làm spec đầy đủ 1 lần (như file
này) thay vì vá từng loại theo từng ticket.

---

## 4. Sai/thiếu cần sửa trong tooling hiện có

Đối chiếu trực tiếp với template/ADR đang có trong package này:

1. **`templates/rap-boilerplate/managed/ztb_object.tabl.xml`** — SAI, không dùng được:
   - `serializer_version="v2.0.0"` — thật là `v1.0.0`.
   - Cú pháp placeholder `<TABNAME>ZTB_<OBJECT></TABNAME>` **phá vỡ well-formed XML** (tag đóng không
     khớp tag mở gần nhất) — bất kỳ XML parser nào (kể cả abapGit) sẽ reject file này.
   - Thiếu `CLIDEP`/`MASTERLANG` (DD02V), thiếu `TABKAT`/`BUFALLOW` (DD09L), **không có `DD03P_TABLE`
     nào** (bảng sinh ra sẽ 0 field), không có `TABL_EXTRAS`.
2. **`templates/rap-boilerplate/managed/package.devc.xml`** — SAI: cùng lỗi version + placeholder tự
   lồng `<PACKAGE><PACKAGE>...`; và tự bịa field `<PACKAGE>` không tồn tại trong DEVC thật (xem §1.3);
   thiếu `LANGUAGE`/`MASTERLANG`.
3. **`templates/abapgit-serial/`** — được khai trong cấu trúc project ở [README.md](../../README.md)
   nhưng **chưa tồn tại** trên đĩa. Đây đúng là nơi nên đặt các template/generator thật hiện thực hoá
   spec này.
4. **ADR-0020 §"Convert format harness → abapGit"** — thiếu hoàn toàn dòng cho DOMA/DTEL/TABL/MSAG (4
   loại DDIC-classic) và cho BDEF; dòng Package cần sửa lại theo §1.3 (giữ `LANGUAGE`+`MASTERLANG`, không
   chỉ `CTEXT`); nên bổ sung field-list chi tiết như §2 thay vì chỉ nói "copy nguyên" (đặc biệt CLAS đang
   thiếu liệt kê `.locals_def`/`.macros` trong danh sách file phụ).

---

## 5. Danh sách [Unverified] — cần verify thêm trước khi tin tuyệt đối

- Full field list của các type hệ thống không nằm trong repo abapGit (không tự fetch được):
  `DDDDLSRCV` (DDLS), `CL_DDLX_WB_OBJECT_DATA=>TY_OBJECT_DATA` (DDLX), `ACM_S_DCLSRC` (DCLS),
  `CL_BLUE_SOURCE_OBJECT_DATA=>TY_OBJECT_DATA`/`-METADATA` (BDEF), `CL_SRVD_WB_OBJECT_DATA=>
  TY_SRVD_OBJECT_DATA` (SRVD), `CL_SRVB_OBJECT_DATA=>TY_OBJECT_DATA` (SRVB). Spec ở §2 chỉ liệt kê field
  thật sự xuất hiện trong source/ví dụ đã đọc — có thể còn field khác chưa biết tới.
- BDEF: field/cơ chế "implementation_type" (chiều tạo, `adtTemplate`) vẫn chưa verify được — 17 ví dụ
  thật đọc được đều là chiều serialize, không nói lên được chiều tạo (xem §2 BDEF).
- TABL: `DD05M` (foreign key) — quy tắc chính xác cho `FORTABLE` (trỏ bảng cha hay chính bảng đó) chưa
  xác định được, 2 ví dụ thật cho kết quả khác nhau (xem §2 TABL).
- DCLS: hành vi `SAVE` khi object đã tồn tại (pull lại) — source chỉ thấy `iv_access_mode='INSERT'`
  hardcode, chưa thấy nhánh update.
- SRVB: tên field chính xác cho "loại/version binding" và "tham chiếu service definition" lấy từ ví dụ
  thật, KHÔNG từ verify-source (class xử lý field này opaque, không đọc theo tên).
- `SEO_CLASS_CREATE_COMPLETE`/`SEO_INTERFACE_CREATE_COMPLETE` có được released cho ABAP Cloud runtime
  hay không — không xác nhận được (không chặn hướng abapGit-staging, vì đây là nội bộ abapGit tự gọi).
- Toàn bộ spec này verify trên abapGit `main` branch tại 1 commit cụ thể (2026-07) — SAP system thật của
  Acme có thể chạy version abapGit khác (cũ hơn/mới hơn), cần đối chiếu version thật đang cài (xem
  `.abapgit.xml` hoặc UI abapGit trong hệ thống) nếu có sai khác khi áp dụng thực tế.
