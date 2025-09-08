#!/usr/bin/env python3
"""
Thermal DICOM Creator GUI Application
A professional GUI for creating thermal DICOM files with comprehensive metadata support.
Designed for leading researchers in medical thermal imaging.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import numpy as np
from PIL import Image, ImageTk
import json

# Add the thermal_dicom package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from thermal_dicom.core import ThermalDicom
    from thermal_dicom.metadata import ThermalMetadata
    from thermal_dicom.utils import generate_organization_uid, get_common_organization_uids, validate_organization_uid
except ImportError as e:
    print(f"Error importing thermal_dicom: {e}")
    print("Please ensure the thermal_dicom package is properly installed.")
    sys.exit(1)


class ModernTheme:
    """Modern color scheme and styling for the GUI."""
    
    # Color palette
    PRIMARY_COLOR = "#2E86AB"      # Professional blue
    SECONDARY_COLOR = "#A23B72"    # Purple accent
    SUCCESS_COLOR = "#28A745"      # Green for success
    WARNING_COLOR = "#FFC107"      # Yellow for warnings
    ERROR_COLOR = "#DC3545"        # Red for errors
    BACKGROUND_COLOR = "#F8F9FA"   # Light gray background
    CARD_BACKGROUND = "#FFFFFF"    # White for cards
    TEXT_COLOR = "#212529"         # Dark text
    BORDER_COLOR = "#DEE2E6"       # Light border
    
    # Font configurations
    TITLE_FONT = ("Segoe UI", 16, "bold")
    HEADER_FONT = ("Segoe UI", 12, "bold")
    BODY_FONT = ("Segoe UI", 10)
    SMALL_FONT = ("Segoe UI", 9)


class DicomCreatorGUI:
    """Main GUI application for creating thermal DICOM files."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal DICOM Creator - Professional Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernTheme.BACKGROUND_COLOR)
        
        # Initialize variables
        self.input_source = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.organization_uid = tk.StringVar()
        self.patient_id = tk.StringVar()
        self.patient_name = tk.StringVar()
        self.patient_age = tk.StringVar()
        self.patient_gender = tk.StringVar(value="")
        self.referring_physician = tk.StringVar()
        self.study_description = tk.StringVar(value="Thermal Medical Imaging Study")
        self.series_description = tk.StringVar(value="Thermal Images")
        
        # Date and time variables
        self.study_date = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        self.study_time = tk.StringVar(value=datetime.now().strftime("%H%M%S"))
        self.series_date = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        self.series_time = tk.StringVar(value=datetime.now().strftime("%H%M%S"))
        
        # Thermal parameters
        self.emissivity = tk.DoubleVar(value=0.98)
        self.distance = tk.DoubleVar(value=1.0)
        self.ambient_temp = tk.DoubleVar(value=22.0)
        self.temp_unit = tk.StringVar(value="Celsius")
        
        # Image data
        self.thermal_image = None
        self.temperature_data = None
        self.image_path = None
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.load_common_organization_uids()
        
        # Center the window
        self.center_window()
    
    def setup_styles(self):
        """Configure modern styles for the GUI."""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       font=ModernTheme.TITLE_FONT, 
                       foreground=ModernTheme.PRIMARY_COLOR,
                       background=ModernTheme.BACKGROUND_COLOR)
        
        style.configure('Header.TLabel', 
                       font=ModernTheme.HEADER_FONT, 
                       foreground=ModernTheme.TEXT_COLOR,
                       background=ModernTheme.BACKGROUND_COLOR)
        
        style.configure('Card.TFrame', 
                       background=ModernTheme.CARD_BACKGROUND,
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Success.TButton',
                       background=ModernTheme.SUCCESS_COLOR,
                       foreground='white',
                       font=ModernTheme.BODY_FONT)
        
        style.configure('Primary.TButton',
                       background=ModernTheme.PRIMARY_COLOR,
                       foreground='white',
                       font=ModernTheme.BODY_FONT)
    
    def create_widgets(self):
        """Create the main GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, style='Card.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Thermal DICOM Creator", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for organized sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Input/Output tab
        io_frame = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(io_frame, text="Input/Output")
        self.create_io_section(io_frame)
        
        # Patient Information tab
        patient_frame = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(patient_frame, text="Patient Information")
        self.create_patient_section(patient_frame)
        
        # Study Information tab
        study_frame = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(study_frame, text="Study Information")
        self.create_study_section(study_frame)
        
        # Thermal Parameters tab
        thermal_frame = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(thermal_frame, text="Thermal Parameters")
        self.create_thermal_section(thermal_frame)
        
        # Preview tab
        preview_frame = ttk.Frame(notebook, style='Card.TFrame', padding="15")
        notebook.add(preview_frame, text="Preview & Create")
        self.create_preview_section(preview_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, 
                              textvariable=self.status_var, 
                              relief='sunken', 
                              anchor='w',
                              font=ModernTheme.SMALL_FONT)
        status_bar.pack(side='bottom', fill='x')
    
    def create_io_section(self, parent):
        """Create the Input/Output section."""
        # Input Source Section
        input_frame = ttk.LabelFrame(parent, text="Input Source", padding="10")
        input_frame.pack(fill='x', pady=(0, 15))
        
        # Input source selection
        ttk.Label(input_frame, text="Input Source:").grid(row=0, column=0, sticky='w', pady=5)
        
        input_options = ttk.Frame(input_frame)
        input_options.grid(row=0, column=1, sticky='w', pady=5)
        
        ttk.Radiobutton(input_options, text="Image File", 
                       variable=self.input_source, value="image").pack(side='left', padx=(0, 20))
        ttk.Radiobutton(input_options, text="Temperature Data", 
                       variable=self.input_source, value="temperature").pack(side='left', padx=(0, 20))
        ttk.Radiobutton(input_options, text="Generate Sample", 
                       variable=self.input_source, value="sample").pack(side='left')
        
        # File selection
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(file_frame, text="File Path:").pack(side='left')
        ttk.Entry(file_frame, textvariable=self.input_source, width=50).pack(side='left', padx=(10, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).pack(side='left')
        
        # Image preview
        self.preview_label = ttk.Label(input_frame, text="No image loaded")
        self.preview_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Output Destination Section
        output_frame = ttk.LabelFrame(parent, text="Output Destination", padding="10")
        output_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(output_frame, text="Destination Folder:").grid(row=0, column=0, sticky='w', pady=5)
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Entry(output_file_frame, textvariable=self.dest_folder, width=50).pack(side='left', padx=(0, 5))
        ttk.Button(output_file_frame, text="Browse", command=self.browse_output_folder).pack(side='left')
    
    def create_patient_section(self, parent):
        """Create the Patient Information section."""
        # Patient Basic Information
        basic_frame = ttk.LabelFrame(parent, text="Basic Information", padding="10")
        basic_frame.pack(fill='x', pady=(0, 15))
        
        # Row 1
        ttk.Label(basic_frame, text="Patient Name:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(basic_frame, textvariable=self.patient_name, width=30).grid(row=0, column=1, sticky='w', padx=(10, 20), pady=5)
        
        ttk.Label(basic_frame, text="Patient ID:").grid(row=0, column=2, sticky='w', pady=5)
        ttk.Entry(basic_frame, textvariable=self.patient_id, width=20).grid(row=0, column=3, sticky='w', padx=(10, 0), pady=5)
        
        # Row 2
        ttk.Label(basic_frame, text="Age:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(basic_frame, textvariable=self.patient_age, width=10).grid(row=1, column=1, sticky='w', padx=(10, 20), pady=5)
        
        ttk.Label(basic_frame, text="Gender:").grid(row=1, column=2, sticky='w', pady=5)
        gender_combo = ttk.Combobox(basic_frame, textvariable=self.patient_gender, 
                                   values=["", "M", "F", "O"], width=5, state="readonly")
        gender_combo.grid(row=1, column=3, sticky='w', padx=(10, 0), pady=5)
        
        # Referring Physician
        physician_frame = ttk.LabelFrame(parent, text="Referring Physician", padding="10")
        physician_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(physician_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(physician_frame, textvariable=self.referring_physician, width=50).grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
    
    def create_study_section(self, parent):
        """Create the Study Information section."""
        # Organization UID
        org_frame = ttk.LabelFrame(parent, text="Organization UID", padding="10")
        org_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(org_frame, text="Organization UID Prefix:").grid(row=0, column=0, sticky='w', pady=5)
        
        org_input_frame = ttk.Frame(org_frame)
        org_input_frame.grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Entry(org_input_frame, textvariable=self.organization_uid, width=50).pack(side='left', padx=(0, 5))
        ttk.Button(org_input_frame, text="Common UIDs", command=self.show_common_uids).pack(side='left')
        
        # Study Information
        study_frame = ttk.LabelFrame(parent, text="Study Information", padding="10")
        study_frame.pack(fill='x', pady=(0, 15))
        
        # Row 1
        ttk.Label(study_frame, text="Study Description:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.study_description, width=40).grid(row=0, column=1, sticky='w', padx=(10, 20), pady=5)
        
        ttk.Label(study_frame, text="Study Date:").grid(row=0, column=2, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.study_date, width=15).grid(row=0, column=3, sticky='w', padx=(10, 0), pady=5)
        
        # Row 2
        ttk.Label(study_frame, text="Study Time:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.study_time, width=15).grid(row=1, column=1, sticky='w', padx=(10, 20), pady=5)
        
        ttk.Label(study_frame, text="Series Description:").grid(row=1, column=2, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.series_description, width=30).grid(row=1, column=3, sticky='w', padx=(10, 0), pady=5)
        
        # Row 3
        ttk.Label(study_frame, text="Series Date:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.series_date, width=15).grid(row=2, column=1, sticky='w', padx=(10, 20), pady=5)
        
        ttk.Label(study_frame, text="Series Time:").grid(row=2, column=2, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.series_time, width=15).grid(row=2, column=3, sticky='w', padx=(10, 0), pady=5)
    
    def create_thermal_section(self, parent):
        """Create the Thermal Parameters section."""
        # Thermal Imaging Parameters
        thermal_frame = ttk.LabelFrame(parent, text="Thermal Imaging Parameters", padding="10")
        thermal_frame.pack(fill='x', pady=(0, 15))
        
        # Row 1
        ttk.Label(thermal_frame, text="Emissivity:").grid(row=0, column=0, sticky='w', pady=5)
        emissivity_scale = ttk.Scale(thermal_frame, from_=0.1, to=1.0, 
                                    variable=self.emissivity, orient='horizontal', length=200)
        emissivity_scale.grid(row=0, column=1, sticky='w', padx=(10, 10), pady=5)
        ttk.Label(thermal_frame, textvariable=self.emissivity).grid(row=0, column=2, sticky='w', pady=5)
        
        ttk.Label(thermal_frame, text="Distance (m):").grid(row=0, column=3, sticky='w', padx=(20, 0), pady=5)
        ttk.Entry(thermal_frame, textvariable=self.distance, width=10).grid(row=0, column=4, sticky='w', padx=(10, 0), pady=5)
        
        # Row 2
        ttk.Label(thermal_frame, text="Ambient Temperature (°C):").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(thermal_frame, textvariable=self.ambient_temp, width=10).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        ttk.Label(thermal_frame, text="Temperature Unit:").grid(row=1, column=2, sticky='w', padx=(20, 0), pady=5)
        temp_unit_combo = ttk.Combobox(thermal_frame, textvariable=self.temp_unit, 
                                      values=["Celsius", "Fahrenheit", "Kelvin"], 
                                      width=10, state="readonly")
        temp_unit_combo.grid(row=1, column=3, sticky='w', padx=(10, 0), pady=5)
        
        # Advanced Parameters
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Parameters", padding="10")
        advanced_frame.pack(fill='x', pady=(0, 15))
        
        # Add more advanced thermal parameters here
        ttk.Label(advanced_frame, text="Additional parameters can be configured here...").pack(pady=10)
    
    def create_preview_section(self, parent):
        """Create the Preview and Create section."""
        # Preview Frame
        preview_frame = ttk.LabelFrame(parent, text="DICOM Preview", padding="10")
        preview_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Preview text area
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=15, width=80)
        self.preview_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Generate Preview", 
                  command=self.generate_preview, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Create DICOM", 
                  command=self.create_dicom, style='Success.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Clear All", 
                  command=self.clear_all).pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(buttons_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(side='right', padx=(10, 0))
    
    def load_common_organization_uids(self):
        """Load common organization UIDs."""
        self.common_uids = get_common_organization_uids()
    
    def show_common_uids(self):
        """Show dialog with common organization UIDs."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Common Organization UIDs")
        dialog.geometry("500x400")
        dialog.configure(bg=ModernTheme.BACKGROUND_COLOR)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create listbox
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Select an Organization UID:", 
                 font=ModernTheme.HEADER_FONT).pack(pady=(0, 10))
        
        listbox = tk.Listbox(frame, height=15, font=ModernTheme.BODY_FONT)
        listbox.pack(fill='both', expand=True, pady=(0, 10))
        
        # Populate listbox
        for name, uid in self.common_uids.items():
            listbox.insert(tk.END, f"{name}: {uid}")
        
        # Selection handler
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                uid = selected_text.split(": ")[1]
                self.organization_uid.set(uid)
                dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left')
    
    def browse_input_file(self):
        """Browse for input file."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.tiff *.tif *.bmp"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Input File", filetypes=filetypes)
        if filename:
            self.input_source.set(filename)
            self.load_image_preview(filename)
    
    def browse_output_folder(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.dest_folder.set(folder)
    
    def load_image_preview(self, filepath):
        """Load and display image preview."""
        try:
            # Load image
            image = Image.open(filepath)
            
            # Resize for preview (max 200x200)
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            
            self.image_path = filepath
            self.status_var.set(f"Loaded image: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")
            self.preview_label.configure(image="", text="Error loading image")
    
    def generate_preview(self):
        """Generate DICOM preview."""
        try:
            self.status_var.set("Generating preview...")
            self.progress_var.set(20)
            
            # Collect all metadata
            metadata = self.collect_metadata()
            
            self.progress_var.set(60)
            
            # Format preview
            preview_text = self.format_metadata_preview(metadata)
            
            self.progress_var.set(80)
            
            # Update preview
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
            
            self.progress_var.set(100)
            self.status_var.set("Preview generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {e}")
            self.status_var.set("Error generating preview")
    
    def collect_metadata(self) -> Dict[str, Any]:
        """Collect all metadata from the GUI."""
        metadata = {
            # Patient Information
            'patient_name': self.patient_name.get(),
            'patient_id': self.patient_id.get(),
            'patient_age': self.patient_age.get(),
            'patient_gender': self.patient_gender.get(),
            'referring_physician': self.referring_physician.get(),
            
            # Study Information
            'organization_uid': self.organization_uid.get(),
            'study_description': self.study_description.get(),
            'series_description': self.series_description.get(),
            'study_date': self.study_date.get(),
            'study_time': self.study_time.get(),
            'series_date': self.series_date.get(),
            'series_time': self.series_time.get(),
            
            # Thermal Parameters
            'emissivity': self.emissivity.get(),
            'distance': self.distance.get(),
            'ambient_temperature': self.ambient_temp.get(),
            'temperature_unit': self.temp_unit.get(),
            
            # File Information
            'input_source': self.input_source.get(),
            'output_folder': self.dest_folder.get(),
            'image_path': self.image_path
        }
        
        return metadata
    
    def format_metadata_preview(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for preview display."""
        preview = "=== THERMAL DICOM PREVIEW ===\n\n"
        
        # Patient Information
        preview += "PATIENT INFORMATION:\n"
        preview += f"  Name: {metadata['patient_name']}\n"
        preview += f"  ID: {metadata['patient_id']}\n"
        preview += f"  Age: {metadata['patient_age']}\n"
        preview += f"  Gender: {metadata['patient_gender']}\n"
        preview += f"  Referring Physician: {metadata['referring_physician']}\n\n"
        
        # Study Information
        preview += "STUDY INFORMATION:\n"
        preview += f"  Organization UID: {metadata['organization_uid']}\n"
        preview += f"  Study Description: {metadata['study_description']}\n"
        preview += f"  Series Description: {metadata['series_description']}\n"
        preview += f"  Study Date: {metadata['study_date']}\n"
        preview += f"  Study Time: {metadata['study_time']}\n"
        preview += f"  Series Date: {metadata['series_date']}\n"
        preview += f"  Series Time: {metadata['series_time']}\n\n"
        
        # Thermal Parameters
        preview += "THERMAL PARAMETERS:\n"
        preview += f"  Emissivity: {metadata['emissivity']}\n"
        preview += f"  Distance: {metadata['distance']} m\n"
        preview += f"  Ambient Temperature: {metadata['ambient_temperature']} °C\n"
        preview += f"  Temperature Unit: {metadata['temperature_unit']}\n\n"
        
        # File Information
        preview += "FILE INFORMATION:\n"
        preview += f"  Input Source: {metadata['input_source']}\n"
        preview += f"  Output Folder: {metadata['output_folder']}\n"
        if metadata['image_path']:
            preview += f"  Image Path: {metadata['image_path']}\n"
        
        return preview
    
    def create_dicom(self):
        """Create the DICOM file."""
        try:
            self.status_var.set("Creating DICOM file...")
            self.progress_var.set(10)
            
            # Validate inputs
            if not self.validate_inputs():
                return
            
            self.progress_var.set(20)
            
            # Collect metadata
            metadata = self.collect_metadata()
            
            self.progress_var.set(40)
            
            # Create DICOM in a separate thread to avoid blocking GUI
            thread = threading.Thread(target=self._create_dicom_thread, args=(metadata,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating DICOM: {e}")
            self.status_var.set("Error creating DICOM")
    
    def _create_dicom_thread(self, metadata: Dict[str, Any]):
        """Create DICOM file in a separate thread."""
        try:
            self.progress_var.set(50)
            
            # Load or generate image data
            if metadata['input_source'] == 'sample':
                # Generate sample thermal data
                thermal_array = self.generate_sample_thermal_data()
                temperature_data = None
            elif metadata['image_path']:
                # Load image file
                thermal_array = self.load_image_data(metadata['image_path'])
                temperature_data = None
            else:
                raise ValueError("No input source specified")
            
            self.progress_var.set(70)
            
            # Create thermal DICOM
            thermal_dicom = ThermalDicom(
                thermal_array=thermal_array,
                temperature_data=temperature_data,
                organization_uid_prefix=metadata['organization_uid'] if metadata['organization_uid'] else None
            )
            
            self.progress_var.set(80)
            
            # Set metadata
            self.set_dicom_metadata(thermal_dicom, metadata)
            
            self.progress_var.set(90)
            
            # Generate output filename
            output_filename = self.generate_output_filename(metadata)
            output_path = os.path.join(metadata['output_folder'], output_filename)
            
            # Save DICOM
            thermal_dicom.save_dicom(output_path)
            
            self.progress_var.set(100)
            
            # Show success message
            self.root.after(0, lambda: self.show_success_message(output_path))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error creating DICOM: {e}"))
            self.root.after(0, lambda: self.status_var.set("Error creating DICOM"))
    
    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        errors = []
        
        # Check required fields
        if not self.patient_name.get().strip():
            errors.append("Patient name is required")
        
        if not self.patient_id.get().strip():
            errors.append("Patient ID is required")
        
        if not self.dest_folder.get().strip():
            errors.append("Output folder is required")
        
        if not os.path.exists(self.dest_folder.get()):
            errors.append("Output folder does not exist")
        
        # Check organization UID format if provided
        if self.organization_uid.get().strip():
            is_valid, error_msg = validate_organization_uid(self.organization_uid.get())
            if not is_valid:
                errors.append(f"Invalid Organization UID: {error_msg}")
        
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Error", error_message)
            return False
        
        return True
    
    def generate_sample_thermal_data(self) -> np.ndarray:
        """Generate sample thermal data for testing."""
        # Create a 512x512 thermal image with temperature gradient
        rows, cols = 512, 512
        
        # Create temperature gradient (20-40°C)
        x = np.linspace(20, 40, cols)
        y = np.linspace(20, 40, rows)
        X, Y = np.meshgrid(x, y)
        
        # Add some thermal patterns
        thermal_data = X + Y + 10 * np.sin(X/10) * np.cos(Y/10)
        
        return thermal_data.astype(np.float32)
    
    def load_image_data(self, image_path: str) -> np.ndarray:
        """Load image data from file."""
        try:
            # Load image using PIL
            image = Image.open(image_path)
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array
            array = np.array(image, dtype=np.float32)
            
            return array
            
        except Exception as e:
            raise ValueError(f"Could not load image: {e}")
    
    def set_dicom_metadata(self, thermal_dicom: ThermalDicom, metadata: Dict[str, Any]):
        """Set metadata in the DICOM object."""
        # Set patient information
        thermal_dicom.dataset.PatientName = metadata['patient_name']
        thermal_dicom.dataset.PatientID = metadata['patient_id']
        
        if metadata['patient_age']:
            thermal_dicom.dataset.PatientAge = metadata['patient_age']
        
        if metadata['patient_gender']:
            thermal_dicom.dataset.PatientSex = metadata['patient_gender']
        
        if metadata['referring_physician']:
            thermal_dicom.dataset.ReferringPhysicianName = metadata['referring_physician']
        
        # Set study information
        thermal_dicom.dataset.StudyDescription = metadata['study_description']
        thermal_dicom.dataset.SeriesDescription = metadata['series_description']
        thermal_dicom.dataset.StudyDate = metadata['study_date']
        thermal_dicom.dataset.StudyTime = metadata['study_time']
        thermal_dicom.dataset.SeriesDate = metadata['series_date']
        thermal_dicom.dataset.SeriesTime = metadata['series_time']
        
        # Set thermal parameters
        thermal_params = {
            'emissivity': metadata['emissivity'],
            'distance_from_camera': metadata['distance'],
            'ambient_temperature': metadata['ambient_temperature'],
            'temperature_unit': metadata['temperature_unit']
        }
        thermal_dicom.set_thermal_parameters(thermal_params)
    
    def generate_output_filename(self, metadata: Dict[str, Any]) -> str:
        """Generate output filename for the DICOM file."""
        # Create filename based on patient info and timestamp
        patient_id = metadata['patient_id'].replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"thermal_{patient_id}_{timestamp}.dcm"
        return filename
    
    def show_success_message(self, output_path: str):
        """Show success message after DICOM creation."""
        messagebox.showinfo("Success", 
                           f"DICOM file created successfully!\n\n"
                           f"Saved to: {output_path}")
        self.status_var.set("DICOM created successfully")
    
    def clear_all(self):
        """Clear all form fields."""
        # Clear all variables
        self.input_source.set("")
        self.dest_folder.set("")
        self.organization_uid.set("")
        self.patient_id.set("")
        self.patient_name.set("")
        self.patient_age.set("")
        self.patient_gender.set("")
        self.referring_physician.set("")
        self.study_description.set("Thermal Medical Imaging Study")
        self.series_description.set("Thermal Images")
        
        # Reset dates and times
        current_date = datetime.now().strftime("%Y%m%d")
        current_time = datetime.now().strftime("%H%M%S")
        self.study_date.set(current_date)
        self.study_time.set(current_time)
        self.series_date.set(current_date)
        self.series_time.set(current_time)
        
        # Reset thermal parameters
        self.emissivity.set(0.98)
        self.distance.set(1.0)
        self.ambient_temp.set(22.0)
        self.temp_unit.set("Celsius")
        
        # Clear preview
        self.preview_text.delete(1.0, tk.END)
        self.preview_label.configure(image="", text="No image loaded")
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Ready")
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = DicomCreatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
