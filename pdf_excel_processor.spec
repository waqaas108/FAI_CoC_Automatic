# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for FAI/Material CoC Processor
# Use: pyinstaller pdf_excel_processor.spec

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['pdf_excel_processor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'fitz',
        'PyMuPDF',
        'click',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Single file executable
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FAI_Processor',
    debug=False,
    bootloader_ignore_signals=False,
