# Pixel Data Handling for Multi-View Thermal Imaging

## Overview

This guide explains how to provide different thermal image data (pixel data) for each view in multi-view thermal imaging. Each view requires its own unique thermal image data that corresponds to the specific perspective being captured.

## How Pixel Data is Handled

### 1. **Data Structure**
Pixel data for different views is provided as a dictionary where:
- **Keys**: View identifiers (e.g., 'anterior', 'left_lateral', 'right_lateral')
- **Values**: NumPy arrays containing the thermal image data for that specific view

### 2. **Data Flow**
```
View Configuration → Thermal Data Dictionary → Individual DICOM Files
     ↓                        ↓                        ↓
  View metadata         Pixel data arrays        Complete DICOM
  (position, etc.)      (temperature values)     (metadata + pixels)
```

## Implementation Examples

### Basic Multi-View with Different Pixel Data

```python
from thermal_dicom import ThermalDicom, ThermalMetadata
import numpy as np

# Initialize metadata handler
metadata = ThermalMetadata()

# Define view configurations
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

# Provide different thermal data for each view
thermal_data_dict = {
    'anterior': np.random.normal(37.0, 1.0, (512, 512)),      # Anterior view data
    'left_lateral': np.random.normal(37.0, 1.2, (512, 512)),  # Left lateral data
    'right_lateral': np.random.normal(37.0, 1.1, (512, 512))  # Right lateral data
}

# Create DICOM files for each view
for i, view_config in enumerate(breast_views):
    view_key = view_config['view_key']
    
    # Get the thermal data for this specific view
    thermal_data = thermal_data_dict[view_key]
    
    # Create thermal DICOM
    thermal_dicom = ThermalDicom()
    
    # Set the thermal image data for this view
    temp_min, temp_max = thermal_data.min(), thermal_data.max()
    thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
    
    # Apply metadata
    series_info = series_metadata[i]
    metadata.standard_metadata.update(series_info)
    metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
    
    # Create and save DICOM
    thermal_dicom.create_standard_thermal_dicom(
        patient_name="DOE^JANE",
        patient_id="THERM001",
        study_description="Breast Thermography"
    )
    
    filename = f"breast_{view_key}_THERM001.dcm"
    thermal_dicom.save_dicom(filename)
```

## Different Data Sources for Views

### 1. **From Different Camera Positions**

```python
# Simulate different camera positions
def create_view_specific_data(view_key, base_temp=37.0, shape=(512, 512)):
    """Create view-specific thermal data based on camera position."""
    
    if view_key == 'anterior':
        # Anterior view - frontal perspective
        data = np.full(shape, base_temp)
        # Add hot spots typical of anterior view
        data[200:250, 200:250] += 3.0  # Central hot spot
        data[300:350, 150:200] += 2.0  # Left hot spot
        data[300:350, 300:350] += 2.0  # Right hot spot
        
    elif view_key == 'left_lateral':
        # Left lateral view - side perspective
        data = np.full(shape, base_temp)
        # Add hot spots typical of left lateral view
        data[250:300, 100:150] += 4.0  # Left side hot spot
        data[200:250, 200:250] += 1.5  # Central area
        
    elif view_key == 'right_lateral':
        # Right lateral view - side perspective
        data = np.full(shape, base_temp)
        # Add hot spots typical of right lateral view
        data[250:300, 350:400] += 4.0  # Right side hot spot
        data[200:250, 200:250] += 1.5  # Central area
        
    else:
        # Default data
        data = np.random.normal(base_temp, 1.0, shape)
    
    return data

# Create view-specific thermal data
thermal_data_dict = {
    'anterior': create_view_specific_data('anterior'),
    'left_lateral': create_view_specific_data('left_lateral'),
    'right_lateral': create_view_specific_data('right_lateral')
}
```

### 2. **From Different Time Points**

```python
# Simulate thermal data from different time points
def create_time_series_data(view_key, time_point, base_temp=37.0, shape=(512, 512)):
    """Create thermal data that varies over time."""
    
    # Base temperature varies with time
    time_variation = np.sin(time_point * 0.1) * 0.5
    current_temp = base_temp + time_variation
    
    # Create base data
    data = np.full(shape, current_temp)
    
    # Add time-dependent hot spots
    if view_key == 'anterior':
        # Hot spots that change over time
        hot_spot_intensity = 2.0 + np.sin(time_point * 0.2) * 1.0
        data[200:250, 200:250] += hot_spot_intensity
        
    elif view_key == 'left_lateral':
        # Different pattern for lateral view
        hot_spot_intensity = 1.5 + np.cos(time_point * 0.15) * 0.8
        data[250:300, 100:150] += hot_spot_intensity
        
    return data

# Create time series data for each view
time_points = [0, 1, 2, 3]  # Different time points
thermal_data_dict = {}

for view_config in breast_views:
    view_key = view_config['view_key']
    thermal_data_dict[view_key] = {}
    
    for t in time_points:
        thermal_data_dict[view_key][f'time_{t}'] = create_time_series_data(view_key, t)
```

### 3. **From Different Processing Parameters**

```python
# Simulate different processing parameters for each view
def create_processed_data(view_key, processing_params, base_temp=37.0, shape=(512, 512)):
    """Create thermal data with different processing parameters."""
    
    # Raw thermal data
    raw_data = np.random.normal(base_temp, 2.0, shape)
    
    # Apply view-specific processing
    if view_key == 'anterior':
        # Anterior view processing
        if processing_params.get('enhance_contrast'):
            raw_data = np.clip(raw_data * 1.2, base_temp - 5, base_temp + 5)
        if processing_params.get('smooth'):
            from scipy.ndimage import gaussian_filter
            raw_data = gaussian_filter(raw_data, sigma=1.0)
            
    elif view_key == 'left_lateral':
        # Lateral view processing
        if processing_params.get('enhance_edges'):
            from scipy.ndimage import sobel
            edges = sobel(raw_data)
            raw_data += edges * 0.1
            
    return raw_data

# Create data with different processing for each view
processing_configs = {
    'anterior': {'enhance_contrast': True, 'smooth': True},
    'left_lateral': {'enhance_edges': True},
    'right_lateral': {'enhance_contrast': False, 'smooth': False}
}

thermal_data_dict = {}
for view_config in breast_views:
    view_key = view_config['view_key']
    params = processing_configs.get(view_key, {})
    thermal_data_dict[view_key] = create_processed_data(view_key, params)
```

## Real-World Data Integration

### 1. **Loading from Different Files**

```python
import cv2
import numpy as np
from PIL import Image

def load_thermal_data_from_files(file_paths_dict):
    """Load thermal data from different files for each view."""
    
    thermal_data_dict = {}
    
    for view_key, file_path in file_paths_dict.items():
        if file_path.endswith('.npy'):
            # NumPy array file
            thermal_data_dict[view_key] = np.load(file_path)
            
        elif file_path.endswith(('.jpg', '.png', '.tiff')):
            # Image file
            if file_path.endswith('.tiff'):
                # Thermal TIFF file
                import tifffile
                thermal_data_dict[view_key] = tifffile.imread(file_path)
            else:
                # Regular image file
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                thermal_data_dict[view_key] = img.astype(np.float32)
                
        elif file_path.endswith('.mat'):
            # MATLAB file
            from scipy.io import loadmat
            mat_data = loadmat(file_path)
            # Assuming the thermal data is in a variable called 'thermal_data'
            thermal_data_dict[view_key] = mat_data['thermal_data']
    
    return thermal_data_dict

# Example usage
file_paths = {
    'anterior': 'data/breast_anterior_thermal.tiff',
    'left_lateral': 'data/breast_left_lateral_thermal.tiff',
    'right_lateral': 'data/breast_right_lateral_thermal.tiff'
}

thermal_data_dict = load_thermal_data_from_files(file_paths)
```

### 2. **From Camera Arrays**

```python
def capture_multi_view_thermal_data(camera_configs):
    """Capture thermal data from multiple cameras or positions."""
    
    thermal_data_dict = {}
    
    for view_key, camera_config in camera_configs.items():
        # This would interface with your actual thermal camera
        # For demonstration, we'll simulate the capture
        
        if camera_config['type'] == 'flir':
            # FLIR camera interface
            thermal_data_dict[view_key] = capture_flir_data(camera_config)
            
        elif camera_config['type'] == 'seek':
            # Seek Thermal camera interface
            thermal_data_dict[view_key] = capture_seek_data(camera_config)
            
        elif camera_config['type'] == 'simulated':
            # Simulated data for testing
            thermal_data_dict[view_key] = simulate_thermal_capture(camera_config)
    
    return thermal_data_dict

# Example camera configurations
camera_configs = {
    'anterior': {
        'type': 'flir',
        'position': 'front',
        'distance': 1.0,
        'emissivity': 0.98
    },
    'left_lateral': {
        'type': 'flir',
        'position': 'left_side',
        'distance': 1.2,
        'emissivity': 0.97
    },
    'right_lateral': {
        'type': 'flir',
        'position': 'right_side',
        'distance': 1.2,
        'emissivity': 0.97
    }
}

thermal_data_dict = capture_multi_view_thermal_data(camera_configs)
```

## Data Validation and Quality Control

### 1. **Data Validation**

```python
def validate_thermal_data(thermal_data_dict, view_configs):
    """Validate thermal data for each view."""
    
    validation_results = {}
    
    for view_config in view_configs:
        view_key = view_config['view_key']
        
        if view_key not in thermal_data_dict:
            validation_results[view_key] = {
                'status': 'ERROR',
                'message': f'No thermal data provided for view: {view_key}'
            }
            continue
            
        thermal_data = thermal_data_dict[view_key]
        
        # Check data type
        if not isinstance(thermal_data, np.ndarray):
            validation_results[view_key] = {
                'status': 'ERROR',
                'message': f'Thermal data for {view_key} is not a NumPy array'
            }
            continue
            
        # Check data shape
        if thermal_data.ndim != 2:
            validation_results[view_key] = {
                'status': 'ERROR',
                'message': f'Thermal data for {view_key} is not 2D'
            }
            continue
            
        # Check temperature range
        temp_min, temp_max = thermal_data.min(), thermal_data.max()
        if temp_min < -50 or temp_max > 100:
            validation_results[view_key] = {
                'status': 'WARNING',
                'message': f'Temperature range for {view_key} is unusual: {temp_min:.1f} to {temp_max:.1f}°C'
            }
        else:
            validation_results[view_key] = {
                'status': 'OK',
                'message': f'Valid thermal data: {temp_min:.1f} to {temp_max:.1f}°C'
            }
    
    return validation_results

# Validate the thermal data
validation_results = validate_thermal_data(thermal_data_dict, breast_views)

for view_key, result in validation_results.items():
    print(f"{view_key}: {result['status']} - {result['message']}")
```

### 2. **Data Preprocessing**

```python
def preprocess_thermal_data(thermal_data_dict, preprocessing_config):
    """Preprocess thermal data for each view."""
    
    processed_data = {}
    
    for view_key, thermal_data in thermal_data_dict.items():
        processed_data[view_key] = thermal_data.copy()
        
        # Apply preprocessing based on configuration
        if preprocessing_config.get('normalize'):
            # Normalize to 0-1 range
            processed_data[view_key] = (thermal_data - thermal_data.min()) / (thermal_data.max() - thermal_data.min())
            
        if preprocessing_config.get('calibrate'):
            # Apply temperature calibration
            processed_data[view_key] = apply_temperature_calibration(thermal_data, view_key)
            
        if preprocessing_config.get('denoise'):
            # Apply denoising
            from scipy.ndimage import gaussian_filter
            processed_data[view_key] = gaussian_filter(processed_data[view_key], sigma=0.5)
    
    return processed_data

# Preprocess the data
preprocessing_config = {
    'normalize': False,  # Keep original temperature values
    'calibrate': True,   # Apply calibration
    'denoise': True      # Apply denoising
}

processed_thermal_data = preprocess_thermal_data(thermal_data_dict, preprocessing_config)
```

## Complete Example with Pixel Data

```python
from thermal_dicom import ThermalDicom, ThermalMetadata
import numpy as np
import os

def create_complete_multi_view_example():
    """Complete example showing pixel data handling for multi-view thermal imaging."""
    
    # Initialize metadata handler
    metadata = ThermalMetadata()
    
    # Define views
    views = [
        {
            'view_key': 'anterior',
            'view_position': 'A',
            'view_comment': 'Anterior view',
            'image_laterality': 'B',
            'patient_position': 'HFS'
        },
        {
            'view_key': 'left_lateral',
            'view_position': 'LL',
            'view_comment': 'Left lateral view',
            'image_laterality': 'L',
            'patient_position': 'HFS'
        }
    ]
    
    # Create different thermal data for each view
    thermal_data_dict = {
        'anterior': create_anterior_view_data(),
        'left_lateral': create_lateral_view_data()
    }
    
    # Create series metadata
    series_metadata = metadata.create_multi_view_series(
        base_series_description="Multi-View Thermography",
        anatomical_region="breast",
        views=views,
        series_number=1
    )
    
    # Create DICOM files for each view
    created_files = {}
    
    for i, view_config in enumerate(views):
        view_key = view_config['view_key']
        
        # Get thermal data for this view
        thermal_data = thermal_data_dict[view_key]
        
        # Create thermal DICOM
        thermal_dicom = ThermalDicom()
        
        # Set thermal image data
        temp_min, temp_max = thermal_data.min(), thermal_data.max()
        thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
        
        # Set thermal parameters
        thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0,
            'relative_humidity': 45.0
        }
        thermal_dicom.set_thermal_parameters(thermal_params)
        
        # Apply metadata
        series_info = series_metadata[i]
        metadata.standard_metadata.update(series_info)
        metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
        
        # Create standard DICOM
        thermal_dicom.create_standard_thermal_dicom(
            patient_name="DOE^JANE",
            patient_id="THERM001",
            study_description="Multi-View Thermography"
        )
        
        # Save DICOM file
        filename = f"multiview_{view_key}_THERM001.dcm"
        thermal_dicom.save_dicom(filename)
        
        created_files[view_key] = {
            'filename': filename,
            'data_shape': thermal_data.shape,
            'temp_range': (temp_min, temp_max),
            'metadata': series_info
        }
    
    return created_files

def create_anterior_view_data():
    """Create thermal data for anterior view."""
    data = np.full((512, 512), 37.0)
    # Add hot spots typical of anterior view
    data[200:250, 200:250] += 3.0
    data[300:350, 150:200] += 2.0
    data[300:350, 300:350] += 2.0
    return data

def create_lateral_view_data():
    """Create thermal data for lateral view."""
    data = np.full((512, 512), 37.0)
    # Add hot spots typical of lateral view
    data[250:300, 100:150] += 4.0
    data[200:250, 200:250] += 1.5
    return data

# Run the complete example
if __name__ == "__main__":
    created_files = create_complete_multi_view_example()
    
    print("Created DICOM files:")
    for view_key, file_info in created_files.items():
        print(f"  {view_key}: {file_info['filename']}")
        print(f"    Data shape: {file_info['data_shape']}")
        print(f"    Temperature range: {file_info['temp_range'][0]:.1f} to {file_info['temp_range'][1]:.1f}°C")
        print(f"    View position: {file_info['metadata'].get('ViewPosition', 'N/A')}")
```

## Summary

The pixel data handling in multi-view thermal imaging works as follows:

1. **Data Organization**: Each view gets its own thermal image data in a dictionary
2. **Data Assignment**: The thermal data is assigned to each DICOM file during creation
3. **Data Validation**: The system validates that data exists for each defined view
4. **Data Processing**: Each view can have different preprocessing and calibration
5. **Data Storage**: Each DICOM file contains the complete thermal image data for that specific view

This approach ensures that each view has its own unique thermal image data while maintaining consistent metadata organization across all views. 