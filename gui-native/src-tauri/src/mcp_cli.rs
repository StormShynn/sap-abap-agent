//! Goi mcp-sap-connect CLI qua subprocess. Rust CHI la lop UI/orchestration -
//! moi logic that (SAP auth, ma hoa, doc/ghi profile registry) van nam trong
//! Python (mcp_sap_connect), goi qua cac subcommand --json de tranh phai viet
//! lai/dong bo lai format file rieng ben Rust (tranh drift giua 2 ngon ngu).

use serde::{Deserialize, Serialize};
use serde_json::Value;
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
