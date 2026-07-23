# 🔒 Security Policy — SAP ABAP Agent

## Bao mat la uu tien hang dau

Du an **SAP ABAP Agent** ket noi voi he thong SAP that (S/4HANA Cloud, BTP) va co the doc/ghi
code, cau hinh, va du lieu nham. Bao mat thong tin tenant SAP cua ban la **trach nhiem so 1**.

---

## 📋 Mục lục

- [Báo cáo lỗi bảo mật](#báo-cáo-lỗi-bảo-mật)
- [Phạm vi áp dụng](#phạm-vi-áp-dụng)
- [Các biện pháp bảo mật hiện tại](#các-biện-pháp-bảo-mật-hiện-tại)
- [Thực hành tốt cho người dùng](#thực-hành-tốt-cho-người-dùng)
- [Hỗ trợ](#hỗ-trợ)

---

## 🚨 Báo cáo lỗi bảo mật

Nếu bạn phát hiện lỗi bảo mật trong **SAP ABAP Agent** (bao gồm MCP server, plugin, hoặc
bất kỳ component nào), **KHÔNG** tạo public issue trên GitHub. Thay vào đó:

### Quy trình báo cáo

| Bước | Hành động | Chi tiết |
|------|-----------|----------|
| 1 | **Liên hệ maintainer** | Mở **confidential issue** trên GitHub hoặc gửi email đến maintainer |
| 2 | **Cung cấp thông tin** | Mô tả lỗi, cách reproduce, mức độ ảnh hưởng |
| 3 | **Chờ xác nhận** | Maintainer sẽ xác nhận trong vòng **48 giờ** |
| 4 | **Phối hợp fix** | Maintainer sẽ làm việc với bạn để fix và release bản vá |
| 5 | **Công bố** | Sau khi fix, thông tin lỗi sẽ được công bố trong release notes |

### Thông tin cần cung cấp

- Mô tả ngắn gọn về lỗi
- Các bước để reproduce
- Mức độ ảnh hưởng (Critical / High / Medium / Low)
- Version của dự án (xem `.claude-plugin/plugin.json`)
- Môi trường (OS, Python version, SAP system version)
- (Nếu có) PoC code hoặc log

### Cam kết của chúng tôi

- ✅ **Phản hồi trong vòng 48 giờ**
- ✅ **Xử lý nghiêm túc và bảo mật**
- ✅ **Ghi nhận đóng góp** trong Security Advisories
- ✅ **Không truy tố** người báo cáo thiện chí

---

## 🎯 Phạm vi áp dụng

Security Policy này áp dụng cho tất cả các component trong repository:

| Component | Mô tả | Có chứa secrets? |
|-----------|-------|------------------|
| `reference/mcp-server/` | MCP server Python kết nối SAP BTP | ✅ Có (xử lý credentials) |
| `.claude-plugin/plugin.json` | Manifest plugin | ❌ Không |
| `agents/` | Agent definitions (YAML + markdown) | ❌ Không |
| `skills/` | Skill implementations | ❌ Không |
| `commands/` | CLI command guides | ❌ Không |
| `reference/modules/` | Knowledge base | ❌ Không |
| `scripts/` | Utility scripts | ❌ Không (nhưng chứa đường dẫn cá nhân) |

### Không nằm trong phạm vi

- **Hệ thống SAP của bạn**: Dự án này chỉ là công cụ kết nối. Bảo mật tenant SAP
  là trách nhiệm của quản trị viên hệ thống SAP.
- **Third-party services**: CDS KB, SAP Docs Research servers — vui lòng báo cáo
  trực tiếp đến nhà cung cấp dịch vụ tương ứng.

---

## 🛡️ Các biện pháp bảo mật hiện tại

### 1. Mã hóa secrets

| Nền tảng | Phương pháp | Chi tiết |
|----------|-------------|----------|
| **Windows** | DPAPI | Mã hóa bằng Windows Data Protection API, gắn với tài khoản Windows |
| **macOS/ Linux** | AES-256-GCM | Key derive từ `hostname + username`, file mode `0o600` |

### 2. Phân tách profile

Mỗi project SAP có profile riêng, secret riêng, mã hóa độc lập:

```
%USERPROFILE%\.sap-btp-agent\profiles\<project-id>\   (Windows)
~/.sap-btp-agent/profiles/<project-id>/               (macOS/Linux)
+-- config.json     <- URL, tenant, client_id (không nhạy cảm)
+-- secrets.json    <- client_secret, token (ĐÃ MÃ HÓA)
```

### 3. File permissions

- File secrets: Chỉ owner read/write (`0o600` trên macOS/Linux)
- Folder cấu hình: Chỉ owner access
- `.gitignore` loại trừ tất cả file cá nhân (`.sap-abap-agent/`, `_*.py`, `scripts/run_sync_skills.bat`)

### 4. Best practices trong code

- **Không hardcode credentials**: Tất cả secrets lưu trong file riêng, mã hóa
- **Stampede protection**: Chỉ 1 lần re-auth cho multiple concurrent 401 requests
- **Cookie isolation**: Cookies cũ được giữ đến khi cookies mới được xác nhận
- **Input validation**: URL, path, và tham số được validate trước khi xử lý
- **No eval()**: Không sử dụng `eval()` hoặc dynamic code execution

### 5. Dependencies

| Dependency | Mục đích | Rủi ro | Giảm thiểu |
|------------|----------|--------|------------|
| `httpx` | HTTP client | MITM | SSL verification mặc định |
| `cryptography` | Mã hóa | Library bug | Dùng bản mới nhất, pinned version |
| `pyyaml` | YAML parsing | Deserialization | Chỉ dùng safe_load |

---

## 👍 Thực hành tốt cho người dùng

### Khi sử dụng SAP ABAP Agent

- ✅ **Luôn dùng phiên bản mới nhất** (check `git pull` thường xuyên)
- ✅ **Sử dụng OAuth2 client_credentials** thay vì username/password nếu có thể
- ✅ **Giới hạn scope của service key** trong SAP BTP (chỉ cấp quyền tối thiểu)
- ✅ **Kiểm tra log định kỳ** tại `.sap-btp-agent/log/`
- ✅ **Xóa profile không dùng** bằng `sap-btp-agent profiles remove <id>`

### Không nên

- ❌ **Không commit** `.sap-btp-agent/`, `scripts/run_sync_skills.bat`, hoặc `_*.py` lên GitHub
- ❌ **Không share** file `secrets.json` hoặc `profiles/` cho người khác
- ❌ **Không dùng** SAP ABAP Agent trên tenant production chưa được phép
- ❌ **Không paste** credentials, session cookies, hoặc token vào public chat/public issues

### Checklist bảo mật hàng ngày

- [ ] Đã `git pull` bản mới nhất?
- [ ] Profile nào đang active? (`sap-btp-agent profiles list`)
- [ ] Có profile cũ không dùng nữa? (xóa đi)
- [ ] Secret có còn hạn? (OAuth2 token expiration)
- [ ] Log có dấu hiệu bất thường?

---

## 📧 Hỗ trợ

| Kênh | Mô tả | Phản hồi |
|------|-------|----------|
| GitHub Issues (confidential) | Báo cáo lỗi bảo mật | 48 giờ |
| GitHub Issues (public) | Câu hỏi chung về bảo mật | 1 tuần |
| [@StormShynn](https://github.com/StormShynn) | Liên hệ trực tiếp maintainer | 48 giờ |

**PGP Key**: (Coming soon)

---

## 📜 Lịch sử thay đổi

| Ngày | Phiên bản | Thay đổi |
|------|-----------|----------|
| 2026-07-11 | v1.0 | Tạo SECURITY.md lần đầu |

---

*Dự án SAP ABAP Agent — Bảo mật là trách nhiệm của tất cả chúng ta.*
