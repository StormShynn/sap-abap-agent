#!/usr/bin/env python3
"""Kiem tra cac GitHub repo URL trong cac file markdown co section "Inspired by" / cam hung.

Quet cac file:
  - README.md
  - CHANGELOG.md
  - reference/modules/*/SKILL.md
  - docs/sap-mcp-recommendations.md

Trich GitHub repo URL dang `https://github.com/<owner>/<repo>` (khong phai sub-path, khong phai
raw blob), HEAD request tung URL, in bang tom tat. FAIL-O PEN: loi mang (timeout, DNS, 5xx)
khong lam script exit non-zero — chi danh dau "unchecked" de reviewer xem xet.

    python reference/scripts/validate_inspired_by_links.py [--strict] [--concurrency 8]

Options:
  --strict          Exit non-zero neu co URL tra ve 404.
  --concurrency N   So HEAD request song song (mac dinh 8).
"""
from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent.parent

# File quet (relative den ROOT)
TARGET_FILES = [
    "README.md",
    "CHANGELOG.md",
    "docs/sap-mcp-recommendations.md",
]

# Tat ca reference/modules/<name>/SKILL.md
def _module_skills() -> list[str]:
    out = []
    for d in (ROOT / "reference" / "modules").glob("*/SKILL.md"):
        out.append(str(d.relative_to(ROOT)))
    return out

GITHUB_REPO_RE = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?")


@dataclass
class CheckResult:
    url: str
    owner: str
    repo: str
    status: str  # "ok", "gone", "unchecked", "not_repo"
    detail: str = ""


def classify_url(url: str) -> tuple[str, str] | None:
    """Tra ve (owner, repo) neu URL la GitHub repo root, khong phai deeper path."""
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    # Loai bo sub-path (blob/tree/issues/...) hoac chi href logo.
    if len(parts) > 2:
        return None
    # Loai bo cac repo co ten ket thuc bang extension (blob URL thuong co them /blob/...)
    # owner/repo co the chi chua ky tu chu + so + _ + . + -
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner):
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        return None
    return owner, repo


def head_check(url: str, timeout: float = 8.0) -> str:
    """HEAD request nhe. Tra ve 'ok' / 'gone' / 'unchecked'."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.status
            return "ok" if code < 400 else ("gone" if code == 404 else "unchecked")
    except urllib.error.HTTPError as e:
        return "gone" if e.code == 404 else "unchecked"
    except Exception:
        return "unchecked"


def collect_urls() -> dict[str, list[str]]:
    """Quet cac file target, tra ve {file_relpath: [url, ...]}."""
    found: dict[str, list[str]] = {}
    files = list(TARGET_FILES) + _module_skills()
    for rel in files:
        p = ROOT / rel
        if not p.exists():
            continue
        urls = []
        seen: set[str] = set()
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            for m in GITHUB_REPO_RE.finditer(line):
                url = m.group(0).rstrip("/")
                if url in seen:
                    continue
                seen.add(url)
                urls.append(url)
        found[rel] = urls
    return found


def run(strict: bool, concurrency: int) -> int:
    files = collect_urls()
    all_results: list[tuple[str, CheckResult]] = []

    # Gom URL unique de khong HEAD trung
    url_to_files: dict[str, list[str]] = {}
    for f, urls in files.items():
        for url in urls:
            url_to_files.setdefault(url, []).append(f)

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        futures = {pool.submit(_classify_and_check, url): url for url in url_to_files}
        for fut in as_completed(futures):
            url = futures[fut]
            res = fut.result()
            if res is None:
                continue
            for f in url_to_files[url]:
                all_results.append((f, res))

    # Sort cho output on dinh: theo owner/repo/file.
    all_results.sort(key=lambda x: (x[1].owner, x[1].repo, x[0]))

    n_ok = n_gone = n_unchecked = n_skip = 0
    by_status: dict[str, list[CheckResult]] = {"ok": [], "gone": [], "unchecked": []}
    for _, res in all_results:
        by_status.setdefault(res.status, []).append(res)
        if res.status == "ok":
            n_ok += 1
        elif res.status == "gone":
            n_gone += 1
        else:
            n_unchecked += 1

    print("=" * 72)
    print("  sap-abap-agent - validate Inspired-by GitHub URLs")
    print("=" * 72)
    for status, items in by_status.items():
        if not items:
            continue
        print(f"\n[{status.upper()}] ({len(items)})")
        seen = set()
        for res in items:
            key = (res.owner, res.repo)
            if key in seen:
                continue
            seen.add(key)
            print(f"  - {res.owner}/{res.repo:<30} {res.url}")

    print(f"\n=== summary ===")
    print(f"  OK        : {n_ok}")
    print(f"  GONE (404): {n_gone}")
    print(f"  UNCHECKED : {n_unchecked}  (network fail, khong phai loi)")
    print(f"  File quet : {len(files)}")

    if strict and n_gone > 0:
        print("\n[strict] co URL tra ve 404, exit non-zero.")
        return 1
    return 0


def _classify_and_check(url: str) -> CheckResult | None:
    info = classify_url(url)
    if not info:
        return None
    owner, repo = info
    # Repo URL chuan hoa (them /) de redirect resolution deu xu ly nhu nhau.
    normalized = f"https://github.com/{owner}/{repo}"
    status = head_check(normalized)
    return CheckResult(url=url, owner=owner, repo=repo, status=status)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Inspired-by GitHub URLs.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero neu co 404.")
    parser.add_argument("--concurrency", type=int, default=8)
    args = parser.parse_args(argv)
    return run(strict=args.strict, concurrency=args.concurrency)


if __name__ == "__main__":
    sys.exit(main())
