"""
Application Settings Manager.
Handles persistent storage of application-wide preferences.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

SETTINGS_FILE = "app_settings.json"
DEFAULT_HISTORY_FILE = "history.json"

class AppSettings:
    """Manages application settings."""
    
    def __init__(self):
        self.settings_path = Path(SETTINGS_FILE)
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from disk."""
        if not self.settings_path.exists():
            return self._default_settings()
            
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except Exception:
            return self._default_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        """Return default settings."""
        return {
            "history_path": str(Path(DEFAULT_HISTORY_FILE).resolve())
        }
        
    def get_history_path(self) -> Path:
        """Get the current history file path."""
        path_str = self.settings.get("history_path")
        if not path_str:
            return Path(DEFAULT_HISTORY_FILE).resolve()
        return Path(path_str)
        
    def set_history_path(self, path: Path):
        """Set a new history file path."""
        self.settings["history_path"] = str(path.resolve())
        self._save_settings()
        
    def _save_settings(self):
        """Save settings to disk."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")
