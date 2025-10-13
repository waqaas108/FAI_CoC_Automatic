@echo off
REM Launcher script that checks dependencies before running the application
echo ==========================================
echo FAI PDF Processor - Launcher
echo ==========================================
echo.

REM Check if executable exists
if not exist "dist\FAI_PDF_Processor.exe" (
    echo Error: Application not built yet.
    echo Please run build_windows.bat first.
    echo.
    pause
    exit /b 1
)

REM Quick dependency check
echo Checking dependencies...
echo.

set "DEPS_OK=1"

REM Check Tesseract
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract OCR: Found
) else (
    echo [!] Tesseract OCR: Not found in PATH
    set "DEPS_OK=0"
)

REM Check Poppler
where pdftoppm >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Poppler utilities: Found
) else (
    echo [!] Poppler utilities: Not found in PATH
    set "DEPS_OK=0"
)

echo.

if "%DEPS_OK%"=="0" (
    echo WARNING: Some dependencies are missing.
    echo The application will run with limited functionality.
    echo.
    echo To install missing dependencies, run:
    echo   setup_dependencies_windows.bat
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "!continue!"=="y" (
        exit /b 0
    )
    echo.
)

REM Launch the application
echo Starting FAI PDF Processor...
echo.
start "" "dist\FAI_PDF_Processor.exe" --gui

echo Application launched!
echo You can close this window.
timeout /t 3 >nul
