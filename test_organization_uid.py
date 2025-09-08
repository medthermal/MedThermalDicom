#!/usr/bin/env python3
"""
Simple test script to verify organization UID functionality.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'thermal_dicom'))

try:
    import numpy as np
    from thermal_dicom import ThermalDicom
    from thermal_dicom.utils import generate_organization_uid, validate_organization_uid
    
    print("✓ Successfully imported thermal_dicom package")
    
    # Test 1: Basic UID generation
    print("\n=== Test 1: Basic UID Generation ===")
    
    # Without organization prefix
    std_uid = generate_organization_uid()
    print(f"Standard UID: {std_uid[:50]}...")
    
    # With organization prefix
    org_prefix = "1.2.826.0.1.3680043.8.498"
    org_uid = generate_organization_uid(org_prefix, "instance")
    print(f"Organization UID: {org_uid}")
    
    # Test 2: UID validation
    print("\n=== Test 2: UID Validation ===")
    
    # Valid UID
    is_valid, message = validate_organization_uid(org_uid)
    print(f"Valid UID: {is_valid}, Message: {message}")
    
    # Invalid UID
    is_valid, message = validate_organization_uid("1.2.3..4.5")
    print(f"Invalid UID: {is_valid}, Message: {message}")
    
    # Test 3: ThermalDicom with organization UID
    print("\n=== Test 3: ThermalDicom with Organization UID ===")
    
    # Create sample data
    thermal_data = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    
    # Create DICOM with organization UID
    thermal_dicom = ThermalDicom(
        thermal_array=thermal_data,
        organization_uid_prefix=org_prefix
    )
    
    # Get UID info
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"Organization prefix: {uid_info['organization_uid_prefix']}")
    print(f"Using custom UIDs: {uid_info['is_using_custom_uids']}")
    print(f"Study UID: {uid_info['current_uids']['study']}")
    
    # Test 4: Change UID prefix after creation
    print("\n=== Test 4: Dynamic UID Prefix Change ===")
    
    # Change to different prefix
    new_prefix = "1.2.826.0.1.3680043.8.499"
    thermal_dicom.set_organization_uid_prefix(new_prefix)
    
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"New organization prefix: {uid_info['organization_uid_prefix']}")
    print(f"New Study UID: {uid_info['current_uids']['study']}")
    
    # Change back to standard UIDs
    thermal_dicom.set_organization_uid_prefix(None)
    
    uid_info = thermal_dicom.get_organization_uid_info()
    print(f"Back to standard UIDs: {uid_info['organization_uid_prefix']}")
    print(f"Standard Study UID: {uid_info['current_uids']['study'][:50]}...")
    
    print("\n✓ All tests passed successfully!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you're running this from the package directory")
    sys.exit(1)
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
