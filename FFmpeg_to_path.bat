@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo        Add FFmpeg to System PATH (All Users).
echo ======================================================
echo.

:: Get the full path to the FFmpeg directory
set "SCRIPT_DIR=%~dp0"
set "FFMPEG_DIR=%SCRIPT_DIR%FFmpeg"

:: Remove trailing backslash if any
if "%FFMPEG_DIR:~-1%" == "\" set "FFMPEG_DIR=%FFMPEG_DIR:~0,-1%"

:: Check if FFmpeg directory exists
if not exist "%FFMPEG_DIR%" (
    echo ERROR: FFmpeg folder not found at:
    echo %FFMPEG_DIR%
    echo.
    echo Please make sure the FFmpeg folder exists in the application directory.
    echo.
    pause
    exit /b 1
)

:: Check for ffmpeg.exe in the directory
if not exist "%FFMPEG_DIR%\ffmpeg.exe" (
    echo ERROR: ffmpeg.exe not found in:
    echo %FFMPEG_DIR%
    echo.
    echo Please make sure FFmpeg is correctly installed in the folder.
    echo.
    pause
    exit /b 1
)

echo FFmpeg found at: %FFMPEG_DIR%
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges.
    echo Please right-click on the script and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

:: Check if FFmpeg is already in System PATH
echo Checking current System PATH...
set "PATH_CONTAINS_FFMPEG="
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "SYS_PATH=%%B"
echo %SYS_PATH% | findstr /i /c:"%FFMPEG_DIR%" >nul && set "PATH_CONTAINS_FFMPEG=1"

if defined PATH_CONTAINS_FFMPEG (
    echo.
    echo FFmpeg is already in the system PATH!
    echo.
    pause
    exit /b 0
)

:: Add FFmpeg to system PATH
echo Adding FFmpeg to system PATH for all users...
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "CURRENT_PATH=%%B"
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "%CURRENT_PATH%;%FFMPEG_DIR%" /f

if %errorlevel% neq 0 (
    echo.
    echo Failed to update system PATH. Error code: %errorlevel%
    echo.
    pause
    exit /b 1
)

:: Notify the system of environment changes
echo Refreshing environment variables...
echo @echo off > "%TEMP%\refresh_env.bat"
echo echo Refreshing environment variables... >> "%TEMP%\refresh_env.bat"
echo rundll32 user32.dll,UpdatePerUserSystemParameters >> "%TEMP%\refresh_env.bat"
start /wait cmd /c "%TEMP%\refresh_env.bat"
del "%TEMP%\refresh_env.bat" 2>nul

echo.
echo FFmpeg has been successfully added to system PATH for all users!
echo.
echo You may need to restart any open applications or command prompts
echo for the PATH changes to take effect.
echo.
pause
