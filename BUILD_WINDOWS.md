# Windows build notes

These instructions are for the copyright holder and authorized contributors. See `LICENSE` before building or distributing EldhoAi.

## Build the portable folder

1. Install the project's Python dependencies with `python -m pip install -r requirements-build.txt`.
2. For a source run, copy `.env.example` to `.env` in the project root and fill in your own API keys. The build script copies `.env` into `%LOCALAPPDATA%\EldhoAi\.env` only if that per-user config file does not already exist. Never upload either file with secrets.
3. Keep `main.py`, all application modules, `EldhoAi.ico`, `rthook_eldhoai.py`, `prepare_portable_data.py`, and `build_eldhoai.bat` in the project root.
4. Run `.\build_eldhoai.bat` from the project root.
5. If successful, test `dist\EldhoAi\EldhoAi.exe` and all application features.

## Build the installer

1. Install Inno Setup.
2. Open `EldhoAi_Installer.iss` in Inno Setup Compiler.
3. Compile the script after the portable build succeeds.
4. Test the installed application, including model calls, data persistence, and configuration loading.
5. Before publishing, inspect the installer output and ensure no `.env`, personal data, logs, or credentials are included.

The installer targets a per-user directory under `%LOCALAPPDATA%\EldhoAi` and is designed not to require administrator privileges. Back up personal app data independently of upgrades or uninstalling.
