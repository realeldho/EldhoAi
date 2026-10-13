"""PyInstaller runtime hook for EldhoAi.

Load API keys from the per-user configuration file, outside the executable.
Also create a startup log and show a dialog for fatal startup exceptions in
windowed builds, where no console is attached.
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def _user_config_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = str(Path.home() / "AppData" / "Local")
    path = Path(local_app_data) / "EldhoAi"
    path.mkdir(parents=True, exist_ok=True)
    return path


_USER_CONFIG_DIR = _user_config_dir()
os.environ.setdefault("ELDHOAI_USER_CONFIG_DIR", str(_USER_CONFIG_DIR))

# .env is deliberately not bundled into EldhoAi.exe.
try:
    from dotenv import load_dotenv
    env_file = _USER_CONFIG_DIR / ".env"
    if env_file.is_file():
        load_dotenv(dotenv_path=env_file, override=False)
except Exception:
    # The main application will show a friendly missing-key message if needed.
    pass


def _fatal_exception_hook(exc_type, exc_value, exc_traceback):
    try:
        logs_dir = _USER_CONFIG_DIR / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "startup_error.log"
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write("\n--- EldhoAi startup/runtime error ---\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=handle)
    except Exception:
        pass

    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "EldhoAi could not continue",
            "EldhoAi encountered an unexpected error.\n\n"
            "A diagnostic log was saved to:\n"
            + str(_USER_CONFIG_DIR / "logs" / "startup_error.log"),
            parent=root,
        )
        root.destroy()
    except Exception:
        pass


sys.excepthook = _fatal_exception_hook
