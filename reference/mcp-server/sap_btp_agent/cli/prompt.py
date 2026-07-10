"""Helper hoi user qua stdin/stdout."""
from __future__ import annotations

import sys


def ask(question: str, *, default: str | None = None,
        validate=None, secret: bool = False) -> str:
    """Hoi user. Tra lai chuoi sau khi trim.

    secret=True: khong in ky tu gi ngoai prompt (chi an text, khong an enter).
    """
    hint = f" [{default}]" if default is not None else ""
    sys.stdout.write(f"{question}{hint}: ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise EOFError("User huy (Ctrl+D).")
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
