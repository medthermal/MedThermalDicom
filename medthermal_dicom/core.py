"""
Core MedThermal DICOM functionality with thermal-specific private tags and metadata handling.
"""

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pydicom.valuerep import DSfloat
from datetime import datetime
from typing import Optional, Union, Dict, Any, Tuple
import warnings
from .utils import generate_organization_uid, validate_organization_uid
from .overlay import DicomOverlay
from pydicom.dataset import Dataset, FileDataset, DataElement
from pydicom.pixel_data_handlers.numpy_handler import pack_bits

class MedThermalDicom:
    """
    Professional thermal DICOM class for medical thermal imaging applications.
    
    This class provides comprehensive support for creating, manipulating, and managing
    thermal DICOM images with thermal-specific private tags for parameters like
    emissivity, distance, ambient temperature, and calibration data.
    """
    
    # Private tag group for thermal parameters
    THERMAL_GROUP = 0x0019

    # Private Creator ID (max length 16)
    PRIVATE_CREATOR_ID = "MEDTHERMAL_DICOM"

    # Offsets within the private block (mapped to elements 0x10xx in the group)
    # These will be placed at element starting from 0x1000
    PRIVATE_OFFSETS = {
        'emissivity': 0x10,
        'distance_from_camera': 0x11,
        'ambient_temperature': 0x12,
        'reflected_temperature': 0x13,
        'atmospheric_temperature': 0x14,
        'relative_humidity': 0x15,
        'temperature_range_min': 0x16,
        'temperature_range_max': 0x17,
        'temperature_unit': 0x18,
        'thermal_sensitivity': 0x19,
        'spectral_range': 0x20,
        'lens_field_of_view': 0x21,        
    }
    
    # Private tag descriptions for DICOM viewers
    PRIVATE_TAG_DESCRIPTIONS = {
        'emissivity': 'Thermal Emissivity Coefficient',
        'distance_from_camera': 'Distance from Camera to Subject (meters)',
        'ambient_temperature': 'Ambient Temperature (°C)',
        'reflected_temperature': 'Reflected Temperature (°C)',
        'atmospheric_temperature': 'Atmospheric Temperature (°C)',
        'relative_humidity': 'Relative Humidity (%)',       
        'temperature_range_min': 'Minimum Temperature (°C)',
        'temperature_range_max': 'Maximum Temperature (°C)',
        'temperature_unit': 'Temperature Unit',
        'thermal_sensitivity': 'Thermal Sensitivity (NETD)',
        'spectral_range': 'Spectral Range (μm)',
        'lens_field_of_view':'Lens Field of View (degrees)'
    }
    
    def _get_private_block(self, create: bool = True):
        """Return the pydicom PrivateBlock for this dataset/group.

        Using a dedicated creator ensures viewers like RadiAnt show a single
        creator row and place values under that block instead of listing
        them as individual "Private Creator" entries.
        """
        return self.dataset.private_block(self.THERMAL_GROUP, self.PRIVATE_CREATOR_ID, create=create)

    def _set_private_value(self, name: str, value: Any) -> None:
        """Write a private value using the private block API.

        Falls back to legacy tags if needed and cleans up any mistakenly
        written creator-range tags (gggg,00xx).
        """
        if name not in self.PRIVATE_OFFSETS:
            return
        offset = self.PRIVATE_OFFSETS[name]
        # Choose VR and normalized value
        if isinstance(value, (int, float)):
            vr, vr_value = 'DS', DSfloat(value)
        elif isinstance(value, str):
            vr, vr_value = 'LO', value
        elif isinstance(value, datetime):
            vr, vr_value = 'DT', value.strftime("%Y%m%d%H%M%S")
        elif isinstance(value, dict):
            import json
            vr, vr_value = 'LT', json.dumps(value)
        else:
            vr, vr_value = 'LO', str(value)

        if self.use_legacy_private_creator_encoding:
            # Legacy behavior: store directly into (gggg,00xx) so viewers list these with
            # description "Private Creator" (not standards-compliant, but matches earlier UI)
            tag_tuple = (self.THERMAL_GROUP, offset)
            self.dataset.add_new(tag_tuple, vr, vr_value)
        else:
            # Standards-compliant: use private block (element 0x10xx)
            block = self._get_private_block(create=True)
            block.add_new(offset, vr, vr_value)
            # Remove any legacy accidental element if present
            legacy_elem = (self.THERMAL_GROUP, offset)
            try:
                if legacy_elem in self.dataset:
                    del self.dataset[legacy_elem]
            except Exception:
                pass

    def _get_private_value(self, name: str) -> Any:
        """Read a private value from the private block; fallback to legacy tag."""
        if name not in self.PRIVATE_OFFSETS:
            return None
        offset = self.PRIVATE_OFFSETS[name]

        # Preferred: private block unless we are in legacy mode
        if not self.use_legacy_private_creator_encoding:
            try:
                block = self._get_private_block(create=False)
                if block is not None:
                    elem = block.get(offset)
                    if elem is not None:
                        return elem.value
            except Exception:
                pass

        # Fallback to legacy creator-range tag (incorrect old format)
        legacy_elem = (self.THERMAL_GROUP, offset)
        if legacy_elem in self.dataset:
            return self.dataset[legacy_elem].value
        return None

    def __init__(self, thermal_array: Optional[np.ndarray] = None, 
                 temperature_data: Optional[np.ndarray] = None,
                 thermal_params: Optional[Dict[str, Any]] = None,
                 use_legacy_private_creator_encoding: bool = False,
                 organization_uid_prefix: Optional[str] = None,
                 patient_sex: Optional[str] = None,
                 patient_birth_date: Optional[str] = None,
                 study_date: Optional[str] = None):
        """
        Initialize thermal DICOM object.
        
        Args:
            thermal_array: Raw thermal image data (grayscale or temperature values)
            temperature_data: Actual temperature values in Celsius
            thermal_params: Dictionary of thermal imaging parameters
            use_legacy_private_creator_encoding: Use legacy private tag encoding
            organization_uid_prefix: Organization's UID prefix for generating custom UIDs
                                   Format: "1.2.826.0.1.3680043.8.498"
                                   If None, uses standard PyDICOM UID generation
            patient_sex: Patient sex ("M", "F", "O", or None for default)
            patient_birth_date: Patient birth date in YYYYMMDD format (None for default)
            study_date: Study date in YYYYMMDD format (None for current date)
        """
        self.dataset = Dataset()
        self.thermal_array = thermal_array
        self.temperature_data = temperature_data
        self.thermal_params = thermal_params or {}
        self.organization_uid_prefix = organization_uid_prefix
        self.patient_sex = patient_sex
        self.patient_birth_date = patient_birth_date
        self.study_date = study_date
        # If True, write values into (gggg,00xx) creator slots to make viewers
        # display "Private Creator" in description like earlier (non-conformant).
        self.use_legacy_private_creator_encoding = use_legacy_private_creator_encoding
        
        # Initialize basic DICOM structure
        self._initialize_dicom_structure()
        
        # Set thermal-specific parameters
        if thermal_params:
            self.set_thermal_parameters(thermal_params)
    
    def _initialize_dicom_structure(self):
        """Initialize basic DICOM dataset structure for thermal imaging."""
        
        # File Meta Information
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"  # Secondary Capture Image Storage
        # Generate one Instance UID and use it consistently for both file_meta and dataset SOP Instance
        instance_uid = self._generate_uid("instance")
        file_meta.MediaStorageSOPInstanceUID = instance_uid
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        file_meta.ImplementationClassUID = self._generate_uid("implementation")
        # VR SH max length is 16; keep within limits to avoid warnings
        file_meta.ImplementationVersionName = "MEDTHERMAL_DCM_1"
        
        self.dataset.file_meta = file_meta
        
        # Patient Information
        self.dataset.PatientName = "MEDTHERMAL^PATIENT"
        self.dataset.PatientID = "MEDTHERMAL001"
        self.dataset.PatientBirthDate = self.patient_birth_date or ""
        self.dataset.PatientSex = self.patient_sex or ""
        
        # Study Information
        self.dataset.StudyInstanceUID = self._generate_uid("study")
        self.dataset.StudyDate = self.study_date or datetime.now().strftime("%Y%m%d")
        self.dataset.StudyTime = datetime.now().strftime("%H%M%S")
        self.dataset.StudyID = "1"
        self.dataset.StudyDescription = "Thermal Imaging Study"
        
        # Series Information
        self.dataset.SeriesInstanceUID = self._generate_uid("series")
        self.dataset.SeriesNumber = "1"
        self.dataset.SeriesDescription = "Thermal Images"
        self.dataset.Modality = "TG"  # Thermography
        
        # Instance Information
        self.dataset.SOPInstanceUID = instance_uid
        self.dataset.SOPClassUID = file_meta.MediaStorageSOPClassUID
        self.dataset.InstanceNumber = "1"
        self.dataset.ContentDate = self.dataset.StudyDate
        self.dataset.ContentTime = self.dataset.StudyTime
        
        # Image Information (will be updated when image data is set)
        self.dataset.SamplesPerPixel = 1
        self.dataset.PhotometricInterpretation = "MONOCHROME2"
        self.dataset.Rows = 0
        self.dataset.Columns = 0
        self.dataset.BitsAllocated = 16
        self.dataset.BitsStored = 16
        self.dataset.HighBit = 15
        self.dataset.PixelRepresentation = 0
        
        # Thermal-specific metadata
        self.dataset.ImageType = ["DERIVED", "SECONDARY", "THERMAL"]
        self.dataset.AcquisitionDeviceProcessingDescription = "Thermal Imaging Processing"
    
    def _generate_uid(self, uid_type: str = "instance") -> str:
        """
        Generate UID using organization prefix if available, otherwise fall back to standard.
        
        Args:
            uid_type: Type of UID to generate ("instance", "series", "study", "implementation")
            
        Returns:
            Generated UID string
        """
        return generate_organization_uid(self.organization_uid_prefix, uid_type)
    
    def set_organization_uid_prefix(self, org_prefix: str):
        """
        Set or change the organization UID prefix after initialization.
        
        Args:
            org_prefix: Organization's UID prefix (e.g., "1.2.826.0.1.3680043.8.498")
            
        Raises:
            ValueError: If the UID prefix format is invalid
        """
        if org_prefix is not None:
            # Validate the prefix format
            from .utils import _is_valid_uid_prefix
            if not _is_valid_uid_prefix(org_prefix):
                raise ValueError(
                    f"Invalid organization UID prefix: {org_prefix}. "
                    "UID must contain only numbers and dots, with no consecutive dots."
                )
        
        self.organization_uid_prefix = org_prefix
        
        # Regenerate UIDs if dataset already exists
        if hasattr(self, 'dataset') and self.dataset:
            self._regenerate_uids()
    
    def _regenerate_uids(self):
        """Regenerate all UIDs with the current organization prefix."""
        if not self.dataset:
            return
            
        # Regenerate file meta UIDs
        if hasattr(self.dataset, 'file_meta') and self.dataset.file_meta:
            self.dataset.file_meta.MediaStorageSOPInstanceUID = self._generate_uid("instance")
            self.dataset.file_meta.ImplementationClassUID = self._generate_uid("implementation")
        
        # Regenerate dataset UIDs
        self.dataset.StudyInstanceUID = self._generate_uid("study")
        self.dataset.SeriesInstanceUID = self._generate_uid("series")
        self.dataset.SOPInstanceUID = self._generate_uid("instance")
        
        # Update SOPClassUID reference
        if hasattr(self.dataset, 'file_meta') and self.dataset.file_meta:
            self.dataset.SOPClassUID = self.dataset.file_meta.MediaStorageSOPClassUID
    
    def get_organization_uid_info(self) -> Dict[str, Any]:
        """
        Get information about the current organization UID configuration.
        
        Returns:
            Dictionary containing UID configuration information
        """
        return {
            'organization_uid_prefix': self.organization_uid_prefix,
            'is_using_custom_uids': self.organization_uid_prefix is not None,
            'current_uids': {
                'study': getattr(self.dataset, 'StudyInstanceUID', None),
                'series': getattr(self.dataset, 'SeriesInstanceUID', None),
                'instance': getattr(self.dataset, 'SOPInstanceUID', None),
                'implementation': getattr(self.dataset.file_meta, 'ImplementationClassUID', None) if hasattr(self.dataset, 'file_meta') else None
            }
        }
    
    def add_overlay(self, overlay_array: np.ndarray, position: Tuple[int, int],text: str):
        """
        Add overlay to the DICOM dataset.
        
        Args:
            overlay_array: Overlay array
            position: Position of the overlay
        """
        overlay_obj = DicomOverlay()
        overlay_image = overlay_obj.draw_annotation(overlay_array, position, text)
        overlay_image = (overlay_image>0).astype(np.uint8)
        packed_bytes = pack_bits(overlay_image)
        rows, cols = overlay_image.shape
        group = 0x6000

        # Required overlay tags
        self.dataset.add(DataElement((group , 0x0010), 'US', rows))           # Rows
        self.dataset.add(DataElement((group , 0x0011), 'US', cols))           # Cols
        self.dataset.add(DataElement((group , 0x0040), 'CS', 'G'))            # Region/Graphics overlay
        self.dataset.add(DataElement((group , 0x0050), 'SS', [1, 1]))         # Origin
        self.dataset.add(DataElement((group , 0x0100), 'US', 1))              # Bits allocated
        self.dataset.add(DataElement((group , 0x0102), 'US', 0))             # Overlay bit position
        self.dataset.add(DataElement((group , 0x0015), 'IS', "1"))            # Number of frames
        self.dataset.add(DataElement((group , 0x3000), 'OW', packed_bytes))   # OverlayData

    def set_thermal_parameters(self, params: Dict[str, Any]):
        """
        Set thermal imaging parameters as private DICOM tags.
        
        Args:
            params: Dictionary containing thermal parameters
        """
        self.thermal_params.update(params)
        
        # Write parameters into our private block
        for param_name, value in params.items():
            if param_name in self.PRIVATE_OFFSETS:
                self._set_private_value(param_name, value)

    
    def get_thermal_parameter(self, param_name: str) -> Any:
        """
        Get thermal parameter value.
        
        Args:
            param_name: Name of the thermal parameter
            
        Returns:
            Parameter value or None if not found
        """
        if param_name in self.PRIVATE_OFFSETS:
            value = self._get_private_value(param_name)
            if value is not None:
                return value
        return self.thermal_params.get(param_name)
    
    def set_thermal_image(self, thermal_array: np.ndarray, 
                         temperature_data: Optional[np.ndarray] = None,
                         temperature_range: Optional[Tuple[float, float]] = None):
         """
         Set thermal image data with optional temperature calibration.
         
         Args:
             thermal_array: Raw thermal image data
             temperature_data: Actual temperature values in Celsius
             temperature_range: Min/max temperature range for scaling
         """
         self.thermal_array = thermal_array.copy()
         
         if temperature_data is not None:
             self.temperature_data = temperature_data.copy()
         else:
             # If no temperature data is provided, clear any previous temperature_data
             self.temperature_data = None
         
         # Update DICOM image parameters
         if len(thermal_array.shape) == 2:
             # Grayscale/temperature matrix
             self.dataset.Rows = thermal_array.shape[0]
             self.dataset.Columns = thermal_array.shape[1]
             self.dataset.SamplesPerPixel = 1
             self.dataset.PhotometricInterpretation = "MONOCHROME2"
             self.dataset.BitsAllocated = 16
             self.dataset.BitsStored = 16
             self.dataset.HighBit = 15
             self.dataset.PixelRepresentation = 0
             # Convert to appropriate bit depth and set pixel data
             if thermal_array.dtype != np.uint16:
                 # Scale to 16-bit range
                 #print('thermal array 16',temperature_range)
                 if temperature_range:
                     min_temp, max_temp = temperature_range
                     scaled_array = ((thermal_array - min_temp) / (max_temp - min_temp) * 65535).astype(np.uint16)
                 else:
                     min_val, max_val = thermal_array.min(), thermal_array.max()
                     print("min max val:",min_val,max_val)
                     if max_val > min_val:
                         scaled_array = ((thermal_array - min_val) / (max_val - min_val) * 65535).astype(np.uint16)
                     else:
                         scaled_array = thermal_array.astype(np.uint16)
             else:
                 scaled_array = thermal_array
             
             self.dataset.PixelData = scaled_array.tobytes()
             
             # Store temperature range information and add viewer-friendly mapping tags
             if temperature_range:
                 self.set_thermal_parameters({
                     'temperature_range_min': temperature_range[0],
                     'temperature_range_max': temperature_range[1],
                     'temperature_unit': 'Celsius'
                 })
 
                 # Add standard rescale so viewers can convert pixel -> temperature
                 min_temp, max_temp = float(temperature_range[0]), float(temperature_range[1])
                 if max_temp > min_temp:
                     slope = (max_temp - min_temp) / 65535.0
                 else:
                     slope = 1.0
                 intercept = min_temp
 
                 # 0028,1053 Rescale Slope; 0028,1052 Rescale Intercept; 0028,1054 Rescale Type
                 self.dataset.RescaleSlope = DSfloat(slope)
                 self.dataset.RescaleIntercept = DSfloat(intercept)
                 self.dataset.RescaleType = "TEMP"
 
                 # Helpful window for temperature range (applied after rescale per standard behavior)
                 self.dataset.WindowCenter = DSfloat((min_temp + max_temp) / 2.0)
                 self.dataset.WindowWidth = DSfloat((max_temp - min_temp))
 
                 # Real World Value Mapping Sequence with UCUM units for Celsius
                 try:
                     from pydicom.sequence import Sequence
                     rwv_item = Dataset()
                     rwv_item.LUTExplanation = "Temperature mapping"
                     rwv_item.RealWorldValueFirstValueMapped = 0
                     rwv_item.RealWorldValueLastValueMapped = 65535
                     rwv_item.RealWorldValueIntercept = DSfloat(intercept)
                     rwv_item.RealWorldValueSlope = DSfloat(slope)
 
                     # Measurement Units Code Sequence (UCUM: degree Celsius)
                     unit_item = Dataset()
                     unit_item.CodeValue = "Cel"
                     unit_item.CodingSchemeDesignator = "UCUM"
                     unit_item.CodeMeaning = "degree Celsius"
                     rwv_item.MeasurementUnitsCodeSequence = Sequence([unit_item])
 
                     self.dataset.RealWorldValueMappingSequence = Sequence([rwv_item])
                 except Exception:
                     # If Sequence import or assignment fails, continue without RWVM
                     pass
             else:
                 # If no explicit temperature range is provided for a grayscale image,
                 # remove any previous rescale/RWVM to avoid implying temperatures.
                 for attr in [
                     'RescaleSlope', 'RescaleIntercept', 'RescaleType',
                     'WindowCenter', 'WindowWidth', 'RealWorldValueMappingSequence']:
                     if hasattr(self.dataset, attr):
                         try:
                             delattr(self.dataset, attr)
                         except Exception:
                             pass
 
         elif len(thermal_array.shape) == 3 and thermal_array.shape[2] == 3:
             # RGB color image input
             self.dataset.Rows = thermal_array.shape[0]
             self.dataset.Columns = thermal_array.shape[1]
             self.dataset.SamplesPerPixel = 3
             self.dataset.PhotometricInterpretation = "RGB"
             self.dataset.PlanarConfiguration = 0  # interleaved RGB
             self.dataset.BitsAllocated = 8
             self.dataset.BitsStored = 8
             self.dataset.HighBit = 7
             self.dataset.PixelRepresentation = 0
 
             # Ensure uint8 [0,255]
             if thermal_array.dtype == np.uint8:
                 rgb_array = thermal_array
             else:
                 # Scale safely to 0-255
                 min_val = float(thermal_array.min())
                 max_val = float(thermal_array.max())
                 if max_val > min_val:
                     rgb_array = ((thermal_array - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)
                 else:
                     rgb_array = np.clip(thermal_array, 0, 255).astype(np.uint8)
 
             self.dataset.PixelData = rgb_array.tobytes()
 
             # For color images without temperature data, ensure temperature mapping metadata is absent
             for attr in [
                 'RescaleSlope', 'RescaleIntercept', 'RescaleType',
                 'WindowCenter', 'WindowWidth', 'RealWorldValueMappingSequence']:
                 if hasattr(self.dataset, attr):
                     try:
                         delattr(self.dataset, attr)
                     except Exception:
                         pass
         else:
             raise ValueError("Unsupported thermal_array shape. Expected (H,W) or (H,W,3).")
    
    def get_temperature_at_pixel(self, row: int, col: int) -> Optional[float]:
        """
        Get temperature value at specific pixel coordinates.
        
        Args:
            row: Row coordinate
            col: Column coordinate
            
        Returns:
            Temperature in Celsius or None if not available
        """
        if self.temperature_data is not None:
            if 0 <= row < self.temperature_data.shape[0] and 0 <= col < self.temperature_data.shape[1]:
                return float(self.temperature_data[row, col])
        
        # If no direct temperature data, try to convert from pixel values
        if self.thermal_array is not None:
            min_temp = self.get_thermal_parameter('temperature_range_min')
            max_temp = self.get_thermal_parameter('temperature_range_max')
            
            if min_temp is not None and max_temp is not None:
                pixel_value = self.thermal_array[row, col]
                if self.thermal_array.dtype == np.uint16:
                    # Convert from 16-bit to temperature
                    normalized = pixel_value / 65535.0
                    return float(min_temp) + normalized * (float(max_temp) - float(min_temp))
        
        return None
    
    def calculate_roi_statistics(self, roi_mask: np.ndarray) -> Dict[str, float]:
        """
        Calculate temperature statistics for a region of interest.
        
        Args:
            roi_mask: Boolean mask defining the ROI
            
        Returns:
            Dictionary with statistical measures
        """
        if self.temperature_data is None:
            raise ValueError("Temperature data not available for ROI analysis")
        
        roi_temps = self.temperature_data[roi_mask]
        
        # Handle empty ROI
        if len(roi_temps) == 0:
            stats = {
                'mean_temperature': 0.0,
                'min_temperature': 0.0,
                'max_temperature': 0.0,
                'std_temperature': 0.0,
                'median_temperature': 0.0,
                'pixel_count': 0
            }
        else:
            stats = {
                'mean_temperature': float(np.mean(roi_temps)),
                'min_temperature': float(np.min(roi_temps)),
                'max_temperature': float(np.max(roi_temps)),
                'std_temperature': float(np.std(roi_temps)),
                'median_temperature': float(np.median(roi_temps)),
                'pixel_count': int(np.sum(roi_mask))
            }
        
        # Store ROI statistics as private tag
        self.set_thermal_parameters({'roi_temperature_stats': stats})
        
        return stats
    
    def save_dicom(self, filepath: str):
        """
        Save thermal DICOM to file.
        
        Args:
            filepath: Output file path
        """
        # Ensure all required fields are present
        if not hasattr(self.dataset, 'PixelData') or self.dataset.PixelData is None:
            warnings.warn("No pixel data set. Creating empty pixel data.")
            self.dataset.Rows = 512
            self.dataset.Columns = 512
            self.dataset.PixelData = np.zeros((512, 512), dtype=np.uint16).tobytes()
        
        # Save the DICOM file
        self.dataset.save_as(filepath, write_like_original=False)
    
    @classmethod
    def load_dicom(cls, filepath: str) -> 'MedThermalDicom':
        """
        Load thermal DICOM from file.
        
        Args:
            filepath: Input file path
            
        Returns:
            MedThermalDicom instance
        """
        dataset = pydicom.dcmread(filepath)
        
        # Create new instance
        thermal_dicom = cls()
        thermal_dicom.dataset = dataset
        
        # Extract thermal parameters from private tags
        thermal_params = {}
        for param_name, offset in cls.PRIVATE_OFFSETS.items():
            # Create the private tag from group and offset
            tag = (cls.THERMAL_GROUP, offset)
            if tag in dataset:
                value = dataset[tag].value
                # Try to convert JSON strings back to dict
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    try:
                        import json
                        value = json.loads(value)
                    except:
                        pass
                thermal_params[param_name] = value
        
        thermal_dicom.thermal_params = thermal_params
        
        # Extract pixel data
        if hasattr(dataset, 'PixelData') and dataset.PixelData:
            pixel_array = dataset.pixel_array
            thermal_dicom.thermal_array = pixel_array
        
        return thermal_dicom
    
    def create_standard_thermal_dicom(self, 
                                    patient_name: str,
                                    patient_id: str,                                                  
                                    study_description: str = "Thermal Medical Imaging",
                                    thermal_params: Optional[Dict[str, Any]] = None,
                                    patient_sex: Optional[str] = None,
                                    patient_birth_date: Optional[str] = None,
                                    study_date: Optional[str] = None) -> 'MedThermalDicom':
        """
        Create a standard thermal DICOM with medical imaging best practices.
        
        Args:
            patient_name: Patient name
            patient_id: Patient ID
            study_description: Study description
            thermal_params: Thermal imaging parameters
            patient_sex: Patient sex ("M", "F", "O", or None for default)
            patient_birth_date: Patient birth date in YYYYMMDD format (None for default)
            study_date: Study date in YYYYMMDD format (None for current date)
            
        Returns:
            Configured MedThermalDicom instance
        """
        # Update patient information
        self.dataset.PatientName = patient_name
        self.dataset.PatientID = patient_id
        self.dataset.StudyDescription = study_description
        
        # Update patient demographics if provided
        if patient_sex is not None:
            self.dataset.PatientSex = patient_sex
        if patient_birth_date is not None:
            self.dataset.PatientBirthDate = patient_birth_date
        if study_date is not None:
            self.dataset.StudyDate = study_date
        
        if thermal_params is None:
            thermal_params = {
                'emissivity':'',  # Human skin emissivity
                'distance_from_camera': '',  # meters
                'ambient_temperature': '',  # Celsius
                'reflected_temperature': '',  # Celsius
                'relative_humidity': '',  # percentage
                'temperature_unit': '',
                'acquisition_mode': ''
            }
        
        self.set_thermal_parameters(thermal_params)
        
        return self