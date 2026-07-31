---
description: Cai dat toan bo cho may moi lan dau dung plugin nay (pip install, profile SAP dau tien, dang ky MCP servers) - thay the chay tung lenh commandline thu cong theo README
argument-hint: ""
---

# /sap-setup — Cai dat toan bo cho may moi

Lenh nay noi lai toan bo cac buoc trong README.md muc "Cai dat (1 lan)" + "Them project SAP
moi" + "Dang ky MCP servers" thanh 1 luong lien tuc, **tu phat hien buoc nao da xong** (khong
lam lai tu dau neu may da cai 1 phan roi). Khong tu doan URL he thong SAP hay tu nhap ho
credential — nhung buoc do van can user tuong tac truc tiep voi wizard that.

**Khong chi go tay**: hook `hooks/first_run_check.py` (SessionStart) tu kiem tra offline moi
phien — neu chua thay profile SAP nao (hoac `mcp-sap-connect` chua cai), Claude se **chu dong
hoi** user co muon chay `/sap-setup` khong, thay vi cho user tu biet go lenh nay. Neu da co it
nhat 1 profile, hook im lang, khong hoi lai moi phien.

## Cach dung

```text
/sap-setup
```

Khong can tham so. Chay 1 lan tren may moi; chay lai cung an toan (idempotent — buoc nao da
xong se tu bo qua).

## Quy trinh (dung lai hoi user o moi diem "BAT BUOC hoi", khong tu doan)

### Buoc 1: Kiem tra Python

```bash
python --version
```

Yeu cau `>= 3.10`. Neu khong dat → dung lai, bao user cai/nang cap Python truoc, chua lam gi
them.

### Buoc 2: Kiem tra `mcp-sap-connect` da cai chua

```bash
python -m mcp_sap_connect.doctor
```

- Chay duoc va bao OK → da cai roi, **bo qua Buoc 3**, sang Buoc 4.
- Bao "module not found"/`ModuleNotFoundError` → chua cai, sang Buoc 3.
- Bao loi PATH (thuong gap tren Windows: pip cai vao user-scheme site-packages, VD
  `%APPDATA%\Python\PythonXY\Scripts` khong tu dong co trong PATH) → doctor tu in san lenh
  PowerShell de fix — **BAT BUOC hoi user** da chay lenh fix do va mo lai terminal chua truoc
  khi tiep tuc.

### Buoc 3: Cai dat (chi khi Buoc 2 bao chua cai)

**BAT BUOC hoi user 2 cau truoc khi chay lenh cai dat**:

1. "Ban cai de **dung** (khuyen nghi, tai wheel release) hay de **contribute/sua code** MCP
   server (git clone + editable install)?"
2. "Ban co dang dung **Windows** khong (de hoi extra `win-dpapi`), va co muon dung **cookie
   auth kieu tu dong mo browser dang nhap** khong (extra `playwright`, can them buoc tai
   browser binary)?"

Xac dinh phien ban wheel moi nhat truoc khi build URL (KHONG dung mot con so version co dinh
da hardcode san — de tranh cai nham ban cu):

```bash
gh release list --repo StormShynn/sap-abap-agent --limit 1
```

Neu khong co `gh` CLI hoac khong co mang, doc dong dau `CHANGELOG.md` (`## [vX.Y.Z]`) trong
repo plugin lam fallback tham khao, nhung uu tien GitHub release That vi day la nguon build
that cua wheel.

**Neu chon "dung"**:

```bash
# Thay <VERSION> bang phien ban vua xac dinh o tren
pip install "https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v<VERSION>/mcp_sap_connect-<VERSION>-py3-none-any.whl[<extras neu co>]"
```

`<extras neu co>` la `win-dpapi`, `playwright`, hoac ca hai cach nhau bang dau phay, theo cau
tra loi Buoc 3.1/3.2 (bo trong neu khong extra nao).

**Neu chon "contribute"**:

```bash
git clone https://github.com/StormShynn/sap-abap-agent.git
cd sap-abap-agent/reference/mcp-server
pip install -e ".[<extras neu co>]"
```

**Neu co chon extra `playwright`**, chay them:

```bash
playwright install chromium
```

Sau khi cai xong, chay lai `python -m mcp_sap_connect.doctor` de xac nhan PATH/dependency OK
truoc khi sang Buoc 4.

### Buoc 4: Kiem tra da co profile SAP nao chua

```bash
mcp-sap-connect profiles list
```

- **Da co profile** → hoi user co muon dung profile hien co (bo qua phan setup profile, sang
  Buoc 5) hay them 1 profile moi (tiep tuc duoi day).
- **Chua co profile nao** → **BAT BUOC hoi user URL he thong SAP** (KHONG tu doan/tu bia URL),
  roi chay:

```bash
mcp-sap-connect setup <URL_user_vua_cung_cap>
```

Day la wizard **tuong tac that** (hoi phuong thuc xac thuc, region, service type,
client_secret/password/token/cookie tuy phuong thuc) — Claude **KHONG duoc tu nhap thay user**
bat ky truong secret/credential nao qua bat ky hinh thuc nao, ke ca doan hop ly. De nguyen wizard
hoi truc tiep nguoi dung qua terminal.

### Buoc 5: Dang ky MCP servers voi Claude Code

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_register.py"
```

Tuong duong goi `/mcp-setup` (xem file do de biet chi tiet 13 server duoc xu ly ra sao — core +
remote tu dong dang ky, ADT alternative hoi xac nhan, product-specific huong dan cai thu cong).

### Buoc 6: Xac nhan tong the

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_status.py"
```

Tom tat cho user: server nao da dang ky OK, server nao con thieu (can cai thu cong theo huong
dan rieng). **Nhac user khoi dong lai Claude Code** de nhan server moi dang ky.

## Danh sach BAT BUOC hoi user (khong tu doan duoi moi hinh thuc)

- Cai de dung hay de contribute (anh huong co git clone hay khong).
- Co extra nao (win-dpapi/playwright) — chi hoi, khong tu bat vi "co ve huu ich".
- URL he thong SAP (neu chua co profile nao) — tuyet doi khong tu bia/doan.
- Phuong thuc xac thuc + secret/token/cookie — de nguyen cho wizard `mcp-sap-connect setup`
  hoi truc tiep, Claude khong nhap thay.
- Da fix PATH chua (neu Buoc 2 bao loi PATH) — xac nhan truoc khi chay tiep, tranh cac lenh sau
  fail vi `mcp-sap-connect` van khong tim thay.

## Luu y

- ⚠️ **Khong bao gio tu dien/doan credential** (client_secret, password, token, cookie) duoi
  bat ky hinh thuc nao — ke ca "gia dinh gia tri mac dinh de test". Day la nguyen tac
  `sap-ask-before-guessing` ap dung xuyen suot toan bo lenh nay.
- ⚠️ Xac dinh phien ban wheel **that** qua `gh release list`/GitHub truoc khi build URL — KHONG
  dung mot con so version hardcode co san trong bat ky tai lieu nao (de tranh cai nham ban cu
  neu README/doc khac chua kip cap nhat theo release moi nhat).
- 💡 Chay lai lenh nay bat ky luc nao cung an toan — moi buoc tu kiem tra truoc khi lam, khong
  lam lai neu da xong.
- 💡 Sau khi setup xong, dung `/sync-skills` dinh ky de cap nhat skill/agent/command moi nhat
  ma khong can chay lai toan bo `/sap-setup`.
- 🔗 Xem `README.md` muc "Cai dat (1 lan)", "Them project SAP moi", "Dang ky MCP servers voi
  Claude Code" cho chi tiet tung buoc neu muon tu lam tay thay vi qua lenh nay.
