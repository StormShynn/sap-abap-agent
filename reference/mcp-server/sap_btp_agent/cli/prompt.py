"""Helper hoi user qua stdin/stdout."""
from __future__ import annotations

import sys


class UserCancelled(Exception):
    """User da huy thu tac vu dang nhap/setup (Ctrl+C / Ctrl+D / Ctrl+Z+Enter).

    Caller (CLI) bat exception nay de thoat sach, KHONG traceback, KHONG ghi
    config/secrets moi - chi giu nguyen trang thai cu.
    """

    def __init__(self, where: str = "?"):
        super().__init__(f"User cancelled at {where}")
        self.where = where


def ask(question: str, *, default: str | None = None,
        validate=None, secret: bool = False) -> str:
    """Hoi user. Tra lai chuoi sau khi trim.

    secret=True: khong in ky tu gi ngoai prompt (chi an text, khong an enter).
    """
    hint = f" [{default}]" if default is not None else ""
    sys.stdout.write(f"{question}{hint}: ")
    sys.stdout.flush()
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        raise UserCancelled("ask (Ctrl+C)")
    if not line:
        # Ctrl+D / Ctrl+Z+Enter: stdin dong, khong co du lieu -> user huy.
        raise UserCancelled("ask (stdin closed)")
    ans = line.rstrip("\n").rstrip("\r").strip()
    if not ans and default is not None:
        ans = default
    if validate and not validate(ans):
        print("  -> Gia tri chua hop le, nhap lai nhe.")
        return ask(question, default=default, validate=validate, secret=secret)
    return ans


def header(text: str) -> None:
    line = "=" * max(len(text) + 2, 30)
    print(f"\n{line}\n {text}\n{line}")


def info(text: str) -> None:
    print(f"  i {text}")


def ok(text: str) -> None:
    print(f"  OK {text}")


def warn(text: str) -> None:
    print(f"  !! {text}")
