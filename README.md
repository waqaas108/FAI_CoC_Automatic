# FAI PDF Processor

A powerful desktop application for processing FAI (First Article Inspection) Excel sheets and Material CoC (Certificate of Compliance) PDFs. This tool automates the matching, searching, and highlighting of part numbers across documents, with full OCR support for scanned PDFs.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 🎯 Key Features

### Document Processing
- **Smart Excel Parsing**: Automatically extracts tables from complex Excel files with mixed content
- **Flexible PDF Matching**: Intelligently matches PDFs using Cablex P/N and FAIR Identifier patterns
- **Advanced OCR**: Processes scanned PDFs using Tesseract OCR to make them searchable
- **Visual Highlighting**: Creates highlighted PDFs with yellow markers on found part numbers
- **Batch Processing**: Handles entire directory structures with hundreds of files efficiently

### User Interface
- **Interactive GUI**: Modern interface with real-time progress tracking
- **Clickable Results Table**: Double-click to open Excel files, PDFs, or highlighted outputs
- **Smart Filtering**: Filter results by "All", "PDF Found", "PDF Not Found", "Part Number Not Found", or "Part Number Found"
- **File-Based Progress**: Progress bar shows Excel file processing (e.g., 6/11 files)
- **Process Controls**: Stop current processing or Reset for a new run
- **Built-in Help**: Comprehensive help dialog accessible with one click
- **CLI Support**: Full command-line interface for automation and scripting

### Output Options
- **Centralized Results**: Option to save all highlighted PDFs in a single output folder
- **Destructive Mode**: Option to replace original PDFs in-place (no backup)
- **CSV Export**: Comprehensive results export with all matching details
- **Searchable PDFs**: OCR-processed PDFs become fully searchable with selectable text

### Advanced Features
- **Recursive Search**: Finds FAI and CoC folders in subdirectories (up to depth 3)
- **Force OCR**: Option to force OCR on all PDFs regardless of text content
- **Auto-sizing Window**: GUI automatically adjusts to fit content

## 📥 Quick Start (Pre-built Executables)

### Windows
1. Download `FAI_PDF_Processor.exe` from [Releases](../../releases)
2. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
3. Install [Poppler](http://blog.alivate.com.au/poppler-windows/)
4. Double-click the executable to run

### macOS
1. Download `FAI_PDF_Processor.dmg` from [Releases](../../releases)
2. Install Tesseract: `brew install tesseract poppler`
3. Drag the app to Applications folder
4. Open the app (you may need to allow it in Security settings)

### Linux
1. Download `FAI_PDF_Processor.AppImage` from [Releases](../../releases)
3. Make executable: `chmod +x FAI_PDF_Processor.AppImage`
4. Run: `./FAI_PDF_Processor.AppImage`

## 🔧 Installation from Source

### 1. Install System Dependencies for OCR

**Linux (Ubuntu/Debian):**
```bash
# Run the installation script
./install_ocr.sh

# Or manually:
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils
```

**macOS:**
```bash
# Using Homebrew
brew install tesseract poppler
```

**Windows:**
1. Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download and install Poppler from: http://blog.alivate.com.au/poppler-windows/
3. Add both to your system PATH

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python pdf_excel_processor.py --help
```

To check if OCR is properly installed:
```bash
python -c "import pytesseract; print('OCR is ready!')"
```

## 💻 Usage

### GUI Mode

1. **Launch the application**:
   ```bash
   python pdf_excel_processor.py --gui
   ```

2. **Select your directory** containing FAI and Material CoC folders

3. **Configure options**:
   - ✅ **Force OCR**: Process all PDFs with OCR (recommended for scanned documents)
   - Choose output mode:
     - **Separate folder** (safe): Saves highlighted PDFs in `highlighted_pdfs/` folder
     - **In-place** (destructive): Replaces original PDFs directly

4. **Click "Process Files"** to start
   - Monitor progress bar (shows file count: 6/11)
   - View detailed progress in the log area
   - Click **Stop** to halt processing at any time

5. **Review results** in the interactive table:
   - **Double-click** Excel files to open them
   - **Double-click** PDF files to view originals
   - **Double-click** "Yes" in Highlighted column to view highlighted PDFs
   - Use **Filter** dropdown to focus on specific results

6. **Click "Reset"** to clear and start a new run

7. **Click "Help"** for comprehensive usage instructions

### CLI Mode

**Basic usage:**
```bash
python pdf_excel_processor.py --path "/path/to/directory"
```

**Advanced options:**
```bash
# With all features enabled (default)
python pdf_excel_processor.py --path "/path/to/dir" --output results.csv

# Disable force OCR (faster for text-based PDFs)
python pdf_excel_processor.py --path "/path/to/dir" --no-force-ocr

# Destructive mode (replace originals)
python pdf_excel_processor.py --path "/path/to/dir" --destructive

# Verbose mode for debugging
python pdf_excel_processor.py --path "/path/to/dir" --verbose
```

## Error Handling

The application handles:
- Missing Excel columns
- Corrupted PDF files
- Invalid directory structures
- Permission errors
- Memory management for large files

## Performance Tips

1. **For large datasets**: Use CLI mode for better performance
2. **Memory usage**: Process directories in batches if handling thousands of files
3. **PDF processing**: Highlighted PDFs are saved separately to preserve originals

## Troubleshooting

### Common Issues:

**ImportError for PyMuPDF:**
```bash
pip uninstall PyMuPDF
pip install PyMuPDF --no-cache-dir
```

**Tkinter not found (Linux):**
```bash
sudo apt-get install python3-tk
```

**Excel file not reading:**
- Ensure Excel file is not corrupted
- Check that required columns exist
- Try opening and re-saving the Excel file

**PDF highlighting not working:**
- Verify PDF is not encrypted
- Check PDF is not a scanned image
- Ensure Part Number text is searchable in PDF

## License

This software is provided as-is for internal use.

## Support

For issues or questions, please check the logs with `--verbose` flag first.
