"""
Utility classes and functions for thermal DICOM processing.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, Union
from scipy import interpolate
import warnings
import time
import random
from typing import Tuple
from pydicom.uid import generate_uid
import time
import random
from pydicom.uid import generate_uid


class TemperatureConverter:
    """
    Utility class for temperature unit conversions and scaling.
    """
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert Celsius to Fahrenheit."""
        return celsius * 9.0 / 5.0 + 32.0
    
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert Fahrenheit to Celsius."""
        return (fahrenheit - 32.0) * 5.0 / 9.0
    
    @staticmethod
    def celsius_to_kelvin(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert Celsius to Kelvin."""
        return celsius + 273.15
    
    @staticmethod
    def kelvin_to_celsius(kelvin: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Convert Kelvin to Celsius."""
        return kelvin - 273.15
    
    @staticmethod
    def normalize_temperature_range(temperature_data: np.ndarray, 
                                  target_range: Tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
        """
        Normalize temperature data to a target range.
        
        Args:
            temperature_data: Input temperature array
            target_range: Target range (min, max)
            
        Returns:
            Normalized temperature array
        """
        min_temp, max_temp = np.min(temperature_data), np.max(temperature_data)
        if max_temp == min_temp:
            return np.full_like(temperature_data, target_range[0])
        
        normalized = (temperature_data - min_temp) / (max_temp - min_temp)
        return normalized * (target_range[1] - target_range[0]) + target_range[0]


class ThermalCalibrator:
    """
    Advanced thermal calibration utilities for accurate temperature measurement.
    """
    
    def __init__(self):
        self.calibration_data = {}
        self.atmospheric_correction = True
        self.emissivity_correction = True
    
    def set_calibration_parameters(self, 
                                 emissivity: float = 0.98,
                                 distance: float = 1.0,
                                 ambient_temp: float = 22.0,
                                 reflected_temp: Optional[float] = None,
                                 relative_humidity: float = 50.0,
                                 atmospheric_temp: Optional[float] = None):
        """
        Set calibration parameters for accurate temperature measurement.
        
        Args:
            emissivity: Object emissivity (0.0 to 1.0)
            distance: Distance from camera in meters
            ambient_temp: Ambient temperature in Celsius
            reflected_temp: Reflected temperature in Celsius (defaults to ambient)
            relative_humidity: Relative humidity percentage
            atmospheric_temp: Atmospheric temperature in Celsius (defaults to ambient)
        """
        self.calibration_data = {
            'emissivity': emissivity,
            'distance': distance,
            'ambient_temperature': ambient_temp,
            'reflected_temperature': reflected_temp or ambient_temp,
            'relative_humidity': relative_humidity,
            'atmospheric_temperature': atmospheric_temp or ambient_temp
        }
    
    def apply_emissivity_correction(self, raw_temperature: np.ndarray, 
                                  emissivity: Optional[float] = None) -> np.ndarray:
        """
        Apply emissivity correction to raw temperature data.
        
        Args:
            raw_temperature: Raw temperature data in Celsius
            emissivity: Object emissivity (uses calibration value if None)
            
        Returns:
            Emissivity-corrected temperature data
        """
        if emissivity is None:
            emissivity = self.calibration_data.get('emissivity', 0.98)
        
        if emissivity <= 0 or emissivity > 1:
            warnings.warn(f"Invalid emissivity value: {emissivity}. Using 0.98.")
            emissivity = 0.98
        
        # Convert to Kelvin for calculations
        raw_kelvin = TemperatureConverter.celsius_to_kelvin(raw_temperature)
        ambient_kelvin = TemperatureConverter.celsius_to_kelvin(
            self.calibration_data.get('ambient_temperature', 22.0)
        )
        
        # Simplified emissivity correction model
        # Real implementation would use Planck's law and camera-specific calibration
        corrected_kelvin = (raw_kelvin - (1 - emissivity) * ambient_kelvin) / emissivity
        
        return TemperatureConverter.kelvin_to_celsius(corrected_kelvin)
    
    def apply_atmospheric_correction(self, temperature_data: np.ndarray,
                                   distance: Optional[float] = None) -> np.ndarray:
        """
        Apply atmospheric attenuation correction.
        
        Args:
            temperature_data: Temperature data in Celsius
            distance: Distance from camera in meters
            
        Returns:
            Atmospherically corrected temperature data
        """
        if distance is None:
            distance = self.calibration_data.get('distance', 1.0)
        
        # Simplified atmospheric correction
        # Real implementation would use atmospheric transmission models
        humidity = self.calibration_data.get('relative_humidity', 50.0)
        atm_temp = self.calibration_data.get('atmospheric_temperature', 22.0)
        
        # Atmospheric transmission coefficient (simplified model)
        transmission = np.exp(-0.01 * distance * (humidity / 100.0))
        
        # Apply correction
        corrected_temp = (temperature_data - (1 - transmission) * atm_temp) / transmission
        
        return corrected_temp
    
    def calibrate_temperature_data(self, raw_temperature: np.ndarray) -> np.ndarray:
        """
        Apply full calibration pipeline to raw temperature data.
        
        Args:
            raw_temperature: Raw temperature data in Celsius
            
        Returns:
            Fully calibrated temperature data
        """
        calibrated = raw_temperature.copy()
        
        if self.emissivity_correction:
            calibrated = self.apply_emissivity_correction(calibrated)
        
        if self.atmospheric_correction:
            calibrated = self.apply_atmospheric_correction(calibrated)
        
        return calibrated
    
    def create_calibration_curve(self, 
                               reference_temps: np.ndarray,
                               measured_temps: np.ndarray,
                               interpolation_method: str = 'cubic') -> callable:
        """
        Create calibration curve from reference and measured temperatures.
        
        Args:
            reference_temps: Reference temperature values
            measured_temps: Measured temperature values
            interpolation_method: Interpolation method ('linear', 'cubic', etc.)
            
        Returns:
            Calibration function
        """
        if len(reference_temps) != len(measured_temps):
            raise ValueError("Reference and measured temperature arrays must have same length")
        
        if len(reference_temps) < 2:
            raise ValueError("At least 2 calibration points required")
        
        # Create interpolation function
        if interpolation_method == 'linear':
            calib_func = interpolate.interp1d(measured_temps, reference_temps, 
                                            kind='linear', fill_value='extrapolate')
        elif interpolation_method == 'cubic':
            if len(reference_temps) >= 4:
                calib_func = interpolate.interp1d(measured_temps, reference_temps,
                                                kind='cubic', fill_value='extrapolate')
            else:
                calib_func = interpolate.interp1d(measured_temps, reference_temps,
                                                kind='linear', fill_value='extrapolate')
        else:
            calib_func = interpolate.interp1d(measured_temps, reference_temps,
                                            kind=interpolation_method, fill_value='extrapolate')
        
        return calib_func
    
    def apply_calibration_curve(self, temperature_data: np.ndarray,
                              calibration_func: callable) -> np.ndarray:
        """
        Apply calibration curve to temperature data.
        
        Args:
            temperature_data: Input temperature data
            calibration_func: Calibration function
            
        Returns:
            Calibrated temperature data
        """
        return calibration_func(temperature_data)


class ThermalImageProcessor:
    """
    Image processing utilities specific to thermal images.
    """
    
    @staticmethod
    def remove_bad_pixels(temperature_data: np.ndarray,
                         threshold_std: float = 3.0) -> np.ndarray:
        """
        Remove bad pixels using statistical outlier detection.
        
        Args:
            temperature_data: Input temperature array
            threshold_std: Standard deviation threshold for outlier detection
            
        Returns:
            Temperature data with bad pixels interpolated
        """
        mean_temp = np.mean(temperature_data)
        std_temp = np.std(temperature_data)
        
        # Identify bad pixels
        bad_pixel_mask = np.abs(temperature_data - mean_temp) > threshold_std * std_temp
        
        # Interpolate bad pixels
        corrected_data = temperature_data.copy()
        
        # Simple nearest neighbor interpolation for bad pixels
        from scipy.ndimage import generic_filter
        
        def replace_outliers(window):
            center = window[len(window)//2]
            if np.abs(center - mean_temp) > threshold_std * std_temp:
                # Return median of surrounding pixels
                surrounding = np.concatenate([window[:len(window)//2], window[len(window)//2+1:]])
                valid_surrounding = surrounding[np.abs(surrounding - mean_temp) <= threshold_std * std_temp]
                if len(valid_surrounding) > 0:
                    return np.median(valid_surrounding)
            return center
        
        corrected_data = generic_filter(corrected_data, replace_outliers, size=3, mode='reflect')
        
        return corrected_data
    
    @staticmethod
    def apply_spatial_filter(temperature_data: np.ndarray,
                           filter_type: str = 'gaussian',
                           filter_size: float = 1.0) -> np.ndarray:
        """
        Apply spatial filtering to temperature data.
        
        Args:
            temperature_data: Input temperature array
            filter_type: Type of filter ('gaussian', 'median', 'bilateral')
            filter_size: Filter size parameter
            
        Returns:
            Filtered temperature data
        """
        from scipy.ndimage import gaussian_filter, median_filter
        
        if filter_type == 'gaussian':
            return gaussian_filter(temperature_data, sigma=filter_size)
        elif filter_type == 'median':
            kernel_size = max(3, int(filter_size * 2 + 1))
            if kernel_size % 2 == 0:
                kernel_size += 1
            return median_filter(temperature_data, size=kernel_size)
        elif filter_type == 'bilateral':
            # Simplified bilateral filter implementation
            from scipy.ndimage import gaussian_filter
            # This is a simplified version - real bilateral filter would preserve edges better
            return gaussian_filter(temperature_data, sigma=filter_size)
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
    
    @staticmethod
    def calculate_temperature_gradient(temperature_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate temperature gradient magnitude and direction.
        
        Args:
            temperature_data: Input temperature array
            
        Returns:
            Tuple of (gradient_magnitude, gradient_direction)
        """
        grad_y, grad_x = np.gradient(temperature_data)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_direction = np.arctan2(grad_y, grad_x)
        
        return gradient_magnitude, gradient_direction


class ThermalROIAnalyzer:
    """
    Region of Interest analysis tools for thermal images.
    """
    
    @staticmethod
    def create_circular_roi(center: Tuple[int, int], radius: int, 
                          image_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create circular ROI mask.
        
        Args:
            center: Center coordinates (row, col)
            radius: Radius in pixels
            image_shape: Shape of the image (rows, cols)
            
        Returns:
            Boolean ROI mask
        """
        rows, cols = image_shape
        row_center, col_center = center
        
        y, x = np.ogrid[:rows, :cols]
        mask = (x - col_center)**2 + (y - row_center)**2 <= radius**2
        
        return mask
    
    @staticmethod
    def create_rectangular_roi(top_left: Tuple[int, int], 
                             bottom_right: Tuple[int, int],
                             image_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create rectangular ROI mask.
        
        Args:
            top_left: Top-left coordinates (row, col)
            bottom_right: Bottom-right coordinates (row, col)
            image_shape: Shape of the image (rows, cols)
            
        Returns:
            Boolean ROI mask
        """
        mask = np.zeros(image_shape, dtype=bool)
        r1, c1 = top_left
        r2, c2 = bottom_right
        
        mask[r1:r2+1, c1:c2+1] = True
        
        return mask
    
    @staticmethod
    def analyze_roi_statistics(temperature_data: np.ndarray, 
                             roi_mask: np.ndarray) -> Dict[str, float]:
        """
        Analyze temperature statistics within ROI.
        
        Args:
            temperature_data: Temperature array
            roi_mask: Boolean ROI mask
            
        Returns:
            Dictionary with statistical measures
        """
        roi_temps = temperature_data[roi_mask]
        
        if len(roi_temps) == 0:
            return {}
        
        stats = {
            'mean': float(np.mean(roi_temps)),
            'median': float(np.median(roi_temps)),
            'std': float(np.std(roi_temps)),
            'min': float(np.min(roi_temps)),
            'max': float(np.max(roi_temps)),
            'range': float(np.max(roi_temps) - np.min(roi_temps)),
            'percentile_25': float(np.percentile(roi_temps, 25)),
            'percentile_75': float(np.percentile(roi_temps, 75)),
            'pixel_count': int(np.sum(roi_mask)),
            'area_pixels': int(np.sum(roi_mask))
        }
        
        return stats


# ------------------------------------------------------------
# Organization UID utilities (DICOM-compliant numeric UIDs)
# ------------------------------------------------------------

def generate_organization_uid(org_prefix: Optional[str] = None,
                              uid_type: str = "instance") -> str:
    """
    Generate organization-specific UID or fall back to standard generate_uid().
    Follows DICOM rules: only digits and dots, max length 64.
    """
    if org_prefix is None:
        return generate_uid()

    if not _is_valid_uid_prefix(org_prefix):
        raise ValueError(
            f"Invalid organization UID prefix: {org_prefix}. "
            "UID must contain only numbers and dots, with no consecutive dots."
        )

    timestamp = int(time.time() * 1000000)  # microseconds since epoch
    random_component = random.randint(100000000, 999999999)  # 9-digit numeric
    type_component = _get_uid_type_component(uid_type)

    uid = f"{org_prefix}.{type_component}.{timestamp}.{random_component}"

    if len(uid) > 64:
        # Trim timestamp if needed to satisfy length constraint
        max_timestamp_length = 64 - len(f"{org_prefix}.{type_component}..{random_component}") - 1
        if max_timestamp_length > 0:
            timestamp = int(str(timestamp)[:max_timestamp_length])
            uid = f"{org_prefix}.{type_component}.{timestamp}.{random_component}"
        else:
            return generate_uid()

    return uid


def _is_valid_uid_prefix(uid_prefix: str) -> bool:
    if not uid_prefix or not isinstance(uid_prefix, str):
        return False
    if not uid_prefix.replace('.', '').isdigit():
        return False
    if '..' in uid_prefix:
        return False
    if uid_prefix.startswith('.') or uid_prefix.endswith('.'): 
        return False
    for component in uid_prefix.split('.'): 
        if not component or int(component) < 0:
            return False
    return True


def _get_uid_type_component(uid_type: str) -> str:
    mapping = {
        "instance": "1",
        "series": "2",
        "study": "3",
        "implementation": "4",
    }
    return mapping.get(uid_type.lower(), "1")


def get_common_organization_uids() -> Dict[str, str]:
    return {
        "example_medical_center": "1.2.826.0.1.3680043.8.498",
        "example_hospital": "1.2.826.0.1.3680043.8.499",
        "example_clinic": "1.2.826.0.1.3680043.8.500",
        "example_research_institute": "1.2.826.0.1.3680043.8.501",
        "example_university": "1.2.826.0.1.3680043.8.502",
        "example_manufacturer": "1.2.826.0.1.3680043.8.503",
    }


def validate_organization_uid(uid: str) -> Tuple[bool, str]:
    if not uid or not isinstance(uid, str):
        return False, "UID must be a non-empty string"
    if len(uid) > 64:
        return False, f"UID length {len(uid)} exceeds DICOM limit of 64 characters"
    if not uid.replace('.', '').isdigit():
        return False, "UID must contain only numbers and dots"
    if '..' in uid:
        return False, "UID cannot contain consecutive dots"
    if uid.startswith('.') or uid.endswith('.'): 
        return False, "UID cannot start or end with a dot"
    for i, component in enumerate(uid.split('.')):
        if not component:
            return False, f"Empty component at position {i}"
        try:
            if int(component) < 0:
                return False, f"Negative component at position {i}: {component}"
        except ValueError:
            return False, f"Invalid numeric component at position {i}: {component}"
    return True, "UID is valid"


# ------------------------------------------------------------
# Organization UID utilities (DICOM-compliant numeric UIDs)
# ------------------------------------------------------------

def generate_organization_uid(org_prefix: Optional[str] = None, 
                              uid_type: str = "instance") -> str:
    """
    Generate organization-specific UID or fall back to standard generate_uid().
    Follows DICOM rules: only digits and dots, max length 64.
    """
    if org_prefix is None:
        return generate_uid()

    if not _is_valid_uid_prefix(org_prefix):
        raise ValueError(
            f"Invalid organization UID prefix: {org_prefix}. "
            "UID must contain only numbers and dots, with no consecutive dots."
        )

    timestamp = int(time.time() * 1000000)  # microseconds since epoch
    random_component = random.randint(100000000, 999999999)  # 9-digit numeric
    type_component = _get_uid_type_component(uid_type)

    uid = f"{org_prefix}.{type_component}.{timestamp}.{random_component}"

    if len(uid) > 64:
        # Trim timestamp if needed to satisfy length constraint
        max_timestamp_length = 64 - len(f"{org_prefix}.{type_component}..{random_component}") - 1
        if max_timestamp_length > 0:
            timestamp = int(str(timestamp)[:max_timestamp_length])
            uid = f"{org_prefix}.{type_component}.{timestamp}.{random_component}"
        else:
            return generate_uid()

    return uid


def _is_valid_uid_prefix(uid_prefix: str) -> bool:
    if not uid_prefix or not isinstance(uid_prefix, str):
        return False
    if not uid_prefix.replace('.', '').isdigit():
        return False
    if '..' in uid_prefix:
        return False
    if uid_prefix.startswith('.') or uid_prefix.endswith('.'): 
        return False
    for component in uid_prefix.split('.'): 
        if not component or int(component) < 0:
            return False
    return True


def _get_uid_type_component(uid_type: str) -> str:
    mapping = {
        "instance": "1",
        "series": "2",
        "study": "3",
        "implementation": "4",
    }
    return mapping.get(uid_type.lower(), "1")


def get_common_organization_uids() -> Dict[str, str]:
    return {
        "example_medical_center": "1.2.826.0.1.3680043.8.498",
        "example_hospital": "1.2.826.0.1.3680043.8.499",
        "example_clinic": "1.2.826.0.1.3680043.8.500",
        "example_research_institute": "1.2.826.0.1.3680043.8.501",
        "example_university": "1.2.826.0.1.3680043.8.502",
        "example_manufacturer": "1.2.826.0.1.3680043.8.503",
    }


def validate_organization_uid(uid: str) -> Tuple[bool, str]:
    if not uid or not isinstance(uid, str):
        return False, "UID must be a non-empty string"
    if len(uid) > 64:
        return False, f"UID length {len(uid)} exceeds DICOM limit of 64 characters"
    if not uid.replace('.', '').isdigit():
        return False, "UID must contain only numbers and dots"
    if '..' in uid:
        return False, "UID cannot contain consecutive dots"
    if uid.startswith('.') or uid.endswith('.'): 
        return False, "UID cannot start or end with a dot"
    for i, component in enumerate(uid.split('.')):
        if not component:
            return False, f"Empty component at position {i}"
        try:
            if int(component) < 0:
                return False, f"Negative component at position {i}: {component}"
        except ValueError:
            return False, f"Invalid numeric component at position {i}: {component}"
    return True, "UID is valid"