#!/usr/bin/env python3
"""
Command Line Interface for Thermal DICOM Library.

Provides command-line tools for thermal DICOM processing, visualization, and analysis.
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
from thermal_dicom import ThermalDicom, ThermalViewer, ThermalMetadata
from thermal_dicom.utils import ThermalCalibrator, ThermalROIAnalyzer


def _load_custom_palette(palette_arg: str) -> np.ndarray:
    """Load a custom palette.
    Accepts:
      - Matplotlib colormap name (e.g., 'jet')
      - Path to JSON/CSV/NPY containing Nx3 or Nx4 colors in 0-1 or 0-255
    Returns Nx3 float array in [0,1].
    """
    import os
    import json
    import numpy as np
    import matplotlib.cm as mcm
    from matplotlib.colors import LinearSegmentedColormap

    if os.path.exists(palette_arg):
        path = palette_arg
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.json', '.jsn']:
            with open(path, 'r') as f:
                data = json.load(f)
            # Accept list of hex strings or list of RGB(A)
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], str):
                    # hex list
                    import matplotlib.colors as mcolors
                    colors = np.array([mcolors.to_rgb(c) for c in data], dtype=float)
                else:
                    colors = np.array(data, dtype=float)
            else:
                raise ValueError('Invalid JSON palette format')
        elif ext in ['.csv', '.txt']:
            import pandas as pd
            df = pd.read_csv(path, header=None)
            colors = df.values.astype(float)
        elif ext in ['.npy']:
            colors = np.load(path).astype(float)
        else:
            raise ValueError(f'Unsupported palette file extension: {ext}')

        if colors.shape[1] == 4:
            colors = colors[:, :3]
        if colors.max() > 1.0:
            colors = colors / 255.0
        if colors.min() < 0.0 or colors.max() > 1.0:
            raise ValueError('Palette values must be in [0,1] after normalization')
        return colors
    else:
        # Treat as matplotlib colormap name
        try:
            cmap = mcm.get_cmap(palette_arg)
        except Exception:
            raise ValueError(f"Unknown palette or file not found: {palette_arg}")
        # Sample to 256 colors
        xs = np.linspace(0, 1, 256)
        colors = np.asarray(cmap(xs))[..., :3]
        return colors


def create_thermal_dicom_cli(args):
    """Create thermal DICOM from temperature data file."""
    print(f"Creating thermal DICOM from: {args.input}")
    
    # Load temperature data
    if args.input.endswith('.npy'):
        temp_data = np.load(args.input)
    elif args.input.endswith('.csv'):
        import pandas as pd
        df = pd.read_csv(args.input)
        if 'Temperature' in df.columns:
            # Assume CSV has Row, Column, Temperature columns
            rows = df['Row'].max() + 1
            cols = df['Column'].max() + 1
            temp_data = np.zeros((rows, cols))
            temp_data[df['Row'], df['Column']] = df['Temperature']
        else:
            temp_data = df.values
    elif args.input.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')):
        from PIL import Image
        img = Image.open(args.input).convert('RGB')
        img_np = np.array(img)
        # Treat as color input; no temperature values
        temp_data = None
        color_image = img_np
    else:
        print(f"Unsupported input format: {args.input}")
        return 1
    
    # Initialize DICOM
    thermal_dicom = ThermalDicom(organization_uid_prefix=args.organization_uid)
    
    if 'color_image' in locals():
        print(f"Loaded color image: {color_image.shape[1]} x {color_image.shape[0]}")
        # Optional: apply palette mapping is not applicable; we already have RGB
        thermal_dicom.set_thermal_image(color_image, temperature_data=None, temperature_range=None)
        # When color input is used, do not set temperature parameters or display values
    else:
        print(f"Loaded temperature data: {temp_data.shape}")
        print(f"Temperature range: {temp_data.min():.2f}°C to {temp_data.max():.2f}°C")
        # If user provides a custom palette, bake it into RGB (optionally keep temperatures)
        if args.palette:
            print(f"Applying custom palette: {args.palette}")
            try:
                palette = _load_custom_palette(args.palette)
            except Exception as e:
                print(f"❌ Failed to load palette: {e}")
                return 1
            # Normalize and map to colors
            mn, mx = float(temp_data.min()), float(temp_data.max())
            denom = (mx - mn) if (mx > mn) else 1.0
            norm = ((temp_data - mn) / denom).clip(0, 1)
            # Sample palette (palette is Nx3); index via 0..N-1
            idx = np.rint(norm * (len(palette) - 1)).astype(int)
            rgb = (palette[idx] * 255.0).astype(np.uint8)
            if args.keep_temperatures:
                # Save RGB but retain temperatures in dataset for analysis/hover
                thermal_dicom.set_thermal_image(rgb, temperature_data=temp_data, temperature_range=(mn, mx))
            else:
                # Save RGB only; no temps will be displayed
                thermal_dicom.set_thermal_image(rgb)
        else:
            temp_range = (temp_data.min(), temp_data.max())
            thermal_dicom.set_thermal_image(temp_data, temp_data, temp_range)
    
    # Display UID information
    if args.organization_uid:
        uid_info = thermal_dicom.get_organization_uid_info()
        print(f"Using organization UID prefix: {uid_info['organization_uid_prefix']}")
        print(f"Generated UIDs:")
        for uid_type, uid_value in uid_info['current_uids'].items():
            if uid_value:
                print(f"  {uid_type}: {uid_value}")
    else:
        print("Using standard PyDICOM UID generation")
    
    # Set thermal parameters
    if 'color_image' not in locals():
        # Only set thermal parameters when we're working with temperature matrices
        if not args.palette or args.keep_temperatures:
            thermal_params = {
                'emissivity': args.emissivity,
                'distance_from_camera': args.distance,
                'ambient_temperature': args.ambient_temp,
                'relative_humidity': args.humidity,
            }
            if args.camera_model:
                thermal_params['camera_model'] = args.camera_model
            thermal_dicom.set_thermal_parameters(thermal_params)
    
    # Create standard thermal DICOM
    thermal_dicom.create_standard_thermal_dicom(
        patient_name=args.patient_name or "THERMAL^PATIENT",
        patient_id=args.patient_id or "THERM001",
        study_description=args.study_description or "Thermal Imaging Study"
    )
    
    # Save DICOM
    thermal_dicom.save_dicom(args.output)
    print(f"✓ Thermal DICOM saved to: {args.output}")
    
    return 0


def visualize_thermal_dicom_cli(args):
    """Visualize thermal DICOM file."""
    print(f"Visualizing thermal DICOM: {args.input}")
    
    # Load thermal DICOM
    thermal_dicom = ThermalDicom.load_dicom(args.input)
    
    # Create viewer
    viewer = ThermalViewer(thermal_dicom)
    viewer.current_colormap = args.colormap
    
    if args.interactive:
        # Launch interactive dashboard
        print("Starting interactive dashboard...")
        app = viewer.create_dashboard_app(port=args.port)
        print(f"Dashboard available at: http://localhost:{args.port}")
        app.run_server(debug=args.debug, host='0.0.0.0', port=args.port)
    else:
        # Create static visualization
        fig = viewer.create_interactive_plot(
            width=args.width,
            height=args.height,
            title=f"Thermal DICOM: {Path(args.input).name}"
        )
        
        # Save visualization
        output_path = args.output or f"{Path(args.input).stem}_visualization.html"
        fig.write_html(output_path)
        print(f"✓ Visualization saved to: {output_path}")
    
    return 0


def analyze_thermal_dicom_cli(args):
    """Analyze thermal DICOM file."""
    print(f"Analyzing thermal DICOM: {args.input}")
    
    # Load thermal DICOM
    thermal_dicom = ThermalDicom.load_dicom(args.input)
    
    if thermal_dicom.temperature_data is None:
        print("❌ No temperature data available in DICOM file")
        return 1
    
    temp_data = thermal_dicom.temperature_data
    
    # Basic statistics
    stats = {
        'shape': temp_data.shape,
        'mean_temperature': float(np.mean(temp_data)),
        'median_temperature': float(np.median(temp_data)),
        'std_temperature': float(np.std(temp_data)),
        'min_temperature': float(np.min(temp_data)),
        'max_temperature': float(np.max(temp_data)),
        'temperature_range': float(np.max(temp_data) - np.min(temp_data))
    }
    
    print("📊 Temperature Statistics:")
    print(f"  Image size: {stats['shape'][1]} x {stats['shape'][0]} pixels")
    print(f"  Mean temperature: {stats['mean_temperature']:.2f}°C")
    print(f"  Median temperature: {stats['median_temperature']:.2f}°C")
    print(f"  Standard deviation: {stats['std_temperature']:.2f}°C")
    print(f"  Min temperature: {stats['min_temperature']:.2f}°C")
    print(f"  Max temperature: {stats['max_temperature']:.2f}°C")
    print(f"  Temperature range: {stats['temperature_range']:.2f}°C")
    
    # Thermal parameters
    print("\n🌡️ Thermal Parameters:")
    for param_name in ['emissivity', 'distance_from_camera', 'ambient_temperature', 
                      'relative_humidity', 'camera_model']:
        value = thermal_dicom.get_thermal_parameter(param_name)
        if value is not None:
            print(f"  {param_name}: {value}")
    
    # ROI analysis if specified
    if args.roi_center and args.roi_radius:
        print(f"\n🎯 ROI Analysis:")
        roi_analyzer = ThermalROIAnalyzer()
        
        center = tuple(map(int, args.roi_center.split(',')))
        roi_mask = roi_analyzer.create_circular_roi(
            center=center,
            radius=args.roi_radius,
            image_shape=temp_data.shape
        )
        
        roi_stats = thermal_dicom.calculate_roi_statistics(roi_mask)
        print(f"  ROI center: {center}")
        print(f"  ROI radius: {args.roi_radius} pixels")
        print(f"  ROI mean temperature: {roi_stats['mean_temperature']:.2f}°C")
        print(f"  ROI max temperature: {roi_stats['max_temperature']:.2f}°C")
        print(f"  ROI min temperature: {roi_stats['min_temperature']:.2f}°C")
        print(f"  ROI std deviation: {roi_stats['std_temperature']:.2f}°C")
        print(f"  ROI pixel count: {roi_stats['pixel_count']}")
        
        stats['roi_analysis'] = roi_stats
    
    # Save analysis results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        print(f"\n✓ Analysis results saved to: {args.output}")
    
    return 0


def convert_thermal_data_cli(args):
    """Convert thermal data between formats."""
    print(f"Converting thermal data: {args.input} -> {args.output}")
    
    # Load input data
    if args.input.endswith('.dcm'):
        thermal_dicom = ThermalDicom.load_dicom(args.input)
        if thermal_dicom.temperature_data is None:
            print("❌ No temperature data in DICOM file")
            return 1
        temp_data = thermal_dicom.temperature_data
    elif args.input.endswith('.npy'):
        temp_data = np.load(args.input)
    else:
        print(f"Unsupported input format: {args.input}")
        return 1
    
    # Save output data
    if args.output.endswith('.npy'):
        np.save(args.output, temp_data)
    elif args.output.endswith('.csv'):
        import pandas as pd
        rows, cols = temp_data.shape
        row_indices, col_indices = np.meshgrid(range(rows), range(cols), indexing='ij')
        
        df = pd.DataFrame({
            'Row': row_indices.flatten(),
            'Column': col_indices.flatten(),
            'Temperature': temp_data.flatten()
        })
        df.to_csv(args.output, index=False)
    elif args.output.endswith('.dcm'):
        # Convert to DICOM
        thermal_dicom = ThermalDicom()
        temp_range = (temp_data.min(), temp_data.max())
        thermal_dicom.set_thermal_image(temp_data, temp_data, temp_range)
        
        # Set basic thermal parameters
        thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0,
        }
        thermal_dicom.set_thermal_parameters(thermal_params)
        
        thermal_dicom.create_standard_thermal_dicom(
            patient_name="CONVERTED^PATIENT",
            patient_id="CONV001",
            study_description="Converted Thermal Data"
        )
        
        thermal_dicom.save_dicom(args.output)
    else:
        print(f"Unsupported output format: {args.output}")
        return 1
    
    print(f"✓ Data converted successfully")
    return 0


def validate_thermal_dicom_cli(args):
    """Validate thermal DICOM file."""
    print(f"Validating thermal DICOM: {args.input}")
    
    try:
        # Load thermal DICOM
        thermal_dicom = ThermalDicom.load_dicom(args.input)
        print("✓ DICOM file loaded successfully")
        
        # Check basic DICOM structure
        dataset = thermal_dicom.dataset
        required_fields = ['PatientName', 'PatientID', 'StudyInstanceUID', 
                          'SeriesInstanceUID', 'SOPInstanceUID']
        
        missing_fields = []
        for field in required_fields:
            if not hasattr(dataset, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️ Missing required DICOM fields: {missing_fields}")
        else:
            print("✓ All required DICOM fields present")
        
        # Check thermal-specific elements
        thermal_fields_found = 0
        for param_name in thermal_dicom.PRIVATE_OFFSETS:
            if thermal_dicom.get_thermal_parameter(param_name) is not None:
                thermal_fields_found += 1
        
        print(f"✓ Found {thermal_fields_found} thermal parameters")
        
        # Check image data
        if hasattr(dataset, 'PixelData') and dataset.PixelData:
            print("✓ Pixel data present")
            if thermal_dicom.thermal_array is not None:
                shape = thermal_dicom.thermal_array.shape
                print(f"✓ Image dimensions: {shape[1]} x {shape[0]}")
        else:
            print("⚠️ No pixel data found")
        
        # Check temperature data
        if thermal_dicom.temperature_data is not None:
            temp_data = thermal_dicom.temperature_data
            print("✓ Temperature data available")
            print(f"  Temperature range: {temp_data.min():.2f}°C to {temp_data.max():.2f}°C")
        else:
            print("⚠️ No temperature data available")
        
        print("\n📋 Validation Summary:")
        if not missing_fields and thermal_fields_found > 0:
            print("✅ DICOM file is valid for thermal imaging")
        else:
            print("⚠️ DICOM file has validation warnings")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Thermal DICOM Library - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create thermal DICOM from numpy array
  thermal-dicom-viewer create temp_data.npy output.dcm --patient-name "DOE^JOHN"
  
  # Create thermal DICOM with organization UID
  thermal-dicom-viewer create temp_data.npy output.dcm --organization-uid "1.2.826.0.1.3680043.8.498"
  
  # Visualize thermal DICOM interactively
  thermal-dicom-viewer visualize thermal.dcm --interactive --port 8050
  
  # Analyze thermal DICOM with ROI
  thermal-dicom-viewer analyze thermal.dcm --roi-center 256,256 --roi-radius 50
  
  # Convert between formats
  thermal-dicom-viewer convert thermal.dcm output.csv
  
  # Validate thermal DICOM
  thermal-dicom-viewer validate thermal.dcm
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create thermal DICOM from data')
    create_parser.add_argument('input', help='Input file (.npy, .csv, or color image .png/.jpg/.tiff)')
    create_parser.add_argument('output', help='Output DICOM file path')
    create_parser.add_argument('--patient-name', help='Patient name (DICOM format)')
    create_parser.add_argument('--patient-id', help='Patient ID')
    create_parser.add_argument('--study-description', help='Study description')
    create_parser.add_argument('--emissivity', type=float, default=0.98, 
                              help='Object emissivity (default: 0.98)')
    create_parser.add_argument('--distance', type=float, default=1.0,
                              help='Distance from camera in meters (default: 1.0)')
    create_parser.add_argument('--ambient-temp', type=float, default=22.0,
                              help='Ambient temperature in Celsius (default: 22.0)')
    create_parser.add_argument('--humidity', type=float, default=45.0,
                              help='Relative humidity percentage (default: 45.0)')
    create_parser.add_argument('--camera-model', help='Thermal camera model')
    create_parser.add_argument('--organization-uid', help='Organization UID prefix for DICOM UIDs (e.g., "1.2.826.0.1.3680043.8.498")')
    create_parser.add_argument('--palette', help='Custom palette: matplotlib name (e.g., jet) or path to JSON/CSV/NPY with Nx3/4 colors')
    create_parser.add_argument('--keep-temperatures', action='store_true', help='When using --palette, also keep temperature data for analysis')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Visualize thermal DICOM')
    viz_parser.add_argument('input', help='Input DICOM file path')
    viz_parser.add_argument('--output', help='Output visualization file path')
    viz_parser.add_argument('--interactive', action='store_true',
                           help='Launch interactive dashboard')
    viz_parser.add_argument('--port', type=int, default=8050,
                           help='Port for interactive dashboard (default: 8050)')
    viz_parser.add_argument('--colormap', default='jet',
                           choices=['jet', 'hot', 'cool', 'viridis', 'plasma', 'inferno'],
                           help='Thermal colormap (default: jet)')
    viz_parser.add_argument('--width', type=int, default=800,
                           help='Visualization width (default: 800)')
    viz_parser.add_argument('--height', type=int, default=600,
                           help='Visualization height (default: 600)')
    viz_parser.add_argument('--debug', action='store_true',
                           help='Enable debug mode for dashboard')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze thermal DICOM')
    analyze_parser.add_argument('input', help='Input DICOM file path')
    analyze_parser.add_argument('--output', help='Output analysis results (JSON)')
    analyze_parser.add_argument('--roi-center', help='ROI center coordinates (row,col)')
    analyze_parser.add_argument('--roi-radius', type=int, help='ROI radius in pixels')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert thermal data formats')
    convert_parser.add_argument('input', help='Input file path')
    convert_parser.add_argument('output', help='Output file path')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate thermal DICOM')
    validate_parser.add_argument('input', help='Input DICOM file path')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        if args.command == 'create':
            return create_thermal_dicom_cli(args)
        elif args.command == 'visualize':
            return visualize_thermal_dicom_cli(args)
        elif args.command == 'analyze':
            return analyze_thermal_dicom_cli(args)
        elif args.command == 'convert':
            return convert_thermal_data_cli(args)
        elif args.command == 'validate':
            return validate_thermal_dicom_cli(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())