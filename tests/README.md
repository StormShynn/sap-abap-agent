# Test directory

Thư mục này chứa **unit test Python** cho các script trong `reference/scripts/`
và MCP server. Có 9 file test + 1 wrapper test ở `hooks/hook_tests/`.

## Cấu trúc

```
tests/
+-- __init__.py                  # (none, dir rỗng, dùng để pytest không báo lỗi)
+-- test_bootstrap_memory.py     # 16 test
+-- test_check_released_api.py   # 7 test
+-- test_lesson_card_add.py      # 16 test
+-- test_mcp_common.py           # 17 test
+-- test_skill_curator.py        # 14 test
+-- test_validate_inspired_by_links.py  # 11 test
+-- test_validate_plugin.py      # 17 test
+-- test_validate_plugin_advanced.py    # 17 test
+-- (src/, __Du_an/)             # ABAP fixtures - bi ignore boi collect_ignore_glob
hooks/hook_tests/
+-- test_hooks_wrapper.py        # 11 test (SessionStart + PostToolUse SELECT *)
```

Tổng cộng: **126 test** (không bao gồm ABAP fixtures).

## Cách chạy

### Tất cả test (collect-only để verify discovery)

```bash
python -m pytest tests/ hooks/hook_tests/ --collect-only -q
```

### Một file cụ thể

```bash
python -m pytest tests/test_validate_plugin.py -v
```

### Test cho MCP server (sub-package)

```bash
cd reference/mcp-server
pip install -e ".[dev]"
python -m pytest tests/ -v
```

Lưu ý: `reference/mcp-server/tests/` chứa 11 file script test cũ (chạy trực tiếp qua
`python tests/test_xxx.py`, không phải pytest function). Đã có `collect_ignore_glob`
trong `conftest.py` để pytest skip chúng.

### Test wrapper hooks (SessionStart, PostToolUse)

```bash
python -m pytest hooks/hook_tests/ -v
```

## Convention khi viết test mới

1. **Tên file**: `test_<script_name>.py` (không có prefix `_` để pytest auto-discover).
2. **Tên hàm**: `test_<behavior>` (snake_case, mô tả 1 behavior cụ thể).
3. **Không phụ thuộc** network, file bên ngoài working tree, hoặc env var ngoài `tmp_path`.
4. **Dùng `tmp_path`** (pytest fixture) cho mọi file tạm — KHÔNG ghi vào `/tmp` cứng.
5. **Skip test**: dùng `@pytest.mark.skip(reason="...")` — KHÔNG comment-out.
6. **Coverage**: nếu thêm script mới trong `reference/scripts/`, viết test ngay trong PR đó.

## Fixtures chung

Định nghĩa trong `conftest.py` (nếu có):

- `tmp_path` (built-in): cho file tạm.
- `monkeypatch` (built-in): cho env var, sys.path.

## CI

Workflow `.github/workflows/validate.yml` chạy pytest collect-only ở mỗi push/PR
(đủ để phát hiện lỗi import / syntax / discovery). Để chạy test thật, có thể:

1. Thêm `python -m pytest tests/ hooks/hook_tests/ -v` vào job `validate`.
2. Hoặc tạo workflow `ci-tests.yml` riêng.

Hiện tại repo chưa chạy test thật trên CI — chỉ chạy local qua pre-commit hook
(`python -m pytest ... -p no:cacheprovider`).


## 4 nhom test (update v1.12.x)

### Root tests/
Test cho cac script trong `reference/scripts/`:
- test_bootstrap_memory.py, test_check_released_api.py, test_lesson_card_add.py
- test_mcp_common.py, test_skill_curator.py
- test_validate_inspired_by_links.py, test_validate_plugin.py, test_validate_plugin_advanced.py

### hooks/hook_tests/
Test cho hook wrapper (SessionStart JSON contract, PostToolUse SELECT * warning):
- test_hooks_wrapper.py (11 test)

### reference/mcp-server/tests/
Script test cu (11 file, khong phai pytest function). Chay truc tiep:
```bash
python tests/test_auto1.py  # vi du
```

### reference/scripts/ (verified by smoke)
- `build_index.py` - smoke test boi validate.yml CI
- `verify_modules_consistency.py` - warning-only
- `scan_clear_text_logging.py` - warning-only
