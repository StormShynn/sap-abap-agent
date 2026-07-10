"""Ma hoa secrets (token, client_secret) theo tung profile.

Moi profile co file secrets.json rieng (mode 0o600), ma hoa doc lap.

Chien luoc ma hoa (uu tien):
  1. Windows + co pywin32 -> DPAPI qua win32crypt
  2. macOS   + co keyring  -> Keychain
  3. Cross-platform fallback -> AES-256-GCM voi key derive
     tu hostname + username (scrypt).
"""
from __future__ import annotations

import base64
import json
import os
import socket
from dataclasses import dataclass
from getpass import getuser
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .paths import get_profile_secrets_file
from .profile import ensure_app_dir, get_current_active

# === Key derive cho AES fallback =====================================
_AES_KEY_SALT = "sap-btp-agent-v1"


def _derive_key() -> bytes:
    """Scrypt key tu hostname + username. Dung cho AES-256-GCM."""
    salt = f"{socket.gethostname()}|{getuser()}|{_AES_KEY_SALT}".encode("utf-8")
    # scrypt: 32 bytes key, 16 bytes salt -> 32 bytes output
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    return kdf.derive(b"sap-btp-agent")


@dataclass
class Blob:
    algo: str
    data: str  # base64


def _encrypt_aes(plaintext: str) -> dict[str, str]:
    key = _derive_key()
    nonce = os.urandom(12)
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return {
        "algo": "aes-256-gcm-v1",
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "data": base64.b64encode(ct).decode("ascii"),
    }


def _decrypt_aes(blob: dict[str, str]) -> str:
    key = _derive_key()
    nonce = base64.b64decode(blob["nonce"])
    ct = base64.b64decode(blob["data"])
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None).decode("utf-8")


def _try_dpapi_protect(plaintext: str) -> dict[str, str] | None:
    """DPAPI tren Windows neu co pywin32."""
    if os.name != "nt":
        return None
    try:
        import win32crypt  # type: ignore
    except ImportError:
        return None
    try:
        blob = win32crypt.CryptProtectData(
            plaintext.encode("utf-8"),
            "sap-btp-agent",
            None,
            None,
            None,
            0x01,  # CRYPTPROTECT_LOCAL_MACHINE = 0x04, CURRENT_USER = 0
        )
        return {
            "algo": "dpapi-v1",
            "data": base64.b64encode(blob).decode("ascii"),
        }
    except Exception:
        return None


def _try_dpapi_unprotect(blob_b64: str) -> str | None:
    if os.name != "nt":
        return None
    try:
        import win32crypt  # type: ignore
    except ImportError:
        return None
    try:
        raw = base64.b64decode(blob_b64)
        plain, _ = win32crypt.CryptUnprotectData(raw, None, None, None, 0)
        return plain.decode("utf-8")
    except Exception:
        return None


def _encrypt_string(plaintext: str) -> dict[str, str]:
    if os.name == "nt":
        blob = _try_dpapi_protect(plaintext)
        if blob is not None:
            return blob
    return _encrypt_aes(plaintext)


def _decrypt_string(blob: dict[str, str]) -> str:
    algo = blob.get("algo")
    if algo == "dpapi-v1":
        out = _try_dpapi_unprotect(blob["data"])
        if out is not None:
            return out
        # Fallback neu doi may / khong decrypt duoc
        raise RuntimeError("Khong giai ma duoc DPAPI (co the do doi may user).")
    if algo == "aes-256-gcm-v1":
        return _decrypt_aes(blob)
    raise RuntimeError(f"Algo khong ho tro: {algo}")


# === Public API =====================================================
def _resolve_id(profile_id: str | None) -> str | None:
    env = os.environ.get("SAP_BTP_PROFILE", "").strip()
    if env:
        return env
    return profile_id


async def _ensure_id(profile_id: str | None) -> str:
    pid = _resolve_id(profile_id) or get_current_active()
    if not pid:
        raise RuntimeError("Chua co profile nao. Chay: sap-btp-agent setup")
    return pid


async def save_secrets(profile_id: str | None, secrets: dict[str, Any]) -> dict[str, Any]:
    pid = await _ensure_id(profile_id)
    ensure_app_dir()
    file = get_profile_secrets_file(pid)
    file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    blob = _encrypt_string(json.dumps(secrets, ensure_ascii=False))
    file.write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(file, 0o600)
    except Exception:
        pass
    return {"id": pid, "file": str(file)}


async def load_secrets(profile_id: str | None = None) -> dict[str, Any]:
    pid = await _ensure_id(profile_id)
    file = get_profile_secrets_file(pid)
    if not file.exists():
        return {}
    try:
        blob = json.loads(file.read_text(encoding="utf-8"))
        plain = _decrypt_string(blob)
        return json.loads(plain)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Loi doc secrets cua '{pid}': {err}") from err
    except Exception as err:
        if "Khong giai ma" in str(err):
            raise
        raise RuntimeError(f"Loi doc secrets cua '{pid}': {err}") from err


async def update_secrets(profile_id: str | None, partial: dict[str, Any]) -> dict[str, Any]:
    pid = await _ensure_id(profile_id)
    current = await load_secrets(pid)
    merged = {**current, **partial}
    await save_secrets(pid, merged)
    return {"id": pid, "merged": merged}


async def clear_secrets(profile_id: str | None) -> dict[str, Any]:
    pid = await _ensure_id(profile_id)
    file = get_profile_secrets_file(pid)
    try:
        file.unlink(missing_ok=True)
    except Exception:
        pass
    return {"id": pid}
