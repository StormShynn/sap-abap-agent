# Pattern tạo chứng từ SAP (dùng chung — AGENTS_DOC owner)

> **Nguồn sự thật DUY NHẤT** cho việc tạo chứng từ SAP standard. `AGENTS_DOC` sở hữu/cập nhật file này;
> `AGENTS_Excel` và `AGENTS_API` **tái dùng** đúng pattern này ở bước tạo chứng từ — KHÔNG tự nghĩ lại.

## Phân vai (đừng trộn)
- **Trigger = agent chính**: Excel file → `AGENTS_Excel`; hệ ngoài OData → `AGENTS_API`;
  UI/action/scheduled (không Excel/không hệ ngoài) → `AGENTS_DOC`.
- **Interface chuẩn để tạo loại chứng từ X** → hỏi **module expert** (`AGENTS_<MODULE>`): trả về tên
  + released-state. **Reuse** class đã có → hỏi `AGENTS_REUSE`.
- **Pattern gọi (file này)** → áp dụng giống nhau ở cả 3 agent.

## Chọn interface (theo thứ tự ưu tiên, phải verify released cho Cloud 2602)
1. **Released BAPI/FM** nếu còn released cho cloud (vd `BAPI_GOODSMVT_CREATE` cho goods movement).
2. **EML** `MODIFY ENTITIES OF <I_BO> ENTITY <e> CREATE …` nếu BO released cho EML.
3. **Standard OData/SOAP API** (api.sap.com) khi (1)(2) không có.
> Module expert xác định cái nào tồn tại + released cho loại chứng từ cụ thể. KHÔNG bịa, KHÔNG dùng
> BAPI cổ chưa released cloud.

## Các bước bắt buộc (bất kể trigger)
1. **Validate input** trước khi tạo (field bắt buộc, kiểu, master data tồn tại).
2. **Map** input → tham số interface (BAPI struct / EML entity / API payload).
3. **Gọi tạo** chứng từ.
4. **Đọc kết quả lỗi**:
   - BAPI → `BAPIRET2` (type E/A = lỗi).
   - EML → `FAILED` / `REPORTED`.
   - API → HTTP status + body messages.
5. **Commit / rollback**:
   - BAPI → `BAPI_TRANSACTION_COMMIT` (wait='X') / `BAPI_TRANSACTION_ROLLBACK`.
   - EML → `COMMIT ENTITIES` + kiểm tra failed.
6. **Bắt số chứng từ** SAP trả về (doc number) → lưu/trả lại cho user.
7. **Idempotency / chống trùng**: theo business key (đừng tạo lặp khi retry).
8. **Audit log** (nếu FS/integration cần) → `ZCL_LOG_INT=>logger()` (xem reusable-team-assets §1).
9. **Tách logic tạo** vào class `ZCL_<TICKET>_*` (PURE phần map) để ABAP Unit test (mock interface
   qua `CL_ABAP_TESTDOUBLE`).

## Reality filter
- Tên BAPI/BO/API/field + released-state **phải verify** (module expert; **MCP read-only**
  `SearchObject`/`GetTypeInfo` nếu kết nối; fallback View Browser ADT / api.sap.com).
  Chưa chắc → `[Unverified]` + INTAKE §6. MCP chỉ để **đọc/verify**, không tạo chứng từ qua MCP.
- KHÔNG direct SQL `INSERT/UPDATE` bảng standard SAP.

## Ai dùng file này
- `AGENTS_DOC` — owner, dùng trực tiếp (trigger UI/action).
- `AGENTS_Excel` — sau khi parse Excel → preview → ở action ProcessUpload, tạo chứng từ theo pattern này.
- `AGENTS_API` — nếu integration inbound cần **tạo chứng từ standard** (không chỉ lưu Z table) → theo pattern này.
