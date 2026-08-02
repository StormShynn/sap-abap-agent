//! System tray icon + menu, tuong duong gui/tray.py (pystray) ben Python.
//!
//! Don gian hoa co chu dich so voi ban Python: bo submenu "Profiles" dong
//! (chon nhanh active profile tu tray) - Tauri tray menu duoc dung 1 lan luc
//! khoi tao, rebuild dong moi lan mo can them wiring event rieng; nguoi dung
//! van doi active profile binh thuong qua dropdown trong cua so chinh. Cac
//! muc con lai giu nguyen hanh vi + them:
//!   - Show window: hien cua so chinh (rename tu "Open GUI").
//!   - Quick ping (active): chay `ping` len profile active ngay tu tray, ket
//!     qua bao qua notification "job-done" (frontend da lang nghe).
//!   - Check for updates...: mo cua so + emit event "tray-check-update" de
//!     frontend mo About va chay onCheckUpdate() ngay lap tuc.

use crate::mcp_cli::run_json;
use std::sync::atomic::{AtomicBool, Ordering};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Emitter, Manager};

/// Setting "Tat thong bao" (sync tu frontend qua invoke, mac dinh BAT).
/// Rust side dung de gate notify() khi job khong spawn duoc — thong bao
/// job/update chinh van do frontend gui (cung da gate o day).
/// Default = BAT (true) de tranh vo tinh tat thong bao neu ai do dung Default.
pub struct NotifyState(AtomicBool);

impl NotifyState {
    pub fn new() -> Self {
        Self(AtomicBool::new(true))
    }
}

impl Default for NotifyState {
    fn default() -> Self {
        Self::new()
    }
}

/// Frontend goi khi user bat/tat notification trong About modal.
#[tauri::command]
pub fn set_notifications_enabled(state: tauri::State<'_, NotifyState>, enabled: bool) {
    state.0.store(enabled, Ordering::SeqCst);
}

async fn current_active_profile() -> Option<String> {
    let value = run_json(&[
        "profiles".to_string(),
        "list".to_string(),
        "--json".to_string(),
    ])
    .await
    .ok()?;
    value
        .get("active")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
}

pub fn build_tray(app: &AppHandle) -> tauri::Result<()> {
    let open_item = MenuItem::with_id(app, "tray-open", "Show window", true, None::<&str>)?;
    let ping_item =
        MenuItem::with_id(app, "tray-ping", "Quick ping (active)", true, None::<&str>)?;
    let reauth_item = MenuItem::with_id(app, "tray-reauth", "Reauth (active)", true, None::<&str>)?;
    let connect_item =
        MenuItem::with_id(app, "tray-connect", "Connect (active)", true, None::<&str>)?;
    let check_update_item = MenuItem::with_id(
        app,
        "tray-check-update",
        "Check for updates...",
        true,
        None::<&str>,
    )?;
    let license_item = MenuItem::with_id(
        app,
        "tray-license",
        "Open License Dashboard...",
        true,
        None::<&str>,
    )?;
    let plugin_item =
        MenuItem::with_id(app, "tray-plugin", "Plugin update...", true, None::<&str>)?;
    let about_item = MenuItem::with_id(app, "tray-about", "About...", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "tray-quit", "Quit", true, None::<&str>)?;
    let separator = PredefinedMenuItem::separator(app)?;

    let menu = Menu::with_items(
        app,
        &[
            &open_item,
            &ping_item,
            &separator,
            &reauth_item,
            &connect_item,
            &separator,
            &check_update_item,
            &license_item,
            &plugin_item,
            &about_item,
            &quit_item,
        ],
    )?;

    let icon = app
        .default_window_icon()
        .cloned()
        .expect("app phai co default window icon (khai bao trong tauri.conf.json)");

    TrayIconBuilder::with_id("main-tray")
        .icon(icon)
        .tooltip("SAP ABAP Agent")
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(move |app, event| {
            let app = app.clone();
            match event.id().as_ref() {
                "tray-open" => show_main_window(&app),
                "tray-ping" => {
                    tauri::async_runtime::spawn(async move {
                        run_active_job(&app, "ping").await;
                    });
                }
                "tray-reauth" => {
                    tauri::async_runtime::spawn(async move {
                        run_active_job(&app, "reauth").await;
                    });
                }
                "tray-connect" => {
                    tauri::async_runtime::spawn(async move {
                        run_active_job(&app, "connect").await;
                    });
                }
                "tray-check-update" => {
                    show_main_window(&app);
                    let _ = app.emit("tray-check-update", ());
                }
                "tray-license" => {
                    show_main_window(&app);
                    let _ = app.emit("open-license-dashboard", ());
                }
                "tray-plugin" => {
                    show_main_window(&app);
                    let _ = app.emit("open-plugin-panel", ());
                }
                "tray-about" => {
                    show_main_window(&app);
                    let _ = app.emit("open-about", ());
                }
                "tray-quit" => app.exit(0),
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                show_main_window(tray.app_handle());
            }
        })
        .build(app)?;

    Ok(())
}

fn show_main_window(app: &AppHandle) {
    if let Some(win) = app.get_webview_window("main") {
        let _ = win.show();
        let _ = win.set_focus();
    }
}

async fn run_active_job(app: &AppHandle, action: &str) {
    let Some(pid) = current_active_profile().await else {
        notify(app, "Chua co profile active. Mo GUI de setup.");
        return;
    };
    let label = format!("{action} {pid}");
    let args = vec![action.to_string(), pid];
    let state = app.state::<crate::jobs::JobState>();
    let result =
        crate::jobs::start_streamed(app.clone(), state, args, None, label.clone()).await;
    if let Err(err) = result {
        notify(app, &format!("{label}: {err}"));
    }
    // Ket qua thanh cong/that bai duoc bao qua event "job-done" ma webview
    // da lang nghe san (webview van song khi cua so bi an xuong tray ->
    // notification van hien duoc); o day chi can bao khi KHONG the spawn duoc
    // job (vd dang co job khac chay).
}

fn notify(app: &AppHandle, message: &str) {
    // User tat thong bao (About modal) -> im lang.
    if !app.state::<NotifyState>().0.load(Ordering::SeqCst) {
        return;
    }
    use tauri_plugin_notification::NotificationExt;
    let _ = app
        .notification()
        .builder()
        .title("SAP ABAP Agent")
        .body(message)
        .show();
}
