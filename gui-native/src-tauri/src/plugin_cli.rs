//! Goi thang binary `claude` (Claude Code CLI) qua subprocess de kiem tra/cap
//! nhat chinh plugin sap-abap-agent trong Claude Code. Khac voi mcp_cli.rs
//! (goi mcp-sap-connect, roi mcp-sap-connect moi goi tiep `claude mcp add/
//! remove`) - o day khong co Python xen giua, Rust goi thang `claude`.

use serde::{Deserialize, Serialize};
use std::path::Path;
use std::process::Stdio;
use tokio::process::Command;

/// Chuoi dung de nhan dien marketplace cua plugin nay trong danh sach
/// `claude plugin marketplace list --json`, khong phu thuoc ten local user
/// da dat luc `marketplace add` (co the khac "sap-abap-agent" tuy cach add).
const REPO_NEEDLE: &str = "stormshynn/sap-abap-agent";

fn build_command(claude_path: &Path, args: &[String]) -> Command {
    let mut cmd = Command::new(claude_path);
    cmd.args(args);
    #[cfg(windows)]
    {
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    cmd
}

/// Chay 1 lenh `claude` ngan, doi ket qua, tra ve (exit_code, stdout, stderr).
/// Tuong duong mcp_cli::run_capture nhung target binary `claude` truc tiep.
async fn run_capture(claude_path: &Path, args: &[String]) -> Result<(i32, String, String), String> {
    let mut cmd = build_command(claude_path, args);
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
    let output = cmd
        .output()
        .await
        .map_err(|e| format!("Khong chay duoc claude: {e}"))?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let code = output.status.code().unwrap_or(-1);
    Ok((code, stdout, stderr))
}

#[derive(Deserialize)]
struct MarketplaceEntry {
    name: String,
    #[serde(default)]
    url: Option<String>,
    #[serde(default)]
    repo: Option<String>,
}

#[derive(Deserialize)]
struct PluginListEntry {
    id: String,
    version: String,
    #[serde(rename = "lastUpdated", default)]
    last_updated: Option<String>,
}

struct Discovered {
    plugin_id: String,
    marketplace_name: String,
    version: String,
    last_updated: Option<String>,
}

/// Tim marketplace + plugin sap-abap-agent da dang ky trong Claude Code.
/// Chi doc cache local (`plugin marketplace list` / `plugin list --json`) -
/// khong dong mang, an toan goi moi lan mo modal.
async fn discover(claude_path: &Path) -> Result<Option<Discovered>, String> {
    let (code, stdout, stderr) = run_capture(
        claude_path,
        &[
            "plugin".to_string(),
            "marketplace".to_string(),
            "list".to_string(),
            "--json".to_string(),
        ],
    )
    .await?;
    if code != 0 {
        return Err(format!("claude plugin marketplace list that bai: {stderr}"));
    }
    let marketplaces: Vec<MarketplaceEntry> = serde_json::from_str(stdout.trim())
        .map_err(|e| format!("Khong parse duoc marketplace list: {e}"))?;
    let needle = REPO_NEEDLE.to_lowercase();
    let Some(marketplace) = marketplaces.iter().find(|m| {
        m.url.as_deref().unwrap_or("").to_lowercase().contains(&needle)
            || m.repo.as_deref().unwrap_or("").to_lowercase().contains(&needle)
    }) else {
        return Ok(None);
    };
    let marketplace_name = marketplace.name.clone();

    let (code, stdout, stderr) = run_capture(
        claude_path,
        &["plugin".to_string(), "list".to_string(), "--json".to_string()],
    )
    .await?;
    if code != 0 {
        return Err(format!("claude plugin list that bai: {stderr}"));
    }
    let plugins: Vec<PluginListEntry> = serde_json::from_str(stdout.trim())
        .map_err(|e| format!("Khong parse duoc plugin list: {e}"))?;
    let suffix = format!("@{marketplace_name}");
    let Some(plugin) = plugins.iter().find(|p| p.id.ends_with(&suffix)) else {
        return Ok(None);
    };

    Ok(Some(Discovered {
        plugin_id: plugin.id.clone(),
        marketplace_name,
        version: plugin.version.clone(),
        last_updated: plugin.last_updated.clone(),
    }))
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct PluginStatusData {
    #[serde(rename = "claudeAvailable")]
    pub claude_available: bool,
    pub found: bool,
    #[serde(rename = "pluginId")]
    pub plugin_id: Option<String>,
    pub version: Option<String>,
    #[serde(rename = "lastUpdated")]
    pub last_updated: Option<String>,
    pub detail: Option<String>,
}

/// Doc trang thai plugin sap-abap-agent hien tai (khong dong mang, thuan doc).
#[tauri::command]
pub async fn plugin_status() -> Result<PluginStatusData, String> {
    let Ok(claude_path) = which::which("claude") else {
        return Ok(PluginStatusData {
            claude_available: false,
            found: false,
            plugin_id: None,
            version: None,
            last_updated: None,
            detail: Some("Khong tim thay 'claude' trong PATH.".to_string()),
        });
    };

    match discover(&claude_path).await? {
        Some(d) => Ok(PluginStatusData {
            claude_available: true,
            found: true,
            plugin_id: Some(d.plugin_id),
            version: Some(d.version),
            last_updated: d.last_updated,
            detail: None,
        }),
        None => Ok(PluginStatusData {
            claude_available: true,
            found: false,
            plugin_id: None,
            version: None,
            last_updated: None,
            detail: Some(
                "Chua tim thay plugin sap-abap-agent da cai trong Claude Code.".to_string(),
            ),
        }),
    }
}

/// Cap nhat plugin sap-abap-agent: refresh marketplace cache roi update plugin
/// (bat buoc dung dang <plugin>@<marketplace>, ten rong se bao "not found").
/// Ok/Err deu tra ve nguyen van text CLI - khong dien giai lai loi CLI.
#[tauri::command]
pub async fn plugin_update() -> Result<String, String> {
    let claude_path =
        which::which("claude").map_err(|_| "Khong tim thay 'claude' trong PATH.".to_string())?;

    let Some(d) = discover(&claude_path).await? else {
        return Err("Chua tim thay plugin sap-abap-agent da cai trong Claude Code.".to_string());
    };

    let (_mkt_code, mkt_stdout, mkt_stderr) = run_capture(
        &claude_path,
        &[
            "plugin".to_string(),
            "marketplace".to_string(),
            "update".to_string(),
            d.marketplace_name.clone(),
        ],
    )
    .await?;

    let (upd_code, upd_stdout, upd_stderr) = run_capture(
        &claude_path,
        &["plugin".to_string(), "update".to_string(), d.plugin_id.clone()],
    )
    .await?;

    let mut combined = String::new();
    for part in [mkt_stdout.trim(), mkt_stderr.trim(), upd_stdout.trim(), upd_stderr.trim()] {
        if !part.is_empty() {
            if !combined.is_empty() {
                combined.push('\n');
            }
            combined.push_str(part);
        }
    }

    if upd_code == 0 {
        Ok(combined)
    } else {
        Err(combined)
    }
}
