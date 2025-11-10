#!/usr/bin/env python3
"""
Advanced Medical Thermal Imaging Example.

This example demonstrates a complete clinical workflow for medical thermal imaging:
1. Patient data management
2. Clinical thermal image acquisition simulation
3. Advanced calibration and quality control
4. Medical-grade visualization and analysis
5. Clinical reporting and DICOM export
6. Integration with medical imaging standards
"""

import sys
import os
# Add parent directory to Python path to allow importing medthermal_dicom
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date
import json
from typing import Dict, List, Tuple, Optional

from medthermal_dicom.core import MedThermalDicom
from medthermal_dicom.visualization import ThermalViewer
from medthermal_dicom.utils import TemperatureConverter, ThermalCalibrator
from medthermal_dicom.metadata import MedThermalMetadata
from medthermal_dicom.utils import ThermalImageProcessor, ThermalROIAnalyzer


class MedicalThermalWorkflow:
    """
    Complete medical thermal imaging workflow for clinical applications.
    """
    
    def __init__(self):
        """Initialize medical thermal workflow."""
        self.patients = {}
        self.studies = {}
        self.quality_control_passed = False
        self.calibration_verified = False
        
    def register_patient(self, patient_info: Dict) -> str:
        """
        Register a new patient in the system.
        
        Args:
            patient_info: Patient demographic and clinical information
            
        Returns:
            Patient ID
        """
        patient_id = patient_info.get('patient_id', f"THERM_{len(self.patients):04d}")
        
        # Validate required patient information
        required_fields = ['patient_name', 'patient_birth_date', 'patient_sex']
        for field in required_fields:
            if field not in patient_info:
                raise ValueError(f"Required patient field missing: {field}")
        
        # Store patient information
        self.patients[patient_id] = {
            'patient_id': patient_id,
            'patient_name': patient_info['patient_name'],
            'patient_birth_date': patient_info['patient_birth_date'],
            'patient_sex': patient_info['patient_sex'],
            'patient_age': patient_info.get('patient_age'),
            'medical_history': patient_info.get('medical_history', []),
            'current_medications': patient_info.get('current_medications', []),
            'allergies': patient_info.get('allergies', []),
            'registration_date': datetime.now().isoformat()
        }
        
        print(f"✓ Patient registered: {patient_id} - {patient_info['patient_name']}")
        return patient_id
    
    def create_clinical_study(self, patient_id: str, study_info: Dict) -> str:
        """
        Create a new clinical thermal imaging study.
        
        Args:
            patient_id: Patient identifier
            study_info: Study information
            
        Returns:
            Study ID
        """
        if patient_id not in self.patients:
            raise ValueError(f"Patient not found: {patient_id}")
        
        study_id = f"STU_{len(self.studies):06d}"
        
        # Create comprehensive study information
        study_data = {
            'study_id': study_id,
            'patient_id': patient_id,
            'study_date': study_info.get('study_date', datetime.now().strftime("%Y%m%d")),
            'study_time': study_info.get('study_time', datetime.now().strftime("%H%M%S")),
            'study_description': study_info.get('study_description', 'Medical Thermal Imaging'),
            'clinical_indication': study_info.get('clinical_indication', ''),
            'referring_physician': study_info.get('referring_physician', ''),
            'technologist': study_info.get('technologist', ''),
            'study_protocol': study_info.get('study_protocol', 'standard_thermal'),
            'body_parts_examined': study_info.get('body_parts_examined', []),
            'acquisition_parameters': study_info.get('acquisition_parameters', {}),
            'environmental_conditions': study_info.get('environmental_conditions', {}),
            'series': []
        }
        
        self.studies[study_id] = study_data
        print(f"✓ Clinical study created: {study_id}")
        return study_id
    
    def perform_quality_control(self) -> bool:
        """
        Perform comprehensive quality control checks.
        
        Returns:
            True if all QC checks pass
        """
        print("\n=== Quality Control Procedures ===")
        
        qc_results = {
            'uniformity_test': self._check_uniformity(),
            'temperature_accuracy': self._check_temperature_accuracy(),
            'spatial_resolution': self._check_spatial_resolution(),
            'noise_assessment': self._check_noise_levels(),
            'bad_pixel_detection': self._detect_bad_pixels()
        }
        
        # All tests must pass
        self.quality_control_passed = all(qc_results.values())
        
        print("QC Results:")
        for test, result in qc_results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test}: {status}")
        
        if self.quality_control_passed:
            print("✓ All quality control checks passed")
        else:
            print("❌ Quality control failed - system not ready for clinical use")
        
        return self.quality_control_passed
    
    def _check_uniformity(self) -> bool:
        """Check thermal uniformity using blackbody reference."""
        # Simulate uniformity check with blackbody at 37°C
        reference_temp = 37.0
        measured_temps = np.random.normal(reference_temp, 0.05, 1000)  # ±0.05°C variation
        uniformity = np.std(measured_temps)
        
        # Clinical requirement: <0.1°C standard deviation
        return uniformity < 0.1
    
    def _check_temperature_accuracy(self) -> bool:
        """Check temperature measurement accuracy."""
        # Simulate accuracy check with multiple reference temperatures
        reference_temps = [25.0, 30.0, 35.0, 40.0]
        max_error = 0
        
        for ref_temp in reference_temps:
            measured_temp = ref_temp + np.random.normal(0, 0.05)
            error = abs(measured_temp - ref_temp)
            max_error = max(max_error, error)
        
        # Clinical requirement: <0.2°C maximum error
        return max_error < 0.2
    
    def _check_spatial_resolution(self) -> bool:
        """Check spatial resolution capability."""
        # Simulate spatial resolution test
        # Clinical requirement: able to resolve 2mm features
        measured_resolution = 1.8 + np.random.normal(0, 0.1)  # mm
        return measured_resolution < 2.0
    
    def _check_noise_levels(self) -> bool:
        """Check noise equivalent temperature difference (NETD)."""
        # Simulate NETD measurement
        netd = 0.04 + np.random.normal(0, 0.01)  # °C
        
        # Clinical requirement: NETD < 0.05°C
        return netd < 0.05
    
    def _detect_bad_pixels(self) -> bool:
        """Detect bad or dead pixels."""
        # Simulate bad pixel detection
        total_pixels = 512 * 512
        bad_pixels = np.random.poisson(5)  # Average 5 bad pixels
        
        # Clinical requirement: <0.1% bad pixels
        bad_pixel_percentage = (bad_pixels / total_pixels) * 100
        return bad_pixel_percentage < 0.1
    
    def calibrate_thermal_system(self) -> bool:
        """
        Perform comprehensive thermal system calibration.
        
        Returns:
            True if calibration successful
        """
        print("\n=== Thermal System Calibration ===")
        
        # Multi-point calibration using blackbody references
        reference_temperatures = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0]
        calibration_points = []
        
        for ref_temp in reference_temperatures:
            # Simulate measured temperature with small error
            measured_temp = ref_temp + np.random.normal(0, 0.02)
            calibration_points.append((ref_temp, measured_temp))
            print(f"  Reference: {ref_temp:.1f}°C, Measured: {measured_temp:.2f}°C")
        
        # Create calibration curve
        calibrator = ThermalCalibrator()
        ref_temps = np.array([point[0] for point in calibration_points])
        measured_temps = np.array([point[1] for point in calibration_points])
        
        try:
            calib_func = calibrator.create_calibration_curve(
                ref_temps, measured_temps, interpolation_method='cubic'
            )
            
            # Validate calibration accuracy
            test_temp = 37.0
            corrected_temp = calib_func(test_temp + 0.1)  # Simulate 0.1°C error
            calibration_error = abs(corrected_temp - test_temp)
            
            self.calibration_verified = calibration_error < 0.05
            
            if self.calibration_verified:
                print(f"✓ Calibration successful - error: {calibration_error:.3f}°C")
            else:
                print(f"❌ Calibration failed - error: {calibration_error:.3f}°C")
            
        except Exception as e:
            print(f"❌ Calibration error: {e}")
            self.calibration_verified = False
        
        return self.calibration_verified
    
    def simulate_clinical_acquisition(self, study_id: str, body_part: str) -> np.ndarray:
        """
        Simulate clinical thermal image acquisition.
        
        Args:
            study_id: Study identifier
            body_part: Body part being imaged
            
        Returns:
            Simulated thermal image data
        """
        print(f"\n=== Clinical Acquisition: {body_part.upper()} ===")
        
        if study_id not in self.studies:
            raise ValueError(f"Study not found: {study_id}")
        
        # Generate realistic clinical thermal data based on body part
        if body_part.lower() == 'breast':
            thermal_data = self._simulate_breast_thermography()
        elif body_part.lower() == 'face':
            thermal_data = self._simulate_facial_thermography()
        elif body_part.lower() == 'hand':
            thermal_data = self._simulate_hand_thermography()
        else:
            thermal_data = self._simulate_generic_thermography()
        
        # Add realistic clinical noise and artifacts
        thermal_data = self._add_clinical_artifacts(thermal_data)
        
        print(f"✓ Acquired {body_part} thermal image: {thermal_data.shape}")
        print(f"  Temperature range: {thermal_data.min():.2f}°C to {thermal_data.max():.2f}°C")
        
        return thermal_data
    
    def _simulate_breast_thermography(self) -> np.ndarray:
        """Simulate breast thermography with realistic temperature patterns."""
        rows, cols = 480, 640
        
        # Create breast outline and temperature distribution
        x = np.linspace(-4, 4, cols)
        y = np.linspace(-3, 3, rows)
        X, Y = np.meshgrid(x, y)
        
        # Base skin temperature
        base_temp = 32.0
        
        # Breast tissue temperature variation
        breast_mask = (X**2 / 16 + Y**2 / 9) < 1  # Elliptical breast outline
        breast_temp = base_temp + 2.0 * breast_mask
        
        # Vascular patterns (increased temperature along blood vessels)
        vascular_pattern = (
            1.5 * np.exp(-((X - 1)**2 + (Y - 0.5)**2) / 0.5) +
            1.2 * np.exp(-((X + 1)**2 + (Y + 0.5)**2) / 0.3) +
            0.8 * np.exp(-(X**2 + (Y - 1)**2) / 0.8)
        )
        
        # Nipple area (slightly higher temperature)
        nipple_temp = 1.0 * np.exp(-(X**2 + Y**2) / 0.1)
        
        # Combine temperature components
        thermal_data = breast_temp + vascular_pattern * breast_mask + nipple_temp * breast_mask
        
        # Add temperature gradient from core to periphery
        distance_from_center = np.sqrt(X**2 + Y**2)
        thermal_gradient = -0.5 * distance_from_center * breast_mask
        thermal_data += thermal_gradient
        
        return thermal_data
    
    def _simulate_facial_thermography(self) -> np.ndarray:
        """Simulate facial thermography with anatomical temperature patterns."""
        rows, cols = 480, 640
        
        # Base facial temperature
        base_temp = 33.0
        thermal_data = np.full((rows, cols), base_temp)
        
        # Forehead (higher temperature)
        forehead_y = slice(50, 150)
        forehead_x = slice(200, 440)
        thermal_data[forehead_y, forehead_x] += 1.5
        
        # Eye regions (higher temperature due to blood flow)
        eye1_y, eye1_x = slice(150, 200), slice(180, 280)
        eye2_y, eye2_x = slice(150, 200), slice(360, 460)
        thermal_data[eye1_y, eye1_x] += 1.0
        thermal_data[eye2_y, eye2_x] += 1.0
        
        # Nose (lower temperature due to air flow)
        nose_y, nose_x = slice(200, 300), slice(300, 340)
        thermal_data[nose_y, nose_x] -= 0.5
        
        # Mouth area
        mouth_y, mouth_x = slice(320, 380), slice(280, 360)
        thermal_data[mouth_y, mouth_x] += 0.8
        
        return thermal_data
    
    def _simulate_hand_thermography(self) -> np.ndarray:
        """Simulate hand thermography with finger temperature patterns."""
        rows, cols = 480, 640
        
        # Base hand temperature
        base_temp = 30.0
        thermal_data = np.full((rows, cols), base_temp)
        
        # Palm (higher temperature)
        palm_y, palm_x = slice(200, 400), slice(200, 440)
        thermal_data[palm_y, palm_x] += 3.0
        
        # Fingers (temperature gradient from palm to tips)
        for i, finger_x in enumerate([150, 220, 290, 360, 430]):
            finger_width = 40
            for y in range(50, 200):
                temp_decrease = (200 - y) / 150 * 2.0  # Cooler at fingertips
                x_start = finger_x - finger_width // 2
                x_end = finger_x + finger_width // 2
                thermal_data[y, x_start:x_end] = base_temp + 2.0 - temp_decrease
        
        return thermal_data
    
    def _simulate_generic_thermography(self) -> np.ndarray:
        """Simulate generic thermal pattern."""
        rows, cols = 480, 640
        base_temp = 32.0
        
        x = np.linspace(-3, 3, cols)
        y = np.linspace(-3, 3, rows)
        X, Y = np.meshgrid(x, y)
        
        thermal_data = base_temp + 3.0 * np.exp(-(X**2 + Y**2) / 2)
        
        return thermal_data
    
    def _add_clinical_artifacts(self, thermal_data: np.ndarray) -> np.ndarray:
        """Add realistic clinical artifacts and noise."""
        # Add thermal noise
        noise = np.random.normal(0, 0.1, thermal_data.shape)
        thermal_data += noise
        
        # Add motion artifacts (slight blur)
        from scipy.ndimage import gaussian_filter
        motion_blur = gaussian_filter(thermal_data, sigma=0.5)
        thermal_data = 0.95 * thermal_data + 0.05 * motion_blur
        
        # Add environmental reflections (random warm spots)
        num_reflections = np.random.poisson(3)
        for _ in range(num_reflections):
            y = np.random.randint(0, thermal_data.shape[0])
            x = np.random.randint(0, thermal_data.shape[1])
            size = np.random.randint(10, 30)
            intensity = np.random.uniform(0.5, 2.0)
            
            y_slice = slice(max(0, y-size), min(thermal_data.shape[0], y+size))
            x_slice = slice(max(0, x-size), min(thermal_data.shape[1], x+size))
            thermal_data[y_slice, x_slice] += intensity
        
        return thermal_data
    
    def create_clinical_thermal_dicom(self, study_id: str, thermal_data: np.ndarray, 
                                    body_part: str, series_number: int = 1) -> MedThermalDicom:
        """
        Create clinical-grade thermal DICOM with comprehensive metadata.
        
        Args:
            study_id: Study identifier
            thermal_data: Thermal image data
            body_part: Body part imaged
            series_number: Series number
            
        Returns:
            Clinical thermal DICOM instance
        """
        study = self.studies[study_id]
        patient = self.patients[study['patient_id']]
        
        # Create thermal DICOM
        thermal_dicom = MedThermalDicom()
        
        # Set thermal image data
        temp_range = (thermal_data.min(), thermal_data.max())
        thermal_dicom.set_thermal_image(thermal_data, thermal_data, temp_range)
        
        # Create comprehensive metadata
        metadata = MedThermalMetadata()
        
        # Patient information
        metadata.set_patient_information(
            patient_name=patient['patient_name'],
            patient_id=patient['patient_id'],
            patient_birth_date=patient['patient_birth_date'],
            patient_sex=patient['patient_sex'],
            patient_age=patient.get('patient_age')
        )
        
        # Study information
        procedure_code = None
        if 'breast' in body_part.lower():
            procedure_code = 'breast_thermography'
        elif 'vascular' in study['study_description'].lower():
            procedure_code = 'vascular_thermography'
        else:
            procedure_code = 'diagnostic_thermography'
        
        metadata.set_study_information(
            study_description=study['study_description'],
            study_id=study['study_id'],
            referring_physician=study.get('referring_physician'),
            study_date=study['study_date'],
            study_time=study['study_time'],
            procedure_code=procedure_code
        )
        
        # Series information
        metadata.set_series_information(
            series_description=f"Thermal Images - {body_part.title()}",
            series_number=str(series_number),
            body_part=body_part.lower() if body_part.lower() in metadata.ANATOMICAL_REGIONS else None
        )
        
        # Equipment information
        metadata.set_equipment_information(
            manufacturer="FLIR Systems",
            manufacturer_model="T1K",
            device_serial_number="TH001234",
            software_version="ThermalDICOM v1.0",
            detector_type="Uncooled Microbolometer",
            spatial_resolution=(0.1, 0.1)
        )
        
        # Acquisition parameters
        metadata.set_acquisition_parameters(
            exposure_time=0.033,  # 30 fps
            frame_rate=30.0,
            integration_time=0.033
        )
        
        # Thermal calibration info
        metadata.set_thermal_calibration_info(
            calibration_method="Multi-point Blackbody Calibration",
            reference_temperature=37.0,
            calibration_uncertainty=0.05,
            blackbody_temperature=37.0
        )
        
        # Quality control info
        metadata.set_quality_control_info(
            uniformity_check=True,
            noise_equivalent_temperature=0.04,
            bad_pixel_count=0,
            spatial_resolution_test=True,
            temperature_accuracy=0.05
        )
        
        # Apply metadata to DICOM
        metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
        
        # Set clinical thermal parameters
        clinical_thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0,
            'reflected_temperature': 22.0,
            'relative_humidity': 45.0,
            'atmospheric_temperature': 22.0,
            'camera_model': 'FLIR T1K',
            'camera_serial': 'TH001234',
            'lens_model': 'Standard 24° Lens',
            'spectral_range': '7.5-14.0 μm',
            'thermal_sensitivity': 0.04,
            'acquisition_mode': 'Medical Thermal Imaging',
            'measurement_conditions': {
                'room_temperature': 22.0,
                'humidity': 45.0,
                'air_flow': 'minimal',
                'patient_acclimatization_time': 15  # minutes
            }
        }
        
        thermal_dicom.set_thermal_parameters(clinical_thermal_params)
        
        return thermal_dicom
    
    def perform_clinical_analysis(self, thermal_dicom: MedThermalDicom, body_part: str) -> Dict:
        """
        Perform comprehensive clinical thermal analysis.
        
        Args:
            thermal_dicom: Thermal DICOM to analyze
            body_part: Body part being analyzed
            
        Returns:
            Clinical analysis results
        """
        print(f"\n=== Clinical Analysis: {body_part.upper()} ===")
        
        temp_data = thermal_dicom.temperature_data
        analysis_results = {
            'body_part': body_part,
            'analysis_date': datetime.now().isoformat(),
            'overall_statistics': {},
            'roi_analysis': [],
            'temperature_asymmetry': {},
            'thermal_patterns': {},
            'clinical_findings': []
        }
        
        # Overall temperature statistics
        analysis_results['overall_statistics'] = {
            'mean_temperature': float(np.mean(temp_data)),
            'median_temperature': float(np.median(temp_data)),
            'std_temperature': float(np.std(temp_data)),
            'min_temperature': float(np.min(temp_data)),
            'max_temperature': float(np.max(temp_data)),
            'temperature_range': float(np.max(temp_data) - np.min(temp_data))
        }
        
        # ROI analysis based on body part
        roi_analyzer = ThermalROIAnalyzer()
        
        if body_part.lower() == 'breast':
            analysis_results['roi_analysis'] = self._analyze_breast_rois(temp_data, roi_analyzer)
        elif body_part.lower() == 'face':
            analysis_results['roi_analysis'] = self._analyze_facial_rois(temp_data, roi_analyzer)
        elif body_part.lower() == 'hand':
            analysis_results['roi_analysis'] = self._analyze_hand_rois(temp_data, roi_analyzer)
        
        # Temperature asymmetry analysis
        analysis_results['temperature_asymmetry'] = self._analyze_temperature_asymmetry(temp_data)
        
        # Thermal pattern analysis
        analysis_results['thermal_patterns'] = self._analyze_thermal_patterns(temp_data)
        
        # Generate clinical findings
        analysis_results['clinical_findings'] = self._generate_clinical_findings(analysis_results)
        
        # Print summary
        stats = analysis_results['overall_statistics']
        print(f"✓ Clinical Analysis Complete:")
        print(f"  Mean temperature: {stats['mean_temperature']:.2f}°C")
        print(f"  Temperature range: {stats['temperature_range']:.2f}°C")
        print(f"  ROI analyses: {len(analysis_results['roi_analysis'])}")
        print(f"  Clinical findings: {len(analysis_results['clinical_findings'])}")
        
        return analysis_results
    
    def _analyze_breast_rois(self, temp_data: np.ndarray, roi_analyzer: ThermalROIAnalyzer) -> List[Dict]:
        """Analyze breast-specific regions of interest."""
        rois = []
        
        # Central breast region
        central_roi = roi_analyzer.create_circular_roi(
            center=(temp_data.shape[0]//2, temp_data.shape[1]//2),
            radius=80,
            image_shape=temp_data.shape
        )
        central_stats = roi_analyzer.analyze_roi_statistics(temp_data, central_roi)
        central_stats['roi_name'] = 'Central Breast'
        central_stats['clinical_significance'] = 'Core breast tissue temperature'
        rois.append(central_stats)
        
        # Upper outer quadrant
        upper_outer_roi = roi_analyzer.create_circular_roi(
            center=(temp_data.shape[0]//3, 2*temp_data.shape[1]//3),
            radius=50,
            image_shape=temp_data.shape
        )
        upper_outer_stats = roi_analyzer.analyze_roi_statistics(temp_data, upper_outer_roi)
        upper_outer_stats['roi_name'] = 'Upper Outer Quadrant'
        upper_outer_stats['clinical_significance'] = 'Common location for pathology'
        rois.append(upper_outer_stats)
        
        return rois
    
    def _analyze_facial_rois(self, temp_data: np.ndarray, roi_analyzer: ThermalROIAnalyzer) -> List[Dict]:
        """Analyze facial regions of interest."""
        rois = []
        
        # Forehead region
        forehead_roi = roi_analyzer.create_rectangular_roi(
            top_left=(50, 200),
            bottom_right=(150, 440),
            image_shape=temp_data.shape
        )
        forehead_stats = roi_analyzer.analyze_roi_statistics(temp_data, forehead_roi)
        forehead_stats['roi_name'] = 'Forehead'
        forehead_stats['clinical_significance'] = 'Vascular perfusion indicator'
        rois.append(forehead_stats)
        
        return rois
    
    def _analyze_hand_rois(self, temp_data: np.ndarray, roi_analyzer: ThermalROIAnalyzer) -> List[Dict]:
        """Analyze hand regions of interest."""
        rois = []
        
        # Palm region
        palm_roi = roi_analyzer.create_rectangular_roi(
            top_left=(200, 200),
            bottom_right=(400, 440),
            image_shape=temp_data.shape
        )
        palm_stats = roi_analyzer.analyze_roi_statistics(temp_data, palm_roi)
        palm_stats['roi_name'] = 'Palm'
        palm_stats['clinical_significance'] = 'Circulation assessment'
        rois.append(palm_stats)
        
        return rois
    
    def _analyze_temperature_asymmetry(self, temp_data: np.ndarray) -> Dict:
        """Analyze temperature asymmetry between left and right sides."""
        height, width = temp_data.shape
        left_side = temp_data[:, :width//2]
        right_side = temp_data[:, width//2:]
        
        # Ensure equal sizes for comparison
        min_width = min(left_side.shape[1], right_side.shape[1])
        left_side = left_side[:, :min_width]
        right_side = right_side[:, -min_width:]
        
        left_mean = np.mean(left_side)
        right_mean = np.mean(right_side)
        asymmetry = abs(left_mean - right_mean)
        
        return {
            'left_mean_temperature': float(left_mean),
            'right_mean_temperature': float(right_mean),
            'temperature_asymmetry': float(asymmetry),
            'asymmetry_significance': 'significant' if asymmetry > 0.5 else 'normal'
        }
    
    def _analyze_thermal_patterns(self, temp_data: np.ndarray) -> Dict:
        """Analyze thermal patterns and gradients."""
        # Calculate temperature gradients
        grad_y, grad_x = np.gradient(temp_data)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Find hot spots (temperatures > 95th percentile)
        hot_threshold = np.percentile(temp_data, 95)
        hot_spots = temp_data > hot_threshold
        num_hot_spots = np.sum(hot_spots)
        
        # Find cold spots (temperatures < 5th percentile)
        cold_threshold = np.percentile(temp_data, 5)
        cold_spots = temp_data < cold_threshold
        num_cold_spots = np.sum(cold_spots)
        
        return {
            'max_gradient': float(np.max(gradient_magnitude)),
            'mean_gradient': float(np.mean(gradient_magnitude)),
            'hot_spot_threshold': float(hot_threshold),
            'num_hot_spots': int(num_hot_spots),
            'cold_spot_threshold': float(cold_threshold),
            'num_cold_spots': int(num_cold_spots),
            'temperature_uniformity': float(1.0 / (1.0 + np.std(temp_data)))
        }
    
    def _generate_clinical_findings(self, analysis_results: Dict) -> List[Dict]:
        """Generate clinical findings based on analysis results."""
        findings = []
        
        # Temperature range assessment
        temp_range = analysis_results['overall_statistics']['temperature_range']
        if temp_range > 8.0:
            findings.append({
                'finding': 'Increased temperature variation',
                'value': temp_range,
                'unit': '°C',
                'significance': 'May indicate vascular or inflammatory changes',
                'recommendation': 'Consider clinical correlation'
            })
        
        # Asymmetry assessment
        asymmetry = analysis_results['temperature_asymmetry']['temperature_asymmetry']
        if asymmetry > 0.7:
            findings.append({
                'finding': 'Significant temperature asymmetry',
                'value': asymmetry,
                'unit': '°C',
                'significance': 'Possible unilateral pathology',
                'recommendation': 'Clinical evaluation recommended'
            })
        
        # Hot spot assessment
        num_hot_spots = analysis_results['thermal_patterns']['num_hot_spots']
        if num_hot_spots > 100:  # Arbitrary threshold for demonstration
            findings.append({
                'finding': 'Multiple thermal hot spots detected',
                'value': num_hot_spots,
                'unit': 'pixels',
                'significance': 'Possible increased metabolic activity',
                'recommendation': 'Monitor for changes over time'
            })
        
        return findings
    
    def generate_clinical_report(self, analysis_results: Dict, output_path: str):
        """Generate comprehensive clinical report."""
        report = {
            'report_header': {
                'report_type': 'Medical Thermal Imaging Report',
                'generation_date': datetime.now().isoformat(),
                'software_version': 'ThermalDICOM v1.0',
                'report_id': f"THERM_RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            },
            'analysis_results': analysis_results,
            'clinical_interpretation': {
                'summary': self._generate_clinical_summary(analysis_results),
                'recommendations': self._generate_recommendations(analysis_results)
            }
        }
        
        # Save JSON report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✓ Clinical report generated: {output_path}")
        return report
    
    def _generate_clinical_summary(self, analysis_results: Dict) -> str:
        """Generate clinical summary text."""
        body_part = analysis_results['body_part']
        stats = analysis_results['overall_statistics']
        findings = analysis_results['clinical_findings']
        
        summary = f"Thermal imaging of {body_part} shows mean temperature of {stats['mean_temperature']:.2f}°C "
        summary += f"with temperature range of {stats['temperature_range']:.2f}°C. "
        
        if len(findings) == 0:
            summary += "No significant thermal abnormalities detected."
        else:
            summary += f"{len(findings)} significant finding(s) identified requiring clinical correlation."
        
        return summary
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate clinical recommendations."""
        recommendations = []
        findings = analysis_results['clinical_findings']
        
        if len(findings) == 0:
            recommendations.append("Continue routine monitoring as clinically indicated.")
        else:
            recommendations.append("Clinical correlation recommended for identified thermal findings.")
            recommendations.append("Consider follow-up thermal imaging in 3-6 months.")
            
            for finding in findings:
                if finding.get('recommendation'):
                    recommendations.append(finding['recommendation'])
        
        return recommendations


def main():
    """Demonstrate complete medical thermal imaging workflow."""
    print("Medical Thermal Imaging Workflow - Clinical Example")
    print("=" * 60)
    
    # Initialize workflow
    workflow = MedicalThermalWorkflow()
    
    try:
        # Step 1: System Quality Control and Calibration
        print("\n🔧 SYSTEM PREPARATION")
        qc_passed = workflow.perform_quality_control()
        if not qc_passed:
            print("❌ System not ready for clinical use")
            return
        
        calibration_ok = workflow.calibrate_thermal_system()
        if not calibration_ok:
            print("❌ System calibration failed")
            return
        
        # Step 2: Patient Registration
        print("\n👤 PATIENT REGISTRATION")
        patient_info = {
            'patient_name': 'DOE^JANE^MEDICAL',
            'patient_id': 'THERM_001',
            'patient_birth_date': '19750815',
            'patient_sex': 'F',
            'patient_age': '048Y',
            'medical_history': ['Breast cancer screening'],
            'current_medications': [],
            'allergies': ['None known']
        }
        patient_id = workflow.register_patient(patient_info)
        
        # Step 3: Create Clinical Study
        print("\n📋 STUDY CREATION")
        study_info = {
            'study_description': 'Breast Thermal Screening Study',
            'clinical_indication': 'Routine breast cancer screening',
            'referring_physician': 'DR^SMITH^ROBERT',
            'technologist': 'TECH^JONES^MARY',
            'body_parts_examined': ['breast'],
            'environmental_conditions': {
                'room_temperature': 22.0,
                'humidity': 45.0,
                'air_circulation': 'minimal'
            }
        }
        study_id = workflow.create_clinical_study(patient_id, study_info)
        
        # Step 4: Clinical Image Acquisition
        print("\n📸 IMAGE ACQUISITION")
        thermal_data = workflow.simulate_clinical_acquisition(study_id, 'breast')
        
        # Step 5: Create Clinical DICOM
        print("\n💾 DICOM CREATION")
        thermal_dicom = workflow.create_clinical_thermal_dicom(
            study_id, thermal_data, 'breast'
        )
        
        # Step 6: Clinical Analysis
        print("\n🔬 CLINICAL ANALYSIS")
        analysis_results = workflow.perform_clinical_analysis(thermal_dicom, 'breast')
        
        # Step 7: Visualization
        print("\n📊 VISUALIZATION")
        viewer = ThermalViewer(thermal_dicom)
        
        # Create clinical visualization
        fig = viewer.create_interactive_plot(
            width=1000, height=800,
            title=f"Clinical Thermal Imaging - {patient_info['patient_name']}"
        )
        
        # Add ROI overlays based on analysis
        for roi_data in analysis_results['roi_analysis']:
            if roi_data['roi_name'] == 'Central Breast':
                roi_mask = ThermalROIAnalyzer.create_circular_roi(
                    center=(thermal_data.shape[0]//2, thermal_data.shape[1]//2),
                    radius=80,
                    image_shape=thermal_data.shape
                )
                viewer.add_roi_overlay(roi_mask, "Central Breast", "yellow", 2)
        
        # Step 8: Save Results
        print("\n💾 SAVING RESULTS")
        os.makedirs('clinical_output', exist_ok=True)
        
        # Save DICOM
        thermal_dicom.save_dicom('clinical_output/clinical_thermal.dcm')
        
        # Save visualization
        viewer.save_visualization('clinical_output/clinical_visualization.html', format='html')
        
        # Generate clinical report
        workflow.generate_clinical_report(
            analysis_results, 
            'clinical_output/clinical_report.json'
        )
        
        # Export temperature data
        viewer.export_temperature_data('clinical_output/temperature_data.csv')
        
        print("\n" + "=" * 60)
        print("✅ CLINICAL WORKFLOW COMPLETED SUCCESSFULLY!")
        print("\nGenerated files in 'clinical_output/' directory:")
        print("  📄 clinical_thermal.dcm - Clinical DICOM file")
        print("  🌐 clinical_visualization.html - Interactive visualization")
        print("  📊 clinical_report.json - Comprehensive clinical report")
        print("  📈 temperature_data.csv - Raw temperature data")
        
        # Print clinical summary
        print(f"\n📋 CLINICAL SUMMARY:")
        print(f"Patient: {patient_info['patient_name']} (ID: {patient_id})")
        print(f"Study: {study_info['study_description']}")
        print(f"Findings: {len(analysis_results['clinical_findings'])} significant finding(s)")
        
        for finding in analysis_results['clinical_findings']:
            print(f"  • {finding['finding']}: {finding['value']:.2f} {finding['unit']}")
        
        print(f"\n🎯 NEXT STEPS:")
        recommendations = workflow._generate_recommendations(analysis_results)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
    except Exception as e:
        print(f"\n❌ Error in clinical workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()