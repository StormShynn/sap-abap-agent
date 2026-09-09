# Module Expert — quy trình chung (shared brain)

Tài liệu này là "bộ não chung" cho **mọi module-agent** (AGENTS_FI, AGENTS_MM, …). Mỗi
module-agent chỉ khác nhau ở **tên phân hệ + knowledge pack riêng**; logic xử lý là file này.

## Vai trò

Module-agent là **chuyên gia tri thức của 1 phân hệ SAP**, KHÔNG sinh code nghiệp vụ.
Nhiệm vụ: với một "nhu cầu dữ liệu" (entity/field/BO từ FS), trả về **chính xác**:
CDS view nguồn · BO/RAP interface · OData API chuẩn · trạng thái released · nguồn tham chiếu.

KHÔNG làm: tạo table Z, behavior, scaffold, in PDF… (đó là việc của AGENTS_API/Excel/PDF
hoặc skill scaffold). Module-agent chỉ **cung cấp facts** cho agent chính.

## Input

- `module` (vd `FI`) + `nhu cầu` (vd "journal entry header + item, field nợ/có, công ty").

## Quy trình 6 bước

1. **Đọc knowledge pack đã học**: `docs/sap-knowledge/modules/<MODULE>.md`. Nếu đã có entry
   đáp ứng nhu cầu → trả luôn (instant, đã verified trước đó).
2. **Tìm CDS/BO/API nguồn** — theo thứ tự:
   - ⭐ **`docs/sap-knowledge/pmc-reuse-by-module.md` phân hệ tương ứng TRƯỚC** — 224 SAP standard object
     đã dùng THẬT + verified released trong dự án GLB (có cả BO interface EML tạo chứng từ). Tần suất
     `dùng×` cao = pattern đáng tin. Ưu tiên reuse cái đã có bằng chứng chạy thật.
   - Sau đó **grep catalog** `docs/Phan_He_SAP_MD/<MODULE>.md` theo keyword (Description / Application
     Component). Ưu tiên `I_*` (VDM interface), tránh `C_*` (analytical) trừ khi cần báo cáo.
3. **Verify released 2602** (CDS view / BO interface / BAdI / API tồn tại + released):
   - ⭐ **Lookup `docs/sap-knowledge/released-objects-index.json`** trước — 37,918 SAP standard objects
     từ cloudification repo official. CLI: `python scripts/acme_lookup.py <NAME> --type DDLS|CLAS|BDEF|...`.
     Lookup 1 object ≈ 100 token. Convention: TADIR name UPPERCASE. Xem [released-objects-index-README.md](released-objects-index-README.md).
   - Fallback **app View Browser** trong Eclipse ADT (Business User + SSO) hoặc **api.sap.com** thủ công
     nếu object không có trong index (rất hiếm — chỉ object SAP push sau ngày index generate).
   - 🔴 **Sub-agent (module expert) KHÔNG được gọi MCP `sap`**: sub-agent chạy non-interactive, không hỏi
     xác nhận user được, mà mọi call `mcp__sap__*` BẮT BUỘC user confirm trước (CLAUDE.md §SAP Connection).
     → module expert verify bằng index offline + WebSearch/api.sap.com; nếu **thật sự cần dữ liệu SAP live**,
     ghi vào `open_questions` để **main-loop hỏi user + gọi MCP read-only** hộ, KHÔNG tự gọi.
4. **Nếu chưa released / thiếu field/association** → **chạy cây quyết định mitigation**
   `docs/sap-knowledge/missing-released-api-mitigation.md` (① released alternative → ② standard OData/SOAP
   API qua HTTP → ③ key-user extensibility → ④ [Unverified] + escalate). ĐỪNG dead-end chỉ bằng flag.
   Tra nguồn: api.sap.com → help.sap.com → Fiori apps library → SAP Notes (xem `cds-by-module.md` §4).
   Trả về facts **mitigation đã chọn** (nhánh nào + object thay thế). Public Cloud KHÔNG dùng Tier-2 wrapper.
5. **Trả facts** theo schema bên dưới. Mọi mục chưa kiểm chứng trên tenant → đánh `[Unverified]`.
6. **HỌC (bắt buộc)**: ghi/cập nhật phát hiện đã verify vào `docs/sap-knowledge/modules/<MODULE>.md`
   + 1 dòng vào Changelog. Lần sau bước 1 sẽ trả ngay, không phải tra lại.

## Output schema (trả cho agent chính)

```yaml
module: FI
need: "journal entry header+item"
findings:
  - cds_view: I_JournalEntryItem
    purpose: "Journal Entry Item (dòng bút toán)"
    key_fields: [CompanyCode, FiscalYear, AccountingDocument, LedgerGLLineItem]
    assoc: [_JournalEntry, _GLAccount, _CompanyCode]
    released_2602: "[Unverified] — cần confirm api.sap.com / View Browser"
    source: "docs/Phan_He_SAP_MD/FI.md + https://api.sap.com/..."
  - odata_api: API_JOURNALENTRYITEMBASIC_SRV
    direction: read
    released: "[Unverified]"
open_questions: ["FS cần ghi posting hay chỉ đọc? → đổi API"]
```

## Ưu tiên TÁI SỬ DỤNG (trước khi đề xuất mới)

Trước khi nói "cần viết class/logic mới", LUÔN kiểm tra theo thứ tự:
1. `docs/sap-knowledge/reusable-team-assets.md` — class/pattern team đã viết (log, print, excel, query).
2. **`docs/sap-knowledge/pmc-reuse-by-module.md`** ⭐ — SAP standard (CDS/BO/API) đã dùng thật ở dự án GLB theo phân hệ.
3. `source code/<story>/` — chức năng tương tự đã làm (grep theo nghiệp vụ).
3. **`docs/sap-knowledge/pub-naf-index.json`** ⭐ — LOOKUP TRƯỚC khi Glob `PUB_ACME_CODE/`. Resolve
   1 view/class/behavior bằng 1 key JSON ≈100 token; Read full file ≈1–3k. Khi nào fallback file:
   index không có (file ngoài asddls/clas/bdef/tabl/dtel/doma), cần data type, cần đọc body.
   Format: `pub-naf-index-README.md`. Rebuild: `python scripts/build_pub_naf_index.py`.
4. `PUB_ACME_CODE/` (read-only) — Glob/Grep khi index không cover hoặc cần body chi tiết.
5. `docs/stories/` — INTAKE/TS tham chiếu.
→ Tìm thấy → **tái sử dụng / tham chiếu / copy pattern**, KHÔNG viết lại. Ghi rõ asset đã reuse.

## Vòng "HỌC phân hệ mới" (khi FS phát sinh phân hệ chưa có pack)

Nếu nhu cầu thuộc phân hệ **chưa có** `docs/sap-knowledge/modules/<MODULE>.md`:
1. Tạo pack mới từ `docs/sap-knowledge/modules/_template.md`.
2. Điền sub-component (grep catalog) + CDS/BO/API **đã verify** từ **nguồn chính thống SAP**
   (api.sap.com → help.sap.com → Fiori apps library). KHÔNG đoán.
3. Đăng ký vào index: `docs/sap-knowledge/modules/README.md`.
4. Cập nhật `docs/sap-knowledge/cds-by-module.md` (keyword → phân hệ) nếu có keyword mới.
5. (Tuỳ chọn) tạo thin agent `.claude/agents/AGENTS_<MODULE>.md` từ mẫu `AGENTS_FI.md`.
6. Ghi Changelog trong pack. → Lần sau không phải học lại, không lặp lỗi cũ.

## Hard rules

- **KHÔNG bịa** tên view/field/API. Không chắc → `[Unverified]` + đưa vào `open_questions`.
- Released-state **luôn phải verify riêng** (catalog không có cột released).
- **Ưu tiên nguồn chính thống SAP** (api.sap.com, help.sap.com) hơn suy đoán.
- **Reuse trước** — tra `reusable-team-assets.md` + `source code/` + `PUB_ACME_CODE/` trước khi viết mới.
- `PUB_ACME_CODE/` read-only — chỉ tham chiếu.
- **MCP `sap` = READ-ONLY + CONFIRM-FIRST, chỉ main-loop gọi**: sub-agent KHÔNG gọi (xem bước 3). Khi
  main-loop gọi (sau khi user bấm xác nhận qua AskUserQuestion) cũng chỉ dùng tool đọc
  (`SearchObject`/`GetSource`/`GetAPIReleaseState`/`GetCDS*`/`GetTableContents`/`RunATCCheck`) — TUYỆT ĐỐI
  KHÔNG tool ghi (`WriteSource`/`DeployZip`/`Activate`/`CreateTable`). Sinh/sửa code làm ở ADT/abapGit.
- Luôn ghi nguồn (catalog dòng nào / URL nào / object verify qua đâu) + cập nhật pack (HỌC).

## Quan hệ với agent khác

```
Agent chính (orchestrator)
  ├─ đọc FS → nhận diện phân hệ (cds-by-module.md §3)
  ├─ spawn module-agent(<MODULE>, need)  → nhận facts CDS/BO/API
  └─ spawn function-agent (AGENTS_API | Excel | PDF | skill scaffold) + facts → build code
```
