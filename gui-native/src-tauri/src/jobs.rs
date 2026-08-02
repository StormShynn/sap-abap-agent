//! Quan ly 1 subprocess job dang chay (giong runner.py + phan reauth/early-
//! finish trong app.py ben Python): stream stdout theo dong qua Tauri event,
//! spawn cua so CMD moi cho cac luong can nhap tay (wizard/setup-from-file),
//! va cho phep cancel job dang chay (dong bam X luc job dang chay).
//!
//! Chi 1 job chay 1 luc (giong Python: self._job) - tranh 2 lenh mcp-sap-connect
//! ghi de secrets.json cua cung 1 profile cung luc.

use crate::mcp_cli::resolve_executable;
use serde::Serialize;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use tauri::{AppHandle, Emitter};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::{Child, Command};
use tokio::sync::Mutex;

#[derive(Serialize, Clone)]
pub struct JobDonePayload {
    pub code: i32,
    pub label: String,
}

/// State toan cuc dung chung qua Tauri (quan ly bang app.manage(JobState::default())).
#[derive(Default)]
pub struct JobState {
    running: Arc<AtomicBool>,
    child: Arc<Mutex<Option<Child>>>,
}

fn build_command(args: &[String], env_extra: &HashMap<String, String>) -> Command {
    let full = resolve_executable();
    let mut cmd = Command::new(&full[0]);
    cmd.args(&full[1..]);
    cmd.args(args);
    for (k, v) in env_extra {
        cmd.env(k, v);
    }
    cmd
}

/// Chay subprocess AN (khong popup console rieng), stream tung dong stdout/
/// stderr qua event "job-line", khi xong emit "job-done".
#[tauri::command]
pub async fn start_streamed(
    app: AppHandle,
    state: tauri::State<'_, JobState>,
    args: Vec<String>,
    env_extra: Option<HashMap<String, String>>,
    label: String,
) -> Result<(), String> {
    if state.running.swap(true, Ordering::SeqCst) {
        return Err("Dang co lenh khac chay - doi lenh hien tai ket thuc truoc.".into());
    }

    let mut cmd = build_command(&args, &env_extra.unwrap_or_default());
    #[cfg(windows)]
    {
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    cmd.stdout(std::process::Stdio::piped());
    cmd.stderr(std::process::Stdio::piped());

    let mut child: Child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => {
            state.running.store(false, Ordering::SeqCst);
            return Err(format!("Khong chay duoc mcp-sap-connect: {e}"));
        }
    };

    let stdout = child.stdout.take().expect("stdout duoc pipe");
    let stderr = child.stderr.take().expect("stderr duoc pipe");

    *state.child.lock().await = Some(child);

    let app_out = app.clone();
    tokio::spawn(async move {
        let mut lines = BufReader::new(stdout).lines();
        while let Ok(Some(line)) = lines.next_line().await {
            let _ = app_out.emit("job-line", line);
        }
    });
    let app_err = app.clone();
    tokio::spawn(async move {
        let mut lines = BufReader::new(stderr).lines();
        while let Ok(Some(line)) = lines.next_line().await {
            let _ = app_err.emit("job-line", line);
        }
    });

    spawn_waiter(app, state.running.clone(), state.child.clone(), label);
    Ok(())
}

/// Mo cua so CMD moi chay lenh (dung cho wizard setup / setup --from-file -
/// can nhap tay interactive: SAML fallback, cookie paste, xac nhan mcp-setup).
/// Emit "job-done" khi cua so do dong.
#[tauri::command]
pub async fn start_new_console(
    app: AppHandle,
    state: tauri::State<'_, JobState>,
    args: Vec<String>,
    label: String,
) -> Result<(), String> {
    if state.running.swap(true, Ordering::SeqCst) {
        return Err("Dang co lenh khac chay - doi lenh hien tai ket thuc truoc.".into());
    }
    let mut cmd = build_command(&args, &HashMap::new());
    #[cfg(windows)]
    {
        const CREATE_NEW_CONSOLE: u32 = 0x0000_0010;
        cmd.creation_flags(CREATE_NEW_CONSOLE);
    }
    let child = match cmd.spawn() {
        Ok(c) => c,
        Err(e) => {
            state.running.store(false, Ordering::SeqCst);
            return Err(format!("Khong mo duoc cua so CMD: {e}"));
        }
    };
    *state.child.lock().await = Some(child);
    spawn_waiter(app, state.running.clone(), state.child.clone(), label);
    Ok(())
}

fn spawn_waiter(
    app: AppHandle,
    running: Arc<AtomicBool>,
    child_slot: Arc<Mutex<Option<Child>>>,
    label: String,
) {
    tokio::spawn(async move {
        let status = {
            let mut guard = child_slot.lock().await;
            match guard.as_mut() {
                Some(c) => c.wait().await,
                None => return,
            }
        };
        *child_slot.lock().await = None;
        running.store(false, Ordering::SeqCst);
        let code = status.map(|s| s.code().unwrap_or(-1)).unwrap_or(-1);
        let _ = app.emit("job-done", JobDonePayload { code, label });
    });
}

/// Huy job dang chay (dung khi user dong cua so chinh giua luc dang chay lenh).
#[tauri::command]
pub async fn cancel_job(state: tauri::State<'_, JobState>) -> Result<(), String> {
    let mut guard = state.child.lock().await;
    if let Some(child) = guard.as_mut() {
        let _ = child.kill().await;
    }
    Ok(())
}

#[tauri::command]
pub fn is_job_running(state: tauri::State<'_, JobState>) -> bool {
    state.running.load(Ordering::SeqCst)
}

// ===== Early-finish marker file (reauth auto mode) ======================
// Tuong duong _on_reauth/_on_done_clicked ben Python: tao 1 duong dan file
// (KHONG tao file that), truyen qua env SAP_BTP_EARLY_FINISH_FILE cho
// subprocess reauth - subprocess (Python, _wire_early_finish_event) watch
// duong dan nay va set asyncio.Event ngay khi file xuat hien. Bam nut "Da
// xong" trong GUI chi la touch file nay.

#[tauri::command]
pub fn make_early_finish_path() -> Result<String, String> {
    let dir = std::env::temp_dir();
    let unique = format!(
        "sap_early_{}.path",
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0)
    );
    let path = dir.join(unique);
    // Chi tra ve duong dan - KHONG tao file that (giong mkstemp+unlink ben
    // Python) - subprocess se tu watch su xuat hien cua duong dan nay.
    Ok(path.to_string_lossy().to_string())
}

#[tauri::command]
pub fn touch_early_finish(path: String) -> Result<(), String> {
    std::fs::File::create(&path).map_err(|e| format!("Khong touch duoc file marker: {e}"))?;
    Ok(())
}

#[tauri::command]
pub fn cleanup_early_finish(path: String) {
    let _ = std::fs::remove_file(path);
}
