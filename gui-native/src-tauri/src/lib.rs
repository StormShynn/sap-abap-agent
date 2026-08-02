mod jobs;
mod mcp_cli;
mod plugin_cli;
mod tray;

use tauri::WindowEvent;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .manage(jobs::JobState::default())
        .invoke_handler(tauri::generate_handler![
            mcp_cli::check_runtime,
            mcp_cli::list_profiles,
            mcp_cli::get_license_statuses,
            mcp_cli::set_active_profile,
            mcp_cli::remove_profile,
            mcp_cli::import_json_backup,
            mcp_cli::mcp_status,
            mcp_cli::mcp_register,
            mcp_cli::mcp_unregister,
            mcp_cli::doctor_json,
            plugin_cli::plugin_status,
            plugin_cli::plugin_update,
            jobs::start_streamed,
            jobs::start_new_console,
            jobs::cancel_job,
            jobs::is_job_running,
            jobs::make_early_finish_path,
            jobs::touch_early_finish,
            jobs::cleanup_early_finish,
        ])
        .setup(|app| {
            tray::build_tray(app.handle())?;
            Ok(())
        })
        .on_window_event(|window, event| {
            // Dong cua so -> an xuong tray thay vi thoat that su (giong
            // _on_close_request ben Python) - Quit that su chi qua menu tray.
            if let WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = window.hide();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
