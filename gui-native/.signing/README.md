# GUI signing keys (auto-updater)

Private keys are **never** committed. A keypair was generated for this channel;
public key is already embedded in `src-tauri/tauri.conf.json` → `plugins.updater.pubkey`.

## Add GitHub secrets (required before first signed release)

Private key file on the machine that generated it (do not commit):

`%TEMP%\sap-abap-agent-gui-keys\sap-abap-agent-gui.key`

```powershell
# From a shell that can reach GitHub (gh auth login)
$key = "$env:TEMP\sap-abap-agent-gui-keys\sap-abap-agent-gui.key"
gh secret set TAURI_SIGNING_PRIVATE_KEY --repo StormShynn/sap-abap-agent < $key
gh secret set TAURI_SIGNING_PRIVATE_KEY_PASSWORD --repo StormShynn/sap-abap-agent --body ""
```

If the key file is gone, regenerate and **replace** `plugins.updater.pubkey` in
`tauri.conf.json` (old installs will not accept updates signed with a new key):

```powershell
cd gui-native
npx tauri signer generate -w "$env:TEMP\sap-abap-agent-gui-keys\sap-abap-agent-gui.key" --ci -f
```

## Updater endpoint

Rolling tag **`gui-latest`** (recreated each `gui-v*` release):

`https://github.com/StormShynn/sap-abap-agent/releases/download/gui-latest/update.json`

**Canonical publish remote:** `https://github.com/StormShynn/sap-abap-agent.git`
(mirror/backup remotes must not receive `gui-v*` / release assets by mistake).

## Local sign (empty password)

Tauri treats missing password as interactive prompt (hangs in CI/non-TTY). Pass an
explicit empty string. On PowerShell, `$env:...=""` / `-p ""` often becomes “unset”;
use a shell cmdline instead:

```powershell
npx tauri signer sign "path\to\file.nsis.zip" -f $key --password ""
```
