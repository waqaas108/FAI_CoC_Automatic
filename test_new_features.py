#!/usr/bin/env python3
"""
Test the new features:
1. Force OCR
2. Flexible PDF matching
3. Separate output folder
4. Searchable PDF output
"""

import sys
from pathlib import Path
from pdf_excel_processor import PDFExcelProcessor

def test_new_features():
    base_path = "/home/waqaas/Nasir/RAW_Kit-05 363K004G01"
    
    print("="*60)
    print("Testing New Features")
    print("="*60)
    
    # Test with force_ocr=True and separate_output=True (defaults)
    print("\n1. Testing with Force OCR and Separate Output Folder...")
    processor = PDFExcelProcessor(base_path, force_ocr=True, separate_output=True)
    
    # Check if output folder was created
    output_folder = Path(base_path) / "highlighted_pdfs"
    if output_folder.exists():
        print(f"✓ Output folder created: {output_folder}")
    else:
        print(f"✗ Output folder not created")
    
    # Process a small sample
    print("\n2. Processing sample PDFs...")
    
    # Test flexible PDF matching
    test_cases = [
        ("136-4010", "763360"),  # Should match 136-4010_763360_12-9-2024.pdf
        ("666-3520", "751670"),  # Should match 666-3520_751670_7-8-2020.pdf
    ]
    
    coc_folder = Path(base_path) / "Material CoC 7A13308H08"
    
    for cablex_pn, fair_id in test_cases:
        pdf_path = processor.find_matching_pdf(cablex_pn, fair_id, coc_folder)
        if pdf_path:
            print(f"✓ Found PDF for {cablex_pn}_{fair_id}: {pdf_path.name}")
            
            # Test OCR and highlighting
            search_term = "KE 104A054-130E+"  # A known part number
            found, output_path = processor.search_and_highlight_pdf(pdf_path, search_term)
            
            if found:
                print(f"  ✓ Highlighted PDF created: {output_path.name}")
                
                # Check if in correct output folder
                if processor.separate_output and "highlighted_pdfs" in str(output_path):
                    print(f"  ✓ Saved in separate output folder")
                else:
                    print(f"  ✗ Not in separate output folder: {output_path.parent.name}")
            else:
                print(f"  - Part number not found in this PDF")
        else:
            print(f"✗ No PDF found for {cablex_pn}_{fair_id}")
    
    # Check for searchable text in output
    print("\n3. Checking if output PDFs are searchable...")
    highlighted_pdfs = list(output_folder.glob("highlighted_*.pdf"))
    if highlighted_pdfs:
        sample_pdf = highlighted_pdfs[0]
        has_text = processor.check_pdf_has_text(sample_pdf)
        if has_text:
            print(f"✓ Output PDF has searchable text: {sample_pdf.name}")
        else:
            print(f"✗ Output PDF is not searchable: {sample_pdf.name}")
    else:
        print("No highlighted PDFs found to test")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == "__main__":
    test_new_features()
