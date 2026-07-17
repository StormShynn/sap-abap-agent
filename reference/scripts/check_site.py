#!/usr/bin/env python3
"""Static + optional browser smoke check for index.html.

Static checks run with zero extra dependencies and catch the exact bug class
hit in this repo before: unbalanced tags from a bad string-replace, duplicated
injected blocks, JS that toggles a CSS class no stylesheet rule ever styles.

    python scripts/check_site.py              # static checks only
    python scripts/check_site.py --browser     # + a real headless-Chromium load

The --browser mode needs Playwright (already an optional dependency of this
project's MCP server, see reference/mcp-server/pyproject.toml):

    pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SITE = ROOT / "index.html"
FAILURES: list[str] = []


def fail(check: str, msg: str) -> None:
    FAILURES.append(f"[{check}] {msg}")


def check_tag_balance(html: str) -> None:
    opens = len(re.findall(r"<div[\s>]", html))
    closes = html.count("</div>")
    if opens != closes:
        fail(
            "tag-balance",
            f"<div> open/close count mismatch: {opens} opened vs {closes} closed — "
            f"a stray/missing closing tag will misnest the DOM (this exact bug broke "
            f"the header layout once already)",
        )


def check_duplicate_blocks(html: str) -> None:
    markers = re.findall(r"/\*\s*={3,}\s*([A-Z0-9 ]+?)\s*={3,}\s*\*/", html)
    seen: dict[str, int] = {}
    for m in markers:
        seen[m] = seen.get(m, 0) + 1
    for marker, count in seen.items():
        if count > 1:
            fail(
                "dup-block",
                f"CSS/JS block marker '/* ===== {marker} ===== */' appears {count} times — "
                f"likely a non-idempotent generator script re-inserting the same block",
            )

    script_tags = re.findall(
        r"<script(\s[^>]*)?>(.*?)</script\s*>", html, re.DOTALL | re.IGNORECASE
    )
    # A script tag with a src= attribute is *meant* to have an empty body — only flag
    # empty inline (no-src) tags, which are dead leftovers from a bad dedup pass.
    empty = sum(1 for attrs, body in script_tags if "src=" not in (attrs or "") and not body.strip())
    if empty:
        fail(
            "dup-block",
            f"{empty} empty <script></script> tag(s) found — leftover from a dedup pass "
            f"that stripped the body but not the wrapper tag",
        )


def check_unstyled_toggled_classes(html: str) -> None:
    style_blocks = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.DOTALL))
    toggled = set(re.findall(r"classList\.(?:add|toggle)\(['\"]([a-zA-Z0-9_-]+)['\"]", html))
    for cls in sorted(toggled):
        if not re.search(rf"\.{re.escape(cls)}\b\s*[,{{]", style_blocks):
            fail(
                "unstyled-class",
                f"JS toggles class '.{cls}' via classList but no '.{cls} {{' rule exists "
                f"in any <style> block — the toggle has no visible effect",
            )


def run_static() -> None:
    if not SITE.exists():
        fail("missing-file", f"{SITE.relative_to(ROOT)} not found")
        return
    html = SITE.read_text(encoding="utf-8")
    check_tag_balance(html)
    check_duplicate_blocks(html)
    check_unstyled_toggled_classes(html)


def run_browser() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fail(
            "browser",
            "playwright not installed — run: pip install playwright && "
            "playwright install chromium",
        )
        return

    console_errors: list[str] = []
    network_blocked = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)
        page.on("pageerror", lambda exc: console_errors.append(f"pageerror: {exc}"))
        page.goto(SITE.resolve().as_uri())
        page.wait_for_timeout(1000)

        network_blocked = any(
            "ERR_NETWORK_ACCESS_DENIED" in e or "ERR_INTERNET_DISCONNECTED" in e or "ERR_NAME_NOT_RESOLVED" in e
            for e in console_errors
        ) or page.evaluate("typeof FlexSearch === 'undefined'")

        for selector, label in [
            ("#searchInput", "search input"),
            ("#langToggle", "language toggle button"),
            ("#themeToggle", "theme toggle button"),
        ]:
            if page.locator(selector).count() == 0:
                fail("browser", f"expected element {label} ({selector}) not found on page")

        if network_blocked:
            print(
                "  SKIP  [browser] FlexSearch CDN unreachable from this environment "
                "(sandboxed/offline) — search-interaction check skipped; re-run with normal "
                "internet access for a trustworthy result"
            )
        elif page.locator("#searchInput").count() > 0:
            page.fill("#searchInput", "SAP")
            page.wait_for_timeout(500)
            results = page.locator("#searchResults")
            if results.count() == 0 or not results.first.is_visible():
                fail(
                    "browser",
                    "typing into #searchInput did not open #searchResults — search feature "
                    "appears broken",
                )

        browser.close()

    for err in console_errors:
        if network_blocked and ("flexsearch" in err.lower() or "ERR_NETWORK" in err or "ERR_INTERNET" in err or "ERR_NAME_NOT_RESOLVED" in err):
            continue
        fail("browser-console", f"console error on load: {err[:150]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", action="store_true", help="also run a headless-Chromium load")
    args = parser.parse_args()

    run_static()
    if args.browser:
        run_browser()

    if FAILURES:
        print(f"--- {len(FAILURES)} finding(s) ---")
        for f in FAILURES:
            print(f"  FAIL  {f}")
        print(f"\ncheck_site.py: {len(FAILURES)} finding(s)")
        return 1

    print("check_site.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
