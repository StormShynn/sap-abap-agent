//! Goi mcp-sap-connect CLI qua subprocess. Rust CHI la lop UI/orchestration -
//! moi logic that (SAP auth, ma hoa, doc/ghi profile registry) van nam trong
//! Python (mcp_sap_connect), goi qua cac subcommand --json de tranh phai viet
//! lai/dong bo lai format file rieng ben Rust (tranh drift giua 2 ngon ngu).

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::process::Stdio;
use tokio::process::Command;

/// Tra ve command de chay CLI - uu tien binary tren PATH (entry point cua pip
/// install), fallback ve `python -m mcp_sap_connect.cli` cho moi truong dev.
/// Tuong duong runner._resolve_executable() ben Python.
pub fn resolve_executable() -> Vec<String> {
    if let Ok(path) = which::which("mcp-sap-connect") {
        return vec![path.to_string_lossy().to_string()];
    }
    let python = which::which("python")
        .or_else(|_| which::which("python3"))
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|_| "python".to_string());
    vec![python, "-m".to_string(), "mcp_sap_connect.cli".to_string()]
}

/// PATH-only ship (decision 0001): GUI khong embed Python. Probe xem CLI goi
/// duoc that su hay khong (binary PATH hoac python -m), de first-run banner
/// huong dan pip/doctor thay vi loi mo ho luc bam Reauth.
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct RuntimeStatus {
    pub ok: bool,
    pub mode: String,
    pub detail: String,
    pub install_hint: String,
}

#[tauri::command]
pub async fn check_runtime() -> Result<RuntimeStatus, String> {
    let install_hint = concat!(
        "pip install \"mcp-sap-connect[win-dpapi]\"\n",
        "roi chay: python -m mcp_sap_connect.doctor\n",
        "(neu 'mcp-sap-connect' khong nhan: them Scripts vao User PATH, mo lai app)"
    )
    .to_string();

    if let Ok(path) = which::which("mcp-sap-connect") {
        let path_s = path.to_string_lossy().to_string();
        match run_capture(&["profiles".to_string(), "list".to_string(), "--json".to_string()]).await
        {
            Ok((code, stdout, _stderr)) if code == 0 || !stdout.trim().is_empty() => {
                return Ok(RuntimeStatus {
                    ok: true,
                    mode: "path".to_string(),
                    detail: format!("mcp-sap-connect tren PATH: {path_s}"),
                    install_hint,
                });
            }
            Ok((code, _stdout, stderr)) => {
                return Ok(RuntimeStatus {
                    ok: false,
                    mode: "path-broken".to_string(),
                    detail: format!(
                        "Tim thay {path_s} nhung chay that bai (exit {code}): {stderr}"
                    ),
                    install_hint,
                });
            }
            Err(e) => {
                return Ok(RuntimeStatus {
                    ok: false,
                    mode: "path-broken".to_string(),
                    detail: format!("Tim thay {path_s} nhung khong chay duoc: {e}"),
                    install_hint,
                });
            }
        }
    }

    // Fallback: python -m mcp_sap_connect.cli (dev / PATH thieu Scripts)
    match run_capture(&["profiles".to_string(), "list".to_string(), "--json".to_string()]).await {
        Ok((code, stdout, _stderr)) if code == 0 || stdout.trim().starts_with('{') => {
            let exe = resolve_executable().join(" ");
            Ok(RuntimeStatus {
                ok: true,
                mode: "python-module".to_string(),
                detail: format!("CLI qua module: {exe}"),
                install_hint,
            })
        }
        Ok((code, _stdout, stderr)) => Ok(RuntimeStatus {
            ok: false,
            mode: "missing".to_string(),
            detail: format!(
                "Khong goi duoc mcp-sap-connect (exit {code}). {stderr}"
            ),
            install_hint,
        }),
        Err(e) => Ok(RuntimeStatus {
            ok: false,
            mode: "missing".to_string(),
            detail: format!("Khong goi duoc mcp-sap-connect: {e}"),
            install_hint,
        }),
    }
}

pub fn build_command(args: &[String]) -> Command {
    let full = resolve_executable();
    let mut cmd = Command::new(&full[0]);
    cmd.args(&full[1..]);
    cmd.args(args);
    #[cfg(windows)]
    {
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    cmd
}

/// Chay 1 lenh CLI ngan, doi ket qua, tra ve (exit_code, stdout, stderr).
/// Dung cho cac lenh --json (list/license/import) - khong can streaming.
pub async fn run_capture(args: &[String]) -> Result<(i32, String, String), String> {
    let mut cmd = build_command(args);
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
    let output = cmd
        .output()
        .await
        .map_err(|e| format!("Khong chay duoc mcp-sap-connect: {e}"))?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let code = output.status.code().unwrap_or(-1);
    Ok((code, stdout, stderr))
}

/// Chay lenh --json va parse ket qua. Loi (khong chay duoc, JSON hong, hoac
/// {"error": ...}/{"ok": false, ...} tu chinh CLI) deu tra ve Err(String) de
/// frontend hien thi thong bao ro rang.
pub async fn run_json(args: &[String]) -> Result<Value, String> {
    let (code, stdout, stderr) = run_capture(args).await?;
    if stdout.trim().is_empty() {
        return Err(format!(
            "mcp-sap-connect khong tra ve gi (exit {code}): {stderr}"
        ));
    }
    let value: Value = serde_json::from_str(stdout.trim()).map_err(|e| {
        format!("Khong parse duoc JSON tu mcp-sap-connect: {e}\nOutput: {stdout}")
    })?;
    if let Some(err) = value.get("error").and_then(|v| v.as_str()) {
        return Err(err.to_string());
    }
    if value.get("ok").and_then(|v| v.as_bool()) == Some(false) {
        let err = value
            .get("error")
            .and_then(|v| v.as_str())
            .unwrap_or("Loi khong xac dinh");
        return Err(err.to_string());
    }
    Ok(value)
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ProfileItem {
    pub id: String,
    pub label: Option<String>,
    pub url: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ProfilesData {
    pub active: Option<String>,
    pub items: Vec<ProfileItem>,
}

#[tauri::command]
pub async fn list_profiles() -> Result<ProfilesData, String> {
    let value = run_json(&[
        "profiles".to_string(),
        "list".to_string(),
        "--json".to_string(),
    ])
    .await?;
    serde_json::from_value(value).map_err(|e| format!("Loi doc profiles: {e}"))
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LicenseStatus {
    pub profile_id: String,
    pub label: String,
    pub url: String,
    pub is_active: bool,
    pub has_credentials: bool,
    #[serde(rename = "type")]
    pub auth_type: String,
    pub expires_at: Option<f64>,
    pub expires_in_human: String,
    pub is_expired: bool,
    pub is_warning: bool,
    pub last_saved: Option<f64>,
    pub extra: Value,
}

#[tauri::command]
pub async fn get_license_statuses() -> Result<Vec<LicenseStatus>, String> {
    let value = run_json(&["license".to_string(), "--json".to_string()]).await?;
    serde_json::from_value(value).map_err(|e| format!("Loi doc license status: {e}"))
}

#[tauri::command]
pub async fn set_active_profile(profile_id: String) -> Result<(), String> {
    let (code, _stdout, stderr) =
        run_capture(&["profiles".to_string(), "use".to_string(), profile_id]).await?;
    if code != 0 {
        return Err(format!("Loi khi set active: {stderr}"));
    }
    Ok(())
}

#[tauri::command]
pub async fn remove_profile(profile_id: String) -> Result<(), String> {
    let (code, _stdout, stderr) =
        run_capture(&["profiles".to_string(), "remove".to_string(), profile_id]).await?;
    if code != 0 {
        return Err(format!("Loi khi xoa profile: {stderr}"));
    }
    Ok(())
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ImportResult {
    #[serde(rename = "profileId")]
    pub profile_id: String,
    pub url: String,
}

#[tauri::command]
pub async fn import_json_backup(path: String) -> Result<ImportResult, String> {
    let value = run_json(&[
        "profiles".to_string(),
        "import".to_string(),
        path,
        "--json".to_string(),
    ])
    .await?;
    serde_json::from_value(value).map_err(|e| format!("Loi import: {e}"))
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct McpServerStatus {
    pub name: String,
    pub category: String,
    pub description: String,
    #[serde(rename = "envVars")]
    pub env_vars: Vec<String>,
    pub registered: bool,
    pub doc: Option<String>,
    /// Absolute URL for in-app "Mo huong dan" (manual servers).
    #[serde(rename = "docUrl", default)]
    pub doc_url: Option<String>,
    /// Install / `claude mcp add` hint for clipboard copy.
    #[serde(rename = "installHint", default)]
    pub install_hint: Option<String>,
    /// false for manual servers that still need clone/build/license.
    #[serde(rename = "canRegister", default)]
    pub can_register: Option<bool>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct McpStatusData {
    pub servers: Vec<McpServerStatus>,
    #[serde(rename = "claudeAvailable")]
    pub claude_available: bool,
    /// Mandatory Core preset names (GUI CTA).
    #[serde(rename = "coreServers", default)]
    pub core_servers: Option<Vec<String>>,
}

/// Doc inventory + trang thai dang ky cua MCP servers (mcp-sap-connect mcp-setup
/// --status-json) - thuan doc, khong thay doi gi.
#[tauri::command]
pub async fn mcp_status() -> Result<McpStatusData, String> {
    let value = run_json(&["mcp-setup".to_string(), "--status-json".to_string()]).await?;
    serde_json::from_value(value).map_err(|e| format!("Loi doc MCP status: {e}"))
}

/// Dang ky 1 MCP server cu the qua `claude mcp add` (mcp-sap-connect mcp-setup
/// --register-json <name> [--env K=V ...]). env rong neu server khong can bien nao.
#[tauri::command]
pub async fn mcp_register(name: String, env: HashMap<String, String>) -> Result<(), String> {
    let mut args = vec![
        "mcp-setup".to_string(),
        "--register-json".to_string(),
        name,
    ];
    for (k, v) in env {
        args.push("--env".to_string());
        args.push(format!("{k}={v}"));
    }
    run_json(&args).await?;
    Ok(())
}

/// Go dang ky 1 MCP server (`mcp-setup --unregister-json <name>` → `claude mcp remove`).
#[tauri::command]
pub async fn mcp_unregister(name: String) -> Result<(), String> {
    let args = vec![
        "mcp-setup".to_string(),
        "--unregister-json".to_string(),
        name,
    ];
    run_json(&args).await?;
    Ok(())
}
