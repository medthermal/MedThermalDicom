@echo off
echo Starting Thermal DICOM Creator Pro...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, numpy, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r gui_requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Launch the enhanced GUI
echo Launching Enhanced Thermal DICOM Creator Pro...
python simple_dicom_gui_enhanced.py

if errorlevel 1 (
    echo.
    echo Error: Failed to launch the application
    pause
)
