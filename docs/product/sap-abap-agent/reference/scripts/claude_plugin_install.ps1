# Install SAP ABAP Agent into Claude Code (marketplace + plugin).
# Requires: `claude` CLI on PATH. Run once per machine/user.
# Usage:
#   powershell -ExecutionPolicy Bypass -File reference\scripts\claude_plugin_install.ps1

$ErrorActionPreference = "Stop"

function Assert-Claude {
    $cmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Host "[ERROR] Khong thay 'claude' trong PATH. Cai Claude Code truoc." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] claude: $($cmd.Source)"
}

Assert-Claude

Write-Host "==> marketplace add StormShynn/sap-abap-agent"
& claude plugin marketplace add StormShynn/sap-abap-agent
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] marketplace add exit $LASTEXITCODE — co the da add truoc do." -ForegroundColor Yellow
}

Write-Host "==> plugin install sap-abap-agent"
& claude plugin install sap-abap-agent
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] plugin install failed (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "[OK] Xong. Mo phien Claude Code MOI de load skills/hooks." -ForegroundColor Green
Write-Host "Tiep: mcp-sap-connect mcp-setup  (hoac GUI MCP Servers → Core)"
Write-Host "Team: xem docs/rollout-guide.md"
