# Thermal DICOM Creator GUI Launcher
# PowerShell script for running the GUI application

Write-Host "Starting Thermal DICOM Creator GUI..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7 or higher" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
try {
    python -c "import pydicom, numpy, PIL" 2>$null
    Write-Host "Required packages are installed" -ForegroundColor Yellow
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    try {
        pip install -r gui_requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install packages"
        }
    } catch {
        Write-Host "Error: Failed to install required packages" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Run the GUI application
Write-Host "Starting GUI..." -ForegroundColor Green
try {
    python simple_dicom_gui.py
    if ($LASTEXITCODE -ne 0) {
        throw "GUI application failed"
    }
} catch {
    Write-Host "Error: Failed to start GUI application" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "GUI application closed." -ForegroundColor Green
Read-Host "Press Enter to exit"
