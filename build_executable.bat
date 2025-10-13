@echo off
REM Build script for creating executable from pdf_excel_processor.py on Windows

echo FAI/Material CoC Processor - Build Script
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check and setup dependencies (Tesseract and Poppler)
echo.
echo Checking dependencies...
if exist setup_dependencies_windows.bat (
    call setup_dependencies_windows.bat
) else (
    echo Warning: setup_dependencies_windows.bat not found
    echo Tesseract and Poppler may need to be installed manually
)
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

REM Build options menu
echo.
echo Select build type:
echo 1) Single file executable (slower startup, portable)
echo 2) Directory bundle (faster startup, multiple files)
echo 3) Both
echo.
set /p choice="Enter choice [1-3]: "

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

if "%choice%"=="1" (
    echo Building single file executable...
    pyinstaller --onefile ^
               --windowed ^
               --name "FAI_Processor" ^
               --hidden-import="openpyxl" ^
               --hidden-import="fitz" ^
               --hidden-import="PIL" ^
               --collect-data="fitz" ^
               pdf_excel_processor.py
    echo Build complete! Executable location: dist\FAI_Processor.exe
) else if "%choice%"=="2" (
    echo Building directory bundle...
    pyinstaller --onedir ^
               --windowed ^
               --name "FAI_Processor" ^
               --hidden-import="openpyxl" ^
               --hidden-import="fitz" ^
               --hidden-import="PIL" ^
               --collect-data="fitz" ^
               pdf_excel_processor.py
    echo Build complete! Application location: dist\FAI_Processor\
) else if "%choice%"=="3" (
    echo Building both versions...
    
    REM Single file
    pyinstaller --onefile ^
               --windowed ^
               --name "FAI_Processor_single" ^
               --hidden-import="openpyxl" ^
               --hidden-import="fitz" ^
               --hidden-import="PIL" ^
               --collect-data="fitz" ^
               pdf_excel_processor.py
    
    REM Directory bundle
    pyinstaller --onedir ^
               --windowed ^
               --name "FAI_Processor_bundle" ^
               --hidden-import="openpyxl" ^
               --hidden-import="fitz" ^
               --hidden-import="PIL" ^
               --collect-data="fitz" ^
               pdf_excel_processor.py
    
    echo Build complete!
    echo Single file: dist\FAI_Processor_single.exe
    echo Bundle: dist\FAI_Processor_bundle\
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Build process finished!
echo.
echo To run the application:
echo   GUI mode: dist\FAI_Processor.exe --gui
echo   CLI mode: dist\FAI_Processor.exe --path C:\path\to\directory
pause
