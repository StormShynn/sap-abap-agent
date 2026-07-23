# Customer Landscape — thông tin cần biết cho mỗi KH

Khi bắt đầu làm cho KH mới, **điền thông tin vào file này** (copy từ template bên dưới).
Mục đích: agent luôn biết KH dùng package nào, namespace nào, có dùng add-on nào không.

## Template (copy và điền)

```markdown
# Customer: <Tên KH> — <Project code>

## System
- **S/4HANA release**: <2602 / 2605 / ...>
- **Edition**: Public / Private
- **Instance URL**: <https://myxxxxxx.sapbydesign.com hoặc URL tương đương>
- **Client**: <100 thường là default>
- **Sandbox/Trail system**: <URL nếu có>

## Package (chứa custom object)
- **Main package**: <VD: ZITC_SCM, ZITC_FI>
- **Sub-packages**:
  - `ZITC_SCM_PO` — Purchase Order
  - `ZITC_SCM_GR` — Goods Receipt
  - ...

## Namespace
- **Prefix chính**: `Z` (hoặc `Y`, tuỳ KH)
- **Project prefix riêng**: <VD: `ZTB_ITC_*` thay vì `ZTB_*` chung>
- **Soft namespace / reserved**: <nếu có>

## Transport
- **Transport layer**: <VD: ZPHA (custom), SAP (standard)>
- **Transport request pattern**: <VD: ITC_Kxxxxx (request từ BA)>
- **Change request (CR) workflow**: <mô tả ngắn>

## Released status
- KH đã subscribe dịch vụ nào: <VD: BTP, Ariba, Concur, ...>
- Extension include nào đã activate: <VD: V_T163K_E, V_TVAP_E>
- Có dùng Developer Extensibility (Custom Fields, Custom Logic): <Yes/No>

## Toolchain
- **IDE**: Eclipse ADT / BAS
- **abapGit**: <Có dùng không, repo ở đâu>
- **SAP BTP account**: <nếu có, subaccount, region>
- **Git server**: <GitHub / GitLab / Bitbucket on-prem>

## Conventions riêng của KH
- <VD: Tất cả custom object phải có comment "ITC SAP 2025 - Team ABC">
- <VD: Number range dùng 51-60 cho PO, 61-70 cho GR>
- <VD: Bắt buộc có ABAP Unit test, coverage > 80%>

## Key person
- **Tech lead KH**: <tên, email, phone>
- **BA KH**: <tên, email>
- **Basis KH**: <tên, email>

## Note
- <Điều đặc biệt: KH dùng add-on IS-Oil / IS-Media, hoặc có integration với hệ legacy>
- <Điều cần tránh: KH ghét RAP, dùng OO ABAP truyền thống>
```

## Ví dụ: Initech (project đầu tiên)

```markdown
# Customer: Initech — ITC_SAP_2025_TH

## System
- **S/4HANA release**: 2602
- **Edition**: Public
- **Instance URL**: https://myxxxxxx.sapbydesign.com
- **Client**: 100

## Package
- **Main package**: ZITC
- **Sub-packages**:
  - `ZITC_SCM_PO` — Purchase Order
  - `ZITC_SCM` — SCM master data

## Namespace
- **Prefix**: `Z` chung, KH chấp nhận
- **Project prefix**: dùng `ZTB_PO*`, `ZI_PO*`, `ZR_PO*` (không prefix ITC)

## Transport
- **Layer**: ZITC
- **TR pattern**: ITC_SAP_Kxxxxx

## Toolchain
- **IDE**: Eclipse ADT
- **abapGit**: có, repo GitHub của team
- **BAS**: có, dùng cho SAPUI5 custom

## Note
- KH thích Fiori Elements, ít custom UI5
- Function Spec template ở: `examples/ITC_FS_SCM_Đơn-đặt-hàng-PO_V1.01.docx`
```

## Acme Group — ACME_SAP_2026_TH

```markdown
# Customer: Acme Group — ACME_SAP_2026_TH

## System
- S/4HANA release: 2602 — Edition: Public

## Namespace / Naming
- Prefix Z chung. Object đặt theo **mã báo cáo** (ZSD01, ZSD02, ZGL07…), KHÔNG theo tên nghiệp vụ.
  3-layer: ZI_<code> → ZR_<code> → ZC_<code>; service ZUI_<code>_O4.

## ACME core codebase — `PUB_ACME_CODE/` (BẮT BUỘC tra trước khi đánh field "ngoài released")
FS ACME ghi nguồn field dạng `[App] Z*` = custom view có sẵn trong `PUB_ACME_CODE/` (abapGit serialization).
Cấu trúc đổi theo thời gian (nay `PUB_ACME_CODE/src/...`) → luôn `find`, đừng hardcode path.

> ⚠️ **4 master view dưới đã có sẵn & active trong core `PUB_ACME_CODE` (đã cập nhật mới — verified 2026-06-30).**
> → Khi project object cần → **chỉ tham chiếu tên** (assoc / select), **TUYỆT ĐỐI KHÔNG sinh file copy**
> trong `source code/<story>/` (copy dễ bị stale so với core). Mỗi view có bản interface `ZI_*` (đầy đủ field)
> và bản consumption `ZC_*` (đã gắn `@EndUserText.label` tiếng Việt, dùng cho value help / UI).
> Field/path lấy từ `pub-naf-index.json` (đã rebuild).

| FS `[App]` | Interface view | Consumption | Thư mục | Key | Field chính (interface) |
|------------|----------------|-------------|---------|-----|--------------------------|
| ZCOMPANY | `ZI_ACME_COMPCODE` | `ZC_ACME_COMPCODE` | `src/zfpt_all/zcompany` | `CompanyCode` | `TenSort`, `TenCtyVN`, `TenCtyEN`, `DiaChiVN`, `DiaChiEN`, `Mail`, `Web`, `Phone`, `MST`(VAT), `Fax` |
| ZPARTNER | `ZI_ACME_BPARTNER` | `ZC_ACME_BPARTNER` | `src/zfpt_all/zbpartner` | `BusinessPartner` | `BPName`, `BPAddress`, `BPTaxNumber`, `BPTelephone`, `BPFax`, `BPEmail`, `BusinessPartnerCategory/Grouping` |
| ZBANKEY/ZBANKKEY | `ZI_ACME_BANKKEY` | `ZC_ACME_BANKKEY` | `src/zfpt_all/zbankkey` | `BankCountry`+`BankKey` | `BankName`, `BankBranch`, `BankAddress`, `BankCity`, `BankCountryName`, `SWIFTCode`, `BankCategory` |
| ZPLANT | `ZI_ACME_PLANT` | `ZC_ACME_PLANT` | `src/zfpt_all/zplant` | `Plant` | `PlantName`, `PlantAddress`, `CompanyCode` |
| ZMATDOC | `ZI_ACME_ZMATDOC` | — | `src/zfpt_all/zmatdoc` | — | (tra index trước khi dùng) |

> Helper liên quan: `ZI_ADDR` (`src/zfpt_all/zbpartner`) — chuẩn hoá địa chỉ BP (street/city/region/country,
> email), được `ZI_ACME_BPARTNER` join inner. Cũng KHÔNG copy.

Framework dùng lại: Print PDF (`src/zfpt_report/zwm/zwm11` + `cl_fp_ads_util` + `zcl_fp_tmpl_store_client`
+ BO `zr_attachment` ở `src/zfpt_function/zattachment`), Excel (`src/zfpt_function/zxlsx`),
util (`zcl_core_util` ở `src/zfpt_core/zutil`). Chi tiết: `cds-by-module.md` §2c.

## Note
- Output FS ghi "ALV" → Public Cloud dùng Fiori Elements List Report.
- Báo cáo có in PDF → pattern report + action Print (xem ZSD02 + ADR-0017).
```

## Cập nhật

Khi bắt đầu làm cho KH mới:
1. Copy template vào `<mã KH>.md`.
2. Điền thông tin từ KH (hỏi BA hoặc tech lead).
3. Commit vào git để team thấy.
4. Update `AGENTS.md` section "Quy ước bắt buộc" nếu KH có convention khác.
