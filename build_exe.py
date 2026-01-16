# Build Script for Batch File Renamer
# Creates a standalone .exe using PyInstaller

# To build the executable, run:
# python build_exe.py

import PyInstaller.__main__
import os
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# PyInstaller arguments
PyInstaller.__main__.run([
    str(current_dir / 'main.py'),           # Entry point
    '--name=BatchFileRenamer',              # Name of the executable
    '--onefile',                            # Create a single executable file
    '--windowed',                           # No console window (GUI app)
    '--icon=app_icon.ico',                  # Custom application icon
    '--clean',                              # Clean PyInstaller cache
    '--noconfirm',                          # Overwrite without asking
    # Add all project files to the bundle
    f'--add-data={current_dir / "config.py"};.',
    f'--add-data={current_dir / "validators.py"};.',
    f'--add-data={current_dir / "renamer_engine.py"};.',
    f'--add-data={current_dir / "gui.py"};.',
])

print("\n" + "="*60)
print("Build complete!")
print("="*60)
print(f"\nExecutable location: {current_dir / 'dist' / 'BatchFileRenamer.exe'}")
print("\nYou can now:")
print("1. Run the .exe directly from the 'dist' folder")
print("2. Copy it anywhere on your computer")
print("3. Share it with others (no Python installation needed)")
print("="*60)
