# Tài sản tái sử dụng — class/pattern team đã viết (REUSE trước khi viết mới)

> Đây là **knowledge pack của `AGENTS_REUSE`** (module expert tài sản dự án). Trước khi đề xuất
> class/logic mới, agent **PHẢI** kiểm tra danh sách này + grep `source code/` + tra
> `PUB_ACME_CODE/` (read-only) + `docs/stories/`. Ưu tiên **tái sử dụng / tham chiếu**, không viết lại.
> `AGENTS_REUSE` cập nhật file này khi phát hiện asset dùng chung mới (cơ chế "học").

## 0. Bản đồ `PUB_ACME_CODE/src/` — KHO CODE DỰ ÁN CHÍNH (read-only)

Nguồn reuse số 1. Luôn Glob/Grep (cấu trúc có thể đổi), đừng hardcode path.

| Vùng | Chứa | Tra khi cần |
|------|------|-------------|
| `zfpt_core/` | `zbo` `zexcel` `zfunction` `zlogo` `zutil` `zview` | util chung (`zcl_core_util`), base view, BO core |
| `zfpt_function/` | `zads_form` `zattachment` `zxlsx` `ztax` `zvariant` `zfpt_extract` | in PDF (Adobe), đính kèm, excel, thuế, variant |
| `zfpt_int/` | `zint_log` `zint_mm` `zint_mfg` `zfpt_einv` `zint_demo` | integration API, logging, e-invoice |
| `zfpt_report/<mod>/` | `zfi` `zmm` `zsd` `zqm` `zwm` `zam` `zcm` `zmfg` `ztr` | **report đã làm theo từng phân hệ** — tham khảo trước khi làm report mới |
| `zfpt_all/` | `zcompany` `zbpartner` `zbankkey` `zmatdoc` `zplant` | master data view `ZI_ACME_*` (Company/Partner/Plant…) |

Ví dụ: `find PUB_ACME_CODE/src -iname "zi_nfg_*"` · `find PUB_ACME_CODE/src/zfpt_report/zsd -iname "*.clas.abap"`.

## 1. Integration logging (BẮT BUỘC cho mọi API)

| Asset | File | Dùng để |
|-------|------|---------|
| `ZCL_LOG_INT=>logger()` | `source code/zint_log/zcl_log_int.clas.abap` | Ghi log request/response API (EML CREATE, có pack + attachment JSON). Gọi trong determination on save. |
| BO `ZR_LOG_INT` / `ZR_LOG_INT_PACK` | `source code/zint_log/` | Log header/detail + action Retry |

## 2. In form PDF (Adobe Forms / ADS)

| Asset | File | Dùng để |
|-------|------|---------|
| Pattern `zcl_<x>_print` | `zcl_gl07_print`, `zcl_am03_print`, `zcl_zsd02_print` (trong `source code/ACME_*`) | Chuẩn bị data + render PDF. Copy pattern, đổi tên. |
| Helper calc | `zcl_am03_calc`, `zcl_aa01_calc`, `zcl_gl07_user_valid` | Logic tách/tính/validate tách khỏi behavior (dễ test) |
| Framework render (ACME core) | `cl_fp_ads_util=>render_pdf`, `zcl_fp_tmpl_store_client`, `zcl_core_util=>abap2xml`, BO `zr_attachment` | Ở `PUB_ACME_CODE/` — **read-only**, chỉ gọi/tham chiếu |

## 3. Excel upload / export

| Asset | File | Dùng để |
|-------|------|---------|
| Upload XLSX | `source code/zxlsx/zimport/zcl_import_excel_xlsx.clas.abap`, `zcl_excel_upload_v1` | Đọc file Excel → internal table |
| Export XLSX | `source code/zxlsx/zexport/zcl_export_excel_xlsx.clas.abap`, `zcl_merge_export_excel_xlsx` | Sinh file Excel |
| Builder theo BO | `source code/zmfg10/zcl_mfg10_xlsx_builder.clas.abap`, `ACME_*_ZSD06/zcl_zsd06_xlsx_builder` | Mẫu builder gắn RAP |
| Check/format | `zxlsx/zimport/zcl_check_amount`, `zcl_check_number`, `zcl_format_quan` | Validate/format cell |

## 4. Integration API (RAP)

| Asset | File | Dùng để |
|-------|------|---------|
| Inbound managed (behavior pool mẫu) | `source code/ACME_INT_ZMM05/zbp_r_zmm05_h.clas.abap`, `ZMM06` | Skeleton RAP managed + draft + 2 binding |
| Outbound read-only (query) | `source code/ACME_INT_ZMM07/zcl_zmm07_query.clas.abap` | `IF_RAP_QUERY_PROVIDER` — đọc dữ liệu từ SAP qua $filter |

## 5. Report SD — pattern 3-layer ZI/ZR/ZC (read-only List Report)

| Asset | Path | Dùng để |
|-------|------|---------|
| `ZI_ZSD01` | `PUB_ACME_CODE/src/zfpt_report/zsd/zsd01/zi_zsd01.ddls.asddls` | Layer ZI: I_OutboundDeliveryItem + I_OutboundDelivery. Pattern assoc Delivery→SalesOrg→CompanyCode |
| `ZR_ZSD01` | `source code/ACME_SAP_2026_TH_ZSD01/zr_zsd01.ddls.asddls` | Layer ZR: assoc ZI_ACME_COMPCODE + ZI_ACME_BPARTNER (Buyer/Consignee). Mẫu flatten multi-join |
| `ZC_ZSD01` | `source code/ACME_SAP_2026_TH_ZSD01/zc_zsd01.ddls.asddls` | Layer ZC: @Consumption.valueHelpDefinition cho mọi filter param SD |
| `ZR_ZSD01.dcls` | `source code/ACME_SAP_2026_TH_ZSD01/zr_zsd01.dcls.asdcls` | Access control mẫu + comment `pfcg_auth(SalesOffice)` chờ auth object |
| `ZI_ZSD02` | `source code/ACME_SAP_2026_TH_ZSD02/src/zcds/zi_zsd02.ddls.asddls` | Thêm assoc I_SalesOrder / I_SalesOrderItem (ReferenceSDDocument) từ Delivery Item |

## 6. Virtual element — IF_SADL_EXIT_CALC_ELEMENT_READ

| Asset | Path | Dùng để |
|-------|------|---------|
| `ZCL_VIRTUAL_ZQM02` | `PUB_ACME_CODE/src/zfpt_report/zqm/zqm02/zcl_virtual_zqm02.clas.abap` | **Pattern hoàn chỉnh**: implements `if_sadl_exit` + `if_sadl_exit_calc_element_read`, CAST original_data → lt_data, LOOP ASSIGN FIELD-SYMBOL, gán calculated field. Copy + đổi tên |
| `ZCL_VE_ZMFG02` | `PUB_ACME_CODE/src/zfpt_report/zmfg/zmfg02/zcl_ve_zmfg02.clas.abap` | Pattern virtual element gọi OData external API trong calculate() |
| `ZC_QM_ZQM02` (khai báo virtual) | `PUB_ACME_CODE/src/zfpt_report/zqm/zqm02/zc_qm_zqm02.ddls.asddls` | Syntax: `@ObjectModel.virtualElementCalculatedBy: 'ABAP:ZCL_...'` + `virtual FieldName : abap.char(N)` trước field |
| `ZCL_VIRTUAL_COMPANY_N` | `PUB_ACME_CODE/src/zfpt_core/zview/zcl_virtual_company_n.clas.abap` | Virtual element đơn giản (Phone) trong view Company |

## 7. ACME Master Data views (ZI_ACME_*)

| Asset | Path | Fields chính |
|-------|------|-------------|
| `ZI_ACME_COMPCODE` | `PUB_ACME_CODE/src/zfpt_all/zcompany/zi_nfg_compcode.ddls.asddls` | `CompanyCode`, `TenSort`, `TenCtyVN`, `TenCtyEN`, `StreetPrefixName2`, `CityName`, `DiaChiVN`, `DiaChiEN`, `AddressID`, `AddressPersonID`, `Mail`, `Web`, `Phone`, `PhoneAreaCodeSubscriberNumber`, `PhoneNumberCountry`, `Fax`, `MST`. Sources: `I_CompanyCode`, `I_Address_2` (IMG "Edit Addresses for Company Codes"), `I_AddressEmailAddress_2`, `I_AddressFaxNumber_2`, `I_AddressPhoneNumber_2`, `I_AddressMainWebsiteURL`, `ZI_COMPANY_RAW`. Đã reuse bởi `ZC_ACME_COMPCODE`, `ZI_ZCM01_COMPANYINFO`, `ZI_ZGL07_PHIEUKETOAN`, `ZR_ZSD01` — view chuẩn dự án cho mọi nhu cầu "tên + địa chỉ Company Code" (report FI/SD/CM) |
| `ZI_ACME_BPARTNER` | `PUB_ACME_CODE/src/zfpt_all/zbpartner/zi_nfg_bpartner.ddls.asddls` | `BusinessPartner`, `BPName` (case org/person), `BPAddress`, `BPTaxNumber`, `BPTelephone`, `BPFax` |
| `ZI_ACME_BANKKEY` | `PUB_ACME_CODE/src/zfpt_all/zbankkey/zi_nfg_bankkey.ddls.asddls` | Bank master |
| `ZI_ACME_ZMATDOC` | `PUB_ACME_CODE/src/zfpt_all/zmatdoc/zi_nfg_zmatdoc.ddls.asddls` | Material document |
| `ZI_ACME_PLANT` (via zplant) | `PUB_ACME_CODE/src/zfpt_all/zplant/` | Plant master |

## 8. Access control — phân quyền Sales Office

| Asset | Path | Pattern |
|-------|------|---------|
| `ZR_ZSD01.dcls` | `source code/ACME_SAP_2026_TH_ZSD01/zr_zsd01.dcls.asdcls` | `grant select on ZR_ZSD01 where (SalesOffice) = aspect pfcg_auth( <Z_AUTH_OBJ>, ACTVT='03')` — hiện comment-out, chờ confirm auth object |
| `ZC_ZSD01.dcls` | `source code/ACME_SAP_2026_TH_ZSD01/zc_zsd01.dcls.asdcls` | `where inheriting conditions from entity ZR_ZSD01` — pattern cascade |
| `ZR_EINV_HDR.dcls` | `PUB_ACME_CODE/src/zfpt_int/zfpt_einv/zr_einv_hdr.dcls.asdcls` | **Access control theo Company Code** (duy nhất trong dự án dùng auth object chuẩn SAP): `grant select on ZR_EINV_HDR where (CompanyCode) = aspect pfcg_auth(F_BKPF_BUK, BUKRS, ACTVT = '03')`. Reuse cho report FI/AP/AR cần phân quyền theo Company Code — copy cú pháp, đổi field bind. `F_BKPF_BUK` cần verify released/active trên tenant KH trước khi dùng thật [Unverified] |

## 9. Helper util core (PUB_ACME_CODE — read-only, chỉ gọi)

| Asset | Path | Methods chính |
|-------|------|--------------|
| `ZCL_CORE_UTIL` | `PUB_ACME_CODE/src/zfpt_core/zutil/zutil_core/zcl_core_util.clas.abap` | `dt_to_utc`, `dt_format_tsl_to_str(pattern)`, `get_last_day_of_month`, `amount_to_word`, `amount_format`, `quantity_format` |
| `ZCL_UTIL_DATETIME` | `PUB_ACME_CODE/src/zfpt_core/zutil/zutil_impl/zcl_util_datetime.clas.abap` | `format_tsl_to_str(pattern YYYY-MM-dd)`, `get_last_day_of_months`, `to_utc(tsl, tz)` |
| `ZCL_EXPORT_EXCEL_XLSX` | `PUB_ACME_CODE/src/zfpt_function/zxlsx/zexport/zcl_export_excel_xlsx.clas.abap` | `export_excel(template, report, data, generate)` |
| `ZCL_MERGE_EXPORT_EXCEL_XLSX` | `PUB_ACME_CODE/src/zfpt_function/zxlsx/zexport/zcl_merge_export_excel_xlsx.clas.abap` | Merge-style export |
| `ZCL_EXCEL_UPLOAD_V1` | `PUB_ACME_CODE/src/zfpt_function/zxlsx/zcl_excel_upload_v1.clas.abap` | Upload XLSX |

## 10. Pattern RAP managed + Z table lưu note (editable column trong read-only report)

| Asset | Path | Mô tả |
|-------|------|-------|
| `ZTB_SD_ZSD06` + `ZR_ZSD06` | `source code/ACME_SAP_2026_TH_ZSD06/zr_zsd06.ddls.asddls` | Mẫu `define root view entity` từ custom Z table (UUID PK, SalesOffice, etag). **Pattern gần nhất** cho Z table lưu note theo key |
| `ZTB_SD_ZSD06.tabl` | `source code/ACME_SAP_2026_TH_ZSD06/ztb_sd_zsd06.tabl.xml` | Cấu trúc table: UUID_X16, SALES_OFFICE, ATTACHMENT, timestamps (created/changed) |
| `ZR_ZSD06.bdef` | `source code/ACME_SAP_2026_TH_ZSD06/zr_zsd06.bdef.asbdef` | Managed + draft + `authorization master (instance)`. Copy pattern cho Z table note |

## 11. Nơi tra thêm (thứ tự ưu tiên)

1. **`PUB_ACME_CODE/src/...`** — kho code dự án chính (xem bản đồ §0), **read-only**.
2. `source code/<story>/` — scaffold/chức năng đã làm trong harness (FI, AA, AM, SD, MM, MFG…).
3. `docs/stories/` — INTAKE/TECHNICAL_SPEC tham chiếu.

> Ghi chú: Freight Order (SAP TM) chưa có report nào trong dự án tra cứu được field `I_FreightOrder*` hoặc TM VDM view. Cần AGENTS_SD verify released API TM trong ADT trước khi build ZSD18.
