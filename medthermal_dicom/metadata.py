"""
MedThermal DICOM metadata handling for standards compliance and interoperability.
"""

import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union, Tuple
import json
import warnings
from .utils import generate_organization_uid


class MedThermalMetadata:
    """
    Professional thermal DICOM metadata management for medical imaging standards compliance.
    
    Handles thermal-specific metadata, DICOM standard compliance, and interoperability
    with medical imaging systems and PACS.
    """
    
    # Standard DICOM modality codes for thermal imaging
    # TG is the preferred modality for Thermography. Keep others for compatibility.
    THERMAL_MODALITIES = {
        'TG': 'Thermography',
        'OT': 'Other',          # Fallback when TG not supported by a system
        'IR': 'Infrared'        # Alternative designation seen in some systems
    }
    
    # Standard DICOM view positions for thermal imaging
    # These follow DICOM standard view position codes
    VIEW_POSITIONS = {
        # Standard anatomical views
        'A': 'Anterior',
        'P': 'Posterior', 
        'L': 'Left',
        'R': 'Right',
        'LA': 'Left Anterior',
        'RA': 'Right Anterior',
        'LP': 'Left Posterior',
        'RP': 'Right Posterior',
        'LL': 'Left Lateral',
        'RL': 'Right Lateral',
        'LAO': 'Left Anterior Oblique',
        'RAO': 'Right Anterior Oblique',
        'LPO': 'Left Posterior Oblique',
        'RPO': 'Right Posterior Oblique',
        
        # Thermal-specific views
        'ANT': 'Anterior View',
        'POST': 'Posterior View',
        'LAT': 'Lateral View',
        'OBL': 'Oblique View',
        'SUP': 'Superior View',
        'INF': 'Inferior View',
        'MED': 'Medial View',
        'LAT': 'Lateral View',
        
        # Special thermal views
        'FRONT': 'Frontal View',
        'BACK': 'Back View',
        'SIDE': 'Side View',
        'TOP': 'Top View',
        'BOTTOM': 'Bottom View'
    }
    
    # Patient positions for thermal imaging
    PATIENT_POSITIONS = {
        'HFS': 'Head First Supine',
        'HFP': 'Head First Prone',
        'FFS': 'Feet First Supine',
        'FFP': 'Feet First Prone',
        'HFDL': 'Head First Decubitus Left',
        'HFDR': 'Head First Decubitus Right',
        'FFDL': 'Feet First Decubitus Left',
        'FFDR': 'Feet First Decubitus Right',
        'STANDING': 'Standing',
        'SITTING': 'Sitting',
        'SEATED': 'Seated'
    }
    
    # Medical thermal imaging procedure codes
    # Use SNOMED CT codes where known; for comprehensive body-region procedures
    # define a private scheme "99THERM" with clear meanings as a safe fallback.
    THERMAL_PROCEDURE_CODES = {
        'breast_thermography': {
            'code': '241439007',
            'meaning': 'Breast thermography',
            'scheme': 'SCT'
        },
        'vascular_thermography': {
            'code': '241440009',
            'meaning': 'Vascular thermography',
            'scheme': 'SCT'
        },
        'diagnostic_thermography': {
            'code': '77477000',
            'meaning': 'Diagnostic thermography',
            'scheme': 'SCT'
        },
        # Whole-body and region-specific workflows (private scheme identifiers)
        'whole_body_thermography': {
            'code': 'WB-THERM',
            'meaning': 'Whole body thermography',
            'scheme': '99THERM'
        },
        'upper_limb_thermography': {
            'code': 'UL-THERM',
            'meaning': 'Upper limb thermography',
            'scheme': '99THERM'
        },
        'lower_limb_thermography': {
            'code': 'LL-THERM',
            'meaning': 'Lower limb thermography',
            'scheme': '99THERM'
        },
        'head_thermography': {
            'code': 'HEAD-THERM',
            'meaning': 'Head thermography',
            'scheme': '99THERM'
        },
        'neck_thermography': {
            'code': 'NECK-THERM',
            'meaning': 'Neck thermography',
            'scheme': '99THERM'
        },
        'spine_back_thermography': {
            'code': 'BACK-THERM',
            'meaning': 'Spine/Back thermography',
            'scheme': '99THERM'
        },
        'hand_thermography': {
            'code': 'HAND-THERM',
            'meaning': 'Hand thermography',
            'scheme': '99THERM'
        },
        'foot_thermography': {
            'code': 'FOOT-THERM',
            'meaning': 'Foot thermography',
            'scheme': '99THERM'
        }
    }
    
    # Anatomical region catalog for whole-body thermography workflows.
    # Where authoritative codes are not readily available, use private scheme.
    ANATOMICAL_REGIONS = {
        'whole_body': { 'code': 'WB', 'meaning': 'Whole Body', 'scheme': '99THERM' },
        'head':       { 'code': '69536005', 'meaning': 'Head', 'scheme': 'SCT' },
        'neck':       { 'code': '45048000', 'meaning': 'Neck', 'scheme': 'SCT' },
        'face':       { 'code': '89545001', 'meaning': 'Face', 'scheme': 'SCT' },
        'chest':      { 'code': '80891009', 'meaning': 'Chest', 'scheme': 'SCT' },
        'abdomen':    { 'code': '818981001', 'meaning': 'Abdomen', 'scheme': 'SCT' },
        'pelvis':     { 'code': '816092008', 'meaning': 'Pelvis', 'scheme': 'SCT' },
        'back':       { 'code': '77568009', 'meaning': 'Back', 'scheme': 'SCT' },
        'spine':      { 'code': '421060000', 'meaning': 'Spine', 'scheme': 'SCT' },
        'shoulder':   { 'code': '16982009', 'meaning': 'Shoulder region', 'scheme': 'SCT' },
        'arm':        { 'code': '40983000', 'meaning': 'Arm', 'scheme': 'SCT' },
        'elbow':      { 'code': '16953009', 'meaning': 'Elbow region', 'scheme': 'SCT' },
        'wrist':      { 'code': '74670003', 'meaning': 'Wrist region', 'scheme': 'SCT' },
        'hand':       { 'code': '85562004', 'meaning': 'Hand', 'scheme': 'SCT' },
        'finger':     { 'code': '7569003', 'meaning': 'Finger', 'scheme': 'SCT' },
        'hip':        { 'code': '85050009', 'meaning': 'Hip region', 'scheme': 'SCT' },
        'thigh':      { 'code': '30021000', 'meaning': 'Thigh', 'scheme': 'SCT' },
        'knee':       { 'code': '72696002', 'meaning': 'Knee region', 'scheme': 'SCT' },
        'leg':        { 'code': '30021000', 'meaning': 'Leg', 'scheme': 'SCT' },
        'ankle':      { 'code': '35185008', 'meaning': 'Ankle region', 'scheme': 'SCT' },
        'foot':       { 'code': '56459004', 'meaning': 'Foot', 'scheme': 'SCT' },
        'toe':        { 'code': '29707007', 'meaning': 'Toe', 'scheme': 'SCT' },
        'breast':     { 'code': '76752008', 'meaning': 'Breast', 'scheme': 'SCT' }
    }
    
    def __init__(self, organization_uid_prefix: Optional[str] = None):
        """Initialize thermal metadata handler.
        
        Args:
            organization_uid_prefix: Optional organization UID prefix used to generate DICOM UIDs
        """
        self.organization_uid_prefix = organization_uid_prefix
        self.standard_metadata = {}
        self.thermal_parameters = {}
        self.quality_control = {}
        self.calibration_info = {}
    
    def _gen_uid(self, uid_type: str) -> str:
        """Generate an org-prefixed UID for the given type."""
        return generate_organization_uid(self.organization_uid_prefix, uid_type)

    def set_patient_information(self, 
                              patient_name: str,
                              patient_id: str,
                              patient_birth_date: Optional[Union[str, date]] = None,
                              patient_sex: Optional[str] = None,
                              patient_age: Optional[str] = None,
                              patient_weight: Optional[float] = None,
                              patient_height: Optional[float] = None) -> Dict[str, Any]:
        """
        Set comprehensive patient information following DICOM standards.
        
        Args:
            patient_name: Patient name in DICOM format (LAST^FIRST^MIDDLE)
            patient_id: Unique patient identifier
            patient_birth_date: Birth date (YYYYMMDD format or date object)
            patient_sex: Patient sex (M, F, O, or empty)
            patient_age: Patient age (format: nnnD, nnnW, nnnM, nnnY)
            patient_weight: Patient weight in kg
            patient_height: Patient height in meters
            
        Returns:
            Dictionary with patient metadata
        """
        patient_info = {
            'PatientName': patient_name,
            'PatientID': patient_id
        }
        
        if patient_birth_date:
            if isinstance(patient_birth_date, date):
                patient_info['PatientBirthDate'] = patient_birth_date.strftime("%Y%m%d")
            else:
                patient_info['PatientBirthDate'] = patient_birth_date
        
        if patient_sex:
            if patient_sex.upper() in ['M', 'F', 'O']:
                patient_info['PatientSex'] = patient_sex.upper()
            else:
                warnings.warn(f"Invalid patient sex: {patient_sex}. Using empty string.")
                patient_info['PatientSex'] = ''
        
        if patient_age:
            patient_info['PatientAge'] = patient_age
        
        if patient_weight:
            patient_info['PatientWeight'] = str(patient_weight)
        
        if patient_height:
            patient_info['PatientSize'] = str(patient_height)
        
        self.standard_metadata.update(patient_info)
        return patient_info
    
    def set_study_information(self,
                            study_description: str = "Thermal Medical Imaging",
                            study_id: Optional[str] = None,
                            accession_number: Optional[str] = None,
                            referring_physician: Optional[str] = None,
                            study_date: Optional[Union[str, date]] = None,
                            study_time: Optional[str] = None,
                            procedure_code: Optional[str] = None,
                            study_instance_uid: Optional[str] = None) -> Dict[str, Any]:
        """
        Set study-level information for thermal imaging.
        
        Args:
            study_description: Description of the study
            study_id: Study identifier
            accession_number: Accession number from RIS/HIS
            referring_physician: Referring physician name
            study_date: Study date (YYYYMMDD format or date object)
            study_time: Study time (HHMMSS format)
            procedure_code: Procedure code key from THERMAL_PROCEDURE_CODES
            
        Returns:
            Dictionary with study metadata
        """
        study_info = {
            'StudyInstanceUID': study_instance_uid or self._gen_uid('study'),
            'StudyDescription': study_description,
            'StudyID': study_id or "1"
        }
        
        if accession_number:
            study_info['AccessionNumber'] = accession_number
        
        if referring_physician:
            study_info['ReferringPhysicianName'] = referring_physician
        
        # Set study date and time
        if study_date:
            if isinstance(study_date, date):
                study_info['StudyDate'] = study_date.strftime("%Y%m%d")
            else:
                study_info['StudyDate'] = study_date
        else:
            study_info['StudyDate'] = datetime.now().strftime("%Y%m%d")
        
        if study_time:
            study_info['StudyTime'] = study_time
        else:
            study_info['StudyTime'] = datetime.now().strftime("%H%M%S")
        
        # Add procedure code sequence if specified
        if procedure_code and procedure_code in self.THERMAL_PROCEDURE_CODES:
            proc_info = self.THERMAL_PROCEDURE_CODES[procedure_code]
            study_info['ProcedureCodeSequence'] = [{
                'CodeValue': proc_info['code'],
                'CodeMeaning': proc_info['meaning'],
                'CodingSchemeDesignator': proc_info['scheme']
            }]
        
        self.standard_metadata.update(study_info)
        return study_info
    
    def set_series_information(self,
                             series_description: str = "Thermal Images",
                             series_number: Optional[str] = None,
                              modality: str = 'TG',
                              body_part: Optional[Union[str, List[str]]] = None,
                             laterality: Optional[str] = None,
                             patient_position: Optional[str] = None,
                             series_instance_uid: Optional[str] = None) -> Dict[str, Any]:
        """
        Set series-level information for thermal imaging.
        
        Args:
            series_description: Description of the series
            series_number: Series number
            modality: DICOM modality (OT, TH, IR)
            body_part: Body part examined (key from ANATOMICAL_REGIONS)
            laterality: Laterality (L, R, B for bilateral)
            patient_position: Patient position (HFS, HFP, FFS, FFP, etc.)
            
        Returns:
            Dictionary with series metadata
        """
        series_info = {
            'SeriesInstanceUID': series_instance_uid or self._gen_uid('series'),
            'SeriesDescription': series_description,
            'SeriesNumber': series_number or "1",
            'Modality': modality if modality in self.THERMAL_MODALITIES else 'OT'
        }
        
        # Body part(s) handling: accepts a single key or a list of keys for whole-body workflows
        if body_part:
            region_keys = body_part if isinstance(body_part, list) else [body_part]
            region_items = []
            for key in region_keys:
                if key in self.ANATOMICAL_REGIONS:
                    info = self.ANATOMICAL_REGIONS[key]
                    region_items.append({
                        'CodeValue': info['code'],
                        'CodeMeaning': info['meaning'],
                        'CodingSchemeDesignator': info['scheme']
                    })
            if region_items:
                series_info['AnatomicRegionSequence'] = region_items
                # Prefer explicit WHOLE BODY if included, else first item
                if 'whole_body' in region_keys:
                    series_info['BodyPartExamined'] = 'WHOLEBODY'
                else:
                    series_info['BodyPartExamined'] = region_items[0]['CodeMeaning'] if len(region_items) == 1 else 'MULTIPLE'
        
        if laterality and laterality.upper() in ['L', 'R', 'B']:
            series_info['Laterality'] = laterality.upper()
        
        if patient_position:
            series_info['PatientPosition'] = patient_position
        
        self.standard_metadata.update(series_info)
        return series_info
    
    def set_view_information(self,
                           view_position: Optional[str] = None,
                           image_laterality: Optional[str] = None,
                           view_comment: Optional[str] = None,
                           image_comments: Optional[str] = None,
                           acquisition_view: Optional[str] = None) -> Dict[str, Any]:
        """
        Set view-specific information for thermal imaging.
        
        This method handles different views of the same anatomical region,
        allowing creation of multiple DICOM files for different perspectives.
        
        Args:
            view_position: View position code (from VIEW_POSITIONS)
            image_laterality: Image laterality (L, R, B for bilateral)
            view_comment: Additional view description
            image_comments: General image comments
            acquisition_view: Acquisition view description
            
        Returns:
            Dictionary with view metadata
        """
        view_info = {}
        
        # Set view position
        if view_position:
            if view_position.upper() in self.VIEW_POSITIONS:
                view_info['ViewPosition'] = view_position.upper()
                view_info['ViewPositionDescription'] = self.VIEW_POSITIONS[view_position.upper()]
            else:
                # Custom view position
                view_info['ViewPosition'] = view_position.upper()
                view_info['ViewPositionDescription'] = view_position
        
        # Set image laterality
        if image_laterality and image_laterality.upper() in ['L', 'R', 'B']:
            view_info['ImageLaterality'] = image_laterality.upper()
        
        # Set view comment
        if view_comment:
            view_info['ViewComment'] = view_comment
        
        # Set image comments
        if image_comments:
            view_info['ImageComments'] = image_comments
        
        # Set acquisition view
        if acquisition_view:
            view_info['AcquisitionView'] = acquisition_view
        
        # Generate unique view identifier
        view_identifier = self._generate_view_identifier(view_info)
        view_info['ViewIdentifier'] = view_identifier
        
        self.standard_metadata.update(view_info)
        return view_info
    
    def _generate_view_identifier(self, view_info: Dict[str, Any]) -> str:
        """
        Generate a unique identifier for the view combination.
        
        Args:
            view_info: Dictionary containing view information
            
        Returns:
            Unique view identifier string
        """
        components = []
        
        if 'ViewPosition' in view_info:
            components.append(view_info['ViewPosition'])
        
        if 'ImageLaterality' in view_info:
            components.append(view_info['ImageLaterality'])
        
        if 'ViewComment' in view_info:
            # Clean comment for identifier
            clean_comment = view_info['ViewComment'].replace(' ', '_').replace('-', '_')
            components.append(clean_comment)
        
        if not components:
            components.append('DEFAULT')
        
        return '_'.join(components)
    
    def create_multi_view_series(self,
                               base_series_description: str,
                               anatomical_region: str,
                               views: List[Dict[str, Any]],
                               series_number: int = 1,
                               study_instance_uid: Optional[str] = None,
                               base_series_instance_uid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create multiple series entries for different views of the same anatomical region.
        
        By default, all views will share the same StudyInstanceUID and SeriesInstanceUID
        so they are grouped under one study and series, while each view will get a
        unique InstanceNumber. You can override the study/series UIDs via parameters.
        
        Args:
            base_series_description: Base description for the series
            anatomical_region: Anatomical region key from ANATOMICAL_REGIONS
            views: List of view dictionaries with view information
            series_number: Starting series/instance number
            study_instance_uid: Optional StudyInstanceUID to enforce across all views
            base_series_instance_uid: Optional SeriesInstanceUID to enforce across all views
            
        Returns:
            List of series metadata dictionaries for each view
        """
        series_list: List[Dict[str, Any]] = []
        
        # Ensure a shared StudyInstanceUID across all views
        shared_study_uid: str = study_instance_uid or self.standard_metadata.get('StudyInstanceUID') or self._gen_uid('study')
        self.standard_metadata['StudyInstanceUID'] = shared_study_uid
        
        # Ensure a shared SeriesInstanceUID across all views (group as one series)
        shared_series_uid: str = base_series_instance_uid or self._gen_uid('series')
        # Provide a shared FrameOfReferenceUID to help some viewers group images
        shared_for_uid: str = self._gen_uid('series')
        # Provide consistent SeriesDate/Time
        series_date = self.standard_metadata.get('StudyDate', datetime.now().strftime("%Y%m%d"))
        series_time = self.standard_metadata.get('StudyTime', datetime.now().strftime("%H%M%S"))
        
        for i, view_config in enumerate(views):
            # Create view-specific series description suffix if provided
            view_position = view_config.get('view_position', '') or ''
            view_desc = f"{base_series_description} - {view_position}".strip() if view_position else base_series_description
            
            # Set series information, enforcing shared SeriesInstanceUID
            series_info = self.set_series_information(
                series_description=base_series_description,
                series_number=str(series_number),
                body_part=anatomical_region,
                laterality=view_config.get('laterality'),
                patient_position=view_config.get('patient_position'),
                series_instance_uid=shared_series_uid
            )
            
            # Set view information
            view_info = self.set_view_information(
                view_position=view_config.get('view_position'),
                image_laterality=view_config.get('image_laterality'),
                view_comment=view_config.get('view_comment'),
                image_comments=view_config.get('image_comments'),
                acquisition_view=view_config.get('acquisition_view')
            )
            
            # Assign per-view InstanceNumber to distinguish instances in the same series
            combined_info = {**series_info, **view_info, 'InstanceNumber': str(series_number + i)}
            # Add shared Frame of Reference and consistent Series timing
            combined_info['FrameOfReferenceUID'] = shared_for_uid
            combined_info['SeriesDate'] = series_date
            combined_info['SeriesTime'] = series_time
            series_list.append(combined_info)
        
        return series_list
    
    def set_equipment_information(self,
                                manufacturer: str = "MedThermal DICOM Library",
                                manufacturer_model: Optional[str] = None,
                                device_serial_number: Optional[str] = None,
                                software_version: Optional[str] = None,
                                detector_type: Optional[str] = None,
                                spatial_resolution: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Set equipment and device information.
        
        Args:
            manufacturer: Equipment manufacturer
            manufacturer_model: Model name
            device_serial_number: Serial number
            software_version: Software version
            detector_type: Type of thermal detector
            spatial_resolution: Spatial resolution (x, y) in mm
            
        Returns:
            Dictionary with equipment metadata
        """
        equipment_info = {
            'Manufacturer': manufacturer,
            'InstitutionName': 'Thermal Imaging Center',
            'StationName': 'THERMAL_WS'
        }
        
        if manufacturer_model:
            equipment_info['ManufacturerModelName'] = manufacturer_model
        
        if device_serial_number:
            equipment_info['DeviceSerialNumber'] = device_serial_number
        
        if software_version:
            equipment_info['SoftwareVersions'] = software_version
        
        if detector_type:
            equipment_info['DetectorType'] = detector_type
        
        if spatial_resolution:
            equipment_info['PixelSpacing'] = [str(spatial_resolution[0]), str(spatial_resolution[1])]
        
        self.standard_metadata.update(equipment_info)
        return equipment_info
    
    def set_acquisition_parameters(self,
                                 acquisition_date: Optional[Union[str, date]] = None,
                                 acquisition_time: Optional[str] = None,
                                 exposure_time: Optional[float] = None,
                                 frame_rate: Optional[float] = None,
                                 integration_time: Optional[float] = None,
                                 gain: Optional[float] = None) -> Dict[str, Any]:
        """
        Set image acquisition parameters.
        
        Args:
            acquisition_date: Acquisition date
            acquisition_time: Acquisition time
            exposure_time: Exposure time in seconds
            frame_rate: Frame rate in Hz
            integration_time: Integration time in seconds
            gain: Detector gain
            
        Returns:
            Dictionary with acquisition metadata
        """
        acq_info = {}
        
        if acquisition_date:
            if isinstance(acquisition_date, date):
                acq_info['AcquisitionDate'] = acquisition_date.strftime("%Y%m%d")
            else:
                acq_info['AcquisitionDate'] = acquisition_date
        else:
            acq_info['AcquisitionDate'] = datetime.now().strftime("%Y%m%d")
        
        if acquisition_time:
            acq_info['AcquisitionTime'] = acquisition_time
        else:
            acq_info['AcquisitionTime'] = datetime.now().strftime("%H%M%S")
        
        if exposure_time:
            acq_info['ExposureTime'] = str(exposure_time)
        
        if frame_rate:
            acq_info['FrameRate'] = str(frame_rate)
        
        if integration_time:
            acq_info['IntegrationTime'] = str(integration_time)
        
        if gain:
            acq_info['DetectorGain'] = str(gain)
        
        self.standard_metadata.update(acq_info)
        return acq_info
    
    def set_thermal_calibration_info(self,
                                   calibration_date: Optional[Union[str, datetime]] = None,
                                   calibration_method: Optional[str] = None,
                                   reference_temperature: Optional[float] = None,
                                   calibration_uncertainty: Optional[float] = None,
                                   blackbody_temperature: Optional[float] = None,
                                   calibration_coefficients: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Set thermal calibration information for traceability.
        
        Args:
            calibration_date: Date of calibration
            calibration_method: Calibration method description
            reference_temperature: Reference temperature used
            calibration_uncertainty: Measurement uncertainty in °C
            blackbody_temperature: Blackbody reference temperature
            calibration_coefficients: Calibration polynomial coefficients
            
        Returns:
            Dictionary with calibration metadata
        """
        calib_info = {}
        
        if calibration_date:
            if isinstance(calibration_date, datetime):
                calib_info['calibration_date'] = calibration_date.strftime("%Y%m%d%H%M%S")
            else:
                calib_info['calibration_date'] = calibration_date
        
        if calibration_method:
            calib_info['calibration_method'] = calibration_method
        
        if reference_temperature:
            calib_info['reference_temperature'] = reference_temperature
        
        if calibration_uncertainty:
            calib_info['calibration_uncertainty'] = calibration_uncertainty
        
        if blackbody_temperature:
            calib_info['blackbody_temperature'] = blackbody_temperature
        
        if calibration_coefficients:
            calib_info['calibration_coefficients'] = calibration_coefficients
        
        self.calibration_info.update(calib_info)
        return calib_info
    
    def set_quality_control_info(self,
                               uniformity_check: Optional[bool] = None,
                               noise_equivalent_temperature: Optional[float] = None,
                               bad_pixel_count: Optional[int] = None,
                               spatial_resolution_test: Optional[bool] = None,
                               temperature_accuracy: Optional[float] = None) -> Dict[str, Any]:
        """
        Set quality control information.
        
        Args:
            uniformity_check: Whether uniformity check passed
            noise_equivalent_temperature: NETD in °C
            bad_pixel_count: Number of bad pixels
            spatial_resolution_test: Whether spatial resolution test passed
            temperature_accuracy: Temperature measurement accuracy in °C
            
        Returns:
            Dictionary with QC metadata
        """
        qc_info = {}
        
        if uniformity_check is not None:
            qc_info['uniformity_check_passed'] = uniformity_check
        
        if noise_equivalent_temperature:
            qc_info['noise_equivalent_temperature'] = noise_equivalent_temperature
        
        if bad_pixel_count is not None:
            qc_info['bad_pixel_count'] = bad_pixel_count
        
        if spatial_resolution_test is not None:
            qc_info['spatial_resolution_test_passed'] = spatial_resolution_test
        
        if temperature_accuracy:
            qc_info['temperature_accuracy'] = temperature_accuracy
        
        self.quality_control.update(qc_info)
        return qc_info
    
    def apply_metadata_to_dataset(self, dataset: Dataset) -> Dataset:
        """
        Apply all metadata to a DICOM dataset.
        
        Args:
            dataset: DICOM dataset to update
            
        Returns:
            Updated DICOM dataset
        """
        # Apply standard metadata
        for key, value in self.standard_metadata.items():
            try:
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    # Handle sequences - create proper Dataset instances
                    sequence = []
                    for item_dict in value:
                        item_dataset = Dataset()
                        for item_key, item_value in item_dict.items():
                            setattr(item_dataset, item_key, item_value)
                        sequence.append(item_dataset)
                    setattr(dataset, key, sequence)
                else:
                    setattr(dataset, key, value)
            except Exception as e:
                # Skip problematic fields
                print(f"Warning: Could not set {key}: {e}")
                continue
        
        # Set content identification
        dataset.ContentDate = self.standard_metadata.get('StudyDate', datetime.now().strftime("%Y%m%d"))
        dataset.ContentTime = self.standard_metadata.get('StudyTime', datetime.now().strftime("%H%M%S"))
        
        # Set image type for thermal imaging
        dataset.ImageType = ["DERIVED", "SECONDARY", "THERMAL"]
        
        # Add thermal-specific processing description
        dataset.AcquisitionDeviceProcessingDescription = "Thermal Imaging Processing"
        
        return dataset
    
    def validate_metadata_completeness(self) -> Dict[str, List[str]]:
        """
        Validate metadata completeness for medical imaging standards.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'missing_required': [],
            'missing_recommended': [],
            'warnings': []
        }
        
        # Required fields for medical imaging
        required_fields = [
            'PatientName', 'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID',
            'StudyDate', 'StudyTime', 'Modality'
        ]
        
        # Recommended fields
        recommended_fields = [
            'StudyDescription', 'SeriesDescription', 'Manufacturer',
            'AcquisitionDate', 'AcquisitionTime'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in self.standard_metadata:
                validation_results['missing_required'].append(field)
        
        # Check recommended fields
        for field in recommended_fields:
            if field not in self.standard_metadata:
                validation_results['missing_recommended'].append(field)
        
        # Check for thermal-specific warnings
        if not self.thermal_parameters:
            validation_results['warnings'].append("No thermal parameters set")
        
        if not self.calibration_info:
            validation_results['warnings'].append("No calibration information provided")
        
        return validation_results
    
    def export_metadata_report(self, filepath: str):
        """
        Export comprehensive metadata report.
        
        Args:
            filepath: Output file path for the report
        """
        report = {
            'metadata_summary': {
                'creation_date': datetime.now().isoformat(),
                'standard_metadata_count': len(self.standard_metadata),
                'thermal_parameters_count': len(self.thermal_parameters),
                'calibration_info_available': bool(self.calibration_info),
                'quality_control_info_available': bool(self.quality_control)
            },
            'standard_metadata': self.standard_metadata,
            'thermal_parameters': self.thermal_parameters,
            'calibration_info': self.calibration_info,
            'quality_control': self.quality_control,
            'validation_results': self.validate_metadata_completeness()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def create_dicom_conformance_statement(self) -> Dict[str, Any]:
        """
        Create DICOM conformance statement for thermal imaging.
        
        Returns:
            Dictionary with conformance information
        """
        conformance = {
            'implementation_class_uid': self._gen_uid('implementation'),
            'implementation_version_name': 'MEDTHERMAL_DICOM_1.0',
            'supported_sop_classes': [
                {
                    'sop_class_uid': '1.2.840.10008.5.1.4.1.1.7',
                    'sop_class_name': 'Secondary Capture Image Storage'
                }
            ],
            'supported_transfer_syntaxes': [
                {
                    'transfer_syntax_uid': '1.2.840.10008.1.2.1',
                    'transfer_syntax_name': 'Explicit VR Little Endian'
                }
            ],
            'thermal_extensions': {
                'private_tag_group': '0x7FE1',
                'supported_thermal_parameters': list(self.thermal_parameters.keys()),
                'temperature_units_supported': ['Celsius', 'Fahrenheit', 'Kelvin'],
                'calibration_methods_supported': ['Blackbody', 'Reference Target', 'Multi-point']
            }
        }
        
        return conformance