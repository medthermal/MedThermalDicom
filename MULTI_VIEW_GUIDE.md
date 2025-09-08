# Multi-View Thermal Imaging Guide

## Overview

This guide explains how to create multiple DICOM files for different views of the same anatomical region in thermal imaging applications. This is essential for comprehensive medical imaging where multiple perspectives of the same body part are required.

## Key Concepts

### 1. **View Positions**
Different perspectives of the same anatomical region:
- **Anterior (A)**: Front view
- **Posterior (P)**: Back view  
- **Left Lateral (LL)**: Left side view
- **Right Lateral (RL)**: Right side view
- **Oblique Views**: Angled perspectives (LAO, RAO, LPO, RPO)

### 2. **Image Laterality**
Specifies which side of the body is being imaged:
- **L**: Left side
- **R**: Right side
- **B**: Bilateral (both sides)

### 3. **Patient Position**
The physical position of the patient during imaging:
- **HFS**: Head First Supine
- **HFP**: Head First Prone
- **STANDING**: Standing position
- **SITTING**: Sitting position

## Implementation

### Basic Multi-View Creation

```python
from thermal_dicom import ThermalDicom, ThermalMetadata
import numpy as np

# Initialize metadata handler
metadata = ThermalMetadata()

# Define different views for the same anatomical region
breast_views = [
    {
        'view_key': 'anterior',
        'view_position': 'A',
        'view_comment': 'Anterior view of both breasts',
        'image_laterality': 'B',
        'patient_position': 'HFS'
    },
    {
        'view_key': 'left_lateral',
        'view_position': 'LL',
        'view_comment': 'Left lateral view of left breast',
        'image_laterality': 'L',
        'patient_position': 'HFS'
    },
    {
        'view_key': 'right_lateral',
        'view_position': 'RL',
        'view_comment': 'Right lateral view of right breast',
        'image_laterality': 'R',
        'patient_position': 'HFS'
    }
]

# Create series metadata for all views
series_metadata = metadata.create_multi_view_series(
    base_series_description="Breast Thermography",
    anatomical_region="breast",
    views=breast_views,
    series_number=1
)
```

### Creating Individual DICOM Files

```python
# For each view, create a separate DICOM file
for i, view_config in enumerate(breast_views):
    # Create thermal DICOM
    thermal_dicom = ThermalDicom()
    
    # Set thermal image data (your actual thermal data here)
    thermal_data = your_thermal_data_for_this_view
    thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
    
    # Apply series and view metadata
    series_info = series_metadata[i]
    metadata.standard_metadata.update(series_info)
    
    # Apply metadata to DICOM
    metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
    
    # Create standard DICOM
    thermal_dicom.create_standard_thermal_dicom(
        patient_name="DOE^JANE",
        patient_id="THERM001",
        study_description="Breast Thermography"
    )
    
    # Save with view-specific filename
    filename = f"breast_thermography_{view_config['view_key']}_THERM001.dcm"
    thermal_dicom.save_dicom(filename)
```

## View Metadata Fields

### Standard DICOM View Fields

| Field | Description | Example Values |
|-------|-------------|----------------|
| `ViewPosition` | Standard DICOM view position code | 'A', 'P', 'LL', 'RL', 'LAO' |
| `ImageLaterality` | Which side of the body | 'L', 'R', 'B' |
| `PatientPosition` | Patient's physical position | 'HFS', 'STANDING', 'SITTING' |
| `ViewComment` | Additional view description | 'Anterior view of both breasts' |
| `ImageComments` | General image comments | 'Patient standing, arms at sides' |
| `AcquisitionView` | Acquisition view description | 'Frontal breast view' |

### Generated Fields

| Field | Description | Example |
|-------|-------------|---------|
| `ViewIdentifier` | Unique identifier for the view | 'A_B_Anterior_view_of_both_breasts' |
| `SeriesDescription` | View-specific series description | 'Breast Thermography - A' |
| `SeriesNumber` | Sequential series number | '1', '2', '3' |

## Complete Example: Breast Thermography

```python
from thermal_dicom import ThermalDicom, ThermalMetadata
import numpy as np
import os

class BreastThermographyMultiView:
    def __init__(self):
        self.metadata = ThermalMetadata()
    
    def create_breast_views(self, patient_name, patient_id, thermal_data_dict):
        """Create multiple DICOM files for breast thermography views."""
        
        # Define breast views
        breast_views = [
            {
                'view_key': 'anterior',
                'view_position': 'A',
                'view_comment': 'Anterior view of both breasts',
                'image_laterality': 'B',
                'patient_position': 'HFS'
            },
            {
                'view_key': 'left_lateral',
                'view_position': 'LL',
                'view_comment': 'Left lateral view of left breast',
                'image_laterality': 'L',
                'patient_position': 'HFS'
            },
            {
                'view_key': 'right_lateral',
                'view_position': 'RL',
                'view_comment': 'Right lateral view of right breast',
                'image_laterality': 'R',
                'patient_position': 'HFS'
            }
        ]
        
        # Create series metadata
        series_metadata = self.metadata.create_multi_view_series(
            base_series_description="Breast Thermography",
            anatomical_region="breast",
            views=breast_views,
            series_number=1
        )
        
        created_files = {}
        
        # Create DICOM for each view
        for i, view_config in enumerate(breast_views):
            view_key = view_config['view_key']
            
            if view_key not in thermal_data_dict:
                continue
                
            thermal_data = thermal_data_dict[view_key]
            
            # Create thermal DICOM
            thermal_dicom = ThermalDicom()
            thermal_dicom.set_thermal_image(thermal_data, thermal_data, 
                                          (thermal_data.min(), thermal_data.max()))
            
            # Apply metadata
            series_info = series_metadata[i]
            self.metadata.standard_metadata.update(series_info)
            self.metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
            
            # Create and save DICOM
            thermal_dicom.create_standard_thermal_dicom(
                patient_name=patient_name,
                patient_id=patient_id,
                study_description="Breast Thermography"
            )
            
            filename = f"breast_{view_key}_{patient_id}.dcm"
            thermal_dicom.save_dicom(filename)
            created_files[view_key] = filename
        
        return created_files

# Usage
breast_multi_view = BreastThermographyMultiView()

# Your thermal data for different views
thermal_data = {
    'anterior': np.random.normal(37, 1, (512, 512)),
    'left_lateral': np.random.normal(37, 1, (512, 512)),
    'right_lateral': np.random.normal(37, 1, (512, 512))
}

# Create multi-view DICOM files
files = breast_multi_view.create_breast_views(
    patient_name="DOE^JANE",
    patient_id="BREAST001",
    thermal_data_dict=thermal_data
)
```

## Advanced Features

### 1. **Custom View Positions**

You can define custom view positions for specific applications:

```python
# Custom view position
custom_view = {
    'view_key': 'custom_angle',
    'view_position': 'CUSTOM_45',  # Custom position code
    'view_comment': '45-degree oblique view',
    'image_laterality': 'L',
    'patient_position': 'STANDING'
}
```

### 2. **View-Specific Thermal Parameters**

Different views may require different thermal parameters:

```python
# View-specific thermal parameters
view_thermal_params = {
    'anterior': {
        'emissivity': 0.98,
        'distance_from_camera': 1.0,
        'ambient_temperature': 22.0
    },
    'lateral': {
        'emissivity': 0.97,  # Different for side view
        'distance_from_camera': 1.2,  # Further distance
        'ambient_temperature': 22.0
    }
}
```

### 3. **Series Organization**

Multiple views can be organized into different series:

```python
# Create separate series for different view types
anterior_series = metadata.create_multi_view_series(
    base_series_description="Breast Thermography - Anterior Views",
    anatomical_region="breast",
    views=[anterior_views],
    series_number=1
)

lateral_series = metadata.create_multi_view_series(
    base_series_description="Breast Thermography - Lateral Views", 
    anatomical_region="breast",
    views=[lateral_views],
    series_number=2
)
```

## Best Practices

### 1. **Consistent Naming**
- Use consistent view keys across your application
- Include anatomical region in filenames
- Use standardized DICOM view position codes

### 2. **Metadata Consistency**
- Maintain consistent patient information across all views
- Use the same study ID for related views
- Ensure proper series numbering

### 3. **File Organization**
```
patient_study/
├── breast_thermography/
│   ├── breast_anterior_THERM001.dcm
│   ├── breast_left_lateral_THERM001.dcm
│   └── breast_right_lateral_THERM001.dcm
├── whole_body_thermography/
│   ├── whole_body_anterior_THERM001.dcm
│   ├── whole_body_posterior_THERM001.dcm
│   └── whole_body_lateral_THERM001.dcm
```

### 4. **Validation**
- Verify that all required metadata fields are present
- Check that view positions are valid
- Ensure proper series organization

## Common Use Cases

### 1. **Breast Thermography**
- Anterior view (both breasts)
- Left/Right lateral views
- Oblique views for better visualization

### 2. **Whole Body Thermography**
- Anterior view
- Posterior view
- Left/Right lateral views

### 3. **Limb Thermography**
- Anterior/Posterior views
- Medial/Lateral views
- Multiple angles for comprehensive assessment

### 4. **Facial Thermography**
- Frontal view
- Left/Right profile views
- Oblique views for detailed analysis

## Troubleshooting

### Common Issues

1. **Missing View Data**
   - Ensure thermal data is provided for all defined views
   - Check that view keys match between configuration and data

2. **Invalid View Positions**
   - Use standard DICOM view position codes
   - Validate view positions against the VIEW_POSITIONS dictionary

3. **Series Organization**
   - Ensure proper series numbering
   - Check that series descriptions are unique and descriptive

4. **Metadata Consistency**
   - Verify that patient information is consistent across views
   - Ensure proper study and series organization

## Summary

The multi-view thermal imaging system provides:

- **Standardized view positions** following DICOM standards
- **Proper series organization** for multiple views
- **Unique identifiers** for each view combination
- **Consistent metadata** across related DICOM files
- **Flexible configuration** for different anatomical regions

This approach ensures that multiple views of the same anatomical region are properly organized, labeled, and can be easily managed in PACS systems and medical imaging workflows. 