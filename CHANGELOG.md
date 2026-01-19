# Changelog

All notable changes to the Batch File Renamer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-19

### ✨ Added

#### Modern UI Theme
- **Apple-inspired design** with clean, flat aesthetics
- Light gray background (`#F5F5F7`) with white panel cards
- Apple Blue (`#0071E3`) accent color for primary actions
- Professional typography with improved spacing
- Custom styled buttons, tabs, and tables
- Enhanced visual hierarchy and readability

#### Deep History Tracking
- **Persistent history tracking** across sessions
- Automatic tracking of all rename operations
- **Original filename preservation** - always shows the first imported name
- Works even after restarting the application
- Example: If you rename `Photo.jpg` → `Temp_1.jpg` → `Final_1.jpg`, it still remembers `Photo.jpg`

#### Undo/Recovery System
- **Complete history viewer** in dedicated "History" tab
- View all past rename sessions with timestamps
- Detailed session view showing original → renamed mappings
- **One-click Undo** to revert any past session
- Safety checks to prevent errors (verifies files exist before reverting)

#### Customizable History Storage
- **"Change Storage Location..."** button in History tab
- Save history file to custom locations (cloud folders, external drives, etc.)
- Option to migrate existing history when changing location
- Settings persist across sessions via `app_settings.json`
- Perfect for:
  - Cloud sync (OneDrive, Dropbox)
  - Backup to external drives
  - Network storage locations

### 🔧 Changed
- Application now uses modern `ttk` theming system
- Improved button styling and spacing
- Enhanced status bar with better visual integration
- "Rename Files" button now uses accent color for better visibility

### 🏗️ Technical
- Added `theme_manager.py` - Theme configuration module
- Added `history_manager.py` - History tracking and undo logic
- Added `app_settings.py` - Persistent application settings
- Updated `gui.py` - Tabbed interface with History tab
- Updated `renamer_engine.py` - Integrated history logging
- Rebuilt standalone executable with all new features

### 📦 Files Added
- `theme_manager.py` - Modern theme definitions
- `history_manager.py` - History and recovery system
- `app_settings.py` - Settings persistence
- `history.json` - Default history storage (auto-created)
- `app_settings.json` - Application preferences (auto-created)

---

## [1.0.0] - 2026-01-16

### 🎉 Initial Release

#### Core Features
- **Batch file renaming** with sequential numbering
- Support for 30-40+ files simultaneously
- Smart zero padding (auto-detect based on file count)
- Multiple sorting options:
  - Alphabetical (A-Z)
  - Date Modified (Oldest/Newest First)
  - Date Created (Oldest/Newest First)
  - Selection Order
- **Live preview** before renaming
- **Conflict resolution** with multiple strategies:
  - Skip (Keep Original)
  - Add Suffix (_copy)
  - Auto-increment Number
- File extension preservation
- Color-coded preview (green/yellow/red indicators)

#### User Interface
- Clean tkinter-based GUI
- Drag-and-drop file selection
- Real-time configuration updates
- Progress bar during operations
- Comprehensive error reporting

#### Error Handling
- Locked file detection
- Permission error handling
- Detailed error messages
- Graceful failure recovery

#### Distribution
- Standalone Windows executable (`.exe`)
- No Python installation required
- Custom application icon
- Portable (run from anywhere)

#### Documentation
- Comprehensive README
- User guide
- Deployment instructions
- Contributing guidelines
- MIT License

---

## Version Comparison

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| Batch Renaming | ✅ | ✅ |
| Live Preview | ✅ | ✅ |
| Conflict Resolution | ✅ | ✅ |
| Modern UI Theme | ❌ | ✅ |
| History Tracking | ❌ | ✅ |
| Undo System | ❌ | ✅ |
| Customizable Storage | ❌ | ✅ |
| Deep History Lookup | ❌ | ✅ |

---

[2.0.0]: https://github.com/MuratBrls/FileNameOrganizer/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/MuratBrls/FileNameOrganizer/releases/tag/v1.0.0
