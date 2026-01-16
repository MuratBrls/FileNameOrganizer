# Batch File Renamer - Distribution Guide

## 📦 Standalone Executable

The application has been packaged as a **standalone Windows executable** that requires **no Python installation**.

### Executable Location

```
FileNameOrganizer/
└── dist/
    └── BatchFileRenamer.exe    (Ready to run!)
```

---

## 🚀 Quick Start

### For End Users (No Technical Knowledge Required)

1. **Locate the executable**: Navigate to `dist` folder
2. **Run the application**: Double-click `BatchFileRenamer.exe`
3. **Use the app**: Select files and configure rename settings
4. **That's it!** No installation, no Python, no dependencies

### Distribution Options

#### Option 1: Share the .exe File
Simply share the `BatchFileRenamer.exe` file with others:
- Copy it to a USB drive
- Send via email (if file size permits)
- Upload to cloud storage (Google Drive, Dropbox, etc.)
- Share on network drive

#### Option 2: Create an Installer (Optional)
For a more professional distribution, you can:
- Use [Inno Setup](https://jrsoftware.org/isinfo.php) to create an installer
- Add desktop shortcuts
- Include in Start Menu
- Add uninstaller

#### Option 3: Portable App
The .exe is already portable:
- No registry entries
- No installation required
- Run from anywhere (Desktop, USB drive, network share)
- No admin rights needed

---

## 📋 System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **RAM**: 50MB minimum
- **Disk Space**: ~15MB for the executable
- **Dependencies**: None (everything is bundled)

---

## 🔧 Developer: Building from Source

If you want to rebuild the executable yourself:

### Prerequisites
```bash
pip install pyinstaller
```

### Build Methods

#### Method 1: Using PyInstaller Directly
```bash
pyinstaller --name=BatchFileRenamer --onefile --windowed --clean --noconfirm main.py
```

#### Method 2: Using Build Script
```bash
python build_exe.py
```

### Build Output
After building:
```
dist/BatchFileRenamer.exe    # Standalone executable (~12-15MB)
build/                       # Temporary build files (can delete)
BatchFileRenamer.spec        # PyInstaller spec file
```

### Build Options

**Current Configuration**:
- `--onefile`: Single executable file (easier to distribute)
- `--windowed`: No console window (GUI app)
- `--clean`: Clean cache before building
- `--noconfirm`: Overwrite without confirmation

**Alternative Options**:

```bash
# With custom icon
pyinstaller --name=BatchFileRenamer --onefile --windowed --icon=app_icon.ico main.py

# With console for debugging
pyinstaller --name=BatchFileRenamer --onefile main.py

# Folder distribution (faster startup)
pyinstaller --name=BatchFileRenamer --windowed main.py
```

---

## 📁 File Structure After Build

```
FileNameOrganizer/
├── dist/
│   └── BatchFileRenamer.exe        # ⭐ Standalone executable
├── build/                          # Temporary build files
├── main.py                         # Source code
├── gui.py
├── renamer_engine.py
├── validators.py
├── config.py
├── build_exe.py                    # Build script
├── BatchFileRenamer.spec           # PyInstaller spec file
└── README.md
```

---

## 🎯 Deployment Checklist

### For Personal Use
- [x] Build executable with PyInstaller
- [ ] Copy `BatchFileRenamer.exe` to desired location
- [ ] Create desktop shortcut (optional)
- [ ] Test with sample files

### For Distribution
- [ ] Test on clean Windows machine (no Python)
- [ ] Verify all features work in .exe
- [ ] Create user documentation
- [ ] Package with README if needed
- [ ] Test on different Windows versions
- [ ] Consider code signing (for trusted publisher status)

---

## 🔒 Security Notes

### Antivirus False Positives
**Why it happens**: PyInstaller executables are sometimes flagged by antivirus software because:
- They bundle Python runtime (looks like "packing")
- Self-extracting behavior
- Common for any Python-to-exe converter

**Solutions**:
1. **Code Signing**: Sign the executable with a certificate (eliminates most warnings)
2. **Submit to Antivirus Vendors**: Upload to VirusTotal and report false positive
3. **User Communication**: Inform users this is expected behavior

### Windows SmartScreen
First-time users may see "Windows protected your PC" warning:
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- After enough users run it, Windows builds reputation

### To Sign Your Executable
```bash
# Requires code signing certificate
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com BatchFileRenamer.exe
```

---

## 📊 Executable Details

### File Size
- **Typical size**: 12-15 MB
- **Includes**: Python runtime, tkinter, all dependencies
- **First run**: May take 2-3 seconds to extract (from single file)

### Performance
- **Startup**: 1-3 seconds (one-time extraction)
- **Runtime**: Same as Python version
- **Memory**: ~50-100 MB (similar to Python)

### Compatibility
- ✅ Windows 10 (all versions)
- ✅ Windows 11
- ⚠️ Windows 7/8 (may require updates)
- ❌ Linux/macOS (need separate builds)

---

## 🐛 Troubleshooting

### Issue: "Windows cannot access the specified device"
**Cause**: Antivirus blocking execution  
**Solution**: Add exclusion in Windows Defender or antivirus software

### Issue: "Application failed to initialize"
**Cause**: Missing Visual C++ Redistributables  
**Solution**: Install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Issue: Slow startup
**Cause**: Single-file executables extract on first run  
**Solution**: Normal behavior, subsequent runs are faster

### Issue: "Permission denied" errors when renaming
**Cause**: Running from protected folder (e.g., Program Files)  
**Solution**: Run from user directory or as administrator

---

## 🔄 Updating the Application

### For Developers
1. Modify source code (`.py` files)
2. Rebuild executable: `pyinstaller --name=BatchFileRenamer --onefile --windowed main.py`
3. Replace old .exe with new one in `dist` folder
4. Update version number in `config.py`

### For End Users
1. Download new `BatchFileRenamer.exe`
2. Replace old file
3. No uninstall/reinstall needed

---

## 📝 Advanced: Creating an Installer

### Using Inno Setup (Free, Recommended)

1. **Download**: [Inno Setup](https://jrsoftware.org/isinfo.php)

2. **Create installer script** (`installer.iss`):
```iss
[Setup]
AppName=Batch File Renamer
AppVersion=1.0.0
DefaultDirName={autopf}\BatchFileRenamer
DefaultGroupName=Batch File Renamer
OutputDir=installer_output
OutputBaseFilename=BatchFileRenamer-Setup

[Files]
Source: "dist\BatchFileRenamer.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\Batch File Renamer"; Filename: "{app}\BatchFileRenamer.exe"
Name: "{autodesktop}\Batch File Renamer"; Filename: "{app}\BatchFileRenamer.exe"
```

3. **Compile**: Run Inno Setup Compiler on the script

4. **Result**: Professional installer with uninstaller

---

## 🎨 Adding Custom Icon (Optional)

1. **Get/Create Icon**: `.ico` file (256x256 recommended)

2. **Rebuild with icon**:
```bash
pyinstaller --name=BatchFileRenamer --onefile --windowed --icon=app_icon.ico main.py
```

3. **Icon Resources**:
   - [Icons8](https://icons8.com) (free)
   - [Flaticon](https://flaticon.com) (free with attribution)
   - [IconArchive](https://iconarchive.com) (various licenses)

---

## 📦 Distribution Package Structure

### Recommended Package
```
BatchFileRenamer-v1.0.0/
├── BatchFileRenamer.exe    # The application
├── README.txt              # Simple user guide
└── test_files/             # Sample files (optional)
```

Zip this folder for easy distribution.

---

## ✅ Quality Assurance

### Testing Checklist
- [ ] Executable runs on clean Windows 10 machine
- [ ] Executable runs on Windows 11
- [ ] All features work (file selection, preview, rename)
- [ ] No Python installation required
- [ ] No console window appears
- [ ] File operations work correctly
- [ ] Error handling works (locked files, permissions)
- [ ] Results dialog displays correctly

### Performance Testing
- [ ] Test with 10 files
- [ ] Test with 100 files
- [ ] Test with 1000 files
- [ ] Test with files on network drive
- [ ] Test with very long filenames
- [ ] Test with Unicode characters

---

## 🚢 Ready to Ship!

Your standalone executable is ready for distribution. Users can:
1. Download `BatchFileRenamer.exe`
2. Double-click to run
3. Start renaming files immediately

**No Python. No Installation. No Hassle.** ✨

---

**Built with**: PyInstaller  
**Version**: 1.0.0  
**Last Updated**: January 2026
