#!/bin/bash

# Installation script for OCR dependencies

echo "======================================"
echo "Installing OCR Dependencies"
echo "======================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system"
    echo ""
    
    # Update package list
    echo "Updating package list..."
    sudo apt-get update
    
    # Install Tesseract OCR
    echo "Installing Tesseract OCR..."
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
    
    # Install Poppler utilities (for pdf2image)
    echo "Installing Poppler utilities..."
    sudo apt-get install -y poppler-utils
    
    # Install Python packages
    echo "Installing Python OCR packages..."
    pip install pytesseract pdf2image Pillow
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system"
    echo ""
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew first:"
        echo "Visit https://brew.sh for installation instructions"
        exit 1
    fi
    
    # Install Tesseract OCR
    echo "Installing Tesseract OCR..."
    brew install tesseract
    
    # Install Poppler utilities
    echo "Installing Poppler utilities..."
    brew install poppler
    
    # Install Python packages
    echo "Installing Python OCR packages..."
    pip install pytesseract pdf2image Pillow
    
else
    echo "Unsupported OS: $OSTYPE"
    echo ""
    echo "For Windows:"
    echo "1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
    echo "2. Download Poppler from: http://blog.alivate.com.au/poppler-windows/"
    echo "3. Add both to your system PATH"
    echo "4. Run: pip install pytesseract pdf2image Pillow"
    exit 1
fi

echo ""
echo "======================================"
echo "Testing OCR installation..."
echo "======================================"
echo ""

# Test Tesseract
if command -v tesseract &> /dev/null; then
    TESS_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract installed: $TESS_VERSION"
else
    echo "✗ Tesseract not found in PATH"
fi

# Test Python packages
python3 -c "import pytesseract; print('✓ pytesseract installed')" 2>/dev/null || echo "✗ pytesseract not installed"
python3 -c "import pdf2image; print('✓ pdf2image installed')" 2>/dev/null || echo "✗ pdf2image not installed"
python3 -c "import PIL; print('✓ Pillow installed')" 2>/dev/null || echo "✗ Pillow not installed"

echo ""
echo "======================================"
echo "Installation complete!"
echo "======================================"
echo ""
echo "You can now run the PDF processor with OCR support."
echo "The processor will automatically use OCR for scanned PDFs."
