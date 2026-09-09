# Tra cứu CDS View theo phân hệ (Module → CDS)

Mục đích: khi đọc Function Spec, **xác định phân hệ SAP** (qua keyword nghiệp vụ), rồi
**tra đúng CDS View nguồn** trong catalog `docs/Phan_He_SAP_MD/`, thay vì tự bịa tên view.

> ⚠️ **REALITY FILTER**: Catalog này **chỉ liệt kê tên + mô tả + Application Component +
> Data Category** của CDS view. Nó **KHÔNG** chứa cột "released state". Vì vậy việc một
> view có mặt trong catalog **không** đồng nghĩa nó đã released cho Cloud Public 2602.
> Luôn cross-check released theo `released-objects-2602.md` + nguồn chính thống SAP
> (xem mục 4) trước khi dùng làm base view.

## 1. Catalog ở đâu

`docs/Phan_He_SAP_MD/<MODULE>.md` — mỗi file là 1 phân hệ, chứa bảng:

| Cột | Ý nghĩa |
|-----|---------|
| Name | Tên CDS view (vd `I_JOURNALENTRYITEM`, `C_OVERDUEPO`) |
| CDS View End User Description / Description | Mô tả nghiệp vụ — dùng để match keyword FS |
| Application Component | Sub-module (vd `FI-GL-IS`, `MM-PUR-ANA`) — lọc đúng nghiệp vụ |
| Data Category | `Dimension` / `Cube` / `Fact` / `nan`… — gợi ý loại view |

## 2. Bảng phân hệ (file → diễn giải + sub-component thực tế)

Cột "Sub-component" lấy **trực tiếp từ cột Application Component trong file** (verified) — dùng
để biết file chứa nghiệp vụ gì + grep cho đúng. Cột "Diễn giải" theo mã chuẩn SAP; mã hiếm
gặp / đa nghĩa đánh `[Unverified]`.

| File | Diễn giải | Sub-component thực tế (mẫu) |
|------|-----------|-----------------------------|
| `FI.md`  | Financial Accounting | `FI-GL-*`, `FI-AR-*`, `FI-AP-*`, `FI-AA`, `FI-LOC-*` |
| `CO.md`  | Controlling | `CO-*` |
| `SD.md`  | Sales & Distribution | `SD-*` |
| `MM.md`  | Materials Management | `MM-PUR-*`, `MM-IM-*` |
| `PP.md`  | Production Planning | `PP-*` |
| `PM.md`  | Plant Maintenance | `PM-*` |
| `QM.md`  | Quality Management | `QM-*` |
| `LE.md`  | Logistics Execution | `LE-*` |
| `SCM.md` | Supply Chain Management | `SCM-*` |
| `TM.md`  | Transportation Management | `TM-*` |
| `PLM.md` | Product Lifecycle Management | `PLM-*` |
| `RE.md`  | Real Estate Management | `RE-*` |
| `PSM.md` | Public Sector Management | `PSM-*` |
| `CRM.md` | Customer Relationship Management | `CRM-*` |
| `AP.md`  | Master Data nền tảng — Business Partner | `AP-MD-BP`, `AP-MD-BP-RAP` |
| `CA.md`  | Cross-Application (generic functions, ATP, bank) | `CA-GTF-*`, `CA-ATP-*`, `CA-BK-BNK` |
| `BC.md`  | Basis Components | `BC-*` |
| `LO.md`  | Logistics – General (BOM, batch, master data) | `LO-MD-BOM`, `LO-BM-MD`, `LO-AB` |
| `EC.md`  | Enterprise Controlling — Profit Center Accounting | `EC-PCA-MD` |
| `FIN.md` | Financial Supply Chain Management (Treasury/Cash/Collections/Dispute) | `FIN-FSCM-TRM`, `-CLM-BAM`, `-COL`, `-DM` |
| `FS.md`  | Financial Services — Insurance Claims Management | `FS-CM` (Insurance Claim) |
| `FT.md`  | Foreign Trade — Intrastat / International Trade | `FT-ITR-CLS`, `FT-ITR-TRC` |
| `CM.md`  | Legal Content Management (Legal Document/Transaction) | `CM-CAT`, `CM-CTX`, `CM-DOC`, `CM-LT`, `CM-GF` |
| `PPM.md` | Enterprise Portfolio & Project Mgmt (Enterprise Project, Billing) | `PPM-SCL-STR`, `PPM-SCL-BIL` |
| `SLC.md` | Supplier Lifecycle & Collaboration | `SLC-SUP`, `SLC-CAT` |
| `SUS.md` | Supplier Self-Services | `SUS-PFM-INT`, `SUS-INT` |

> Tài sản cố định nằm trong `FI.md` dưới `FI-AA`. Khi FS nói "tài khoản/journal/GL" → `FI-GL`;
> "công nợ phải thu/khách hàng" → `FI-AR`; "công nợ phải trả/nhà cung cấp" → `FI-AP`.

## 2c. Tra Z* custom app trong FS → `PUB_ACME_CODE` (BẮT BUỘC trước khi đánh ❌/placeholder)

FS của ACME thường ghi nguồn field dạng **`[App] Zxxx`** (custom app/CDS do dự án/đối tác xây,
KHÔNG phải released SAP). Trước đây các field này hay bị đánh "ngoài released → placeholder".
**Quy ước mới**: các Z* app này **đã có sẵn** trong repo `PUB_ACME_CODE/` (codebase ACME core). LUÔN
tra ở đó trước khi kết luận field không có nguồn.

> `PUB_ACME_CODE/` là abapGit serialization của package core ACME. Cấu trúc thay đổi theo thời gian
> (đã từng phẳng, nay nằm dưới `PUB_ACME_CODE/src/...`). **Luôn dùng Glob/find theo tên** thay vì
> hardcode đường dẫn.
>
> ⛔ **`PUB_ACME_CODE/` READ-ONLY**: chỉ Read/Glob/Grep/find để **tham khảo**. TUYỆT ĐỐI KHÔNG
> Write/Edit/tạo/xoá/ghi-đè bất cứ file nào trong `PUB_ACME_CODE/`. Cần tái sử dụng view ACME →
> tham chiếu tên (assoc/select) hoặc copy ra `source code/<story>/` rồi sửa bản copy.

### Bảng tra nhanh `[App]` trong FS → view ACME (verified 2026-06-27)

| FS `[App]` | Thư mục PUB_ACME_CODE | Interface view | Field tiêu biểu |
|------------|-------------------|----------------|-----------------|
| `ZCOMPANY` | `src/zfpt_all/zcompany` | `ZI_ACME_COMPCODE` | TenCtyVN/TenCtyEN, DiaChiVN/EN, Mail, Phone, Fax, MST |
| `ZPARTNER` | `src/zfpt_all/zbpartner` | `ZI_ACME_BPARTNER` | BPName, BPAddress, BPTelephone, BPFax, BPTaxNumber |
| `ZBANKEY` / `ZBANKKEY` | `src/zfpt_all/zbankkey` | `ZI_ACME_BANKKEY` | BankName, BankAddress, SWIFTCode, BankBranch |
| `ZPLANT` | `src/zplant` hoặc `src/zfpt_all/zplant` | `ZI_ACME_PLANT` | Plant master |
| `ZMATDOC` | `src/zmatdoc` | `ZI_ACME_ZMATDOC` | Material document |
| Print PDF / Adobe Forms | `src/zfpt_report/.../` (mẫu `zwm/zwm11`), `src/zfpt_function/zattachment`, `src/zfpt_core/zfunction/zads` | `cl_fp_ads_util=>render_pdf`, `zcl_fp_tmpl_store_client=>get_template_by_tcode`, `zcl_core_util=>abap2xml`, BO `zr_attachment` | framework in PDF |
| Excel upload/export | `src/zfpt_function/zxlsx`, `src/zfpt_core/zexcel` | `ZCL_*` XCO XLSX | framework Excel |
| Attachment / file | `src/zfpt_function/zattachment` | `ZI_ATTACHMENT(p_module_obj,p_app_id)`, BO `zr_attachment` | lưu file/PDF |
| Tax | `src/zfpt_function/ztax` | `ZI_TAX_CODE`, `ZC_TAX_GROUP` | thuế |
| FSV / variant | `src/zfpt_function/zfsv`, `zvariant` | `ZI_FSV*`, `ZI_VARIANT*` | layout/variant |

### Quy trình tra Z* app
```bash
# 1) Tìm thư mục app theo keyword:
find PUB_ACME_CODE -type d -iname "*company*"
# 2) Tìm interface view (ZI_*) + xem field:
find PUB_ACME_CODE -iname "zi_nfg_compcode.ddls.asddls"
# 3) Đọc view để lấy đúng tên field, KHÔNG bịa.
```
- Match keyword nghiệp vụ (company/partner/bank/plant/material/attachment/excel/print) → thư mục.
- Ưu tiên `ZI_*` (interface) làm assoc nguồn; consumption `ZC_*` chỉ để tham khảo UI.
- Nếu app Z* **không có** trong PUB_ACME_CODE → khi đó mới đánh placeholder + đưa vào INTAKE §6.
- Pattern **report + Print PDF**: tham chiếu `PUB_ACME_CODE/src/zfpt_report/zwm/zwm11/zwm11a`
  (RAP report + `action Print` → ADS render → `zr_attachment`). Xem
  `docs/stories/ACME_SAP_2026_TH_ZSD02` làm ví dụ áp dụng.

## 3. Quy trình tra cứu (bắt buộc khi đọc FS)

1. **Nhận diện phân hệ** từ keyword nghiệp vụ trong FS:
   - "phiếu kế toán / journal / GL / tài khoản" → **FI** (`FI-GL-*`)
   - "đơn mua / purchase order / PR / contract / supplier" → **MM** (`MM-PUR-*`)
   - "đơn bán / sales order / billing / delivery" → **SD**
   - "tài sản cố định / asset" → **FI-AA** (trong `FI.md`)
   - "giá thành / cost center / internal order" → **CO**
   - "sản xuất / production order / BOM" → **PP**
   - "bảo trì / maintenance order / equipment" → **PM**
   - "kho / inbound / outbound / handling unit" → **LE**
   - "freight order / transportation order / freight unit / vận chuyển TM / carrier / biển số xe / chuyến" → **TM** (`TM.md`, views `I_TransportationOrder*_2`, xem §ZSD18 Knowledge trong `TM.md`)
   - (không rõ → ghi vào INTAKE mục 6 "cần làm rõ phân hệ").
2. **Mở** `docs/Phan_He_SAP_MD/<MODULE>.md`, search theo keyword tiếng Anh
   (Description) hoặc Application Component.
3. **Ưu tiên view nền (VDM)**:
   - `I_*` = interface/basic VDM view (thường là nền tái sử dụng) → ưu tiên làm base.
   - `C_*` = consumption/analytical (cube, query) → dùng cho báo cáo phân tích.
   - `P_*` / `F_*` / `R_*` = private/derived → tránh dùng trực tiếp.
4. **Cross-check RELEASED** (catalog không nói released — xem reality filter ở đầu file):
   - Theo `released-objects-2602.md` + ATC "Released APIs" trong ADT.
   - Hoặc app **View Browser** / **CDS Views** trên tenant thật (Eclipse ADT / Fiori).
5. **Ghi kết quả** vào INTAKE mục nguồn field + TECHNICAL_SPEC (tên CDS base + released state +
   nếu chưa chắc thì đánh `[Unverified]`).

## 3b. Cách tra hiệu quả (file ~1.2MB — KHÔNG đọc cả file)

Mỗi file catalog rất lớn → **luôn dùng Grep theo keyword**, không Read nguyên file (tránh tràn context):

```bash
# Tìm theo nghiệp vụ (Description) trong 1 phân hệ:
grep -iE "journal entry|voucher" docs/Phan_He_SAP_MD/FI.md

# Lọc theo sub-component:
grep -E "FI-GL" docs/Phan_He_SAP_MD/FI.md

# Chỉ lấy view nền I_* (bỏ cube/analytical C_*):
grep -E "I_[A-Z]" docs/Phan_He_SAP_MD/MM.md | grep -i "purchase order"
```

Với tool Grep: `glob="docs/Phan_He_SAP_MD/<MODULE>.md"`, `output_mode="content"`, đặt `head_limit`
hợp lý. Lấy ra danh sách ngắn ứng viên rồi mới quyết định.

## 4. Khi CDS chưa released HOẶC không đáp ứng FS

Nếu view tìm được **chưa released cho Cloud Public 2602**, hoặc **thiếu field/association**
mà FS yêu cầu → tìm thêm theo thứ tự **nguồn chính thống SAP** (KHÔNG tự bịa):

1. **SAP Business Accelerator Hub** — https://api.sap.com/ → search CDS / OData, lọc
   "SAP S/4HANA Cloud Public Edition", check tab API State (C1/released).
2. **SAP Help Portal** — https://help.sap.com/ → "CDS Views" của phân hệ tương ứng (release 2602).
3. **SAP Fiori apps reference library** — https://fioriappslibrary.hana.ondemand.com/ →
   tìm app nghiệp vụ → xem OData service + CDS phía sau.
4. **MCP read-only** (nếu kết nối được tenant): `SearchObject` / `GetTypeInfo` / `CheckView` —
   verify object tồn tại + field + released **trực tiếp trên tenant**. CHỈ tool đọc, không tool ghi.
5. **ADT "Released APIs"** + app **View Browser** trên tenant thật (Eclipse ADT) — fallback khi MCP
   không kết nối (Cloud Public cần SSO); verify thủ công.
6. **SAP Notes / Community** chỉ dùng để tham khảo, **không** thay thế API State.

Quy tắc: mọi tên view/field lấy từ nguồn ngoài catalog phải **ghi rõ nguồn** trong
TECHNICAL_SPEC; nếu chưa kiểm chứng trên tenant → đánh `[Unverified]` và đưa vào mục
"cần làm rõ / cần spike".

## Reference

- Catalog: `docs/Phan_He_SAP_MD/<MODULE>.md`
- Released state: `docs/sap-knowledge/released-objects-2602.md`
- Naming: `docs/sap-knowledge/naming-conventions.md`
- Kết nối tenant (abapGit): `scripts/sap-connection/README.md`
