#!/usr/bin/env python3
"""
Test script to verify the detailed progress tracking
"""

import sys
from pathlib import Path
from pdf_excel_processor import PDFExcelProcessor

def test_progress_callback(message, progress):
    """Simple progress callback for testing"""
    print(f"[{progress:3.0f}%] {message}")

def main():
    test_dir = "/home/waqaas/Nasir/RAW_Kit-05 363K004G01"
    
    if not Path(test_dir).exists():
        print(f"Error: Test directory not found: {test_dir}")
        return
    
    print("="*80)
    print("Testing Detailed Progress Tracking")
    print("="*80)
    print(f"Directory: {test_dir}\n")
    
    processor = PDFExcelProcessor(test_dir)
    
    # Process with detailed callback
    results = processor.process_directory(
        progress_callback=None,
        detailed_callback=test_progress_callback
    )
    
    print("\n" + "="*80)
    print("Processing Results:")
    print("="*80)
    
    if results.empty:
        print("No results found!")
        print("\nDebug Information:")
        print("-"*40)
        
        # Check for FAI folders
        fai_folders = list(Path(test_dir).glob("FAI*"))
        print(f"FAI folders found: {len(fai_folders)}")
        for folder in fai_folders[:3]:
            print(f"  - {folder.name}")
            excel_files = list(folder.glob("*.xlsx")) + list(folder.glob("*.xls"))
            print(f"    Excel files: {len(excel_files)}")
            for excel in excel_files:
                print(f"      - {excel.name}")
        
        # Check for CoC folders
        coc_folders = list(Path(test_dir).glob("Material CoC*"))
        print(f"\nMaterial CoC folders found: {len(coc_folders)}")
        for folder in coc_folders[:3]:
            print(f"  - {folder.name}")
            pdf_files = list(folder.glob("*.pdf"))
            print(f"    PDF files: {len(pdf_files)}")
    else:
        print(f"Total rows processed: {len(results)}")
        print(f"Columns: {', '.join(results.columns)}")
        
        if len(results) > 0:
            print("\nFirst 5 results:")
            print("-"*40)
            print(results[['Cablex P/N', 'FAIR Identifier', 'Part Number', 'PDF Status', 'Part Number Found']].head())
        
        # Statistics
        pdfs_found = len(results[results['PDF Status'] == 'Found'])
        parts_found = len(results[results['Part Number Found'] == 'Yes'])
        
        print(f"\nStatistics:")
        print(f"  PDFs found: {pdfs_found}/{len(results)}")
        if pdfs_found > 0:
            print(f"  Part numbers highlighted: {parts_found}/{pdfs_found}")
        
        # Save test results
        output_file = "test_results_detailed.csv"
        results.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
