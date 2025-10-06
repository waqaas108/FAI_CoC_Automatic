#!/bin/bash

# Cross-platform build script for FAI PDF Processor

echo "=========================================="
echo "FAI PDF Processor - Multi-Platform Build"
echo "=========================================="
echo ""

# Check for required tools
echo "Checking requirements..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.egg-info

# Detect platform
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    MINGW*|MSYS*|CYGWIN*)  PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Building for: ${PLATFORM}"
echo ""

# Build the executable
if [ "${PLATFORM}" = "Windows" ]; then
    echo "Building Windows executable..."
    pyinstaller --clean --onefile \
        --name "FAI_PDF_Processor" \
        --windowed \
        --add-data "README.md;." \
        --add-data "requirements.txt;." \
        --hidden-import pandas \
        --hidden-import openpyxl \
        --hidden-import PyMuPDF \
        --hidden-import pytesseract \
        --hidden-import pdf2image \
        --hidden-import PIL \
        pdf_excel_processor.py
    
    echo "Windows executable created: dist/FAI_PDF_Processor.exe"
    
elif [ "${PLATFORM}" = "macOS" ]; then
    echo "Building macOS application..."
    pyinstaller --clean --onefile \
        --name "FAI_PDF_Processor" \
        --windowed \
        --osx-bundle-identifier "com.fai.pdfprocessor" \
        --add-data "README.md:." \
        --add-data "requirements.txt:." \
        --hidden-import pandas \
        --hidden-import openpyxl \
        --hidden-import PyMuPDF \
        --hidden-import pytesseract \
        --hidden-import pdf2image \
        --hidden-import PIL \
        pdf_excel_processor.py
    
    # Create DMG for distribution (optional)
    if command -v create-dmg &> /dev/null; then
        echo "Creating DMG installer..."
        create-dmg \
            --volname "FAI PDF Processor" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --app-drop-link 450 185 \
            "dist/FAI_PDF_Processor.dmg" \
            "dist/FAI_PDF_Processor.app"
    fi
    
    echo "macOS application created: dist/FAI_PDF_Processor.app"
    
else  # Linux
    echo "Building Linux executable..."
    pyinstaller --clean --onefile \
        --name "FAI_PDF_Processor" \
        --add-data "README.md:." \
        --add-data "requirements.txt:." \
        --hidden-import pandas \
        --hidden-import openpyxl \
        --hidden-import PyMuPDF \
        --hidden-import pytesseract \
        --hidden-import pdf2image \
        --hidden-import PIL \
        pdf_excel_processor.py
    
    # Make executable
    chmod +x dist/FAI_PDF_Processor
    
    # Create AppImage for better distribution (optional)
    if command -v appimagetool &> /dev/null; then
        echo "Creating AppImage..."
        # Create AppDir structure
        mkdir -p AppDir/usr/bin
        cp dist/FAI_PDF_Processor AppDir/usr/bin/
        
        # Create desktop entry
        cat > AppDir/FAI_PDF_Processor.desktop <<EOF
[Desktop Entry]
Type=Application
Name=FAI PDF Processor
Comment=Process FAI Excel sheets and Material CoC PDFs
Exec=FAI_PDF_Processor
Icon=FAI_PDF_Processor
Categories=Office;Utility;
EOF
        
        # Create AppImage
        appimagetool AppDir dist/FAI_PDF_Processor.AppImage
    fi
    
    echo "Linux executable created: dist/FAI_PDF_Processor"
fi

echo ""
echo "=========================================="
echo "Build complete!"
echo ""
echo "Distribution files are in the 'dist' directory"
echo ""
echo "Note: Users will still need to install system dependencies:"
echo "  - Tesseract OCR"
echo "  - Poppler utilities"
echo "=========================================="
