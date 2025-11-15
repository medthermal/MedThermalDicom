# MedThermal DICOM

**Professional thermal imaging DICOM library for medical applications**

A comprehensive Python library for creating and managing thermal DICOM images with support for thermal-specific metadata.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Converting FLIR Radiometric Images to CSV](#converting-flir-radiometric-images-to-csv)
- [Core API Reference](#core-api-reference)
  - [MedThermalDicom Class](#medthermaldicom-class)
  - [MedThermalMetadata Class](#medthermalmetadata-class)
  - [Utility Classes](#utility-classes)
- [Usage Examples](#usage-examples)
  - [Basic DICOM Creation](#basic-dicom-creation)
  - [Setting Thermal Parameters](#setting-thermal-parameters)
  - [Metadata Management](#metadata-management)
  - [Adding Overlays for ROI Visualization](#adding-overlays-for-roi-visualization)
- [GUI Application](#gui-application)
- [Examples](#examples)
- [License](#license)

## Overview

MedThermal DICOM is designed for researchers, clinicians, and developers working with medical thermal imaging. It provides:

- **Python API**: Programmatic creation and manipulation of thermal DICOM files
- **GUI Applications**: User-friendly interfaces for non-programmers
- **Standards Compliance**: Full DICOM compliance with thermal-specific extensions
- **Rich Metadata**: Comprehensive thermal imaging metadata support

## Features

### Core Features
- ✅ Create DICOM files from thermal images (PNG, JPG)
- ✅ Import temperature data from CSV or numpy arrays
- ✅ Set comprehensive thermal parameters (emissivity, distance, ambient temperature, etc.)
- ✅ Manage patient, study, and series metadata
- ✅ Add binary mask overlays for ROI visualization
- ✅ Export to standard DICOM format
- ✅ Organization UID management for custom UID generation

### GUI Features
- 🎨 Simple user interface
- 🏥 Comprehensive patient and study information entry
- 🌡️ Thermal parameter configuration
- 📊 Organization UID management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

1. Clone or download this repository:
```bash
git clone https://github.com/medthermal/MedThermalDicom.git
cd MedThermalDicom
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

```bash
pip install -e .
```

### Install as Package from PyPI
```bash
pip install medthermal-dicom
```
This installs the `medthermal_dicom` package and makes it available system-wide.

## Quick Start 

### Using the API

Here's a minimal example to create a DICOM file with metadata and body part:

```python
import numpy as np
from medthermal_dicom import MedThermalDicom, MedThermalMetadata

# Create thermal DICOM
thermal_dicom = MedThermalDicom()
temperature_data = np.random.rand(256, 256) * 10 + 30  # Sample temperature data
thermal_dicom.set_thermal_image(temperature_data,  (30.0, 40.0))

# Add metadata and set body part
metadata = MedThermalMetadata()
metadata.set_patient_information(patient_name="TEST^PATIENT", patient_id="TH001")
metadata.set_study_information(study_description="Thermal Study")
metadata.set_series_information(series_description="Chest Imaging", body_part="chest")
metadata.apply_metadata_to_dataset(thermal_dicom.dataset)

# Save DICOM file
thermal_dicom.save_dicom("output.dcm")
```

## Converting FLIR Radiometric Images to CSV

If you have radiometric JPG images from FLIR thermal cameras, you need to convert them to CSV format before using them with MedThermal DICOM.

### Step 1: Download FLIR Tools
- Visit [FLIR Tools Download Page](https://www.flir.com/products/flir-tools/)
- Download and install **FLIR Tools** 

### Step 2: Open Radiometric JPG in FLIR Tools
- Launch FLIR Tools
- Open your radiometric JPG file 

### Step 3: Export to CSV
- Right-click on the thermal image
- Select **"Export to CSV"** 
- Save the CSV file to your desired location
- Use CSV with MedThermal DICOM as shown in the [Examples](#usage-examples) or [GUI](#gui-application)

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

Thermal DICOM metadata management for medical imaging standards compliance.

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
    temperature_range=(temp_min, temp_max)
)


```

### Setting Thermal Parameters

```python
# Assuming thermal_dicom is already created (see Basic DICOM Creation)

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
from medthermal_dicom import MedThermalMetadata, MedThermalDicom
import numpy as np

# Create thermal_dicom instance
thermal_dicom = MedThermalDicom()
temperature_data = np.random.rand(256, 256) * 20 + 25
thermal_dicom.set_thermal_image(temperature_data,  
                               (temperature_data.min(), temperature_data.max()))

# Create metadata handler
metadata = MedThermalMetadata()

# Set patient information
metadata.set_patient_information(
    patient_name="ANONYMOUS^PATIENT",
    patient_id="TH001",
    patient_birth_date="19850315",
    patient_sex="M",
    patient_age="038Y"
)

# Set study information
metadata.set_study_information(
    study_description="Breast Thermal Imaging Study",
    accession_number="ACC123456",
    referring_physician="DR^EXAMPLE^PHYSICIAN",
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

# Save DICOM file
thermal_dicom.save_dicom("output.dcm")
```

### Adding Overlays for ROI Visualization

You can add binary mask overlays to highlight regions of interest (ROI) in thermal images:

```python
import numpy as np
from medthermal_dicom import MedThermalDicom

# Load thermal data
temperature_data = np.loadtxt("thermal_data.csv", delimiter=",")

# Create thermal DICOM
thermal_dicom = MedThermalDicom()
thermal_dicom.set_thermal_image(temperature_data)

# Create binary mask for ROI (same shape as thermal data)
roi_mask = np.zeros_like(temperature_data, dtype=bool)
roi_mask[100:200, 150:250] = True  # Define rectangular ROI

# Add overlay to DICOM
thermal_dicom.add_overlay(roi_mask)

# Set patient info and thermal parameters
thermal_dicom.create_standard_thermal_dicom(
    patient_name="TEST^PATIENT",
    patient_id="THERMAL001",
    study_description="Thermal Imaging with ROI",
    thermal_params={
        'emissivity': 0.98,
        'distance_from_camera': 1.0,
        'ambient_temperature': 22.5
    }
)

# Save DICOM file with overlay
thermal_dicom.save_dicom("output_with_overlay.dcm")
```

**Key Points:**
- The mask must be a boolean numpy array with the same shape as the thermal image
- Overlay pixels appear highlighted in DICOM viewers that support overlays
- Overlays are stored in DICOM-compliant overlay planes



## GUI Application

The simple GUI provides an intuitive interface for creating single thermal DICOM files.
#### Windows:
Unzip methermaldicom_gui.zip file 
```bash
methermaldicom_gui.exe
```
**Launch:**
```bash
python simple_dicom_gui.py
```

**Features:**
- Single file processing
- Patient information entry
- Thermal parameter configuration
- Organization UID selection

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
- **`overlay_example.py`**: Add binary mask overlays for ROI visualization
- **`multi_view_thermal_imaging.py`**: Multi-view thermal imaging with different anatomical views


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




## Contributing

Contributions are welcome! \
Please write to medthermaldicom@niramai.com

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Support

For questions, issues, or feature requests:
- Check existing documentation in the `examples/` directory
- Review additional guides: `ORGANIZATION_UID_GUIDE.md`, `GUI_README.md`
- Open an issue on the project repository

## Citation

If you use this code in your research, please cite our work using the following reference:


```
Govindaraju, Bharath, Siva Teja Kakileti, Ronak Dedhiya, Geetha Manjunath."MedThermal-DICOM: An Open-Source DICOM-Compliant Framework for Medical Thermal Imaging Enabling Clinical Integration and Research Reproducibility
" 4th International Conference on Artificial Intelligence over Infrared Images for Medical Applications.
```

## Acknowledgments

We gratefully acknowledge:

- **[DICOM Standards Committee](https://www.dicomstandard.org/)** - For establishing and maintaining comprehensive medical imaging standards that enable interoperability across healthcare systems
- **[PyDICOM Project](https://pydicom.github.io/)** - For providing excellent Python tools for working with DICOM files, which form the foundation of this library
- **Medical Thermal Imaging Community** - For advancing research and clinical applications in thermal imaging

---

**MedThermal DICOM** - Making thermal medical imaging accessible, standardized, and professional.

