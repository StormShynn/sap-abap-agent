---
description: Cai dat toan bo cho may moi lan dau dung plugin nay - tu cai, tu dang ky MCP, tu sinh file config mau; user chi can dien 1 file va chay 1 lenh, khong con phai tra loi wizard tung buoc
argument-hint: ""
---

# /sap-setup — Cai dat toan bo cho may moi, it thao tac tay nhat co the

Lenh nay tu dong lam **toan bo** phan cai dat (kiem tra Python, pip install, dang ky MCP) —
KHONG hoi user cau nao ve nhung thu Claude tu quyet dinh duoc (OS, extra nao nen cai, dung wheel
hay editable). Phan **duy nhat khong the tu dong** la nhap credential SAP that (khong ai doan
duoc thay user) — phan nay cung duoc rut gon toi da: thay vi tra loi wizard nhieu buoc trong
terminal, user chi **dien 1 file JSON mau** roi chay **1 lenh**.

**Khong chi go tay**: hook `hooks/first_run_check.py` (SessionStart) tu kiem tra offline moi
phien — neu chua thay profile SAP nao, Claude se **chu dong hoi** user co muon chay `/sap-setup`
khong. Neu da co it nhat 1 profile, hook im lang.

## Cach dung

```text
/sap-setup
```

Khong can tham so. Chay 1 lan tren may moi; chay lai cung an toan (idempotent — buoc nao da
xong tu bo qua, khong lam lai).

## Quy trinh (Claude tu quyet dinh moi thu KHONG lien quan credential — chi dung lai o phan bat buoc phai co that)

### Buoc 1: Kiem tra Python + cai dat (tu dong, khong hoi)

```bash
python --version                    # yeu cau >= 3.10
python -m mcp_sap_connect.doctor    # da cai chua?
```

- Python `< 3.10` → dung lai, bao user nang cap truoc (khong the tu dong hoa buoc nay).
- Doctor OK → da cai roi, bo qua phan cai dat, sang Buoc 2.
- Doctor bao loi PATH → tu ap dung lenh fix doctor da in san (`Invoke-Expression` lenh
  PowerShell do neu Windows), roi kiem tra lai — chi bao user neu lenh fix that bai.
- Chua cai (`ModuleNotFoundError`) → tu cai, **khong hoi gi**:
  1. Tu phat hien OS qua `python -c "import platform; print(platform.system())"`.
  2. Xac dinh version wheel moi nhat qua `gh release list --repo StormShynn/sap-abap-agent --limit 1`
     (KHONG hardcode version — neu khong co `gh`/mang, fallback doc dong dau `CHANGELOG.md`).
  3. Luon them extra `win-dpapi` NEU OS la Windows (khong co nhuoc diem, mac dinh nen dung) —
     KHONG hoi. KHONG tu them `playwright` (chi can cho 1 trong 4 kieu xac thuc, de cap sau
     neu user chon cookie-auth voi auto-relogin).
  4. Chay:
     ```bash
     pip install "https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v<VERSION>/mcp_sap_connect-<VERSION>-py3-none-any.whl[win-dpapi]"
     # (bo "[win-dpapi]" neu khong phai Windows)
     ```
  5. Chay lai `python -m mcp_sap_connect.doctor` de xac nhan.

  Che do "contribute" (git clone + editable install) **khong hoi mac dinh** — chi lam neu user
  tu noi ro muon sua code MCP server (xem README.md muc "Dev/contributor").

### Buoc 2: Kiem tra da co profile SAP chua (tu dong)

```bash
mcp-sap-connect profiles list
```

- **Da co profile** → bo qua toan bo Buoc 3, sang Buoc 4 luon.
- **Chua co** → sang Buoc 3.

### Buoc 3: Sinh file config mau + huong dan dien (day la buoc duy nhat can user)

1. Xac dinh thu muc `in/` cua user (local, KHONG nam trong git repo):
   ```bash
   python -c "from mcp_sap_connect.config.paths import get_in_dir; print(get_in_dir())"
   ```
2. Copy **ca 4 file mau** tu `reference/templates/mcp-sap-connect-profile-sample/` vao
   `<in_dir>/sap-setup/` (thu muc local cua user, an toan de dien secret that — KHONG bao gio
   bao user dien truc tiep vao file trong `reference/templates/` cua repo plugin, vi do la
   thu muc git-tracked, dien secret that vao do co the vo tinh bi commit).
3. Bao cho user, **dung 1 lan duy nhat can tuong tac**:
   > Đã copy 4 file mẫu vào `<in_dir>/sap-setup/`. Mở đúng 1 file khớp cách bạn xác thực
   > (`profile.oauth2.json` khuyến dùng nếu có Communication Arrangement; hoặc `.password`/
   > `.bearer`/`.cookie.json`), điền các field có `<...>`, lưu lại. Xem
   > `<in_dir>/sap-setup/README.md` nếu cần giải thích field/edition. Xong thì báo tôi (hoặc tự
   > chạy lệnh dưới) để tôi tạo profile.
4. Sau khi user xac nhan da dien xong, chay:
   ```bash
   mcp-sap-connect setup --from-file "<in_dir>/sap-setup/profile.<mode>.json"
   ```
   Lenh nay tu validate (tu choi neu con placeholder `<...>` chua dien) va tao profile — KHONG
   can tra loi them cau nao trong terminal.

**BAT BUOC**: KHONG bao gio tu dien gia tri vao cac field `<...>` thay user (URL, client_id,
secret, password, token, cookie) duoi bat ky hinh thuc nao, ke ca "doan gia tri hop ly de test".
Day la nguyen tac `sap-ask-before-guessing` — day la diem dung lai BAT BUOC duy nhat trong ca
lenh nay.

### Buoc 4: Dang ky MCP servers (tu dong, khong hoi)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_register.py"
```

Tuong duong `/mcp-setup` — tu dang ky server core/remote, hoi xac nhan rieng cho ADT alternative
(vi day la lua chon co that giua nhieu option, khong co mac dinh ro rang), huong dan cai thu cong
cho product-specific server.

### Buoc 5: Xac nhan tong the (tu dong)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_status.py"
```

Tom tat cho user server nao OK/thieu. **Nhac khoi dong lai Claude Code** de nhan server moi.

## Diem duy nhat BAT BUOC hoi/dung lai (tat ca con lai tu dong)

- Dien file config mau (Buoc 3) — khong ai thay the duoc user o day.
- Python `< 3.10` — can user tu nang cap, Claude khong tu cai Python duoc.
- Loi PATH khong tu fix duoc bang lenh doctor da goi y.
- ADT alternative server (Buoc 4) — co nhieu lua chon that su (SAP Official/ARC-1/mcp-abap-adt),
  khong co mac dinh "dung nhat cho moi nguoi".

## Luu y

- ⚠️ **Khong bao gio tu dien/doan credential** duoi bat ky hinh thuc nao. Nguyen tac
  `sap-ask-before-guessing` ap dung xuyen suot.
- ⚠️ **Khong bao gio bao user dien secret that truc tiep vao file trong `reference/templates/`
  cua repo** — luon copy ra `in/sap-setup/` (thu muc local, khong git-tracked) truoc.
- ⚠️ Xac dinh phien ban wheel that qua `gh release list` — KHONG hardcode version.
- 💡 Chay lai lenh nay bat ky luc nao cung an toan (idempotent).
- 💡 Muon tra loi wizard tuong tac tung buoc thay vi dien file (vd de xem giai thich ngay khi
  nhap)? Van dung duoc `mcp-sap-connect setup <url>` truc tiep — khong bi thay the, chi la lua
  chon khac.
- 🔗 Chi tiet template: `reference/templates/mcp-sap-connect-profile-sample/README.md` (5
  edition, 4 auth mode, vi du gia tri that). Chi tiet dang ky MCP: `commands/mcp-setup.md`.
