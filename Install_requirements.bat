@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo       Secure Media Downloader - Dependencies Installer
echo ========================================================
echo.

:: Check if Python is installed
echo Checking for Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8 or newer from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Get and validate Python version
echo Detecting Python version...
python --version >temp_version.txt 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Unable to get Python version.
    if exist temp_version.txt del temp_version.txt
    pause
    exit /b 1
)

:: Parse Python version more reliably
for /f "tokens=2 delims= " %%i in (temp_version.txt) do set PYTHON_VERSION=%%i
del temp_version.txt

if "!PYTHON_VERSION!"=="" (
    echo ERROR: Could not detect Python version.
    pause
    exit /b 1
)

echo Detected Python !PYTHON_VERSION!

:: Extract major and minor version numbers for validation
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

:: Check if Python version is 3.8 or newer
if !PYTHON_MAJOR! lss 3 (
    echo ERROR: Python !PYTHON_VERSION! is too old. Please install Python 3.8 or newer.
    pause
    exit /b 1
)
if !PYTHON_MAJOR! equ 3 if !PYTHON_MINOR! lss 8 (
    echo ERROR: Python !PYTHON_VERSION! is too old. Please install Python 3.8 or newer.
    pause
    exit /b 1
)

echo Python version is compatible.

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in current directory.
    echo Please ensure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

:: Check if pip is available
echo Checking for pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not available. Attempting to install pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install pip. Please install pip manually.
        pause
        exit /b 1
    )
    echo Pip installed successfully.
)

echo.
echo Updating pip to latest version...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip, but continuing with installation...
    echo You may want to upgrade pip manually later.
) else (
    echo Pip updated successfully.
)

echo.
echo Installing required packages from requirements.txt...
echo This may take a few minutes depending on your internet connection.
echo Please wait...
echo.

:: Install requirements with better error handling
python -m pip install -r requirements.txt --upgrade
set PIP_ERROR=%errorlevel%

if %PIP_ERROR% neq 0 (
    echo.
    echo ERROR: Failed to install Python dependencies.
    echo Please check:
    echo - Your internet connection
    echo - You have necessary permissions
    echo - requirements.txt is not corrupted
    echo.
    echo You can try running this command manually:
    echo python -m pip install -r requirements.txt --upgrade
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo             Installation Complete!
echo ======================================================
echo.
echo You can now run the application using webui.bat
echo.
pause
