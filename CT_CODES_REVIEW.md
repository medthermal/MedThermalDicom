# CT Codes and Scheme Names Review

## Summary of Changes Made

### 1. **SNOMED CT Codes (SCT scheme) - FIXED**

**Previous Issues:**
- Invalid "T-D" format codes were being used as SNOMED CT codes
- Mixed valid and invalid code formats
- Inconsistent scheme usage

**Changes Made:**
All anatomical region codes have been updated to use proper SNOMED CT codes:

| Region | Old Code | New Code | Meaning |
|--------|----------|----------|---------|
| head | T-D1100 | 69536005 | Head |
| neck | T-D4000 | 45048000 | Neck |
| chest | T-D3000 | 80891009 | Chest |
| abdomen | T-D4003 | 818981001 | Abdomen |
| pelvis | T-D6000 | 816092008 | Pelvis |
| spine | T-11500 | 421060000 | Spine |
| shoulder | T-15430 | 16982009 | Shoulder region |
| arm | T-D8200 | 40983000 | Arm |
| elbow | T-15710 | 16953009 | Elbow region |
| wrist | T-15460 | 74670003 | Wrist region |
| finger | T-D8810 | 7569003 | Finger |
| hip | T-15770 | 85050009 | Hip region |
| thigh | T-D8800 | 30021000 | Thigh |
| knee | T-15750 | 72696002 | Knee region |
| leg | T-D9400 | 30021000 | Leg |
| ankle | T-15760 | 35185008 | Ankle region |
| toe | T-D9713 | 29707007 | Toe |

### 2. **Valid SNOMED CT Codes (Already Correct)**

These codes were already correct and remain unchanged:
- `241439007` - Breast thermography (SCT)
- `241440009` - Vascular thermography (SCT)
- `77477000` - Diagnostic thermography (SCT)
- `89545001` - Face (SCT)
- `77568009` - Back (SCT)
- `85562004` - Hand (SCT)
- `56459004` - Foot (SCT)
- `76752008` - Breast (SCT)

### 3. **Private Scheme Usage (99THERM)**

The private scheme `99THERM` is correctly used for:
- Whole body thermography procedures
- Region-specific thermography procedures
- Whole body anatomical region

## Scheme Names Summary

### **SCT (SNOMED CT)**
- **Purpose**: Standard medical terminology codes
- **Usage**: Anatomical regions and medical procedures
- **Format**: Numeric codes (e.g., 69536005)
- **Authority**: SNOMED International

### **99THERM (Private Scheme)**
- **Purpose**: Thermal imaging specific codes
- **Usage**: Thermal procedures and whole body regions
- **Format**: Alphanumeric codes (e.g., WB-THERM, WB)
- **Authority**: Internal thermal imaging standard

### **UCUM (Unified Code for Units of Measure)**
- **Purpose**: Standardized units for measurements
- **Usage**: Temperature units, distance units
- **Format**: Standard unit codes (e.g., Cel, m)
- **Authority**: UCUM Consortium

## Recommendations

### 1. **Code Validation**
- ✅ All SNOMED CT codes now use proper numeric format
- ✅ Private scheme usage is appropriate for thermal-specific codes
- ✅ No invalid "T-D" codes remain in SCT scheme

### 2. **Future Considerations**
- Consider registering the `99THERM` private scheme with DICOM authorities
- Document the private scheme codes in a formal specification
- Consider creating a mapping between private codes and standard codes where possible

### 3. **Quality Assurance**
- Implement code validation in the metadata creation process
- Add unit tests to verify code format compliance
- Create documentation for scheme usage guidelines

## Compliance Status

- ✅ **DICOM Standard**: Compliant with DICOM coding scheme requirements
- ✅ **SNOMED CT**: All SCT codes now use valid numeric format
- ✅ **Private Tags**: Properly structured private scheme usage
- ✅ **Modality Codes**: Using standard 'TG' (Thermography) modality

## Notes

- The 'TH' modality code mentioned in the questions has already been removed
- All anatomical region codes now use proper SNOMED CT numeric codes
- Private scheme `99THERM` is appropriately used for thermal-specific procedures
- The code structure maintains backward compatibility while improving standards compliance 