<div align="center">

![Batch File Renamer](app_logo.png)

# Batch File Renamer

**A professional batch file renaming utility with sequential numbering, intelligent sorting, and conflict resolution.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

A professional batch file renaming utility designed for video editors, photographers, and anyone who needs to rename multiple files efficiently. Built with Python and tkinter, featuring a clean GUI and powerful renaming capabilities.

- ✨ **Batch Rename**: Rename 30-40+ files in seconds with sequential numbering
- 📁 **File Selection**: Browse or drag-and-drop support for file selection
- 🔢 **Smart Numbering**: Auto-detect zero padding based on file count (1-9 → no padding, 10-99 → 2 digits, 100+ → 3 digits)
- 🔀 **Flexible Sorting**: Sort files alphabetically, by date modified, date created, or selection order
- ⚡ **Live Preview**: See exactly how files will be renamed before executing
- 🛡️ **Conflict Resolution**: Automatic handling of naming conflicts with multiple strategies
- 🎯 **Extension Preservation**: Automatically preserves file extensions (.mp4, .mov, .jpg, etc.)
- 🔒 **Error Handling**: Detects locked files and permission errors with detailed reporting
- 🎨 **Color-Coded Preview**: Visual indicators for safe renames (green), conflicts (yellow), and errors (red)

## Installation

### Option 1: Standalone Executable (Recommended for Non-Developers)

**No Python installation required!**

1. Download `BatchFileRenamer.exe` from the `dist` folder
2. Double-click to run
3. Start renaming files immediately

✅ Works on any Windows 10/11 computer  
✅ No dependencies  
✅ Portable (run from anywhere)

### Option 2: Run from Source (For Developers)

#### Prerequisites
- Python 3.10 or higher
- tkinter (usually included with Python)

#### Setup

1. Clone or download this repository
2. Navigate to the project directory:
```bash
cd FileNameOrganizer
```

3. Run the application:
```bash
python main.py
```

### Building Your Own Executable

If you want to rebuild the .exe yourself:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --name=BatchFileRenamer --onefile --windowed --clean main.py

# Find the .exe in the dist/ folder
```

See [DEPLOYMENT.md](file:///c:/Users/egule/Desktop/antigravity/FileNameOrganizer/DEPLOYMENT.md) for detailed build instructions.

## Usage

### Quick Start

1. **Launch the application**: Run `python main.py`
2. **Select files**: Click "Browse Files..." or drag files into the application
3. **Configure naming**:
   - Enter a base name (e.g., `Murat_Deneme`)
   - Choose starting number (default: 1)
   - Select zero padding option
   - Choose sorting method
4. **Preview changes**: Review the "Old → New" preview to ensure correctness
5. **Rename**: Click "Rename Files" when ready

### Configuration Options

#### Base Name
The prefix for all renamed files. Example: `VideoClip` will produce `VideoClip_1.mp4`, `VideoClip_2.mp4`, etc.

**Rules**:
- Cannot be empty
- No forbidden characters: `< > : " / \ | ? *`
- Cannot be a reserved Windows name (CON, PRN, AUX, NUL, COM1-9, LPT1-9)

#### Separator
Character(s) between base name and number. Default: `_` (underscore)
- Examples: `_` → `Video_1.mp4`, `-` → `Video-1.mp4`, ` ` → `Video 1.mp4`

#### Start Number
The first number in the sequence. Default: 1
- Range: 0 to 999,999

#### Zero Padding
How numbers are formatted:
- **Auto-detect** (recommended): Automatically adjusts based on file count
  - 1-9 files → no padding (1, 2, 3...)
  - 10-99 files → 2 digits (01, 02, 03...)
  - 100+ files → 3 digits (001, 002, 003...)
- **No Padding**: Always use minimum digits (1, 2, 3, 10, 100...)
- **2 Digits**: Force 2 digits (01, 02, 03...)
- **3 Digits**: Force 3 digits (001, 002, 003...)
- **4 Digits**: Force 4 digits (0001, 0002, 0003...)

#### Sort By
Determines the order files are renamed:
- **Alphabetical (A-Z)**: Sort by filename alphabetically
- **Date Modified (Oldest/Newest First)**: Sort by last modification date
- **Date Created (Oldest/Newest First)**: Sort by creation date
- **Selection Order**: Keep the order you selected files in

#### Conflict Resolution
What to do when a file with the new name already exists:
- **Skip (Keep Original)**: Don't rename files that would conflict
- **Add Suffix (_copy)**: Add `_copy` (or `_copy2`, `_copy3`, etc.) to the filename
- **Auto-increment Number** (recommended): Find the next available number
- **Prompt for Each**: Ask you what to do for each conflict (not yet implemented)

## Use Cases

### Video Editing Sequence
Rename raw footage files to maintain sequence order for NLE timelines:
```
Before: IMG_4521.mp4, IMG_4522.mp4, IMG_4523.mp4
After: RawFootage_001.mp4, RawFootage_002.mp4, RawFootage_003.mp4
```

### Organizing Photo Shoots
Rename photos from a shoot with descriptive names:
```
Before: DSC_0001.jpg, DSC_0002.jpg, DSC_0003.jpg
After: Wedding_01.jpg, Wedding_02.jpg, Wedding_03.jpg
```

### Batch Audio Files
Rename exported audio stems for easier organization:
```
Before: Audio 1.wav, Audio 2.wav, Audio 3.wav
After: Stem_01.wav, Stem_02.wav, Stem_03.wav
```

## Error Handling

### Locked Files
If a file is open in another program (e.g., Premiere Pro, DaVinci Resolve), the renamer will:
- Detect the locked file
- Skip it during the rename operation
- Report it in the results dialog
- Continue processing other files

### Permission Errors
If you don't have write permission in a directory:
- The preview will show an error
- The file will be marked in red
- A detailed error message will be displayed

### Name Conflicts
When a target filename already exists:
- The conflict resolution strategy is applied automatically
- Yellow warning indicators show potential conflicts in the preview
- You can change the strategy at any time

## Tips & Best Practices

1. **Always Preview First**: Check the preview pane before renaming to ensure the output matches your expectations

2. **Use Auto-Padding**: The auto-detect padding option ensures proper sorting in file explorers and NLEs

3. **Sort by Date for Chronological Order**: When working with camera files, sort by date created to maintain chronological order

4. **Close Files First**: Close files in other applications (video editors, image viewers) before renaming to avoid lock errors

5. **Test with a Few Files**: If unsure, test with 2-3 files first to verify the naming pattern

6. **Backup Important Files**: While the renamer is safe, always maintain backups of irreplaceable files

## Troubleshooting

### Issue: "File is locked or you don't have permission"
**Solution**: Close the file in any other applications and try again. Check that you have write permission in the directory.

### Issue: Preview shows all files in red
**Solution**: Check that your base name doesn't contain forbidden characters (`< > : " / \ | ? *`)

### Issue: Numbers aren't padded correctly
**Solution**: Change the "Zero Padding" setting from "Auto-detect" to a fixed option (2, 3, or 4 digits)

### Issue: Files aren't in the right order
**Solution**: Change the "Sort By" option to match your desired ordering (e.g., Date Modified for chronological order)

## Screenshots

*Coming soon - add screenshots of your application in action!*

## Technical Details

- **Language**: Python 3.10+
- **GUI Framework**: tkinter (built-in)
- **File Operations**: pathlib (built-in)
- **Threading**: Multi-threaded rename execution to keep UI responsive
- **Platform**: Cross-platform (Windows, macOS, Linux)

## Project Structure

```
FileNameOrganizer/
├── main.py              # Application entry point
├── gui.py               # GUI implementation
├── renamer_engine.py    # Core renaming logic
├── validators.py        # Input validation
├── config.py            # Configuration and constants
├── app_icon.ico         # Application icon
├── app_logo.png         # Logo image
├── build_exe.py         # PyInstaller build script
├── convert_icon.py      # Icon conversion utility
├── README.md            # This file
├── LICENSE              # MIT License
├── CONTRIBUTING.md      # Contribution guidelines
├── DEPLOYMENT.md        # Deployment guide
└── USER_GUIDE.txt       # End-user instructions
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Future Enhancements

Potential features for future versions:
- Undo/Rollback capability with operation logging
- Naming templates (save/load presets)
- Find & Replace mode
- Custom date/time stamps in filenames
- Batch resize/convert operations
- Context menu integration (right-click in Windows Explorer)
- macOS and Linux standalone builds

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and tkinter
- Icon conversion using Pillow
- Executable packaging with PyInstaller

## Support

If you encounter any issues or have questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Read the [DEPLOYMENT.md](DEPLOYMENT.md) for build/distribution issues
3. Open an issue on GitHub

## Changelog

### v1.0.0 (January 2026)
- Initial release
- Complete batch renaming with GUI
- Sequential numbering with auto-padding
- Multiple sorting options
- Conflict resolution strategies
- Live preview
- Error handling
- Standalone executable with custom icon
- Comprehensive documentation

---

<div align="center">

**Made with ❤️**

[Report Bug](https://github.com/YOUR_USERNAME/FileNameOrganizer/issues) • [Request Feature](https://github.com/YOUR_USERNAME/FileNameOrganizer/issues) • [Documentation](DEPLOYMENT.md)

</div>
