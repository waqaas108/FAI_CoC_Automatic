#!/usr/bin/env python3
"""
Test script for OCR functionality
Tests whether OCR is installed and working with sample PDFs
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_excel_processor import PDFExcelProcessor, OCR_AVAILABLE

def check_ocr_installation():
    """Check if OCR dependencies are installed"""
    print("="*60)
    print("OCR Installation Check")
    print("="*60)
    
    if not OCR_AVAILABLE:
        print("❌ OCR libraries not available!")
        print("\nTo enable OCR, please install:")
        print("1. System dependencies:")
        print("   - Linux: sudo apt-get install tesseract-ocr poppler-utils")
        print("   - macOS: brew install tesseract poppler")
        print("   - Windows: Download Tesseract and Poppler (see README)")
        print("\n2. Python packages:")
        print("   pip install pytesseract pdf2image Pillow")
        return False
    
    print("✅ OCR libraries are available!")
    
    # Test tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
    except Exception as e:
        print(f"❌ Tesseract error: {e}")
        return False
    
    # Test pdf2image
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image is working")
    except Exception as e:
        print(f"❌ pdf2image error: {e}")
        return False
    
    return True

def test_pdf_ocr():
    """Test OCR on a sample PDF"""
    print("\n" + "="*60)
    print("PDF OCR Test")
    print("="*60)
    
    # Find a sample PDF
    test_dir = Path("/home/waqaas/Nasir/RAW_Kit-05 363K004G01")
    sample_pdf = None
    
    # Look for a PDF in Material CoC folders
    for coc_folder in test_dir.glob("Material CoC*"):
        pdfs = list(coc_folder.glob("*.pdf"))
        if pdfs:
            sample_pdf = pdfs[0]
            break
    
    if not sample_pdf:
        print("No sample PDF found for testing")
        return
    
    print(f"Testing with: {sample_pdf.name}")
    print(f"File size: {sample_pdf.stat().st_size / 1024:.1f} KB")
    
    processor = PDFExcelProcessor(test_dir)
    
    # Check if PDF has text
    print("\nChecking if PDF has searchable text...")
    has_text = processor.check_pdf_has_text(sample_pdf)
    
    if has_text:
        print("✅ PDF has searchable text (OCR may not be needed)")
    else:
        print("⚠️  PDF appears to be scanned (OCR will be used)")
    
    # Test search with a sample part number
    test_terms = ["M83519/2-8", "560R844H32", "KE 104A054-130E+"]
    
    print("\nTesting search and highlight with OCR enabled...")
    for term in test_terms:
        print(f"\nSearching for: {term}")
        found, output_path = processor.search_and_highlight_pdf(sample_pdf, term, use_ocr=True)
        
        if found:
            print(f"✅ Found and highlighted! Output: {output_path.name}")
            break
        else:
            print(f"❌ Not found")
    
    if not found:
        print("\nTrying OCR directly on the first page...")
        if OCR_AVAILABLE:
            try:
                from pdf2image import convert_from_path
                import pytesseract
                
                images = convert_from_path(str(sample_pdf), dpi=200, first_page=1, last_page=1)
                if images:
                    text = pytesseract.image_to_string(images[0])
                    print("OCR extracted text (first 500 chars):")
                    print("-"*40)
                    print(text[:500])
                    print("-"*40)
            except Exception as e:
                print(f"OCR test failed: {e}")

def main():
    """Run all OCR tests"""
    # Check installation
    if not check_ocr_installation():
        print("\n⚠️  Please install OCR dependencies first!")
        print("Run: ./install_ocr.sh")
        return 1
    
    # Test OCR functionality
    test_pdf_ocr()
    
    print("\n" + "="*60)
    print("OCR Testing Complete!")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
