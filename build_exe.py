#!/usr/bin/env python3
"""
Build script for creating executable from the Thermal DICOM Creator GUI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def build_executable():
    """Build the executable using PyInstaller."""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    gui_script = current_dir / "simple_dicom_gui.py"
    
    if not gui_script.exists():
        print(f"Error: {gui_script} not found!")
        return False
    
    # Create dist directory if it doesn't exist
    dist_dir = current_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window
        "--name=ThermalDicomCreator",  # Name of the executable
        "--icon=icon.ico" if (current_dir / "icon.ico").exists() else None,  # Icon if available
        "--add-data", f"{current_dir / 'thermal_dicom'};thermal_dicom",  # Include the thermal_dicom package
        "--hidden-import=pydicom",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        str(gui_script)
    ]
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, cwd=current_dir, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(result.stdout)
        
        # Check if executable was created
        exe_path = dist_dir / "ThermalDicomCreator.exe"
        if exe_path.exists():
            print(f"\nExecutable created successfully: {exe_path}")
            print(f"Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            print("Error: Executable not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer():
    """Create a simple installer script."""
    installer_script = """
@echo off
echo Installing Thermal DICOM Creator...
echo.

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\ThermalDicomCreator
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "dist\\ThermalDicomCreator.exe" "%INSTALL_DIR%\\"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\\Desktop
echo @echo off > "%DESKTOP%\\Thermal DICOM Creator.bat"
echo cd /d "%INSTALL_DIR%" >> "%DESKTOP%\\Thermal DICOM Creator.bat"
echo start ThermalDicomCreator.exe >> "%DESKTOP%\\Thermal DICOM Creator.bat"

echo Installation completed!
echo A shortcut has been created on your desktop.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_script)
    
    print("Installer script created: install.bat")

def main():
    """Main build process."""
    print("=== Thermal DICOM Creator Build Process ===\n")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        print("\n=== Build Successful! ===")
        
        # Create installer
        create_installer()
        
        print("\nNext steps:")
        print("1. Test the executable: dist/ThermalDicomCreator.exe")
        print("2. Run install.bat to install the application")
        print("3. Distribute the executable to users")
        
    else:
        print("\n=== Build Failed! ===")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
