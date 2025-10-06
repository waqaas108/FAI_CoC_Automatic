#!/usr/bin/env python3
"""
Test script for the PDF Excel Processor
Tests basic functionality with the sample directory
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_excel_processor import PDFExcelProcessor

def test_basic_functionality():
    """Test the processor with sample data"""
    
    print("Testing PDF Excel Processor")
    print("=" * 50)
    
    # Test directory
    test_dir = "/home/waqaas/Nasir/RAW_Kit-05 363K004G01"
    
    if not Path(test_dir).exists():
        print(f"Error: Test directory not found: {test_dir}")
        return False
    
    try:
        # Initialize processor
        print(f"Initializing processor with directory: {test_dir}")
        processor = PDFExcelProcessor(test_dir)
        
        # Test FAI number extraction
        print("\n1. Testing FAI number extraction...")
        fai_num = processor.extract_fai_number("FAI 127K667G02")
        assert fai_num == "127K667G02", f"Expected '127K667G02', got '{fai_num}'"
        print("   ✓ FAI number extraction works correctly")
        
        # Test finding FAI folders
        print("\n2. Checking FAI folders...")
        fai_folders = [f for f in processor.base_path.iterdir() 
                      if f.is_dir() and f.name.startswith('FAI')]
        print(f"   Found {len(fai_folders)} FAI folders")
        
        if fai_folders:
            # Test reading Excel from first FAI folder
            test_fai = fai_folders[0]
            print(f"\n3. Testing Excel reading from {test_fai.name}...")
            
            excel_files = list(test_fai.glob('*.xlsx')) + list(test_fai.glob('*.xls'))
            if excel_files:
                excel_file = excel_files[0]
                print(f"   Reading: {excel_file.name}")
                
                df = processor.read_excel_tables(excel_file)
                if not df.empty:
                    print(f"   ✓ Successfully read {len(df)} rows")
                    print(f"   Columns found: {', '.join(df.columns)}")
                    
                    # Test PDF matching
                    if len(df) > 0:
                        row = df.iloc[0]
                        fai_number = processor.extract_fai_number(test_fai.name)
                        coc_folder = processor.base_path / f"Material CoC {fai_number}"
                        
                        if coc_folder.exists():
                            print(f"\n4. Testing PDF matching...")
                            print(f"   Looking for: {row['Cablex P/N']}_{row['FAIR Identifier']}_*.pdf")
                            
                            pdf_path = processor.find_matching_pdf(
                                row['Cablex P/N'],
                                row['FAIR Identifier'],
                                coc_folder
                            )
                            
                            if pdf_path:
                                print(f"   ✓ Found matching PDF: {pdf_path.name}")
                            else:
                                print(f"   ✗ No matching PDF found")
                        else:
                            print(f"   Material CoC folder not found: {coc_folder}")
                else:
                    print("   ✗ No data found in Excel file")
            else:
                print("   ✗ No Excel files found")
        
        # Quick process test (just first folder to save time)
        print("\n5. Running quick processing test...")
        print("   This will process just the first FAI folder...")
        
        # Process with limited scope for testing
        results = processor.process_directory()
        
        if not results.empty:
            print(f"\n   ✓ Processing successful!")
            print(f"   Total rows processed: {len(results)}")
            print(f"   PDFs found: {len(results[results['PDF Status'] == 'Found'])}")
            
            # Save test results
            test_output = Path("test_results.csv")
            results.head(20).to_csv(test_output, index=False)
            print(f"\n   Sample results saved to: {test_output}")
            
            return True
        else:
            print("   ✗ No results generated")
            return False
            
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed successfully!")
        print("You can now run the full processor with:")
        print("  python pdf_excel_processor.py --path '/home/waqaas/Nasir/RAW_Kit-05 363K004G01'")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)
