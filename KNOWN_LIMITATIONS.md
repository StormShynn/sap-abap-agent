# Known Limitations

> File nay track cac han che da biet nhung chua fix (khong phai bug - la
> scope quyet dinh co chu dich). Xem `docs/plans/active/sap-multi-system-router.md`
> cho context day du.

## SAML fast-path (cookie auth) - saml_form_login / saml_or_browser_login

Port tu vibing-steampunk `pkg/adt/saml_auth.go` (`reference/mcp-server/mcp_sap_connect/sap/auth.py`).

- **Khong ho tro MFA**: `saml_form_login()` tu POST form login IAS bang username/password
  thuan qua HTTP - neu IAS doi hoi them buoc thu 2 (OTP, push notification, FIDO...), form
  sau cung se khong con dung dang mong doi (khong co field `j_username`) va ham se raise
  `SamlLoginError` voi thong bao chung chung ("kiem tra lai username/password, hoac IAS co
  the yeu cau MFA") - **khong tu phat hien/phan biet duoc chinh xac ly do that bai** (giong
  han che cua ban Go goc). Caller (`saml_or_browser_login`, `_setup_from_file`, wizard) deu
  tu fallback ve `web_login_auto` (browser, ho tro ca MFA) khi gap loi nay, nen khong bi ket -
  chi cham hon (phai mo browser) thay vi nhanh (~1-3s qua HTTP).
- **Phu thuoc cau truc HTML trang login IAS**: `_extract_form`/`_FirstFormParser` parse
  `<form>` dau tien tim thay + field ten `j_username`/`j_password`. Neu SAP thay doi cau truc
  trang login IAS (hiem nhung co the), fast-path se that bai gracefully (fallback browser) chu
  khong crash - nhung se khong con "nhanh" nua cho toi khi co ai cap nhat lai parser.
- **Password luu local, mã hoa nhung van la 1 diem luu tru them**: neu dang nhap fast-path
  thanh cong, `samlUsername`/`samlPassword` duoc luu (ma hoa DPAPI/AES tuy OS, cung co che
  voi `authMode=password`) trong `profiles/<id>/secrets.json` de tai su dung cho reauth sau.
  Day la tradeoff co chu dich (doi lay tu dong hoa reauth), khong phai bug - muon ngung luu,
  xoa profile roi tao lai voi 2 field bootstrap de trong.

## vsp (vibing-steampunk) - sap-vsp MCP server

- **Single-profile**: `vsp` chi nhan 1 bo credential luc khoi dong (qua env
  `SAP_ADT_URL`/`SAP_ADT_USER`/`SAP_ADT_PASSWORD`). Neu user doi profile active
  (`mcp-sap-connect profiles use <other>`), `sap-vsp` KHONG tu dong nhan
  credential moi - phai chay lai `mcp-sap-connect mcp-setup` de dang ky lai voi
  credential cua profile moi.
- **Chi ho tro password auth**: `SAP_ADT_USER`/`SAP_ADT_PASSWORD` chi dien tu
  dong duoc khi profile active dung `authMode: password` (mac dinh cho
  `onprem`/`rise_with_sap`). Profile dung `cookie` (SSO qua Playwright),
  `oauth2`, hoac `bearer` khong co plain password luu tru de chuyen cho 1
  process rieng (`vsp` la Go binary doc lap, khong dung chung session/cookie
  jar voi `sap-connect`) - user can tu cung cap user/password rieng cho ADT
  neu muon dung `sap-vsp` tren cac profile nay.
- **Debug adapter chua tich hop sau**: cac tinh nang Lua scripting, checkpoint,
  force-replay cua `vsp` debug adapter chua duoc wire vao routing/skill nao -
  out of scope cho v1 cua plan `sap-multi-system-router`. Co the dung truc
  tiep qua tool `vsp_*` neu can, nhung khong co huong dan/routing tu dong.
- **Khong co tren PATH / auto-download that bai**: neu mang khong on dinh luc
  `mcp-setup` tai `vsp` tu GitHub Release, dang ky se bi skip (co warning ro).
  Cai thu cong binary tu
  `https://github.com/oisee/vibing-steampunk/releases/tag/v<version>` roi set
  env `MCP_SAP_CONNECT_VSP_BIN=<duong-dan-binary>` truoc khi chay lai
  `mcp-sap-connect mcp-setup` (bo qua auto-download, dung binary da pin).
