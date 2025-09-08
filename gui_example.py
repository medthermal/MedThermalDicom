#!/usr/bin/env python3
"""
Example script demonstrating the Thermal DICOM Creator GUI functionality.
This script shows how to programmatically create DICOM files using the same
functionality as the GUI.
"""

import os
import sys
import numpy as np
from datetime import datetime
from PIL import Image

# Add the thermal_dicom package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from thermal_dicom.core import ThermalDicom
    from thermal_dicom.utils import get_common_organization_uids, validate_organization_uid
except ImportError as e:
    print(f"Error importing thermal_dicom: {e}")
    sys.exit(1)


def create_sample_thermal_data():
    """Create sample thermal data for demonstration."""
    print("Creating sample thermal data...")
    
    # Create a 512x512 thermal image with temperature gradient
    rows, cols = 512, 512
    
    # Create temperature gradient (20-40°C)
    x = np.linspace(20, 40, cols)
    y = np.linspace(20, 40, rows)
    X, Y = np.meshgrid(x, y)
    
    # Add some thermal patterns (simulating hot spots)
    thermal_data = X + Y + 10 * np.sin(X/10) * np.cos(Y/10)
    
    # Add a hot spot in the center
    center_row, center_col = rows // 2, cols // 2
    for i in range(rows):
        for j in range(cols):
            distance = np.sqrt((i - center_row)**2 + (j - center_col)**2)
            if distance < 50:
                thermal_data[i, j] += 15 * np.exp(-distance / 20)
    
    return thermal_data.astype(np.float32)


def create_dicom_from_image(image_path, output_path, metadata):
    """Create DICOM from an image file."""
    print(f"Creating DICOM from image: {image_path}")
    
    # Load image
    image = Image.open(image_path)
    if image.mode != 'L':
        image = image.convert('L')
    
    # Convert to numpy array
    thermal_array = np.array(image, dtype=np.float32)
    
    # Create DICOM
    create_dicom_from_array(thermal_array, output_path, metadata)


def create_dicom_from_array(thermal_array, output_path, metadata):
    """Create DICOM from a numpy array."""
    print(f"Creating DICOM with shape: {thermal_array.shape}")
    
    # Create thermal DICOM object
    thermal_dicom = ThermalDicom(
        thermal_array=thermal_array,
        organization_uid_prefix=metadata.get('organization_uid')
    )
    
    # Set metadata
    set_dicom_metadata(thermal_dicom, metadata)
    
    # Save DICOM
    thermal_dicom.save_dicom(output_path)
    print(f"DICOM saved to: {output_path}")


def set_dicom_metadata(thermal_dicom, metadata):
    """Set metadata in the DICOM object."""
    # Patient information
    thermal_dicom.dataset.PatientName = metadata['patient_name']
    thermal_dicom.dataset.PatientID = metadata['patient_id']
    
    if metadata.get('patient_age'):
        thermal_dicom.dataset.PatientAge = metadata['patient_age']
    
    if metadata.get('patient_gender'):
        thermal_dicom.dataset.PatientSex = metadata['patient_gender']
    
    if metadata.get('referring_physician'):
        thermal_dicom.dataset.ReferringPhysicianName = metadata['referring_physician']
    
    # Study information
    thermal_dicom.dataset.StudyDescription = metadata.get('study_description', 'Thermal Medical Imaging')
    
    # Thermal parameters
    thermal_params = {
        'emissivity': metadata.get('emissivity', 0.98),
        'distance_from_camera': metadata.get('distance', 1.0),
        'ambient_temperature': metadata.get('ambient_temperature', 22.0),
        'temperature_unit': metadata.get('temperature_unit', 'Celsius')
    }
    thermal_dicom.set_thermal_parameters(thermal_params)


def validate_metadata(metadata):
    """Validate metadata before creating DICOM."""
    errors = []
    
    # Check required fields
    if not metadata.get('patient_name'):
        errors.append("Patient name is required")
    
    if not metadata.get('patient_id'):
        errors.append("Patient ID is required")
    
    if not metadata.get('output_path'):
        errors.append("Output path is required")
    
    # Check organization UID if provided
    if metadata.get('organization_uid'):
        is_valid, error_msg = validate_organization_uid(metadata['organization_uid'])
        if not is_valid:
            errors.append(f"Invalid Organization UID: {error_msg}")
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def main():
    """Main example function."""
    print("=== Thermal DICOM Creator Example ===\n")
    
    # Example metadata
    metadata = {
        'patient_name': 'DOE^JOHN',
        'patient_id': 'PAT001',
        'patient_age': '45Y',
        'patient_gender': 'M',
        'referring_physician': 'DR. SMITH',
        'study_description': 'Thermal Imaging Study - Example',
        'organization_uid': '1.2.826.0.1.3680043.8.498',  # Example medical center
        'emissivity': 0.98,
        'distance': 1.0,
        'ambient_temperature': 22.0,
        'temperature_unit': 'Celsius'
    }
    
    # Create output directory
    output_dir = "example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Example 1: Create DICOM from sample data
    print("Example 1: Creating DICOM from sample thermal data")
    print("-" * 50)
    
    if validate_metadata(metadata):
        # Generate sample data
        thermal_array = create_sample_thermal_data()
        
        # Set output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"sample_thermal_{timestamp}.dcm")
        metadata['output_path'] = output_path
        
        # Create DICOM
        create_dicom_from_array(thermal_array, output_path, metadata)
        print("✓ Example 1 completed successfully\n")
    
    # Example 2: Create DICOM from image file (if available)
    print("Example 2: Creating DICOM from image file")
    print("-" * 50)
    
    # Look for sample images in the project
    sample_images = [
        "thermal_image_clr.dcm",  # If you have sample DICOM files
        "thermal_image_gs.dcm",
        "1thermal_image_org.dcm",
        "2thermal_image_org.dcm"
    ]
    
    for image_file in sample_images:
        if os.path.exists(image_file):
            print(f"Found sample image: {image_file}")
            
            # Update metadata for this example
            metadata['patient_id'] = 'PAT002'
            metadata['patient_name'] = 'DOE^JANE'
            metadata['study_description'] = 'Thermal Imaging from Sample Image'
            
            # Set output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"image_thermal_{timestamp}.dcm")
            metadata['output_path'] = output_path
            
            # Create DICOM from image
            create_dicom_from_image(image_file, output_path, metadata)
            print("✓ Example 2 completed successfully\n")
            break
    else:
        print("No sample images found. Skipping Example 2.\n")
    
    # Example 3: Show available organization UIDs
    print("Example 3: Available Organization UIDs")
    print("-" * 50)
    
    common_uids = get_common_organization_uids()
    for name, uid in common_uids.items():
        print(f"{name}: {uid}")
    
    print("\n=== Example completed successfully! ===")
    print(f"Output files saved in: {output_dir}")
    print("\nYou can now:")
    print("1. Open the created DICOM files in a DICOM viewer")
    print("2. Run the GUI application: python simple_dicom_gui.py")
    print("3. Build the executable: python build_exe.py")


if __name__ == "__main__":
    main()
