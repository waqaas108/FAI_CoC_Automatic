# Version 1.1 Updates

## Changes Implemented

### 1. ✅ Auto-sizing Window
- **Removed fixed window dimensions** - Window now automatically wraps around all GUI elements
- **Set minimum size** after initial layout to prevent shrinking below usable size
- Window adapts to content rather than having unused space

### 2. ✅ Enhanced Filtering Options
- **Added "PDF Found" filter** to the dropdown menu
- Filter options now include:
  - All (shows everything)
  - **PDF Found** (new - shows only entries where PDF was matched)
  - PDF Not Found (shows entries without matching PDFs)
  - Part Number Not Found (shows PDFs found but part number not highlighted)
  - Part Number Found (shows successfully highlighted entries)

### 3. ✅ Destructive In-Place Replacement Mode
- **Replaced checkbox with radio buttons** for output mode selection:
  - **Option 1**: Save highlighted PDFs in separate 'highlighted_pdfs' folder (default)
  - **Option 2**: Replace original PDFs in-place (destructive - no backup)
  
- **Destructive mode behavior**:
  - OCRs and highlights the original PDF files directly
  - No new files created - originals are overwritten
  - **Warning**: No backup is created - use with caution!
  
- **Available in both GUI and CLI**:
  ```bash
  # CLI with destructive mode
  python pdf_excel_processor.py --path "/path/to/dir" --destructive
  ```

### 4. ✅ Enhanced Progress Tracking
- **File information display** added next to "Progress Details:" label
- Shows current file being processed with format: `filename.xlsx (6/11)`
- Updates in real-time as each Excel file is processed
- Provides clear visibility into:
  - Current file name
  - Current file number
  - Total number of files

## Technical Implementation Details

### Window Auto-sizing
```python
# Removed: self.root.geometry("1000x700")
# Added: Auto-sizing with minimum constraints
self.root.update_idletasks()
self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
```

### Destructive Mode Logic
```python
if self.destructive:
    output_path = pdf_path  # Replace original
elif self.separate_output and self.output_folder:
    output_path = self.output_folder / f"highlighted_{pdf_path.name}"
else:
    output_path = pdf_path.parent / f"highlighted_{pdf_path.name}"
```

### Progress File Info
```python
file_info = {
    'filename': excel_file.name,
    'current': idx + 1,
    'total': total_files
}
# Displayed as: "filename.xlsx (6/11)"
```

## User Impact

### Benefits
1. **Better UI/UX**: Window fits content perfectly without wasted space
2. **More filtering options**: Easier to find specific types of results
3. **Flexible output**: Choose between safe (separate folder) or destructive (in-place) modes
4. **Better progress visibility**: Always know which file is being processed and progress

### Breaking Changes
- None - all changes are additive or improvements

### Migration Notes
- Existing workflows continue to work as before
- Default behavior unchanged (separate output folder)
- New destructive mode is opt-in only

## Testing Recommendations

1. **Test auto-sizing** on different screen resolutions
2. **Verify "PDF Found" filter** shows correct entries
3. **Test destructive mode** on a copy of data first (no undo!)
4. **Confirm file progress** updates correctly during processing

## CLI Examples

```bash
# Standard processing (safe mode)
python pdf_excel_processor.py --path "/path/to/dir"

# Destructive mode (replace originals)
python pdf_excel_processor.py --path "/path/to/dir" --destructive

# Destructive with no OCR forcing
python pdf_excel_processor.py --path "/path/to/dir" --destructive --no-force-ocr
```

---

**Version**: 1.1.0  
**Date**: 2024-10-05  
**Status**: Ready for testing
