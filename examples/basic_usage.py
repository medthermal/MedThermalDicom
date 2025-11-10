#!/usr/bin/env python3
"""
Basic usage example for the MedThermal DICOM Library.

This example demonstrates how to:
1. Create thermal DICOM images with proper metadata
2. Set thermal-specific parameters (emissivity, distance, etc.)
3. Visualize thermal images with temperature hover display
4. Save and load thermal DICOM files
5. Perform basic thermal image analysis
"""

import sys
import os
# Add parent directory to Python path to allow importing medthermal_dicom
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from medthermal_dicom import MedThermalDicom, MedThermalViewer, MedThermalTemperatureConverter, MedThermalCalibrator, MedThermalMetadata
from medthermal_dicom.utils import MedThermalROIAnalyzer


def create_sample_thermal_data():
    """Create sample thermal data for demonstration."""
    # Create a synthetic thermal image (512x512)
    rows, cols = 512, 512
    
    # Create a temperature gradient with some hot spots
    x = np.linspace(-5, 5, cols)
    y = np.linspace(-5, 5, rows)
    X, Y = np.meshgrid(x, y)
    
    # Base temperature field with gradient
    base_temp = 25.0 + 5.0 * np.exp(-(X**2 + Y**2) / 10)
    
    # Add some hot spots (simulating inflammation or increased blood flow)
    hot_spot1 = 8.0 * np.exp(-((X - 2)**2 + (Y - 1)**2) / 0.5)
    hot_spot2 = 6.0 * np.exp(-((X + 1.5)**2 + (Y + 2)**2) / 0.8)
    hot_spot3 = 4.0 * np.exp(-((X + 2)**2 + (Y - 2.5)**2) / 0.3)
    
    # Combine temperature components
    temperature_data = base_temp + hot_spot1 + hot_spot2 + hot_spot3
    
    # Add some noise
    noise = np.random.normal(0, 0.5, temperature_data.shape)
    temperature_data += noise
    
    # Ensure realistic temperature range (20-45°C for medical thermal imaging)
    temperature_data = np.clip(temperature_data, 20.0, 45.0)
    
    return temperature_data


def basic_thermal_dicom_creation():
    """Demonstrate basic thermal DICOM creation."""
    print("=== Basic MedThermal DICOM Creation ===")
    
    # Create sample thermal data
    temperature_data = create_sample_thermal_data()
    print(f"Created thermal data: {temperature_data.shape}")
    print(f"Temperature range: {temperature_data.min():.2f}°C to {temperature_data.max():.2f}°C")
    
    # Create thermal DICOM instance
    medthermal_dicom = MedThermalDicom()
    
    # Set thermal image data
    temp_range = (temperature_data.min(), temperature_data.max())
    medthermal_dicom.set_thermal_image(temperature_data, temperature_data, temp_range)
    
    # Set thermal-specific parameters
    thermal_params = {
        'emissivity': 0.98,  # Human skin emissivity
        'distance_from_camera': 1.0,  # 1 meter from camera
        'ambient_temperature': 22.0,  # Room temperature
        'reflected_temperature': 22.0,  # Assumed same as ambient
        'relative_humidity': 45.0,  # 45% humidity
        'camera_model': 'FLIR E8-XT',
        'camera_serial': 'TH001234',
        'spectral_range': '7.5-14.0 um',
        'thermal_sensitivity': 0.05,  # 0.05°C NETD
        'acquisition_mode': 'Medical Thermal Imaging'
    }
    
    medthermal_dicom.set_thermal_parameters(thermal_params)
    
    # Create standard medical thermal DICOM
    medthermal_dicom.create_standard_thermal_dicom(
        patient_name="DOE^JOHN^",
        patient_id="THERM001",
        study_description="Breast Thermal Imaging Study"
    )
    
    print("[OK] MedThermal DICOM created with parameters:")
    for param, value in thermal_params.items():
        print(f"  {param}: {value}")
    
    return medthermal_dicom


def demonstrate_metadata_handling():
    """Demonstrate comprehensive metadata handling."""
    print("\n=== Metadata Handling ===")
    
    # Create metadata handler
    metadata = MedThermalMetadata()
    
    # Set patient information
    metadata.set_patient_information(
        patient_name="DOE^JOHN^MEDICAL",
        patient_id="THERM001",
        patient_birth_date="19850315",
        patient_sex="M",
        patient_age="038Y"
    )
    
    # Set study information
    metadata.set_study_information(
        study_description="Medical Thermal Imaging - Breast Screening",
        accession_number="ACC123456",
        referring_physician="DR^SMITH^JANE",
        procedure_code="breast_thermography"
    )
    
    # Set series information
    metadata.set_series_information(
        series_description="Thermal Images - Anterior View",
        body_part="breast",
        patient_position="HFS"
    )
    
    # Set equipment information
    metadata.set_equipment_information(
        manufacturer="FLIR Systems",
        manufacturer_model="E8-XT",
        device_serial_number="TH001234",
        software_version="MedThermalDICOM v1.0",
        detector_type="Uncooled Microbolometer",
        spatial_resolution=(0.1, 0.1)  # 0.1mm pixel spacing
    )
    
    # Set calibration information
    metadata.set_thermal_calibration_info(
        calibration_method="Blackbody Reference",
        reference_temperature=37.0,
        calibration_uncertainty=0.1,
        blackbody_temperature=37.0
    )
    
    # Set quality control information
    metadata.set_quality_control_info(
        uniformity_check=True,
        noise_equivalent_temperature=0.05,
        bad_pixel_count=0,
        spatial_resolution_test=True,
        temperature_accuracy=0.1
    )
    
    # Validate metadata
    validation = metadata.validate_metadata_completeness()
    print("[OK] Metadata validation:")
    print(f"  Missing required fields: {len(validation['missing_required'])}")
    print(f"  Missing recommended fields: {len(validation['missing_recommended'])}")
    print(f"  Warnings: {len(validation['warnings'])}")
    
    return metadata


def demonstrate_calibration():
    """Demonstrate thermal calibration capabilities."""
    print("\n=== MedThermal Calibration ===")
    
    # Create sample raw temperature data
    raw_temp = create_sample_thermal_data()
    
    # Create calibrator
    calibrator = MedThermalCalibrator()
    
    # Set calibration parameters
    calibrator.set_calibration_parameters(
        emissivity=0.98,
        distance=1.0,
        ambient_temp=22.0,
        relative_humidity=45.0
    )
    
    # Apply calibration
    calibrated_temp = calibrator.calibrate_temperature_data(raw_temp)
    
    print("[OK] Calibration applied:")
    print(f"  Raw temperature range: {raw_temp.min():.2f}°C to {raw_temp.max():.2f}°C")
    print(f"  Calibrated range: {calibrated_temp.min():.2f}°C to {calibrated_temp.max():.2f}°C")
    print(f"  Mean difference: {np.mean(calibrated_temp - raw_temp):.3f}°C")
    
    return calibrated_temp


def demonstrate_visualization():
    """Demonstrate thermal visualization capabilities."""
    print("\n=== MedThermal Visualization ===")
    
    # Create thermal DICOM
    medthermal_dicom = basic_thermal_dicom_creation()
    
    # Create viewer
    viewer = MedThermalViewer(medthermal_dicom)
    
    # Create interactive plot
    fig = viewer.create_interactive_plot(
        width=800, 
        height=600,
        title="Medical Thermal Imaging - Interactive Temperature Display"
    )
    
    # Save visualization
    os.makedirs('output', exist_ok=True)
    viewer.save_visualization('output/thermal_visualization.html', format='html')
    print("[OK] Interactive visualization saved to 'output/thermal_visualization.html'")
    
    # Create temperature histogram
    hist_fig = viewer.create_temperature_histogram()
    hist_fig.write_html('output/temperature_histogram.html')
    print("[OK] Temperature histogram saved to 'output/temperature_histogram.html'")
    
    # Demonstrate ROI analysis
    roi_analyzer = MedThermalROIAnalyzer()
    
    # Create circular ROI
    roi_mask = roi_analyzer.create_circular_roi(
        center=(256, 300), 
        radius=50, 
        image_shape=medthermal_dicom.temperature_data.shape
    )
    
    # Add ROI overlay
    viewer.add_roi_overlay(roi_mask, "Hot Spot ROI", "yellow", 2)
    
    # Analyze ROI statistics
    roi_stats = medthermal_dicom.calculate_roi_statistics(roi_mask)
    print("[OK] ROI Analysis:")
    print(f"  Mean temperature: {roi_stats['mean_temperature']:.2f}°C")
    print(f"  Max temperature: {roi_stats['max_temperature']:.2f}°C")
    print(f"  Min temperature: {roi_stats['min_temperature']:.2f}°C")
    print(f"  Std deviation: {roi_stats['std_temperature']:.2f}°C")
    print(f"  Pixel count: {roi_stats['pixel_count']}")
    
    return viewer


def demonstrate_temperature_conversion():
    """Demonstrate temperature unit conversions."""
    print("\n=== Temperature Conversions ===")
    
    # Sample temperature in Celsius
    temp_celsius = 37.5
    
    # Convert to other units
    temp_fahrenheit = MedThermalTemperatureConverter.celsius_to_fahrenheit(temp_celsius)
    temp_kelvin = MedThermalTemperatureConverter.celsius_to_kelvin(temp_celsius)
    
    print(f"[OK] Temperature conversions for {temp_celsius}°C:")
    print(f"  Fahrenheit: {temp_fahrenheit:.2f}°F")
    print(f"  Kelvin: {temp_kelvin:.2f}K")
    
    # Convert back to verify
    temp_back = MedThermalTemperatureConverter.fahrenheit_to_celsius(temp_fahrenheit)
    print(f"  Back to Celsius: {temp_back:.2f}°C (difference: {abs(temp_celsius - temp_back):.6f}°C)")


def demonstrate_file_operations():
    """Demonstrate saving and loading thermal DICOM files."""
    print("\n=== File Operations ===")
    
    # Create thermal DICOM
    medthermal_dicom = basic_thermal_dicom_creation()
    
    # Apply metadata
    metadata = demonstrate_metadata_handling()
    metadata.apply_metadata_to_dataset(medthermal_dicom.dataset)
    
    # Save DICOM file
    os.makedirs('output', exist_ok=True)
    medthermal_dicom.save_dicom('output/thermal_sample.dcm')
    print("[OK] MedThermal DICOM saved to 'output/thermal_sample.dcm'")
    
    # Load DICOM file
    loaded_thermal = MedThermalDicom.load_dicom('output/thermal_sample.dcm')
    print("[OK] MedThermal DICOM loaded successfully")
    
    # Verify loaded data
    if loaded_thermal.thermal_array is not None:
        print(f"  Loaded image shape: {loaded_thermal.thermal_array.shape}")
        print(f"  Patient name: {loaded_thermal.dataset.PatientName}")
        print(f"  Study description: {loaded_thermal.dataset.StudyDescription}")
        
        # Check thermal parameters
        emissivity = loaded_thermal.get_thermal_parameter('emissivity')
        distance = loaded_thermal.get_thermal_parameter('distance_from_camera')
        print(f"  Emissivity: {emissivity}")
        print(f"  Distance from camera: {distance}m")
    
    return loaded_thermal


def demonstrate_advanced_analysis():
    """Demonstrate advanced thermal image analysis."""
    print("\n=== Advanced Analysis ===")
    
    # Create thermal DICOM
    medthermal_dicom = basic_thermal_dicom_creation()
    temp_data = medthermal_dicom.temperature_data
    
    # Calculate temperature gradient
    from medthermal_dicom.utils import MedThermalImageProcessor
    
    grad_magnitude, grad_direction = MedThermalImageProcessor.calculate_temperature_gradient(temp_data)
    
    print(f"[OK] Temperature gradient analysis:")
    print(f"  Max gradient magnitude: {grad_magnitude.max():.3f}°C/pixel")
    print(f"  Mean gradient magnitude: {grad_magnitude.mean():.3f}°C/pixel")
    
    # Apply spatial filtering
    filtered_temp = MedThermalImageProcessor.apply_spatial_filter(
        temp_data, filter_type='gaussian', filter_size=1.0
    )
    
    noise_reduction = np.std(temp_data) - np.std(filtered_temp)
    print(f"  Noise reduction from filtering: {noise_reduction:.3f}°C std")
    
    # Remove bad pixels
    cleaned_temp = MedThermalImageProcessor.remove_bad_pixels(temp_data, threshold_std=3.0)
    bad_pixels_removed = np.sum(np.abs(cleaned_temp - temp_data) > 0.01)
    print(f"  Bad pixels corrected: {bad_pixels_removed}")
    
    return grad_magnitude, filtered_temp


def main():
    """Run all demonstration examples."""
    print("MedThermal DICOM Library - Basic Usage Examples")
    print("=" * 50)
    
    try:
        # Basic creation
        medthermal_dicom = basic_thermal_dicom_creation()
        
        # Metadata handling
        metadata = demonstrate_metadata_handling()
        
        # Calibration
        calibrated_data = demonstrate_calibration()
        
        # Visualization
        viewer = demonstrate_visualization()
        
        # Temperature conversions
        demonstrate_temperature_conversion()
        
        # File operations
        loaded_thermal = demonstrate_file_operations()
        
        # Advanced analysis
        grad_magnitude, filtered_temp = demonstrate_advanced_analysis()
        
        print("\n" + "=" * 50)
        print("[OK] All examples completed successfully!")
        print("\nOutput files created in 'output/' directory:")
        print("  - thermal_sample.dcm (DICOM file)")
        print("  - thermal_visualization.html (Interactive plot)")
        print("  - temperature_histogram.html (Temperature distribution)")
        
        print("\nTo view the interactive visualizations, open the HTML files in a web browser.")
        print("To start the interactive dashboard, run:")
        print("  python -c \"from examples.basic_usage import *; viewer = demonstrate_visualization(); app = viewer.create_dashboard_app(); app.run_server(debug=True)\"")
        
    except Exception as e:
        print(f"\n[ERROR] Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()