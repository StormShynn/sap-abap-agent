//! Kiem tra ban GUI moi tren GitHub Releases (tag `gui-v*`).
//!
//! Khong dung tauri-plugin-updater o day: can signing key + `update.json` tren
//! release (giong mcp-switch). PATH-only GA chi can bao "co ban moi" + mo trang
//! Releases de user tai NSIS/MSI thu cong.

use serde::{Deserialize, Serialize};

const REPO: &str = "StormShynn/sap-abap-agent";
const RELEASES_API: &str = "https://api.github.com/repos/StormShynn/sap-abap-agent/releases?per_page=40";
const RELEASES_PAGE: &str = "https://github.com/StormShynn/sap-abap-agent/releases";

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct UpdateCheckResult {
    /// idle semantics for UI: "up_to_date" | "available" | "no_gui_release" | "error"
    pub status: String,
    pub current_version: String,
    pub latest_tag: Option<String>,
    pub latest_version: Option<String>,
    pub release_url: Option<String>,
    pub message: String,
}

#[derive(Deserialize)]
struct GhRelease {
    tag_name: String,
    html_url: String,
    draft: bool,
    #[serde(default)]
    assets: Vec<GhAsset>,
}

#[derive(Deserialize)]
struct GhAsset {
    name: String,
}

/// Semver (major, minor, patch) tu chuoi "1.19.0" / "gui-v1.19.0" / "v1.19.0".
fn parse_semver(raw: &str) -> Option<(u64, u64, u64)> {
    let s = raw.trim();
    let s = s.strip_prefix("gui-v").or_else(|| s.strip_prefix('v')).unwrap_or(s);
    let mut parts = s.split('.');
    let major = parts.next()?.parse().ok()?;
    let minor = parts.next()?.parse().ok()?;
    let patch = parts.next()?.parse().ok()?;
    Some((major, minor, patch))
}

fn cmp_semver(a: (u64, u64, u64), b: (u64, u64, u64)) -> std::cmp::Ordering {
    a.cmp(&b)
}

fn has_installer_asset(rel: &GhRelease) -> bool {
    rel.assets.iter().any(|a| {
        let n = a.name.to_ascii_lowercase();
        n.ends_with(".exe") || n.ends_with(".msi")
    })
}

#[tauri::command]
pub async fn check_gui_update() -> Result<UpdateCheckResult, String> {
    let current_version = env!("CARGO_PKG_VERSION").to_string();
    let current = parse_semver(&current_version).ok_or_else(|| {
        format!("Khong parse duoc version hien tai: {current_version}")
    })?;

    let body = tokio::task::spawn_blocking(|| {
        ureq::get(RELEASES_API)
            .set("User-Agent", "sap-abap-agent-gui")
            .set("Accept", "application/vnd.github+json")
            .call()
            .map_err(|e| format!("Khong goi duoc GitHub API (offline / rate limit?): {e}"))?
            .into_string()
            .map_err(|e| format!("Doc response GitHub that bai: {e}"))
    })
    .await
    .map_err(|e| format!("Task join failed: {e}"))??;

    let releases: Vec<GhRelease> = serde_json::from_str(&body)
        .map_err(|e| format!("JSON GitHub Releases khong hop le: {e}"))?;

    let mut gui_releases: Vec<(GhRelease, (u64, u64, u64))> = Vec::new();
    for rel in releases {
        if rel.draft {
            continue;
        }
        if !rel.tag_name.starts_with("gui-v") {
            continue;
        }
        let Some(ver) = parse_semver(&rel.tag_name) else {
            continue;
        };
        gui_releases.push((rel, ver));
    }

    if gui_releases.is_empty() {
        return Ok(UpdateCheckResult {
            status: "no_gui_release".to_string(),
            current_version,
            latest_tag: None,
            latest_version: None,
            release_url: Some(RELEASES_PAGE.to_string()),
            message: format!(
                "Chua co GitHub Release tag gui-v* (co asset NSIS/MSI) tren {REPO}. \
                 Tag co the da push nhung workflow gui-release chua tao Release — \
                 xem {RELEASES_PAGE}"
            ),
        });
    }

    gui_releases.sort_by(|a, b| cmp_semver(b.1, a.1));
    let (best, best_ver) = &gui_releases[0];
    let latest_version = format!("{}.{}.{}", best_ver.0, best_ver.1, best_ver.2);
    let has_assets = has_installer_asset(best);

    if cmp_semver(*best_ver, current) == std::cmp::Ordering::Greater {
        let asset_note = if has_assets {
            "Co installer trong Release.".to_string()
        } else {
            "Release chua co file .exe/.msi — can chay lai workflow gui-release.".to_string()
        };
        return Ok(UpdateCheckResult {
            status: "available".to_string(),
            current_version,
            latest_tag: Some(best.tag_name.clone()),
            latest_version: Some(latest_version),
            release_url: Some(best.html_url.clone()),
            message: format!(
                "Co ban GUI moi: {} (ban dang dung v{}). {asset_note}",
                best.tag_name, env!("CARGO_PKG_VERSION")
            ),
        });
    }

    Ok(UpdateCheckResult {
        status: "up_to_date".to_string(),
        current_version,
        latest_tag: Some(best.tag_name.clone()),
        latest_version: Some(latest_version),
        release_url: Some(best.html_url.clone()),
        message: if has_assets {
            format!("Dang o ban moi nhat ({}).", best.tag_name)
        } else {
            format!(
                "Tag {} la moi nhat nhung Release chua co installer (.exe/.msi).",
                best.tag_name
            )
        },
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_gui_tag() {
        assert_eq!(parse_semver("gui-v1.19.0"), Some((1, 19, 0)));
        assert_eq!(parse_semver("1.19.1"), Some((1, 19, 1)));
        assert_eq!(parse_semver("v0.10.1"), Some((0, 10, 1)));
    }

    #[test]
    fn compare_newer() {
        assert_eq!(
            cmp_semver((1, 19, 1), (1, 19, 0)),
            std::cmp::Ordering::Greater
        );
    }
}
