#!/usr/bin/env python3
"""
Test script for multi-view thermal imaging functionality.
"""

import numpy as np
import os
from thermal_dicom import ThermalDicom, ThermalMetadata

def test_multi_view_functionality():
    """Test the multi-view thermal imaging functionality."""
    
    print("=== Testing Multi-View Thermal Imaging ===\n")
    
    # Initialize metadata handler
    metadata = ThermalMetadata()
    
    # Define test views for breast thermography
    test_views = [
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
    
    print("1. Creating multi-view series metadata...")
    
    # Create series metadata for all views
    series_metadata = metadata.create_multi_view_series(
        base_series_description="Test Breast Thermography",
        anatomical_region="breast",
        views=test_views,
        series_number=1
    )
    
    print(f"   Created {len(series_metadata)} series metadata entries")
    
    # Display metadata for each view
    for i, series_info in enumerate(series_metadata):
        view_key = test_views[i]['view_key']
        print(f"\n   View {i+1}: {view_key}")
        print(f"     Series Description: {series_info.get('SeriesDescription', 'N/A')}")
        print(f"     Series Number: {series_info.get('SeriesNumber', 'N/A')}")
        print(f"     View Position: {series_info.get('ViewPosition', 'N/A')}")
        print(f"     Image Laterality: {series_info.get('ImageLaterality', 'N/A')}")
        print(f"     View Comment: {series_info.get('ViewComment', 'N/A')}")
        print(f"     View Identifier: {series_info.get('ViewIdentifier', 'N/A')}")
    
    print("\n2. Testing view information setting...")
    
    # Test individual view information setting
    view_info = metadata.set_view_information(
        view_position='A',
        image_laterality='B',
        view_comment='Test anterior view',
        image_comments='Test image comments',
        acquisition_view='Test acquisition view'
    )
    
    print("   Set view information:")
    for key, value in view_info.items():
        print(f"     {key}: {value}")
    
    print("\n3. Testing view identifier generation...")
    
    # Test view identifier generation
    test_view_info = {
        'ViewPosition': 'LL',
        'ImageLaterality': 'L',
        'ViewComment': 'Left lateral test view'
    }
    
    view_identifier = metadata._generate_view_identifier(test_view_info)
    print(f"   Generated view identifier: {view_identifier}")
    
    print("\n4. Testing available view positions...")
    
    # Display available view positions
    print("   Available view positions:")
    for code, description in metadata.VIEW_POSITIONS.items():
        print(f"     {code}: {description}")
    
    print("\n5. Testing available patient positions...")
    
    # Display available patient positions
    print("   Available patient positions:")
    for code, description in metadata.PATIENT_POSITIONS.items():
        print(f"     {code}: {description}")
    
    print("\n=== Multi-View Test Complete ===")
    
    return True

def test_view_metadata_creation():
    """Test creating actual DICOM files with view metadata."""
    
    print("\n=== Testing DICOM Creation with View Metadata ===\n")
    
    # Create output directory
    os.makedirs("test_output", exist_ok=True)
    
    # Initialize metadata handler
    metadata = ThermalMetadata()
    
    # Define a simple view
    view_config = {
        'view_key': 'test_anterior',
        'view_position': 'A',
        'view_comment': 'Test anterior view',
        'image_laterality': 'B',
        'patient_position': 'HFS'
    }
    
    # Create series metadata
    series_metadata = metadata.create_multi_view_series(
        base_series_description="Test Thermography",
        anatomical_region="breast",
        views=[view_config],
        series_number=1
    )
    
    # Generate test thermal data
    thermal_data = np.random.normal(37.0, 1.0, (256, 256))
    
    # Create thermal DICOM
    thermal_dicom = ThermalDicom()
    thermal_dicom.set_thermal_image(thermal_data, thermal_data, 
                                  (thermal_data.min(), thermal_data.max()))
    
    # Set thermal parameters
    thermal_params = {
        'emissivity': 0.98,
        'distance_from_camera': 1.0,
        'ambient_temperature': 22.0,
        'relative_humidity': 45.0
    }
    thermal_dicom.set_thermal_parameters(thermal_params)
    
    # Apply metadata
    series_info = series_metadata[0]
    metadata.standard_metadata.update(series_info)
    metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
    
    # Create standard DICOM
    thermal_dicom.create_standard_thermal_dicom(
        patient_name="TEST^PATIENT",
        patient_id="TEST001",
        study_description="Test Thermography"
    )
    
    # Save DICOM file
    filename = "test_output/test_multi_view.dcm"
    thermal_dicom.save_dicom(filename)
    
    print(f"Created test DICOM file: {filename}")
    
    # Verify metadata in the DICOM file
    print("\nVerifying DICOM metadata:")
    dataset = thermal_dicom.dataset
    
    view_fields = [
        'ViewPosition', 'ImageLaterality', 'ViewComment', 
        'ImageComments', 'ViewIdentifier', 'SeriesDescription'
    ]
    
    for field in view_fields:
        if hasattr(dataset, field):
            value = getattr(dataset, field)
            print(f"  {field}: {value}")
        else:
            print(f"  {field}: Not found")
    
    print("\n=== DICOM Creation Test Complete ===")
    
    return True

if __name__ == "__main__":
    # Run tests
    test_multi_view_functionality()
    test_view_metadata_creation()
    
    print("\nAll tests completed successfully!")
    print("\nTo run the full multi-view example:")
    print("  python examples/multi_view_thermal_imaging.py") 