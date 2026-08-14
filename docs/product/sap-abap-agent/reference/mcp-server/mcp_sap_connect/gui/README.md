# mcp-sap-connect GUI

GUI desktop + system tray cho `mcp-sap-connect`, giup thao tac khong can nho lenh.

## Cai dat

```
pip install mcp-sap-connect[gui]
```

Lenh nay cai them `pystray` + `Pillow` (icon tray). Sau khi cai xong, co them command `mcp-sap-connect-gui`.

Neu muon dung auto-login (`reauthMode=auto`) thi cai them:
```
pip install mcp-sap-connect[gui,playwright]
python -m playwright install chromium
```

## Su dung

```
mcp-sap-connect-gui                  # Mo GUI + tray (mac dinh)
mcp-sap-connect-gui --no-tray         # Chi GUI, khong co tray icon
mcp-sap-connect-gui --tray-only       # Chi tray (an hoan toan, khong cua so)
```

## Giao dien

```
+---------------------------------------------------------------+
| Profile: [project1.s4hana.cloud.sap      v] [Refresh] [+ New] |
| URL:     https://project1.s4hana.cloud.sap                     |
+---------------------------------------------------------------+
| [   Reauth   ] [   Connect   ] [   Set Active   ] [   Remove ] |
+---------------------------------------------------------------+
| Log:                                                            |
| +-----------------------------------------------------------+ |
| |  ... output tu mcp-sap-connect ...                         | |
| +-----------------------------------------------------------+ |
| [Clear] [Copy]                          [Status: Ready]      |
+---------------------------------------------------------------+
```

### Cac nut chinh

| Nut | Tuong duong CLI | Mo ta |
|---|---|---|
| Reauth | `mcp-sap-connect reauth <profile>` | Mo browser + paste cookie moi |
| Connect | `mcp-sap-connect connect <profile>` | Test ket noi ADT (read + write) |
| Set Active | `mcp-sap-connect profiles use <id>` | Chuyen profile active |
| Remove | `mcp-sap-connect profiles remove <id>` | Xoa profile (kem confirm) |
| + New | `mcp-sap-connect setup <URL>` (cua so CMD rieng) | Wizard setup (vi can nhap nhieu) |

## System tray

Sau khi mo GUI, duoi thanh taskbar Windows se co 1 icon hinh tron xanh chu **S**.

### Menu chuot phai

```
* Reauth (active)
  Connect (active)
  Profiles
    project1.s4hana.cloud.sap    (set active)
    old-dev.s4hana.cloud.sap
    ...
  ---
  Open GUI
  Quit
```

- **Reauth (active)**: chay `reauth` cho profile hien dang active, khong can mo GUI.
- **Profiles**: chon nhanh profile active tu menu (khong can mo GUI).
- **Open GUI**: hien lai cua so (neu dang an).
- **Quit**: thoat hang app (dong tray).

### Click trai / double-click

Mo lai cua so GUI neu dang an.

### Balloon notification

Moi lan `reauth`/`connect` xong (qua tray hoac GUI), Windows se hien toast o goc phai:
- "reauth OK" (xanh)
- "reauth that bai (rc=1)" (do)

## Hanh vi dac biet

### An xuong tray khi dong cua so

Bam **X** tren cua so GUI -> app khong thoat, chi an xuong tray. De thoat hang, dung **Quit** trong menu tray, hoac tat tu Task Manager.

Neu dang co 1 subprocess chay (`reauth`/`connect`) thi se hoi confirm truoc khi thoat.

### Log console

Moi output tu `mcp-sap-connect` duoc stream real-time vao o log phia duoi GUI. Khi gap loi, copy log nay paste vao GitHub issue de debug.

## So sanh GUI vs CLI

| Tac vu | CLI | GUI |
|---|---|---|
| Setup wizard | `mcp-sap-connect setup <url>` (terminal) | Nut **+ New** (mo CMD moi) |
| Reauth | `mcp-sap-connect reauth` | Nut **Reauth** hoac menu tray |
| Connect | `mcp-sap-connect connect` | Nut **Connect** |
| Profiles list | `mcp-sap-connect profiles list` | Combo box + menu tray |
| Switch active | `mcp-sap-connect profiles use <id>` | Nut **Set Active** hoac menu tray |
| Remove | `mcp-sap-connect profiles remove <id>` | Nut **Remove** (co confirm) |
| Doctor | `mcp-sap-connect doctor` | (chua co - chay CLI neu can) |

## Troubleshooting

### Tray icon khong hien
- Kiem tra `pystray` + `Pillow` da cai: `pip show pystray Pillow`.
- Windows 10/11: mo **Settings -> Personalization -> Taskbar -> Notification area** -> bat "Always show all icons".
- Chay lai voi `--no-tray` de xac nhan GUI van hoat dong.

### Loi "tkinter not found"
- Windows: tkinter co san trong Python installer chinh thuc.
- Linux: `sudo apt install python3-tk`.
- macOS: cai Python tu python.org (khong dung Homebrew).

### Click "Reauth" ma khong co gi xay ra
- Kiem tra o log - output tu CLI se hien o do.
- Neu profile chua set `authMode=cookie` thi `reauth` se in loi "khong phai cookie" - chay lai `setup` de chon dung auth mode.

### Muon setup profile moi ngay trong GUI
- Setup wizard can nhap URL, OAuth credentials, paste cookie -> qua nhieu de nhoi vao GUI.
- Hien tai bam **+ New** mo CMD moi - chay `setup` o do xong quay lai GUI bam **Refresh**.
