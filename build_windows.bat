@echo off
echo ==========================================
echo FAI PDF Processor - Windows Build
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install/update dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build the executable
echo Building Windows executable...
pyinstaller --clean --onefile ^
    --name "FAI_PDF_Processor" ^
    --windowed ^
    --add-data "README.md;." ^
    --add-data "requirements.txt;." ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import PyMuPDF ^
    --hidden-import pytesseract ^
    --hidden-import pdf2image ^
    --hidden-import PIL ^
    pdf_excel_processor.py

echo.
echo ==========================================
echo Build complete!
echo.
echo Executable location: dist\FAI_PDF_Processor.exe
echo.
echo Note: Users will need to install:
echo   1. Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
echo   2. Poppler from: http://blog.alivate.com.au/poppler-windows/
echo ==========================================
pause
