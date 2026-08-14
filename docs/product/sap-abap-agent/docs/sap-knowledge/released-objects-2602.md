# Released Objects trong SAP S/4HANA Cloud Public Edition 2602

**Quy tắc vàng**: Trong SAP Public Cloud, agent chỉ được dùng object đã được
**release cho public cloud** (state C0 = Cloud-Ready, C1 = Released for SAP BTP ABAP Environment).
Object chỉ "released for on-premise" (state R) → KHÔNG dùng được trong cloud.

## Cách kiểm tra (theo thứ tự ưu tiên)

1. ⭐ **Lookup local index** — `docs/sap-knowledge/released-objects-index.json` (37,918 object từ SAP cloudification repo, Apache-2.0).
   - CLI: `python scripts/naf_lookup.py I_CompanyCode --type DDLS`
   - Inline: xem [released-objects-index-README.md](released-objects-index-README.md)
   - Refresh sau mỗi release SAP (~6 tháng): `python scripts/build_released_objects_index.py --refresh`
2. Fallback **api.sap.com** (cần network + SPA): search class/interface → tab "APIs & News" → check "Available in SAP S/4HANA Cloud Public Edition".
3. Fallback **Eclipse ADT View Browser** với Business User + SSO: hiển thị released state thật từ tenant.
4. ATC check trong Eclipse ADT: right-click package → Check → ABAP Test Cockpit → filter "Released APIs for SAP BTP, ABAP Environment".

## Class quan trọng trong 2602 (đều released)

### RAP core
- `CL_ABAP_BEHAVIOR_HANDLER` — base cho behavior pool.
- `CL_ABAP_BEHAVIOR_SAVER` — saver cho unmanaged.
- `CL_ABAP_BEHAVIOR_EVENT_HANDLER` — event handler.
- `ABAP_BEHV_*` structures — runtime behavior.

### Data manipulation
- `CL_ABAP_CORRESPONDING` — move data giữa structure (released trong 7.55+).
- `CL_ABAP_TABLE_IRENDERER` — render table.
- `CL_ABAP_FORMAT` — format số, ngày.

### Runtime
- `CX_*` — system exceptions, đều released.
- `XCO_CP_*` — XCO library, released cho cloud.

### String / Date
- `STRING_TEMPLATE` — string template `|Hello { lv_name }|`, released.
- `CONV` — conversion operator, released.
- `CORRESPONDING` — move-corresponding, released.
- `VALUE` / `REDUCE` / `FILTER` / `COND` / `SWITCH` — table expressions, released.

## Class KHÔNG được dùng trong cloud

- `CL_GUI_*` — controls (chỉ dùng SAP GUI, không chạy trong cloud).
- `CL_HTTP_*` cũ — thay bằng `CL_HTTP_CLIENT` mới (released).
- `DYNP_*` — dynpro fields, không dùng trong Fiori.
- BAPI truyền thống — thay bằng RAP OData service.
- `CALL TRANSACTION` — không dùng, dùng POST/PUT qua OData.
- `AUTHORITY-CHECK` statement — không dùng, dùng ABAP CDS DCL.
- `CHECK` statement — không dùng, dùng CDS annotation.

## Phương pháp an toàn

1. **Mặc định nghi ngờ**: mọi class chưa chắc chắn → check API state.
2. **Dùng Eclipse ATC**: chạy check trước mỗi commit.
3. **Lint tự động**: `scripts/check_released_api.py` check các keyword
   nguy hiểm (`CL_GUI`, `CALL TRANSACTION`, v.v.).
4. **Khi không chắc**: hỏi KH hoặc check SAP note mới nhất.

## Release schedule

- SAP Public Cloud release mỗi năm 2 lần: ~ tháng 4 và tháng 10.
- Release 2602 = February 2026 (đang dùng).
- Next: 2608 (August 2026).
- Mỗi release có thể deprecate class cũ, add class mới.

## Lint

```bash
python scripts/check_released_api.py src/
```

Check:
- Không dùng `CL_GUI*` (trừ một số class được note released).
- Không có `CALL TRANSACTION`, `CALL DIALOG`.
- Không có `AUTHORITY-CHECK` statement.
- Không có `CHECK` statement.
- Class được dùng phải có reference đến doc/API state trong comment.
