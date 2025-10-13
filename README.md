# FAI PDF Processor

A powerful Windows desktop application for processing FAI (First Article Inspection) Excel sheets and Material CoC (Certificate of Compliance) PDFs. This tool automates the matching, searching, and highlighting of part numbers across documents, with full OCR support for scanned PDFs.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)

## 🎯 Key Features

### Document Processing
- **Smart Excel Parsing**: Automatically extracts tables from complex Excel files with mixed content
- **Flexible PDF Matching**: Intelligently matches PDFs using Cablex P/N and FAIR Identifier patterns
- **Advanced OCR**: Processes scanned PDFs using Tesseract OCR to make them searchable
- **Visual Highlighting**: Creates highlighted PDFs with yellow markers on found part numbers
- **Parallel Processing**: Uses multithreading to process multiple PDFs simultaneously (up to 8 threads)
- **Batch Processing**: Handles entire directory structures with hundreds of files efficiently

### User Interface
- **Interactive GUI**: Modern interface with real-time progress tracking
- **Clickable Results Table**: Double-click to open Excel files, PDFs, or highlighted outputs
- **Smart Filtering**: Filter results by "All", "PDF Found", "PDF Not Found", "Part Number Not Found", or "Part Number Found"
- **File-Based Progress**: Progress bar shows Excel file processing with real-time updates
- **Process Controls**: Stop current processing or Reset for a new run
- **Built-in Help**: Comprehensive help dialog accessible with one click

### Output Options
- **Centralized Results**: Option to save all highlighted PDFs in a single output folder
- **CSV Export**: Comprehensive results export with all matching details
- **Searchable PDFs**: OCR-processed PDFs become fully searchable with selectable text

### Advanced Features
- **Recursive Search**: Finds FAI and CoC folders in subdirectories (up to depth 3)
- **Force OCR**: Option to force OCR on all PDFs regardless of text content
- **Auto-sizing Window**: GUI automatically adjusts to fit content

## 🚀 Quick Start

### Prerequisites
1. **Python 3.11 or later** - [Download from python.org](https://www.python.org/downloads/)
2. **Tesseract OCR** - [Download from GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
3. **Poppler utilities** - Included in repository as `poppler.zip`

### Running the Application

1. **Clone or download this repository**
2. **Double-click `run.bat`**

That's it! The script will:
- ✅ Verify Python is installed
- ✅ Check for Tesseract OCR
- ✅ Install Python dependencies automatically
- ✅ Extract and configure Poppler utilities
- ✅ Launch the GUI application

**Note:** See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup guide and troubleshooting.

## 🔧 Manual Installation

### 1. Install Python 3.11+
Download and install from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### 2. Install Tesseract OCR
Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Install to default location: `C:\Program Files\Tesseract-OCR`

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python pdf_excel_processor.py
```

The application will automatically:
- Detect Tesseract installation
- Extract Poppler from included `poppler.zip`
- Configure all paths for the session

## 💻 Usage

### Launching the Application

**Option 1: Using run.bat (Recommended)**
```bash
run.bat
```

**Option 2: Direct Python execution**
```bash
python pdf_excel_processor.py
```

### Using the GUI

1. **Select your directory** containing FAI and Material CoC folders

2. **Configure options**:
   - ✅ **Force OCR**: Process all PDFs with OCR (recommended for scanned documents)
   - Choose output mode:
     - **Separate folder** (safe): Saves highlighted PDFs in `highlighted_pdfs/` folder

3. **Click "Process Files"** to start
   - Monitor progress bar with real-time updates
   - View detailed progress in the log area
   - Multiple PDFs are processed in parallel for faster performance
   - Click **Stop** to halt processing at any time

4. **Review results** in the interactive table:
   - **Double-click** Excel files to open them
   - **Double-click** PDF files to view originals
   - **Double-click** "Yes" in Highlighted column to view highlighted PDFs
   - Use **Filter** dropdown to focus on specific results

5. **Click "Reset"** to clear and start a new run

6. **Click "Help"** for comprehensive usage instructions

## Error Handling

The application handles:
- Missing Excel columns
- Corrupted PDF files
- Invalid directory structures
- Permission errors
- Memory management for large files

## Performance Tips

1. **Parallel Processing**: The application automatically uses up to 8 threads for PDF processing
2. **Memory usage**: Process directories in batches if handling thousands of files
3. **PDF processing**: Highlighted PDFs are saved separately to preserve originals
4. **PATH Configuration**: `run.bat` automatically configures all paths, even if system PATH is reset

## Troubleshooting

### Common Issues:

**Python not found:**
- Install Python 3.11+ from python.org
- Make sure "Add Python to PATH" was checked during installation
- Restart your computer after installation

**Tesseract not found:**
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`
- Restart your computer after installation

**Poppler not found:**
- Ensure `poppler.zip` is in the same folder as `run.bat`
- Delete the `poppler` folder and run `run.bat` again to re-extract

**PATH issues:**
- `run.bat` automatically configures PATH for each session
- No permanent system changes are needed
- If issues persist, try running as Administrator

**Excel file not reading:**
- Ensure Excel file is not corrupted
- Check that required columns exist
- Try opening and re-saving the Excel file

**PDF highlighting not working:**
- Verify PDF is not encrypted
- Check PDF is not a scanned image
- Ensure Part Number text is searchable in PDF

For more help, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## Project Structure

```
FAI_CoC_Automatic/
├── pdf_excel_processor.py    # Main application (GUI-only)
├── run.bat                    # Launch script (handles all setup)
├── poppler.zip                # Poppler utilities (auto-extracted)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── SETUP_INSTRUCTIONS.md      # Detailed setup guide
└── LICENSE                    # MIT License
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

For issues or questions:
1. Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed troubleshooting
2. Review the application logs in the GUI
3. Ensure all prerequisites are properly installed
