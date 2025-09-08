# Thermal DICOM Creator GUI

A professional GUI application for creating thermal DICOM files with comprehensive metadata support. Designed for leading researchers in medical thermal imaging.

## Features

- **Elegant User Interface**: Modern, professional GUI designed for researchers
- **Comprehensive Metadata Support**: All standard DICOM fields including patient information, study details, and thermal parameters
- **Multiple Input Sources**: Support for image files, temperature data, or sample generation
- **Organization UID Management**: Built-in common organization UIDs with validation
- **Real-time Preview**: Preview DICOM metadata before creation
- **Validation**: Comprehensive input validation with helpful error messages
- **Professional Output**: Standards-compliant DICOM files with thermal-specific private tags

## Installation

### Option 1: Run from Source

1. Install Python dependencies:
```bash
pip install -r gui_requirements.txt
```

2. Run the GUI application:
```bash
python simple_dicom_gui.py
```

### Option 2: Build Executable

1. Install build dependencies:
```bash
pip install -r gui_requirements.txt
```

2. Build the executable:
```bash
python build_exe.py
```

3. The executable will be created in the `dist/` folder as `ThermalDicomCreator.exe`

## Usage

### Input Sources

1. **Image File**: Select an image file (PNG, JPG, TIFF, BMP) to convert to DICOM
2. **Temperature Data**: Use temperature data arrays (advanced users)
3. **Generate Sample**: Create sample thermal data for testing

### Required Fields

- **Patient Name**: Full patient name
- **Patient ID**: Unique patient identifier
- **Output Folder**: Destination folder for the DICOM file

### Optional Fields

- **Age**: Patient age
- **Gender**: Patient gender (M/F/O)
- **Referring Physician**: Name of referring physician
- **Organization UID**: Organization-specific UID prefix
- **Study Description**: Description of the study

### Thermal Parameters

The application automatically sets standard thermal imaging parameters:
- Emissivity: 0.98 (human skin)
- Distance: 1.0 meters
- Ambient Temperature: 22°C
- Temperature Unit: Celsius

## DICOM Standards Compliance

The application creates DICOM files that comply with:
- DICOM Standard 3.0
- Secondary Capture Image Storage SOP Class
- Thermal imaging private tags (Group 0x7FE1)
- Organization UID validation

## Output

- **File Format**: DICOM (.dcm)
- **Naming Convention**: `thermal_{patient_id}_{timestamp}.dcm`
- **Metadata**: Complete patient, study, and thermal information
- **Private Tags**: Thermal-specific parameters for professional viewers

## Technical Details

### DICOM Structure
- **Modality**: TG (Thermography)
- **Image Type**: DERIVED, SECONDARY, THERMAL
- **Photometric Interpretation**: MONOCHROME2
- **Bits Allocated**: 16-bit
- **Temperature Mapping**: Rescale slope/intercept for temperature conversion

### Private Tags
- Emissivity coefficient
- Distance from camera
- Ambient temperature
- Temperature unit
- Camera calibration data

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed
2. **File Not Found**: Check file paths and permissions
3. **Invalid UID**: Use the "Common UIDs" button for valid organization UIDs
4. **Permission Denied**: Run as administrator if installing to Program Files

### Validation Errors

The application validates:
- Required field completion
- Organization UID format
- Output folder existence
- File format compatibility

## Development

### Building from Source

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -r gui_requirements.txt
```

3. Run the GUI:
```bash
python simple_dicom_gui.py
```

### Customization

The GUI can be customized by modifying:
- `simple_dicom_gui.py`: Main GUI application
- `build_exe.py`: Build configuration
- `gui_requirements.txt`: Dependencies

## Support

For technical support or feature requests, please refer to the main project documentation or create an issue in the repository.

## License

This application is part of the Thermal DICOM package and follows the same licensing terms.
