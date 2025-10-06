# Changelog

## [1.2.0] - 2024-10-05

### Added
- **Stop Button**: Gracefully stop processing at any time during execution
- **Reset Button**: Clear all results and start a new run without restarting the application
- **Help Button**: Built-in comprehensive help dialog with full usage instructions
- **Recursive Directory Search**: Finds FAI and CoC folders in subdirectories up to depth 3
- **PDF Found Filter**: New filter option to show only entries where PDFs were matched
- **Destructive Mode**: Option to replace original PDFs in-place (no backup created)

### Changed
- **File-Based Progress Bar**: Progress bar now shows Excel file processing (e.g., 6/11 files) instead of step-based progress
- **Auto-sizing Window**: Window automatically adjusts to fit content (no fixed size)
- **Output Mode Radio Buttons**: Changed from checkbox to radio buttons for clearer output selection
- **Enhanced Filter Options**: Now includes "All", "PDF Found", "PDF Not Found", "Part Number Not Found", "Part Number Found"

### Improved
- Better progress visibility during long OCR operations
- More intuitive progress tracking
- Cleaner GUI layout with button grouping
- Stop functionality checks at multiple points for responsive cancellation

## [1.0.0] - 2024-10-05

### Added
- **Interactive Results Table**: Replaced text output with clickable table for easy file access
- **Smart Filtering**: Added dropdown filter for "PDF Not Found", "Part Number Not Found", and "Part Number Found"  
- **Double-Click to Open**: Click any cell in the table to open associated Excel files, PDFs, or highlighted outputs
- **Force OCR Option**: Checkbox to force OCR on all PDFs (enabled by default)
- **Separate Output Folder**: Option to save all highlighted PDFs in central 'highlighted_pdfs' folder
- **Flexible PDF Matching**: Improved algorithm to find PDFs even with non-standard naming
- **Searchable OCR PDFs**: OCR text is embedded as searchable layer in output PDFs
- **Cross-Platform Support**: Build scripts for Windows, macOS, and Linux
- **Progress Details Window**: Step-by-step processing information

### Changed
- Results summary now shows as single line above table
- PDF highlights now placed on actual text positions (not just annotations)
- Red text annotation added at top of highlighted PDFs showing matched part number

### Fixed
- OCR now works with all scanned PDFs
- PDF text layer properly preserved for searchability
- Improved Excel parsing for messy sheets with mixed content

### Technical
- Added platform detection for OS-specific file opening
- Improved memory management for large batch processing
- Better error handling and logging
- PyInstaller spec file updated for all platforms

## Previous Versions

### [0.9.0] - Initial Release
- Basic Excel and PDF processing
- GUI and CLI interfaces  
- Simple text search in PDFs
- CSV export functionality
