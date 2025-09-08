# Thermal DICOM Creator Pro - Enhanced GUI Launcher
# PowerShell script for Windows

Write-Host "Starting Thermal DICOM Creator Pro..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    python -c "import tkinter, numpy, PIL" 2>$null
    Write-Host "All required packages are available" -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    try {
        pip install -r gui_requirements.txt
        Write-Host "Packages installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to install required packages" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Launch the enhanced GUI
Write-Host "Launching Enhanced Thermal DICOM Creator Pro..." -ForegroundColor Green
try {
    python simple_dicom_gui_enhanced.py
} catch {
    Write-Host ""
    Write-Host "Error: Failed to launch the application" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
