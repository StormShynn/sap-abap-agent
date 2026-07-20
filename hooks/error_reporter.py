#!/usr/bin/env python
"""
SAP ABAP Agent — Error Reporter (Auto Issue Creator)

Chạy ngầm qua hook system, tự động phát hiện lỗi runtime trong quá trình dùng
plugin và tạo GitHub issue trên repo chính (StormShynn/sap-abap-agent) để
theo dõi, fix lỗi liên tục — continuous improvement loop.

Cơ chế:
  ┌─────────────────────────────────────────────────────────────┐
  │  1. PostToolUse (Bash)  ──detect-bash──>  ghi error_log    │
  │  2. PostToolUse (Tool)  ──detect-tool──>  ghi error_log    │
  │  3. PostToolUse (Edit)  ──detect-fix───>  ghi fix_log      │
  │  4. Stop                ──report───────>  dedup +          │
  │                            tạo issue + add fix comment     │
  └─────────────────────────────────────────────────────────────┘

Khi Claude trả lời cách fix lỗi và viết code sửa:
  - detect-fix phát hiện code đang sửa liên quan đến error đã log
  - report giai đoạn 2: add comment fix vào GitHub issue có sẵn
  → Issue trở thành "error + solution" hoàn chỉnh 📖

Storage: ~/.sap-abap-agent/error-reports/
  error_log.jsonl     — append-only log của mọi error detected
  fix_log.jsonl       — append-only log của mọi fix detected
  known_issues.json   — cache issue đã tạo (hash → issue info)
  pending_queue.json  — error chưa tạo được issue (chờ auth)

Fail-open: KHÔNG bao giờ block user — lỗi trong script chỉ log ra stderr
và exit(0). Không ảnh hưởng đến luồng chính của Claude Code.

Opt-in (mặc định TẮT): script không log/tạo issue gì cả trừ khi user bật
rõ ràng bằng 1 trong 2 cách:
  1. Env var SAP_ABAP_AGENT_ERROR_REPORTING=1 (hoặc true/yes/on)
  2. Tạo file marker: ~/.sap-abap-agent/error-reports/ENABLED
Lý do: cài plugin Claude Code không bắt buộc user phải có GitHub auth, và
việc thu thập error/code silently mà không hỏi trước là vi phạm quyền riêng
tư — xem _is_enabled().

Giới hạn phạm vi fix-comment: CHỈ đính kèm code snippet khi file đang sửa
nằm trong chính thư mục cài đặt plugin này (xem _is_plugin_file()) — KHÔNG
BAO GIỜ đính code của user (VD class ABAP nội bộ công ty họ) lên issue
public. Nghĩa là tính năng "đính fix" chủ yếu phục vụ người phát triển
plugin, không áp dụng cho code người dùng cuối.

Requirements:
  - GitHub CLI (gh) hoặc GITHUB_TOKEN env var để tạo issue/comment
  - Python 3.10+ (std lib only — zero extra dependencies)
  - `pip install`? Không cần — chỉ dùng thư viện chuẩn của Python.
  - `gh` CLI? Không bắt buộc — fallback qua REST API nếu có GITHUB_TOKEN.
  - Không có cả 2? Lưu pending queue, retry sau.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Constants ──────────────────────────────────────────────────────────────

AGENT_HOME = Path(os.environ.get(
    "SAP_ABAP_AGENT_HOME",
    Path.home() / ".sap-abap-agent",
))
ERROR_REPORTS_DIR = AGENT_HOME / "error-reports"
ERROR_LOG = ERROR_REPORTS_DIR / "error_log.jsonl"
FIX_LOG = ERROR_REPORTS_DIR / "fix_log.jsonl"
KNOWN_ISSUES = ERROR_REPORTS_DIR / "known_issues.json"
PENDING_QUEUE = ERROR_REPORTS_DIR / "pending_queue.json"
# Reports dir: local Markdown luôn được save, không cần GitHub auth
REPORTS_DIR = ERROR_REPORTS_DIR / "reports"
# Rate limit: không tạo quá 1 issue cho cùng 1 error_hash trong N giây
DEDUP_WINDOW_SEC = 86400  # 24h
# Threshold: nếu cùng error_hash xuất hiện > N lần, tạo issue bổ sung
REISSUE_THRESHOLD = 5

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

PLUGIN_VERSION = "unknown"
try:
    plugin_json = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        PLUGIN_VERSION = json.loads(plugin_json.read_text(encoding="utf-8")).get("version", "unknown")
except Exception:
    pass


def _is_enabled() -> bool:
    """Error reporting la opt-in — mac dinh TAT.

    Cai plugin Claude Code khong bat buoc user phai co GitHub auth, va thu
    thap error/code silently ma khong hoi truoc la vi pham quyen rieng tu.
    Bat bang 1 trong 2 cach:
      1. Env var SAP_ABAP_AGENT_ERROR_REPORTING=1 (hoac true/yes/on)
      2. Tao file marker: ~/.sap-abap-agent/error-reports/ENABLED
    """
    env = os.environ.get("SAP_ABAP_AGENT_ERROR_REPORTING", "").strip().lower()
    if env in ("1", "true", "yes", "on"):
        return True
    return (ERROR_REPORTS_DIR / "ENABLED").exists()


def _is_plugin_file(file_path: str) -> bool:
    """True neu file_path nam trong chinh thu muc cai dat plugin nay.

    Dung de gioi han fix-comment: CHI dinh kem code snippet khi dang sua
    code cua plugin (VD dev fix bug plugin) — KHONG BAO GIO dinh kem code
    cua user (VD class ABAP noi bo cong ty ho) len issue public.
    """
    if not file_path:
        return False
    try:
        return Path(file_path).resolve().is_relative_to(PLUGIN_ROOT)
    except (OSError, ValueError):
        return False


# Cac dang chuoi giong secret/credential thuong gap trong error message,
# stderr, bash command — che truoc khi log/publish (defense in depth, ke ca
# khi da gioi han fix-comment chi trong plugin file o tren).
_REDACT_PATTERNS = [
    (re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9\-._~+/]+=*"), r"\1 ***REDACTED***"),
    (re.compile(r"(?i)\b(authorization|x-api-key|x-csrf-token|cookie|set-cookie)\s*[:=]\s*\S+"),
     r"\1: ***REDACTED***"),
    (re.compile(r"://([^/\s:@]+):([^/\s@]+)@"), r"://\1:***REDACTED***@"),
    (re.compile(r"(?i)\b(password|passwd|client_secret|clientsecret|secret|"
                r"api[_-]?key|access_token|refresh_token)\s*[:=]\s*['\"]?[^\s'\",;]+"),
     r"\1=***REDACTED***"),
]


def _redact(text: str) -> str:
    """Che cac chuoi giong secret/token/credential truoc khi log/publish.

    Best-effort (regex) — khong bat duoc 100% cac dang the hien token, nhung
    chan cac pattern pho bien nhat (Bearer, Authorization header, URL co
    user:pass@, password=/token=/secret=...).
    """
    if not text:
        return text
    redacted = text
    for pattern, repl in _REDACT_PATTERNS:
        redacted = pattern.sub(repl, redacted)
    return redacted


class _FileLock:
    """Lock don gian, portable (Windows/macOS/Linux), khong can dependency
    ngoai — dung open(path, O_CREAT|O_EXCL) lam mutex.

    Chong race condition khi nhieu session Claude Code chay song song deu
    goi Stop hook gan nhau: ca 2 doc known_issues.json thay "chua co issue",
    ca 2 deu tao issue moi -> issue trung. Tu bo qua lock cu (stale) qua
    stale_after_s de tranh deadlock vinh vien neu process truoc crash giua
    luc dang giu lock. Fail-open: het wait_s ma khong lay duoc lock thi van
    tiep tuc KHONG co lock (uu tien khong block/mat report hon la dedup
    hoan hao).
    """

    def __init__(self, path: Path, stale_after_s: float = 60.0, wait_s: float = 45.0):
        self.path = path
        self.stale_after_s = stale_after_s
        self.wait_s = wait_s
        self._acquired = False

    def __enter__(self) -> "_FileLock":
        _ensure_dir()
        deadline = time.time() + self.wait_s
        while True:
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale_after_s:
                        self.path.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.time() >= deadline:
                    return self
                time.sleep(0.1)
            except OSError:
                return self

    def __exit__(self, *exc: Any) -> None:
        if self._acquired:
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass


KNOWN_ISSUES_LOCK = ERROR_REPORTS_DIR / "known_issues.lock"


# ── Helpers ────────────────────────────────────────────────────────────────


def _ensure_dir() -> None:
    """Tạo thư mục error-reports nếu chưa có."""
    ERROR_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_hash(message: str) -> str:
    """Tạo hash SHA256 ngắn (12 ký tự) từ error message đã normalize."""
    norm = re.sub(r"\s+", " ", message.strip().lower())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    _ensure_dir()
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        print(f"[error-reporter] Khong ghi duoc {path}: {exc}", file=sys.stderr)


def _append_log(path: Path, record: dict) -> None:
    """Append 1 dòng JSON vào file .jsonl."""
    _ensure_dir()
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[error-reporter] Khong ghi log {path.name}: {exc}", file=sys.stderr)


def _read_log(path: Path, max_age_days: int = 7) -> list[dict]:
    """Đọc file .jsonl, trả về list records không quá max_age_days."""
    if not path.exists():
        return []
    cutoff = time.time() - max_age_days * 86400
    records: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = rec.get("timestamp", "")
            try:
                epoch = datetime.fromisoformat(ts).timestamp()
            except (ValueError, TypeError):
                epoch = time.time()
            if epoch >= cutoff:
                records.append(rec)
    except OSError:
        pass
    return records


# ── Detect Errors ──────────────────────────────────────────────────────────


def _is_meaningful_error(error_type: str, error_message: str) -> bool:
    """Kiểm tra lỗi có đủ ý nghĩa để tạo issue không.

    Nguyên tắc: ưu tiên 1 issue thừa hơn 1 bug thiếu.
    Chỉ filter noise rõ ràng (warning/info) — KHÔNG filter 'not found'/
    'timeout' vì trong ABAP context đây thường là bug thật.
    """
    msg_lower = error_message.lower()

    meaningful_types = {
        "mcp_error", "sap_error",
        "abap_syntax_error", "abap_activate_error",
    }
    if error_type in meaningful_types:
        return True

    # Chỉ filter warning/info thực sự (không phải lỗi)
    if "[info]" in msg_lower and "error" not in msg_lower:
        return False
    if "[information]" in msg_lower and "error" not in msg_lower:
        return False

    if error_type == "bash_error":
        sap_keywords = [
            "sap", "abap", "rfc", "bapi", "s4hana", "btp",
            "activate", "syntax", "ddic", "data element", "domain",
            "table", "cds", "odata", "transport", "package",
        ]
        if any(kw in msg_lower for kw in sap_keywords):
            return True
        if "error" in msg_lower or "exception" in msg_lower:
            return True

    if error_type in ("edit_error",):
        return True

    return False


def _extract_details(payload: dict) -> dict | None:
    """Trích xuất thông tin lỗi từ hook payload.

    Trả về dict error record hoặc None nếu không phải lỗi.
    """
    tool_name = (payload.get("tool_name") or payload.get("tool") or "").strip()
    tool_input = payload.get("tool_input") or {}
    result = payload.get("result") or payload.get("tool_result") or {}
    session_id = payload.get("session_id", "unknown")
    is_mcp_tool = bool(tool_name) and tool_name not in ("Bash", "Edit", "Write", "Read")

    error_type: str | None = None
    error_message: str | None = None
    context: dict[str, Any] = {}

    # ── Bash errors ────────────────────────────────────────────────
    if tool_name == "Bash" and isinstance(result, dict):
        exit_code = result.get("exit_code")
        if exit_code is None:
            exit_code = result.get("exitCode")
        stderr = (result.get("stderr") or result.get("error") or "").strip()
        command = tool_input.get("command", "")

        if exit_code is not None and exit_code != 0:
            error_type = "bash_error"
            error_message = _redact(stderr[:1000] if stderr else f"Exit code {exit_code}")
            context = {
                "command": _redact(command[:300]),
                "exit_code": exit_code,
                "stderr_preview": _redact(stderr[:500]),
            }
        elif stderr and any(kw in stderr.lower() for kw in ["error", "exception", "fail"]):
            error_type = "bash_error"
            error_message = _redact(stderr[:1000])
            context = {"command": _redact(command[:300]), "stderr_preview": _redact(stderr[:500])}
        elif "sap" in command.lower()[:100] and len(command) > 20:
            error_type = "bash_info"
            error_message = f"SAP-related Bash command executed: {_redact(command[:200])}"
            context = {"command": _redact(command[:300]), "note": "khong co exit code - log de trace"}

    # ── MCP tool errors ────────────────────────────────────────────
    elif is_mcp_tool and isinstance(result, dict):
        is_error = result.get("isError") or result.get("is_error", False)
        content = result.get("content") or result.get("text") or ""

        if is_error or (isinstance(content, str) and "error" in content.lower()[:200]):
            error_type = "mcp_error"
            raw_message = str(content)[:1500] if isinstance(content, str) else json.dumps(content)[:1500]
            error_message = _redact(raw_message)
            context = {
                "tool_name": tool_name,
                "input": {
                    k: (_redact(v) if isinstance(v, str) else v)
                    for k, v in tool_input.items() if k not in ("password", "secret")
                },
            }
            err_lower = error_message.lower()
            if "syntax" in err_lower and ("check" in err_lower or "error" in err_lower):
                error_type = "abap_syntax_error"
            elif "activate" in err_lower:
                error_type = "abap_activate_error"
            elif "401" in err_lower or "unauthorized" in err_lower or "auth" in err_lower:
                error_type = "sap_error"
            elif "403" in err_lower or "forbidden" in err_lower:
                error_type = "sap_error"

    # ── Edit/Write errors ──────────────────────────────────────────
    elif tool_name in ("Edit", "Write"):
        result_str = str(result)
        if "error" in result_str.lower()[:200]:
            error_type = "edit_error"
            error_message = _redact(result_str[:1000])
            context = {"file_path": tool_input.get("file_path", "")}

    if error_type and error_message:
        return {
            "session_id": session_id,
            "tool": tool_name,
            "error_type": error_type,
            "error_message": error_message.strip(),
            "context": context,
            "plugin_version": PLUGIN_VERSION,
            "platform": sys.platform,
            "timestamp": _now(),
        }
    return None


def _record_error_record(record: dict) -> None:
    """Ghi 1 error record vào log, gắn error_hash."""
    record["error_hash"] = _error_hash(record.get("error_message", ""))
    _append_log(ERROR_LOG, record)


# ── Detect Fixes ────────────────────────────────────────────────────────────
#
# Khi Claude viết code sửa lỗi (Edit/Write PostToolUse), ta kiểm tra:
#   1. file_path có xuất hiện trong error_log gần đây không?
#   2. new_string có chứa pattern "sửa" / keyword liên quan error không?
#   3. Nếu match → ghi fix record vào fix_log.jsonl
#
# Tại Stop hook, fix record này được dùng để add comment vào GitHub issue.


def _find_matching_errors(file_path: str, new_code: str, session_id: str) -> list[dict]:
    """Tìm error records trong 7 ngày gần nhất có match với file/code đang edit.

    Matching strategy:
      1. Cùng session_id + file_path trong context
      2. file_path match với context.file_path
      3. Nội dung error message có chứa keyword từ new_code
    """
    if not file_path and not new_code:
        return []

    errors = _read_log(ERROR_LOG, max_age_days=7)
    related: list[dict] = []
    file_path_lower = file_path.lower()
    new_code_lower = new_code.lower()[:500]  # chỉ lấy phần đầu cho performance

    # Trích keywords kỹ thuật từ code mới (tên class, method, table, field...)
    code_keywords = set()
    for match in re.findall(r"\b[A-Z][A-Z0-9_]{2,50}\b", new_code):
        code_keywords.add(match.lower())
    for match in re.findall(r"\b[a-z][a-z0-9_]{3,30}\b", new_code[:1000]):
        code_keywords.add(match.lower())

    for rec in errors:
        score = 0
        ctx = rec.get("context", {})
        rec_msg = (rec.get("error_message", "") or "").lower()

        # Match file_path
        if file_path_lower:
            ctx_file = (ctx.get("file_path") or ctx.get("input", {}).get("object_name") or "").lower()
            if file_path_lower == ctx_file or ctx_file in file_path_lower or file_path_lower in ctx_file:
                score += 3

        # Match session
        if session_id and rec.get("session_id") == session_id:
            score += 1

        # Match code keywords
        if code_keywords:
            keyword_matches = sum(1 for kw in code_keywords if kw in rec_msg)
            if keyword_matches > 1:
                score += min(keyword_matches, 3)

        if score >= 2:
            related.append(rec)

    return related


def _detect_fix(payload: dict) -> dict | None:
    """Phát hiện fix từ Edit/Write payload.

    Trả về dict fix record hoặc None nếu không tìm thấy error liên quan.
    """
    tool_name = (payload.get("tool_name") or payload.get("tool") or "").strip()
    if tool_name not in ("Edit", "Write"):
        return None

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path", "") or ""
    old_string = tool_input.get("old_string", "") or ""
    new_string = tool_input.get("new_string", "") or ""
    session_id = payload.get("session_id", "unknown")

    if not new_string:
        return None

    # Chi dinh kem code snippet khi sua CHINH code cua plugin nay — khong
    # bao gio bat/leak code cua user (VD class ABAP noi bo cong ty ho).
    if not _is_plugin_file(file_path):
        return None

    # Tìm error liên quan
    matching_errors = _find_matching_errors(file_path, new_string, session_id)
    if not matching_errors:
        return None

    # Gom error_hash
    error_hashes = list(dict.fromkeys(e.get("error_hash", "") for e in matching_errors if e.get("error_hash")))
    if not error_hashes:
        return None

    # Tạo summary ngắn về fix
    diff_summary = _summarize_diff(old_string, new_string)
    primary_error = matching_errors[0]

    fix_record = {
        "session_id": session_id,
        "tool": tool_name,
        "file_path": file_path[:300],
        "error_hashes": error_hashes,  # các error_hash liên quan
        "primary_error_hash": error_hashes[0],
        "diff_summary": diff_summary,
        "fix_code_preview": _redact(new_string[:1000]),
        "old_code_preview": _redact(old_string[:500]),
        "error_type": primary_error.get("error_type", "unknown"),
        "plugin_version": PLUGIN_VERSION,
        "platform": sys.platform,
        "timestamp": _now(),
    }
    return fix_record


def _summarize_diff(old_string: str, new_string: str) -> str:
    """Tạo mô tả ngắn về sự khác biệt (fix đã làm gì)."""
    if not old_string:
        return "Them moi code (new file or new block)"
    old_lines = old_string.strip().split("\n")
    new_lines = new_string.strip().split("\n")
    added = len(new_lines) - len(old_lines)
    if added > 0:
        return f"Them {added} dong code"
    elif added < 0:
        return f"Xoa {abs(added)} dong code"
    else:
        # Cùng số dòng → kiểm tra thay đổi ký tự
        changes = sum(1 for a, b in zip(old_lines, new_lines) if a != b)
        if changes:
            return f"Sua {changes} dong code"
    return "Dieu chinh code"


def _record_fix_record(record: dict) -> None:
    """Ghi 1 fix record vào fix_log.jsonl, gắn fix_hash."""
    raw = record.get("fix_code_preview", "") or record.get("diff_summary", "")
    record["fix_hash"] = _error_hash(raw)
    _append_log(FIX_LOG, record)


# ── Local Report (Luôn save, không cần auth) ─────────────────────────────

REPORT_HEAD = """# 🐛 Error Report — SAP ABAP Agent

> File này được tự động tạo bởi `hooks/error_reporter.py`.
> Không cần GitHub auth — đây là bản local, dùng để debug.
> Nếu muốn share lên GitHub, copy nội dung file này lên Issues.

"""


def _save_local_report(records: list[dict], fix_records: list[dict] | None = None) -> str | None:
    """Save error report thành file Markdown trong REPORTS_DIR.

    Luôn chạy, không cần GitHub auth. Trả về path file hoặc None nếu lỗi.
    """
    _ensure_dir()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    first = records[0]
    ehash = first.get("error_hash", _error_hash(first.get("error_message", "")))
    safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", first.get("error_message", "error")[:50])
    filename = f"{_now()[:10]}_{ehash}_{safe_title}.md"
    filepath = REPORTS_DIR / filename

    # Build report body từ issue body
    body = REPORT_HEAD + _build_issue_body(records)

    # Thêm fix solutions nếu có
    if fix_records:
        body += "\n\n---\n\n"
        body += _build_fix_comment(fix_records)

    # Footer với hướng dẫn
    body += "\n\n---\n"
    body += "\n### 📋 Cách share lên GitHub Issues"
    body += "\n"
    body += "\n1. Mở https://github.com/StormShynn/sap-abap-agent/issues/new"
    body += "\n2. Chọn template `🐛 Bug report`"
    body += "\n3. Paste nội dung file này vào"
    body += "\n4. Submit"
    body += "\n"
    body += "\n_Hoặc dùng CLI nếu có auth:_"
    body += "\n```bash"
    body += "\ngh issue create --label bug,auto-reported --title \"...\" --body @" + str(filepath) + ""
    body += "\n```"
    body += ""

    try:
        filepath.write_text(body, encoding="utf-8")
        print(f"[error-reporter] Da luu local report: {filepath}", file=sys.stderr)
        return str(filepath)
    except OSError as exc:
        print(f"[error-reporter] Khong ghi duoc report: {exc}", file=sys.stderr)
        return None


# ── GitHub Issue ───────────────────────────────────────────────────────────


def _get_repo_from_git() -> tuple[str, str] | None:
    """Đọc owner/repo từ git remote của plugin repo."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5, cwd=str(PLUGIN_ROOT),
        )
        url = result.stdout.strip()
        if not url:
            return None
        match = re.search(r"github\.com[/:]([^/]+)/([^/.]+)(\.git)?", url)
        if match:
            return match.group(1), match.group(2).removesuffix(".git")
    except Exception:
        pass
    return None


def _build_issue_body(records: list[dict]) -> str:
    """Xây dựng nội dung GitHub issue từ các error records đã gom nhóm."""
    first = records[0]
    count = len(records)

    lines = [
        "## 🐛 Lỗi tự động phát hiện",
        "",
        f"- **Plugin version:** {first.get('plugin_version', 'unknown')}",
        f"- **Platform:** {first.get('platform', sys.platform)}",
        f"- **Error type:** `{first.get('error_type', 'unknown')}`",
        f"- **Tool:** `{first.get('tool', 'unknown')}`",
        f"- **Số lần xuất hiện:** {count}",
        f"- **Khoảng thời gian:** {records[0].get('timestamp', '?')} → {records[-1].get('timestamp', '?')}",
        "",
        "### Error message",
        "",
        "```",
        first.get("error_message", ""),
        "```",
        "",
    ]

    ctx = first.get("context", {})
    if ctx:
        lines.extend([
            "### Context (lần đầu)",
            "",
            "```json",
            json.dumps(ctx, indent=2, ensure_ascii=False),
            "```",
            "",
        ])

    sessions = set(r.get("session_id", "?")[:12] for r in records)
    lines.extend([
        "### Sessions affected",
        "",
        f"- **{len(sessions)}** session(s) bị ảnh hưởng",
        f"- Error hash: `{first.get('error_hash', '?')}`",
        "",
        "---",
        "",
        "_Issue được tự động tạo bởi `hooks/error_reporter.py` — ",
        "SAP ABAP Agent Continuous Improvement Engine._",
        "",
    ])
    return "\n".join(lines)


def _build_issue_title(records: list[dict]) -> str:
    """Tạo title ngắn gọn cho issue từ error records."""
    first = records[0]
    msg = first.get("error_message", "")
    title_line = msg.split("\n")[0].strip()
    if len(title_line) > 80:
        title_line = title_line[:77] + "..."
    error_type = first.get("error_type", "error")
    tool = first.get("tool", "unknown")
    return f"[Auto] [{error_type}] {tool}: {title_line}"


# ── GitHub API: Issue Comments ─────────────────────────────────────────────


def _parse_issue_number(issue_url: str) -> str | None:
    """Trích xuất issue number từ URL."""
    m = re.search(r"/issues/(\d+)", issue_url)
    return m.group(1) if m else None


def _build_fix_comment(fix_records: list[dict]) -> str:
    """Xây dựng comment chứa fix solution để add vào GitHub issue."""
    if not fix_records:
        return ""

    parts = [
        "## ✅ Fix tự động phát hiện",
        "",
        "Claude đã phát hiện và sửa lỗi này. Dưới đây là chi tiết:",
        "",
    ]

    for i, rec in enumerate(fix_records, 1):
        file_path = rec.get("file_path", "")
        diff_summary = rec.get("diff_summary", "")
        fix_code = rec.get("fix_code_preview", "")
        old_code = rec.get("old_code_preview", "")
        session = rec.get("session_id", "?")[:12]

        parts.append(f"### Fix #{i}: {diff_summary}")
        parts.append("")
        if file_path:
            parts.append(f"- **File:** `{file_path}`")
        parts.append(f"- **Session:** `{session}`")
        parts.append(f"- **Plugin version:** {rec.get('plugin_version', '?')}")
        parts.append("")

        if old_code:
            parts.extend(["#### Code cũ", "", "```abap", old_code, "```", ""])

        if fix_code:
            parts.extend(["#### Code mới", "", "```abap", fix_code, "```", ""])

        parts.append("---")
        parts.append("")

    parts.append(
        "_Comment được tự động thêm bởi `hooks/error_reporter.py` — "
        "Continuous Improvement Engine._"
    )
    return "\n".join(parts)


def _try_add_comment_via_gh(issue_url: str, comment_body: str) -> bool:
    """Thêm comment vào issue qua GitHub CLI."""
    issue_num = _parse_issue_number(issue_url)
    if not issue_num:
        return False

    repo_info = _get_repo_from_git()
    if not repo_info:
        return False
    owner, repo = repo_info
    repo_arg = f"{owner}/{repo}"

    try:
        auth_check = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, timeout=10,
        )
        if auth_check.returncode != 0:
            return False

        result = subprocess.run(
            ["gh", "issue", "comment", str(issue_num),
             "--repo", repo_arg,
             "--body", comment_body],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"[error-reporter] Added fix comment to issue #{issue_num}", file=sys.stderr)
            return True
        print(f"[error-reporter] gh comment failed: {result.stderr[:200]}", file=sys.stderr)
        return False
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return False
    except Exception as exc:
        print(f"[error-reporter] gh comment error: {exc}", file=sys.stderr)
        return False


def _try_add_comment_via_api(issue_url: str, comment_body: str) -> bool:
    """Thêm comment vào issue qua GitHub REST API."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return False

    repo_info = _get_repo_from_git()
    if not repo_info:
        return False
    owner, repo = repo_info
    issue_num = _parse_issue_number(issue_url)
    if not issue_num:
        return False

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments"
    data = json.dumps({"body": comment_body}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "sap-abap-agent-error-reporter",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[error-reporter] Added fix comment via API to issue #{issue_num}", file=sys.stderr)
            return True
    except urllib.error.HTTPError as exc:
        print(f"[error-reporter] API comment error {exc.code}: {exc.reason[:200]}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"[error-reporter] API comment error: {exc}", file=sys.stderr)
        return False


def _try_add_fix_comment(issue_url: str, fix_records: list[dict]) -> bool:
    """Wrapper: thử add comment fix vào issue qua nhiều phương thức."""
    comment = _build_fix_comment(fix_records)
    if not comment:
        return False

    if _try_add_comment_via_gh(issue_url, comment):
        return True
    if _try_add_comment_via_api(issue_url, comment):
        return True
    print(f"[error-reporter] Khong the add fix comment (no auth) cho {issue_url}", file=sys.stderr)
    return False


def _try_create_issue_via_gh(title: str, body: str) -> str | None:
    """Tạo issue qua GitHub CLI. Trả về issue URL nếu thành công."""
    try:
        auth_check = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, timeout=10,
        )
        if auth_check.returncode != 0:
            return None

        repo_info = _get_repo_from_git()
        if not repo_info:
            return None
        owner, repo = repo_info
        repo_arg = f"{owner}/{repo}"

        result = subprocess.run(
            ["gh", "issue", "create",
             "--repo", repo_arg,
             "--title", title,
             "--body", body,
             "--label", "bug",
             "--label", "auto-reported"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            issue_match = re.search(r"/issues/(\d+)", url)
            if issue_match:
                print(f"[error-reporter] Created issue #{issue_match.group(1)}: {url}", file=sys.stderr)
            return url
        print(f"[error-reporter] gh issue create failed: {result.stderr[:200]}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("[error-reporter] gh CLI not found", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("[error-reporter] gh issue create timed out", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[error-reporter] gh error: {exc}", file=sys.stderr)
        return None


def _try_create_issue_via_api(title: str, body: str) -> str | None:
    """Tạo issue qua GitHub REST API. Trả về issue URL nếu thành công."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return None

    repo_info = _get_repo_from_git()
    if not repo_info:
        return None
    owner, repo = repo_info

    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    data = json.dumps({
        "title": title,
        "body": body,
        "labels": ["bug", "auto-reported"],
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "sap-abap-agent-error-reporter",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode())
            issue_num = resp_data.get("number", "?")
            issue_url = resp_data.get("html_url", f"https://github.com/{owner}/{repo}/issues/{issue_num}")
            print(f"[error-reporter] Created issue #{issue_num} via API: {issue_url}", file=sys.stderr)
            return issue_url
    except urllib.error.HTTPError as exc:
        print(f"[error-reporter] API error {exc.code}: {exc.reason[:200]}", file=sys.stderr)
        return None
    except Exception as exc:
        print(f"[error-reporter] API error: {exc}", file=sys.stderr)
        return None


def _try_create_issue(records: list[dict]) -> str | None:
    """Wrapper: thử tạo issue. Trả về URL hoặc None.

    Luôn save local report bất kể có auth GitHub hay không.
    """
    title = _build_issue_title(records)
    body = _build_issue_body(records)

    # Luôn save local report — không cần auth
    _save_local_report(records)

    issue_url = _try_create_issue_via_gh(title, body)
    if issue_url:
        return issue_url

    issue_url = _try_create_issue_via_api(title, body)
    if issue_url:
        return issue_url

    # Lưu vào pending queue — retry lần sau
    pending = _load_json(PENDING_QUEUE, [])
    pending.append({
        "title": title,
        "body": body[:500],
        "error_hash": records[0].get("error_hash", ""),
        "error_count": len(records),
        "timestamp": _now(),
        "retry_count": 0,
    })
    _save_json(PENDING_QUEUE, pending)
    print(f"[error-reporter] Khong co auth GitHub -> luu pending: {title[:60]}", file=sys.stderr)
    return None


# ── Report (Stop hook) ──────────────────────────────────────────────────────
#
# Giai đoạn 1: Gom error → dedup → tạo GitHub issue (cho error mới)
# Giai đoạn 2: Gom fix → match với known issues → add comment fix


def _aggregate_errors() -> dict[str, list[dict]]:
    """Đọc error_log, gom nhóm theo error_hash trong 24h."""
    if not ERROR_LOG.exists():
        return {}

    cutoff = time.time() - DEDUP_WINDOW_SEC
    now_ts = time.time()
    groups: dict[str, list[dict]] = {}

    try:
        text = ERROR_LOG.read_text(encoding="utf-8")
    except OSError:
        return {}

    for line in text.strip().split("\n"):
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue

        rec_ts = rec.get("timestamp", "")
        try:
            rec_epoch = datetime.fromisoformat(rec_ts).timestamp()
        except (ValueError, TypeError):
            rec_epoch = now_ts

        if rec_epoch < cutoff:
            continue

        ehash = rec.get("error_hash", _error_hash(rec.get("error_message", "")))
        groups.setdefault(ehash, []).append(rec)

    return groups


def _aggregate_fixes() -> dict[str, list[dict]]:
    """Đọc fix_log, gom nhóm fix records theo primary_error_hash trong 7 ngày."""
    fixes = _read_log(FIX_LOG, max_age_days=7)
    groups: dict[str, list[dict]] = {}
    for rec in fixes:
        ehash = rec.get("primary_error_hash", "")
        if ehash:
            groups.setdefault(ehash, []).append(rec)
    return groups


def _process_pending_queue() -> dict[str, str]:
    """Retry các issue trong pending queue cũ.

    Returns: dict[error_hash, issue_url]
    """
    pending = _load_json(PENDING_QUEUE, [])
    if not pending:
        return {}

    newly_created: dict[str, str] = {}
    still_pending: list[dict] = []

    for item in pending:
        if item.get("retry_count", 0) >= 3:
            print(f"[error-reporter] Bo qua pending (retry > 3): {item.get('title', '?')[:60]}", file=sys.stderr)
            continue

        url = _try_create_issue_via_gh(item.get("title", ""), item.get("body", ""))
        if not url:
            url = _try_create_issue_via_api(item.get("title", ""), item.get("body", ""))

        if url:
            newly_created[item.get("error_hash", "")] = url
        else:
            item["retry_count"] = item.get("retry_count", 0) + 1
            still_pending.append(item)

    if newly_created:
        print(f"[error-reporter] Da tao {len(newly_created)} issue tu pending queue", file=sys.stderr)

    _save_json(PENDING_QUEUE, still_pending)
    return newly_created


def _run_report() -> None:
    """Main report logic (khoá bằng _FileLock quanh known_issues.json).

    Nhiều session Claude Code có thể chạy song song, cùng gọi Stop hook gần
    nhau — khoá tránh 2 session cùng đọc "chưa có issue" rồi cùng tạo issue
    trùng cho cùng 1 error_hash.
    """
    with _FileLock(KNOWN_ISSUES_LOCK):
        _run_report_locked()


def _run_report_locked() -> None:
    """Phase 1 — Error Reporting: Gom error → dedup → tạo issue (nếu mới).
    Phase 2 — Fix Attaching: Gom fix → match với known issues → add comment fix.
    """
    _ensure_dir()

    # ── Phase 1: Error Reporting ───────────────────────────────────
    groups = _aggregate_errors()
    known = _load_json(KNOWN_ISSUES, {})
    # Giữ issues 7 ngày — cần cho phase 2 (fix-attaching) vì fix có thể đến sau
    cutoff_7d = datetime.fromtimestamp(time.time() - 7 * 86400).isoformat()[:10]
    known = {k: v for k, v in known.items() if v.get("timestamp", cutoff_7d) > cutoff_7d}

    new_count = 0
    for ehash, records in groups.items():
        if ehash in known:
            if len(records) <= REISSUE_THRESHOLD:
                continue
            print(f"[error-reporter] Error {ehash} da xuat hien {len(records)} lan, tao issue bo sung", file=sys.stderr)

        if not _is_meaningful_error(records[0].get("error_type", ""), records[0].get("error_message", "")):
            continue

        issue_url = _try_create_issue(records)
        if issue_url:
            known[ehash] = {
                "issue_url": issue_url,
                "error_count": len(records),
                "timestamp": _now(),
                "error_type": records[0].get("error_type", ""),
            }
            new_count += 1

    # Retry pending queue
    pending_results = _process_pending_queue()
    for ehash, url in pending_results.items():
        if ehash not in known:
            known[ehash] = {
                "issue_url": url,
                "error_count": 0,
                "timestamp": _now(),
                "error_type": "pending_retry",
            }
            new_count += 1

    if new_count:
        _save_json(KNOWN_ISSUES, known)
        print(f"[error-reporter] Da tao {new_count} issue moi trong phien nay", file=sys.stderr)

    # ── Phase 2: Fix Attaching ─────────────────────────────────────
    fix_groups = _aggregate_fixes()
    if fix_groups:
        print(f"[error-reporter] Dang xu ly {sum(len(v) for v in fix_groups.values())} fix records...", file=sys.stderr)

    attached_fixes = 0
    for ehash, fix_records in fix_groups.items():
        issue_info = known.get(ehash)

        # Nếu không có issue trên GitHub, vẫn lưu local report kèm fix
        if not issue_info:
            # Tìm error records cho ehash này trong groups
            error_records = groups.get(ehash, [])
            if error_records:
                _save_local_report(error_records, fix_records)
            continue

        issue_url = issue_info.get("issue_url", "")
        if not issue_url:
            continue

        already_commented = issue_info.get("commented_fix_hashes", [])
        new_fixes = [r for r in fix_records if r.get("fix_hash", "") not in already_commented]
        if not new_fixes:
            continue

        if _try_add_fix_comment(issue_url, new_fixes):
            commented = list(already_commented)
            for r in new_fixes:
                fh = r.get("fix_hash", "")
                if fh and fh not in commented:
                    commented.append(fh)
            known[ehash] = {**issue_info, "commented_fix_hashes": commented}
            attached_fixes += 1

    if attached_fixes:
        _save_json(KNOWN_ISSUES, known)
        print(f"[error-reporter] Da add {attached_fixes} fix comment vao issue", file=sys.stderr)


# ── Status (CLI) ────────────────────────────────────────────────────────────


def _run_status() -> None:
    """In thống kê error + fix hiện tại."""
    groups = _aggregate_errors()
    fix_groups = _aggregate_fixes()
    known = _load_json(KNOWN_ISSUES, {})
    pending = _load_json(PENDING_QUEUE, [])

    total_errors = 0
    total_fixes = 0
    try:
        if ERROR_LOG.exists():
            total_errors = sum(1 for _ in open(ERROR_LOG, encoding="utf-8"))
        if FIX_LOG.exists():
            total_fixes = sum(1 for _ in open(FIX_LOG, encoding="utf-8"))
    except OSError:
        pass

    report = {
        "plugin_version": PLUGIN_VERSION,
        "error_reports_dir": str(ERROR_REPORTS_DIR),
        "total_logged_errors": total_errors,
        "total_logged_fixes": total_fixes,
        "active_error_groups_24h": len(groups),
        "active_fix_groups_7d": len(fix_groups),
        "known_issues_created": len(known),
        "pending_queue": len(pending),
        "error_breakdown": {},
    }

    for ehash, records in groups.items():
        r = records[0]
        report["error_breakdown"][ehash] = {
            "type": r.get("error_type", "?"),
            "tool": r.get("tool", "?"),
            "count": len(records),
            "message_preview": r.get("error_message", "")[:100],
            "has_issue": ehash in known,
            "has_fix": ehash in fix_groups,
            "fix_count": len(fix_groups.get(ehash, [])),
        }

    print(json.dumps(report, indent=2, ensure_ascii=False))


# ── Cleanup old logs ────────────────────────────────────────────────────────


def _rotate_logs() -> None:
    """Xóa error_log cũ hơn 7 ngày."""
    if not ERROR_LOG.exists():
        return
    cutoff = time.time() - DEDUP_WINDOW_SEC * 7
    lines: list[str] = []
    try:
        for line in ERROR_LOG.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            try:
                rec = json.loads(line)
                ts = rec.get("timestamp", "")
                epoch = datetime.fromisoformat(ts).timestamp() if ts else 0
                if epoch >= cutoff:
                    lines.append(line)
            except (json.JSONDecodeError, ValueError, TypeError):
                lines.append(line)
        ERROR_LOG.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    except OSError:
        pass

    # Xoá luôn fix_log cũ
    if FIX_LOG.exists():
        try:
            lines2 = []
            for line in FIX_LOG.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    ts = rec.get("timestamp", "")
                    epoch = datetime.fromisoformat(ts).timestamp() if ts else 0
                    if epoch >= cutoff:
                        lines2.append(line)
                except (json.JSONDecodeError, ValueError, TypeError):
                    lines2.append(line)
            FIX_LOG.write_text("\n".join(lines2) + ("\n" if lines2 else ""), encoding="utf-8")
        except OSError:
            pass


# ── Main Dispatch ───────────────────────────────────────────────────────────


def main() -> None:
    """Entry point — dispatch theo chế độ dòng lệnh.

    Usage (qua hooks.json):
      python hooks/error_reporter.py detect-bash   # PostToolUse Bash
      python hooks/error_reporter.py detect-tool   # PostToolUse MCP tool
      python hooks/error_reporter.py detect-fix    # PostToolUse Edit/Write
      python hooks/error_reporter.py report        # Stop hook
      python hooks/error_reporter.py status        # CLI: xem thống kê
    """
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    # Opt-in: cac mode ghi log/goi GitHub deu tat mac dinh. "status" van cho
    # phep chay (chi doc, khong ghi/goi gi) de tu kiem tra cau hinh.
    if mode in ("detect-bash", "detect-tool", "detect-fix", "report") and not _is_enabled():
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        if mode == "status":
            _run_status()
            return
        sys.exit(0)

    try:
        if mode == "detect-bash" or mode == "detect-tool":
            record = _extract_details(payload)
            if record:
                _record_error_record(record)

        elif mode == "detect-fix":
            fix_record = _detect_fix(payload)
            if fix_record:
                _record_fix_record(fix_record)

        elif mode == "report":
            _rotate_logs()
            _run_report()

        elif mode == "status":
            _run_status()

        sys.exit(0)

    except Exception:
        # Fail open: lỗi trong script không bao giờ block user
        sys.exit(0)


if __name__ == "__main__":
    main()
