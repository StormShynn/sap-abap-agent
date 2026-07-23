"""Xac dinh duong dan folder cau hinh trong user home.

Mac dinh:
    Windows: %USERPROFILE%\\.sap-btp-agent\\
    macOS/Linux: ~/.sap-btp-agent/

Co the override qua SAP_BTP_AGENT_HOME.

Cau truc multi-profile:
    <appDir>/
    +- profiles.json             <- registry
    +- profiles/<id>/
    |   +- config.json           <- thong tin khong nhay cam
    |   +- secrets.json          <- secret da ma hoa
    +- log/
    +- cache/
    +- in/                       <- FS/tai lieu dau vao (Function Spec, ...), khong commit git
    +- out/                      <- output sinh ra (md, INTAKE/TECHNICAL_SPEC, scaffold ABAP...)
"""
from __future__ import annotations

import os
import re
from pathlib import Path

APP_DIR_NAME = ".sap-btp-agent"

_PROFILE_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def get_app_dir() -> Path:
    """Tra ve folder goc cua SAP BTP Agent. Tao neu chua co (lazy)."""
    override = os.environ.get("SAP_BTP_AGENT_HOME", "").strip()
    if override:
        return Path(override).resolve()
    home = Path.home()
    if not home or str(home) == "":
        raise RuntimeError("Khong xac dinh duoc thu muc home.")
    return home / APP_DIR_NAME


def get_active_profile_id() -> str | None:
    """Env SAP_BTP_PROFILE (uu tien cao nhat) hoac None."""
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    return env or None


def _validate_profile_id(id_: str) -> None:
    if not id_ or not _PROFILE_ID_RE.match(id_) or len(id_) > 64:
        raise ValueError(
            f'Profile id khong hop le: "{id_}". '
            "Chi cho phep chu, so, '.', '_', '-' (toi da 64 ky tu)."
        )


def get_profiles_dir() -> Path:
    return get_app_dir() / "profiles"


def get_profile_dir(id_: str) -> Path:
    _validate_profile_id(id_)
    return get_profiles_dir() / id_


def get_profile_config_file(id_: str) -> Path:
    return get_profile_dir(id_) / "config.json"


def get_profile_secrets_file(id_: str) -> Path:
    return get_profile_dir(id_) / "secrets.json"


def get_registry_file() -> Path:
    return get_app_dir() / "profiles.json"


def get_log_dir() -> Path:
    return get_app_dir() / "log"


def get_cache_dir() -> Path:
    return get_app_dir() / "cache"


def get_in_dir() -> Path:
    """Thu muc chua tai lieu dau vao (Function Spec .docx/.xlsx...) - khong nam trong git repo."""
    return get_app_dir() / "in"


def get_out_dir() -> Path:
    """Thu muc chua output sinh ra (md, INTAKE/TECHNICAL_SPEC, scaffold ABAP...) - khong nam trong git repo."""
    return get_app_dir() / "out"


# === Dev mirror (CHI danh cho nguoi dang build/sua plugin nay) ==========
#
# Mac dinh sap-btp-agent chi ghi vao get_app_dir() (%USERPROFILE%\.sap-btp-agent hoac
# SAP_BTP_AGENT_HOME). End user thuc te KHONG BAO GIO dat 2 bien env duoi day, nen hanh vi
# cua ho khong doi. Chi khi dang dev plugin va muon tien kiem tra config/registry ngay trong
# project (khong phai mo %USERPROFILE%) thi moi dat SAP_BTP_AGENT_DEV_MIRROR.


def get_dev_mirror_dir() -> Path | None:
    """Thu muc mirror (vd: <project>/.sap-abap-agent/dev-mirror) - None neu khong dat."""
    override = os.environ.get("SAP_BTP_AGENT_DEV_MIRROR", "").strip()
    return Path(override).resolve() if override else None


def dev_mirror_includes_secrets() -> bool:
    """secrets.json (da ma hoa) chi duoc mirror neu dat rieng bien nay = '1' - mac dinh KHONG,
    tranh nhan doi noi luu du lieu nhay cam kem can thiet cho muc dich 'tien kiem tra config'."""
    return os.environ.get("SAP_BTP_AGENT_DEV_MIRROR_SECRETS", "").strip() == "1"


def _mirror_target(real_file: Path) -> Path | None:
    """Duong dan tuong ung trong mirror dir cho real_file, hoac None neu khong ap dung
    (khong bat mirror, hoac real_file nam ngoai get_app_dir() - vd user tu -o path khac)."""
    mirror_root = get_dev_mirror_dir()
    if mirror_root is None:
        return None
    try:
        rel = real_file.relative_to(get_app_dir())
    except ValueError:
        return None
    return mirror_root / rel


def mirror_write_text(real_file: Path, content: str, *, sensitive: bool = False) -> None:
    """Ghi them 1 ban sao cua real_file (dang text) vao SAP_BTP_AGENT_DEV_MIRROR (neu co dat),
    giu nguyen cau truc con tuong doi so voi app dir. No-op neu khong dat bien env, hoac
    real_file nam ngoai app dir. Best-effort: loi mirror KHONG duoc lam fail thao tac ghi that
    (real_file da ghi xong truoc khi ham nay duoc goi)."""
    if sensitive and not dev_mirror_includes_secrets():
        return
    target = _mirror_target(real_file)
    if target is None:
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except Exception:
        pass


def mirror_write_bytes(real_file: Path, content: bytes) -> None:
    """Nhu mirror_write_text nhung cho noi dung nhi phan (vd anh trich xuat tu .docx trong
    sap-doc-to-md). Khong co tham so sensitive - noi dung dang xu ly o day (tai lieu FS da
    convert) khong phai secret ket noi, chi la du lieu nghiep vu can can nhac rieng (xem
    canh bao trong office_to_md.py ve khong commit tai lieu khach hang)."""
    target = _mirror_target(real_file)
    if target is None:
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    except Exception:
        pass
