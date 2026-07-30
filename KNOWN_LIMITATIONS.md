# Known Limitations

> File nay track cac han che da biet nhung chua fix (khong phai bug - la
> scope quyet dinh co chu dich). Xem `docs/plans/active/sap-multi-system-router.md`
> cho context day du.

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
