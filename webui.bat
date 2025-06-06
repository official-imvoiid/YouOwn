@echo off
cls
echo Starting Secure Media Downloader...

:: Set temporary PATH for FFmpeg executables
set "BASE_DIR=%cd%"
set "FFMPEG_DIR=%BASE_DIR%\FFmpeg"
set "PATH=%PATH%;%FFMPEG_DIR%"
:: Quick check for FFmpeg executables (silent)
for %%F in (ffmpeg.exe ffplay.exe ffprobe.exe) do (
    if not exist "%FFMPEG_DIR%\%%F" (
        echo ERROR: %%F not found in %FFMPEG_DIR%
        echo Please ensure FFmpeg executables are in FFmpeg folder.
        pause
        exit /b 1
    )
)

:: Quick Python check (silent)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

:: Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found in current directory.
    pause
    exit /b 1
)

:: Show status message
echo.
echo =========================================================
echo         Application Running Locally
echo ---------------------------------------------------------
echo   To stop the application: Close this window
echo   To open in browser: Ctrl + Right-Click the URL below
echo =========================================================

:: Start App
python app.py 