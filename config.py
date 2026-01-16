"""
Configuration constants and settings for the Batch Renamer application.
"""
import os
from pathlib import Path

# Application Metadata
APP_NAME = "Batch File Renamer"
APP_VERSION = "1.0.0"
AUTHOR = "FileNameOrganizer"

# Default Settings
DEFAULT_SEPARATOR = "_"
DEFAULT_START_NUMBER = 1
DEFAULT_SORT_METHOD = "alphabetical"  # Options: alphabetical, date_modified, date_created, selection_order
DEFAULT_CONFLICT_RESOLUTION = "auto_increment"  # Options: skip, add_suffix, prompt, auto_increment
DEFAULT_PADDING = "auto"  # Options: auto, none, 2, 3, 4

# File System Constraints
MAX_FILENAME_LENGTH = 255  # Maximum filename length (most file systems)
MAX_PATH_LENGTH = 260  # Windows MAX_PATH limitation
WINDOWS_FORBIDDEN_CHARS = r'<>:"/\|?*'  # Characters forbidden in Windows filenames
RESERVED_NAMES = [
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
]

# UI Settings
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Supported Sort Methods
SORT_METHODS = {
    "alphabetical": "Alphabetical (A-Z)",
    "date_modified": "Date Modified (Oldest First)",
    "date_modified_desc": "Date Modified (Newest First)",
    "date_created": "Date Created (Oldest First)",
    "date_created_desc": "Date Created (Newest First)",
    "selection_order": "Selection Order"
}

# Conflict Resolution Strategies
CONFLICT_STRATEGIES = {
    "skip": "Skip (Keep Original)",
    "add_suffix": "Add Suffix (_copy)",
    "auto_increment": "Auto-increment Number",
    "prompt": "Prompt for Each"
}

# Padding Options
PADDING_OPTIONS = {
    "auto": "Auto-detect",
    "none": "No Padding (1, 2, 3...)",
    "2": "2 Digits (01, 02, 03...)",
    "3": "3 Digits (001, 002, 003...)",
    "4": "4 Digits (0001, 0002, 0003...)"
}

# Colors for UI (Preview highlighting)
COLOR_SAFE = "#2ecc71"      # Green - safe to rename
COLOR_WARNING = "#f39c12"   # Orange - potential conflict
COLOR_ERROR = "#e74c3c"     # Red - error/locked file
COLOR_BG = "#ecf0f1"        # Light gray background
COLOR_ACCENT = "#3498db"    # Blue accent

class RenameConfig:
    """Configuration class for rename operations."""
    
    def __init__(self):
        self.base_name = ""
        self.start_number = DEFAULT_START_NUMBER
        self.separator = DEFAULT_SEPARATOR
        self.sort_method = DEFAULT_SORT_METHOD
        self.conflict_resolution = DEFAULT_CONFLICT_RESOLUTION
        self.padding = DEFAULT_PADDING
        
    def get_padding_width(self, total_files):
        """Calculate padding width based on configuration and file count."""
        if self.padding == "auto":
            # Auto-detect based on total file count
            if total_files < 10:
                return 0
            elif total_files < 100:
                return 2
            elif total_files < 1000:
                return 3
            else:
                return 4
        elif self.padding == "none":
            return 0
        else:
            return int(self.padding)
    
    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            "base_name": self.base_name,
            "start_number": self.start_number,
            "separator": self.separator,
            "sort_method": self.sort_method,
            "conflict_resolution": self.conflict_resolution,
            "padding": self.padding
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create configuration from dictionary."""
        config = cls()
        config.base_name = data.get("base_name", "")
        config.start_number = data.get("start_number", DEFAULT_START_NUMBER)
        config.separator = data.get("separator", DEFAULT_SEPARATOR)
        config.sort_method = data.get("sort_method", DEFAULT_SORT_METHOD)
        config.conflict_resolution = data.get("conflict_resolution", DEFAULT_CONFLICT_RESOLUTION)
        config.padding = data.get("padding", DEFAULT_PADDING)
        return config
