@echo off
echo ==========================================
echo FAI PDF Processor - Launcher
echo ==========================================
echo.

:: Add common Python installation paths to PATH
set "PATH=C:\Python311;C:\Python311\Scripts;%PATH%"
set "PATH=C:\Python312;C:\Python312\Scripts;%PATH%"
set "PATH=C:\Python313;C:\Python313\Scripts;%PATH%"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts;%PATH%"
set "PATH=%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts;%PATH%"
set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
set "PATH=%ProgramFiles%\Python313;%ProgramFiles%\Python313\Scripts;%PATH%"

:: Add Tesseract to PATH
set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
set "PATH=C:\Program Files (x86)\Tesseract-OCR;%PATH%"

:: Check for Python
echo Checking Python installation...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Recommended version: Python 3.11 or later
    echo.
    pause
    exit /b 1
)

echo Python: OK
python --version
echo.

:: Check for Tesseract
echo Checking Tesseract OCR...
where tesseract >nul 2>nul
if errorlevel 1 (
    echo WARNING: Tesseract is not installed or not in PATH
    echo.
    echo Please install Tesseract OCR from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo The application may not work properly without Tesseract.
    echo.
    pause
) else (
    echo Tesseract: OK
)
echo.

:: Install/Update Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies: OK
echo.

:: Check and setup Poppler
echo Checking Poppler utilities...
set POPPLER_DIR=%~dp0poppler
set POPPLER_BIN=%POPPLER_DIR%\Library\bin

:: Add local Poppler to PATH immediately if it exists
if exist "%POPPLER_BIN%\pdftoppm.exe" (
    set "PATH=%POPPLER_BIN%;%PATH%"
    echo Poppler: Found locally at %POPPLER_DIR%
    goto :verify_poppler
)

:: Check if Poppler is already in system PATH
where pdftoppm >nul 2>nul
if not errorlevel 1 (
    echo Poppler: Already in PATH
    goto :launch
)

:: Extract Poppler from zip if it exists
if exist "%~dp0poppler.zip" (
    echo Extracting Poppler from poppler.zip...
    powershell -Command "Expand-Archive -Path '%~dp0poppler.zip' -DestinationPath '%~dp0' -Force"
    
    :: Find the extracted poppler directory (it may have version in name)
    for /d %%i in ("%~dp0poppler-*") do (
        if exist "%%i\Library\bin\pdftoppm.exe" (
            echo Renaming %%i to poppler...
            move "%%i" "%POPPLER_DIR%" >nul 2>nul
            set "PATH=%POPPLER_DIR%\Library\bin;%PATH%"
            goto :verify_poppler
        )
    )
    
    :: Check if it extracted directly to poppler folder
    if exist "%POPPLER_BIN%\pdftoppm.exe" (
        set "PATH=%POPPLER_BIN%;%PATH%"
        goto :verify_poppler
    )
    
    echo ERROR: Failed to extract Poppler properly
    pause
    exit /b 1
) else (
    echo ERROR: poppler.zip not found in the repository
    echo.
    echo Please ensure poppler.zip is in the same directory as this script.
    echo You can download it from:
    echo https://github.com/oschwartz10612/poppler-windows/releases
    echo.
    pause
    exit /b 1
)

:verify_poppler
:: Verify Poppler is working
pdftoppm -h >nul 2>nul
if errorlevel 1 (
    echo WARNING: Poppler may not be working correctly
) else (
    echo Poppler: OK
)
echo.

:launch
:: Launch the application
echo ==========================================
echo All dependencies checked!
echo Launching FAI PDF Processor...
echo ==========================================
echo.

python pdf_excel_processor.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to launch the application
    pause
)
