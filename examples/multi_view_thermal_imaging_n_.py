"""
Multi-view Thermal Imaging Example

This example demonstrates how to create multiple DICOM files for different views
of the same anatomical region, with proper metadata organization and series management.
"""

import numpy as np
import os
import sys
from datetime import datetime
# Add parent directory to Python path to allow importing thermal_dicom when running examples directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from medthermal_dicom.core import MedThermalDicom
from medthermal_dicom.metadata import MedThermalMetadata
from medthermal_dicom.visualization import ThermalViewer
from scipy import io 
from PIL import Image

class MultiViewThermalImaging:
	"""
	Handles creation of multiple DICOM files for different views of the same anatomical region.
	
	This class provides methods to:
	1. Create multiple views of the same body part
	2. Organize them into proper series
	3. Maintain consistent metadata across views
	4. Generate unique identifiers for each view
	"""
	
	def __init__(self, organization_uid_prefix: str = None):
		"""
		Initialize multi-view thermal imaging handler.
		
		Args:
			organization_uid_prefix: Organization UID prefix for DICOM files
		"""
		self.organization_uid_prefix = organization_uid_prefix
		self.metadata = MedThermalMetadata(organization_uid_prefix=organization_uid_prefix)
		
	def create_breast_thermography_views(self, 
	                                   patient_name: str,
	                                   patient_id: str,
	                                   thermal_data_dict: dict,
	                                   output_dir: str = "multi_view_output") -> dict:
		"""
		Create multiple DICOM files for different breast thermography views.
		"""
		# Create output directory
		os.makedirs(output_dir, exist_ok=True)
		
		# Define breast thermography views
		breast_views = [
			{
				'view_key': 'frontal',
				'view_position': 'RL',
				'view_comment': 'Breast Frontal view',
				'image_laterality': 'F',            
			},
			{
				'view_key': 'left_obl',
				'view_position': 'O',
				'view_comment': 'Breast Left Oblique view',
				'image_laterality': 'L',            
			},
			{
				'view_key': 'right_obl',
				'view_position': 'O',
				'view_comment': 'Breast Right Oblique view',
				'image_laterality': 'R',            
			},
		]
		
		# Generate a shared StudyInstanceUID for all views using org prefix
		study_uid = self.metadata._gen_uid('study')
		
		# Create series metadata for all views with shared Study/Series UIDs
		series_metadata = self.metadata.create_multi_view_series(
			base_series_description="Breast Thermography",
			anatomical_region="breast",
			views=breast_views,
			series_number=1,
			study_instance_uid=study_uid
		)
		# Extract shared SeriesInstanceUID and FrameOfReferenceUID
		shared_series_uid = series_metadata[0]['SeriesInstanceUID']
		shared_for_uid = series_metadata[0].get('FrameOfReferenceUID')
		
		created_files = {}
		
		# Create DICOM file for each view
		for i, view_config in enumerate(breast_views):
			view_key = view_config['view_key']
			
			if view_key not in thermal_data_dict:
				print(f"Warning: No thermal data provided for view '{view_key}'")
				continue
				
			thermal_data = thermal_data_dict[view_key]
			
			# Create thermal DICOM
			thermal_dicom = MedThermalDicom(
				organization_uid_prefix=self.organization_uid_prefix
			)
			
			# Set thermal image data
			# Handle color (RGB/RGBA) vs grayscale/temperature arrays
			if thermal_data.ndim == 3:
				# If RGBA, drop alpha
				if thermal_data.shape[2] == 4:
					thermal_data = thermal_data[:, :, :3]
				thermal_dicom.set_thermal_image(thermal_data)
			else:
				# 2D array: if floats, treat as temperature matrix with range; else display-only grayscale
				if np.issubdtype(thermal_data.dtype, np.floating):
					temp_min, temp_max = float(thermal_data.min()), float(thermal_data.max())
					thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
				else:
					thermal_dicom.set_thermal_image(thermal_data)
			
			# Set thermal parameters
			thermal_params = {
				'emissivity': 0.98,  # Human skin
				'distance_from_camera': 1.0,  # 1 meter
				'ambient_temperature': 22.0,  # Room temperature
				'relative_humidity': 45.0,
				'camera_model': 'FLIR T1K',
				'calibration_date': datetime.now().strftime("%Y%m%d")
			}
			thermal_dicom.set_thermal_parameters(thermal_params)
			
			# Set patient information
			self.metadata.set_patient_information(
				patient_name=patient_name,
				patient_id=patient_id,
				patient_sex="F",
				patient_age="045Y"
			)
			
			# Set study information with shared StudyInstanceUID
			self.metadata.set_study_information(
				study_description="Breast Thermography Screening",
				study_id=f"BREAST_{patient_id}",
				referring_physician="DR^SMITH^THERMAL",
				procedure_code="breast_thermography",
				study_instance_uid=study_uid
			)
			
			# Apply series and view metadata
			series_info = series_metadata[i]
			self.metadata.standard_metadata.update(series_info)
			
			# Apply metadata to DICOM
			self.metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
			
			# Enforce shared UIDs explicitly
			thermal_dicom.dataset.StudyInstanceUID = study_uid
			thermal_dicom.dataset.SeriesInstanceUID = shared_series_uid
			if shared_for_uid:
				thermal_dicom.dataset.FrameOfReferenceUID = shared_for_uid
			thermal_dicom.dataset.SeriesNumber = "1"
			thermal_dicom.dataset.InstanceNumber = series_info.get('InstanceNumber', str(i+1))
			thermal_dicom.dataset.SeriesDescription = "Breast Thermography"
			
			# Create standard DICOM
			thermal_dicom.create_standard_thermal_dicom(
				patient_name=patient_name,
				patient_id=patient_id,
				study_description="Breast Thermography Screening"
			)
			
			# Generate filename
			filename = f"breast_thermography_{view_key}_{patient_id}.dcm"
			filepath = os.path.join(output_dir, filename)
			
			# Save DICOM file
			thermal_dicom.save_dicom(filepath)
			
			created_files[view_key] = {
				'filepath': filepath,
				'metadata': series_info,
				'thermal_dicom': thermal_dicom
			}
			
			print(f"Created DICOM for {view_key} view: {filepath}")
		
		return created_files
	
	def create_whole_body_thermography_views(self,
	                                       patient_name: str,
	                                       patient_id: str,
	                                       thermal_data_dict: dict,
	                                       output_dir: str = "whole_body_output") -> dict:
		"""
		Create multiple DICOM files for whole body thermography views.
		"""
		# Create output directory
		os.makedirs(output_dir, exist_ok=True)
		
		# Define whole body views
		whole_body_views = [
			{
				'view_key': 'anterior',
				'view_position': 'A',
				'view_comment': 'Anterior whole body view',
				'image_laterality': 'B',
				'patient_position': 'STANDING',
				'acquisition_view': 'Frontal whole body view'
			},
			{
				'view_key': 'posterior',
				'view_position': 'P',
				'view_comment': 'Posterior whole body view',
				'image_laterality': 'B',
				'patient_position': 'STANDING',
				'acquisition_view': 'Back whole body view'
			},
			{
				'view_key': 'left_lateral',
				'view_position': 'LL',
				'view_comment': 'Left lateral whole body view',
				'image_laterality': 'L',
				'patient_position': 'STANDING',
				'acquisition_view': 'Left side whole body view'
			},
			{
				'view_key': 'right_lateral',
				'view_position': 'RL',
				'view_comment': 'Right lateral whole body view',
				'image_laterality': 'R',
				'patient_position': 'STANDING',
				'acquisition_view': 'Right side whole body view'
			}
		]
		
		# Generate a shared StudyInstanceUID for all views using org prefix
		study_uid = self.metadata._gen_uid('study')
		
		# Create series metadata for all views with shared Study/Series UIDs
		series_metadata = self.metadata.create_multi_view_series(
			base_series_description="Whole Body Thermography",
			anatomical_region="whole_body",
			views=whole_body_views,
			series_number=1,
			study_instance_uid=study_uid
		)
		# Extract shared SeriesInstanceUID and FrameOfReferenceUID
		shared_series_uid = series_metadata[0]['SeriesInstanceUID']
		shared_for_uid = series_metadata[0].get('FrameOfReferenceUID')
		
		created_files = {}
		
		# Create DICOM file for each view
		for i, view_config in enumerate(whole_body_views):
			view_key = view_config['view_key']
			
			if view_key not in thermal_data_dict:
				print(f"Warning: No thermal data provided for view '{view_key}'")
				continue
				
			thermal_data = thermal_data_dict[view_key]
			
			# Create thermal DICOM
			thermal_dicom = MedThermalDicom(
				organization_uid_prefix=self.organization_uid_prefix
			)
			
			# Set thermal image data
			temp_min, temp_max = thermal_data.min(), thermal_data.max()
			thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
			
			# Set thermal parameters
			thermal_params = {
				'emissivity': 0.98,
				'distance_from_camera': 2.0,  # 2 meters for whole body
				'ambient_temperature': 22.0,
				'relative_humidity': 45.0,
				'camera_model': 'FLIR T1K',
				'calibration_date': datetime.now().strftime("%Y%m%d")
			}
			thermal_dicom.set_thermal_parameters(thermal_params)
			
			# Set patient information
			self.metadata.set_patient_information(
				patient_name=patient_name,
				patient_id=patient_id,
				patient_sex="F",
				patient_age="045Y"
			)
			
			# Set study information with shared StudyInstanceUID
			self.metadata.set_study_information(
				study_description="Whole Body Thermography Screening",
				study_id=f"WHOLEBODY_{patient_id}",
				referring_physician="DR^SMITH^THERMAL",
				procedure_code="whole_body_thermography",
				study_instance_uid=study_uid
			)
			
			# Apply series and view metadata
			series_info = series_metadata[i]
			self.metadata.standard_metadata.update(series_info)
			
			# Apply metadata to DICOM
			self.metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
			
			# Enforce shared UIDs explicitly
			thermal_dicom.dataset.StudyInstanceUID = study_uid
			thermal_dicom.dataset.SeriesInstanceUID = shared_series_uid
			if shared_for_uid:
				thermal_dicom.dataset.FrameOfReferenceUID = shared_for_uid
			thermal_dicom.dataset.SeriesNumber = "1"
			thermal_dicom.dataset.InstanceNumber = series_info.get('InstanceNumber', str(i+1))
			thermal_dicom.dataset.SeriesDescription = "Whole Body Thermography"
			
			# Create standard DICOM
			thermal_dicom.create_standard_thermal_dicom(
				patient_name=patient_name,
				patient_id=patient_id,
				study_description="Whole Body Thermography Screening"
			)
			
			# Generate filename
			filename = f"whole_body_{view_key}_{patient_id}.dcm"
			filepath = os.path.join(output_dir, filename)
			
			# Save DICOM file
			thermal_dicom.save_dicom(filepath)
			
			created_files[view_key] = {
				'filepath': filepath,
				'metadata': series_info,
				'thermal_dicom': thermal_dicom
			}
			
			print(f"Created DICOM for {view_key} view: {filepath}")
		
		return created_files
	
	def create_custom_multi_view_series(self,
	                                  patient_name: str,
	                                  patient_id: str,
	                                  anatomical_region: str,
	                                  view_configs: list,
	                                  thermal_data_dict: dict,
	                                  output_dir: str = "custom_output") -> dict:
		"""
		Create custom multi-view series for any anatomical region.
		"""
		# Create output directory
		os.makedirs(output_dir, exist_ok=True)
		
		# Generate a shared StudyInstanceUID for all views using org prefix
		study_uid = self.metadata._gen_uid('study')
		
		# Create series metadata for all views with shared Study/Series UIDs
		series_metadata = self.metadata.create_multi_view_series(
			base_series_description=f"{anatomical_region.title()} Thermography",
			anatomical_region=anatomical_region,
			views=view_configs,
			series_number=1,
			study_instance_uid=study_uid
		)
		# Extract shared SeriesInstanceUID and FrameOfReferenceUID
		shared_series_uid = series_metadata[0]['SeriesInstanceUID']
		shared_for_uid = series_metadata[0].get('FrameOfReferenceUID')
		
		created_files = {}
		
		# Create DICOM file for each view
		for i, view_config in enumerate(view_configs):
			view_key = view_config.get('view_key', f'view_{i+1}')
			
			if view_key not in thermal_data_dict:
				print(f"Warning: No thermal data provided for view '{view_key}'")
				continue
				
			thermal_data = thermal_data_dict[view_key]
			
			# Create thermal DICOM
			thermal_dicom = MedThermalDicom(
				organization_uid_prefix=self.organization_uid_prefix
			)
			
			# Set thermal image data
			temp_min, temp_max = thermal_data.min(), thermal_data.max()
			thermal_dicom.set_thermal_image(thermal_data, thermal_data, (temp_min, temp_max))
			
			# Set thermal parameters
			thermal_params = {
				'emissivity': 0.98,
				'distance_from_camera': 1.0,
				'ambient_temperature': 22.0,
				'relative_humidity': 45.0,
				'camera_model': 'FLIR T1K',
				'calibration_date': datetime.now().strftime("%Y%m%d")
			}
			thermal_dicom.set_thermal_parameters(thermal_params)
			
			# Set patient information
			self.metadata.set_patient_information(
				patient_name=patient_name,
				patient_id=patient_id,
				patient_sex="F",
				patient_age="045Y"
			)
			
			# Set study information with shared StudyInstanceUID
			self.metadata.set_study_information(
				study_description=f"{anatomical_region.title()} Thermography",
				study_id=f"{anatomical_region.upper()}_{patient_id}",
				referring_physician="DR^SMITH^THERMAL",
				procedure_code="diagnostic_thermography",
				study_instance_uid=study_uid
			)
			
			# Apply series and view metadata
			series_info = series_metadata[i]
			self.metadata.standard_metadata.update(series_info)
			
			# Apply metadata to DICOM
			self.metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
			
			# Enforce shared UIDs explicitly
			thermal_dicom.dataset.StudyInstanceUID = study_uid
			thermal_dicom.dataset.SeriesInstanceUID = shared_series_uid
			if shared_for_uid:
				thermal_dicom.dataset.FrameOfReferenceUID = shared_for_uid
			thermal_dicom.dataset.SeriesNumber = "1"
			thermal_dicom.dataset.InstanceNumber = series_info.get('InstanceNumber', str(i+1))
			thermal_dicom.dataset.SeriesDescription = f"{anatomical_region.title()} Thermography"
			
			# Create standard DICOM
			thermal_dicom.create_standard_thermal_dicom(
				patient_name=patient_name,
				patient_id=patient_id,
				study_description=f"{anatomical_region.title()} Thermography"
			)
			
			# Generate filename
			filename = f"{anatomical_region}_{view_key}_{patient_id}.dcm"
			filepath = os.path.join(output_dir, filename)
			
			# Save DICOM file
			thermal_dicom.save_dicom(filepath)
			
			created_files[view_key] = {
				'filepath': filepath,
				'metadata': series_info,
				'thermal_dicom': thermal_dicom
			}
			
			print(f"Created DICOM for {view_key} view: {filepath}")
		
		return created_files


def generate_sample_thermal_data(shape=(512, 512), base_temp=37.0, variation=2.0):
    """Generate sample thermal data for demonstration."""
    # Create base temperature array
    thermal_data = np.full(shape, base_temp)
    
    # Add some variation
    noise = np.random.normal(0, variation, shape)
    thermal_data += noise
    
    # Add some hot spots
    hot_spots = [
        (100, 100, 5.0),  # (x, y, temperature increase)
        (400, 300, 3.0),
        (250, 400, 4.0)
    ]
    
    for x, y, temp_increase in hot_spots:
        if 0 <= x < shape[0] and 0 <= y < shape[1]:
            thermal_data[x, y] += temp_increase
    
    return thermal_data


def main():
    """Demonstrate multi-view thermal imaging capabilities."""
    print("=== Multi-View Thermal Imaging Example ===\n")
    
    # Initialize multi-view handler
    multi_view = MultiViewThermalImaging(
        organization_uid_prefix="1.2.826.0.1.3680043.8.276"
    )
    
    # Patient information
    patient_name = "DOE^JANE^THERMAL"
    patient_id = "MULTI001"
    
    print("1. Creating Breast Thermography Multi-View Series")
    print("-" * 50)
    
    # Generate sample thermal data for different breast views
    # breast_thermal_data = {
    #     'frontal': generate_sample_thermal_data((512, 512), 37.0, 1.5),
    #     'lef': generate_sample_thermal_data((512, 512), 37.0, 1.8),
    #     'right_lateral': generate_sample_thermal_data((512, 512), 37.0, 1.6),
    #     'left_oblique': generate_sample_thermal_data((512, 512), 37.0, 1.7),
    #     'right_oblique': generate_sample_thermal_data((512, 512), 37.0, 1.9)
    # }
    
    # # Create breast thermography views
    # breast_files = multi_view.create_breast_thermography_views(
    #     patient_name=patient_name,
    #     patient_id=patient_id,
    #     thermal_data_dict=breast_thermal_data,
    #     output_dir="multi_view_output/breast"
    # )
    
    # print(f"\nCreated {len(breast_files)} breast thermography DICOM files")
    
    # print("\n2. Creating Whole Body Thermography Multi-View Series")
    # print("-" * 50)
    
    # # Generate sample thermal data for whole body views
    # whole_body_thermal_data = {
    #     'anterior': generate_sample_thermal_data((1024, 512), 37.0, 2.0),
    #     'posterior': generate_sample_thermal_data((1024, 512), 37.0, 2.1),
    #     'left_lateral': generate_sample_thermal_data((1024, 512), 37.0, 1.9),
    #     'right_lateral': generate_sample_thermal_data((1024, 512), 37.0, 2.0)
    # }
    
    # # Create whole body thermography views
    # whole_body_files = multi_view.create_whole_body_thermography_views(
    #     patient_name=patient_name,
    #     patient_id=patient_id,
    #     thermal_data_dict=whole_body_thermal_data,
    #     output_dir="multi_view_output/whole_body"
    # )
    
    # print(f"\nCreated {len(whole_body_files)} whole body thermography DICOM files")
    
    # print("\n3. Creating Custom Multi-View Series (Hand Thermography)")
    # print("-" * 50)
    
    # Define custom hand thermography views
    breast_view_configs = [
        {
            'view_key': 'frontal',
            'view_position': 'F',
            'view_comment': 'Breast Frontal view',
            'image_laterality': 'F',            
        },
        {
            'view_key': 'left_obl',
            'view_position': 'O',
            'view_comment': 'Breast Left Oblique view',
            'image_laterality': 'L',            
        },
        {
            'view_key': 'right_obl',
            'view_position': 'O',
            'view_comment': 'Breast Right Oblique view',
            'image_laterality': 'R',            
        },
        
    ]
    
    # Generate sample thermal data for hand views
    # breast_thermal_data = {
    #     'frontal': io.loadmat(r"D:\Bharath\work\kidwai\345\2022001832\1\front.mat")['mappedTemperatureImage'],
    #     'left_obl': io.loadmat(r"D:\Bharath\work\kidwai\345\2022001832\1\left_obl.mat")['mappedTemperatureImage'],
    #     'right_obl': io.loadmat(r"D:\Bharath\work\kidwai\345\2022001832\1\right_obl.mat")['mappedTemperatureImage']
    # }
    # breast_thermal_data = {
    #     'frontal': np.array(Image.open(r"D:\Bharath\work\therm_files\HCG\148329\front.jpg")),
    #     'left_obl': np.array(Image.open(r"D:\Bharath\work\therm_files\HCG\148329\left_obl.jpg")),
    #     'right_obl': np.array(Image.open(r"D:\Bharath\work\therm_files\HCG\148329\right_obl.jpg"))
    # }
    breast_thermal_data = {
        'frontal': np.loadtxt(r"D:\Bharath\work\therm_files\temp_csv\temp2.csv",delimiter=","),
        'left_obl': np.loadtxt(r"D:\Bharath\work\therm_files\temp_csv\temperature1.csv",delimiter=","),
        # 'right_obl': io.loadmat(r"D:\Bharath\work\kidwai\345\2022001832\1\right_obl.mat")['mappedTemperatureImage']
    }
    # Create custom hand thermography views
    # breast_files = multi_view.create_custom_multi_view_series(
    #     patient_name=patient_name,
    #     patient_id=patient_id,
    #     anatomical_region="breast",
    #     view_configs=breast_view_configs,
    #     thermal_data_dict=breast_thermal_data,
    #     output_dir="multi_view_output/breastclr"
    # )

    breast_files = multi_view.create_breast_thermography_views(
        patient_name=patient_name,
        patient_id=patient_id,
        thermal_data_dict=breast_thermal_data,
        output_dir="multi_view_output/breastclr2"
    )

    print(f"\nCreated {len(breast_files)} hand thermography DICOM files")
    
    print("\n4. Metadata Analysis")
    print("-" * 50)
    
    # Analyze metadata for one of the breast views
    if breast_files:
        sample_file = list(breast_files.values())[0]
        metadata = sample_file['metadata']
        
        print("Sample metadata for breast anterior view:")
        print(f"  Series Description: {metadata.get('SeriesDescription', 'N/A')}")
        print(f"  Series Number: {metadata.get('SeriesNumber', 'N/A')}")
        print(f"  View Position: {metadata.get('ViewPosition', 'N/A')}")
        print(f"  Image Laterality: {metadata.get('ImageLaterality', 'N/A')}")
        print(f"  View Comment: {metadata.get('ViewComment', 'N/A')}")
        print(f"  View Identifier: {metadata.get('ViewIdentifier', 'N/A')}")
        print(f"  Body Part Examined: {metadata.get('BodyPartExamined', 'N/A')}")
    
    print("\n=== Multi-View Thermal Imaging Complete ===")
    print("\nFiles created in:")
    print("  - multi_view_output/breast/")
    print("  - multi_view_output/whole_body/")
    print("  - multi_view_output/hand/")
    
    print("\nEach DICOM file contains:")
    print("  - Unique Series Instance UID")
    print("  - View-specific metadata")
    print("  - Proper anatomical region coding")
    print("  - View position and laterality information")
    print("  - Unique view identifiers")


if __name__ == "__main__":
    main() 