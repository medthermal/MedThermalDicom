#!/usr/bin/env python3
"""
Overlay Example for Thermal DICOM
Demonstrates how to add a binary mask overlay to thermal DICOM files.
"""


import numpy as np
from medthermal_dicom import MedThermalDicom

# Load thermal data from CSV file
# Replace with your actual CSV file path
csv_file = "path/to/your/thermal_data.csv"
img = np.loadtxt(csv_file, delimiter=",")

# User must provide binary mask for ROI
# mask should be a binary numpy array with same shape as img
# Example: mask = np.zeros_like(img, dtype=bool)
#          mask[100:200, 150:250] = True  # Define ROI region
mask = None  # TODO: User must provide the binary mask here

if mask is None:
    raise ValueError("Please provide a binary mask for the ROI")

# Create thermal DICOM with the image
thermal_dicom = MedThermalDicom()
thermal_dicom.set_thermal_image(img)
thermal_dicom.create_standard_thermal_dicom(
    patient_name="TEST^PATIENT",
    patient_id="TEST001",
    study_description="Thermal Imaging Study",
    thermal_params={
        'emissivity': 0.98,
        'distance_from_camera': 1.0,
        'ambient_temperature': 22.5,
        'reflected_temperature': 22.0,
        'relative_humidity': 45.0,
        'temperature_unit': 'Celsius'
    }
)

# Add overlay mask
thermal_dicom.add_overlay(mask)

# Save DICOM file with overlay
thermal_dicom.save_dicom("out_overlay.dcm")

print("✓ Thermal DICOM with overlay saved successfully!")
print(f"  Input shape: {img.shape}")
print(f"  Mask shape: {mask.shape}")
print(f"  Temperature range: {img.min():.2f}°C to {img.max():.2f}°C")
print(f"  Output file: out_overlay.dcm")

