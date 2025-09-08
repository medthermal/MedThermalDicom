# Thermal DICOM Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Medical Imaging](https://img.shields.io/badge/Medical-Imaging-green.svg)](https://en.wikipedia.org/wiki/Medical_imaging)

**The Professional Thermal DICOM Library for Medical Applications**

A comprehensive Python library specifically designed for creating, manipulating, and visualizing thermal DICOM images in medical applications. This library provides professional-grade tools for thermal imaging with full DICOM compliance, thermal-specific private tags, interactive temperature visualization, and clinical workflow support.

## 🎯 Key Features

### 🔬 **Medical-Grade Thermal DICOM Support**
- Full DICOM compliance with thermal-specific private tags
- Support for emissivity, distance, ambient temperature, and other thermal parameters
- Medical imaging standards compliance (SNOMED CT codes, anatomical regions)
- Quality control and calibration management

### 🌡️ **Advanced Temperature Management**
- Precise temperature measurement and calibration
- Multiple temperature unit support (Celsius, Fahrenheit, Kelvin)
- Emissivity and atmospheric correction algorithms
- Bad pixel detection and correction

### 📊 **Interactive Visualization**
- **Temperature hover display** - See exact temperature values on mouse hover
- Multiple thermal colormaps (Jet, Hot, Iron, Medical, etc.)
- ROI (Region of Interest) analysis tools
- Interactive web-based dashboard with Plotly and Dash
- Temperature profiles and statistical analysis

### 🏥 **Clinical Workflow Integration**
- Patient data management
- Study and series organization
- Clinical reporting and documentation
- PACS compatibility
- Quality assurance protocols

### 🔧 **Professional Tools**
- Advanced calibration utilities
- Image processing for thermal data
- Metadata validation and compliance checking
- Export capabilities (CSV, HTML, DICOM)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (when available)
pip install thermal-dicom

# Or install from source
git clone https://github.com/thermal-dicom/thermal-dicom.git
cd thermal-dicom
pip install -e .
```

### Basic Usage

```python
import numpy as np
from thermal_dicom import ThermalDicom, ThermalViewer

# Create sample thermal data
temperature_data = np.random.normal(37.0, 2.0, (512, 512))  # Body temperature simulation

# Create thermal DICOM
thermal_dicom = ThermalDicom()
thermal_dicom.set_thermal_image(temperature_data, temperature_data, (30.0, 45.0))

# Set thermal parameters
thermal_params = {
    'emissivity': 0.98,           # Human skin emissivity
    'distance_from_camera': 1.0,  # 1 meter from camera
    'ambient_temperature': 22.0,  # Room temperature
    'relative_humidity': 45.0,    # 45% humidity
    'camera_model': 'FLIR E8-XT'
}
thermal_dicom.set_thermal_parameters(thermal_params)

# Create standard medical thermal DICOM
thermal_dicom.create_standard_thermal_dicom(
    patient_name="DOE^JOHN^",
    patient_id="THERM001",
    study_description="Medical Thermal Imaging"
)

# Save DICOM file
thermal_dicom.save_dicom('thermal_image.dcm')

# Create interactive visualization
viewer = ThermalViewer(thermal_dicom)
fig = viewer.create_interactive_plot(title="Interactive Thermal Image")

# Get temperature at specific pixel (with hover functionality)
temp = thermal_dicom.get_temperature_at_pixel(256, 256)
print(f"Temperature at center: {temp:.2f}°C")
```

### Interactive Dashboard

```python
# Launch interactive web dashboard
app = viewer.create_dashboard_app()
app.run_server(debug=True)
# Open browser to http://localhost:8050 to see interactive thermal viewer
```

## 🖥️ Graphical User Interface (GUI)

### Enhanced DICOM Creator GUI

The library includes a professional GUI application for creating thermal DICOM files with an intuitive interface:

#### Running the GUI

```bash
# Run the enhanced GUI application
python simple_dicom_gui_enhanced.py
```

#### GUI Features

- **📁 Multi-file Input Support**: Select multiple image files (PNG, JPG, TIFF, BMP) or CSV files
- **👤 Patient Information Management**: Complete patient data entry with validation
- **🔬 Study Configuration**: Comprehensive study metadata including organization UIDs
- **🌡️ Thermal Parameters**: Advanced thermal imaging parameter configuration
- **📊 Multi-view Support**: Create DICOM series from multiple angles/views
- **🎨 Modern Interface**: Professional, user-friendly design with real-time validation

#### GUI Workflow

1. **Input Selection**: Browse and select multiple thermal image files or CSV data
2. **Patient Data**: Enter patient information (name, ID, age, gender)
3. **Study Setup**: Configure study description, dates, and organization UID
4. **Thermal Parameters**: Set emissivity, distance, ambient temperature, etc.
5. **Create DICOM**: Generate DICOM series with proper metadata organization

#### Supported Input Formats

- **Image Files**: PNG, JPG, JPEG, TIFF, TIF, BMP
- **CSV Files**: Temperature data in matrix format
- **Multi-view**: Automatic series creation for multiple views

#### GUI Requirements

```bash
# Install GUI dependencies
pip install tkinter pillow numpy
```

For detailed GUI usage instructions, see the [GUI README](GUI_README.md).

## 📖 Comprehensive Examples

### Multi-View Thermal Imaging

Create multiple DICOM files for different views of the same anatomical region:

```python
from thermal_dicom import ThermalDicom, ThermalMetadata
from examples.multi_view_thermal_imaging import MultiViewThermalImaging
import numpy as np

# Initialize multi-view handler
multi_view = MultiViewThermalImaging(
    organization_uid_prefix="1.2.826.0.1.3680043.8.276"
)

# Patient information
patient_name = "DOE^JANE^THERMAL"
patient_id = "MULTI001"

# Generate sample thermal data for different breast views
breast_thermal_data = {
    'frontal': np.random.normal(37.0, 1.5, (512, 512)),
    'left_obl': np.random.normal(37.0, 1.8, (512, 512)),
    'right_obl': np.random.normal(37.0, 1.6, (512, 512))
}

# Create breast thermography multi-view series
breast_files = multi_view.create_breast_thermography_views(
    patient_name=patient_name,
    patient_id=patient_id,
    thermal_data_dict=breast_thermal_data,
    output_dir="multi_view_output/breast"
)

print(f"Created {len(breast_files)} breast thermography DICOM files")
```

### Medical Thermal Imaging Workflow

```python
from thermal_dicom import ThermalDicom, ThermalViewer, ThermalMetadata
import numpy as np

# 1. Create comprehensive metadata
metadata = ThermalMetadata()

# Patient information
metadata.set_patient_information(
    patient_name="DOE^JANE^MEDICAL",
    patient_id="THERM001",
    patient_birth_date="19850315",
    patient_sex="F",
    patient_age="038Y"
)

# Study information with clinical codes
metadata.set_study_information(
    study_description="Breast Thermal Screening",
    referring_physician="DR^SMITH^ROBERT",
    procedure_code="breast_thermography"  # Uses SNOMED CT codes
)

# Equipment information
metadata.set_equipment_information(
    manufacturer="FLIR Systems",
    manufacturer_model="T1K",
    device_serial_number="TH001234",
    detector_type="Uncooled Microbolometer",
    spatial_resolution=(0.1, 0.1)  # 0.1mm pixel spacing
)

# 2. Create thermal DICOM with clinical data
thermal_dicom = ThermalDicom()
# ... set thermal image and parameters ...

# Apply metadata
metadata.apply_metadata_to_dataset(thermal_dicom.dataset)

# 3. Clinical analysis with ROI
from thermal_dicom.utils import ThermalROIAnalyzer

roi_analyzer = ThermalROIAnalyzer()
roi_mask = roi_analyzer.create_circular_roi(
    center=(256, 256), radius=50, 
    image_shape=thermal_dicom.temperature_data.shape
)

# Analyze ROI statistics
roi_stats = thermal_dicom.calculate_roi_statistics(roi_mask)
print(f"ROI mean temperature: {roi_stats['mean_temperature']:.2f}°C")
```

### Advanced Calibration

```python
from thermal_dicom import ThermalCalibrator

# Create calibrator with clinical parameters
calibrator = ThermalCalibrator()
calibrator.set_calibration_parameters(
    emissivity=0.98,      # Human skin
    distance=1.0,         # 1 meter
    ambient_temp=22.0,    # Room temperature
    relative_humidity=45.0
)

# Apply emissivity and atmospheric corrections
raw_temperature = np.array([[36.5, 37.2], [36.8, 37.0]])
calibrated_temp = calibrator.calibrate_temperature_data(raw_temperature)

# Create custom calibration curve
reference_temps = np.array([25.0, 30.0, 35.0, 40.0])
measured_temps = np.array([25.1, 29.9, 35.2, 39.8])
calib_func = calibrator.create_calibration_curve(reference_temps, measured_temps)
```

## 🏥 Clinical Applications

### Supported Medical Procedures
- **Breast Thermography** - Cancer screening and monitoring
- **Vascular Assessment** - Blood flow and circulation analysis  
- **Inflammatory Conditions** - Joint and tissue inflammation
- **Wound Healing** - Monitoring healing progress
- **Pain Management** - Objective pain assessment
- **Sports Medicine** - Injury detection and recovery monitoring

### DICOM Compliance Features
- **Private Tags** for thermal parameters (Group 0x7FE1)
- **SNOMED CT** procedure and anatomy codes
- **Standard DICOM** metadata structure
- **PACS Integration** ready
- **Quality Control** metadata tracking

## 🔧 Advanced Features

### Temperature Hover Display
The library provides **real-time temperature display** when hovering over thermal images:

```python
# Interactive plot with temperature hover
viewer = ThermalViewer(thermal_dicom)
fig = viewer.create_interactive_plot()

# Temperature is displayed as: "Position: (x, y), Temperature: 37.2°C"
# Hover over any pixel to see exact temperature value
```

### Thermal-Specific Private Tags

The library uses DICOM private tags (Group 0x7FE1) for thermal parameters:

| Parameter | Tag | Description |
|-----------|-----|-------------|
| Emissivity | (7FE1,0010) | Object emissivity (0.0-1.0) |
| Distance | (7FE1,0011) | Distance from camera (meters) |
| Ambient Temperature | (7FE1,0012) | Ambient temperature (°C) |
| Reflected Temperature | (7FE1,0013) | Reflected temperature (°C) |
| Relative Humidity | (7FE1,0015) | Relative humidity (%) |
| Camera Model | (7FE1,0020) | Thermal camera model |
| Spectral Range | (7FE1,0035) | Detector spectral range |
| Thermal Sensitivity | (7FE1,0034) | NETD in °C |

### Quality Control and Validation

```python
# Comprehensive metadata validation
validation = metadata.validate_metadata_completeness()
print(f"Missing required fields: {validation['missing_required']}")
print(f"Warnings: {validation['warnings']}")

# Quality control information
metadata.set_quality_control_info(
    uniformity_check=True,
    noise_equivalent_temperature=0.05,  # NETD in °C
    bad_pixel_count=0,
    spatial_resolution_test=True,
    temperature_accuracy=0.1  # ±0.1°C
)
```

## 📊 Visualization Capabilities

### Interactive Features
- **Temperature Hover**: Real-time temperature display on mouse hover
- **Multiple Colormaps**: Jet, Hot, Iron, Medical, Viridis, Plasma, etc.
- **ROI Analysis**: Draw and analyze regions of interest
- **Temperature Profiles**: Line profiles showing temperature variation
- **Statistical Overlays**: Mean, min, max, standard deviation display
- **Web Dashboard**: Full-featured web interface with controls

### Supported Output Formats
- **Interactive HTML** - Full interactivity preserved
- **Static Images** - PNG, JPG, SVG, PDF
- **Data Export** - CSV, JSON
- **DICOM Files** - Full medical imaging compliance

## 🧪 Testing and Quality Assurance

```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_core.py -v          # Core functionality
python -m pytest tests/test_visualization.py -v # Visualization
python -m pytest tests/test_metadata.py -v      # Metadata handling
python -m pytest tests/test_calibration.py -v   # Calibration algorithms
```

## 📁 Project Structure

```
thermal_dicom/
├── thermal_dicom/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── core.py             # Core ThermalDicom class
│   ├── visualization.py    # Interactive visualization
│   ├── utils.py            # Utility functions and calibration
│   └── metadata.py         # DICOM metadata handling
├── examples/               # Usage examples
│   ├── basic_usage.py      # Basic library usage
│   ├── medical_workflow.py # Complete clinical workflow
│   ├── multi_view_thermal_imaging.py # Multi-view DICOM creation
│   └── organization_uid_example.py # Organization UID examples
├── tests/                  # Test suite
├── docs/                   # Documentation
├── simple_dicom_gui_enhanced.py # Enhanced GUI application
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
├── ISSUES.md              # Known issues and feature requests
└── README.md              # This file
```

## 🔗 Dependencies

### Core Dependencies
- **pydicom** ≥ 2.3.0 - DICOM file handling
- **numpy** ≥ 1.21.0 - Numerical computations
- **scipy** ≥ 1.7.0 - Scientific computing

### Visualization Dependencies  
- **plotly** ≥ 5.0.0 - Interactive plotting
- **dash** ≥ 2.0.0 - Web dashboard
- **matplotlib** ≥ 3.5.0 - Static plotting

### Image Processing
- **opencv-python** ≥ 4.5.0 - Image processing
- **pillow** ≥ 8.0.0 - Image handling

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/thermal-dicom/thermal-dicom.git
cd thermal-dicom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://thermal-dicom.readthedocs.io](https://thermal-dicom.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/thermal-dicom/thermal-dicom/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thermal-dicom/thermal-dicom/discussions)
- **Email**: support@thermal-dicom.org

## 📋 Known Issues & Feature Requests

For a comprehensive list of known issues, planned features, and enhancement requests, see our [ISSUES.md](ISSUES.md) file. This includes:

- **DICOM Series Creation**: Support for creating proper DICOM series when multiple files are provided
- **Temperature Hover Display**: Enhanced temperature display for color thermal images
- **GUI Enhancements**: Body part selection and improved user interface
- **Metadata Validation**: SNOMED-CT code verification and DICOM compliance
- **Annotation Support**: Adding annotation layers to DICOM files

We welcome contributions to address these issues and implement new features!

## 🏆 Why Choose Thermal DICOM Library?

### ✅ **Medical-Grade Quality**
- Full DICOM compliance for medical environments
- Clinical workflow integration
- Quality control and validation tools
- PACS compatibility

### ✅ **Thermal Imaging Expertise**
- Purpose-built for thermal imaging applications
- Advanced calibration and correction algorithms
- Thermal-specific metadata and private tags
- Professional visualization tools

### ✅ **Interactive Temperature Display**
- **Real-time temperature hover** - See exact values instantly
- Professional thermal colormaps
- ROI analysis and statistical tools
- Web-based interactive dashboard

### ✅ **Comprehensive Feature Set**
- Complete thermal imaging workflow
- From acquisition to clinical reporting
- Extensible and customizable
- Professional documentation and support

### ✅ **Open Source & Community-Driven**
- MIT licensed for commercial use
- Active development and community
- Comprehensive documentation
- Professional support available

---

**Make Thermal DICOM Library your go-to solution for medical thermal imaging applications!**

*For medical professionals, researchers, and developers working with thermal imaging in healthcare.*