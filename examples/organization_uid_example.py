#!/usr/bin/env python3
"""
Organization UID Example for Thermal DICOM Library.

This example demonstrates how to:
1. Create thermal DICOMs with your organization's UID prefix
2. Fall back to standard UID generation when no prefix is provided
3. Change organization UIDs after creation
4. Validate and display UID information
"""

import os
import numpy as np
from medthermal_dicom.core import MedThermalDicom


def create_thermal_with_org_uid():
    """Create thermal DICOM with organization UID prefix."""
    print("=== Creating Thermal DICOM with Organization UID ===")
    
    # Your organization UID prefix (replace with your actual UID)
    org_uid = "1.2.826.0.1.3680043.8.498"
    
    # Create sample thermal data
    temperature_data = np.random.normal(37.0, 2.0, (256, 256))
    
    # Create thermal DICOM with organization UID
    thermal_dicom = MedThermalDicom(organization_uid_prefix=org_uid)
    
    # Set thermal image
    thermal_dicom.set_thermal_image(temperature_data, temperature_data, (30.0, 45.0))
    
    # Set basic thermal parameters
    thermal_params = {
        'emissivity': 0.98,
        'distance_from_camera': 1.0,
        'ambient_temperature': 22.0,
    }
    thermal_dicom.set_thermal_parameters(thermal_params)
    
    # Display UID information
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"✓ Organization UID prefix: {uid_info['organization_uid_prefix']}")
    print(f"✓ Using custom UIDs: {uid_info['is_using_custom_uids']}")
    print("\nGenerated UIDs:")
    for uid_type, uid_value in uid_info['current_uids'].items():
        if uid_value:
            print(f"  {uid_type}: {uid_value}")
    
    return thermal_dicom


def create_thermal_without_org_uid():
    """Create thermal DICOM without organization UID (uses standard generation)."""
    print("\n=== Creating Thermal DICOM without Organization UID ===")
    
    # Create sample thermal data
    temperature_data = np.random.normal(37.0, 2.0, (256, 256))
    
    # Create thermal DICOM without organization UID
    thermal_dicom = MedThermalDicom()  # No organization_uid_prefix
    
    # Set thermal image
    thermal_dicom.set_thermal_image(temperature_data, temperature_data, (30.0, 45.0))
    
    # Display UID information
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"✓ Organization UID prefix: {uid_info['organization_uid_prefix']}")
    print(f"✓ Using custom UIDs: {uid_info['is_using_custom_uids']}")
    print("\nGenerated UIDs:")
    for uid_type, uid_value in uid_info['current_uids'].items():
        if uid_value:
            print(f"  {uid_type}: {uid_value}")
    
    return thermal_dicom


def change_organization_uid_after_creation():
    """Demonstrate changing organization UID after DICOM creation."""
    print("\n=== Changing Organization UID After Creation ===")
    
    # Create thermal DICOM without organization UID
    thermal_dicom = create_thermal_without_org_uid()
    
    # Change to organization UID
    new_org_uid = "1.2.826.0.1.3680043.8.499"  # Different UID
    print(f"\nChanging to new organization UID: {new_org_uid}")
    
    thermal_dicom.set_organization_uid_prefix(new_org_uid)
    
    # Display updated UID information
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"✓ Updated organization UID prefix: {uid_info['organization_uid_prefix']}")
    print(f"✓ Using custom UIDs: {uid_info['is_using_custom_uids']}")
    print("\nUpdated UIDs:")
    for uid_type, uid_value in uid_info['current_uids'].items():
        if uid_value:
            print(f"  {uid_type}: {uid_value}")
    
    return thermal_dicom


def demonstrate_uid_validation():
    """Demonstrate UID validation capabilities."""
    print("\n=== UID Validation Examples ===")
    
    from medthermal_dicom.utils import validate_organization_uid
    
    # Valid UIDs
    valid_uids = [
        "1.2.826.0.1.3680043.8.498",
        "1.2.826.0.1.3680043.8.499",
        "1.2.826.0.1.3680043.8.500"
    ]
    
    # Invalid UIDs
    invalid_uids = [
        "1.2.826.0.1.3680043.8.498.",  # Trailing dot
        "1.2.826.0.1.3680043..8.498",  # Consecutive dots
        "1.2.826.0.1.3680043.8.498a",  # Contains letter
        "1.2.826.0.1.3680043.8.-498",  # Negative number
        "1.2.826.0.1.3680043.8.498" * 10  # Too long
    ]
    
    print("Validating UIDs:")
    for uid in valid_uids:
        is_valid, message = validate_organization_uid(uid)
        print(f"  {uid}: {'✓' if is_valid else '✗'} {message}")
    
    print("\nValidating invalid UIDs:")
    for uid in invalid_uids:
        is_valid, message = validate_organization_uid(uid)
        print(f"  {uid}: {'✓' if is_valid else '✗'} {message}")


def save_and_load_with_org_uid():
    """Demonstrate saving and loading DICOMs with organization UIDs."""
    print("\n=== Saving and Loading with Organization UIDs ===")
    
    # Create thermal DICOM with organization UID
    thermal_dicom = create_thermal_with_org_uid()
    
    # Save DICOM file
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'thermal_with_org_uid.dcm')
    
    thermal_dicom.save_dicom(filename)
    print(f"✓ Saved DICOM with organization UID to: {filename}")
    
    # Load DICOM file
    loaded_dicom = MedThermalDicom.load_dicom(filename)
    
    # Check if organization UID information is preserved
    uid_info = loaded_dicom.get_organization_uid_info()
    print(f"✓ Loaded DICOM organization UID prefix: {uid_info['organization_uid_prefix']}")
    
    return loaded_dicom


def main():
    """Run organization UID examples."""
    print("Thermal DICOM Library - Organization UID Examples")
    print("=" * 60)
    
    try:
        # Create with organization UID
        thermal_with_org = create_thermal_with_org_uid()
        
        # Create without organization UID
        thermal_without_org = create_thermal_without_org_uid()
        
        # Change organization UID after creation
        thermal_changed = change_organization_uid_after_creation()
        
        # Demonstrate UID validation
        demonstrate_uid_validation()
        
        # Save and load with organization UIDs
        loaded_dicom = save_and_load_with_org_uid()
        
        print("\n" + "=" * 60)
        print("✓ All organization UID examples completed successfully!")
        print("\nKey Points:")
        print("  1. Organization UIDs are automatically applied to all DICOM UIDs")
        print("  2. If no organization UID is provided, standard PyDICOM UIDs are used")
        print("  3. Organization UIDs can be changed after creation")
        print("  4. UID validation ensures proper format compliance")
        print("  5. Organization UID information is preserved when saving/loading")
        
        print("\nTo use your own organization UID:")
        print("  1. Replace the example UID in the code with your actual UID")
        print("  2. Ensure your UID follows DICOM format standards")
        print("  3. Consider registering your UID with DICOM authorities")
        
    except Exception as e:
        print(f"\n[ERROR] Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
