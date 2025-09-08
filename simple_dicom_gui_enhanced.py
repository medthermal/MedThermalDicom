#!/usr/bin/env python3
"""
Enhanced Thermal DICOM Creator GUI
A professional, modern GUI for creating thermal DICOM files.
Designed for thousands of users with enterprise-grade UI/UX.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk, ImageOps

# Add the thermal_dicom package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from thermal_dicom.core import ThermalDicom
    from thermal_dicom.metadata import ThermalMetadata
    from thermal_dicom.utils import get_common_organization_uids, validate_organization_uid
    # Import the MultiViewThermalImaging class from the examples
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples'))
    from multi_view_thermal_imaging import MultiViewThermalImaging
except ImportError as e:
    print(f"Error importing thermal_dicom: {e}")
    sys.exit(1)


class EnhancedDicomCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MedTherm DICOM")
        self.root.geometry("900x800")
        self.root.minsize(800, 700)
        
        # Configure modern styling
        self.setup_styling()
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.patient_name = tk.StringVar()
        self.patient_id = tk.StringVar()
        self.patient_age = tk.StringVar()
        self.patient_gender = tk.StringVar(value="")
        self.referring_physician = tk.StringVar()
        self.study_description = tk.StringVar(value="Thermal Medical Imaging")
        self.organization_uid = tk.StringVar()
        self.scan_date = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        self.study_date = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        self.input_files = []  # List to store multiple input files
        
        # Initialize MultiViewThermalImaging instance
        self.multi_view_handler = None
        self.metadata_handler = None
        
        # Create GUI
        self.create_widgets()
        self.load_common_uids()
        
        # Center window
        self.center_window()
    
    def setup_styling(self):
        """Configure modern styling for the application."""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Segoe UI', 9), foreground='#27ae60')
        
        # Configure frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Success.TFrame', relief='solid', borderwidth=2, bordercolor='#27ae60')
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton', font=('Segoe UI', 11, 'bold'))
        style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Configure entry fields
        style.configure('Modern.TEntry', fieldbackground='#ecf0f1', borderwidth=1)
        style.configure('Modern.TCombobox', fieldbackground='#ecf0f1', borderwidth=1)
        
        # Configure label frames
        style.configure('Card.TLabelframe', font=('Segoe UI', 11, 'bold'))
        style.configure('Card.TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground='#2c3e50')
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create the enhanced GUI widgets."""
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title section with logo
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill='x', pady=(10, 15))
        
        title_label = ttk.Label(title_frame, text="🔥 MedTherm DICOM", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Professional Medical Imaging Software for Research & Clinical Use", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(2, 0))
        
        # Input/Output Section
        io_frame = ttk.LabelFrame(scrollable_frame, text="📁 Input/Output Management", 
                                 padding="10", style='Card.TLabelframe')
        io_frame.pack(fill='x', pady=(0, 15), padx=15)
        
        # Input files section
        input_frame = ttk.Frame(io_frame)
        input_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(input_frame, text="📸 Input Files (Multi-view):", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        input_controls = ttk.Frame(input_frame)
        input_controls.pack(fill='x')
        
        ttk.Entry(input_controls, textvariable=self.input_file, width=60, 
                 style='Modern.TEntry').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(input_controls, text="📂 Browse Files", command=self.browse_input, 
                  style='Primary.TButton').pack(side='left', padx=(0, 5))
        ttk.Button(input_controls, text="🗑️ Clear All", command=self.clear_input_files, 
                  style='Danger.TButton').pack(side='left')
        
        # File list with modern styling
        list_frame = ttk.Frame(input_frame)
        list_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(list_frame, text="Selected Files:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Create a frame for the listbox with border
        listbox_frame = ttk.Frame(list_frame, relief='solid', borderwidth=1)
        listbox_frame.pack(fill='x')
        
        self.file_listbox = tk.Listbox(listbox_frame, height=4, font=('Segoe UI', 9),
                                      selectmode='single', activestyle='none',
                                      selectbackground='#3498db', selectforeground='white',
                                      bg='#ffffff', fg='#2c3e50', relief='flat')
        self.file_listbox.pack(fill='both', expand=True, padx=2, pady=2)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # File info display
        info_frame = ttk.Frame(input_frame)
        info_frame.pack(fill='x', pady=(15, 0))
        
        self.file_info_var = tk.StringVar(value="Select files to see information")
        self.file_info_label = ttk.Label(info_frame, textvariable=self.file_info_var, 
                                        style='Info.TLabel')
        self.file_info_label.pack(anchor='w')
        
        # Output folder section
        output_frame = ttk.Frame(io_frame)
        output_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Label(output_frame, text="📁 Output Folder:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        output_controls = ttk.Frame(output_frame)
        output_controls.pack(fill='x')
        
        ttk.Entry(output_controls, textvariable=self.output_folder, width=60, 
                 style='Modern.TEntry').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(output_controls, text="📂 Browse Folder", command=self.browse_output, 
                  style='Primary.TButton').pack(side='left')
        
        # Patient Information Section
        patient_frame = ttk.LabelFrame(scrollable_frame, text="👤 Patient Information", 
                                      padding="10", style='Card.TLabelframe')
        patient_frame.pack(fill='x', pady=(0, 15), padx=15)
        
        # Patient info in two columns
        patient_left = ttk.Frame(patient_frame)
        patient_left.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        patient_right = ttk.Frame(patient_frame)
        patient_right.pack(side='left', fill='x', expand=True)
        
        # Left column
        ttk.Label(patient_left, text="Patient Name:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(patient_left, textvariable=self.patient_name, width=35, 
                 style='Modern.TEntry').pack(fill='x', pady=(0, 15))
        
        ttk.Label(patient_left, text="Patient ID:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(patient_left, textvariable=self.patient_id, width=35, 
                 style='Modern.TEntry').pack(fill='x', pady=(0, 15))
        
        ttk.Label(patient_left, text="Referring Physician:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(patient_left, textvariable=self.referring_physician, width=35, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Right column
        ttk.Label(patient_right, text="Age:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(patient_right, textvariable=self.patient_age, width=15, 
                 style='Modern.TEntry').pack(fill='x', pady=(0, 15))
        
        ttk.Label(patient_right, text="Gender:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        gender_combo = ttk.Combobox(patient_right, textvariable=self.patient_gender, 
                                   values=["", "M", "F", "O"], width=10, state="readonly",
                                   style='Modern.TCombobox')
        gender_combo.pack(fill='x', pady=(0, 15))
        
        # Study Information Section
        study_frame = ttk.LabelFrame(scrollable_frame, text="🔬 Study Information", 
                                    padding="10", style='Card.TLabelframe')
        study_frame.pack(fill='x', pady=(0, 15), padx=15)
        
        # Organization UID
        uid_frame = ttk.Frame(study_frame)
        uid_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(uid_frame, text="Organization UID:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        uid_controls = ttk.Frame(uid_frame)
        uid_controls.pack(fill='x')
        
        ttk.Entry(uid_controls, textvariable=self.organization_uid, width=60, 
                 style='Modern.TEntry').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(uid_controls, text="📋 Common UIDs", command=self.show_common_uids, 
                  style='Primary.TButton').pack(side='left')
        
        # Study Description
        ttk.Label(study_frame, text="Study Description:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(study_frame, textvariable=self.study_description, width=60, 
                 style='Modern.TEntry').pack(fill='x', pady=(0, 15))
        
        # Dates in two columns
        dates_frame = ttk.Frame(study_frame)
        dates_frame.pack(fill='x', pady=(0, 15))
        
        date_left = ttk.Frame(dates_frame)
        date_left.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        date_right = ttk.Frame(dates_frame)
        date_right.pack(side='left', fill='x', expand=True)
        
        ttk.Label(date_left, text="Scan Date:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(date_left, textvariable=self.scan_date, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(date_right, text="Study Date:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        ttk.Entry(date_right, textvariable=self.study_date, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Date format hint
        ttk.Label(study_frame, text="📅 Format: YYYYMMDD (e.g., 20241201)", 
                 style='Info.TLabel').pack(anchor='w', pady=(10, 0))
        
        # Additional Study Information
        additional_frame = ttk.Frame(study_frame)
        additional_frame.pack(fill='x', pady=(15, 0))
        
        # Row 1: Study ID and Accession Number
        study_row1 = ttk.Frame(additional_frame)
        study_row1.pack(fill='x', pady=(0, 10))
        
        study_id_frame = ttk.Frame(study_row1)
        study_id_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        accession_frame = ttk.Frame(study_row1)
        accession_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(study_id_frame, text="Study ID:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.study_id = tk.StringVar()
        ttk.Entry(study_id_frame, textvariable=self.study_id, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(accession_frame, text="Accession Number:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.accession_number = tk.StringVar()
        ttk.Entry(accession_frame, textvariable=self.accession_number, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Row 2: Study Time and Series Time
        study_row2 = ttk.Frame(additional_frame)
        study_row2.pack(fill='x', pady=(0, 10))
        
        study_time_frame = ttk.Frame(study_row2)
        study_time_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        series_time_frame = ttk.Frame(study_row2)
        series_time_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(study_time_frame, text="Study Time:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.study_time = tk.StringVar(value=datetime.now().strftime("%H%M%S"))
        ttk.Entry(study_time_frame, textvariable=self.study_time, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(series_time_frame, text="Series Time:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.series_time = tk.StringVar(value=datetime.now().strftime("%H%M%S"))
        ttk.Entry(series_time_frame, textvariable=self.series_time, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Row 3: Modality and Body Part
        study_row3 = ttk.Frame(additional_frame)
        study_row3.pack(fill='x', pady=(0, 10))
        
        modality_frame = ttk.Frame(study_row3)
        modality_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        body_part_frame = ttk.Frame(study_row3)
        body_part_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(modality_frame, text="Modality:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.modality = tk.StringVar(value="TG")
        modality_combo = ttk.Combobox(modality_frame, textvariable=self.modality, 
                                     values=["TG", "OT", "XA", "CR", "CT", "MR", "US"], 
                                     width=10, state="readonly", style='Modern.TCombobox')
        modality_combo.pack(fill='x')
        
        ttk.Label(body_part_frame, text="Body Part Examined:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.body_part = tk.StringVar()
        body_part_combo = ttk.Combobox(body_part_frame, textvariable=self.body_part, 
                                      values=["", "BREAST", "HAND", "FOOT", "FACE", "CHEST", "ABDOMEN", "BACK", "WHOLE BODY"], 
                                      width=15, state="readonly", style='Modern.TCombobox')
        body_part_combo.pack(fill='x')
        
        # Row 4: View Position and Patient Position
        study_row4 = ttk.Frame(additional_frame)
        study_row4.pack(fill='x', pady=(0, 10))
        
        view_pos_frame = ttk.Frame(study_row4)
        view_pos_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        patient_pos_frame = ttk.Frame(study_row4)
        patient_pos_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(view_pos_frame, text="View Position:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.view_position = tk.StringVar()
        view_pos_combo = ttk.Combobox(view_pos_frame, textvariable=self.view_position, 
                                     values=["", "A", "P", "L", "R", "OBL", "LAT", "PA", "AP"], 
                                     width=10, state="readonly", style='Modern.TCombobox')
        view_pos_combo.pack(fill='x')
        
        ttk.Label(patient_pos_frame, text="Patient Position:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.patient_position = tk.StringVar()
        patient_pos_combo = ttk.Combobox(patient_pos_frame, textvariable=self.patient_position, 
                                        values=["", "FFS", "FFP", "FFDR", "FFDL", "HFDR", "HFDL"], 
                                        width=10, state="readonly", style='Modern.TCombobox')
        patient_pos_combo.pack(fill='x')
        
        # Row 5: Laterality and Anatomical Region
        study_row5 = ttk.Frame(additional_frame)
        study_row5.pack(fill='x', pady=(0, 10))
        
        laterality_frame = ttk.Frame(study_row5)
        laterality_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        anatomical_frame = ttk.Frame(study_row5)
        anatomical_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(laterality_frame, text="Laterality:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.laterality = tk.StringVar()
        laterality_combo = ttk.Combobox(laterality_frame, textvariable=self.laterality, 
                                       values=["", "L", "R", "B"], 
                                       width=10, state="readonly", style='Modern.TCombobox')
        laterality_combo.pack(fill='x')
        
        ttk.Label(anatomical_frame, text="Anatomical Region:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.anatomical_region = tk.StringVar()
        anatomical_combo = ttk.Combobox(anatomical_frame, textvariable=self.anatomical_region, 
                                       values=["", "BREAST", "HAND", "FOOT", "FACE", "CHEST", "ABDOMEN", "BACK", "EXTREMITY"], 
                                       width=15, state="readonly", style='Modern.TCombobox')
        anatomical_combo.pack(fill='x')
        
        # Thermal Parameters Section
        thermal_frame = ttk.LabelFrame(scrollable_frame, text="🌡️ Thermal Imaging Parameters", 
                                      padding="10", style='Card.TLabelframe')
        thermal_frame.pack(fill='x', pady=(0, 15), padx=15)
        
        # Row 1: Emissivity and Distance
        thermal_row1 = ttk.Frame(thermal_frame)
        thermal_row1.pack(fill='x', pady=(0, 10))
        
        emissivity_frame = ttk.Frame(thermal_row1)
        emissivity_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        distance_frame = ttk.Frame(thermal_row1)
        distance_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(emissivity_frame, text="Emissivity:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.emissivity = tk.StringVar(value="0.98")
        ttk.Entry(emissivity_frame, textvariable=self.emissivity, width=15, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(distance_frame, text="Distance (m):", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.distance = tk.StringVar(value="1.0")
        ttk.Entry(distance_frame, textvariable=self.distance, width=15, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Row 2: Ambient and Reflected Temperature
        thermal_row2 = ttk.Frame(thermal_frame)
        thermal_row2.pack(fill='x', pady=(0, 10))
        
        ambient_frame = ttk.Frame(thermal_row2)
        ambient_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        reflected_frame = ttk.Frame(thermal_row2)
        reflected_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(ambient_frame, text="Ambient Temp (°C):", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.ambient_temp = tk.StringVar(value="22.0")
        ttk.Entry(ambient_frame, textvariable=self.ambient_temp, width=15, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(reflected_frame, text="Reflected Temp (°C):", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.reflected_temp = tk.StringVar(value="22.0")
        ttk.Entry(reflected_frame, textvariable=self.reflected_temp, width=15, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Row 3: Humidity and Camera Info
        thermal_row3 = ttk.Frame(thermal_frame)
        thermal_row3.pack(fill='x', pady=(0, 10))
        
        humidity_frame = ttk.Frame(thermal_row3)
        humidity_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        camera_frame = ttk.Frame(thermal_row3)
        camera_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(humidity_frame, text="Relative Humidity (%):", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.humidity = tk.StringVar(value="50.0")
        ttk.Entry(humidity_frame, textvariable=self.humidity, width=15, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(camera_frame, text="Camera Model:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.camera_model = tk.StringVar()
        ttk.Entry(camera_frame, textvariable=self.camera_model, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Row 4: Acquisition Mode and Calibration
        thermal_row4 = ttk.Frame(thermal_frame)
        thermal_row4.pack(fill='x', pady=(0, 10))
        
        acquisition_frame = ttk.Frame(thermal_row4)
        acquisition_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        calibration_frame = ttk.Frame(thermal_row4)
        calibration_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(acquisition_frame, text="Acquisition Mode:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.acquisition_mode = tk.StringVar(value="Medical Thermal Imaging")
        ttk.Entry(acquisition_frame, textvariable=self.acquisition_mode, width=25, 
                 style='Modern.TEntry').pack(fill='x')
        
        ttk.Label(calibration_frame, text="Calibration Date:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.calibration_date = tk.StringVar(value=datetime.now().strftime("%Y%m%d"))
        ttk.Entry(calibration_frame, textvariable=self.calibration_date, width=20, 
                 style='Modern.TEntry').pack(fill='x')
        
        # Action Buttons Section
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', pady=(15, 20), padx=15)
        
        # Main action buttons
        action_buttons = ttk.Frame(button_frame)
        action_buttons.pack()
        
        ttk.Button(action_buttons, text="🚀 Create DICOM Series", command=self.create_dicom, 
                  style='Success.TButton').pack(side='left', padx=(0, 15))
        ttk.Button(action_buttons, text="🧹 Clear All", command=self.clear_all, 
                  style='Danger.TButton').pack(side='left', padx=(0, 15))
        ttk.Button(action_buttons, text="❓ Help", command=self.show_help, 
                  style='Primary.TButton').pack(side='left')
        
        # Status bar
        status_frame = ttk.Frame(scrollable_frame)
        status_frame.pack(fill='x', padx=20)
        
        self.status_var = tk.StringVar(value="✅ Ready to create thermal DICOM files")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              relief='sunken', anchor='w', padding=(10, 5))
        status_bar.pack(fill='x')
        
        # Initialize variables
        self.csv_data = None
        self.preview_photo = None
        self.preview_disp_size = (0, 0)
        self.is_temperature_data = False
    
    def load_common_uids(self):
        """Load common organization UIDs."""
        try:
            common_uids = get_common_organization_uids()
            # Store for later use
            self.common_uids = common_uids
        except Exception as e:
            self.common_uids = []
            print(f"Could not load common UIDs: {e}")
    
    def show_common_uids(self):
        """Show common organization UIDs in a dialog."""
        if not hasattr(self, 'common_uids') or not self.common_uids:
            messagebox.showinfo("Common UIDs", "No common UIDs available.")
            return
        
        # Create a new window
        uid_window = tk.Toplevel(self.root)
        uid_window.title("Common Organization UIDs")
        uid_window.geometry("600x400")
        uid_window.transient(self.root)
        uid_window.grab_set()
        
        # Add content
        ttk.Label(uid_window, text="Common Organization UIDs", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Create listbox
        listbox = tk.Listbox(uid_window, font=('Consolas', 9), selectmode='single')
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add UIDs
        for uid in self.common_uids:
            listbox.insert(tk.END, uid)
        
        # Add copy button
        def copy_selected():
            selection = listbox.curselection()
            if selection:
                selected_uid = listbox.get(selection[0])
                uid_window.clipboard_clear()
                uid_window.clipboard_append(selected_uid)
                self.organization_uid.set(selected_uid)
                messagebox.showinfo("Copied", f"UID copied to clipboard and form:\n{selected_uid}")
        
        ttk.Button(uid_window, text="Copy Selected UID", command=copy_selected).pack(pady=10)
    
    def show_help(self):
        """Show help information."""
        help_text = """
MedTherm DICOM - Help

📁 Input Files:
• Select multiple image files (PNG, JPG, TIFF, BMP) or CSV files
• CSV files should contain temperature data in Celsius
• Images will be processed as thermal data

👤 Patient Information:
• Fill in patient details for DICOM metadata
• Patient ID is required for file naming

🔬 Study Information:
• Organization UID: Your institution's unique identifier
• Study Description: Brief description of the imaging study
• Dates: Use YYYYMMDD format (e.g., 20241201)

📊 Multi-view Support:
• Create DICOM series from multiple angles/views
• All files share the same series UID for proper grouping
• Each file gets a unique instance number

🚀 Creating DICOM:
• Click 'Create DICOM Series' to process all files
• Files are saved with descriptive names
• Temperature data is properly scaled for DICOM viewers

For technical support, contact your system administrator.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - MedTherm DICOM")
        help_window.geometry("500x600")
        help_window.transient(self.root)
        
        text_widget = tk.Text(help_window, wrap='word', font=('Segoe UI', 9))
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
    
    def browse_input(self):
        """Browse for input files."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.tiff *.tif *.bmp"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        filenames = filedialog.askopenfilenames(title="Select Input Files", filetypes=filetypes)
        if filenames:
            self.input_files = list(filenames)
            self.input_file.set(f"{len(filenames)} file(s) selected")
            self.update_file_list()
            self.preview_selected_file()
    
    def update_file_list(self):
        """Update the file listbox with selected files."""
        self.file_listbox.delete(0, tk.END)
        for i, filename in enumerate(self.input_files):
            basename = os.path.basename(filename)
            self.file_listbox.insert(tk.END, f"{i+1}. {basename}")
    
    def preview_selected_file(self, filename=None):
        """Show file information for the selected file."""
        if filename is None and self.input_files:
            filename = self.input_files[0]
        
        if not filename:
            return
            
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".csv":
            self.is_temperature_data = True
            try:
                self.csv_data = self.load_csv_data(filename)
                self.show_file_info(filename, "CSV", self.csv_data.shape)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")
                self.clear_file_info()
        else:
            self.is_temperature_data = False
            try:
                self.show_file_info(filename, "Image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image info: {e}")
                self.clear_file_info()
    
    def show_file_info(self, filename, file_type, data_shape=None):
        """Display file information instead of preview."""
        try:
            basename = os.path.basename(filename)
            file_size = os.path.getsize(filename)
            size_kb = file_size / 1024
            
            if file_type == "CSV" and data_shape:
                info_text = f"📄 {basename} | CSV Data | Shape: {data_shape[0]}×{data_shape[1]} | Size: {size_kb:.1f} KB"
            elif file_type == "Image":
                try:
                    with Image.open(filename) as img:
                        width, height = img.size
                        mode = img.mode
                    info_text = f"🖼️ {basename} | Image | Size: {width}×{height} | Mode: {mode} | File: {size_kb:.1f} KB"
                except:
                    info_text = f"🖼️ {basename} | Image | Size: {size_kb:.1f} KB"
            else:
                info_text = f"📁 {basename} | {file_type} | Size: {size_kb:.1f} KB"
            
            self.file_info_var.set(info_text)
        except Exception as e:
            self.file_info_var.set(f"Error reading file: {e}")
    
    def clear_file_info(self):
        """Clear file information display."""
        self.file_info_var.set("Select files to see information")
        self.csv_data = None
        self.is_temperature_data = False
    
    def clear_input_files(self):
        """Clear all input files."""
        self.input_files = []
        self.input_file.set("")
        self.file_listbox.delete(0, tk.END)
        self.clear_file_info()
    
    def on_file_select(self, event):
        """Handle file selection in listbox for preview."""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.input_files):
                filename = self.input_files[index]
                self.preview_selected_file(filename)
    
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def create_dicom(self):
        """Create DICOM files from input data using MultiViewThermalImaging class."""
        if not self.validate_inputs():
            return
        
        if not self.input_files:
            messagebox.showerror("Error", "Please select input files")
            return
        
        try:
            self.status_var.set("🔄 Creating DICOM series...")
            self.root.update()
            
            # Get organization UID
            org_uid = self.organization_uid.get().strip()
            if not org_uid:
                messagebox.showerror("Error", "Organization UID is required")
                return
            
            # Validate organization UID
            if not validate_organization_uid(org_uid):
                messagebox.showerror("Error", "Invalid Organization UID format")
                return
            
            # Initialize MultiViewThermalImaging handler
            self.multi_view_handler = MultiViewThermalImaging(organization_uid_prefix=org_uid)
            self.metadata_handler = self.multi_view_handler.metadata
            
            # Create output directory if it doesn't exist
            output_dir = self.output_folder.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare thermal data dictionary
            thermal_data_dict = {}
            view_configs = []
            
            # Process each input file
            for i, input_file in enumerate(self.input_files):
                try:
                    # Load data based on file type
                    ext = os.path.splitext(input_file)[1].lower()
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    
                    if ext == ".csv":
                        thermal_array = self.load_csv_data(input_file)
                    else:
                        thermal_array = self.load_image_data(input_file)
                    
                    # Create view key and config
                    view_key = f"view_{i+1}"
                    thermal_data_dict[view_key] = thermal_array
                    
                    # Create view configuration
                    view_config = {
                        'view_key': view_key,
                        'view_position': self.view_position.get() or 'A',
                        'view_comment': f'{base_name} view',
                        'image_laterality': self.laterality.get() or 'B',
                        'patient_position': self.patient_position.get() or 'STANDING',
                        'acquisition_view': f'{base_name} thermal imaging view'
                    }
                    view_configs.append(view_config)
                    
                    self.status_var.set(f"🔄 Processing file {i+1}/{len(self.input_files)}: {base_name}")
                    self.root.update()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process {input_file}: {e}")
                    continue
            
            if not thermal_data_dict:
                messagebox.showerror("Error", "No valid files were processed")
                return
            
            # Get anatomical region from UI
            anatomical_region = self.anatomical_region.get() or self.body_part.get() or "unknown"
            anatomical_region = anatomical_region.lower().replace(" ", "_")
            
            # Create custom multi-view series using the same pattern as the script
            created_files = self.multi_view_handler.create_custom_multi_view_series(
                patient_name=self.patient_name.get() or "ANONYMOUS",
                patient_id=self.patient_id.get() or "UNKNOWN",
                anatomical_region=anatomical_region,
                view_configs=view_configs,
                thermal_data_dict=thermal_data_dict,
                output_dir=output_dir
            )
            
            if created_files:
                messagebox.showinfo("Success", f"🎉 DICOM series created successfully!\n\nCreated {len(created_files)} files in series.\n\nSaved to: {output_dir}")
                self.status_var.set(f"✅ DICOM series created: {len(created_files)} files")
            else:
                messagebox.showerror("Error", "No DICOM files were created successfully")
                self.status_var.set("❌ Failed to create DICOM series")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating DICOM series: {e}")
            self.status_var.set("❌ Error creating DICOM series")
    
    def validate_inputs(self):
        """Validate form inputs."""
        if not self.input_files:
            messagebox.showerror("Validation Error", "Please select input files")
            return False
        
        if not self.output_folder.get().strip():
            messagebox.showerror("Validation Error", "Please select output folder")
            return False
        
        # Only Patient ID is mandatory for basic functionality
        # All other fields are optional and will use defaults if not provided
        return True
    
    def load_image_data(self, image_path):
        """Load image data from file. Preserves color when present."""
        try:
            image = Image.open(image_path)
            # If image has 3 channels, ensure RGB uint8; if grayscale, keep 2D
            if image.mode in ["RGB", "RGBA"]:
                image = image.convert("RGB")
                array = np.array(image, dtype=np.uint8)  # shape (H, W, 3)
            else:
                image = image.convert('L')
                array = np.array(image, dtype=np.float32)  # shape (H, W)
            return array
        except Exception as e:
            raise ValueError(f"Could not load image: {e}")

    def load_csv_data(self, csv_path):
        """Load numeric matrix from CSV file as float32 2D array."""
        try:
            # Try comma-delimited first
            data = np.genfromtxt(csv_path, delimiter=',')
            if data is None or (isinstance(data, float) and np.isnan(data)):
                # Fallback to whitespace-delimited
                data = np.genfromtxt(csv_path)
            if data.ndim == 1:
                # If single row, try to reshape as a column
                data = data.reshape(-1, 1)
            # Replace NaNs with zeros to avoid issues
            data = np.nan_to_num(data).astype(np.float32)
            return data
        except Exception as e:
            raise ValueError(f"Could not load CSV data: {e}")

    # render_csv_preview method removed - replaced with file information display

    # clear_csv_preview method removed

    # render_image_preview method removed

    # Mouse event methods removed - no longer needed without preview
    
    def generate_sample_data(self):
        """Generate sample thermal data."""
        rows, cols = 512, 512
        x = np.linspace(20, 40, cols)
        y = np.linspace(20, 40, rows)
        X, Y = np.meshgrid(x, y)
        thermal_data = X + Y + 10 * np.sin(X/10) * np.cos(Y/10)
        return thermal_data.astype(np.float32)
    
    # set_metadata method removed - now handled by MultiViewThermalImaging class
    
    def clear_all(self):
        """Clear all form fields."""
        self.input_file.set("")
        self.output_folder.set("")
        
        # Patient Information
        self.patient_name.set("")
        self.patient_id.set("")
        self.patient_age.set("")
        self.patient_gender.set("")
        self.referring_physician.set("")
        
        # Study Information
        self.study_description.set("Thermal Medical Imaging")
        self.organization_uid.set("")
        self.study_id.set("")
        self.accession_number.set("")
        self.study_time.set(datetime.now().strftime("%H%M%S"))
        self.series_time.set(datetime.now().strftime("%H%M%S"))
        self.modality.set("TG")
        self.body_part.set("")
        self.view_position.set("")
        self.patient_position.set("")
        self.laterality.set("")
        self.anatomical_region.set("")
        
        # Thermal Parameters
        self.emissivity.set("0.98")
        self.distance.set("1.0")
        self.ambient_temp.set("22.0")
        self.reflected_temp.set("22.0")
        self.humidity.set("50.0")
        self.camera_model.set("")
        self.acquisition_mode.set("Medical Thermal Imaging")
        self.calibration_date.set(datetime.now().strftime("%Y%m%d"))
        
        self.status_var.set("✅ Ready to create thermal DICOM files")
        self.clear_file_info()
        self.clear_input_files()


def main():
    """Main function to run the enhanced GUI application."""
    root = tk.Tk()
    app = EnhancedDicomCreatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
