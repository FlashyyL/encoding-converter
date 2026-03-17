#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Encoding Converter - Main Entry Point

Features:
- Detect file encoding
- Batch convert file encoding
- Support multiple common encoding formats

Usage:
    python main.py
"""

import sys
import tkinter as tk
from gui import EncodingConverterGUI


def check_dependencies():
    """Check required dependencies"""
    try:
        import chardet
        return True
    except ImportError:
        print("[ERROR] - Missing dependency: chardet")
        print("[INFO] - Please install: pip install chardet")
        return False


def main():
    """Main function"""
    print("[INFO] - Starting File Encoding Converter...")
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        # Create main window
        root = tk.Tk()
        
        # Set DPI awareness (Windows)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # Create application
        app = EncodingConverterGUI(root)
        
        # Run main loop
        print("[INFO] - GUI started")
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] - Program error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("[INFO] - Program exited")


if __name__ == '__main__':
    main()