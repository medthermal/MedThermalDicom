
@echo off
echo Installing Thermal DICOM Creator...
echo.

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\ThermalDicomCreator
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "dist\ThermalDicomCreator.exe" "%INSTALL_DIR%\"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
echo @echo off > "%DESKTOP%\Thermal DICOM Creator.bat"
echo cd /d "%INSTALL_DIR%" >> "%DESKTOP%\Thermal DICOM Creator.bat"
echo start ThermalDicomCreator.exe >> "%DESKTOP%\Thermal DICOM Creator.bat"

echo Installation completed!
echo A shortcut has been created on your desktop.
pause
