#!/usr/bin/env python3
"""
Simple example demonstrating pixel data handling for multi-view thermal imaging.
"""

import numpy as np
import os
import sys
# Add parent directory to Python path to allow importing medthermal_dicom when running examples directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from medthermal_dicom.core import MedThermalDicom
from medthermal_dicom.metadata import MedThermalMetadata


def create_view_specific_thermal_data():
    """Create different thermal data for each view."""
    
    # Create different thermal data for each view
    thermal_data_dict = {
        'anterior': create_anterior_view_data(),
        'left_lateral': create_left_lateral_view_data(),
        'right_lateral': create_right_lateral_view_data()
    }
    
    return thermal_data_dict


def create_anterior_view_data():
    """Create thermal data for anterior view."""
    data = np.full((256, 256), 37.0)  # Base temperature 37°C
    
    # Add hot spots typical of anterior view
    data[100:120, 100:120] += 3.0  # Central hot spot
    data[150:170, 80:100] += 2.0   # Left hot spot
    data[150:170, 150:170] += 2.0  # Right hot spot
    
    # Add some noise
    data += np.random.normal(0, 0.5, data.shape)
    
    return data


def create_left_lateral_view_data():
    """Create thermal data for left lateral view."""
    data = np.full((256, 256), 37.0)
    
    # Add hot spots typical of left lateral view
    data[120:140, 60:80] += 4.0    # Left side hot spot
    data[100:120, 100:120] += 1.5  # Central area
    
    # Add some noise
    data += np.random.normal(0, 0.6, data.shape)
    
    return data


def create_right_lateral_view_data():
    """Create thermal data for right lateral view."""
    data = np.full((256, 256), 37.0)
    
    # Add hot spots typical of right lateral view
    data[120:140, 170:190] += 4.0  # Right side hot spot
    data[100:120, 100:120] += 1.5  # Central area
    
    # Add some noise
    data += np.random.normal(0, 0.6, data.shape)
    
    return data


def demonstrate_pixel_data_handling():
    """Demonstrate how pixel data is handled for different views."""
    
    print("=== Pixel Data Handling for Multi-View Thermal Imaging ===\n")
    
    # Initialize metadata handler
    metadata = MedThermalMetadata()
    
    # Define view configurations
    views = [
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
    
    print("1. Creating view-specific thermal data...")
    
    # Create different thermal data for each view
    thermal_data_dict = create_view_specific_thermal_data()
    
    print(f"   Created thermal data for {len(thermal_data_dict)} views:")
    for view_key, data in thermal_data_dict.items():
        print(f"     {view_key}: shape={data.shape}, temp_range=({data.min():.1f}, {data.max():.1f})°C")
    
    print("\n2. Creating series metadata...")
    
    # Create series metadata for all views
    series_metadata = metadata.create_multi_view_series(
        base_series_description="Breast Thermography",
        anatomical_region="breast",
        views=views,
        series_number=1
    )
    
    print(f"   Created {len(series_metadata)} series metadata entries")
    
    print("\n3. Creating DICOM files for each view...")
    
    # Create output directory
    os.makedirs("pixel_data_output", exist_ok=True)
    
    created_files = {}
    
    # Create DICOM files for each view
    for i, view_config in enumerate(views):
        view_key = view_config['view_key']
        
        print(f"   Processing view: {view_key}")
        
        # Get the thermal data for this specific view
        thermal_data = thermal_data_dict[view_key]
        
        # Create thermal DICOM
        thermal_dicom = MedThermalDicom()
        
        # Set the thermal image data for this view
        temp_min, temp_max = thermal_data.min(), thermal_data.max()
        thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
        
        # Set thermal parameters
        thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0,
            'relative_humidity': 45.0,
            'camera_model': 'FLIR T1K'
        }
        thermal_dicom.set_thermal_parameters(thermal_params)
        
        # Apply metadata
        series_info = series_metadata[i]
        metadata.standard_metadata.update(series_info)
        metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
        
        # Create standard DICOM
        thermal_dicom.create_standard_thermal_dicom(
            patient_name="DOE^JANE",
            patient_id="PIXEL001",
            study_description="Breast Thermography - Pixel Data Example"
        )
        
        # Save DICOM file
        filename = f"pixel_data_output/breast_{view_key}_PIXEL001.dcm"
        thermal_dicom.save_dicom(filename)
        
        created_files[view_key] = {
            'filename': filename,
            'data_shape': thermal_data.shape,
            'temp_range': (temp_min, temp_max),
            'view_position': series_info.get('ViewPosition', 'N/A'),
            'image_laterality': series_info.get('ImageLaterality', 'N/A')
        }
        
        print(f"     Created: {filename}")
    
    print("\n4. Summary of created files:")
    
    for view_key, file_info in created_files.items():
        print(f"\n   {view_key.upper()} VIEW:")
        print(f"     File: {file_info['filename']}")
        print(f"     Data shape: {file_info['data_shape']}")
        print(f"     Temperature range: {file_info['temp_range'][0]:.1f} to {file_info['temp_range'][1]:.1f}°C")
        print(f"     View position: {file_info['view_position']}")
        print(f"     Image laterality: {file_info['image_laterality']}")
    
    print("\n=== Pixel Data Handling Complete ===")
    print("\nKey Points:")
    print("1. Each view gets its own unique thermal image data")
    print("2. Data is provided as a dictionary with view keys")
    print("3. Each DICOM file contains the complete pixel data for that view")
    print("4. Metadata is consistent across views while pixel data differs")
    
    return created_files


def demonstrate_data_validation():
    """Demonstrate data validation for multi-view thermal data."""
    
    print("\n=== Data Validation Example ===\n")
    
    # Create thermal data dictionary
    thermal_data_dict = create_view_specific_thermal_data()
    
    # Define views
    views = [
        {'view_key': 'anterior'},
        {'view_key': 'left_lateral'},
        {'view_key': 'right_lateral'},
        {'view_key': 'missing_view'}  # This view has no data
    ]
    
    print("Validating thermal data for each view:")
    
    for view_config in views:
        view_key = view_config['view_key']
        
        if view_key not in thermal_data_dict:
            print(f"  ❌ {view_key}: No thermal data provided")
            continue
        
        thermal_data = thermal_data_dict[view_key]
        
        # Validate data
        if not isinstance(thermal_data, np.ndarray):
            print(f"  ❌ {view_key}: Data is not a NumPy array")
            continue
        
        if thermal_data.ndim != 2:
            print(f"  ❌ {view_key}: Data is not 2D")
            continue
        
        temp_min, temp_max = thermal_data.min(), thermal_data.max()
        
        if temp_min < -50 or temp_max > 100:
            print(f"  ⚠️  {view_key}: Unusual temperature range ({temp_min:.1f} to {temp_max:.1f}°C)")
        else:
            print(f"  ✅ {view_key}: Valid data, shape={thermal_data.shape}, temp=({temp_min:.1f}, {temp_max:.1f})°C")


if __name__ == "__main__":
    # Demonstrate pixel data handling
    created_files = demonstrate_pixel_data_handling()
    
    # Demonstrate data validation
    demonstrate_data_validation()
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("Check the 'pixel_data_output' directory for created DICOM files.")
    print("Each file contains different thermal image data for its respective view.") 