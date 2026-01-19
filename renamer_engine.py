"""
Core file renaming engine with sorting, conflict resolution, batch operations, and history logging.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Callable, Any
from config import RenameConfig
from validators import validate_rename_operation, validate_file_access
from history_manager import HistoryManager


class RenameResult:
    """Result of a rename operation."""
    def __init__(self, old_path, new_path, success=False, error=None):
        self.old_path = Path(old_path)
        self.new_path = Path(new_path)
        self.success = success
        self.error = error
    
    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.old_path.name} → {self.new_path.name}"


class FileRenamer:
    """Main file renaming engine."""
    
    def __init__(self, files: List[Path], config: RenameConfig, history_manager: Optional['HistoryManager'] = None):
        """
        Initialize the renamer.
        
        Args:
            files: List of file paths to rename
            config: RenameConfig object with settings
            history_manager: Optional shared HistoryManager instance
        """
        self.files = [Path(f) for f in files]
        self.config = config
        self.sorted_files = []
        self.rename_plan = []
        self.history_manager = history_manager if history_manager else HistoryManager()
        
    def extract_extension(self, filepath: Path) -> str:
        """
        Extract file extension safely.
        
        Args:
            filepath: Path to the file
            
        Returns:
            File extension including the dot (e.g., '.jpg'), or empty string
        """
        # Use pathlib's suffix (includes the dot)
        return filepath.suffix
    
    def generate_new_name(self, base_name: str, index: int, extension: str) -> str:
        """
        Generate a new filename with proper formatting.
        
        Args:
            base_name: Base name for the file
            index: Sequential index number
            extension: File extension (including dot)
            
        Returns:
            New filename as string
        """
        # Calculate padding width
        padding_width = self.config.get_padding_width(len(self.files))
        
        # Format the index with padding
        if padding_width > 0:
            index_str = str(index).zfill(padding_width)
        else:
            index_str = str(index)
        
        # Combine parts
        separator = self.config.separator
        new_name = f"{base_name}{separator}{index_str}{extension}"
        
        return new_name
    
    def sort_files(self, sort_method: str) -> List[Path]:
        """
        Sort files based on the specified method.
        
        Args:
            sort_method: Sorting method from config.SORT_METHODS
            
        Returns:
            Sorted list of file paths
        """
        if sort_method == "alphabetical":
            return sorted(self.files, key=lambda f: f.name.lower())
        
        elif sort_method == "date_modified":
            return sorted(self.files, key=lambda f: f.stat().st_mtime)
        
        elif sort_method == "date_modified_desc":
            return sorted(self.files, key=lambda f: f.stat().st_mtime, reverse=True)
        
        elif sort_method == "date_created":
            return sorted(self.files, key=lambda f: f.stat().st_ctime)
        
        elif sort_method == "date_created_desc":
            return sorted(self.files, key=lambda f: f.stat().st_ctime, reverse=True)
        
        elif sort_method == "selection_order":
            return self.files.copy()
        
        else:
            # Default to alphabetical
            return sorted(self.files, key=lambda f: f.name.lower())
    
    def check_conflicts(self, rename_plan: List[Tuple[Path, Path]]) -> Dict[Path, Path]:
        """
        Check for naming conflicts in the rename plan.
        
        Args:
            rename_plan: List of (old_path, new_path) tuples
            
        Returns:
            Dictionary of conflicts: {new_path: existing_file}
        """
        conflicts = {}
        
        # Check if any target file already exists
        for old_path, new_path in rename_plan:
            if new_path.exists() and new_path != old_path:
                conflicts[new_path] = old_path
        
        # Check for duplicates within the rename plan itself
        new_paths = [new_path for _, new_path in rename_plan]
        seen = set()
        for new_path in new_paths:
            if new_path in seen:
                conflicts[new_path] = None  # Internal conflict
            seen.add(new_path)
        
        return conflicts
    
    def resolve_conflict(self, new_path: Path, index: int) -> Path:
        """
        Resolve a naming conflict based on configured strategy.
        
        Args:
            new_path: The conflicting path
            index: Current index number
            
        Returns:
            Resolved path
        """
        strategy = self.config.conflict_resolution
        
        if strategy == "skip":
            # Return original (will be skipped in execution)
            return new_path
        
        elif strategy == "add_suffix":
            # Add _copy suffix before extension
            stem = new_path.stem
            extension = new_path.suffix
            parent = new_path.parent
            
            counter = 1
            while True:
                new_name = f"{stem}_copy{counter if counter > 1 else ''}{extension}"
                resolved_path = parent / new_name
                if not resolved_path.exists():
                    return resolved_path
                counter += 1
        
        elif strategy == "auto_increment":
            # Find next available number
            base_name = self.config.base_name
            separator = self.config.separator
            extension = new_path.suffix
            parent = new_path.parent
            padding_width = self.config.get_padding_width(len(self.files))
            
            search_index = index
            while True:
                if padding_width > 0:
                    index_str = str(search_index).zfill(padding_width)
                else:
                    index_str = str(search_index)
                
                test_name = f"{base_name}{separator}{index_str}{extension}"
                test_path = parent / test_name
                
                if not test_path.exists():
                    return test_path
                
                search_index += 1
                
                # Safety limit
                if search_index > index + 10000:
                    # Fall back to timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    return parent / f"{base_name}{separator}{timestamp}{extension}"
        
        elif strategy == "prompt":
            # This will be handled in the GUI
            return new_path
        
        else:
            return new_path
    
    def preview_rename(self) -> List[Tuple[Path, Path, bool, Optional[str]]]:
        """
        Generate a preview of the rename operation.
        
        Returns:
            List of tuples: (old_path, new_path, is_valid, error_message)
        """
        # Sort files first
        self.sorted_files = self.sort_files(self.config.sort_method)
        
        preview = []
        index = self.config.start_number
        
        # Generate initial rename plan
        initial_plan = []
        for filepath in self.sorted_files:
            extension = self.extract_extension(filepath)
            new_name = self.generate_new_name(self.config.base_name, index, extension)
            new_path = filepath.parent / new_name
            initial_plan.append((filepath, new_path))
            index += 1
        
        # Check for conflicts
        conflicts = self.check_conflicts(initial_plan)
        
        # Build preview with conflict resolution
        index = self.config.start_number
        for filepath, new_path in initial_plan:
            # Validate the operation
            is_valid, error = validate_rename_operation(filepath, new_path)
            
            # Handle conflicts
            if new_path in conflicts and self.config.conflict_resolution != "skip":
                new_path = self.resolve_conflict(new_path, index)
                # Re-validate after resolution
                is_valid, error = validate_rename_operation(filepath, new_path)
            elif new_path in conflicts and self.config.conflict_resolution == "skip":
                is_valid = False
                error = "File already exists (will be skipped)"
            
            preview.append((filepath, new_path, is_valid, error))
            index += 1
        
        self.rename_plan = preview
        return preview
    
    def execute_rename(self, progress_callback: Optional[Callable] = None) -> List[RenameResult]:
        """
        Execute the rename operation and log to history.
        
        Args:
            progress_callback: Optional function(current, total, filename) for progress updates
            
        Returns:
            List of RenameResult objects
        """
        results = []
        successful_renames = []
        total = len(self.rename_plan)
        
        for i, (old_path, new_path, is_valid, error) in enumerate(self.rename_plan):
            if progress_callback:
                progress_callback(i + 1, total, old_path.name)
            
            # Skip invalid operations
            if not is_valid:
                result = RenameResult(old_path, new_path, success=False, error=error)
                results.append(result)
                continue
            
            # Skip if paths are the same
            if old_path.resolve() == new_path.resolve():
                result = RenameResult(old_path, new_path, success=True, error=None)
                results.append(result)
                continue
            
            # Attempt rename
            try:
                old_path.rename(new_path)
                result = RenameResult(old_path, new_path, success=True, error=None)
                results.append(result)
                successful_renames.append({
                    "old_path": str(old_path),
                    "new_path": str(new_path)
                })
            except PermissionError:
                error_msg = f"Permission denied - file may be locked or in use"
                result = RenameResult(old_path, new_path, success=False, error=error_msg)
                results.append(result)
            except OSError as e:
                error_msg = f"OS Error: {str(e)}"
                result = RenameResult(old_path, new_path, success=False, error=error_msg)
                results.append(result)
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                result = RenameResult(old_path, new_path, success=False, error=error_msg)
                results.append(result)
        
        # Log to history if any changes were made
        if successful_renames:
            self.history_manager.add_session(successful_renames)
            
        return results
    
    def verify_rename(self, results: List[RenameResult]) -> Dict[str, Any]:
        """
        Verify the results of a rename operation.
        
        Args:
            results: List of RenameResult objects
            
        Returns:
            Dictionary with verification statistics
        """
        stats = {
            "total": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "skipped": sum(1 for r in results if not r.success and "skip" in str(r.error).lower()),
            "errors": [r for r in results if not r.success],
            "success_rate": 0.0
        }
        
        if stats["total"] > 0:
            stats["success_rate"] = (stats["successful"] / stats["total"]) * 100
        
        return stats

    def undo_session(self, session_data: Dict[str, Any], progress_callback: Optional[Callable] = None) -> List[RenameResult]:
        """
        Undo a specific rename session.
        
        Args:
            session_data: The session data dictionary containing file mappings.
            progress_callback: Optional progress callback.
            
        Returns:
            List of results from the undo operation.
        """
        results = []
        files = session_data.get("files", [])
        total = len(files)
        
        # Reverse the order to prevent conflicts (e.g. 1->2, 2->3 needs to be undone as 3->2, 2->1)
        # Actually it depends on how the rename happened. If it was A->B and B existed, B might have been renamed to C.
        # But for simple mass renames, reverse order is generally safer if they were sequential.
        # However, since we store absolute paths, we just map new->old.
        
        for i, file_record in enumerate(reversed(files)):
            old_original_path = Path(file_record["old_path"])
            current_path = Path(file_record["new_path"])
            
            if progress_callback:
                progress_callback(i + 1, total, current_path.name)
            
            if not current_path.exists():
                results.append(RenameResult(current_path, old_original_path, success=False, error="File not found"))
                continue
                
            try:
                # Check if original path exists (potential conflict if file was replaced back)
                if old_original_path.exists():
                     # If the original path exists, we can't just overwrite it without risk.
                     # But for an undo, we implicitly want to restore. 
                     # However, safe practice: Add a suffix or fail.
                     # For now, let's fail to be safe.
                     results.append(RenameResult(current_path, old_original_path, success=False, error="Target path already exists"))
                     continue
                
                current_path.rename(old_original_path)
                results.append(RenameResult(current_path, old_original_path, success=True))
            except Exception as e:
                results.append(RenameResult(current_path, old_original_path, success=False, error=str(e)))
                
        return results
