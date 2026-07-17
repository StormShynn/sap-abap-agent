"""Test cho reference/scripts/validate_inspired_by_links.py.

Khong goi network that - mock urllib.request.urlopen de co dinh ket qua.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "reference" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_inspired_by_links as vil  # noqa: E402


class _FakeResp:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_classify_url_repo_root():
    assert vil.classify_url("https://github.com/owner/repo") == ("owner", "repo")
    assert vil.classify_url("https://github.com/owner/repo/") == ("owner", "repo")


def test_classify_url_owner_repo_with_dot_and_dash():
    assert vil.classify_url("https://github.com/foo-bar/baz.qux") == ("foo-bar", "baz.qux")


def test_classify_url_rejects_subpath():
    # Sub-path (blob/tree/issues/...) khong phai repo root, bo qua.
    assert vil.classify_url("https://github.com/owner/repo/blob/main/README.md") is None
    assert vil.classify_url("https://github.com/owner/repo/tree/main/src") is None
    assert vil.classify_url("https://github.com/owner/repo/issues/1") is None


def test_classify_url_rejects_non_github():
    assert vil.classify_url("https://gitlab.com/owner/repo") is None
    assert vil.classify_url("https://example.com/owner/repo") is None


def test_classify_url_rejects_malformed_owner_repo():
    # Ky tu khong hop le (space, slash) phai bi loai bo
    assert vil.classify_url("https://github.com/owne r/repo") is None
    # Owner/repo co "/" nghia la path hon 2 phan, tra ve None
    assert vil.classify_url("https://github.com/owner/repo/extra") is None


def test_head_check_ok():
    with mock.patch.object(vil.urllib.request, "urlopen", return_value=_FakeResp(200)):
        assert vil.head_check("https://github.com/owner/repo") == "ok"


def test_head_check_gone():
    err = mock.MagicMock()
    err.code = 404
    err.__class__ = vil.urllib.error.HTTPError  # type: ignore[attr-defined]
    # urllib raise HTTPError; mo phong bang side_effect
    with mock.patch.object(
        vil.urllib.request, "urlopen", side_effect=vil.urllib.error.HTTPError("u", 404, "NF", {}, None)
    ):
        assert vil.head_check("https://github.com/owner/repo") == "gone"


def test_head_check_unchecked_on_network_fail():
    with mock.patch.object(vil.urllib.request, "urlopen", side_effect=OSError("dns")):
        assert vil.head_check("https://github.com/owner/repo") == "unchecked"


def test_collect_urls_finds_github_repo_urls(tmp_path, monkeypatch):
    # Tao 1 file tam co URL hop le + URL sai de kiem tra regex.
    md = tmp_path / "README.md"
    md.write_text(
        "text [link](https://github.com/foo/bar) text\n"
        "ignore me https://gitlab.com/x/y\n"
        "another https://github.com/baz/qux/blob/main/README.md\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(vil, "ROOT", tmp_path)
    monkeypatch.setattr(vil, "TARGET_FILES", ["README.md"])
    monkeypatch.setattr(vil, "_module_skills", lambda: [])

    found = vil.collect_urls()
    assert "README.md" in found
    urls = found["README.md"]
    # Chi 1 URL hop le (foo/bar); qux bi loai vi sub-path
    # collect_urls tra ve tat ca URL match regex (gom ca sub-path);`n    # classify_url moi loai bo sub-path -> _classify_and_check tra ve None cho URL thu 2.`n    assert set(urls) == {"https://github.com/foo/bar", "https://github.com/baz/qux"}


def test_classify_and_check_combines_url_and_status():
    fake = _FakeResp(200)
    with mock.patch.object(vil, "head_check", return_value="ok") as m:
        res = vil._classify_and_check("https://github.com/owner/repo")
    assert res is not None
    assert res.status == "ok"
    assert res.owner == "owner"
    assert res.repo == "repo"
    m.assert_called_once()


def test_classify_and_check_returns_none_for_non_repo_url():
    assert vil._classify_and_check("https://github.com/owner/repo/blob/main/x") is None
    assert vil._classify_and_check("https://gitlab.com/owner/repo") is None
