@echo off
echo Starting Thermal DICOM Creator GUI...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import pydicom, numpy, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r gui_requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Run the GUI application
echo Starting GUI...
python simple_dicom_gui.py

if errorlevel 1 (
    echo Error: Failed to start GUI application
    pause
    exit /b 1
)

echo GUI application closed.
pause
