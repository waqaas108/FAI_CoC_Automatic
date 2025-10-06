#!/usr/bin/env python3
"""
Quick Start Script for FAI/Material CoC Processor
Helps users get started quickly with the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        print("Please run manually: pip install -r requirements.txt")
        return False

def main():
    print("=" * 60)
    print("FAI/Material CoC Processor - Quick Start")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    print()
    
    # Install dependencies
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found")
        print("Please ensure you're in the correct directory")
        return
    
    install_dependencies()
    print()
    
    # Options menu
    print("What would you like to do?")
    print("1. Launch GUI interface")
    print("2. Run CLI with sample directory")
    print("3. Run test script")
    print("4. Build executable")
    print("5. View documentation")
    print("6. Exit")
    print()
    
    choice = input("Enter choice [1-6]: ").strip()
    
    if choice == "1":
        print("\nLaunching GUI...")
        subprocess.run([sys.executable, "pdf_excel_processor.py", "--gui"])
        
    elif choice == "2":
        sample_dir = "/home/waqaas/Nasir/RAW_Kit-05 363K004G01"
        if Path(sample_dir).exists():
            print(f"\nProcessing sample directory: {sample_dir}")
            subprocess.run([sys.executable, "pdf_excel_processor.py", "--path", sample_dir])
        else:
            dir_path = input("Enter directory path: ").strip()
            if Path(dir_path).exists():
                subprocess.run([sys.executable, "pdf_excel_processor.py", "--path", dir_path])
            else:
                print("Directory not found")
                
    elif choice == "3":
        print("\nRunning test script...")
        subprocess.run([sys.executable, "test_processor.py"])
        
    elif choice == "4":
        print("\nBuilding executable...")
        if sys.platform == "win32":
            subprocess.run(["build_executable.bat"])
        else:
            subprocess.run(["./build_executable.sh"])
            
    elif choice == "5":
        print("\nOpening README...")
        if sys.platform == "win32":
            os.system("type README.md | more")
        else:
            os.system("less README.md")
            
    elif choice == "6":
        print("Goodbye!")
        return
        
    else:
        print("Invalid choice")
    
    print()
    print("=" * 60)
    print("For more information, see README.md")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
