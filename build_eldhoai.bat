@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build EldhoAi for Windows

echo ============================================================
echo                 ELDHOAI WINDOWS BUILD
echo ============================================================
echo.

if not exist "main.py" (
    echo ERROR: main.py was not found.
    echo Extract this build kit into your EldhoAI project root,
    echo beside main.py, gui.py, brain.py, and the other source files.
    echo.
    pause
    exit /b 1
)

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

"%PYTHON_EXE%" -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not available in the selected Python environment.
    echo Install it with: python -m pip install pyinstaller
    echo.
    pause
    exit /b 1
)

if not exist "EldhoAi.ico" (
    echo ERROR: EldhoAi.ico is missing. Re-extract the build kit.
    echo.
    pause
    exit /b 1
)
if not exist "rthook_eldhoai.py" (
    echo ERROR: rthook_eldhoai.py is missing. Re-extract the build kit.
    echo.
    pause
    exit /b 1
)
if not exist "prepare_portable_data.py" (
    echo ERROR: prepare_portable_data.py is missing. Re-extract the build kit.
    echo.
    pause
    exit /b 1
)

set "APP_CONFIG=%LOCALAPPDATA%\EldhoAi"
if not exist "%APP_CONFIG%" mkdir "%APP_CONFIG%"

rem Keep secrets outside dist and outside the executable.
if not exist "%APP_CONFIG%\.env" (
    if exist ".env" (
        copy /Y ".env" "%APP_CONFIG%\.env" >nul
        echo Your existing .env was copied to the per-user config folder:
        echo %APP_CONFIG%\.env
    ) else (
        echo WARNING: No project .env was found.
        echo After building, create %APP_CONFIG%\.env with your API keys.
    )
) else (
    echo Existing per-user API configuration will be kept unchanged.
)

echo.
echo Building EldhoAi. This may take several minutes...
echo.

"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean --onedir --windowed --name EldhoAi --contents-directory . --icon "EldhoAi.ico" --runtime-hook "rthook_eldhoai.py" --collect-all customtkinter --collect-all PIL --collect-all openai --collect-all tavily --collect-all dotenv --collect-all pypdf --collect-all docx --collect-all riva --collect-all grpc --collect-all sounddevice --collect-all numpy --collect-all pyttsx3 --collect-all comtypes --collect-all certifi --hidden-import=pyttsx3.drivers.sapi5 --hidden-import=pythoncom --hidden-import=pywintypes --hidden-import=win32com.client --hidden-import=comtypes.client main.py
if errorlevel 1 (
    echo.
    echo BUILD FAILED. Review the error output above.
    echo If needed, send the final 30-50 lines of the PyInstaller log.
    echo Do not send your .env file or API keys.
    echo.
    pause
    exit /b 1
)

rem Preserve the user's existing settings, chat history, and image attachments.
if exist "data" (
    if not exist "dist\EldhoAi\data" mkdir "dist\EldhoAi\data"
    xcopy "data\*" "dist\EldhoAi\data\" /E /I /Y /Q >nul
    "%PYTHON_EXE%" "prepare_portable_data.py" "data" "dist\EldhoAi\data"
    if errorlevel 1 (
        echo WARNING: Saved image paths could not all be migrated.
    )
)

echo.
echo ============================================================
echo BUILD COMPLETE
echo ============================================================
echo.
echo Executable:
echo %~dp0dist\EldhoAi\EldhoAi.exe
echo.
echo Double-click EldhoAi.exe to launch the application.
echo.
echo IMPORTANT: API keys are kept separately in:
echo %APP_CONFIG%\.env
echo Do not publish or share that file.
echo.
echo This is a portable one-folder build. Keep the whole dist\EldhoAi

echo folder together and run it from a folder where you can write files.
echo.
pause
