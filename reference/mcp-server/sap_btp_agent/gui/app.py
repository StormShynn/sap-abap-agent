"""GUI chinh cho sap-btp-agent (Tkinter).

Cau truc:
  +---------------------------------------------------------------+
  | Profile: [project1.s4hana.cloud.sap      v] [Refresh] [+ New] |
  | URL:     https://project1.s4hana.cloud.sap                     |
  +---------------------------------------------------------------+
  | [   Reauth   ] [   Connect   ] [   Set Active   ] [   Remove ] |
  +---------------------------------------------------------------+
  | Log:                                                            |
  | +-----------------------------------------------------------+ |
  | |  ... lines streamed from sap-btp-agent ...               | |
  | +-----------------------------------------------------------+ |
  | [Clear] [Copy]                          [Status: idle / busy] |
  +---------------------------------------------------------------+
"""
from __future__ import annotations

import queue
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from .. import license as _lic
from ..config.profile import (
    list_profiles,
    set_active_profile,
)
from ..config.profile import (
    remove_profile as remove_profile_registry,
)
from . import runner

# Mau sac (Tone Windows 11-ish)
COLOR_BG = "#f3f3f3"
COLOR_CARD = "#ffffff"
COLOR_ACCENT = "#0078d4"
COLOR_ACCENT_HOVER = "#106ebe"
COLOR_DANGER = "#d83b01"
COLOR_TEXT = "#1f1f1f"
COLOR_MUTED = "#605e5c"


class SapBtpGui:
    """Cua so GUI chinh."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SAP BTP Agent")
        self.root.geometry("780x560")
        self.root.minsize(640, 460)
        self.root.configure(bg=COLOR_BG)

        # Tray reference (set sau khi TrayController khoi dong)
        self._tray: Any | None = None

        # Job hien tai (1 tien trinh subprocess chay 1 luc)
        self._job: runner.Job | None = None
        # Early-finish marker file (GUI tao file de CLI subprocess phat hien
        # user bam nut "✓ Đa xong" trong GUI).
        self._early_finish_file = None

        # Queue truyen dong tu worker thread -> GUI thread (Tkinter mainloop)
        self._line_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        # moi entry: (kind, text); kind in {"line", "done"}

        # Live countdown: profile_id hien tai dang select (None neu khong co)
        self._countdown_pid: str | None = None
        # Vi tri dang chon trong combo (de update label sau khi _refresh_profiles)
        self._selected_idx: int = -1

        self._build_ui()
        self._refresh_profiles()
        self._poll_queue()
        # Bat dau countdown loop (moi giay update license label neu can)
        self._tick_countdown()

        # Dong cua so -> an xuong tray neu co
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_request)

    # ===== UI construction ==========================================

    def _build_ui(self) -> None:
        # === Header: profile selector ===
        header = tk.Frame(self.root, bg=COLOR_BG, padx=16, pady=12)
        header.pack(fill="x")

        tk.Label(
            header, text="Profile:", font=("Segoe UI", 10, "bold"),
            bg=COLOR_BG, fg=COLOR_TEXT,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(
            header, textvariable=self.profile_var, state="readonly",
            width=42, font=("Segoe UI", 10),
        )
        self.profile_combo.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_changed)
        header.columnconfigure(1, weight=1)

        tk.Button(
            header, text="Refresh", command=self._refresh_profiles,
            font=("Segoe UI", 9), relief="flat", padx=12,
        ).grid(row=0, column=2, padx=(0, 4))

        # Nut + Add: menu thả xuống cho cac tac vu them profile moi.
        self.add_btn = tk.Menubutton(
            header, text="+ Add", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, pady=4,
            bg=COLOR_ACCENT, fg="white",
            activebackground=COLOR_ACCENT_HOVER, activeforeground="white",
            borderwidth=0, indicatoron=False,
        )
        self.add_btn.grid(row=0, column=3)
        add_menu = tk.Menu(self.add_btn, tearoff=0)
        add_menu.add_command(label="Setup wizard (interactive)...", command=self._on_new_setup)
        add_menu.add_command(label="Import from JSON backup...", command=self._on_import_json)
        self.add_btn.configure(menu=add_menu)

        # URL label
        self.url_var = tk.StringVar(value="(no profile selected)")
        tk.Label(
            header, textvariable=self.url_var, font=("Segoe UI", 9),
            bg=COLOR_BG, fg=COLOR_MUTED, anchor="w",
        ).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6, 0))

        # License status label (dong thu 2)
        self.license_var = tk.StringVar(value="")
        self.license_label = tk.Label(
            header, textvariable=self.license_var, font=("Segoe UI", 9, "bold"),
            bg=COLOR_BG, fg=COLOR_MUTED, anchor="w", cursor="hand2",
        )
        self.license_label.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(2, 0))
        self.license_label.bind("<Button-1>", lambda e: self._open_license_window())

        # Nut License (góc phai)
        tk.Button(
            header, text="📋 License", command=self._open_license_window,
            font=("Segoe UI", 9), relief="flat", padx=10,
        ).grid(row=2, column=3, sticky="e", pady=(2, 0))

        # === Quick actions ===
        actions = tk.Frame(self.root, bg=COLOR_BG, padx=16, pady=4)
        actions.pack(fill="x")

        self.btn_reauth = self._make_action_button(
            actions, "🔐\nReauth", self._on_reauth,
        )
        self.btn_connect = self._make_action_button(
            actions, "🔌\nConnect", self._on_connect,
        )
        self.btn_active = self._make_action_button(
            actions, "⭐\nSet Active", self._on_set_active,
        )
        self.btn_remove = self._make_action_button(
            actions, "🗑\nRemove", self._on_remove,
            danger=True,
        )
        for col, btn in enumerate([self.btn_reauth, self.btn_connect,
                                   self.btn_active, self.btn_remove]):
            btn.grid(row=0, column=col, sticky="ew", padx=4, pady=4)
            actions.columnconfigure(col, weight=1)

        # === Log console ===
        log_frame = tk.Frame(self.root, bg=COLOR_BG, padx=16, pady=8)
        log_frame.pack(fill="both", expand=True)

        tk.Label(
            log_frame, text="Log:", font=("Segoe UI", 10, "bold"),
            bg=COLOR_BG, fg=COLOR_TEXT, anchor="w",
        ).pack(anchor="w")

        log_inner = tk.Frame(log_frame, bg=COLOR_CARD,
                             highlightbackground="#cccccc",
                             highlightthickness=1)
        log_inner.pack(fill="both", expand=True, pady=(4, 0))

        scroll = tk.Scrollbar(log_inner)
        scroll.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_inner, wrap="word", yscrollcommand=scroll.set,
            font=("Consolas", 9), bg=COLOR_CARD, fg=COLOR_TEXT,
            borderwidth=0, highlightthickness=0, padx=8, pady=8,
            state="disabled",
        )
        self.log_text.pack(fill="both", expand=True)
        scroll.config(command=self.log_text.yview)

        # Log toolbar
        log_tools = tk.Frame(log_frame, bg=COLOR_BG)
        log_tools.pack(fill="x", pady=(4, 0))
        tk.Button(
            log_tools, text="Clear", command=self._clear_log,
            font=("Segoe UI", 9), relief="flat", padx=10,
        ).pack(side="left")
        tk.Button(
            log_tools, text="Copy", command=self._copy_log,
            font=("Segoe UI", 9), relief="flat", padx=10,
        ).pack(side="left", padx=(4, 0))

        # Nut "OK da xong": chi enable khi dang trong reauth auto mode.
        # Bấm -> subprocess set early_event -> web_login_auto ket thuc som.
        self.btn_done = tk.Button(
            log_tools, text="✓ Đã đăng nhập xong",
            command=self._on_done_clicked,
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10,
            bg="#107c10", fg="white",
            activebackground="#0b5a0b", activeforeground="white",
            borderwidth=0, state="disabled",
        )
        self.btn_done.pack(side="left", padx=(12, 0))

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            log_tools, textvariable=self.status_var,
            font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_MUTED,
        ).pack(side="right")

    def _make_action_button(self, parent, text, command, danger=False):
        bg = COLOR_DANGER if danger else COLOR_ACCENT
        hover = "#a52a00" if danger else COLOR_ACCENT_HOVER
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 10, "bold"),
            bg=bg, fg="white", activebackground=hover,
            activeforeground="white", borderwidth=0,
            relief="flat", padx=12, pady=14, height=2,
        )

    # ===== Profile management =======================================

    def _refresh_profiles(self) -> None:
        try:
            data = list_profiles()
        except Exception as err:
            messagebox.showerror("Error", f"Khong doc duoc profile registry:\n{err}")
            return
        items = data.get("items", [])
        active = data.get("active")

        self._profiles = items
        self._active_id = active

        # Build label voi badge license status.
        self._profile_labels = []  # list of (id, display_label)
        for p in items:
            marker = "* " if p["id"] == active else "  "
            try:
                st = _lic.get_profile_status(p["id"])
                badge = self._format_badge(st)
            except Exception:
                badge = ""
            label = f'{marker}{p["id"]}  {badge}'.rstrip()
            self._profile_labels.append((p["id"], label))
        self.profile_combo["values"] = [lbl for _, lbl in self._profile_labels]

        # Chon profile active neu co
        if active and active in [p["id"] for p in items]:
            idx = [p["id"] for p in items].index(active)
            self.profile_combo.current(idx)
            self.url_var.set(items[idx].get("url", "(no URL)"))
        elif items:
            self.profile_combo.current(0)
            self.url_var.set(items[0].get("url", "(no URL)"))
        else:
            self.profile_combo.set("")
            self.url_var.set("(chua co profile nao - bam '+ New' de setup)")

        self._set_buttons_state()

    def _on_profile_changed(self, _event=None) -> None:
        idx = self.profile_combo.current()
        self._selected_idx = idx
        if 0 <= idx < len(self._profiles):
            p = self._profiles[idx]
            self.url_var.set(p.get("url", "(no URL)"))
            self._countdown_pid = p["id"]
            self._update_license_label(p["id"])
        else:
            self._countdown_pid = None

    def _tick_countdown(self) -> None:
        """Update license label moi giay de hien thi countdown real-time."""
        if self._countdown_pid:
            try:
                self._update_license_label(self._countdown_pid)
            except Exception:
                pass
        # Reschedule sau 1s (1000ms)
        self.root.after(1000, self._tick_countdown)

    def _update_license_label(self, profile_id: str) -> None:
        """Update label dưới URL với trạng thái cookie/token."""
        try:
            st = _lic.get_profile_status(profile_id)
            if not st["has_credentials"]:
                txt = "🔓 No credentials saved"
                color = COLOR_MUTED
            elif st["is_expired"]:
                txt = f"❌ Expired ({st['expires_in_human']}) - run Reauth"
                color = COLOR_DANGER
            elif st["is_warning"]:
                txt = f"⚠ Expiring soon: {st['expires_in_human']} remaining"
                color = "#ca5010"  # cam
            else:
                txt = f"✓ OK: {st['expires_in_human']} remaining"
                color = "#107c10"  # xanh
        except Exception as err:
            txt = f"⚠ Cannot read license info: {err}"
            color = COLOR_MUTED
        self.license_var.set(txt)
        self.license_label.configure(fg=color)

    @staticmethod
    def _format_badge(st: dict) -> str:
        """Tra ve badge ngan cho combo label."""
        if not st["has_credentials"]:
            return "🔓"
        if st["is_expired"]:
            return "❌"
        if st["is_warning"]:
            return f"⚠ {st['expires_in_human']}"
        return f"✓ {st['expires_in_human']}"

    def _selected_profile_id(self) -> str | None:
        idx = self.profile_combo.current()
        if 0 <= idx < len(self._profiles):
            return self._profiles[idx]["id"]
        return None

    def _set_buttons_state(self, busy: bool = False) -> None:
        state = "disabled" if busy else "normal"
        has_profile = bool(self._selected_profile_id())
        for btn in [self.btn_reauth, self.btn_connect, self.btn_active, self.btn_remove]:
            btn.configure(state=state if has_profile else "disabled")

    # ===== Action handlers ==========================================

    def _on_new_setup(self) -> None:
        """Mo cua so CMD moi chay wizard setup (vi can interactive nhap nhieu thu)."""
        if self._job is not None and self._job.running:
            messagebox.showinfo("Busy", "Hay doi lenh hien tai ket thuc truoc.")
            return

        # Hoi URL SAP (optional). Neu user nhap -> chay wizard voi URL san,
        # neu bo trong -> wizard tu hoi trong CMD moi.
        url = None
        try:
            url = tk.simpledialog.askstring(
                "Setup new profile",
                "Nhap URL SAP (bo trong de wizard tu hoi):\n"
                "VD: https://project1.s4hana.cloud.sap",
                parent=self.root,
            )
        except Exception:
            url = None

        args = ["setup"]
        if url and url.strip():
            args.append(url.strip())

        self._append_log(f"$ sap-btp-agent {' '.join(args)}  (mo cua so CMD moi)\n")
        runner.start_new_console(args, on_done=self._on_setup_done)
        self.status_var.set("Setup dang chay (cua so CMD rieng)...")
        self._notify_tray("Setup dang chay trong cua so CMD rieng.")

    def _on_import_json(self) -> None:
        """Import profile tu file config.json backup (BTW: khong import secrets vi
        secrets.json da ma hoa DPAPI, chi may cua user moi giai ma duoc)."""
        from tkinter import filedialog

        from ..config.profile import derive_profile_id_from_url

        path = filedialog.askopenfilename(
            title="Chon file config.json de import",
            parent=self.root,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return

        # Doc file JSON
        try:
            import json
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as err:
            messagebox.showerror("Import failed", f"Khong doc duoc file JSON:\n{err}")
            return

        if not isinstance(data, dict):
            messagebox.showerror("Import failed", "File JSON khong phai dang object.")
            return

        url = data.get("btpUrl")
        if not url:
            messagebox.showinfo(
                "Import",
                "Vui long chon file config.json (chua truong btpUrl).\n"
                "File secrets.json khong the import vi da ma hoa DPAPI.",
            )
            return

        pid = derive_profile_id_from_url(url)
        if not pid:
            messagebox.showerror("Import failed", f"Khong suy ra duoc profile id tu URL: {url}")
            return

        # Goi CLI de dang ky profile (se copy file vao app_dir)
        from ..config.profile import upsert_profile
        try:
            upsert_profile(pid, url=url)
        except Exception as err:
            messagebox.showerror("Import failed", str(err))
            return

        messagebox.showinfo(
            "Import OK",
            f"Da dang ky profile: {pid}\n"
            f"URL: {url}\n\n"
            "Tiep theo hay copy secrets.json vao:\n"
            f"  %APPDATA%\\Python\\Python314\\site-packages\\sap_btp_agent\\profiles\\{pid}\\",
        )
        self._refresh_profiles()
        self._notify_tray(f"Da import profile: {pid}")

    def _on_setup_done(self, rc: int) -> None:
        def update():
            if rc == 0:
                self.status_var.set("Setup hoan tat - profile moi co the da duoc them.")
                self._append_log("[setup] hoan tat, dang refresh...\n")
                self._refresh_profiles()
                self._notify_tray("Setup thanh cong.")
            else:
                self.status_var.set(f"Setup that bai (rc={rc}).")
                self._notify_tray(f"Setup that bai (rc={rc}).")
        self.root.after(0, update)

    def _on_reauth(self) -> None:
        pid = self._selected_profile_id()
        if not pid:
            return
        if self._job is not None and self._job.running:
            messagebox.showinfo("Busy", "Hay doi lenh hien tai ket thuc truoc.")
            return

        # Tao file marker de CLI subprocess watch va set asyncio.Event khi user bam nut.
        # File duoc tao TRUOC khi spawn subprocess; subprocess watch no.
        # Neu user khong bam nut -> file khong duoc touch -> subprocess van doi 30s.
        import os as _os
        import tempfile as _tf
        fd, mpath = _tf.mkstemp(prefix="sap_early_", suffix=".path")
        _os.close(fd)
        # Xoa file ngay - chi giu PATH. CLI tao asyncio.Event va watch path.
        _os.unlink(mpath)
        self._early_finish_file = mpath
        _os.environ["SAP_BTP_EARLY_FINISH_FILE"] = mpath

        # Enable nut OK
        self.btn_done.configure(state="normal")

        self._append_log(f"$ sap-btp-agent reauth {pid}\n")
        self._set_buttons_state(busy=True)
        self.status_var.set("Dang dang nhap lai...")

        # Spawn subprocess voi env SAP_BTP_EARLY_FINISH_FILE
        self._job = runner.start(
            ["reauth", pid],
            on_line=lambda line: self._line_queue.put(("line", line)),
            on_done=lambda rc: self._line_queue.put(("done", f"reauth rc={rc}")),
            env_extra={"SAP_BTP_EARLY_FINISH_FILE": mpath},
        )

    def _on_connect(self) -> None:
        pid = self._selected_profile_id()
        if not pid:
            return
        if self._job is not None and self._job.running:
            messagebox.showinfo("Busy", "Hay doi lenh hien tai ket thuc truoc.")
            return

        self._append_log(f"$ sap-btp-agent connect {pid}\n")
        self._set_buttons_state(busy=True)
        self.status_var.set("Dang test ket noi...")

        self._job = runner.start(
            ["connect", pid],
            on_line=lambda line: self._line_queue.put(("line", line)),
            on_done=lambda rc: self._line_queue.put(("done", f"connect rc={rc}")),
        )

    def _on_set_active(self) -> None:
        pid = self._selected_profile_id()
        if not pid:
            return
        try:
            set_active_profile(pid)
        except Exception as err:
            messagebox.showerror("Error", str(err))
            return
        self._append_log(f"[OK] Da set '{pid}' lam profile active.\n")
        self.status_var.set(f"Active: {pid}")
        self._refresh_profiles()
        self._notify_tray(f"Profile active: {pid}")

    def _on_remove(self) -> None:
        pid = self._selected_profile_id()
        if not pid:
            return
        if not messagebox.askyesno(
            "Xoa profile?",
            f"Ban co chac muon xoa profile '{pid}'?\n"
            f"(se xoa config.json + secrets.json cua profile nay)",
            parent=self.root,
        ):
            return
        try:
            remove_profile_registry(pid)
        except Exception as err:
            messagebox.showerror("Error", str(err))
            return
        self._append_log(f"[OK] Da xoa profile '{pid}'.\n")
        self._refresh_profiles()
        self._notify_tray(f"Da xoa profile '{pid}'.")

    # ===== Log helpers ==============================================

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _copy_log(self) -> None:
        content = self.log_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)

    # ===== Queue pump (worker thread -> main thread) ================

    def _poll_queue(self) -> None:
        try:
            while True:
                kind, payload = self._line_queue.get_nowait()
                if kind == "line":
                    self._append_log(payload + "\n")
                elif kind == "done":
                    # payload vi du "reauth rc=0"
                    self._on_job_done(payload)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_queue)

    def _open_license_window(self) -> None:
        """Mo Toplevel dashboard hien thi license status cua tat ca profiles.

        Moi profile 1 row: [name + progressbar + countdown text].
        Progressbar update moi giay de hien thi % thoi gian con lai.
        Color-coded: xanh > 20%, cam 5-20%, do < 5%.
        """
        if hasattr(self, "_license_win") and self._license_win is not None:
            try:
                if self._license_win.winfo_exists():
                    self._license_win.lift()
                    self._license_win.focus_force()
                    return
            except Exception:
                pass

        win = tk.Toplevel(self.root)
        win.title("License Dashboard - SAP BTP Agent")
        win.geometry("720x460")
        win.configure(bg=COLOR_BG)
        self._license_win = win

        tk.Label(
            win, text="License / Credentials Status (auto-refresh 1s)",
            font=("Segoe UI", 12, "bold"), bg=COLOR_BG, fg=COLOR_TEXT,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Refresh + Close buttons
        btn_frame = tk.Frame(win, bg=COLOR_BG)
        btn_frame.pack(fill="x", padx=16)
        tk.Button(
            btn_frame, text="Refresh", command=lambda: self._refresh_license_dashboard(win),
            font=("Segoe UI", 9), relief="flat", padx=10,
        ).pack(side="left")
        tk.Button(
            btn_frame, text="Close", command=win.destroy,
            font=("Segoe UI", 9), relief="flat", padx=10,
        ).pack(side="right")

        # Scrollable row container
        container = tk.Frame(win, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=16, pady=(8, 8))

        canvas = tk.Canvas(container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        rows_frame = tk.Frame(canvas, bg=COLOR_BG)
        canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        rows_frame.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        win._rows_frame = rows_frame
        win._row_widgets = []  # list of {pid, label, progress, countdown, ...}

        # Build initial rows
        self._refresh_license_dashboard(win)

        # Tick moi 1s de update countdown
        def _tick_dashboard():
            try:
                self._tick_dashboard_rows(win)
            except Exception:
                pass
            try:
                if win.winfo_exists():
                    win.after(1000, _tick_dashboard)
            except Exception:
                pass

        win.after(1000, _tick_dashboard)
        win._cancel_tick = lambda: None  # tk auto-cancel when widget destroyed
        win.protocol("WM_DELETE_WINDOW",
                     lambda: (setattr(self, "_license_win", None), win.destroy()))

    def _refresh_license_dashboard(self, win: tk.Toplevel) -> None:
        """Tao lai cac row trong dashboard (goi khi user bam Refresh hoac moi mo)."""
        try:
            statuses = _lic.list_all_statuses()
        except Exception as err:
            messagebox.showerror("Error", f"Khong the doc license status: {err}", parent=win)
            return
        rows_frame = getattr(win, "_rows_frame", None)
        if rows_frame is None:
            return

        # Clear existing rows
        for w in win._row_widgets:
            w["frame"].destroy()
        win._row_widgets = []

        if not statuses:
            tk.Label(
                rows_frame, text="(chua co profile nao - chay: sap-btp-agent setup <url>)",
                font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_MUTED,
            ).pack(anchor="w", padx=8, pady=8)
            return

        import datetime as _dt
        for s in statuses:
            row = tk.Frame(rows_frame, bg=COLOR_CARD,
                           highlightbackground="#cccccc", highlightthickness=1)
            row.pack(fill="x", padx=4, pady=4)

            # Header: profile name + active marker
            marker = "★ " if s.get("is_active") else "  "
            header_lbl = tk.Label(
                row, text=f"{marker}{s['profile_id']}  ({s['type']})",
                font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT, anchor="w",
            )
            header_lbl.pack(fill="x", padx=10, pady=(6, 2))

            # Progress bar
            pb_frame = tk.Frame(row, bg=COLOR_CARD)
            pb_frame.pack(fill="x", padx=10, pady=2)
            pb = ttk.Progressbar(pb_frame, length=400, mode="determinate", maximum=100, value=0)
            pb.pack(side="left", fill="x", expand=True)

            countdown_lbl = tk.Label(
                pb_frame, text="", font=("Consolas", 10, "bold"),
                bg=COLOR_CARD, fg=COLOR_TEXT, width=18, anchor="w",
            )
            countdown_lbl.pack(side="left", padx=(10, 0))

            # Detail line: saved_at + extra
            saved_at = s.get("last_saved")
            saved_txt = (_dt.datetime.fromtimestamp(saved_at).strftime("%Y-%m-%d %H:%M:%S")
                         if saved_at else "(never)")
            extra = s.get("extra", {})
            if s["type"] == "cookie":
                extra_txt = f"{len(extra.get('session_cookies', []))} session / {extra.get('total_cookies', 0)} total"
            elif s["type"] == "oauth2":
                extra_txt = (extra.get("token_endpoint") or "?")[:50]
            else:
                extra_txt = ""

            detail_lbl = tk.Label(
                row, text=f"Saved: {saved_txt}    {extra_txt}",
                font=("Segoe UI", 8), bg=COLOR_CARD, fg=COLOR_MUTED, anchor="w",
            )
            detail_lbl.pack(fill="x", padx=10, pady=(2, 6))

            win._row_widgets.append({
                "frame": row,
                "progress": pb,
                "countdown": countdown_lbl,
                "status": s,
                "expires_at": s.get("expires_at"),
                "last_saved": saved_at,
            })

        # Initial tick
        self._tick_dashboard_rows(win)

    def _tick_dashboard_rows(self, win: tk.Toplevel) -> None:
        """Update progressbar + countdown cho moi profile trong dashboard."""
        import time as _t
        now = _t.time()
        for w in win._row_widgets:
            expires_at = w["expires_at"]
            last_saved = w["last_saved"]
            if not expires_at:
                # Khong co expires -> set 0%, label "unknown"
                w["progress"]["value"] = 0
                w["countdown"].configure(text="unknown", fg=COLOR_MUTED)
                continue

            # Tinh % con lai dua tren (expires_at - last_saved) gia su la max_age
            # Neu khong co last_saved -> uoc luong = 8h
            if last_saved:
                max_age = expires_at - last_saved
            else:
                max_age = 8 * 3600
            if max_age <= 0:
                max_age = 1
            remaining = max(0, expires_at - now)
            pct = min(100, max(0, (remaining / max_age) * 100))
            w["progress"]["value"] = pct

            # Color theo %
            from sap_btp_agent.license import format_expires_in_human
            text = format_expires_in_human(expires_at)
            if pct <= 0 or pct < 5:
                w["countdown"].configure(text=text, fg=COLOR_DANGER)
            elif pct < 20:
                w["countdown"].configure(text=text, fg="#ca5010")
            else:
                w["countdown"].configure(text=text, fg="#107c10")

    def _on_done_clicked(self) -> None:
        """User bam nut OK trong GUI -> touch file marker.

        Subprocess CLI dang watch file SAP_BTP_EARLY_FINISH_FILE; khi file duoc
        touch, no set asyncio.Event va web_login_auto ket thuc som.
        """
        from pathlib import Path as _P
        if self._early_finish_file:
            _P(self._early_finish_file).touch()
            self._append_log("[gui] ✓ Đa bam nut OK - yeu cau subprocess ket thuc som...\n")
            self.btn_done.configure(state="disabled")

    def _reset_early_finish(self) -> None:
        """Disable nut OK + clear marker khi subprocess xong."""
        self.btn_done.configure(state="disabled")
        if self._early_finish_file:
            try:
                import os as _os
                _os.unlink(self._early_finish_file)
            except OSError:
                pass
            self._early_finish_file = None

    def _on_job_done(self, summary: str) -> None:
        self._reset_early_finish()
        self._set_buttons_state(busy=False)
        # summary dang "reauth rc=0"
        try:
            cmd, rest = summary.split(" ", 1)
            rc = int(rest.split("=")[1])
        except Exception:
            cmd, rc = summary, -1

        self._append_log(f"\n[exit {cmd} rc={rc}]\n\n")
        self.status_var.set(f"{cmd}: rc={rc}")
        self._job = None
        if rc == 0:
            self._notify_tray(f"{cmd} thanh cong.")
        else:
            self._notify_tray(f"{cmd} that bai (rc={rc}).")

    # ===== Tray integration =========================================

    def set_tray(self, tray) -> None:
        self._tray = tray

    def _notify_tray(self, message: str) -> None:
        if self._tray is not None:
            try:
                self._tray.notify(message)
            except Exception:
                pass

    def hide_to_tray(self) -> None:
        """An cua so xuong system tray (goi tu tray khi user click Close)."""
        self.root.withdraw()

    def show_from_tray(self) -> None:
        """Hien lai cua so tu tray."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    # ===== Close handling ===========================================

    def _on_close_request(self) -> None:
        if self._job is not None and self._job.running:
            if not messagebox.askyesno(
                "Confirm exit",
                "Co lenh dang chay. Ban co chac muon thoat?\n"
                "(lenh se bi terminate)",
                parent=self.root,
            ):
                return
            try:
                self._job.cancel()
            except Exception:
                pass

        if self._tray is not None:
            # An xuong tray thay vi exit that su
            self.hide_to_tray()
            self._notify_tray("Sap-btp-agent van chay (click icon de mo lai).")
        else:
            self.root.destroy()

    # ===== Entry point ==============================================

    def run(self) -> None:
        self.root.mainloop()
