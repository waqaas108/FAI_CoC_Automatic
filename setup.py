"""
Setup script for cx_Freeze to create executable
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["pandas", "openpyxl", "fitz", "click", "tkinter", "threading", "concurrent.futures"],
    "includes": ["tkinter", "tkinter.ttk", "tkinter.scrolledtext", "tkinter.filedialog", "tkinter.messagebox"],
    "include_files": ["requirements.txt", "README.md"],
    "excludes": ["matplotlib", "scipy", "numpy.testing"],
}

# Base for GUI applications
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "pdf_excel_processor.py",
        base=base,
        target_name="FAI_Processor",
        icon=None  # Add path to .ico file if you have one
    )
]

setup(
    name="FAI Material CoC Processor",
    version="1.0.0",
    description="Process FAI Excel sheets and Material CoC PDFs",
    author="Your Name",
    options={"build_exe": build_exe_options},
    executables=executables
)
