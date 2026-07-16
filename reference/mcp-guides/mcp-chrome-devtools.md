# mcp-chrome-devtools — Chrome DevTools MCP Server

**Dung o dau**: doc file nay khi user can debug 1 trang web that dang chay (dac biet Fiori/UI5
app tren browser) va can hon `WebFetch`/`WebSearch` (chi doc HTML tinh, khong chay duoc JS/SPA).
Duoc tro toi tu `README.md` muc "MCP server moi: Chrome DevTools".

## Tong quan

`chrome-devtools-mcp` la MCP server **chinh chu** cua Google / ChromeDevTools team, dung
Puppeteer de dieu khien 1 Chrome that. Cho AI assistant kha nang: doc console log, network
request, ghi performance trace, chup screenshot, thao tac DOM (click/fill/type) tren 1 trang web
that dang chay - khac voi WebFetch (chi convert HTML tinh sang markdown, khong chay JS).

**Repository**: `https://github.com/ChromeDevTools/chrome-devtools-mcp`
**npm package**: `chrome-devtools-mcp`

**Khong phai tool SAP-specific** - nhung huu ich trong plugin nay de debug **Fiori/UI5 app chay
tren browser** (console error runtime, network call OData bi loi, performance load cham) - viec
ma khong MCP server SAP nao trong plugin nay lam duoc (`sap-btp`, ADT alternatives... deu la
source-level ABAP/OData, khong "nhin" duoc vao trang da render that tren browser).

**Yeu cau**: Node.js (LTS) + Google Chrome (ban stable) da cai san tren may. Chi ho tro chinh
thuc Chrome / Chrome for Testing (khong ho tro Firefox/Edge/Safari).

## Cai dat

### Dang ky MCP (Claude Code)

```bash
claude mcp add --transport stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

### Cach 2: qua script chung cua plugin (hoi Y/n, tu dong chay lenh o tren)

```bash
python reference/scripts/mcp_register.py
```

Script se hoi `Register chrome-devtools (...)? [Y/n]` - dong y thi tu dong chay lenh
`claude mcp add` o tren cho ban. Server nay nam trong category `dev-tool` trong
`reference/scripts/mcp_inventory.json` - cung nhom "prompt" voi cac ADT alternative (hoi truoc
khi chay, khong tu dong bundle), du khong can credential rieng nhu ADT. Ly do: day la nang luc
dieu khien 1 Chrome that (mo URL, chay JS tuy y), khac voi cac MCP server tra cuu docs read-only
dang duoc bundle san (`sap-btp`, `cds-kb`, `notion`...), nen van can 1 buoc xac nhan thay vi tu
dong bat cho moi nguoi cai plugin.

### Cau hinh .mcp.json (thay the neu dung file thay vi CLI)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### CLI flags dang chu y

| Flag | Mo ta |
|------|-------|
| `--isolated` | Dung user-data-dir tam, tu xoa sau khi dong - KHUYEN DUNG de khong dung toi cookie/session cua Chrome that dang dung hang ngay |
| `--headless` | Chay khong hien cua so browser |
| `--channel` | Chon kenh Chrome: `stable` / `beta` / `dev` / `canary` |
| `--executablePath` | Duong dan toi 1 Chrome binary tuy chinh |
| `--browser-url` | Ket noi vao 1 Chrome dang chay san (VD: `http://127.0.0.1:9222`) thay vi tu mo Chrome moi |
| `--slim` | Chi expose 1 tap tool toi thieu (giam so luong tool load vao context) |

Vi du dang ky kem flag (khuyen dung cho may ca nhan):

```bash
claude mcp add --transport stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest --isolated --headless
```

## Tools (theo nhom - nguon: README chinh thuc cua repo)

### Navigation & Input Automation

| Tool | Mo ta |
|------|-------|
| `navigate_page` / `new_page` / `close_page` / `list_pages` / `select_page` | Mo/dong/chuyen tab |
| `click` / `click_at` / `fill` / `fill_form` / `type_text` / `hover` / `drag` | Thao tac tren trang |
| `press_key` | Nhan phim |
| `upload_file` | Upload file qua input[type=file] |
| `handle_dialog` | Xu ly dialog (confirm/alert/prompt) |
| `wait_for` | Cho 1 dieu kien/text xuat hien tren trang |

### Debugging

| Tool | Mo ta |
|------|-------|
| `take_snapshot` | Chup DOM snapshot (doc cau truc trang - nen goi truoc khi click/fill) |
| `take_screenshot` | Chup anh man hinh trang hien tai |
| `list_console_messages` / `get_console_message` | Doc console log/error cua trang (debug UI5 runtime error) |
| `evaluate_script` | Chay 1 doan JS trong context trang |
| `lighthouse_audit` | Chay Lighthouse audit |
| `screencast_start` / `screencast_stop` | Ghi video man hinh |

### Network & Performance

| Tool | Mo ta |
|------|-------|
| `list_network_requests` / `get_network_request` | Liet ke/xem chi tiet 1 network request (debug OData call bi loi 400/500) |
| `performance_start_trace` / `performance_stop_trace` | Ghi performance trace (debug app load cham) |
| `performance_analyze_insight` | Phan tich 1 insight tu trace da ghi |
| `emulate` / `resize_page` | Gia lap device/network condition, doi kich thuoc trang |

### Memory & Extensions (nang cao, it dung cho Fiori/UI5)

Repo con co tool doc heap snapshot (`take_heapsnapshot`, `compare_heapsnapshots`...) va quan ly
Chrome extension (`install_extension`, `list_extensions`...) - xem README chinh thuc cua repo
neu can dung toi nhom nay.

## Bao mat & Luu y

| Van de | Khuyen nghi |
|--------|-------------|
| Dieu khien Chrome THAT | Dung `--isolated` de khong dung toi cookie/session/lich su cua Chrome that dang dung hang ngay |
| `evaluate_script` chay JS tuy y | Chi dung tren trang/URL ban tin tuong (VD Fiori Launchpad noi bo), khong dung tren trang la |
| Khong phai tool SAP | Khong thay the `sap-btp`/ADT alternatives - chi ho tro debug **lop giao dien** (Fiori/UI5), khong doc/sua code ABAP |
| Opt-in, khong bundle mac dinh | Giong `sap-gui` - can Node.js + Chrome cai san may, nen KHONG nam trong `.mcp.json` bundled cua plugin; tu `claude mcp add` khi can dung |

## Vi du su dung trong Claude

```text
"Mo Fiori Launchpad va xem co console error khong"
  -> navigate_page(url) + list_console_messages

"Kiem tra request OData nao bi loi khi mo app Manage Sales Orders"
  -> navigate_page + list_network_requests (loc status >= 400) + get_network_request

"App nay load cham, ghi thu performance trace"
  -> performance_start_trace + (thao tac trong app) + performance_stop_trace + performance_analyze_insight

"Chup man hinh trang hien tai"
  -> take_screenshot
```

## Nguon tham khao

- Repository: `https://github.com/ChromeDevTools/chrome-devtools-mcp`
- npm: `https://www.npmjs.com/package/chrome-devtools-mcp`
