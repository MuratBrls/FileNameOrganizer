"""
Validation functions for file renaming operations.
"""
import os
import re
from pathlib import Path
from config import WINDOWS_FORBIDDEN_CHARS, RESERVED_NAMES, MAX_FILENAME_LENGTH, MAX_PATH_LENGTH


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_base_name(name):
    """
    Validate the base name for file renaming.
    
    Args:
        name (str): The base name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Base name cannot be empty"
    
    # Check for forbidden characters
    forbidden_pattern = f"[{re.escape(WINDOWS_FORBIDDEN_CHARS)}]"
    if re.search(forbidden_pattern, name):
        forbidden_found = [c for c in WINDOWS_FORBIDDEN_CHARS if c in name]
        return False, f"Base name contains forbidden characters: {', '.join(forbidden_found)}"
    
    # Check for reserved names (Windows)
    name_upper = name.upper()
    if name_upper in RESERVED_NAMES:
        return False, f"'{name}' is a reserved system name and cannot be used"
    
    # Check for leading/trailing spaces or dots (problematic on Windows)
    if name != name.strip():
        return False, "Base name cannot have leading or trailing spaces"
    
    if name.endswith('.'):
        return False, "Base name cannot end with a period"
    
    return True, ""


def validate_start_number(number):
    """
    Validate the starting number for sequential renaming.
    
    Args:
        number: The starting number to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        num = int(number)
        if num < 0:
            return False, "Starting number must be non-negative"
        if num > 999999:
            return False, "Starting number is too large (max: 999999)"
        return True, ""
    except (ValueError, TypeError):
        return False, "Starting number must be a valid integer"


def validate_separator(separator):
    """
    Validate the separator character.
    
    Args:
        separator (str): The separator to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if separator is None:
        separator = ""
    
    # Separator can be empty
    if len(separator) == 0:
        return True, ""
    
    # Check for forbidden characters
    forbidden_pattern = f"[{re.escape(WINDOWS_FORBIDDEN_CHARS)}]"
    if re.search(forbidden_pattern, separator):
        return False, f"Separator contains forbidden characters"
    
    # Limit length
    if len(separator) > 5:
        return False, "Separator is too long (max: 5 characters)"
    
    return True, ""


def validate_file_access(filepath):
    """
    Check if a file is accessible and not locked.
    
    Args:
        filepath (str or Path): Path to the file
        
    Returns:
        tuple: (is_accessible, error_message)
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False, "File does not exist"
    
    if not filepath.is_file():
        return False, "Path is not a file"
    
    # Try to access the file
    try:
        # Attempt to open in append mode (doesn't truncate, works with read-only)
        with open(filepath, 'a'):
            pass
        return True, ""
    except PermissionError:
        return False, "File is locked or you don't have permission"
    except OSError as e:
        return False, f"Cannot access file: {str(e)}"


def validate_path_length(new_path):
    """
    Validate that the new path doesn't exceed OS limitations.
    
    Args:
        new_path (str or Path): The new file path
        
    Returns:
        tuple: (is_valid, error_message)
    """
    new_path = Path(new_path)
    
    # Check filename length
    filename = new_path.name
    if len(filename) > MAX_FILENAME_LENGTH:
        return False, f"Filename too long ({len(filename)} > {MAX_FILENAME_LENGTH} chars)"
    
    # Check total path length (Windows limitation)
    full_path = str(new_path.resolve())
    if len(full_path) > MAX_PATH_LENGTH:
        return False, f"Full path too long ({len(full_path)} > {MAX_PATH_LENGTH} chars)"
    
    return True, ""


def validate_files_list(files):
    """
    Validate a list of files for batch renaming.
    
    Args:
        files (list): List of file paths
        
    Returns:
        tuple: (is_valid, error_message, details_dict)
    """
    if not files:
        return False, "No files selected", {}
    
    details = {
        "total": len(files),
        "accessible": 0,
        "locked": 0,
        "missing": 0,
        "errors": []
    }
    
    for filepath in files:
        is_accessible, error_msg = validate_file_access(filepath)
        if is_accessible:
            details["accessible"] += 1
        else:
            if "does not exist" in error_msg:
                details["missing"] += 1
            elif "locked" in error_msg or "permission" in error_msg.lower():
                details["locked"] += 1
            details["errors"].append({
                "file": str(filepath),
                "error": error_msg
            })
    
    if details["accessible"] == 0:
        return False, "No accessible files found", details
    
    return True, "", details


def validate_rename_operation(old_path, new_path):
    """
    Validate a single rename operation before execution.
    
    Args:
        old_path (str or Path): Original file path
        new_path (str or Path): New file path
        
    Returns:
        tuple: (is_valid, error_message)
    """
    old_path = Path(old_path)
    new_path = Path(new_path)
    
    # Check if source exists
    if not old_path.exists():
        return False, f"Source file does not exist: {old_path.name}"
    
    # Check if source is accessible
    is_accessible, error = validate_file_access(old_path)
    if not is_accessible:
        return False, error
    
    # Check if paths are the same
    if old_path.resolve() == new_path.resolve():
        return False, "Source and destination are the same"
    
    # Check destination path length
    is_valid_length, error = validate_path_length(new_path)
    if not is_valid_length:
        return False, error
    
    # Check if destination directory is writable
    dest_dir = new_path.parent
    if not os.access(dest_dir, os.W_OK):
        return False, f"Destination directory is not writable: {dest_dir}"
    
    return True, ""
