---
description: Cai dat toan bo cho may moi lan dau dung plugin nay - tu cai CLI, tu cai GUI desktop, tu dang ky MCP, tu sinh file config mau; user chi can dien 1 file va chay 1 lenh, khong con phai tra loi wizard tung buoc
argument-hint: ""
---

# /sap-setup — Cai dat toan bo cho may moi, it thao tac tay nhat co the

Lenh nay tu dong lam **toan bo** phan cai dat (kiem tra Python, pip install, cai GUI desktop
native, dang ky MCP) — KHONG hoi user cau nao ve nhung thu Claude tu quyet dinh duoc (OS, extra
nao nen cai, dung wheel hay editable, ban GUI moi nhat). Phan **duy nhat khong the tu dong** la
nhap credential SAP that (khong ai doan duoc thay user) — phan nay cung duoc rut gon toi da: thay
vi tra loi wizard nhieu buoc trong terminal, user chi **dien 1 file JSON mau** roi chay **1 lenh**.

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
     KHONG hoi. **Luon them ca extra `playwright`** (khong doi user chon auth mode truoc nua —
     "cai het, khong bo sot" ap dung cho ca auth fallback: 1 trong 4 kieu xac thuc (cookie-auth
     voi auto-relogin) can no, cai san tranh phai quay lai Buoc 1 lan 2 khi user doi auth mode
     sau nay).
  4. Chay:
     ```bash
     pip install "https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v<VERSION>/mcp_sap_connect-<VERSION>-py3-none-any.whl[win-dpapi,playwright]"
     # (bo "win-dpapi," neu khong phai Windows, giu "[playwright]")
     ```
  5. Cai chromium binary cho Playwright (khong hoi — doctor coi day la optional/non-blocking
     nhung `/sap-setup` van chu dong cai de auth fallback hoat dong ngay lan dau, khong doi
     loi giua luc dang xac thuc voi user):
     ```bash
     python -m playwright install chromium
     ```
  6. Chay lai `python -m mcp_sap_connect.doctor` de xac nhan — dong `Playwright chromium: OK
     (<path>)` phai xuat hien.

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

Tuong duong `/register-mcp-servers` — tu dang ky server core/remote/dev-tool, hoi xac nhan rieng
cho ADT alternative (ten cu `/mcp-setup` van redirect). **Khac** slash `/mcp` cua Claude Code
(dang nhap OAuth Notion). Adt-alternative van hoi Y/n (vi day la lua chon co that giua nhieu
option, khong co mac dinh ro rang), huong dan cai thu cong cho product-specific server.

Script nay luon ghi `.mcp.json` (project scope) truoc, bat ke moi truong co lenh `claude` tren
PATH hay khong — day la fallback bat buoc phai co: khi Claude Code chay trong moi truong khong
expose `claude` CLI cho shell con (vd VSCode extension goi qua Bash tool), moi loi goi
`claude mcp add` deu tra ve SKIP **am tham**, ke ca cho server loi `sap-connect` — neu chi dua vao
`claude mcp add` ma khong co `.mcp.json` thi user mat luon server chinh ma khong biet vi sao. Neu
script in dong `WARN Khong tim thay claude CLI` thi bao user: server core/docs-remote van duoc
nhan qua `.mcp.json` sau khi khoi dong lai Claude Code, nhung `dev-tool` (chrome-devtools, khong
nam trong `.mcp.json` dung chung) va `adt-alternative` se can chay lai lenh nay tu mot terminal
thuc co `claude` tren PATH.

⚠️ **3 file config KHAC NHAU, khong file nao thay the file kia** — thieu 1 buoc la MCP "bien
mat" o dung tool do ma khong ro vi sao (day la trieu chung thuc te user gap: cai xong nhung mo
Claude Desktop/Claude CLI khong thay server, vi ho tuong 1 lenh la du cho ca 2 app):

| File | App doc file nay | Script tu ghi? |
| --- | --- | --- |
| `.mcp.json` (project root) | Claude Code, KHI mo dung project nay | Co, luon |
| `~/.claude.json` (`mcpServers`) | Claude Code CLI, moi noi (user scope) | Co, nhung **CHI `chrome-devtools`** — core/docs-remote da co qua `.mcp.json` roi, ghi lai o day se bi `mcp_status.py` bao "!! may conflict" (da kiem chung thuc te 2026-08-03: ghi ca 2 noi lam status bao trung) |
| `claude_desktop_config.json` (`%APPDATA%\Claude\` Windows / `~/Library/Application Support/Claude/` macOS) | **Claude Desktop — app HOAN TOAN KHAC Claude Code**, khong doc `.mcp.json` hay `~/.claude.json` | Co, **ca core+docs-remote+dev-tool** (day la NOI DUY NHAT Desktop co the thay bat ky server nao) — CHI khi thu muc `Claude/` da ton tai san (tuc user da cai Claude Desktop it nhat 1 lan); neu chua cai thi bo qua, KHONG tu tao thu muc cho app chua cai |

Ca 2 file JSON o tren deu duoc **backup truoc khi ghi** (`<file>.bak-<timestamp>`, cung thu muc)
vi day la file quan trong/co the rat lon (chua ca lich su session) — merge chi them/cap nhat key
`mcpServers`, khong dong den bat ky du lieu khac trong file (da kiem chung thuc te bang cach so
sanh JSON truoc/sau: 100% du lieu khac giu nguyen).

**`chrome-devtools` (dev-tool) tu 2026-08 KHONG con hoi Y/n nua** — theo quyet dinh cua nguoi dung
san pham ("cai het, khong bo sot"), no nam trong nhom auto giong core/docs-remote. Truoc khi
chay script, kiem tra Chrome da cai chua (dev-tool nay dieu khien Chrome that qua CDP, khong tu
mo Chromium rieng):

```powershell
(Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe")
```

- Co Chrome → bo qua, chay `mcp_register.py` binh thuong.
- Chua co → tu tai va cai silent, khong hoi (browser thong thuong, khong phai nang luc dieu
  khien can consent nhu chinh MCP server nen khong can hoi Y/n):

  ```powershell
  Invoke-WebRequest 'https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise64.msi' -OutFile "$env:TEMP\chrome_enterprise.msi"
  Start-Process msiexec.exe -ArgumentList '/i', "$env:TEMP\chrome_enterprise.msi", '/qn' -Wait
  ```

  ⚠️ [Unverified] URL + co silent tren la suy luan tu quy uoc Google Chrome Enterprise MSI da
  biet noi chung — **chua duoc chay thu tren may nao trong phien lam viec nay** (Chrome da co
  san tren may test nen khong co dip xac minh). Claude PHAI xac nhan lai bang `Test-Path` sau
  khi cai — khong thay file → dung lai, huong dan user tu tai Chrome tu trang chinh thuc
  `google.com/chrome` va cai bang tay, KHONG doan them URL/lenh khac de "thu cho ra".

### Buoc 5: Cai dat GUI desktop native (tu dong, Windows only, khong hoi)

Chi ap dung tren Windows (quyet dinh `0001-gui-path-only-no-sidecar`: GUI la **PATH-only**,
khong embed Python, luon can Buoc 1 xong truoc). OS khac Windows → bo qua buoc nay, noi cho user
ban Tkinter legacy (`pip install mcp-sap-connect[gui]` → lenh `mcp-sap-connect-gui`).

1. **Kiem tra da cai chua** (idempotent — da co ban moi nhat thi bo qua):

   ```powershell
   Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall' `
     -ErrorAction SilentlyContinue | Get-ItemProperty |
     Where-Object { $_.DisplayName -eq 'SAP ABAP Agent' } |
     Select-Object DisplayVersion, InstallLocation
   ```

   Neu da co: so sanh `DisplayVersion` voi tag asset moi nhat cua `gui-latest` (Buoc 5.3) — bang
   nhau thi bo qua cai dat, sang Buoc 6. Cu hon thi chay lai installer de update (khong can go
   cai truoc).

   ⚠️ Truoc MOI lenh `Invoke-WebRequest`/`curl` trong ca Buoc 5 nay: neu shell dang chay la
   **Windows PowerShell 5.1** (khong phai PowerShell 7 `pwsh`), TLS 1.2 co the KHONG duoc bat
   san → tai file se fail voi loi "underlying connection was closed"/"trust relationship".
   Chay dong nay truoc cho an toan (vo hai tren PS7, chi la no-op):

   ```powershell
   [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
   ```

2. **Kiem tra WebView2 runtime** (Tauri can, Windows 11 co san, Windows 10 co the thieu):

   ```powershell
   (Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
   ```

   Co gia tri → OK. Rong/khong co key → tu tai va cai Evergreen Bootstrapper, khong hoi:

   ```powershell
   Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile "$env:TEMP\MicrosoftEdgeWebview2Setup.exe"
   Start-Process "$env:TEMP\MicrosoftEdgeWebview2Setup.exe" -ArgumentList '/silent','/install' -Wait
   ```

3. **Tai installer NSIS moi nhat** (KHONG hardcode version, dung tag rolling `gui-latest`):

   ```powershell
   gh release download gui-latest --repo StormShynn/sap-abap-agent --pattern "*-setup.exe" --dir "$env:TEMP" --clobber
   ```

   Neu **khong co `gh`** tren may (rat co the tren may user cuoi, khac may dev) — `gh release
   download` se bao "command not found", KHONG dung lai o day, tu fallback qua GitHub REST API
   thuan (khong can auth cho public repo, da kiem chung thuc te 2026-08-03):

   ```powershell
   $rel = Invoke-RestMethod 'https://api.github.com/repos/StormShynn/sap-abap-agent/releases/tags/gui-latest'
   $asset = $rel.assets | Where-Object { $_.name -like '*-setup.exe' } | Select-Object -First 1
   Invoke-WebRequest $asset.browser_download_url -OutFile (Join-Path $env:TEMP $asset.name)
   ```

4. **Cai silent, khong hoi** — `installMode` cua NSIS la `currentUser` (`tauri.conf.json`) nen
   KHONG can elevate/UAC:

   ```powershell
   $installer = Get-ChildItem "$env:TEMP\*-setup.exe" | Select-Object -First 1
   Start-Process $installer.FullName -ArgumentList '/S' -Wait
   ```

   `/S` da duoc kiem chung thuc te (2026-08-03, reinstall cung version 1.23.1): exit code 0,
   khong hien UI, registry van dung sau khi cai. Chua kiem chung rieng truong hop cai lan dau
   tren may hoan toan chua co ban nao / thieu WebView2 — **Claude van PHAI xac nhan lai bang
   Buoc 5.5** cho tung may cu the, khong duoc bao "cai xong" chi vi lenh chay khong throw loi.

5. **Xac nhan da cai thanh cong**: chay lai lenh o Buoc 5.1. Van khong thay `SAP ABAP Agent`
   trong registry → dung lai, KHONG tu doan lenh khac de "thu cho ra" — mo thang file `.exe` vua
   tai trong `$env:TEMP` va bao user tu chay wizard cai bang tay (day la 1 trong cac diem dung
   lai bat buoc, xem muc duoi).

6. **Smoke-test** (tu dong, khong hoi) — CHI kiem tra app khong crash ngay khi mo, KHONG phai
   kiem tra UI/luong nghiep vu thuc (Claude khong "nhin thay" cua so app):

   ```powershell
   $installLoc = (Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
     Where-Object { $_.DisplayName -eq 'SAP ABAP Agent' }).InstallLocation
   $exe = Get-ChildItem $installLoc -Filter '*.exe' | Where-Object { $_.Name -ne 'uninstall.exe' } | Select-Object -First 1
   $p = Start-Process $exe.FullName -PassThru
   Start-Sleep -Seconds 4
   if (Get-Process -Id $p.Id -ErrorAction SilentlyContinue) {
     Write-Output "OK - khong crash ngay khi mo"
     Stop-Process -Id $p.Id -Force   # chi la smoke test, dong lai sau khi xac nhan
   } else {
     Write-Output "LOI - process tu tat ngay, bao user (co the thieu WebView2/CLI, xem banner runtime check trong app khi user tu mo lai)"
   }
   ```

   Ten file thuc thi hien tai la `gui-native.exe` (ten package Cargo, **khac** `SAP ABAP Agent.exe`)
   — vi ten nay co the doi giua cac ban release, doc dong tu `InstallLocation` roi liet ke `.exe`
   trong do thay vi hardcode ten file.

7. Bao cho user: GUI da cai/cap nhat, **khuyen nghi tu mo app 1 lan** de kiem tra banner runtime
   check (thieu CLI se hien banner vang) va them profile qua UI neu muon dung GUI thay CLI.

### Buoc 6: Xac nhan tong the (tu dong)

```bash
python "${CLAUDE_PLUGIN_ROOT}/reference/scripts/mcp_status.py"
```

Tom tat cho user server nao OK/thieu. **Nhac khoi dong lai Claude Code** de nhan server moi.

## Diem duy nhat BAT BUOC hoi/dung lai (tat ca con lai tu dong)

- Dien file config mau (Buoc 3) — khong ai thay the duoc user o day.
- Python `< 3.10` — can user tu nang cap, Claude khong tu cai Python duoc.
- Loi PATH khong tu fix duoc bang lenh doctor da goi y.
- ADT alternative server (Buoc 4) — co nhieu lua chon that su (SAP Official/ARC-1/mcp-abap-adt),
  khong co mac dinh "dung nhat cho moi nguoi". Trong shell non-interactive (vd Claude Code goi
  qua Bash tool), cau hoi nay tu dong tra loi "n" (bo qua) thay vi crash — Claude phai NOI RO
  cho user la ADT alternative van chua duoc chon, khong duoc coi la "da xong".
- GUI installer sau Buoc 5.4 van khong xuat hien trong registry (Buoc 5.5 that bai) — nghia la co
  silent-install flag khong hoat dong nhu ky vong (chua duoc kiem chung tren moi ban NSIS) — dung
  lai, dua user tu chay installer bang tay, KHONG tu doan lenh khac de thay the.

## Luu y

- ⚠️ **Khong bao gio tu dien/doan credential** duoi bat ky hinh thuc nao. Nguyen tac
  `sap-ask-before-guessing` ap dung xuyen suot.
- ⚠️ **Khong bao gio bao user dien secret that truc tiep vao file trong `reference/templates/`
  cua repo** — luon copy ra `in/sap-setup/` (thu muc local, khong git-tracked) truoc.
- ⚠️ Xac dinh phien ban wheel that qua `gh release list` — KHONG hardcode version.
- ⚠️ Xac dinh installer GUI that qua tag rolling `gui-latest` (`gh release download`) — KHONG
  hardcode version, KHONG doan URL.
- 💡 Chay lai lenh nay bat ky luc nao cung an toan (idempotent) — ke ca Buoc 4/5, da kiem tra
  thuc te: `mcp_register.py` luon ghi lai `.mcp.json` moi lan chay (khong crash tren shell
  non-interactive), Buoc 5.1 tu bo qua neu GUI da la ban moi nhat.
- 💡 Muon tra loi wizard tuong tac tung buoc thay vi dien file (vd de xem giai thich ngay khi
  nhap)? Van dung duoc `mcp-sap-connect setup <url>` truc tiep — khong bi thay the, chi la lua
  chon khac.
- 🔗 Chi tiet template: `reference/templates/mcp-sap-connect-profile-sample/README.md` (5
  edition, 4 auth mode, vi du gia tri that). Chi tiet dang ky MCP: `commands/register-mcp-servers.md`
  (alias cu `commands/mcp-setup.md`).
