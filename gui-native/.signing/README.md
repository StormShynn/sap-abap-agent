# GUI signing (updater minisign + optional Authenticode)

Private keys and code-signing certificates are **never** committed. Do not add
`.pfx`, `.p12`, `.key`, or raw private-key files to the repo.

## Two different trust systems

| Mechanism | Purpose | Secrets / config | Required to ship? |
|-----------|---------|------------------|-------------------|
| **Minisign (Tauri updater)** | In-app update trust — clients verify `update.json` + `.sig` against `plugins.updater.pubkey` | `TAURI_SIGNING_PRIVATE_KEY` (+ empty password) | **Yes** for `gui-release.yml` |
| **Authenticode (Windows / SmartScreen)** | OS / browser trust — reduces SmartScreen “unknown publisher” for downloaded NSIS/MSI | `WINDOWS_CERTIFICATE` + `WINDOWS_CERTIFICATE_PASSWORD` | **No** — fail-soft: unsigned installers still publish when these secrets are absent |

Minisign does **not** satisfy SmartScreen. Authenticode does **not** replace the
updater pubkey. Both can be enabled together.

## Canonical git remote

Clone and push GUI releases against the canonical repo only:

```text
https://github.com/StormShynn/sap-abap-agent.git
```

```powershell
git remote set-url origin https://github.com/StormShynn/sap-abap-agent.git
git remote -v
```

Mirror/backup remotes (for example a `-backup` redirect) must not receive
`gui-v*` tags or release assets by mistake. Never change global git config for this.

## Minisign — add GitHub secrets (required before first signed release)

Private key file on the machine that generated it (do not commit):

`%TEMP%\sap-abap-agent-gui-keys\sap-abap-agent-gui.key`

```powershell
# From a shell that can reach GitHub (gh auth login).
# IMPORTANT: use cmd.exe stdin redirect — PowerShell piping/UTF-8-BOM corrupts the key
# (Tauri then fails with: Invalid symbol 239, offset 0).
$key = "$env:TEMP\sap-abap-agent-gui-keys\sap-abap-agent-gui.key"
cmd /c "gh secret set TAURI_SIGNING_PRIVATE_KEY --repo StormShynn/sap-abap-agent < %TEMP%\sap-abap-agent-gui-keys\sap-abap-agent-gui.key"
# Empty password must be ZERO bytes (not a newline from `echo.`):
python -c "import subprocess; subprocess.run(['gh','secret','set','TAURI_SIGNING_PRIVATE_KEY_PASSWORD','--repo','StormShynn/sap-abap-agent'], input=b'', check=True)"
```

If the key file is gone, regenerate and **replace** `plugins.updater.pubkey` in
`tauri.conf.json` (old installs will not accept updates signed with a new key):

```powershell
cd gui-native
npx tauri signer generate -w "$env:TEMP\sap-abap-agent-gui-keys\sap-abap-agent-gui.key" --ci -f
```

### Updater endpoint

Rolling tag **`gui-latest`** (recreated each `gui-v*` release):

`https://github.com/StormShynn/sap-abap-agent/releases/download/gui-latest/update.json`

### Local minisign (empty password)

Tauri treats missing password as interactive prompt (hangs in CI/non-TTY). Pass an
explicit empty string. On PowerShell, `$env:...=""` / `-p ""` often becomes “unset”;
use a shell cmdline instead:

```powershell
npx tauri signer sign "path\to\file.nsis.zip" -f $key --password ""
```

## Authenticode — optional Windows code signing

### Current repo status (as of 2026-08-02)

| Secret | Present? |
|--------|----------|
| `TAURI_SIGNING_PRIVATE_KEY` (+ password empty OK) | **Yes** — required for `gui-release.yml` |
| `WINDOWS_CERTIFICATE` | **No** |
| `WINDOWS_CERTIFICATE_PASSWORD` | **No** |

Next `gui-v*` release ships **minisign-signed** updater artifacts; installers remain
**without** Authenticode until a human buys a cert and sets the two secrets above.
CI fail-soft wiring is already in `gui-release.yml` (warn + continue).

### Decision (product preference)

- Ship GUI releases when **minisign** secrets are present.
- If Authenticode secrets are **missing**, CI logs a warning and continues with
  **unsigned** NSIS/MSI (SmartScreen may warn users). Do not fail the job.
- If Authenticode secrets are **present**, CI imports the PFX, overlays
  `certificateThumbprint` / `digestAlgorithm` / `timestampUrl` for the Tauri
  build, and signs binaries + installers via `signtool`.

Buying and uploading a real code-signing certificate is a **human** step. Agents
must not invent certificates or commit PFX material.

### Obtain a certificate (human)

1. Purchase a **code signing** certificate (not SSL/TLS) from a CA Microsoft trusts.
   - **OV** (Organization Validated) or **EV** (Extended Validation). EV usually
     reaches SmartScreen reputation faster.
   - Since mid-2023 many CAs issue **non-exportable / HSM-backed** keys only.
     If you cannot get a `.pfx`, prefer **Azure Trusted Signing** (or Azure Key
     Vault + custom `signCommand`) instead of the PFX path below — see
     [Tauri Windows Code Signing](https://v2.tauri.app/distribute/sign/windows/).
2. If you have an exportable cert + private key, produce a password-protected PFX:

```powershell
openssl pkcs12 -export -in cert.cer -inkey private-key.key -out certificate.pfx
```

3. Base64-encode the PFX for GitHub Actions (raw base64, no PEM headers):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.pfx")) | Set-Clipboard
# Or: certutil -encode certificate.pfx base64cert.txt  (strip BEGIN/END lines if using FromBase64String)
```

4. Set repo secrets (never commit the PFX):

```powershell
# Paste base64 when prompted (or redirect a file of raw base64):
gh secret set WINDOWS_CERTIFICATE --repo StormShynn/sap-abap-agent
gh secret set WINDOWS_CERTIFICATE_PASSWORD --repo StormShynn/sap-abap-agent
```

5. Re-run **GUI Native Windows Release** on a `gui-v*` tag (or `workflow_dispatch`).
   When secrets are present, the job imports the cert and passes a Tauri config
   overlay; when absent, it warns and ships unsigned Authenticode.

### CI behavior (`.github/workflows/gui-release.yml`)

| Secrets | Build outcome |
|---------|----------------|
| Minisign only | Updater-signed artifacts; installers not Authenticode-signed |
| Minisign + `WINDOWS_CERTIFICATE` + `WINDOWS_CERTIFICATE_PASSWORD` | Updater-signed **and** Authenticode-signed |
| Missing minisign | Job **fails** (updater channel broken without it) |

Optional overlay fields applied only when Authenticode secrets exist:

- `bundle.windows.certificateThumbprint` (from imported PFX)
- `bundle.windows.digestAlgorithm`: `sha256`
- `bundle.windows.timestampUrl`: `http://timestamp.digicert.com`

Committed `tauri.conf.json` stays free of thumbprints so local unsigned builds remain the default.

### Verify a signed installer (after a signed release)

```powershell
Get-AuthenticodeSignature path\to\SAP_ABAP_Agent_*_x64-setup.exe
# Status should be Valid when the cert chain is trusted on the machine
```
