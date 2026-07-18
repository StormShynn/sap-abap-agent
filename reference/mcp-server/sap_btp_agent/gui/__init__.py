"""GUI cho sap-btp-agent: cua so Tkinter + system tray icon.

Su dung:
    sap-btp-agent-gui              # mo GUI + tray
    sap-btp-agent-gui --no-tray    # chi GUI
    sap-btp-agent-gui --tray-only  # chi tray (khong cua so)
"""
from __future__ import annotations

import argparse
import sys
import threading


def main() -> int:
    parser = argparse.ArgumentParser(prog="sap-btp-agent-gui")
    parser.add_argument("--no-tray", action="store_true",
                        help="Chi mo GUI, khong chay tray icon.")
    parser.add_argument("--tray-only", action="store_true",
                        help="Chi chay tray icon (khong cua so GUI).")
    args = parser.parse_args()

    if args.no_tray and args.tray_only:
        print("Khong the dung --no-tray va --tray-only cung luc.", file=sys.stderr)
        return 2

    if args.tray_only:
        # Tray-only mode
        from .tray import run_tray_only
        return run_tray_only()

    # Che do binh thuong: GUI + tray song song
    from .app import SapBtpGui
    from .tray import TrayController

    gui = SapBtpGui()
    tray = None
    if not args.no_tray:
        try:
            tray = TrayController(gui)
            gui.set_tray(tray)
            tray.start()
        except Exception as err:
            # Loi tray (thuong do thieu pystray/Pillow) -> van chay GUI
            print(f"  i Khong the khoi dong tray icon ({err}). GUI van chay binh thuong.",
                  file=sys.stderr)

    try:
        gui.run()
    finally:
        if tray is not None:
            try:
                tray.stop()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
