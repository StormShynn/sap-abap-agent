import threading
from sap_btp_agent.gui.app import SapBtpGui

gui = SapBtpGui()
gui._tray = type("FakeTray", (), {"notify": lambda self, msg: None})()

print("btn_done text:", gui.btn_done.cget("text"))
print("btn_done state (initial):", str(gui.btn_done.cget("state")))

# Mo phong bam nut OK
def fake_touch():
    from pathlib import Path
    Path(gui._early_finish_file).touch()
    print("[gui] touched file:", gui._early_finish_file)
    gui.btn_done.configure(state="disabled")

# Set up marker file de test touch
import tempfile, os
fd, p = tempfile.mkstemp(prefix="sap_early_test_", suffix=".path")
os.close(fd)
os.unlink(p)
gui._early_finish_file = p
gui.btn_done.configure(state="normal")

print("btn_done state (after enable):", str(gui.btn_done.cget("state")))

# Click button programmatically (via invoke)
gui.btn_done.invoke()
print("After click:")
print("  btn_done state:", str(gui.btn_done.cget("state")))
print("  file exists:", os.path.exists(p))

gui.root.after(200, gui.root.destroy)
gui.run()
print("OK")
