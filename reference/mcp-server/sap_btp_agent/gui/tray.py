"""System tray icon cho sap-btp-agent (pystray).

Tinh nang:
- Icon nam trong system tray (Windows: notification area).
- Menu chuot phai: Reauth active, Connect, Profiles (sub-menu), Open GUI, Quit.
- Double-click icon: toggle hien/an GUI.
- notify(message): hien balloon Windows (dung cho thong bao reauth xong).
- TrayController.start() khoi dong icon o 1 thread rieng.
- TrayController.stop() dung icon (goi khi app thoat).
"""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .app import SapBtpGui


# Pillow dung de ve icon 16x16 don gian (khong can file .ico rieng).
def _make_icon_image():
    """Tao icon 64x64: vong tron xanh + chu S trang."""
    from PIL import Image, ImageDraw, ImageFont
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Vong tron xanh
    draw.ellipse((4, 4, size - 4, size - 4), fill="#0078d4")
    # Chu "S" trang o giua
    try:
        font = ImageFont.truetype("segoeui.ttf", 36)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except Exception:
            font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "S", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
        "S", fill="white", font=font,
    )
    return img


class TrayController:
    """Dieu khien icon tray (pystray)."""

    def __init__(self, gui: "SapBtpGui"):
        self.gui = gui
        self._icon = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()

    def start(self) -> None:
        """Khoi dong tray icon (non-blocking).

        Ngay khi start, check license status cua cac profiles va notify 1 lan
        neu co profile sap het han (warning/expired).
        """
        # Check warning profiles TRUOC khi khoi dong icon
        try:
            from .. import license as _lic
            warnings = _lic.warning_profiles()
            for s in warnings[:3]:  # max 3 notification
                label = s["profile_id"]
                if s["is_expired"]:
                    self.notify(f"Cookie/token da HET HAN: {label}",
                                title="License expired")
                else:
                    self.notify(f"{label}: con {s['expires_in_human']} (sap het han)",
                                title="License warning")
        except Exception as err:
            pass  # khong anh huong start icon
        from pystray import Icon, Menu, MenuItem
        import pystray

        icon_img = _make_icon_image()
        self._icon = Icon(
            "sap-btp-agent",
            icon_img,
            title="SAP BTP Agent",
            menu=self._build_menu(),
        )

        # Gan callback double-click -> toggle GUI
        def on_activate(icon, item=None):
            self.gui.show_from_tray()
        # pystray: su dung default action (left click) la show
        try:
            self._icon.on_activate = on_activate
        except Exception:
            pass

        # Chay icon o thread rieng (pystray.Icon.run la blocking)
        def runner():
            try:
                self._icon.run()
            except Exception:
                pass

        self._thread = threading.Thread(target=runner, daemon=True, name="tray-icon")
        self._thread.start()

    def stop(self) -> None:
        """Dung tray icon."""
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass

    def notify(self, message: str, title: str = "SAP BTP Agent") -> None:
        """Hien balloon/toast notification."""
        if self._icon is None:
            return
        try:
            self._icon.notify(message, title=title)
        except Exception:
            pass

    def _build_menu(self):
        """Xay menu context - tao moi moi lan goi de profile list luon moi."""
        from pystray import Menu, MenuItem

        def get_profile_items():
            try:
                from ..config.profile import list_profiles, set_active_profile, get_current_active
                data = list_profiles()
                active = data.get("active")
                items = []
                for p in data.get("items", []):
                    pid = p["id"]
                    label = ("* " if pid == active else "  ") + pid
                    def make_setter(profile_id):
                        def action(icon, item):
                            try:
                                set_active_profile(profile_id)
                                self.notify(f"Active: {profile_id}")
                            except Exception as err:
                                self.notify(f"Loi: {err}")
                        return action
                    items.append(MenuItem(label, make_setter(pid)))
                return items
            except Exception:
                return [MenuItem("(khong doc duoc)", None, enabled=False)]

        def on_reauth(icon, item):
            # Reauth profile active
            from ..config.profile import get_current_active
            pid = get_current_active()
            if not pid:
                self.notify("Chua co profile active. Mo GUI de setup.")
                return
            # Spawn subprocess reauth, stream ra notify
            self._run_in_background(["reauth", pid])

        def on_connect(icon, item):
            from ..config.profile import get_current_active
            pid = get_current_active()
            if not pid:
                self.notify("Chua co profile active.")
                return
            self._run_in_background(["connect", pid])

        def on_open_gui(icon, item):
            self.gui.show_from_tray()

        def on_quit(icon, item):
            self.stop()
            # Thoat app luon
            try:
                self.gui.root.after(0, self.gui.root.destroy)
            except Exception:
                import sys
                sys.exit(0)

        def on_license(icon, item):
            self.gui._open_license_window()

        return Menu(
            MenuItem("Reauth (active)", on_reauth, default=True),
            MenuItem("Connect (active)", on_connect),
            MenuItem("Profiles", Menu(get_profile_items)),
            Menu.SEPARATOR,
            MenuItem("Open License Dashboard...", on_license),
            MenuItem("Open GUI", on_open_gui),
            MenuItem("Quit", on_quit),
        )

    def _run_in_background(self, args: list[str]) -> None:
        """Chay subprocess, stream output va notify khi xong."""
        from . import runner as r

        def on_line(line: str):
            # Push vao GUI log neu cua so dang mo
            try:
                self.gui._line_queue.put(("line", f"[tray] {line}"))
            except Exception:
                pass

        def on_done(rc: int):
            if rc == 0:
                self.notify(" ".join(args) + " OK")
            else:
                self.notify(" ".join(args) + f" that bai (rc={rc})")

        r.start(args, on_line=on_line, on_done=on_done)


def run_tray_only() -> int:
    """Che do chi chay tray (khong GUI). Dung cho may chay nen."""
    import queue
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()

    class _HiddenGui:
        """Fake GUI: chi expose _line_queue + show_from_tray (no-op) de tray
        co the goi ma khong crash khi khong co cua so that su."""
        def __init__(self, root):
            self.root = root
            self._line_queue = queue.Queue()

        def show_from_tray(self):
            # Tray-only mode khong co cua so -> chi thong bao user mo GUI.
            pass

    gui = _HiddenGui(root)
    tray = TrayController(gui)
    tray.start()

    try:
        root.mainloop()
    finally:
        tray.stop()
    return 0
