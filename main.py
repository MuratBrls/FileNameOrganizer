"""
Batch File Renamer - Main Entry Point

A utility for batch renaming files with sequential numbering and intelligent conflict resolution.
"""
import sys
import tkinter as tk
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gui import start

if __name__ == "__main__":
    start()
