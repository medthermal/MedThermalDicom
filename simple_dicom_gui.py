#!/usr/bin/env python3
"""
Simple Thermal DICOM Creator GUI
A professional GUI for creating thermal DICOM files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk, ImageOps

# Add the medthermal_dicom package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from medthermal_dicom.core import MedThermalDicom
    from medthermal_dicom.utils import get_common_organization_uids, validate_organization_uid
except ImportError as e:
    print(f"Error importing medthermal_dicom: {e}")
    sys.exit(1)


class DicomCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal DICOM Creator Pro")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        
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
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#7f8c8d')
        
        # Configure frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Success.TFrame', relief='solid', borderwidth=2, bordercolor='#27ae60')
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Configure entry fields
        style.configure('Modern.TEntry', fieldbackground='#ecf0f1', borderwidth=1)
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Thermal DICOM Creator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Input/Output Section
        io_frame = ttk.LabelFrame(main_frame, text="Input/Output", padding="10")
        io_frame.pack(fill='x', pady=(0, 10))
        
        # Input files
        ttk.Label(io_frame, text="Input Files (Multi-view):").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(io_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=(10, 5), pady=5)
        ttk.Button(io_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, pady=5)
        ttk.Button(io_frame, text="Clear All", command=self.clear_input_files).grid(row=0, column=3, padx=(5, 0), pady=5)

        # File list and preview area
        self.file_listbox = tk.Listbox(io_frame, height=4, width=60)
        self.file_listbox.grid(row=2, column=0, columnspan=4, sticky='w', pady=(10, 0))
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # CSV preview area
        self.preview_label = ttk.Label(io_frame)
        self.preview_label.grid(row=3, column=0, columnspan=4, sticky='w', pady=(10, 0))
        self.hover_value_var = tk.StringVar(value="")
        self.hover_value_label = ttk.Label(io_frame, textvariable=self.hover_value_var)
        self.hover_value_label.grid(row=4, column=0, columnspan=4, sticky='w', pady=(5, 0))
        self.csv_data = None
        self.preview_photo = None
        self.preview_disp_size = (0, 0)
        self.is_temperature_data = False  # Track if input is temperature CSV
        
        # Output folder
        ttk.Label(io_frame, text="Output Folder:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(io_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=(10, 5), pady=5)
        ttk.Button(io_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # Patient Information Section
        patient_frame = ttk.LabelFrame(main_frame, text="Patient Information", padding="10")
        patient_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1
        ttk.Label(patient_frame, text="Patient Name:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(patient_frame, textvariable=self.patient_name, width=30).grid(row=0, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(patient_frame, text="Patient ID:").grid(row=0, column=2, sticky='w', pady=5)
        ttk.Entry(patient_frame, textvariable=self.patient_id, width=20).grid(row=0, column=3, pady=5)
        
        # Row 2
        ttk.Label(patient_frame, text="Age:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(patient_frame, textvariable=self.patient_age, width=10).grid(row=1, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(patient_frame, text="Gender:").grid(row=1, column=2, sticky='w', pady=5)
        gender_combo = ttk.Combobox(patient_frame, textvariable=self.patient_gender, 
                                   values=["", "M", "F", "O"], width=5, state="readonly")
        gender_combo.grid(row=1, column=3, pady=5)
        
        # Row 3
        ttk.Label(patient_frame, text="Referring Physician:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(patient_frame, textvariable=self.referring_physician, width=50).grid(row=2, column=1, columnspan=3, padx=(10, 0), pady=5)
        
        # Study Information Section
        study_frame = ttk.LabelFrame(main_frame, text="Study Information", padding="10")
        study_frame.pack(fill='x', pady=(0, 10))
        
        # Organization UID
        ttk.Label(study_frame, text="Organization UID:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.organization_uid, width=50).grid(row=0, column=1, padx=(10, 5), pady=5)
        ttk.Button(study_frame, text="Common UIDs", command=self.show_common_uids).grid(row=0, column=2, pady=5)
        
        # Study Description
        ttk.Label(study_frame, text="Study Description:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.study_description, width=50).grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=5)
        
        # Dates
        ttk.Label(study_frame, text="Scan Date:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.scan_date, width=20).grid(row=2, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(study_frame, text="Study Date:").grid(row=2, column=2, sticky='w', pady=5)
        ttk.Entry(study_frame, textvariable=self.study_date, width=20).grid(row=2, column=3, pady=5)
        
        # Date format hint
        ttk.Label(study_frame, text="Format: YYYYMMDD (e.g., 20241201)", 
                 font=("Arial", 8), foreground="gray").grid(row=3, column=0, columnspan=4, sticky='w', pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Create DICOM", command=self.create_dicom).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side='left')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x', pady=(10, 0))
    
    def load_common_uids(self):
        """Load common organization UIDs."""
        self.common_uids = get_common_organization_uids()
    
    def show_common_uids(self):
        """Show dialog with common organization UIDs."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Common Organization UIDs")
        dialog.geometry("500x400")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Select an Organization UID:").pack(pady=(0, 10))
        
        listbox = tk.Listbox(frame, height=15)
        listbox.pack(fill='both', expand=True, pady=(0, 10))
        
        for name, uid in self.common_uids.items():
            listbox.insert(tk.END, f"{name}: {uid}")
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                uid = selected_text.split(": ")[1]
                self.organization_uid.set(uid)
                dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left')
    
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
        """Preview the selected file."""
        if filename is None and self.input_files:
            filename = self.input_files[0]
        
        if not filename:
            return
            
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".csv":
            self.is_temperature_data = True
            try:
                self.csv_data = self.load_csv_data(filename)
                self.render_csv_preview(self.csv_data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")
                self.clear_csv_preview()
        else:
            self.is_temperature_data = False
            try:
                self.render_image_preview(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image preview: {e}")
            self.clear_csv_preview()
    
    def clear_input_files(self):
        """Clear all input files."""
        self.input_files = []
        self.input_file.set("")
        self.file_listbox.delete(0, tk.END)
        self.clear_csv_preview()
    
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
        """Create DICOM files from input data."""
        if not self.validate_inputs():
            return
        
        if not self.input_files:
            messagebox.showerror("Error", "Please select input files")
            return
        
        try:
            self.status_var.set("Creating DICOM series...")
            self.root.update()
            
            # Generate base metadata
            patient_id = self.patient_id.get().replace(' ', '_') if self.patient_id.get() else 'UNKNOWN'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create series UID for grouping
            series_uid = f"1.2.826.0.1.3680043.{timestamp}"
            
            created_files = []
            
            for i, input_path in enumerate(self.input_files):
                try:
                    # Load data based on file type
                    ext = os.path.splitext(input_path)[1].lower()
                    if ext == ".csv":
                        thermal_array = self.load_csv_data(input_path)
                        is_temp_data = True
                    else:
                        thermal_array = self.load_image_data(input_path)
                        is_temp_data = False

                    # Create thermal DICOM
                    thermal_dicom = MedThermalDicom(
                        organization_uid_prefix=self.organization_uid.get() if self.organization_uid.get() else None
                    )
                    
                    # For CSV temperature data, set with temperature range for proper DICOM scaling
                    if is_temp_data:
                        temp_min, temp_max = float(np.min(thermal_array)), float(np.max(thermal_array))
                        thermal_dicom.set_thermal_image(thermal_array, temperature_range=(temp_min, temp_max))
                    else:
                        thermal_dicom.set_thermal_image(thermal_array)
                    
                    # Set metadata with series information
                    self.set_metadata(thermal_dicom, series_uid=series_uid, instance_number=i+1)
                    
                    # Generate output filename
                    basename = os.path.splitext(os.path.basename(input_path))[0]
                    output_filename = f"thermal_{patient_id}_{basename}_{timestamp}_{i+1:03d}.dcm"
                    output_path = os.path.join(self.output_folder.get(), output_filename)
                    
                    # Save DICOM
                    thermal_dicom.save_dicom(output_path)
                    created_files.append(output_path)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error processing {os.path.basename(input_path)}: {e}")
                    continue
            
            if created_files:
                messagebox.showinfo("Success", f"DICOM series created successfully!\n\nCreated {len(created_files)} files in series.\n\nSaved to: {self.output_folder.get()}")
                self.status_var.set(f"DICOM series created: {len(created_files)} files")
            else:
                messagebox.showerror("Error", "No DICOM files were created successfully")
                self.status_var.set("Failed to create DICOM series")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating DICOM series: {e}")
            self.status_var.set("Error creating DICOM series")
    
    def validate_inputs(self):
        """Validate user inputs."""
        errors = []
        
        if not self.patient_name.get().strip():
            errors.append("Patient name is required")
        
        if not self.patient_id.get().strip():
            errors.append("Patient ID is required")
        
        if not self.output_folder.get().strip():
            errors.append("Output folder is required")
        
        if not os.path.exists(self.output_folder.get()):
            errors.append("Output folder does not exist")
        
        if self.organization_uid.get().strip():
            is_valid, error_msg = validate_organization_uid(self.organization_uid.get())
            if not is_valid:
                errors.append(f"Invalid Organization UID: {error_msg}")
        
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

    def render_csv_preview(self, data: np.ndarray):
        """Render a small preview and set up hover to show values."""
        try:
            if data.size == 0:
                self.clear_csv_preview()
                return
            dmin = float(np.min(data))
            dmax = float(np.max(data))
            if dmax == dmin:
                norm = np.zeros_like(data, dtype=np.uint8)
            else:
                norm = ((data - dmin) / (dmax - dmin) * 255.0).astype(np.uint8)

            img = Image.fromarray(norm, mode='L')
            try:
                img = ImageOps.colorize(img, black="#001030", white="#ffe680")
            except Exception:
                pass

            max_w, max_h = 256, 256
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            self.preview_disp_size = img.size
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=self.preview_photo)
            self.preview_label.image = self.preview_photo

            self.preview_label.bind("<Motion>", self.on_csv_mouse_move)
            self.preview_label.bind("<Leave>", self.on_csv_mouse_leave)
            self.hover_value_var.set("Hover over preview to see values (°C)")
        except Exception as e:
            self.clear_csv_preview()
            raise e

    def clear_csv_preview(self):
        self.preview_label.configure(image="")
        self.preview_label.image = None
        try:
            self.preview_label.unbind("<Motion>")
            self.preview_label.unbind("<Leave>")
        except Exception:
            pass
        self.hover_value_var.set("")
        self.csv_data = None
        self.preview_photo = None
        self.preview_disp_size = (0, 0)

    def render_image_preview(self, image_path):
        """Render preview for image files."""
        try:
            image = Image.open(image_path)
            max_w, max_h = 256, 256
            image.thumbnail((max_w, max_h), Image.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.preview_photo)
            self.preview_label.image = self.preview_photo
            
            # Show image info
            orig_size = Image.open(image_path).size
            mode = Image.open(image_path).mode
            self.hover_value_var.set(f"Image: {orig_size[0]}×{orig_size[1]}, Mode: {mode}")
        except Exception as e:
            self.clear_csv_preview()
            raise e

    def on_csv_mouse_move(self, event):
        if self.csv_data is None or self.preview_disp_size == (0, 0):
            return
        disp_w, disp_h = self.preview_disp_size
        rows, cols = self.csv_data.shape
        x = max(0, min(event.x, disp_w - 1))
        y = max(0, min(event.y, disp_h - 1))
        col = int(x * cols / disp_w)
        row = int(y * rows / disp_h)
        if 0 <= row < rows and 0 <= col < cols:
            val = float(self.csv_data[row, col])
            self.hover_value_var.set(f"Row {row}, Col {col}: {val:.2f} °C")
            self.status_var.set(f"CSV hover → r={row}, c={col}, temp={val:.2f} °C")

    def on_csv_mouse_leave(self, _event):
        self.hover_value_var.set("")
    
    def generate_sample_data(self):
        """Generate sample thermal data."""
        rows, cols = 512, 512
        x = np.linspace(20, 40, cols)
        y = np.linspace(20, 40, rows)
        X, Y = np.meshgrid(x, y)
        thermal_data = X + Y + 10 * np.sin(X/10) * np.cos(Y/10)
        return thermal_data.astype(np.float32)
    
    def set_metadata(self, thermal_dicom, series_uid=None, instance_number=1):
        """Set metadata in the DICOM object."""
        # Patient information
        thermal_dicom.dataset.PatientName = self.patient_name.get()
        thermal_dicom.dataset.PatientID = self.patient_id.get()
        
        if self.patient_age.get():
            thermal_dicom.dataset.PatientAge = self.patient_age.get()
        
        if self.patient_gender.get():
            thermal_dicom.dataset.PatientSex = self.patient_gender.get()
        
        if self.referring_physician.get():
            thermal_dicom.dataset.ReferringPhysicianName = self.referring_physician.get()
        
        # Study information
        thermal_dicom.dataset.StudyDescription = self.study_description.get()
        
        # Dates
        if self.scan_date.get():
            thermal_dicom.dataset.AcquisitionDate = self.scan_date.get()
        
        if self.study_date.get():
            thermal_dicom.dataset.StudyDate = self.study_date.get()
        
        # Series information for multiple files
        if series_uid:
            thermal_dicom.dataset.SeriesInstanceUID = series_uid
            thermal_dicom.dataset.SeriesNumber = "1"
            thermal_dicom.dataset.InstanceNumber = str(instance_number)
        
        # Thermal parameters
        thermal_params = {
            'emissivity': 0.98,
            'distance_from_camera': 1.0,
            'ambient_temperature': 22.0,
            'temperature_unit': 'Celsius'
        }
        thermal_dicom.set_thermal_parameters(thermal_params)
    
    def clear_all(self):
        """Clear all form fields."""
        self.input_file.set("")
        self.output_folder.set("")
        self.patient_name.set("")
        self.patient_id.set("")
        self.patient_age.set("")
        self.patient_gender.set("")
        self.referring_physician.set("")
        self.study_description.set("Thermal Medical Imaging")
        self.organization_uid.set("")
        self.status_var.set("Ready")
        self.clear_csv_preview()
        self.is_temperature_data = False
        self.clear_input_files()


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = DicomCreatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
