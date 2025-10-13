@echo off
REM ==========================================
REM Tesseract and Poppler Setup for Windows
REM ==========================================
echo.
echo FAI PDF Processor - Dependency Setup
echo ==========================================
echo.

setlocal enabledelayedexpansion

REM Define installation directories
set "INSTALL_DIR=%ProgramFiles%\FAI_Processor_Dependencies"
set "TESSERACT_DIR=%INSTALL_DIR%\Tesseract-OCR"
set "POPPLER_DIR=%INSTALL_DIR%\poppler"

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Not running as administrator.
    echo Some installation steps may fail.
    echo Please right-click and "Run as Administrator" for best results.
    echo.
    pause
)

REM ==========================================
REM Check and Install Tesseract
REM ==========================================
echo Checking for Tesseract OCR...
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract is already installed and in PATH
    tesseract --version
) else (
    echo [!] Tesseract not found in PATH
    
    REM Check common installation locations
    set "TESSERACT_FOUND="
    for %%P in (
        "%ProgramFiles%\Tesseract-OCR\tesseract.exe"
        "%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe"
        "%TESSERACT_DIR%\tesseract.exe"
        "C:\Program Files\Tesseract-OCR\tesseract.exe"
        "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ) do (
        if exist %%P (
            echo [OK] Found Tesseract at %%P
            set "TESSERACT_FOUND=%%~dpP"
            goto :tesseract_found
        )
    )
    
    :tesseract_not_found
    echo [!] Tesseract not found in common locations
    echo.
    echo Tesseract needs to be installed manually:
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Run the installer (tesseract-ocr-w64-setup-*.exe)
    echo 3. Install to default location or: %TESSERACT_DIR%
    echo 4. Re-run this script
    echo.
    echo Opening download page...
    start https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    set /p continue="Press Enter after installing Tesseract, or type 'skip' to continue without it: "
    if /i "!continue!"=="skip" goto :check_poppler
    goto :check_tesseract_again
    
    :tesseract_found
    echo Adding Tesseract to PATH for this session...
    set "PATH=%TESSERACT_FOUND%;%PATH%"
    
    :check_tesseract_again
    where tesseract >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Still cannot find Tesseract. Please check installation.
    ) else (
        echo [OK] Tesseract is now accessible
    )
)

echo.

REM ==========================================
REM Check and Install Poppler
REM ==========================================
echo Checking for Poppler utilities...
where pdftoppm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Poppler is already installed and in PATH
    pdftoppm -v
) else (
    echo [!] Poppler not found in PATH
    
    REM Check common installation locations
    set "POPPLER_FOUND="
    for %%P in (
        "%ProgramFiles%\poppler\Library\bin\pdftoppm.exe"
        "%ProgramFiles(x86)%\poppler\Library\bin\pdftoppm.exe"
        "%POPPLER_DIR%\Library\bin\pdftoppm.exe"
        "%POPPLER_DIR%\bin\pdftoppm.exe"
        "C:\Program Files\poppler\Library\bin\pdftoppm.exe"
        "C:\Program Files (x86)\poppler\Library\bin\pdftoppm.exe"
    ) do (
        if exist %%P (
            echo [OK] Found Poppler at %%P
            set "POPPLER_FOUND=%%~dpP"
            goto :poppler_found
        )
    )
    
    :poppler_not_found
    echo [!] Poppler not found in common locations
    echo.
    echo Attempting to download and install Poppler...
    
    REM Try to use winget if available (Windows 10+)
    where winget >nul 2>&1
    if %errorlevel% equ 0 (
        echo Using winget to install Poppler...
        winget install --id=sharkdp.poppler --silent --accept-package-agreements --accept-source-agreements
        if %errorlevel% equ 0 (
            echo [OK] Poppler installed via winget
            goto :check_poppler_again
        )
    )
    
    REM Try chocolatey if available
    where choco >nul 2>&1
    if %errorlevel% equ 0 (
        echo Using Chocolatey to install Poppler...
        choco install poppler -y
        if %errorlevel% equ 0 (
            echo [OK] Poppler installed via Chocolatey
            goto :check_poppler_again
        )
    )
    
    REM Manual download instructions
    echo.
    echo Poppler needs to be installed manually:
    echo 1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
    echo 2. Extract the ZIP file
    echo 3. Copy the extracted folder to: %POPPLER_DIR%
    echo 4. Re-run this script
    echo.
    echo Opening download page...
    start https://github.com/oschwartz10612/poppler-windows/releases/latest
    echo.
    set /p continue="Press Enter after installing Poppler, or type 'skip' to continue without it: "
    if /i "!continue!"=="skip" goto :create_config
    goto :check_poppler_again
    
    :poppler_found
    echo Adding Poppler to PATH for this session...
    set "PATH=%POPPLER_FOUND%;%PATH%"
    
    :check_poppler_again
    where pdftoppm >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Still cannot find Poppler. Please check installation.
    ) else (
        echo [OK] Poppler is now accessible
    )
)

echo.

REM ==========================================
REM Create configuration file
REM ==========================================
:create_config
echo Creating dependency configuration file...

set "CONFIG_FILE=dependency_paths.txt"

(
    echo # Dependency Paths Configuration
    echo # Auto-generated by setup_dependencies_windows.bat
    echo.
    where tesseract 2>nul
    if !errorlevel! equ 0 (
        for /f "delims=" %%i in ('where tesseract') do echo TESSERACT_PATH=%%~dpi
    ) else (
        echo TESSERACT_PATH=NOT_FOUND
    )
    echo.
    where pdftoppm 2>nul
    if !errorlevel! equ 0 (
        for /f "delims=" %%i in ('where pdftoppm') do echo POPPLER_PATH=%%~dpi
    ) else (
        echo POPPLER_PATH=NOT_FOUND
    )
) > "%CONFIG_FILE%"

echo [OK] Configuration saved to %CONFIG_FILE%

echo.
echo ==========================================
echo Setup Summary
echo ==========================================

REM Check final status
set "TESSERACT_OK=0"
set "POPPLER_OK=0"

where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract: READY
    set "TESSERACT_OK=1"
) else (
    echo [!] Tesseract: NOT FOUND
)

where pdftoppm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Poppler: READY
    set "POPPLER_OK=1"
) else (
    echo [!] Poppler: NOT FOUND
)

echo.

if "%TESSERACT_OK%"=="1" if "%POPPLER_OK%"=="1" (
    echo [SUCCESS] All dependencies are ready!
    echo You can now build and run the FAI PDF Processor.
) else (
    echo [WARNING] Some dependencies are missing.
    echo The application will run with limited functionality.
    echo OCR features will not be available without Tesseract and Poppler.
)

echo.
echo ==========================================
pause
