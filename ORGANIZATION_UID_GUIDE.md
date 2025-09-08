# Organization UID Guide for Thermal DICOM Library

This guide explains how to use organization unique IDs (UIDs) with your thermal DICOM system. The system automatically generates all DICOM UIDs using your organization prefix, or falls back to standard PyDICOM UID generation if no prefix is provided.

## 🎯 What Are Organization UIDs?

Organization UIDs are unique identifiers that follow the DICOM standard format. They allow you to:
- **Identify your organization** in DICOM files
- **Ensure uniqueness** across your DICOM system
- **Maintain traceability** of your medical images
- **Comply with DICOM standards** for medical imaging

## 🚀 How to Use Organization UIDs

### Option 1: Set During Creation (Recommended)

```python
from thermal_dicom import ThermalDicom

# Your organization UID prefix (replace with your actual UID)
org_uid = "1.2.826.0.1.3680043.8.498"

# Create thermal DICOM with organization UID
thermal_dicom = ThermalDicom(organization_uid_prefix=org_uid)

# All DICOM UIDs will automatically use your organization prefix
uid_info = thermal_dicom.get_organization_uid_info()
print(f"Using organization UID: {uid_info['organization_uid_prefix']}")
```

### Option 2: Set After Creation

```python
# Create thermal DICOM first
thermal_dicom = ThermalDicom()

# Set organization UID later
thermal_dicom.set_organization_uid_prefix("1.2.826.0.1.3680043.8.498")

# UIDs will be regenerated with the new prefix
uid_info = thermal_dicom.get_organization_uid_info()
print(f"Updated organization UID: {uid_info['organization_uid_prefix']}")
```

### Option 3: Use CLI with Organization UID

```bash
# Create thermal DICOM with organization UID via command line
thermal-dicom-viewer create temp_data.npy output.dcm \
    --organization-uid "1.2.826.0.1.3680043.8.498" \
    --patient-name "DOE^JOHN"
```

## 🔧 Automatic UID Generation

When you provide an organization UID, the system automatically generates:

| UID Type | Description | Example |
|----------|-------------|---------|
| **Study Instance UID** | Unique study identifier | `1.2.826.0.1.3680043.8.498.3.1703123456789.123456789` |
| **Series Instance UID** | Unique series identifier | `1.2.826.0.1.3680043.8.498.2.1703123456789.123456789` |
| **SOP Instance UID** | Unique image identifier | `1.2.826.0.1.3680043.8.498.1.1703123456789.123456789` |
| **Implementation Class UID** | Software identifier | `1.2.826.0.1.3680043.8.498.4.1703123456789.123456789` |

## 📋 UID Format Requirements

Your organization UID must follow DICOM standards:

✅ **Valid Format:**
- Numbers separated by dots
- Maximum 64 characters total
- Each component is a positive integer
- No consecutive dots
- No leading/trailing dots

❌ **Invalid Examples:**
- `1.2.826.0.1.3680043.8.498.` (trailing dot)
- `1.2.826.0.1.3680043..8.498` (consecutive dots)
- `1.2.826.0.1.3680043.8.498a` (contains letter)
- `1.2.826.0.1.3680043.8.-498` (negative number)

## 🔄 Fallback to Standard UIDs

If no organization UID is provided, the system automatically uses standard PyDICOM UID generation:

```python
# No organization UID - uses standard generation
thermal_dicom = ThermalDicom()

uid_info = thermal_dicom.get_organization_uid_info()
print(f"Organization UID: {uid_info['organization_uid_prefix']}")  # None
print(f"Using custom UIDs: {uid_info['is_using_custom_uids']}")   # False
```

## 🛠️ UID Validation

The system includes built-in UID validation:

```python
from thermal_dicom.utils import validate_organization_uid

# Validate your organization UID
org_uid = "1.2.826.0.1.3680043.8.498"
is_valid, message = validate_organization_uid(org_uid)

if is_valid:
    print(f"✓ UID is valid: {message}")
else:
    print(f"✗ UID is invalid: {message}")
```

## 📊 UID Information and Management

### Get Current UID Information

```python
uid_info = thermal_dicom.get_organization_uid_info()

print(f"Organization UID prefix: {uid_info['organization_uid_prefix']}")
print(f"Using custom UIDs: {uid_info['is_using_custom_uids']}")
print("Current UIDs:")
for uid_type, uid_value in uid_info['current_uids'].items():
    if uid_value:
        print(f"  {uid_type}: {uid_value}")
```

### Change Organization UID

```python
# Change to a different organization UID
new_org_uid = "1.2.826.0.1.3680043.8.499"
thermal_dicom.set_organization_uid_prefix(new_org_uid)

# All UIDs will be regenerated automatically
uid_info = thermal_dicom.get_organization_uid_info()
print(f"Updated to: {uid_info['organization_uid_prefix']}")
```

## 🏥 Medical Imaging Compliance

### DICOM Standards
- **Full DICOM compliance** with your organization UIDs
- **PACS integration** ready
- **Medical imaging standards** compliance
- **Quality control** metadata tracking

### Clinical Workflow
- **Patient data management** with unique identifiers
- **Study and series organization** using your UIDs
- **Clinical reporting** with traceable images
- **Quality assurance** protocols

## 📝 Example Workflow

### Complete Example with Organization UID

```python
import numpy as np
from thermal_dicom import ThermalDicom

# 1. Set your organization UID
org_uid = "1.2.826.0.1.3680043.8.498"  # Replace with your actual UID

# 2. Create thermal DICOM with organization UID
thermal_dicom = ThermalDicom(organization_uid_prefix=org_uid)

# 3. Create sample thermal data
temperature_data = np.random.normal(37.0, 2.0, (256, 256))

# 4. Set thermal image and parameters
thermal_dicom.set_thermal_image(temperature_data, temperature_data, (30.0, 45.0))
thermal_dicom.set_thermal_parameters({
    'emissivity': 0.98,
    'distance_from_camera': 1.0,
    'ambient_temperature': 22.0,
})

# 5. Create standard medical DICOM
thermal_dicom.create_standard_thermal_dicom(
    patient_name="DOE^JOHN^",
    patient_id="THERM001",
    study_description="Medical Thermal Imaging"
)

# 6. Display UID information
uid_info = thermal_dicom.get_organization_uid_info()
print(f"✓ Using organization UID: {uid_info['organization_uid_prefix']}")
print(f"✓ Custom UIDs enabled: {uid_info['is_using_custom_uids']}")

# 7. Save DICOM file
thermal_dicom.save_dicom('thermal_with_org_uid.dcm')
print("✓ DICOM saved with organization UIDs")
```

## 🚨 Important Notes

### 1. **Register Your UID**
- Contact your DICOM authority to get a unique organization UID
- Ensure your UID is not already in use
- Keep documentation of your UID assignment

### 2. **UID Persistence**
- Organization UID information is preserved when saving/loading DICOM files
- UIDs are automatically regenerated when changing organization UID
- All DICOM UIDs maintain consistency within your organization

### 3. **Fallback Behavior**
- If no organization UID is provided, standard PyDICOM UIDs are used
- This ensures compatibility and prevents errors
- You can always add organization UIDs later

### 4. **Validation**
- Always validate your organization UID format
- Test UID generation with your actual prefix
- Verify UID uniqueness in your DICOM system

## 🔍 Troubleshooting

### Common Issues

**1. UID too long**
```
Error: UID length exceeds DICOM limit of 64 characters
```
**Solution:** Use a shorter organization UID prefix

**2. Invalid UID format**
```
Error: Invalid organization UID prefix
```
**Solution:** Ensure UID contains only numbers and dots, no consecutive dots

**3. UIDs not updating**
```
Problem: UIDs remain the same after changing organization UID
```
**Solution:** UIDs are automatically regenerated when calling `set_organization_uid_prefix()`

### Getting Help

- Check the example files: `examples/organization_uid_example.py`
- Run the test file: `test_organization_uid.py`
- Review the CLI help: `thermal-dicom-viewer create --help`

## 📚 Additional Resources

- **DICOM Standard**: [DICOM UID Guidelines](https://dicom.nema.org/dicom/2013/output/chtml/part05/chapter_B.html)
- **Organization UID Registration**: Contact your local DICOM authority
- **Example Code**: See `examples/organization_uid_example.py`
- **Configuration**: See `CONFIGURATION_GUIDE.md` for advanced setup

---

**Your thermal DICOM system is now ready to use organization UIDs for professional medical imaging applications!**
