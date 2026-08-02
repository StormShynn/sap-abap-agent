"""Test _keep_alive_loop cap nhat tin hieu het han theo thoi gian thuc:
- Ping thanh cong -> gia han uoc luong (goi lai cookie_auth.save_cookies()).
- Ping that bai -> danh dau het han NGAY (update_secrets cookie_expires_at=now)
  thay vi de nguyen uoc luong cu (co the con sai toi vai gio).

Dung pytest thuong (khong asyncio.run(main()) o module scope nhu cac file
test_auto*/test_int* cu) - can pytest-asyncio hoac chay qua asyncio.run truc
tiep trong ham test (dung o day de khong phu thuoc plugin ngoai).
"""
import asyncio
from unittest.mock import AsyncMock, patch

from mcp_sap_connect.sap.client import SapClient


def _run(coro):
    return asyncio.run(coro)


def test_keep_alive_success_extends_estimate():
    async def scenario():
        client = SapClient("fake_profile_for_test")
        client.config = {"authMode": "cookie", "btpUrl": "https://example.com"}
        client._initialized = True
        client.cookie_auth.save_cookies = AsyncMock()

        with patch.object(client, "check_write_access", new=AsyncMock(return_value="ok")), \
             patch("mcp_sap_connect.config.secrets.update_secrets", new=AsyncMock()) as mock_update:
            client.start_keep_alive(interval_s=0.05)
            await asyncio.sleep(0.15)
            client.stop_keep_alive()
            await asyncio.sleep(0.05)

        assert client.cookie_auth.save_cookies.call_count >= 1
        assert mock_update.call_count == 0

    _run(scenario())


def test_keep_alive_failure_marks_expired_now():
    async def scenario():
        client = SapClient("fake_profile_for_test")
        client.config = {"authMode": "cookie", "btpUrl": "https://example.com"}
        client._initialized = True
        client.cookie_auth.save_cookies = AsyncMock()

        with patch.object(client, "check_write_access",
                           new=AsyncMock(side_effect=RuntimeError("session dead"))), \
             patch("mcp_sap_connect.config.secrets.update_secrets", new=AsyncMock()) as mock_update:
            before = asyncio.get_event_loop().time()
            client.start_keep_alive(interval_s=0.05)
            await asyncio.sleep(0.15)
            client.stop_keep_alive()
            await asyncio.sleep(0.05)

        assert client.cookie_auth.save_cookies.call_count == 0
        assert mock_update.call_count >= 1
        pid, partial = mock_update.call_args.args
        assert pid == "fake_profile_for_test"
        assert "cookie_expires_at" in partial
        import time
        # Moc thoi gian ghi phai gan "bay gio" (khong phai gia tri cu/uoc luong xa).
        assert abs(partial["cookie_expires_at"] - time.time()) < 5

    _run(scenario())


def test_keep_alive_skips_secrets_update_for_non_cookie_auth():
    """OAuth2/password/bearer: keep-alive van ping duoc nhung KHONG dung toi
    cookie_auth.save_cookies()/update_secrets - vi expiry cua cac mode nay da
    tu quan ly rieng (token refresh), khong lien quan uoc luong cookie."""
    async def scenario():
        client = SapClient("fake_profile_for_test")
        client.config = {"authMode": "oauth2", "btpUrl": "https://example.com"}
        client._initialized = True
        client.cookie_auth.save_cookies = AsyncMock()

        with patch.object(client, "check_write_access", new=AsyncMock(return_value="ok")), \
             patch("mcp_sap_connect.config.secrets.update_secrets", new=AsyncMock()) as mock_update:
            client.start_keep_alive(interval_s=0.05)
            await asyncio.sleep(0.15)
            client.stop_keep_alive()
            await asyncio.sleep(0.05)

        assert client.cookie_auth.save_cookies.call_count == 0
        assert mock_update.call_count == 0

    _run(scenario())
