import numpy as np
from thermal_dicom import ThermalDicom, ThermalViewer
from scipy import io 
import cv2 
from PIL import Image 
 
# Create sample thermal data
#temperature_data = np.random.normal(37.0, 2.0, (512, 512))  # Body temperature simulation

temperature_data = io.loadmat(r"D:\Bharath\work\kidwai\345\2022001832\1\front.mat")['mappedTemperatureImage']
#temperature_data = cv2.imread(r"D:\Bharath\work\therm_files\HCG\148329\front.jpg")
#temperature_data = np.array(Image.open(r"D:\Bharath\work\therm_files\HCG\148329\front.jpg"))
#pallette = cv2.imread(r"D:\Bharath\work\DICOM\pcsps\colorbar_medi.jpg") 
#print("test:",temperature_data[183,61])
# Create thermal DICOM with organization UID (optional)
# Replace with your actual organization UID prefix
organization_uid = "1.2.826.0.1.3680043.8.276"  # Example UID - change this!

# Create thermal DICOM
thermal_dicom = ThermalDicom(organization_uid_prefix=organization_uid)

# Display UID information
uid_info = thermal_dicom.get_organization_uid_info()
print(f"Organization UID prefix: {uid_info['organization_uid_prefix']}")
print(f"Using custom UIDs: {uid_info['is_using_custom_uids']}")
print("Generated UIDs:")
for uid_type, uid_value in uid_info['current_uids'].items():
    if uid_value:
        print(f"  {uid_type}: {uid_value}")

#thermal_dicom.set_thermal_image(temperature_data)
thermal_dicom.set_thermal_image(temperature_data, temperature_data, (temperature_data.min(), temperature_data.max()))

# Set thermal parameters
thermal_params = {
    'emissivity': 0.98,           # Human skin emissivity
    'distance_from_camera': 1.0,  # 1 meter from camera
    'ambient_temperature': 22.0,  # Room temperature
    'relative_humidity': 45.0,    # 45% humidity
    'camera_model': 'FLIR E8-XT'
}
thermal_dicom.set_thermal_parameters(thermal_params)

# Create standard medical thermal DICOM
thermal_dicom.create_standard_thermal_dicom(
    patient_name="DOE^JOHN^",
    patient_id="THERM001",
    study_description="Medical Thermal Imaging"
)

# Save DICOM file
thermal_dicom.save_dicom('thermal_image_gs.dcm')

# Create interactive visualization
viewer = ThermalViewer(thermal_dicom)
fig = viewer.create_interactive_plot(title="Interactive Thermal Image")

# Get temperature at specific pixel (with hover functionality)
print(temperature_data.shape)
#r,c,*_ = temperature_data.shape
#temp = thermal_dicom.get_temperature_at_pixel(r//2, c//2)
#print(f"Temperature at center: {temp:.2f}°C")


### Interactive Dashboard

#```python
# Launch interactive web dashboard
# app = viewer.create_dashboard_app()
# app.run(debug=True)