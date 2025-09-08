#!/usr/bin/env python3
"""
Test suite for thermal_dicom.core module.

Tests the core ThermalDicom class functionality including:
- DICOM creation and structure
- Thermal parameters handling
- Private tags implementation
- Temperature data management
- File I/O operations
"""

import pytest
import numpy as np
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the module to test
from thermal_dicom.core import ThermalDicom


class TestThermalDicomInit:
    """Test ThermalDicom initialization."""
    
    def test_init_empty(self):
        """Test initialization with no parameters."""
        thermal_dicom = ThermalDicom()
        
        assert thermal_dicom.thermal_array is None
        assert thermal_dicom.temperature_data is None
        assert thermal_dicom.thermal_params == {}
        assert thermal_dicom.dataset is not None
        
    def test_init_with_thermal_array(self):
        """Test initialization with thermal array."""
        thermal_array = np.random.rand(100, 100)
        thermal_dicom = ThermalDicom(thermal_array=thermal_array)
        
        assert np.array_equal(thermal_dicom.thermal_array, thermal_array)
        assert thermal_dicom.temperature_data is None
        
    def test_init_with_temperature_data(self):
        """Test initialization with temperature data."""
        thermal_array = np.random.rand(100, 100)
        temperature_data = np.random.normal(37.0, 2.0, (100, 100))
        
        thermal_dicom = ThermalDicom(
            thermal_array=thermal_array,
            temperature_data=temperature_data
        )
        
        assert np.array_equal(thermal_dicom.thermal_array, thermal_array)
        assert np.array_equal(thermal_dicom.temperature_data, temperature_data)
        
    def test_init_with_thermal_params(self):
        """Test initialization with thermal parameters."""
        thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0
        }
        
        thermal_dicom = ThermalDicom(thermal_params=thermal_params)
        
        assert thermal_dicom.thermal_params == thermal_params


class TestThermalParameters:
    """Test thermal parameters handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        
    def test_set_thermal_parameters_basic(self):
        """Test setting basic thermal parameters."""
        params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.5,
            'ambient_temperature': 23.0
        }
        
        self.thermal_dicom.set_thermal_parameters(params)
        
        # Check parameters are stored
        assert self.thermal_dicom.thermal_params == params
        
        # Check private tags are set in dataset
        emissivity_tag = self.thermal_dicom.PRIVATE_TAGS['emissivity']
        distance_tag = self.thermal_dicom.PRIVATE_TAGS['distance_from_camera']
        ambient_tag = self.thermal_dicom.PRIVATE_TAGS['ambient_temperature']
        
        assert emissivity_tag in self.thermal_dicom.dataset
        assert distance_tag in self.thermal_dicom.dataset
        assert ambient_tag in self.thermal_dicom.dataset
        
        assert self.thermal_dicom.dataset[emissivity_tag].value == '0.98'
        assert self.thermal_dicom.dataset[distance_tag].value == '1.5'
        assert self.thermal_dicom.dataset[ambient_tag].value == '23.0'
        
    def test_set_thermal_parameters_all_types(self):
        """Test setting thermal parameters with different data types."""
        from datetime import datetime
        
        params = {
            'emissivity': 0.98,  # float
            'camera_model': 'FLIR E8-XT',  # string
            'calibration_date': datetime.now(),  # datetime
            'roi_temperature_stats': {'mean': 37.0, 'std': 1.5},  # dict
        }
        
        self.thermal_dicom.set_thermal_parameters(params)
        
        # Check different data types are handled correctly
        emissivity_tag = self.thermal_dicom.PRIVATE_TAGS['emissivity']
        camera_tag = self.thermal_dicom.PRIVATE_TAGS['camera_model']
        calib_tag = self.thermal_dicom.PRIVATE_TAGS['calibration_date']
        roi_tag = self.thermal_dicom.PRIVATE_TAGS['roi_temperature_stats']
        
        assert self.thermal_dicom.dataset[emissivity_tag].value == '0.98'
        assert self.thermal_dicom.dataset[camera_tag].value == 'FLIR E8-XT'
        assert calib_tag in self.thermal_dicom.dataset
        assert roi_tag in self.thermal_dicom.dataset
        
    def test_get_thermal_parameter_existing(self):
        """Test getting existing thermal parameter."""
        params = {'emissivity': 0.95}
        self.thermal_dicom.set_thermal_parameters(params)
        
        value = self.thermal_dicom.get_thermal_parameter('emissivity')
        assert value == '0.95'  # DICOM tags store as strings
        
    def test_get_thermal_parameter_nonexistent(self):
        """Test getting non-existent thermal parameter."""
        value = self.thermal_dicom.get_thermal_parameter('nonexistent')
        assert value is None
        
    def test_get_thermal_parameter_from_params_dict(self):
        """Test getting parameter from params dict when not in DICOM tags."""
        # Set parameter that's not in PRIVATE_TAGS
        self.thermal_dicom.thermal_params['custom_param'] = 'custom_value'
        
        value = self.thermal_dicom.get_thermal_parameter('custom_param')
        assert value == 'custom_value'


class TestThermalImageHandling:
    """Test thermal image data handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        self.test_array = np.random.normal(37.0, 2.0, (256, 256))
        
    def test_set_thermal_image_basic(self):
        """Test setting thermal image with basic parameters."""
        temperature_range = (self.test_array.min(), self.test_array.max())
        
        self.thermal_dicom.set_thermal_image(
            self.test_array, 
            self.test_array, 
            temperature_range
        )
        
        # Check arrays are stored
        assert np.array_equal(self.thermal_dicom.thermal_array, self.test_array)
        assert np.array_equal(self.thermal_dicom.temperature_data, self.test_array)
        
        # Check DICOM parameters are updated
        assert self.thermal_dicom.dataset.Rows == 256
        assert self.thermal_dicom.dataset.Columns == 256
        assert self.thermal_dicom.dataset.SamplesPerPixel == 1
        
        # Check temperature range is stored
        min_temp = self.thermal_dicom.get_thermal_parameter('temperature_range_min')
        max_temp = self.thermal_dicom.get_thermal_parameter('temperature_range_max')
        assert min_temp is not None
        assert max_temp is not None
        
    def test_set_thermal_image_rgb(self):
        """Test setting RGB thermal image."""
        rgb_array = np.random.rand(256, 256, 3)
        
        self.thermal_dicom.set_thermal_image(rgb_array)
        
        assert self.thermal_dicom.dataset.Rows == 256
        assert self.thermal_dicom.dataset.Columns == 256
        assert self.thermal_dicom.dataset.SamplesPerPixel == 3
        assert self.thermal_dicom.dataset.PhotometricInterpretation == "RGB"
        
    def test_set_thermal_image_scaling(self):
        """Test thermal image scaling to 16-bit."""
        # Test with float array that needs scaling
        float_array = np.random.rand(100, 100).astype(np.float32)
        
        self.thermal_dicom.set_thermal_image(float_array)
        
        # Check pixel data is set
        assert hasattr(self.thermal_dicom.dataset, 'PixelData')
        assert self.thermal_dicom.dataset.PixelData is not None
        
    def test_get_temperature_at_pixel_with_temperature_data(self):
        """Test getting temperature at pixel with temperature data."""
        temp_data = np.full((100, 100), 37.5)
        temp_data[50, 50] = 38.2  # Set specific temperature
        
        self.thermal_dicom.set_thermal_image(temp_data, temp_data)
        
        temp = self.thermal_dicom.get_temperature_at_pixel(50, 50)
        assert temp == 38.2
        
    def test_get_temperature_at_pixel_without_temperature_data(self):
        """Test getting temperature at pixel without temperature data."""
        # Set only thermal array with temperature range
        thermal_array = np.full((100, 100), 32768, dtype=np.uint16)  # Mid-range 16-bit
        temp_range = (30.0, 40.0)
        
        self.thermal_dicom.set_thermal_image(thermal_array, None, temp_range)
        
        temp = self.thermal_dicom.get_temperature_at_pixel(50, 50)
        assert temp is not None
        assert 30.0 <= temp <= 40.0
        
    def test_get_temperature_at_pixel_out_of_bounds(self):
        """Test getting temperature at out-of-bounds pixel."""
        temp_data = np.random.normal(37.0, 1.0, (100, 100))
        self.thermal_dicom.set_thermal_image(temp_data, temp_data)
        
        # Test out of bounds coordinates
        temp = self.thermal_dicom.get_temperature_at_pixel(150, 150)
        assert temp is None
        
        temp = self.thermal_dicom.get_temperature_at_pixel(-1, 50)
        assert temp is None


class TestROIAnalysis:
    """Test Region of Interest analysis."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        self.temp_data = np.random.normal(37.0, 2.0, (100, 100))
        self.thermal_dicom.set_thermal_image(self.temp_data, self.temp_data)
        
    def test_calculate_roi_statistics_basic(self):
        """Test basic ROI statistics calculation."""
        # Create simple ROI mask
        roi_mask = np.zeros((100, 100), dtype=bool)
        roi_mask[40:60, 40:60] = True  # 20x20 square
        
        stats = self.thermal_dicom.calculate_roi_statistics(roi_mask)
        
        # Check all expected statistics are present
        expected_keys = [
            'mean_temperature', 'min_temperature', 'max_temperature',
            'std_temperature', 'median_temperature', 'pixel_count'
        ]
        for key in expected_keys:
            assert key in stats
            
        # Check pixel count is correct
        assert stats['pixel_count'] == 400  # 20x20 = 400 pixels
        
    def test_calculate_roi_statistics_no_temperature_data(self):
        """Test ROI statistics without temperature data."""
        thermal_dicom = ThermalDicom()
        roi_mask = np.ones((100, 100), dtype=bool)
        
        with pytest.raises(ValueError, match="Temperature data not available"):
            thermal_dicom.calculate_roi_statistics(roi_mask)
            
    def test_calculate_roi_statistics_stored_as_private_tag(self):
        """Test that ROI statistics are stored as private tag."""
        roi_mask = np.ones((50, 50), dtype=bool)
        
        # Use smaller array for this test
        small_temp_data = np.random.normal(36.0, 1.0, (50, 50))
        self.thermal_dicom.set_thermal_image(small_temp_data, small_temp_data)
        
        stats = self.thermal_dicom.calculate_roi_statistics(roi_mask)
        
        # Check that ROI stats are stored as private tag
        roi_stats_param = self.thermal_dicom.get_thermal_parameter('roi_temperature_stats')
        assert roi_stats_param is not None


class TestDicomStructure:
    """Test DICOM structure and metadata."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        
    def test_dicom_structure_initialization(self):
        """Test that DICOM structure is properly initialized."""
        dataset = self.thermal_dicom.dataset
        
        # Check file meta information
        assert hasattr(dataset, 'file_meta')
        assert dataset.file_meta.MediaStorageSOPClassUID == "1.2.840.10008.5.1.4.1.1.7"
        assert dataset.file_meta.ImplementationVersionName == "THERMAL_DICOM_1.0"
        
        # Check patient information
        assert dataset.PatientName == "THERMAL^PATIENT"
        assert dataset.PatientID == "THERMAL001"
        
        # Check study information
        assert hasattr(dataset, 'StudyInstanceUID')
        assert dataset.StudyDescription == "Thermal Imaging Study"
        assert dataset.Modality == "TG"
        
        # Check thermal-specific metadata
        assert "THERMAL" in dataset.ImageType
        
    def test_create_standard_thermal_dicom(self):
        """Test creating standard thermal DICOM with patient info."""
        result = self.thermal_dicom.create_standard_thermal_dicom(
            patient_name="TEST^PATIENT^NAME",
            patient_id="TEST123",
            study_description="Test Thermal Study"
        )
        
        # Should return self
        assert result is self.thermal_dicom
        
        # Check updated information
        assert self.thermal_dicom.dataset.PatientName == "TEST^PATIENT^NAME"
        assert self.thermal_dicom.dataset.PatientID == "TEST123"
        assert self.thermal_dicom.dataset.StudyDescription == "Test Thermal Study"
        
        # Check thermal parameters are set
        emissivity = self.thermal_dicom.get_thermal_parameter('emissivity')
        assert emissivity == '0.98'  # Default human skin emissivity


class TestFileOperations:
    """Test file I/O operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        self.temp_data = np.random.normal(37.0, 1.0, (128, 128))
        self.thermal_dicom.set_thermal_image(self.temp_data, self.temp_data)
        
        # Set some thermal parameters
        params = {
            'emissivity': 0.95,
            'distance_from_camera': 1.2,
            'camera_model': 'Test Camera'
        }
        self.thermal_dicom.set_thermal_parameters(params)
        
    def test_save_dicom_file(self):
        """Test saving DICOM file."""
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp_file:
            try:
                self.thermal_dicom.save_dicom(tmp_file.name)
                
                # Check file was created
                assert os.path.exists(tmp_file.name)
                assert os.path.getsize(tmp_file.name) > 0
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    
    def test_save_dicom_without_pixel_data(self):
        """Test saving DICOM without pixel data (should create empty data)."""
        thermal_dicom = ThermalDicom()  # No pixel data set
        
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp_file:
            try:
                with pytest.warns(UserWarning, match="No pixel data set"):
                    thermal_dicom.save_dicom(tmp_file.name)
                    
                # Check file was created with default size
                assert thermal_dicom.dataset.Rows == 512
                assert thermal_dicom.dataset.Columns == 512
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    
    def test_load_dicom_file(self):
        """Test loading DICOM file."""
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp_file:
            try:
                # Save first
                self.thermal_dicom.save_dicom(tmp_file.name)
                
                # Load
                loaded_thermal = ThermalDicom.load_dicom(tmp_file.name)
                
                # Check loaded data
                assert loaded_thermal is not None
                assert loaded_thermal.thermal_array is not None
                assert loaded_thermal.thermal_array.shape == (128, 128)
                
                # Check thermal parameters were loaded
                assert 'emissivity' in loaded_thermal.thermal_params
                assert loaded_thermal.thermal_params['emissivity'] == '0.95'
                
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    
    def test_load_dicom_with_json_parameters(self):
        """Test loading DICOM with JSON-encoded parameters."""
        # Set complex parameter that will be JSON-encoded
        complex_param = {'mean': 37.0, 'std': 1.5, 'count': 100}
        self.thermal_dicom.set_thermal_parameters({'roi_temperature_stats': complex_param})
        
        with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp_file:
            try:
                # Save and load
                self.thermal_dicom.save_dicom(tmp_file.name)
                loaded_thermal = ThermalDicom.load_dicom(tmp_file.name)
                
                # Check complex parameter was loaded correctly
                loaded_stats = loaded_thermal.thermal_params.get('roi_temperature_stats')
                assert loaded_stats is not None
                # Should be loaded as dict (from JSON)
                if isinstance(loaded_stats, dict):
                    assert loaded_stats['mean'] == 37.0
                    assert loaded_stats['std'] == 1.5
                    assert loaded_stats['count'] == 100
                    
            finally:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)


class TestPrivateTags:
    """Test private tag functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.thermal_dicom = ThermalDicom()
        
    def test_private_tags_definition(self):
        """Test that private tags are properly defined."""
        # Check that THERMAL_GROUP is defined
        assert hasattr(ThermalDicom, 'THERMAL_GROUP')
        assert ThermalDicom.THERMAL_GROUP == 0x7FE1
        
        # Check that PRIVATE_TAGS dict exists and has expected entries
        assert hasattr(ThermalDicom, 'PRIVATE_TAGS')
        
        expected_tags = [
            'emissivity', 'distance_from_camera', 'ambient_temperature',
            'reflected_temperature', 'relative_humidity', 'camera_model'
        ]
        
        for tag_name in expected_tags:
            assert tag_name in ThermalDicom.PRIVATE_TAGS
            tag = ThermalDicom.PRIVATE_TAGS[tag_name]
            assert tag[0] == 0x7FE1  # Group should be THERMAL_GROUP
            
    def test_private_tag_storage(self):
        """Test that private tags are stored correctly in dataset."""
        params = {
            'emissivity': 0.98,
            'camera_model': 'FLIR E8-XT',
            'spectral_range': '7.5-14.0 μm'
        }
        
        self.thermal_dicom.set_thermal_parameters(params)
        
        # Check tags are in dataset
        for param_name, value in params.items():
            if param_name in ThermalDicom.PRIVATE_TAGS:
                tag = ThermalDicom.PRIVATE_TAGS[param_name]
                assert tag in self.thermal_dicom.dataset
                assert self.thermal_dicom.dataset[tag].value == str(value)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_temperature_data(self):
        """Test handling of empty temperature data."""
        thermal_dicom = ThermalDicom()
        
        # Should return None for temperature queries
        temp = thermal_dicom.get_temperature_at_pixel(0, 0)
        assert temp is None
        
    def test_invalid_roi_mask(self):
        """Test ROI analysis with invalid mask."""
        thermal_dicom = ThermalDicom()
        temp_data = np.random.normal(37.0, 1.0, (100, 100))
        thermal_dicom.set_thermal_image(temp_data, temp_data)
        
        # Empty ROI mask
        empty_mask = np.zeros((100, 100), dtype=bool)
        
        # Should handle empty ROI gracefully
        stats = thermal_dicom.calculate_roi_statistics(empty_mask)
        assert stats['pixel_count'] == 0
        
    def test_mismatched_array_shapes(self):
        """Test handling of mismatched thermal and temperature array shapes."""
        thermal_array = np.random.rand(100, 100)
        temperature_data = np.random.normal(37.0, 1.0, (50, 50))  # Different shape
        
        # Should not raise error, but store both arrays
        thermal_dicom = ThermalDicom(thermal_array, temperature_data)
        assert thermal_dicom.thermal_array.shape == (100, 100)
        assert thermal_dicom.temperature_data.shape == (50, 50)
        
    def test_very_large_temperature_values(self):
        """Test handling of extreme temperature values."""
        extreme_temps = np.array([[1000.0, -273.0], [0.0, 100.0]])
        thermal_dicom = ThermalDicom()
        
        # Should handle extreme values without error
        thermal_dicom.set_thermal_image(extreme_temps, extreme_temps)
        
        temp = thermal_dicom.get_temperature_at_pixel(0, 0)
        assert temp == 1000.0
        
        temp = thermal_dicom.get_temperature_at_pixel(0, 1)
        assert temp == -273.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])