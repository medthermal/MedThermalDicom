"""
Thermal DICOM Package - Professional thermal imaging DICOM library for medical applications

A comprehensive Python library for creating, manipulating, and visualizing thermal DICOM images
with support for thermal-specific metadata, temperature calibration, and interactive visualization.
"""

__version__ = "1.0.0"
__author__ = "Thermal DICOM Contributors"
__email__ = "support@thermal-dicom.org"

from .core import ThermalDicom
from .visualization import ThermalViewer
from .utils import generate_organization_uid, validate_organization_uid, get_common_organization_uids
from .utils import TemperatureConverter, ThermalCalibrator, ThermalImageProcessor, ThermalROIAnalyzer
from .metadata import ThermalMetadata

__all__ = [
    'ThermalDicom',
    'ThermalViewer',
    'ThermalMetadata',
    'TemperatureConverter',
    'ThermalCalibrator',
    'ThermalImageProcessor',
    'ThermalROIAnalyzer',
    'generate_organization_uid',
    'validate_organization_uid', 
    'get_common_organization_uids'
]