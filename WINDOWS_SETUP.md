# Windows Setup Guide

This guide will help you set up the FAI PDF Processor on Windows, including all required dependencies.

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Run the dependency setup script:**
   ```batch
   setup_dependencies_windows.bat
   ```
   This script will:
   - Check if Tesseract OCR is installed
   - Check if Poppler utilities are installed
   - Guide you through installation if needed
   - Automatically configure paths

2. **Build the application:**
   ```batch
   build_windows.bat
   ```
   This will automatically run the dependency check before building.

### Option 2: Manual Setup

If you prefer to install dependencies manually:

## Prerequisites

### 1. Python 3.8 or higher
- Download from: https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation

### 2. Tesseract OCR

**Automatic Detection:**
The application will automatically search for Tesseract in these locations:
- `C:\Program Files\Tesseract-OCR`
- `C:\Program Files (x86)\Tesseract-OCR`
- `C:\Program Files\FAI_Processor_Dependencies\Tesseract-OCR`

**Installation Steps:**
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run `tesseract-ocr-w64-setup-*.exe`
3. Install to the default location (recommended)
4. The application will automatically find it

**Manual PATH Setup (if needed):**
If Tesseract is not automatically detected:
1. Right-click "This PC" → Properties → Advanced System Settings
2. Click "Environment Variables"
3. Under "System variables", find and edit "Path"
4. Add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`)
5. Click OK and restart your command prompt

### 3. Poppler Utilities

**Automatic Detection:**
The application will automatically search for Poppler in these locations:
- `C:\Program Files\poppler\Library\bin`
- `C:\Program Files (x86)\poppler\Library\bin`
- `C:\Program Files\poppler\bin`
- `C:\Program Files\FAI_Processor_Dependencies\poppler\Library\bin`

**Installation Options:**

#### Option A: Using winget (Windows 10/11)
```batch
winget install --id=sharkdp.poppler
```

#### Option B: Using Chocolatey
```batch
choco install poppler
```

#### Option C: Manual Installation
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/latest
2. Extract the ZIP file
3. Copy the extracted folder to `C:\Program Files\poppler`
4. The application will automatically find it

**Manual PATH Setup (if needed):**
If Poppler is not automatically detected:
1. Right-click "This PC" → Properties → Advanced System Settings
2. Click "Environment Variables"
3. Under "System variables", find and edit "Path"
4. Add the Poppler bin directory (e.g., `C:\Program Files\poppler\Library\bin`)
5. Click OK and restart your command prompt

## Building the Application

### Using build_windows.bat (Recommended)
```batch
build_windows.bat
```

This script will:
1. Check for Python
2. Run dependency setup
3. Create a virtual environment
4. Install Python dependencies
5. Build the executable with PyInstaller

### Using build_executable.bat (Advanced)
```batch
build_executable.bat
```

This script offers more options:
1. Single file executable (portable, slower startup)
2. Directory bundle (faster startup, multiple files)
3. Both versions

## Verifying Installation

### Check Tesseract
```batch
tesseract --version
```
Should display version information.

### Check Poppler
```batch
pdftoppm -v
```
Should display version information.

### Check Python Dependencies
```batch
pip list
```
Should show: pandas, openpyxl, PyMuPDF, pytesseract, pdf2image, Pillow, click

## Troubleshooting

### "Tesseract not found" Error

**Solution 1: Run dependency setup**
```batch
setup_dependencies_windows.bat
```

**Solution 2: Create config file manually**
Create a file named `dependency_paths.txt` in the same directory as the application:
```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\
POPPLER_PATH=C:\Program Files\poppler\Library\bin\
```

**Solution 3: Set environment variable**
```batch
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### "Poppler not found" Error

**Solution 1: Run dependency setup**
```batch
setup_dependencies_windows.bat
```

**Solution 2: Add to PATH temporarily**
```batch
set PATH=%PATH%;C:\Program Files\poppler\Library\bin
```

### OCR Not Working

1. Verify both Tesseract and Poppler are installed:
   ```batch
   tesseract --version
   pdftoppm -v
   ```

2. Check the application logs for specific error messages

3. Try running the dependency setup again:
   ```batch
   setup_dependencies_windows.bat
   ```

### Permission Issues

If you get "Access Denied" errors:
1. Right-click the batch file
2. Select "Run as Administrator"
3. This is especially important for the dependency setup script

### Build Fails

**Clear previous builds:**
```batch
rmdir /s /q build
rmdir /s /q dist
del *.spec
```

**Reinstall dependencies:**
```batch
pip install --upgrade --force-reinstall -r requirements.txt
```

**Try a clean build:**
```batch
build_windows.bat
```

## Running the Application

### GUI Mode
```batch
dist\FAI_PDF_Processor.exe --gui
```

Or simply double-click `FAI_PDF_Processor.exe`

### CLI Mode
```batch
dist\FAI_PDF_Processor.exe --path "C:\path\to\your\directory"
```

## Advanced Configuration

### Custom Installation Paths

If you installed Tesseract or Poppler to custom locations, create a `dependency_paths.txt` file:

```
TESSERACT_PATH=D:\MyApps\Tesseract\
POPPLER_PATH=D:\MyApps\poppler\bin\
```

Place this file in the same directory as the executable.

### Environment Variables

You can also set these environment variables:
- `TESSERACT_CMD`: Full path to tesseract.exe
- `PATH`: Include directories containing tesseract.exe and poppler utilities

## System Requirements

- **OS:** Windows 10 or later (Windows 7/8 may work but not tested)
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 500MB for dependencies, 100MB for application
- **Python:** 3.8 or higher (for building from source)

## Support

If you encounter issues:
1. Check the logs in the application
2. Review this troubleshooting guide
3. Ensure all dependencies are properly installed
4. Try running `setup_dependencies_windows.bat` again
5. Check the main README.md for additional information

## Notes

- The dependency setup script requires internet connection for downloads
- Administrator privileges may be required for installation
- Antivirus software may flag the executable - this is a false positive
- The first run may be slower as Windows scans the new executable
