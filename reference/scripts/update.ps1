#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Sap-btp-agent & plugin auto-update — tu dong update moi nhat tu GitHub Releases
.DESCRIPTION
    - Tai wheel .whl moi nhat tu GitHub Release (mcp-server-v*)
    - pip install --upgrade
    - Neu co thay doi plugin, clone lai hoac git pull
.EXAMPLE
    .\reference\scripts\update.ps1
#>

$Repo = "StormShynn/sap-abap-agent"
$ApiUrl = "https://api.github.com/repos/$Repo/releases"

Write-Host "=== SAP ABAP Agent — Auto Update ===" -ForegroundColor Cyan

# 1. Kiem tra git co san khong
$hasGit = (Get-Command git -ErrorAction SilentlyContinue) -ne $null

if ($hasGit -and (Test-Path ".git")) {
    Write-Host "[1/3] Git pull plugin..." -ForegroundColor Yellow
    git pull --rebase
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Plugin updated" -ForegroundColor Green
    } else {
        Write-Host "  !! Git pull failed, check manually" -ForegroundColor Red
    }
} else {
    Write-Host "[1/3] Git not available or not a git repo — clone plugin..." -ForegroundColor Yellow
    $pluginDir = "$env:USERPROFILE\.claude\plugins\sap-abap-agent"
    if (Test-Path $pluginDir) {
        Set-Location $pluginDir; git pull
    } else {
        git clone "https://github.com/$Repo.git" $pluginDir
        Write-Host "  Plugin cloned to $pluginDir" -ForegroundColor Green
        Write-Host "  Run: claude plugin install $pluginDir" -ForegroundColor Yellow
    }
}

# 2. Tai wheel moi nhat
Write-Host "[2/3] Fetch latest release..." -ForegroundColor Yellow
try {
    $releases = Invoke-RestMethod -Uri $ApiUrl -Headers @{ "Accept" = "application/vnd.github.v3+json" }
    $mcpRelease = $releases | Where-Object { $_.tag_name -like "mcp-server-v*" } | Select-Object -First 1
    if (-not $mcpRelease) {
        Write-Host "  !! No mcp-server release found" -ForegroundColor Red
        exit 1
    }
    $version = $mcpRelease.tag_name -replace "^mcp-server-v", ""
    $wheelName = "sap_abap_agent_mcp-${version}-py3-none-any.whl"
    $asset = $mcpRelease.assets | Where-Object { $_.name -eq $wheelName }
    if (-not $asset) {
        Write-Host "  !! Wheel not found in release" -ForegroundColor Red
        exit 1
    }
    $wheelUrl = $asset.browser_download_url
    $tempDir = "$env:TEMP\sap-btp-update"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    $wheelPath = "$tempDir\$wheelName"

    Write-Host "  Downloading $wheelName ..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $wheelUrl -OutFile $wheelPath
    Write-Host "  OK Downloaded" -ForegroundColor Green
}
catch {
    Write-Host "  !! Failed: $_" -ForegroundColor Red
    exit 1
}

# 3. pip install
Write-Host "[3/3] pip install --upgrade ..." -ForegroundColor Yellow

# Neu sap-btp-agent.exe dang chay (vd MCP server dang duoc Claude Code giu ket
# noi), pip khong ghi de duoc file .exe khoa boi tien trinh do (WinError 32).
# Dong het truoc khi cai - an toan vi day chi la entry-point script, khong mat
# du lieu; ket noi MCP se tu ket noi lai sau khi restart Claude Code.
Get-Process -Name "sap-btp-agent" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

pip install --upgrade "$wheelPath"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK sap-btp-agent updated to v$version" -ForegroundColor Green
} else {
    Write-Host "  !! pip install failed" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "sap-btp-agent version: v$version" -ForegroundColor Green
sap-btp-agent --help
