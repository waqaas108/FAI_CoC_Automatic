#!/bin/bash

# Build script for creating executable from pdf_excel_processor.py

echo "FAI/Material CoC Processor - Build Script"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Install PyInstaller
echo "Installing PyInstaller..."
pip3 install pyinstaller

# Build options menu
echo ""
echo "Select build type:"
echo "1) Single file executable (slower startup, portable)"
echo "2) Directory bundle (faster startup, multiple files)"
echo "3) Both"
echo ""
read -p "Enter choice [1-3]: " choice

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

case $choice in
    1)
        echo "Building single file executable..."
        pyinstaller --onefile \
                   --name "FAI_Processor" \
                   --hidden-import="openpyxl" \
                   --hidden-import="fitz" \
                   --hidden-import="PIL" \
                   --collect-data="fitz" \
                   pdf_excel_processor.py
        echo "Build complete! Executable location: dist/FAI_Processor"
        ;;
    2)
        echo "Building directory bundle..."
        pyinstaller --onedir \
                   --windowed \
                   --name "FAI_Processor" \
                   --hidden-import="openpyxl" \
                   --hidden-import="fitz" \
                   --hidden-import="PIL" \
                   --collect-data="fitz" \
                   pdf_excel_processor.py
        echo "Build complete! Application location: dist/FAI_Processor/"
        ;;
    3)
        echo "Building both versions..."
        
        # Single file
        pyinstaller --onefile \
                   --name "FAI_Processor_single" \
                   --hidden-import="openpyxl" \
                   --hidden-import="fitz" \
                   --hidden-import="PIL" \
                   --collect-data="fitz" \
                   pdf_excel_processor.py
        
        # Directory bundle
        pyinstaller --onedir \
                   --windowed \
                   --name "FAI_Processor_bundle" \
                   --hidden-import="openpyxl" \
                   --hidden-import="fitz" \
                   --hidden-import="PIL" \
                   --collect-data="fitz" \
                   pdf_excel_processor.py
        
        echo "Build complete!"
        echo "Single file: dist/FAI_Processor_single"
        echo "Bundle: dist/FAI_Processor_bundle/"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Build process finished!"
echo ""
echo "To run the application:"
echo "  GUI mode: ./dist/FAI_Processor --gui"
echo "  CLI mode: ./dist/FAI_Processor --path /path/to/directory"
