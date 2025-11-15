#!/usr/bin/env python3
"""
Enhanced Thermal DICOM Creator GUI
A modern GUI for creating thermal DICOM files.
Designed for thousands of users with enterprise-grade UI/UX.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk, ImageOps


class ToolTip:
    """Create a tooltip for a given widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", 
                        relief="solid", borderwidth=1, font=("Segoe UI", 9))
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Add the medthermal_dicom package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from medthermal_dicom.core import MedThermalDicom
    from medthermal_dicom.metadata import MedThermalMetadata
    from medthermal_dicom.utils import get_common_organization_uids, validate_organization_uid
except ImportError as e:
    print(f"Error importing medthermal_dicom: {e}")
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
        self.main_canvas = tk.Canvas(self.root, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        scrollable_frame = ttk.Frame(self.main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create window with full width
        canvas_window = self.main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Make scrollable_frame expand to canvas width
        def on_canvas_configure(event):
            self.main_canvas.itemconfig(canvas_window, width=event.width)
        
        self.main_canvas.bind("<Configure>", on_canvas_configure)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling anywhere on the window
        def on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to root window (works anywhere in the GUI)
        self.root.bind("<MouseWheel>", on_mousewheel)
        
        # Also bind to canvas for good measure
        self.main_canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Pack canvas and scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title section with logo
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill='x', pady=(10, 15))
        
        title_label = ttk.Label(title_frame, text="🔥 MedTherm DICOM", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Medical Imaging Software for Research & Clinical Use", 
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(2, 0))
        
        # Input/Output Section
        io_frame = ttk.LabelFrame(scrollable_frame, text="📁 Input/Output Management", 
                                 padding="10", style='Card.TLabelframe')
        io_frame.pack(fill='x', pady=(0, 15), padx=15)
        
        # Input file section
        input_frame = ttk.Frame(io_frame)
        input_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(input_frame, text="📸 Input File:", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        input_controls = ttk.Frame(input_frame)
        input_controls.pack(fill='x')
        
        ttk.Entry(input_controls, textvariable=self.input_file, width=60, 
                 style='Modern.TEntry').pack(side='left', fill='x', expand=True, padx=(0, 10))
        ttk.Button(input_controls, text="📂 Browse File", command=self.browse_input, 
                  style='Primary.TButton').pack(side='left', padx=(0, 5))
        ttk.Button(input_controls, text="🗑️ Clear", command=self.clear_input_file, 
                  style='Danger.TButton').pack(side='left')
        
        # File info display
        info_frame = ttk.Frame(input_frame)
        info_frame.pack(fill='x', pady=(15, 0))
        
        self.file_info_var = tk.StringVar(value="Select a file to see information")
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
        
        # Configure grid columns
        patient_frame.columnconfigure(0, weight=0, minsize=120)  # Label column
        patient_frame.columnconfigure(1, weight=1)  # Input column
        patient_frame.columnconfigure(2, weight=0, minsize=80)   # Label column
        patient_frame.columnconfigure(3, weight=0, minsize=100)  # Input column
        
        # Row 1: Patient Name and Age
        ttk.Label(patient_frame, text="Patient Name: *", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 10), padx=(0, 5))
        patient_name_entry = ttk.Entry(patient_frame, textvariable=self.patient_name, width=25, 
                 style='Modern.TEntry')
        patient_name_entry.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(0, 20))
        
        ttk.Label(patient_frame, text="Age: *", style='Header.TLabel').grid(
            row=0, column=2, sticky='w', pady=(0, 10), padx=(0, 5))
        patient_age_entry = ttk.Entry(patient_frame, textvariable=self.patient_age, width=10, 
                 style='Modern.TEntry')
        patient_age_entry.grid(row=0, column=3, sticky='w', pady=(0, 10))
        ToolTip(patient_age_entry, "Enter age in years (e.g., 45)")
        
        # Row 2: Patient ID and Gender
        ttk.Label(patient_frame, text="Patient ID: *", style='Header.TLabel').grid(
            row=1, column=0, sticky='w', pady=(0, 10), padx=(0, 5))
        patient_id_entry = ttk.Entry(patient_frame, textvariable=self.patient_id, width=25, 
                 style='Modern.TEntry')
        patient_id_entry.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(0, 20))
        
        ttk.Label(patient_frame, text="Gender:", style='Header.TLabel').grid(
            row=1, column=2, sticky='w', pady=(0, 10), padx=(0, 5))
        gender_combo = ttk.Combobox(patient_frame, textvariable=self.patient_gender, 
                                   values=["", "M", "F", "O"], width=8, state="readonly",
                                   style='Modern.TCombobox')
        gender_combo.grid(row=1, column=3, sticky='w', pady=(0, 10))
        
        # Row 3: Referring Physician (spans all columns)
        ttk.Label(patient_frame, text="Referring Physician:", style='Header.TLabel').grid(
            row=2, column=0, sticky='w', pady=(0, 5), padx=(0, 5))
        ttk.Entry(patient_frame, textvariable=self.referring_physician, width=50, 
                 style='Modern.TEntry').grid(row=2, column=1, columnspan=3, sticky='ew')
        
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
        
        org_uid_entry = ttk.Entry(uid_controls, textvariable=self.organization_uid, width=60, 
                 style='Modern.TEntry')
        org_uid_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        ToolTip(org_uid_entry, "Optional - If empty, a unique UID will be auto-generated")
        ttk.Button(uid_controls, text="📋 Example UIDs", command=self.show_common_uids, 
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
        accession_entry = ttk.Entry(accession_frame, textvariable=self.accession_number, width=20, 
                 style='Modern.TEntry')
        accession_entry.pack(fill='x')
        ToolTip(accession_entry, "Optional - Only required for hospital/PACS integration")
        
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
                                     values=["TG"], 
                                     width=10, state="disabled", style='Modern.TCombobox')
        modality_combo.pack(fill='x')
        ToolTip(modality_combo, "TG (Thermography) for thermal imaging")
        
        ttk.Label(body_part_frame, text="Body Part Examined:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.body_part = tk.StringVar()
        body_part_combo = ttk.Combobox(body_part_frame, textvariable=self.body_part, 
                                      values=["", "BREAST", "HAND", "FOOT", "FACE", "CHEST", "ABDOMEN", "BACK", "WHOLE BODY"], 
                                      width=15, state="readonly", style='Modern.TCombobox')
        body_part_combo.pack(fill='x')
        
        # Row 4: View Position and Laterality
        study_row4 = ttk.Frame(additional_frame)
        study_row4.pack(fill='x', pady=(0, 10))
        
        view_pos_frame = ttk.Frame(study_row4)
        view_pos_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        laterality_frame = ttk.Frame(study_row4)
        laterality_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(view_pos_frame, text="View Position:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.view_position = tk.StringVar()
        view_pos_combo = ttk.Combobox(view_pos_frame, textvariable=self.view_position, 
                                     values=["", "A", "P", "L", "R", "OBL", "LAT", "PA", "AP", 
                                            "FFS", "HFS", "HFP", "FFP", "HFDL", "HFDR", "FFDL", "FFDR"], 
                                     width=10, state="readonly", style='Modern.TCombobox')
        view_pos_combo.pack(fill='x')
        
        ttk.Label(laterality_frame, text="Laterality:", style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        self.laterality = tk.StringVar()
        laterality_combo = ttk.Combobox(laterality_frame, textvariable=self.laterality, 
                                       values=["", "L", "R", "B"], 
                                       width=10, state="readonly", style='Modern.TCombobox')
        laterality_combo.pack(fill='x')
        
        
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
        
        ttk.Button(action_buttons, text="🚀 Create DICOM", command=self.create_dicom, 
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
        uid_window.geometry("700x400")
        uid_window.transient(self.root)
        uid_window.grab_set()
        
        # Add content
        ttk.Label(uid_window, text="Common Organization UIDs", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Create listbox
        listbox = tk.Listbox(uid_window, font=('Consolas', 9), selectmode='single')
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add UIDs with names (store mapping)
        uid_mapping = {}
        for name, uid in self.common_uids.items():
            display_text = f"{name}: {uid}"
            listbox.insert(tk.END, display_text)
            uid_mapping[display_text] = uid
        
        # Add copy button
        def copy_selected():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                selected_uid = uid_mapping[selected_text]
                uid_window.clipboard_clear()
                uid_window.clipboard_append(selected_uid)
                self.organization_uid.set(selected_uid)
                uid_window.destroy()
                messagebox.showinfo("Selected", f"UID set to:\n{selected_uid}")
        
        ttk.Button(uid_window, text="Select UID", command=copy_selected).pack(pady=10)
    
    def show_help(self):
        """Show help information."""
        help_text = """
MedTherm DICOM - Help

📁 Input File:
• Select a single image file (PNG, JPG, TIFF, BMP) or CSV file
• CSV files should contain temperature data in Celsius
• Images will be processed as thermal data

👤 Patient Information:
• Fill in patient details for DICOM metadata
• Patient ID is recommended for file naming

🔬 Study Information:
• Organization UID: Your institution's unique identifier
• Study Description: Brief description of the imaging study
• Dates: Use YYYYMMDD format (e.g., 20241201)

🌡️ Thermal Parameters:
• Emissivity: Surface emissivity (default: 0.98 for human skin)
• Distance: Distance from camera in meters
• Ambient Temperature: Room temperature in °C
• Other parameters for accurate temperature calibration

🚀 Creating DICOM:
• Click 'Create DICOM' to process the file
• File is saved with a descriptive name including patient ID and timestamp
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
        """Browse for input file."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.tiff *.tif *.bmp"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Input File", filetypes=filetypes)
        if filename:
            self.input_file.set(filename)
            self.preview_selected_file(filename)
    
    
    def preview_selected_file(self, filename=None):
        """Show file information for the selected file."""
        if filename is None:
            filename = self.input_file.get()
        
        if not filename or not os.path.exists(filename):
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
        self.file_info_var.set("Select a file to see information")
        self.csv_data = None
        self.is_temperature_data = False
    
    def clear_input_file(self):
        """Clear input file."""
        self.input_file.set("")
        self.clear_file_info()
    
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def create_dicom(self):
        """Create DICOM file from input data."""
        if not self.validate_inputs():
            return
        
        input_file = self.input_file.get().strip()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
        
        try:
            self.status_var.set("🔄 Creating DICOM file...")
            self.root.update()
            
            # Get organization UID (generate if empty)
            org_uid = self.organization_uid.get().strip()
            if not org_uid:
                # Auto-generate using pydicom if not provided
                from pydicom.uid import generate_uid
                org_uid = generate_uid()
                self.status_var.set("🔄 Auto-generated Organization UID...")
                self.root.update()
            else:
                # Validate if provided
                if not validate_organization_uid(org_uid):
                    messagebox.showerror("Error", "Invalid Organization UID format")
                    return
            
            # Create output directory if it doesn't exist
            output_dir = self.output_folder.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Load data based on file type
            ext = os.path.splitext(input_file)[1].lower()
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            
            self.status_var.set(f"🔄 Loading file: {base_name}")
            self.root.update()
            
            if ext == ".csv":
                thermal_array = self.load_csv_data(input_file)
            else:
                thermal_array = self.load_image_data(input_file)
            
            # Create MedThermalDicom instance
            thermal_dicom = MedThermalDicom(organization_uid_prefix=org_uid)
            
            # Create metadata handler for proper SNOMED CT coding
            metadata = MedThermalMetadata(organization_uid_prefix=org_uid)
            
            # Set thermal image data
            if thermal_array.ndim == 3:
                # Color image
                thermal_dicom.set_thermal_image(thermal_array)
            else:
                # Temperature data
                temp_min, temp_max = float(thermal_array.min()), float(thermal_array.max())
                thermal_dicom.set_thermal_image(thermal_array, thermal_array, (temp_min, temp_max))
            
            self.status_var.set("🔄 Setting metadata...")
            self.root.update()
            
            # Set equipment information using standard DICOM fields
            equipment_info = metadata.set_equipment_information(
                manufacturer=self.camera_model.get().split()[0].upper() if self.camera_model.get() else "THERMAL_IMAGING",
                manufacturer_model=self.camera_model.get() or "Thermal Camera",
                software_version="MedThermalDICOM_v1.0"
            )
            
            # Set thermal parameters (only the ones that are in PRIVATE_OFFSETS)
            thermal_params = {
                'emissivity': float(self.emissivity.get()),
                'distance_from_camera': float(self.distance.get()),
                'ambient_temperature': float(self.ambient_temp.get()),
                'reflected_temperature': float(self.reflected_temp.get()),
                'relative_humidity': float(self.humidity.get())
            }
            thermal_dicom.set_thermal_parameters(thermal_params)
            
            # Set patient information
            thermal_dicom.dataset.PatientName = self.patient_name.get() or "ANONYMOUS"
            thermal_dicom.dataset.PatientID = self.patient_id.get() or "UNKNOWN"
            
            # Format age properly for DICOM (must be nnnY, nnnM, nnnW, or nnnD)
            if self.patient_age.get():
                try:
                    age_value = int(self.patient_age.get())
                    # Format as 3-digit number followed by 'Y' for years
                    thermal_dicom.dataset.PatientAge = f"{age_value:03d}Y"
                except ValueError:
                    # If not a number, try to use as-is (user might have entered formatted value)
                    thermal_dicom.dataset.PatientAge = self.patient_age.get()
            
            if self.patient_gender.get():
                thermal_dicom.dataset.PatientSex = self.patient_gender.get()
            
            if self.referring_physician.get():
                thermal_dicom.dataset.ReferringPhysicianName = self.referring_physician.get()
            
            # Set study information
            thermal_dicom.dataset.StudyDescription = self.study_description.get()
            thermal_dicom.dataset.StudyDate = self.study_date.get()
            thermal_dicom.dataset.StudyTime = self.study_time.get()
            # SeriesDate should be a date (YYYYMMDD), not time
            thermal_dicom.dataset.SeriesDate = self.scan_date.get()
            thermal_dicom.dataset.SeriesTime = self.series_time.get()
            
            if self.study_id.get():
                thermal_dicom.dataset.StudyID = self.study_id.get()
            
            if self.accession_number.get():
                thermal_dicom.dataset.AccessionNumber = self.accession_number.get()
            
            # Map GUI body part values to metadata keys for SNOMED CT coding
            body_part_mapping = {
                'BREAST': 'breast',
                'HAND': 'hand',
                'FOOT': 'foot',
                'FACE': 'face',
                'CHEST': 'chest',
                'ABDOMEN': 'abdomen',
                'BACK': 'back',
                'WHOLE BODY': 'whole_body'
            }
            
            # Use metadata handler to set series information with SNOMED CT codes
            body_part_key = None
            if self.body_part.get():
                body_part_key = body_part_mapping.get(self.body_part.get().upper())
            
            series_info = metadata.set_series_information(
                series_description=self.study_description.get() or "Thermal Imaging",
                series_number=1,
                modality=self.modality.get(),
                body_part=body_part_key,
                laterality=self.laterality.get() if self.laterality.get() else None
            )
            
            # Apply series information with SNOMED CT codes to dataset
            # This also applies equipment information (Manufacturer, ManufacturerModelName, etc.)
            metadata.apply_metadata_to_dataset(thermal_dicom.dataset)
            
            # Set view position separately (not part of series_info)
            if self.view_position.get():
                thermal_dicom.dataset.ViewPosition = self.view_position.get()
            
            # Store acquisition mode in a standard DICOM field
            if self.acquisition_mode.get():
                thermal_dicom.dataset.AcquisitionDeviceProcessingDescription = self.acquisition_mode.get()
            
            # Store calibration date
            if self.calibration_date.get():
                thermal_dicom.dataset.CalibrationDate = self.calibration_date.get()
            
            # Generate output filename
            patient_id = self.patient_id.get() or "UNKNOWN"
            patient_id = patient_id.replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"thermal_{patient_id}_{base_name}_{timestamp}.dcm"
            output_path = os.path.join(output_dir, output_filename)
            
            self.status_var.set("🔄 Saving DICOM file...")
            self.root.update()
            
            # Save DICOM file
            thermal_dicom.save_dicom(output_path)
            
            messagebox.showinfo("Success", f"🎉 DICOM file created successfully!\n\nSaved to:\n{output_path}")
            self.status_var.set(f"✅ DICOM file created successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating DICOM file: {e}")
            self.status_var.set("❌ Error creating DICOM file")
            import traceback
            traceback.print_exc()
    
    def validate_inputs(self):
        """Validate form inputs."""
        errors = []
        
        if not self.input_file.get().strip():
            errors.append("Please select an input file")
        
        if not self.output_folder.get().strip():
            errors.append("Please select output folder")
        
        # Validate mandatory patient fields
        if not self.patient_name.get().strip():
            errors.append("Patient Name is required (marked with *)")
        
        if not self.patient_id.get().strip():
            errors.append("Patient ID is required (marked with *)")
        
        if not self.patient_age.get().strip():
            errors.append("Patient Age is required (marked with *)")
        else:
            # Validate age is a number
            try:
                age_val = int(self.patient_age.get())
                if age_val < 0 or age_val > 150:
                    errors.append("Age must be between 0 and 150")
            except ValueError:
                errors.append("Age must be a valid number")
        
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Validation Error", error_message)
            return False
        
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
        self.laterality.set("")
        
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
        self.clear_input_file()


def main():
    """Main function to run the enhanced GUI application."""
    root = tk.Tk()
    app = EnhancedDicomCreatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
