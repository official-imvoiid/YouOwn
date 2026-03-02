@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       Secure Media Downloader - Upgrader
echo ========================================================
echo.

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in current directory.
    echo Please ensure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

echo Upgrading all packages from requirements.txt...
echo Please wait...
echo.

:: Upgrade all packages with --upgrade flag
python -m pip install -r requirements.txt --upgrade
set PIP_ERROR=%errorlevel%

if %PIP_ERROR% neq 0 (
    echo.
    echo ERROR: Failed to upgrade packages.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo             Upgrade Complete!
echo ======================================================
echo.
pause
