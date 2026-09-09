# Org setup — Windows Authenticode (GUI installer)

Mục đích: giảm SmartScreen khi phân phối NSIS/MSI nội bộ công ty.
**Updater trong app** đã tin cậy qua **minisign** (`gui-latest`) — Authenticode là UX bổ sung.

Chi tiết contributor/CI: [`gui-native/.signing/README.md`](../gui-native/.signing/README.md).

---

## Khi nào cần

| Tình huống | Cần Authenticode? |
|------------|-------------------|
| Pilot &lt; 10 người, tin Release GitHub | Không bắt buộc (More info → Run anyway) |
| Rollout rộng / IT policy cấm unsigned | Có — OV hoặc EV code signing cert |

---

## Bước cho org admin

1. Mua cert **OV/EV Code Signing** (DigiCert, Sectigo, …) theo tên công ty.
2. Export **PFX** + password (lưu vault nội bộ, không commit).
3. Trên repo `StormShynn/sap-abap-agent` (hoặc fork nội bộ), set GitHub Actions secrets:
   - `WINDOWS_CERTIFICATE` — nội dung PFX (base64 theo hướng dẫn workflow `gui-release`)
   - `WINDOWS_CERTIFICATE_PASSWORD`
4. Giữ secrets minisign updater (`TAURI_SIGNING_PRIVATE_KEY*`) như hiện tại.
5. Tag lại `gui-vX.Y.Z` để workflow build + ký.
6. Smoke: cài NSIS trên máy sạch → SmartScreen sạch hơn / không chặn → About → Check for updates.

---

## Không làm

- Không commit file `.pfx` / `.key` vào git.
- Không dùng cert cá nhân cho bản phát hành công ty nếu IT yêu cầu OV/EV org.
- Không thay minisign updater bằng “chỉ Authenticode” — giữ cả hai kênh.

---

## Liên kết

- Rollout team: [`rollout-guide.md`](rollout-guide.md)
- Signing keys updater: [`gui-native/.signing/README.md`](../gui-native/.signing/README.md)
