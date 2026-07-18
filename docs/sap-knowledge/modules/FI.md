# Knowledge Pack — Phân hệ FI (Financial Accounting)

> Bộ nhớ "đã học" của module-agent FI. Đọc trước khi tra catalog; ghi lại sau mỗi lần verify.
> ⚠️ Đây là **starter** — phần lớn released-state còn `[Unverified]`, PHẢI confirm trên
> api.sap.com / View Browser tenant trước khi dùng làm base. KHÔNG bịa.

**Sub-components**: `FI-GL` (sổ cái), `FI-AR` (phải thu/khách hàng), `FI-AP` (phải trả/NCC),
`FI-AA` (tài sản cố định), `FI-LOC-*` (localization).
**Catalog gốc**: `docs/Phan_He_SAP_MD/FI.md` (890 views)

## 1. CDS view nền (candidate — cần verify released)

| CDS view | Mục đích | Key fields (dự kiến) | Released 2602 | Nguồn |
|----------|----------|----------------------|---------------|-------|
| `I_JournalEntry` | Bút toán (header) | CompanyCode, FiscalYear, AccountingDocument | `[Unverified]` | catalog FI.md |
| `I_JournalEntryItem` | Dòng bút toán | + LedgerGLLineItem | `[Unverified]` | catalog FI.md |
| `I_OperationalAcctgDocItem` | Item kế toán vận hành | … | `[Unverified]` | catalog FI.md |
| `I_GLAccountLineItem` | Dòng sổ cái | … | `[Unverified]` | catalog FI.md |
| `I_GLAccountInChartOfAccounts` | TK sổ cái theo COA | ChartOfAccounts, GLAccount | `[Unverified]` | catalog FI.md |
| `I_CompanyCode` | Mã công ty | CompanyCode, `_Address`→AddressID | **released** | released-objects-index.json (`DDLS:I_COMPANYCODE`, ac=FI-GL-GL-N-2CL) |
| `I_AccountingDocumentType` | Loại chứng từ | AccountingDocumentType | `[Unverified]` | catalog FI.md |
| `I_JournalEntry` | Journal Entry **header** — có field `DocumentReferenceID` (= "Reference"/BKPF-XBLNR, KHÔNG có ở item view) | CompanyCode, FiscalYear, AccountingDocument, DocumentReferenceID, DocumentDate | **released** | released-objects-index.json (`DDLS:I_JOURNALENTRY`, ac=FI-GL-IS-2CL) |
| `I_OperationalAcctgDocItem` | FI-AP/AR/GL item — Manage Supplier/Customer Line Items app dùng view này | CompanyCode, FiscalYear, AccountingDocument, AccountingDocumentItem, Supplier, DocumentDate, GLAccount, Reference1/2/3IDByBusinessPartner (= UI "Reference Key 1/2/3"), TaxCode, TaxAmount, TaxAmountInCoCodeCrcy, TaxBaseAmountInCoCodeCrcy, AmountInCompanyCodeCurrency. **KHÔNG có** field "Reference"/"Base Amount" đơn giản — Reference (số hoá đơn) phải lấy từ `I_JournalEntry.DocumentReferenceID` (join qua CompanyCode+FiscalYear+AccountingDocument); "Base Amount" (giá trị hoá đơn trước thuế) không có field tên thẳng, gần nhất là `TaxBaseAmountInCoCodeCrcy`/`OriginalTaxBaseAmount` (cần xác nhận nghiệp vụ khớp) | **released** | released-objects-index.json (`DDLS:I_OPERATIONALACCTGDOCITEM`, ac=FI-GL-IS-2CL) + pmc-reuse-by-module.md (dùng 11×) + catalog FI.md dòng ~12599-13062 |
| `I_JournalEntryItem` | Dòng bút toán (cube, dùng 25× trong GLB) | CompanyCode, FiscalYear, AccountingDocument, DocumentDate, Supplier, GLAccount, TaxCode, TaxCountry. **KHÔNG có** Reference1/2/3IDByBusinessPartner, KHÔNG có DocumentReferenceID | **released** | released-objects-index.json (`DDLS:I_JOURNALENTRYITEM`) + catalog FI.md |
| `I_TaxCodeRate` | Rate/config tax code (cho Advance Return for Tax on Sales/Purchases — filter theo tax code + GL account 1331*) | TaxCode, ... | **released** | released-objects-index.json (`DDLS:I_TAXCODERATE`, ac=FI-GL-IS-2CL) + pmc-reuse-by-module.md (dùng 14×) |

> Keyword FS → view: "phiếu kế toán/journal/bút toán" → `I_JournalEntry(Item)`;
> "số dư/dòng sổ cái" → `I_GLAccountLineItem`; "tài khoản GL" → `I_GLAccountInChartOfAccounts`;
> "công ty" → `I_CompanyCode`. Tài sản cố định (FI-AA) → tra catalog `FI-AA`.

## 2. Business Object / RAP BO interface

| BO / Interface | Loại | Dùng cho | Released | Nguồn |
|----------------|------|----------|----------|-------|
| *(cần tra khi có nhu cầu write)* | | | | |

## 3. OData / API chuẩn (api.sap.com — candidate)

| API | Chiều | Mục đích | Released | Nguồn |
|-----|-------|----------|----------|-------|
| `API_JOURNALENTRYITEMBASIC_SRV` | read | Đọc journal entry item | `[Unverified]` | api.sap.com |
| Journal Entry – Post (Inbound) | write | Ghi bút toán (FS posting) | `[Unverified]` — confirm tên chính xác | api.sap.com |

## 4. Value help / dimension view hay dùng

| View | Cho field | Nguồn |
|------|-----------|-------|
| `I_AccountingDocumentType` | DocumentType | catalog FI.md |
| `I_OrganizationAddress` | Address công ty/tổ chức — Name1/2 (`AddresseeName1/2`), Street (`Street`/`StreetName`/`StreetPrefixName1/2`/`StreetSuffixName1/2` — KHÔNG có field literal "Street2"/"Street3"), `Region` (code, cần join `I_RegionText` lấy description), `Country` (code, assoc `_Country`→`I_Country` lấy description). Join với `I_CompanyCode` qua `I_CompanyCode.AddressID = I_OrganizationAddress.AddressID`. App IMG "Edit Addresses for Company Codes" dùng pattern này | released-objects-index.json (`DDLS:I_ORGANIZATIONADDRESS` ac=BC-SRV-ADR, `DDLS:I_COUNTRY`, `DDLS:I_REGION`, `DDLS:I_REGIONTEXT` — tất cả released) + catalog BC.md dòng 1111-1200 (KHÔNG nằm trong FI.md vì AC=BC-SRV-ADR) |

## 5. Ghi chú / pitfall đã học

- FI dữ liệu standard rất lớn → LUÔN grep catalog theo `FI-GL` / `FI-AR` / `FI-AP` để thu hẹp.
- Tài sản cố định nằm chung file FI.md dưới `FI-AA` (không tách file riêng).
- Đa số FS ACME là **đọc/in** (xem ZGL07) → ưu tiên 3-layer CDS read-only, không cần posting API.
- **Address view KHÔNG nằm trong `docs/Phan_He_SAP_MD/FI.md`** — application component `BC-SRV-ADR`
  → phải grep `docs/Phan_He_SAP_MD/BC.md`. Gotcha: nhiều field địa chỉ (company/vendor/customer) nằm
  ở catalog BC, không phải FI/MM/SD — luôn thử BC.md nếu cần Name1/Street/Region/Country.
- **`I_OperationalAcctgDocItem` (item-level) vs `I_JournalEntry` (header-level)**: field
  `Reference` (số hoá đơn, UI label "Reference" = BKPF-XBLNR) chỉ có ở **header** view
  `I_JournalEntry.DocumentReferenceID`, KHÔNG có ở item view. Field "Reference Key 1/2/3"
  (UI label) lại chỉ có ở **item** view `I_OperationalAcctgDocItem.Reference1/2/3IDByBusinessPartner`
  (KHÔNG có ở `I_JournalEntryItem`). App "Manage Supplier/Customer Line Items" cần JOIN cả 2 view
  qua CompanyCode+FiscalYear+AccountingDocument nếu FS cần cả Reference lẫn Reference Key 1/2.
- Field "Base Amount" (giá trị hoá đơn trước thuế) generic KHÔNG tồn tại trực tiếp trong
  `I_OperationalAcctgDocItem` — chỉ có biến thể theo mục đích: `TaxBaseAmountInCoCodeCrcy`,
  `OriginalTaxBaseAmount`, `CashDiscountBaseAmount`. Phải hỏi rõ FS "Base Amount" nghĩa là base
  amount của dòng thuế nào trước khi chọn field, KHÔNG bịa field tên "BaseAmount" đơn giản.

## Changelog (học dần)

| Ngày | Đã thêm/verify | Bởi (story/FS) |
|------|----------------|----------------|
| 2026-06-27 | Khởi tạo starter pack (candidate, chưa verify released) | thiết kế module-agent |
| 2026-07-04 | Verify released `I_CompanyCode`, `I_JournalEntry`, `I_OperationalAcctgDocItem`, `I_JournalEntryItem`, `I_TaxCodeRate`, `I_OrganizationAddress`, `I_Country`, `I_Region`, `I_RegionText` qua released-objects-index.json. Học field thật cho Reference/Reference Key 1-2/Base Amount/address (xem §5 pitfall) | FS FI_AP_ZAP06 "Bảng kê chứng từ vận chuyển hàng hóa xuất khẩu" |
