//! System tray icon + menu, tuong duong gui/tray.py (pystray) ben Python.
//!
//! Don gian hoa co chu dich so voi ban Python: bo submenu "Profiles" dong
//! (chon nhanh active profile tu tray) - Tauri tray menu duoc dung 1 lan luc
//! khoi tao, rebuild dong moi lan mo can them wiring event rieng; nguoi dung
//! van doi active profile binh thuong qua dropdown trong cua so chinh. Cac
//! muc con lai (Reauth/Connect active, License Dashboard, Open GUI, Quit)
//! giu nguyen hanh vi.

use crate::mcp_cli::run_json;
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Emitter, Manager};

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
    let reauth_item = MenuItem::with_id(app, "tray-reauth", "Reauth (active)", true, None::<&str>)?;
    let connect_item =
        MenuItem::with_id(app, "tray-connect", "Connect (active)", true, None::<&str>)?;
    let license_item = MenuItem::with_id(
        app,
        "tray-license",
        "Open License Dashboard...",
        true,
        None::<&str>,
    )?;
    let plugin_item =
        MenuItem::with_id(app, "tray-plugin", "Plugin / Check update...", true, None::<&str>)?;
    let open_item = MenuItem::with_id(app, "tray-open", "Open GUI", true, None::<&str>)?;
    let about_item = MenuItem::with_id(app, "tray-about", "About / Check update...", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "tray-quit", "Quit", true, None::<&str>)?;
    let separator = PredefinedMenuItem::separator(app)?;

    let menu = Menu::with_items(
        app,
        &[
            &reauth_item,
            &connect_item,
            &separator,
            &license_item,
            &plugin_item,
            &open_item,
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
                "tray-license" => {
                    show_main_window(&app);
                    let _ = app.emit("open-license-dashboard", ());
                }
                "tray-plugin" => {
                    show_main_window(&app);
                    let _ = app.emit("open-plugin-panel", ());
                }
                "tray-open" => show_main_window(&app),
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
    // Ket qua thanh cong/that bai duoc bao qua event "job-done" ma cua so
    // chinh (neu dang mo) da lang nghe san; o day chi can bao khi KHONG the
    // spawn duoc job (vd dang co job khac chay).
}

fn notify(app: &AppHandle, message: &str) {
    use tauri_plugin_notification::NotificationExt;
    let _ = app
        .notification()
        .builder()
        .title("SAP ABAP Agent")
        .body(message)
        .show();
}
