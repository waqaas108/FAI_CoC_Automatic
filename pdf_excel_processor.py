#!/usr/bin/env python3
"""
PDF and Excel Processor for FAI/Material CoC Analysis
Processes FAI Excel sheets and corresponding Material CoC PDFs
"""

import os
import sys
import re
import logging
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd
import openpyxl
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_windows_paths():
    """Setup Tesseract and Poppler paths for Windows"""
    if platform.system() != 'Windows':
        return
    
    # Common Tesseract installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR',
        r'C:\Program Files (x86)\Tesseract-OCR',
        r'C:\Program Files\FAI_Processor_Dependencies\Tesseract-OCR',
        os.path.expandvars(r'%ProgramFiles%\Tesseract-OCR'),
        os.path.expandvars(r'%ProgramFiles(x86)%\Tesseract-OCR'),
    ]
    
    # Common Poppler installation paths
    # Check local directory first (where run.bat extracts it)
    script_dir = Path(__file__).parent
    poppler_paths = [
        str(script_dir / 'poppler' / 'Library' / 'bin'),  # Local extraction
        str(script_dir / 'poppler' / 'bin'),  # Alternative local structure
        r'C:\poppler\Library\bin',  # Alternative system location
        r'C:\Program Files\poppler\Library\bin',
        r'C:\Program Files (x86)\poppler\Library\bin',
        r'C:\Program Files\poppler\bin',
        r'C:\Program Files\FAI_Processor_Dependencies\poppler\Library\bin',
        r'C:\Program Files\FAI_Processor_Dependencies\poppler\bin',
        os.path.expandvars(r'%ProgramFiles%\poppler\Library\bin'),
        os.path.expandvars(r'%ProgramFiles(x86)%\poppler\Library\bin'),
    ]
    
    # Check for dependency_paths.txt config file
    config_file = Path(__file__).parent / 'dependency_paths.txt'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('TESSERACT_PATH=') and 'NOT_FOUND' not in line:
                        path = line.split('=', 1)[1].strip()
                        if path and Path(path).exists():
                            tesseract_paths.insert(0, path)
                    elif line.startswith('POPPLER_PATH=') and 'NOT_FOUND' not in line:
                        path = line.split('=', 1)[1].strip()
                        if path and Path(path).exists():
                            poppler_paths.insert(0, path)
        except Exception as e:
            logger.debug(f"Could not read config file: {e}")
    
    # Find and set Tesseract path
    tesseract_found = False
    for tess_path in tesseract_paths:
        tesseract_exe = Path(tess_path) / 'tesseract.exe'
        if tesseract_exe.exists():
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
                logger.info(f"Tesseract found at: {tesseract_exe}")
                tesseract_found = True
                break
            except ImportError:
                pass
    
    if not tesseract_found:
        logger.warning("Tesseract not found in common locations. OCR may not work.")
    
    # Find and add Poppler to PATH
    poppler_found = False
    for pop_path in poppler_paths:
        pdftoppm_exe = Path(pop_path) / 'pdftoppm.exe'
        if pdftoppm_exe.exists():
            # Add to PATH if not already there
            if pop_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{pop_path};{os.environ.get('PATH', '')}"
            logger.info(f"Poppler found at: {pop_path}")
            poppler_found = True
            break
    
    if not poppler_found:
        logger.warning("Poppler not found in common locations. PDF to image conversion may not work.")
    
    return tesseract_found and poppler_found


# Setup Windows paths before importing OCR libraries
if platform.system() == 'Windows':
    setup_windows_paths()

# OCR imports with error handling
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    OCR_ERROR = str(e)
    logger.warning(f"OCR libraries not available: {e}")


class PDFExcelProcessor:
    """Main processor class for handling FAI Excel sheets and Material CoC PDFs"""
    
    def __init__(self, base_path: str, force_ocr: bool = True, separate_output: bool = True, destructive: bool = False):
        self.base_path = Path(base_path)
        self.results_df = pd.DataFrame()
        self.processed_pdfs = []
        self.force_ocr = force_ocr
        self.separate_output = separate_output
        self.destructive = destructive
        self.output_folder = None
        
        # Create output folder if needed (only if not destructive and separate output is enabled)
        if self.separate_output and not self.destructive:
            self.output_folder = self.base_path / "highlighted_pdfs"
            self.output_folder.mkdir(exist_ok=True)
        
        # Track folder structure for organizing outputs
        self.folder_map = {}
        
    @staticmethod
    def _clean_cell(value) -> str:
        """Normalize cell contents by stripping whitespace and collapsing newlines"""
        if pd.isna(value):
            return ''
        text = str(value).replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_table_from_sheet(self, sheet_df: pd.DataFrame) -> pd.DataFrame:
        """Locate and extract the Cablex/FAIR/Part Number table from a messy worksheet"""
        if sheet_df.empty:
            return pd.DataFrame()

        normalized = sheet_df.map(self._clean_cell)

        header_row_idx = None
        header_candidates = {}

        for idx, row in normalized.iterrows():
            row_lower = [cell.lower() for cell in row if cell]
            if not row_lower:
                continue

            has_cablex = any('cablex' in cell and 'p/n' in cell for cell in row_lower)
            has_fair = any('fair' in cell and 'identifier' in cell for cell in row_lower)
            has_part = any('part number' in cell for cell in row_lower)

            if has_cablex and has_fair and has_part:
                header_row_idx = idx
                header_candidates = {
                    'Cablex P/N': None,
                    'FAIR Identifier': None,
                    'Part Number': None,
                }

                header_row = normalized.iloc[idx]
                for col_idx, text in header_row.items():
                    lower = text.lower()
                    if not lower:
                        continue
                    if 'cablex' in lower and 'p/n' in lower:
                        header_candidates['Cablex P/N'] = col_idx
                    elif 'fair' in lower and 'identifier' in lower:
                        header_candidates['FAIR Identifier'] = col_idx
                    elif 'part number' in lower:
                        header_candidates['Part Number'] = col_idx
                break

        if header_row_idx is None or None in header_candidates.values():
            return pd.DataFrame()

        records = []
        empty_streak = 0

        footer_markers = (
            'does fair contain',
            'fair verified',
            'fair reviewed',
            'customer approval',
            'comments:',
        )

        for idx in range(header_row_idx + 1, len(normalized)):
            row = normalized.iloc[idx]
            row_text = ' '.join(cell for cell in row if cell)

            if not row_text:
                empty_streak += 1
                if empty_streak >= 2:
                    break
                continue

            empty_streak = 0

            lowered = row_text.lower()
            if any(marker in lowered for marker in footer_markers):
                break

            record = {}
            filled = False
            for key, col_idx in header_candidates.items():
                value = row.get(col_idx, '')
                record[key] = value
                if value:
                    filled = True

            if filled:
                records.append(record)

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    def extract_identifier(self, folder_name: str) -> str:
        """Extract the identifier from folder name
        
        Examples:
            'FAI 127K667G02' -> '127K667G02'
            'Material CoC 127K667G02' -> '127K667G02'
            '127K667G02' -> '127K667G02'
        """
        # Try to extract from 'FAI <identifier>' pattern
        match = re.search(r'FAI\s+(.+)', folder_name)
        if match:
            return match.group(1)
        
        # Try to extract from 'Material CoC <identifier>' pattern
        match = re.search(r'Material\s+CoC\s+(.+)', folder_name)
        if match:
            return match.group(1)
        
        # Return as-is if no pattern matches
        return folder_name
    
    def extract_fai_number(self, folder_name: str) -> str:
        """Legacy method - calls extract_identifier for backward compatibility"""
        return self.extract_identifier(folder_name)
    
    def read_excel_tables(self, excel_path: Path) -> pd.DataFrame:
        """Read Excel file and extract tables with required columns"""
        try:
            # Try reading all sheets
            excel_file = pd.ExcelFile(excel_path)
            all_data = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    raw_sheet = pd.read_excel(
                        excel_path,
                        sheet_name=sheet_name,
                        header=None,
                        dtype=object
                    )

                    table_df = self._extract_table_from_sheet(raw_sheet)

                    if not table_df.empty:
                        table_df['Sheet'] = sheet_name
                        all_data.append(table_df)
                    else:
                        logger.debug(f"Required table not found in sheet {sheet_name}")
                        
                except Exception as e:
                    logger.warning(f"Error reading sheet {sheet_name}: {e}")
            
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading Excel file {excel_path}: {e}")
            return pd.DataFrame()
    
    def find_matching_pdf(self, cablex_pn: str, fair_id: str, coc_folder: Path) -> Optional[Path]:
        """Find matching PDF file based on Cablex P/N and FAIR Identifier"""
        if not coc_folder.exists():
            return None
        
        cablex_pn = str(cablex_pn).strip()
        fair_id = str(fair_id).strip()
        
        # More flexible matching - just check if both identifiers are in the filename
        for pdf_file in coc_folder.glob('*.pdf'):
            filename = pdf_file.name.lower()
            # Remove common separators for better matching
            filename_clean = filename.replace('_', ' ').replace('-', ' ')
            cablex_clean = cablex_pn.lower().replace('_', ' ').replace('-', ' ')
            fair_clean = fair_id.lower().replace('_', ' ').replace('-', ' ')
            
            # Check if both identifiers appear in the filename
            if cablex_clean in filename_clean and fair_clean in filename_clean:
                return pdf_file
        
        # Fallback to original strict pattern matching
        for pdf_file in coc_folder.glob('*.pdf'):
            filename = pdf_file.name
            pattern = f"{cablex_pn}_{fair_id}_"
            if filename.startswith(pattern):
                return pdf_file
        return None
    
    def check_pdf_has_text(self, pdf_path: Path) -> bool:
        """Check if PDF has searchable text"""
        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(min(3, len(doc))):  # Check first 3 pages
                page = doc[page_num]
                text = page.get_text()
                if text and len(text.strip()) > 50:  # Has meaningful text
                    doc.close()
                    return True
            doc.close()
            return False
        except Exception as e:
            logger.error(f"Error checking PDF text in {pdf_path}: {e}")
            return False
    
    def ocr_pdf_and_create_searchable(self, pdf_path: Path, doc: fitz.Document, search_term: str) -> Tuple[bool, List[Tuple[int, List[fitz.Rect]]]]:
        """Perform OCR on PDF and create searchable text layer, returns (found, [(page_num, [match_rects])])"""
        if not OCR_AVAILABLE:
            logger.warning("OCR not available. Install pytesseract and pdf2image.")
            return False, []
        
        try:
            logger.info(f"Performing OCR on {pdf_path.name}...")
            
            # Convert PDF to images
            images = convert_from_path(str(pdf_path), dpi=200)
            
            found_pages = []
            search_term_lower = search_term.lower().strip()
            
            for page_num, image in enumerate(images):
                if page_num >= len(doc):
                    break
                    
                page = doc[page_num]
                
                # Get OCR data with bounding boxes
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Clear existing text if any
                page.clean_contents()
                
                # Add invisible text layer for searchability
                text_instances = []
                full_text = ""
                
                for i in range(len(ocr_data['text'])):
                    text = ocr_data['text'][i].strip()
                    if text:
                        # Get position from OCR
                        x = ocr_data['left'][i]
                        y = ocr_data['top'][i]
                        w = ocr_data['width'][i]
                        h = ocr_data['height'][i]
                        
                        # Convert image coordinates to PDF coordinates
                        # Assuming standard DPI conversion
                        scale = page.rect.width / image.width
                        pdf_x = x * scale
                        pdf_y = y * scale
                        pdf_w = w * scale
                        pdf_h = h * scale
                        
                        # Create rectangle for this word
                        rect = fitz.Rect(pdf_x, pdf_y, pdf_x + pdf_w, pdf_y + pdf_h)
                        
                        # Add invisible text at this position
                        rc = page.insert_text(
                            fitz.Point(pdf_x, pdf_y + pdf_h),
                            text,
                            fontsize=1,
                            color=(1, 1, 1),  # White (invisible on white background)
                            render_mode=3  # Invisible rendering
                        )
                        
                        full_text += text + " "
                        
                        # Check if this word matches our search term
                        if search_term_lower in text.lower():
                            text_instances.append(rect)
                
                # Also check for multi-word matches in the full text
                if search_term_lower in full_text.lower() and not text_instances:
                    # Find approximate position for multi-word match
                    # This is a simplified approach - could be improved
                    start_idx = full_text.lower().find(search_term_lower)
                    if start_idx >= 0:
                        # Add a general marker for this page
                        text_instances.append(fitz.Rect(50, 50, 200, 70))
                
                if text_instances:
                    found_pages.append((page_num, text_instances))
                    logger.debug(f"Found '{search_term}' on page {page_num + 1} via OCR")
            
            return len(found_pages) > 0, found_pages
            
        except Exception as e:
            logger.error(f"OCR error on {pdf_path}: {e}")
            return False, []
    
    def search_and_highlight_pdf(self, pdf_path: Path, search_term: str, source_folder: str = None) -> Tuple[bool, Path]:
        """Search for term in PDF and highlight if found, using OCR if needed
        
        Args:
            pdf_path: Path to the PDF file
            search_term: Term to search for
            source_folder: Name of the source folder (e.g., 'Material CoC 123456') for organizing outputs
        """
        try:
            doc = fitz.open(str(pdf_path))
            found = False
            search_term = str(search_term).strip()
            highlighted_pages = set()
            
            # First try normal text search
            for page_num, page in enumerate(doc):
                text_instances = page.search_for(search_term, quads=False)
                
                if text_instances:
                    found = True
                    highlighted_pages.add(page_num)
                    for inst in text_instances:
                        # Add yellow highlight
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors({"stroke": [1, 1, 0]})  # Yellow
                        highlight.update()
            
            # If not found OR force OCR is enabled, perform OCR
            use_ocr = self.force_ocr or (not found and not self.check_pdf_has_text(pdf_path))
            
            if use_ocr:
                logger.info(f"Performing OCR for {pdf_path.name}")
                ocr_found, ocr_matches = self.ocr_pdf_and_create_searchable(pdf_path, doc, search_term)
                
                if ocr_found:
                    found = True
                    # Highlight the found text regions
                    for page_num, match_rects in ocr_matches:
                        if page_num < len(doc):
                            page = doc[page_num]
                            
                            # Highlight each matched region
                            for rect in match_rects:
                                try:
                                    highlight = page.add_highlight_annot(rect)
                                    highlight.set_colors({"stroke": [1, 1, 0]})  # Yellow
                                    highlight.update()
                                except:
                                    pass  # Skip if rect is invalid
                            
                            # Also add text annotation at top
                            point = fitz.Point(50, 30)
                            text_str = f"Matched Part Number: {search_term}"
                            page.insert_text(point, text_str, fontsize=12, color=(1, 0, 0))  # Red text
            
            if found:
                # Determine output path based on settings
                if self.destructive:
                    # Replace original file in place
                    output_path = pdf_path
                elif self.separate_output and self.output_folder:
                    # Create subfolder based on source folder
                    if source_folder:
                        subfolder = self.output_folder / source_folder
                        subfolder.mkdir(exist_ok=True)
                        output_path = subfolder / f"highlighted_{pdf_path.name}"
                    else:
                        output_path = self.output_folder / f"highlighted_{pdf_path.name}"
                else:
                    output_path = pdf_path.parent / f"highlighted_{pdf_path.name}"
                
                # Save with text layer for searchability
                doc.save(str(output_path), garbage=3, deflate=True)
                doc.close()
                return True, output_path
            else:
                doc.close()
                return False, pdf_path
                
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return False, pdf_path
    
    def process_directory(self, progress_callback=None, detailed_callback=None, stop_flag=None) -> pd.DataFrame:
        """Process all FAI folders and Material CoC folders in the directory"""
        all_results = []
        
        # Helper to check if we should stop
        def should_stop():
            return stop_flag and stop_flag()
        stats = {
            'fai_folders': 0,
            'coc_folders': 0,
            'excel_files': 0,
            'excel_rows': 0,
            'pdfs_found': 0,
            'parts_highlighted': 0
        }
        
        # Step 1: Find all Material CoC folders and their corresponding Excel folders (search up to depth 3)
        if detailed_callback:
            detailed_callback("Step 1: Finding folder pairs...", 0)
        
        # Search for Material CoC folders up to depth 3 (these are stable)
        coc_folders = []
        def find_coc_folders(directory, current_depth=0, max_depth=3):
            if current_depth > max_depth:
                return
            try:
                for item in directory.iterdir():
                    if item.is_dir():
                        if item.name.startswith('Material CoC'):
                            coc_folders.append(item)
                        # Recurse into subdirectories
                        if current_depth < max_depth:
                            find_coc_folders(item, current_depth + 1, max_depth)
            except PermissionError:
                pass
        
        find_coc_folders(self.base_path)
        coc_folders = sorted(coc_folders)
        stats['coc_folders'] = len(coc_folders)
        
        # For each CoC folder, find corresponding Excel folder
        folder_pairs = []
        for coc_folder in coc_folders:
            identifier = self.extract_identifier(coc_folder.name)
            parent_dir = coc_folder.parent
            
            # Try multiple patterns to find the Excel folder
            excel_folder = None
            potential_names = [
                f"FAI {identifier}",  # Standard FAI folder
                identifier,           # Just the identifier (for kit folders)
                f"FAI{identifier}",   # No space variant
            ]
            
            # First check in same directory
            for name in potential_names:
                candidate = parent_dir / name
                if candidate.exists() and candidate.is_dir():
                    excel_folder = candidate
                    break
            
            # If not found in same directory, search in subdirectories
            if not excel_folder:
                found_excel = None
                def find_excel_folder(directory, target_names, current_depth=0, max_depth=3):
                    nonlocal found_excel
                    if found_excel or current_depth > max_depth:
                        return
                    try:
                        for item in directory.iterdir():
                            if item.is_dir():
                                if item.name in target_names:
                                    found_excel = item
                                    return
                                if current_depth < max_depth:
                                    find_excel_folder(item, target_names, current_depth + 1, max_depth)
                    except PermissionError:
                        pass
                
                find_excel_folder(parent_dir, potential_names)
                excel_folder = found_excel
            
            if excel_folder and excel_folder.exists():
                stats['fai_folders'] += 1
                folder_pairs.append((excel_folder, coc_folder, identifier))
                logger.info(f"Paired: {excel_folder.name} <-> {coc_folder.name}")
            else:
                logger.warning(f"No Excel folder found for {coc_folder.name}. Tried: {', '.join(potential_names)}")
                # Still add the CoC folder even without Excel folder
                folder_pairs.append((None, coc_folder, identifier))
        
        if detailed_callback:
            detailed_callback(f"Step 1: Found {stats['coc_folders']} CoC folders, {stats['fai_folders']} Excel folders", 10)
        
        # Step 2: Find Excel files
        if detailed_callback:
            detailed_callback("Step 2: Finding Excel files...", 15)
        
        excel_files_to_process = []
        for excel_folder, coc_folder, identifier in folder_pairs:
            # Skip if no Excel folder found
            if not excel_folder:
                continue
            
            excel_files = list(excel_folder.glob('*.xlsx')) + list(excel_folder.glob('*.xls'))
            for excel_file in excel_files:
                excel_files_to_process.append((excel_file, excel_folder, coc_folder, identifier))
                stats['excel_files'] += 1
        
        if detailed_callback:
            detailed_callback(f"Step 2: Found {stats['excel_files']} Excel files", 20)
        
        if stats['excel_files'] == 0:
            logger.error("No Excel files found in any FAI folder")
            if detailed_callback:
                detailed_callback("Error: No Excel files found", 100)
            return pd.DataFrame()
        
        # Step 3: Parse Excel files and extract rows
        if detailed_callback:
            detailed_callback("Step 3: Parsing Excel files...", 25)
        
        total_files = len(excel_files_to_process)
        for idx, (excel_file, excel_folder, coc_folder, identifier) in enumerate(excel_files_to_process):
            # Check if we should stop
            if should_stop():
                logger.info("Processing stopped by user")
                break
            
            progress = 25 + (idx / total_files) * 20  # Progress from 25% to 45%
            
            # Update with file info
            file_info = {
                'filename': excel_file.name,
                'current': idx + 1,
                'total': total_files
            }
            
            if progress_callback:
                progress_callback(f"Processing {excel_file.name}...", progress, file_info)
            
            logger.info(f"Processing Excel file: {excel_file}")
            
            # Extract data from Excel
            df = self.read_excel_tables(excel_file)
            
            if df.empty:
                logger.warning(f"No valid data found in {excel_file}")
                continue
            
            stats['excel_rows'] += len(df)
            
            # Add identifier column
            df['FAI Folder'] = identifier
            df['Excel File'] = excel_file.name
            df['Excel Folder Name'] = excel_folder.name
            
            # Process each row - collect tasks for parallel processing
            total_rows = len(df)
            pdf_tasks = []
            row_results = []
            
            # First pass: prepare all rows and identify PDFs to process
            for idx_row, row in df.iterrows():
                # Check if we should stop
                if should_stop():
                    break
                    
                result = row.to_dict()
                
                # Check if PDF exists
                pdf_path = None
                if coc_folder:
                    pdf_path = self.find_matching_pdf(
                        row['Cablex P/N'], 
                        row['FAIR Identifier'], 
                        coc_folder
                    )
                
                if pdf_path:
                    stats['pdfs_found'] += 1
                    result['PDF Status'] = 'Found'
                    result['PDF File'] = pdf_path.name
                    
                    # Add to tasks for parallel processing
                    source_folder_name = coc_folder.name if coc_folder else None
                    pdf_tasks.append({
                        'pdf_path': pdf_path,
                        'part_number': row['Part Number'],
                        'source_folder': source_folder_name,
                        'result_index': len(row_results)
                    })
                else:
                    result['PDF Status'] = 'Not Found'
                    result['PDF File'] = ''
                    result['Part Number Found'] = 'N/A'
                    result['Highlighted PDF'] = ''
                
                row_results.append(result)
            
            # Process PDFs in parallel using ThreadPoolExecutor
            if pdf_tasks and not should_stop():
                max_workers = min(8, os.cpu_count() or 4)  # Use up to 8 threads
                
                if detailed_callback:
                    detailed_callback(f"Step 4-5: Processing {len(pdf_tasks)} PDFs in parallel with {max_workers} threads...", 50)
                
                def process_single_pdf(task):
                    """Process a single PDF in a thread"""
                    try:
                        found, output_path = self.search_and_highlight_pdf(
                            task['pdf_path'], 
                            task['part_number'],
                            source_folder=task['source_folder']
                        )
                        return task['result_index'], found, output_path, task['source_folder']
                    except Exception as e:
                        logger.error(f"Error processing PDF {task['pdf_path']}: {e}")
                        return task['result_index'], False, None, task['source_folder']
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks
                    futures = {executor.submit(process_single_pdf, task): task for task in pdf_tasks}
                    
                    # Process completed tasks
                    completed = 0
                    for future in as_completed(futures):
                        if should_stop():
                            executor.shutdown(wait=False)
                            break
                        
                        try:
                            result_index, found, output_path, source_folder = future.result(timeout=30)
                            
                            if found and output_path:
                                stats['parts_highlighted'] += 1
                                row_results[result_index]['Part Number Found'] = 'Yes'
                                row_results[result_index]['Highlighted PDF'] = output_path.name
                                row_results[result_index]['Source Folder'] = source_folder
                                self.processed_pdfs.append(output_path)
                            else:
                                row_results[result_index]['Part Number Found'] = 'No'
                                row_results[result_index]['Highlighted PDF'] = ''
                            
                            completed += 1
                            if detailed_callback:
                                progress = 50 + (completed / len(pdf_tasks)) * 30
                                detailed_callback(f"Step 4-5: Processed {completed}/{len(pdf_tasks)} PDFs", progress)
                        except Exception as e:
                            logger.error(f"Error getting result from thread: {e}")
            
            # Add all results
            all_results.extend(row_results)
        
        # Step 6: Create final DataFrame
        if detailed_callback:
            detailed_callback("Step 6: Creating final output CSV...", 90)
        
        self.results_df = pd.DataFrame(all_results)
        
        # Final summary
        summary = f"Complete! Processed {stats['excel_rows']} rows from {stats['excel_files']} Excel files. "
        summary += f"Found {stats['pdfs_found']} PDFs, highlighted {stats['parts_highlighted']} part numbers."
        
        if detailed_callback:
            detailed_callback(summary, 100)
        elif progress_callback:
            progress_callback(summary, 100)
            
        return self.results_df
    
    def save_results(self, output_path: str = None) -> str:
        """Save results to CSV file"""
        if self.results_df.empty:
            raise ValueError("No results to save. Run process_directory first.")
            
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.base_path / f"processing_results_{timestamp}.csv"
        else:
            output_path = Path(output_path)
            
        self.results_df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")
        return str(output_path)


class ProcessorGUI:
    """GUI interface for the PDF Excel Processor"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FAI/Material CoC Processor")
        # Don't set geometry - let it auto-size
        
        self.processor = None
        self.current_file_info = {"current": 0, "total": 0, "filename": ""}
        self.processing_thread = None
        self.stop_processing = False
        self.setup_ui()
        
        # Update window to calculate size, then set minimum size
        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        
    def setup_ui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # OCR Status
        ocr_status = "OCR Available" if OCR_AVAILABLE else "OCR Not Available (install dependencies)"
        ocr_color = "green" if OCR_AVAILABLE else "red"
        ocr_label = ttk.Label(main_frame, text=f"Status: {ocr_status}", foreground=ocr_color)
        ocr_label.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Directory selection
        ttk.Label(main_frame, text="Select Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.dir_var, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_directory).grid(row=1, column=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Force OCR checkbox
        self.force_ocr_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, 
            text="Force OCR on all PDFs (recommended for scanned documents)",
            variable=self.force_ocr_var
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Output options - radio buttons
        self.output_mode_var = tk.StringVar(value="separate")
        
        ttk.Radiobutton(
            options_frame,
            text="Save highlighted PDFs in separate 'highlighted_pdfs' folder",
            variable=self.output_mode_var,
            value="separate"
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(
            options_frame,
            text="Replace original PDFs in-place (destructive - no backup)",
            variable=self.output_mode_var,
            value="destructive"
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.process_btn = ttk.Button(button_frame, text="Process Files", command=self.process_files)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_processing_func, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(button_frame, text="Reset", command=self.reset_gui, state='disabled')
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        help_btn = ttk.Button(button_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=600, variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Progress details with file info
        progress_header_frame = ttk.Frame(main_frame)
        progress_header_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(progress_header_frame, text="Progress Details:").pack(side=tk.LEFT)
        self.file_progress_label = ttk.Label(progress_header_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.file_progress_label.pack(side=tk.LEFT, padx=10)
        
        self.progress_text = scrolledtext.ScrolledText(main_frame, width=100, height=8)
        self.progress_text.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Results summary label
        self.results_summary = ttk.Label(main_frame, text="", font=('TkDefaultFont', 9, 'bold'))
        self.results_summary.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=9, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=30, state='readonly')
        filter_combo['values'] = ("All", "PDF Found", "PDF Not Found", "Part Number Not Found", "Part Number Found")
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
        # Results table with scrollbar
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=10, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(10, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Create Treeview for results table
        columns = ('Excel File', 'Part Number', 'PDF Status', 'PDF File', 'Highlighted')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.results_tree.heading('Excel File', text='Excel File')
        self.results_tree.heading('Part Number', text='Part Number')
        self.results_tree.heading('PDF Status', text='PDF Status')
        self.results_tree.heading('PDF File', text='PDF File')
        self.results_tree.heading('Highlighted', text='Highlighted')
        
        # Configure column widths
        self.results_tree.column('Excel File', width=200)
        self.results_tree.column('Part Number', width=150)
        self.results_tree.column('PDF Status', width=100)
        self.results_tree.column('PDF File', width=250)
        self.results_tree.column('Highlighted', width=80)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click event to open files
        self.results_tree.bind('<Double-1>', self.on_item_double_click)
        
        # Store full results for filtering
        self.full_results = []
        
        # Save button
        self.save_btn = ttk.Button(main_frame, text="Save Results to CSV", command=self.save_results, state='disabled')
        self.save_btn.grid(row=11, column=0, columnspan=3, pady=10)
        
    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
    
    def show_help(self):
        """Display help dialog with usage instructions"""
        help_window = tk.Toplevel(self.root)
        help_window.title("FAI PDF Processor - Help")
        help_window.geometry("700x600")
        
        # Create scrolled text widget for help content
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=80, height=35)
        help_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Help content
        help_content = """FAI PDF PROCESSOR - USER GUIDE
============================================================

OVERVIEW
--------
This tool processes FAI (First Article Inspection) Excel sheets and Material CoC 
(Certificate of Compliance) PDFs to automatically match, search, and highlight 
part numbers across documents.

DIRECTORY STRUCTURE
------------------
Your working directory should contain:

  FAI [number]/              ← Contains Excel files
  Material CoC [number]/     ← Contains corresponding PDF files
  
Example:
  FAI 123456/
    ├── FAI Sheets-123456.xlsx
  Material CoC 123456/
    ├── part1_123456_date.pdf
    ├── part2_123456_date.pdf

HOW TO USE
----------
1. SELECT DIRECTORY
   Click "Browse" and select your working directory containing FAI and 
   Material CoC folders.

2. CONFIGURE OPTIONS
   
   ✓ Force OCR on all PDFs
     - Recommended for scanned documents
     - Processes all PDFs with OCR to make them searchable
     - Slower but ensures text is found in scanned images
   
   ○ Output Mode (choose one):
     
     • Save in separate 'highlighted_pdfs' folder (SAFE)
       - Creates new highlighted PDFs in a central folder
       - Original PDFs remain untouched
       - Easy to collect all results in one place
     
     • Replace original PDFs in-place (DESTRUCTIVE)
       - Modifies original PDF files directly
       - No backup created - use with caution!
       - Useful when you want originals updated

3. PROCESS FILES
   Click "Process Files" and monitor progress:
   - Progress bar shows overall completion
   - File info shows current file (e.g., "file.xlsx (6/11)")
   - Progress Details shows step-by-step actions

4. REVIEW RESULTS
   
   • Summary Line: Shows total entries, PDFs found, parts highlighted
   
   • Filter Dropdown: Focus on specific results
     - All: Show everything
     - PDF Found: Only entries with matching PDFs
     - PDF Not Found: Entries without PDFs
     - Part Number Not Found: PDFs found but part not highlighted
     - Part Number Found: Successfully highlighted entries
   
   • Results Table: Interactive table with your results
     - Double-click Excel File to open it
     - Double-click PDF File to view original
     - Double-click "Yes" in Highlighted column to view highlighted PDF

5. EXPORT RESULTS
   Click "Save Results to CSV" to export all data for further analysis.

WHAT THE TOOL DOES
------------------
1. Finds FAI folders and matching Material CoC folders
2. Extracts tables from Excel files (Cablex P/N, FAIR Identifier, Part Number)
3. Matches PDFs using flexible naming patterns
4. Performs OCR on scanned PDFs to make them searchable
5. Searches for part numbers in PDFs
6. Highlights found part numbers with yellow markers
7. Adds "Matched Part Number: [number]" text at top of highlighted PDFs
8. Creates searchable PDF outputs with embedded OCR text

PDF MATCHING
-----------
The tool uses flexible matching to find PDFs:
- Primary: {Cablex P/N}_{FAIR Identifier}_{date}.pdf
- Flexible: Any filename containing both identifiers
- Example matches: "139-3040_763360_30-07-2024.pdf", "763360-139-3040.pdf"

EXCEL FILE FORMAT
----------------
Excel files must contain a table with these columns:
- Cablex P/N: Part number identifier
- FAIR Identifier: Quality/inspection identifier
- Part Number: The specific part number to search in PDFs

The tool intelligently finds these tables even in complex Excel files.

OUTPUT FILES
-----------
• Highlighted PDFs:
  - Yellow highlights on matched text
  - Red text annotation at top showing matched part number
  - Fully searchable with OCR-embedded text
  - Location depends on output mode selected

• CSV Results:
  - Complete processing results
  - All matching details and status information
  - Can be opened in Excel for analysis

TROUBLESHOOTING
--------------
• "No results found"
  → Check directory structure matches expected format
  → Ensure Excel files contain required columns
  → Verify PDF naming includes identifiers

• "OCR Not Available"
  → Install Tesseract OCR and Poppler utilities
  → See README.md for installation instructions

• Part numbers not found
  → Enable "Force OCR" for scanned documents
  → Check that part numbers in Excel match PDF content
  → Some PDFs may have poor scan quality

SYSTEM REQUIREMENTS
------------------
• Python 3.8+
• Tesseract OCR engine
• Poppler utilities
• See README.md for detailed installation

SUPPORT
-------
For issues or questions, check the README.md file or open an issue on GitHub.

============================================================
"""
        
        help_text.insert(1.0, help_content)
        help_text.config(state='disabled')  # Make read-only
        
        # Close button
        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=10)
        
        # Center the help window
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center on parent window
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (help_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
            
    def update_progress(self, message, progress, file_info=None):
        """Update progress bar and status"""
        self.status_label.config(text=message)
        
        # Update file progress label and progress bar if file info provided
        if file_info:
            self.current_file_info = file_info
            file_label = f"{file_info['filename']} ({file_info['current']}/{file_info['total']})"
            self.file_progress_label.config(text=file_label)
            # Set progress bar based on file count
            file_progress = (file_info['current'] / file_info['total']) * 100 if file_info['total'] > 0 else 0
            self.progress_var.set(file_progress)
        else:
            self.progress_var.set(progress)
        
        self.root.update_idletasks()
        
    def update_detailed_progress(self, message, progress, file_info=None):
        """Update detailed progress with step-by-step information"""
        self.status_label.config(text=message[:80] + "..." if len(message) > 80 else message)
        
        # Update file progress label and progress bar if file info provided
        if file_info:
            self.current_file_info = file_info
            file_label = f"{file_info['filename']} ({file_info['current']}/{file_info['total']})"
            self.file_progress_label.config(text=file_label)
            # Set progress bar based on file count
            file_progress = (file_info['current'] / file_info['total']) * 100 if file_info['total'] > 0 else 0
            self.progress_var.set(file_progress)
        else:
            self.progress_var.set(progress)
        
        # Append to progress text area
        self.progress_text.insert(tk.END, f"[{progress:3.0f}%] {message}\n")
        self.progress_text.see(tk.END)  # Auto-scroll to bottom
        self.root.update_idletasks()
        
    def stop_processing_func(self):
        """Stop the current processing"""
        self.stop_processing = True
        self.status_label.config(text="Stopping...")
        self.stop_btn.config(state='disabled')
    
    def reset_gui(self):
        """Reset GUI to initial state for another run"""
        # Clear results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.full_results = []
        
        # Clear progress
        self.progress_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.file_progress_label.config(text="")
        
        # Clear summary
        self.results_summary.config(text="")
        
        # Reset status
        self.status_label.config(text="Ready")
        
        # Reset buttons
        self.process_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.reset_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        
        # Reset stop flag
        self.stop_processing = False
        self.processor = None
    
    def process_files(self):
        """Process files in background thread"""
        directory = self.dir_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a directory")
            return
            
        self.process_btn.config(state='disabled')
        self.stop_btn.config(state='enabled')
        self.reset_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.progress_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.stop_processing = False
        
        # Add initial message
        self.progress_text.insert(tk.END, f"Starting processing for: {directory}\n")
        self.progress_text.insert(tk.END, "="*80 + "\n")
        
        def run_processing():
            try:
                # Get processing options
                force_ocr = self.force_ocr_var.get()
                output_mode = self.output_mode_var.get()
                separate_output = (output_mode == "separate")
                destructive = (output_mode == "destructive")
                
                # Create processor with options
                self.processor = PDFExcelProcessor(
                    directory,
                    force_ocr=force_ocr,
                    separate_output=separate_output,
                    destructive=destructive
                )
                
                # Create a wrapper for detailed callback that runs in main thread
                # Clear table before processing
                self.root.after(0, lambda: self.results_tree.delete(*self.results_tree.get_children()))
                self.root.after(0, lambda: self.results_summary.config(text=""))
                
                def detailed_callback_wrapper(msg, prog, file_info=None):
                    self.root.after(0, self.update_detailed_progress, msg, prog, file_info)
                
                results = self.processor.process_directory(
                    progress_callback=self.update_progress,
                    detailed_callback=detailed_callback_wrapper,
                    stop_flag=lambda: self.stop_processing
                )
                
                # Check if stopped
                if self.stop_processing:
                    self.root.after(0, lambda: self.status_label.config(text="Processing stopped by user"))
                    self.root.after(0, lambda: self.progress_text.insert(tk.END, "\n*** Processing stopped by user ***\n"))
                else:
                    # Display results
                    self.root.after(0, self.display_results, results)
                
            except Exception as e:
                error_msg = f"Error: {str(e)}\n{type(e).__name__}"
                self.root.after(0, lambda: self.progress_text.insert(tk.END, f"\n{error_msg}\n"))
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                import traceback
                logger.error(f"Processing error: {traceback.format_exc()}")
            finally:
                # Re-enable buttons
                self.root.after(0, lambda: self.process_btn.config(state='normal'))
                self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
                self.root.after(0, lambda: self.reset_btn.config(state='normal'))
                
        self.processing_thread = threading.Thread(target=run_processing, daemon=True)
        self.processing_thread.start()
        
    def open_file(self, file_path):
        """Open a file using the system's default application"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                messagebox.showwarning("File Not Found", f"File does not exist: {file_path.name}")
                return
            
            # Open file based on OS
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(file_path)])
            elif platform.system() == 'Windows':
                os.startfile(str(file_path))
            else:  # Linux and others
                subprocess.run(['xdg-open', str(file_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def on_item_double_click(self, event):
        """Handle double-click on table item to open files"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        # Get column clicked
        column = self.results_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        if col_index == 0:  # Excel File column
            # Open Excel file
            excel_file = values[5]  # Full path stored in tag
            if excel_file:
                self.open_file(excel_file)
        elif col_index == 3:  # PDF File column
            # Open PDF file
            if values[2] == 'Found':  # Check if PDF was found
                pdf_file = values[6]  # Full path stored in tag
                if pdf_file:
                    self.open_file(pdf_file)
        elif col_index == 4:  # Highlighted column
            # Open highlighted PDF
            if values[4] == 'Yes':
                highlighted_file = values[7]  # Full path stored in tag
                if highlighted_file:
                    self.open_file(highlighted_file)
    
    def apply_filter(self, event=None):
        """Apply filter to the results table"""
        # Clear current items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        filter_value = self.filter_var.get()
        
        # Apply filter and repopulate
        for row_data in self.full_results:
            excel_file, part_number, pdf_status, pdf_file, highlighted, excel_path, pdf_path, highlighted_path = row_data
            
            # Apply filter logic
            if filter_value == "All":
                show = True
            elif filter_value == "PDF Found":
                show = (pdf_status == "Found")
            elif filter_value == "PDF Not Found":
                show = (pdf_status == "Not Found")
            elif filter_value == "Part Number Not Found":
                show = (pdf_status == "Found" and highlighted == "No")
            elif filter_value == "Part Number Found":
                show = (highlighted == "Yes")
            else:
                show = True
            
            if show:
                # Insert with full paths as tags for opening files
                item_id = self.results_tree.insert('', 'end', 
                    values=(excel_file, part_number, pdf_status, pdf_file, highlighted,
                           excel_path, pdf_path, highlighted_path))
    
    def display_results(self, results):
        """Display processing results"""
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.full_results = []
        
        if results.empty:
            self.results_summary.config(text="No results found.")
        else:
            # Summary statistics
            total_rows = len(results)
            pdfs_found = len(results[results['PDF Status'] == 'Found'])
            parts_found = len(results[results['Part Number Found'] == 'Yes'])
            
            summary = f"Processing Complete! | "
            summary += f"Total entries: {total_rows} | "
            summary += f"PDFs found: {pdfs_found}/{total_rows} | "
            if pdfs_found > 0:
                summary += f"Part numbers highlighted: {parts_found}/{pdfs_found}"
            
            self.results_summary.config(text=summary)
            
            # Populate table
            for idx, row in results.iterrows():
                excel_file = row.get('Excel File', '')
                part_number = row.get('Part Number', '')
                pdf_status = row.get('PDF Status', 'Not Found')
                pdf_file = row.get('PDF File', '') if pdf_status == 'Found' else ''
                part_found = row.get('Part Number Found', 'N/A')
                highlighted = 'Yes' if part_found == 'Yes' else 'No' if pdf_status == 'Found' else 'N/A'
                
                # Build full paths
                excel_path = ''
                if excel_file:
                    fai_folder = f"FAI {row.get('FAI Folder', '')}"
                    excel_path = str(self.processor.base_path / fai_folder / excel_file)
                
                pdf_path = ''
                if pdf_file:
                    coc_folder = f"Material CoC {row.get('FAI Folder', '')}"
                    pdf_path = str(self.processor.base_path / coc_folder / pdf_file)
                
                highlighted_path = ''
                if row.get('Highlighted PDF'):
                    if self.processor.separate_output and self.processor.output_folder:
                        # Check if we have source folder info
                        source_folder = row.get('Source Folder', '')
                        if source_folder:
                            highlighted_path = str(self.processor.output_folder / source_folder / row.get('Highlighted PDF'))
                        else:
                            highlighted_path = str(self.processor.output_folder / row.get('Highlighted PDF'))
                    else:
                        coc_folder = f"Material CoC {row.get('FAI Folder', '')}"
                        highlighted_path = str(self.processor.base_path / coc_folder / row.get('Highlighted PDF'))
                
                # Store full data including paths
                row_data = (excel_file, part_number, pdf_status, pdf_file, highlighted,
                           excel_path, pdf_path, highlighted_path)
                self.full_results.append(row_data)
                
                # Insert into tree (paths are stored in values for access)
                self.results_tree.insert('', 'end', 
                    values=row_data)
            
        self.process_btn.config(state='normal')
        self.save_btn.config(state='normal')
        
    def save_results(self):
        """Save results to CSV"""
        if not self.processor or self.processor.results_df.empty:
            messagebox.showerror("Error", "No results to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            output_path = self.processor.save_results(file_path)
            messagebox.showinfo("Success", f"Results saved to {output_path}")


# Main entry point - GUI only
def main():
    """Launch FAI PDF Processor GUI"""
    root = tk.Tk()
    app = ProcessorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
