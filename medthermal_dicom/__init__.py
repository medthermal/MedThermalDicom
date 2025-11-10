"""
MedThermal DICOM Package - Professional thermal imaging DICOM library for medical applications

A comprehensive Python library for creating, manipulating, and visualizing thermal DICOM images
with support for thermal-specific metadata, temperature calibration, and interactive visualization.
"""

__version__ = "1.0.0"
__author__ = "MedThermal DICOM Contributors"
__email__ = "support@medthermal-dicom.org"

from .core import MedThermalDicom
from .visualization import MedThermalViewer
from .utils import generate_organization_uid, validate_organization_uid, get_common_organization_uids
from .utils import MedThermalTemperatureConverter, MedThermalCalibrator, MedThermalImageProcessor, MedThermalROIAnalyzer
from .metadata import MedThermalMetadata

__all__ = [
    'MedThermalDicom',
    'MedThermalViewer',
    'MedThermalMetadata',
    'MedThermalTemperatureConverter',
    'MedThermalCalibrator',
    'MedThermalImageProcessor',
    'MedThermalROIAnalyzer',
    'generate_organization_uid',
    'validate_organization_uid', 
    'get_common_organization_uids'
]