# Thermal DICOM Library - Issues & Feature Requests

This document tracks known issues, planned features, and enhancement requests for the Thermal DICOM Library.

## 🚀 Planned Features

### High Priority

#### 1. **DICOM Series Creation for Multiple Files**
- **Issue**: Currently, when multiple files are provided for the same body part, they are created as separate instances rather than a proper DICOM series
- **Request**: Implement functionality to create DICOM files in a series when multiple files for the same anatomical part are provided
- **Benefits**: 
  - Proper PACS integration
  - Better organization in DICOM viewers
  - Standard medical imaging workflow compliance
- **Implementation**: 
  - Generate shared SeriesInstanceUID for related files
  - Sequential InstanceNumber assignment
  - Consistent StudyInstanceUID across series

#### 2. **Temperature Hover Display for Color Images**
- **Issue**: When color thermal images are taken as input, temperature values are not displayed on hover
- **Request**: Add functionality to display temperature values on hover for color thermal images
- **Benefits**:
  - Better user experience for color thermal data
  - Accurate temperature reading from color-coded images
  - Enhanced visualization capabilities
- **Implementation**:
  - Color-to-temperature mapping algorithms
  - Interactive hover tooltips
  - Temperature scale calibration

#### 3. **GUI Body Part Selection**
- **Issue**: The GUI lacks functionality to accept inputs for different body parts
- **Request**: Add GUI functionality to accept and process inputs for different anatomical regions
- **Benefits**:
  - Streamlined workflow for different body parts
  - Automatic metadata configuration based on body part
  - Reduced manual input requirements
- **Implementation**:
  - Body part selection dropdown
  - Automatic view position suggestions
  - Pre-configured thermal parameters per body part

#### 4. **Metadata Tags and SNOMED-CT Code Verification**
- **Issue**: Need to verify and validate metadata tags and SNOMED-CT codes for medical compliance
- **Request**: Implement comprehensive validation of metadata tags and SNOMED-CT codes
- **Benefits**:
  - Medical standards compliance
  - Reduced errors in clinical workflows
  - Better integration with medical systems
- **Implementation**:
  - SNOMED-CT code validation
  - DICOM tag verification
  - Medical terminology compliance checking

#### 5. **Annotation Layer in DICOM Files**
- **Issue**: No support for adding annotation layers to DICOM files
- **Request**: Add functionality to include annotation layers in DICOM files
- **Benefits**:
  - Clinical documentation capabilities
  - ROI marking and measurement tools
  - Enhanced clinical reporting
- **Implementation**:
  - DICOM annotation overlay support
  - ROI drawing and measurement tools
  - Text annotation capabilities

## 🔧 Technical Improvements

### Medium Priority

#### 6. **Enhanced Error Handling**
- Improve error messages and user feedback
- Add validation for input file formats
- Better handling of corrupted or invalid data

#### 7. **Performance Optimization**
- Optimize large file processing
- Memory usage improvements
- Faster DICOM creation for batch processing

#### 8. **Additional File Format Support**
- Support for more thermal camera formats
- Raw thermal data import
- Integration with popular thermal imaging software

#### 9. **Advanced Visualization Features**
- 3D thermal visualization
- Time-series thermal imaging
- Comparative analysis tools

#### 10. **Quality Control Features**
- Image quality assessment
- Calibration verification tools
- Automated quality checks

## 🐛 Known Issues

### Current Limitations

1. **File Format Support**
   - Limited support for proprietary thermal camera formats
   - Some color thermal images may not display temperature values correctly

2. **GUI Limitations**
   - No body part-specific configuration
   - Limited batch processing capabilities
   - No preview of thermal data before DICOM creation

3. **Metadata Validation**
   - Incomplete SNOMED-CT code validation
   - Some DICOM tags may not be fully compliant with latest standards

4. **Performance**
   - Large files may take longer to process
   - Memory usage could be optimized for batch operations

## 📋 Feature Request Guidelines

### How to Submit a Feature Request

1. **Check Existing Issues**: Review this document and existing GitHub issues
2. **Provide Details**: Include:
   - Clear description of the feature
   - Use case and benefits
   - Expected behavior
   - Any relevant examples or mockups

3. **Priority Level**: Indicate if this is:
   - Critical (blocks current workflow)
   - High (significant improvement)
   - Medium (nice to have)
   - Low (future consideration)

### Feature Request Template

```markdown
## Feature Request: [Feature Name]

### Description
[Clear description of the requested feature]

### Use Case
[Describe the specific use case and why this feature is needed]

### Expected Behavior
[Describe how the feature should work]

### Benefits
[List the benefits this feature would provide]

### Priority
[Critical/High/Medium/Low]

### Additional Context
[Any additional information, examples, or references]
```

## 🎯 Roadmap

### Version 2.0 (Planned)
- DICOM series creation for multiple files
- Temperature hover display for color images
- Enhanced GUI with body part selection
- SNOMED-CT code validation

### Version 2.1 (Future)
- Annotation layer support
- Advanced visualization features
- Performance optimizations
- Additional file format support

### Version 3.0 (Long-term)
- 3D thermal visualization
- AI-powered analysis tools
- Cloud integration
- Advanced clinical workflow support

## 🤝 Contributing

We welcome contributions to address these issues and implement new features. Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

### Development Priorities

1. **DICOM Series Support** - Critical for medical workflow
2. **Color Image Temperature Display** - Important for user experience
3. **GUI Enhancements** - Improves usability
4. **Metadata Validation** - Ensures medical compliance
5. **Annotation Support** - Enables clinical documentation

## 📞 Support

For questions about these issues or to discuss implementation approaches:

- **GitHub Issues**: [Create an issue](https://github.com/thermal-dicom/thermal-dicom/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thermal-dicom/thermal-dicom/discussions)
- **Email**: support@thermal-dicom.org

---

*Last updated: December 2024*
*This document is regularly updated as issues are resolved and new features are planned.*
