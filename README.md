# MedThermal DICOM

**Professional thermal imaging DICOM library for medical applications**

A comprehensive Python library for creating, manipulating, and managing thermal DICOM images with support for thermal-specific metadata, temperature calibration, and DICOM-compliant overlays.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core API Reference](#core-api-reference)
  - [MedThermalDicom Class](#medthermaldicom-class)
  - [MedThermalMetadata Class](#medthermalmetadata-class)
  - [Utility Classes](#utility-classes)
- [Usage Examples](#usage-examples)
  - [Basic DICOM Creation](#basic-dicom-creation)
  - [Setting Thermal Parameters](#setting-thermal-parameters)
  - [Metadata Management](#metadata-management)
  - [Text Annotations with DICOM Overlays](#text-annotations-with-dicom-overlays)
  - [Organization UID Management](#organization-uid-management)
- [GUI Applications](#gui-applications)
- [Examples](#examples)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Advanced Topics](#advanced-topics)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

MedThermal DICOM is designed for researchers, clinicians, and developers working with medical thermal imaging. It provides:

- **Python API**: Programmatic creation and manipulation of thermal DICOM files
- **GUI Applications**: User-friendly interfaces for non-programmers
- **Standards Compliance**: Full DICOM compliance with thermal-specific extensions
- **Rich Metadata**: Comprehensive thermal imaging metadata support

## Features

### Core Features
- ✅ Create DICOM files from thermal images (PNG, JPG, TIFF, BMP)
- ✅ Import temperature data from CSV or numpy arrays
- ✅ Set comprehensive thermal parameters (emissivity, distance, ambient temperature, etc.)
- ✅ Manage patient, study, and series metadata
- ✅ Text annotation overlays (toggleable in DICOM viewers)
- ✅ Export to standard DICOM format
- ✅ Organization UID management for custom UID generation

### GUI Features
- 🎨 Modern, professional user interface
- 🔍 Real-time file preview
- 🏥 Comprehensive patient and study information entry
- 🌡️ Advanced thermal parameter configuration
- ✔️ Input validation with helpful error messages
- 📊 Organization UID management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/MedThermalDicom.git
cd MedThermalDicom
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Install as Package

```bash
pip install -e .
```

This installs the `medthermal_dicom` package and makes it available system-wide.

## Quick Start

### Using the API

```python
import numpy as np
from medthermal_dicom import MedThermalDicom

# Load your temperature data (example with numpy array)
temperature_data = np.loadtxt("temperature_data.csv", delimiter=",")

# Create DICOM instance
thermal_dicom = MedThermalDicom()

# Set thermal image
temp_range = (temperature_data.min(), temperature_data.max())
thermal_dicom.set_thermal_image(temperature_data, temperature_data, temp_range)

# Set thermal parameters
thermal_params = {
    'emissivity': 0.98,
    'distance_from_camera': 1.0,
    'ambient_temperature': 22.0,
    'camera_model': 'FLIR E8-XT'
}
thermal_dicom.set_thermal_parameters(thermal_params)

# Create DICOM with patient info
thermal_dicom.create_standard_thermal_dicom(
    patient_name="DOE^JOHN",
    patient_id="PATIENT001",
    study_description="Breast Thermal Imaging"
)

# Save DICOM file
thermal_dicom.save_dicom("output.dcm")
```

### Using the GUI

#### Windows:
```bash
run_gui.bat
```

#### PowerShell or Linux/Mac:
```bash
python simple_dicom_gui.py
```


## Core API Reference

### MedThermalDicom Class

The main class for creating and managing thermal DICOM files.

#### Initialization

```python
MedThermalDicom(
    thermal_array: Optional[np.ndarray] = None,
    temperature_data: Optional[np.ndarray] = None,
    thermal_params: Optional[Dict[str, Any]] = None,
    use_legacy_private_creator_encoding: bool = False,
    organization_uid_prefix: Optional[str] = None,
    patient_sex: Optional[str] = None,
    patient_birth_date: Optional[str] = None,
    study_date: Optional[str] = None
)
```

### MedThermalMetadata Class

Professional thermal DICOM metadata management for medical imaging standards compliance.

### Utility Classes

#### Organization UID Utilities

**Functions:**
- `generate_organization_uid(org_prefix=None, uid_type="instance")` - Generate organization-specific UID
- `validate_organization_uid(uid)` - Validate UID format
- `get_common_organization_uids()` - Get dictionary of common organization UIDs

## Usage Examples

### Basic DICOM Creation

```python
from medthermal_dicom import MedThermalDicom
import numpy as np

# Create instance
thermal_dicom = MedThermalDicom()

# Load temperature data from CSV
temperature_data = np.loadtxt("temp_data.csv", delimiter=",")

# Set thermal image (display array, temperature array, temperature range)
temp_min, temp_max = temperature_data.min(), temperature_data.max()
thermal_dicom.set_thermal_image(
    thermal_array=temperature_data,
    temperature_data=temperature_data,
    temperature_range=(temp_min, temp_max)
)

# Create standard DICOM
thermal_dicom.create_standard_thermal_dicom(
    patient_name="SMITH^JANE",
    patient_id="TH001",
    study_description="Thermal Imaging Study",
    patient_sex="F",
    patient_birth_date="19900101"
)

# Save the DICOM file
thermal_dicom.save_dicom("output_thermal.dcm")
```

### Setting Thermal Parameters

```python
# Define thermal parameters
thermal_params = {
    'emissivity': 0.98,                    # Human skin emissivity
    'distance_from_camera': 1.0,           # Distance in meters
    'ambient_temperature': 22.0,           # Room temperature in °C
    'reflected_temperature': 22.0,         # Reflected temperature
    'atmospheric_temperature': 22.0,       # Atmospheric temp
    'relative_humidity': 45.0,            # Humidity percentage
    'temperature_range_min': 20.0,        # Min temperature
    'temperature_range_max': 40.0,        # Max temperature
    'temperature_unit': 'Celsius',        # Temperature unit
    'thermal_sensitivity': 0.05,          # NETD in °C
    'spectral_range': '7.5-14.0',         # Spectral range in μm
    'lens_field_of_view': 24.0            # FOV in degrees
}

thermal_dicom.set_thermal_parameters(thermal_params)
```

### Metadata Management

```python
from medthermal_dicom import MedThermalMetadata

# Create metadata handler
metadata = MedThermalMetadata()

# Set patient information
metadata.set_patient_information(
    patient_name="DOE^JOHN^MEDICAL",
    patient_id="TH001",
    patient_birth_date="19850315",
    patient_sex="M",
    patient_age="038Y"
)

# Set study information
metadata.set_study_information(
    study_description="Breast Thermal Imaging Study",
    accession_number="ACC123456",
    referring_physician="DR^SMITH^JANE",
    procedure_code="breast_thermography"  # SNOMED CT code
)

# Set series information
metadata.set_series_information(
    series_description="Thermal Images - Anterior View",
    body_part="breast",  # Uses SNOMED CT codes
    patient_position="HFS"
)

# Set equipment information
metadata.set_equipment_information(
    manufacturer="FLIR Systems",
    manufacturer_model="T1K",
    device_serial_number="SN12345",
    software_version="MedThermalDICOM v1.0"
)

# Apply metadata to DICOM dataset
metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
```

### Text Annotations with DICOM Overlays

Add text annotations to your DICOM files that can be toggled on/off in DICOM viewers:

```python
from medthermal_dicom import MedThermalDicom
import numpy as np

# Create and configure thermal DICOM
thermal_dicom = MedThermalDicom()
thermal_dicom.set_thermal_image(temperature_data, temperature_data, (20.0, 40.0))

# Add text overlay annotation (stored in DICOM group 0x6000)
# The overlay is drawn on a blank array matching image dimensions
overlay_array = np.zeros_like(temperature_data)
thermal_dicom.add_overlay(
    overlay_array=overlay_array,
    position=(50, 50),      # (x, y) coordinates in pixels
    text="Patient ROI - Max Temp: 38.5°C"
)

# Save DICOM with overlays
thermal_dicom.save_dicom("thermal_with_annotations.dcm")
```

**Features:**
- ✅ Overlays are stored in standard DICOM overlay groups (0x6000-0x60FF)
- ✅ Can be toggled on/off in DICOM viewers (RadiAnt, Horos, etc.)
- ✅ Supports multiple independent overlays per image
- ✅ Text is rendered as binary bitmap overlay
- ✅ Fully DICOM-compliant for maximum compatibility

### Organization UID Management

```python
from medthermal_dicom.utils import (
    generate_organization_uid,
    validate_organization_uid,
    get_common_organization_uids
)

# Get list of common organization UIDs
common_uids = get_common_organization_uids()
for org, uid in common_uids.items():
    print(f"{org}: {uid}")

# Validate organization UID
is_valid, message = validate_organization_uid("1.2.826.0.1.3680043.8.498")
print(f"UID valid: {is_valid}, Message: {message}")

# Create thermal DICOM with organization UID
org_prefix = "1.2.826.0.1.3680043.8.498"
thermal_dicom = MedThermalDicom(organization_uid_prefix=org_prefix)

# Generate UIDs with organization prefix
study_uid = generate_organization_uid(org_prefix, "study")
series_uid = generate_organization_uid(org_prefix, "series")
instance_uid = generate_organization_uid(org_prefix, "instance")

# Get UID information
uid_info = thermal_dicom.get_organization_uid_info()
print(f"Using custom UIDs: {uid_info['is_using_custom_uids']}")
print(f"Current UIDs: {uid_info['current_uids']}")
```

## GUI Applications

### Simple GUI

The simple GUI provides an intuitive interface for creating single thermal DICOM files.

**Launch:**
```bash
python simple_dicom_gui.py
```

**Features:**
- Single file processing
- Patient information entry
- Thermal parameter configuration
- Organization UID selection
- File preview

**Workflow:**
1. Browse and select input file (image or CSV)
2. Fill in patient information (Name, ID, Age, Gender)
3. Configure thermal parameters (optional)
4. Select output folder
5. Click "Create DICOM"

## Examples

The `examples/` directory contains comprehensive usage examples:

- **`basic_usage.py`**: Complete API tutorial covering all features
- **`medical_thermal_imaging.py`**: Medical imaging workflow example
- **`organization_uid_example.py`**: Organization UID management
- **`pixel_data_example.py`**: Advanced pixel data handling

Run an example:
```bash
cd examples
python basic_usage.py
```

This will create output files in `examples/output/`:
- `thermal_sample.dcm` - DICOM file

## Requirements

### Core Dependencies

```
pydicom>=2.3.0          # DICOM file handling
numpy>=1.21.0           # Numerical operations
matplotlib>=3.5.0       # Plotting and colormaps
opencv-python>=4.5.0    # Image processing
scipy>=1.7.0            # Scientific computing
pillow>=8.0.0           # Image I/O
pandas>=1.3.0           # Data handling
```

### GUI Dependencies

```
tkinter                 # GUI framework (usually included with Python)
```

### Installation

Install all dependencies:
```bash
pip install -r requirements.txt
```

For GUI only:
```bash
pip install -r gui_requirements.txt
```

## Project Structure

```
MedThermalDicom/
├── medthermal_dicom/          # Main package
│   ├── __init__.py           # Package initialization
│   ├── core.py               # Core DICOM functionality (MedThermalDicom)
│   ├── metadata.py           # Metadata management (MedThermalMetadata)
│   ├── overlay.py            # Overlay functionality (DicomOverlay)
│   ├── utils.py              # Utility functions and classes
│   └── cli.py                # Command-line interface
├── examples/                  # Usage examples
│   ├── basic_usage.py        # Comprehensive API examples
│   ├── medical_thermal_imaging.py
│   ├── organization_uid_example.py
│   └── pixel_data_example.py
├── sample_data/              # Sample input data
│   ├── csv/                  # Temperature CSV files
│   └── images/               # Sample thermal images
├── tests/                    # Unit tests
│   └── test_core.py
├── simple_dicom_gui.py       # Simple GUI application
├── run_gui.bat               # Windows launcher
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
└── README.md                 # This file
```

## Advanced Topics

### Loading and Modifying Existing DICOM

```python
# Load existing DICOM
loaded_dicom = MedThermalDicom.load_dicom('input_thermal.dcm')

# Access temperature data
temp_data = loaded_dicom.temperature_data
print(f"Temperature range: {temp_data.min():.2f} to {temp_data.max():.2f}°C")

# Get thermal parameters
emissivity = loaded_dicom.get_thermal_parameter('emissivity')
distance = loaded_dicom.get_thermal_parameter('distance_from_camera')

# Modify and save
loaded_dicom.dataset.StudyDescription = "Updated Study Description"
loaded_dicom.set_thermal_parameters({'emissivity': 0.99})
loaded_dicom.save_dicom('modified_thermal.dcm')
```

### Working with RGB Images

```python
from PIL import Image
import numpy as np

# Load RGB image
img = Image.open("thermal_image.png")
rgb_array = np.array(img)

# Create DICOM from RGB image (no temperature data)
thermal_dicom = MedThermalDicom()
thermal_dicom.set_thermal_image(rgb_array)

# Save as DICOM
thermal_dicom.save_dicom("rgb_thermal.dcm")
```

### Metadata Validation

```python
from medthermal_dicom import MedThermalMetadata

# Create metadata handler
metadata = MedThermalMetadata()

# Set metadata
metadata.set_patient_information(patient_name="DOE^JOHN", patient_id="TH001")
metadata.set_study_information(study_description="Thermal Study")

# Validate completeness
validation = metadata.validate_metadata_completeness()
print(f"Missing required: {validation['missing_required']}")
print(f"Missing recommended: {validation['missing_recommended']}")
print(f"Warnings: {validation['warnings']}")

# Export metadata report
metadata.export_metadata_report('metadata_report.json')
```

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'medthermal_dicom'`
- **Solution**: Install the package: `pip install -r requirements.txt` or `pip install -e .`

**Issue**: GUI doesn't launch
- **Solution**: Ensure tkinter is installed. On Linux: `sudo apt-get install python3-tk`

**Issue**: Temperature values seem incorrect
- **Solution**: Check that your CSV data is in Celsius and contains actual temperature values, not pixel intensities

**Issue**: DICOM viewer shows strange colors
- **Solution**: The DICOM stores temperature data. Load with `MedThermalDicom.load_dicom()` to access temperature arrays

**Issue**: Overlays not visible in DICOM viewer
- **Solution**: Ensure overlays are added before saving. Some viewers require overlay groups to be enabled in display settings

**Issue**: CLI command not found
- **Solution**: Ensure the package is installed with `pip install -e .` to register the console script entry point

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- Documentation is updated
- New features include examples

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Support

For questions, issues, or feature requests:
- Check existing documentation in the `examples/` directory
- Review additional guides: `ORGANIZATION_UID_GUIDE.md`, `GUI_README.md`
- Open an issue on the project repository

## Citation

If you use this software in your research, please cite:

```
MedThermal DICOM - Professional Thermal Imaging DICOM Library
Version 1.0.0
https://github.com/yourusername/MedThermalDicom
```

## Acknowledgments

This library is designed for medical thermal imaging research and clinical applications. It complies with DICOM standards and includes thermal-specific extensions based on best practices in the medical imaging community.

---

**MedThermal DICOM** - Making thermal medical imaging accessible, standardized, and professional.

