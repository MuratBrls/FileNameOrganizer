"""
History and Logging Manager for the Batch File Renamer.
Handles persistent storage of rename sessions and provides undo capabilities.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any

class HistoryManager:
    """Manages the history of rename operations."""
    
    def __init__(self, storage_file: str = "history.json"):
        """
        Initialize the HistoryManager.
        
        Args:
            storage_file: Path to the JSON file for storing history.
        """
        self.storage_file = Path(storage_file)
        self.history_data = self._load_history()
        
    def _load_history(self) -> Dict[str, Any]:
        """Load history from disk."""
        if not self.storage_file.exists():
            return {"sessions": []}
            
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # If file is corrupt or unreadable, start fresh
            return {"sessions": []}
            
    def _save_history(self):
        """Save history to disk."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"Failed to save history: {e}")

    def add_session(self, rename_records: List[Dict[str, str]]) -> str:
        """
        Record a new rename session.
        
        Args:
            rename_records: List of dicts, each containing 'old_path' and 'new_path'.
            
        Returns:
            The unique Session ID.
        """
        if not rename_records:
            return None
            
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        session = {
            "id": session_id,
            "timestamp": timestamp,
            "count": len(rename_records),
            "files": rename_records
        }
        
        # Prepend to keep newest first
        self.history_data["sessions"].insert(0, session)
        self._save_history()
        
        return session_id

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Return all recorded sessions."""
        return self.history_data["sessions"]
        
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific session by ID."""
        for session in self.history_data["sessions"]:
            if session["id"] == session_id:
                return session
        return None

    def trace_original_name(self, current_path: Path) -> Optional[str]:
        """
        Trace back the history to find the original name of a file.
        Useful when a file has been renamed multiple times.
        
        Args:
            current_path: The current path of the file.
            
        Returns:
            The original name/path string if found, else None.
        """
        search_path = str(current_path.resolve())
        original_found = None
        
        # Search efficiently? 
        # Since we want to trace A->B->C, and we have C.
        # We need to find the session where "new_path" == C. Then take "old_path" (B).
        # Then find session where "new_path" == B. Then take "old_path" (A).
        
        # Iterate through sessions from Newest to Oldest
        # (sessions[0] is newest)
        
        trace_cursor = search_path
        
        for session in self.history_data["sessions"]:
            for record in session["files"]:
                # Normalize paths for comparison
                try:
                    record_new = str(Path(record["new_path"]).resolve())
                    
                    if record_new == trace_cursor:
                        trace_cursor = str(Path(record["old_path"]).resolve())
                        original_found = trace_cursor
                        # Break inner loop to continue searching in older sessions with the new cursor
                        break 
                except Exception:
                    continue
                    
        if original_found:
             return Path(original_found).name
             
        return None

    def clear_history(self):
        """Clear all history."""
        self.history_data = {"sessions": []}
        self._save_history()
