"""
Main GUI window for MR Frequency Sculptor.
"""

import sys
import time
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QGroupBox,
    QGridLayout, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import h5py

# Import project modules
from ..data.loaders import load_phantom
from ..kspace import image_to_kspace
from ..kspace.reconstruction import reconstruct_image_from_kspace, normalize_by_reference
from ..kspace.filters import (
    simulate_partial_kspace, apply_lowpass_filter, apply_highpass_filter
)
from ..analysis.metrics import calculate_sharpness, calculate_noise, calculate_mae
from ..config import (
    H5_FILE, PARTIAL_KSpace_FRACTION, LOWPASS_SIGMA_FRACTION, HIGHPASS_SIGMA_FRACTION
)


class ProcessingThread(QThread):
    """Thread for processing k-space to avoid freezing UI."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, original_image, image, kspace, processing_type, partial_fraction=None, sigma_fraction=None):
        super().__init__()
        self.original_image = original_image  # Ground Truth Image
        self.image = image
        self.kspace = kspace
        self.processing_type = processing_type
        self.partial_fraction = partial_fraction or PARTIAL_KSpace_FRACTION
        self.sigma_fraction = sigma_fraction or LOWPASS_SIGMA_FRACTION

    def run(self):
        try:
            if self.processing_type == 'full':
                result = reconstruct_image_from_kspace(self.kspace)
                ref_max = result.max() if result.max() != 0 else 1.0
                result = normalize_by_reference(result, ref_max)
            elif self.processing_type == 'partial':
                partial_kspace = simulate_partial_kspace(self.kspace, fraction=self.partial_fraction)
                result = reconstruct_image_from_kspace(partial_kspace)
                ref_max = self.image.max() if self.image.max() != 0 else 1.0
                result = normalize_by_reference(result, ref_max)
            elif self.processing_type == 'lowpass':
                lowpass_kspace = apply_lowpass_filter(self.kspace, sigma_fraction=self.sigma_fraction)
                result = reconstruct_image_from_kspace(lowpass_kspace)
                ref_max = self.image.max() if self.image.max() != 0 else 1.0
                result = normalize_by_reference(result, ref_max)
            elif self.processing_type == 'highpass':
                highpass_kspace = apply_highpass_filter(self.kspace, sigma_fraction=self.sigma_fraction)
                result = reconstruct_image_from_kspace(highpass_kspace)
                ref_max = self.image.max() if self.image.max() != 0 else 1.0
                result = normalize_by_reference(result, ref_max)
            else:
                raise ValueError(f"Unknown processing type: {self.processing_type}")

            # Calculate metrics
            sharpness = calculate_sharpness(result)
            noise = calculate_noise(result)
            # Calculate Mean Absolute Error (MAE) against the Ground Truth
            mae = calculate_mae(self.original_image, result)

            self.finished.emit({
                'image': result,
                'sharpness': sharpness,
                'noise': noise,
                'mae': mae,  # Return MAE
                'type': self.processing_type
            })
        except Exception as e:
            self.error.emit(str(e))


class ImageDisplayWidget(QWidget):
    """Widget for displaying images with title."""

    def __init__(self, title="Image", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Title - Made an instance variable for easy updating
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.title_label)

        # Matplotlib canvas
        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # Set a dark background for the plot area
        self.figure.patch.set_facecolor('#2d2d30')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2d2d30')
        self.ax.axis('off')
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def display_image(self, image):
        """Display image."""
        self.ax.clear()
        self.ax.axis('off')

        if image is not None:
            # Special case for difference map: use 'hot' colormap to highlight errors
            if self.title_label.text().startswith("Difference Map"):
                self.ax.imshow(image, cmap='hot', vmin=0, vmax=image.max() if image.max() > 0 else 1e-6)
            else:
                self.ax.imshow(image, cmap='gray', vmin=0, vmax=1)

        # Redraw the canvas
        self.canvas.draw()


class MetricsDisplayWidget(QWidget):
    """Widget for displaying metrics in a centralized, professional format."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MetricsWidget")
        self.setup_ui()

    def setup_ui(self):
        # Use QGridLayout for structured, centered, professional layout
        layout = QGridLayout()
        layout.setContentsMargins(15, 15, 15, 15)  # Add internal padding
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)

        # Row 0: Title
        title_label = QLabel("Reconstruction Metrics")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setObjectName("MetricsTitle")
        layout.addWidget(title_label, 0, 0, 1, 2)

        # Row 1: Header/Status
        self.header_label = QLabel("Select a processing method to analyze results.")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Arial", 10))
        self.header_label.setObjectName("MetricsHeader")
        layout.addWidget(self.header_label, 1, 0, 1, 2)  # Span two columns

        # Row 2: Sharpness
        layout.addWidget(QLabel("Sharpness (Edge Retention Index):"), 2, 0, Qt.AlignLeft)
        self.sharpness_label = QLabel("N/A")
        self.sharpness_label.setObjectName("DataLabel")
        layout.addWidget(self.sharpness_label, 2, 1, Qt.AlignRight)

        # Row 3: Noise
        layout.addWidget(QLabel("Noise (Texture Level Index):"), 3, 0, Qt.AlignLeft)
        self.noise_label = QLabel("N/A")
        self.noise_label.setObjectName("DataLabel")
        layout.addWidget(self.noise_label, 3, 1, Qt.AlignRight)

        # Row 4: MAE
        layout.addWidget(QLabel("MAE (Mean Absolute Error vs GT):"), 4, 0, Qt.AlignLeft)
        self.mae_label = QLabel("N/A")
        self.mae_label.setObjectName("DataLabel")
        layout.addWidget(self.mae_label, 4, 1, Qt.AlignRight)

        # Ensure content is vertically centered/pushed to the top
        layout.setRowStretch(5, 1)
        layout.setColumnStretch(0, 1)  # Description column stretch
        layout.setColumnStretch(1, 1)  # Data column stretch

        self.setLayout(layout)

    def update_metrics(self, processing_type, metrics):
        """Update the displayed metrics using individual labels."""
        if metrics:

            # Format the processing type name for the header
            if processing_type == 'full':
                name = 'Full K-Space (Ideal)'
            elif processing_type == 'partial':
                name = 'Partial K-Space'
            elif processing_type == 'lowpass':
                name = 'Low-Pass Filter'
            elif processing_type == 'highpass':
                name = 'High-Pass Filter'
            else:
                name = processing_type.capitalize()

            self.header_label.setText(f"CURRENT RECONSTRUCTION: {name}")
            self.sharpness_label.setText(f"{metrics.get('sharpness', 0):.4f}")
            self.noise_label.setText(f"{metrics.get('noise', 0):.4f}")
            self.mae_label.setText(f"{metrics.get('error', 0):.4f}")
        else:
            self.header_label.setText("Select a processing method to analyze results.")
            self.sharpness_label.setText("N/A")
            self.noise_label.setText("N/A")
            self.mae_label.setText("N/A")


class MRFrequencySculptorApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_kspace = None
        self.reconstructions = {}
        self.processing_threads = []
        self.setup_ui()

    def setup_ui(self):
        # Set professional title with logo
        self.setWindowTitle("MR Frequency Sculptor | Biomedical Signal Processing Tool")
        # Set the logo as the application icon (top-left of the window frame)
        self.setWindowIcon(QIcon("../assets/logo.png"))

        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Image displays
        right_panel = self.create_display_panel()
        main_layout.addWidget(right_panel, stretch=3)

        # Apply styles (must be called after setting up widgets)
        self.apply_styles()

        # Open in full screen (Maximize)
        self.showMaximized()

    def create_control_panel(self):
        """Create the left control panel (Tight fit)."""
        panel = QWidget()
        panel.setObjectName("ControlPanel")
        panel.setMaximumWidth(350)
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Image Selection Group
        selection_group = QGroupBox("Image Selection")
        selection_layout = QVBoxLayout()

        # Load Phantom button
        self.btn_phantom = QPushButton("Load Shepp-Logan Phantom")
        self.btn_phantom.clicked.connect(self.load_phantom)
        selection_layout.addWidget(self.btn_phantom)

        # Load MRI from H5 file
        mri_layout = QHBoxLayout()
        self.btn_load_mri = QPushButton("Load MRI from H5")
        self.btn_load_mri.clicked.connect(self.load_mri_file)
        mri_layout.addWidget(self.btn_load_mri)

        self.slice_spinbox = QSpinBox()
        self.slice_spinbox.setMinimum(0)
        self.slice_spinbox.setMaximum(17)
        self.slice_spinbox.setValue(0)
        self.slice_spinbox.setEnabled(False)
        self.slice_spinbox.valueChanged.connect(self.on_slice_changed)
        mri_layout.addWidget(QLabel("Slice:"))
        mri_layout.addWidget(self.slice_spinbox)
        selection_layout.addLayout(mri_layout)

        # Load from file button
        self.btn_load_file = QPushButton("Load Image from File")
        self.btn_load_file.clicked.connect(self.load_image_file)
        selection_layout.addWidget(self.btn_load_file)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Processing Group
        processing_group = QGroupBox("K-Space Processing")
        processing_layout = QVBoxLayout()

        self.btn_process_full = QPushButton("1. Full K-Space (Reference)")
        self.btn_process_full.clicked.connect(lambda: self.process_image('full'))
        self.btn_process_full.setEnabled(False)
        processing_layout.addWidget(self.btn_process_full)

        self.btn_process_partial = QPushButton("2. Partial K-Space (Sampling)")
        self.btn_process_partial.clicked.connect(lambda: self.process_image('partial'))
        self.btn_process_partial.setEnabled(False)
        processing_layout.addWidget(self.btn_process_partial)

        self.btn_process_lowpass = QPushButton("3. Low-Pass Filter (Smoothing)")
        self.btn_process_lowpass.clicked.connect(lambda: self.process_image('lowpass'))
        self.btn_process_lowpass.setEnabled(False)
        processing_layout.addWidget(self.btn_process_lowpass)

        self.btn_process_highpass = QPushButton("4. High-Pass Filter (Edge Enhancement)")
        self.btn_process_highpass.clicked.connect(lambda: self.process_image('highpass'))
        self.btn_process_highpass.setEnabled(False)
        processing_layout.addWidget(self.btn_process_highpass)

        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)

        # Parameters Group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout()

        # Partial k-space fraction
        partial_layout = QHBoxLayout()
        partial_layout.addWidget(QLabel("Partial Fraction:"))
        self.partial_spinbox = QSpinBox()
        self.partial_spinbox.setMinimum(1)
        self.partial_spinbox.setMaximum(100)
        self.partial_spinbox.setValue(int(PARTIAL_KSpace_FRACTION * 100))
        self.partial_spinbox.setSuffix("%")
        partial_layout.addWidget(self.partial_spinbox)
        params_layout.addLayout(partial_layout)

        # Sigma fraction
        sigma_layout = QHBoxLayout()
        sigma_layout.addWidget(QLabel("Filter Sigma:"))
        self.sigma_spinbox = QSpinBox()
        self.sigma_spinbox.setMinimum(1)
        self.sigma_spinbox.setMaximum(20)
        self.sigma_spinbox.setValue(int(LOWPASS_SIGMA_FRACTION * 1000))
        self.sigma_spinbox.setSuffix("%")
        sigma_layout.addWidget(self.sigma_spinbox)
        params_layout.addLayout(sigma_layout)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Exit Button
        self.btn_exit = QPushButton("Exit Application")
        self.btn_exit.setObjectName("ExitButton")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        panel.setLayout(layout)
        return panel

    def create_display_panel(self):
        """
        Create the right display panel with the final 2x2 layout:
        Row 1: Original | Reconstructed
        Row 2: Difference Map | Metrics Panel
        """
        panel = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Professional Title Bar (Top Right Element)
        title_bar = QHBoxLayout()
        title_bar.addStretch(1)

        # 1. Logo beside title (using QPixmap and scaling)
        self.logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("../assets/logo.png")
            # Scale logo to a reasonable size, e.g., 20px height for the title bar
            scaled_pixmap = logo_pixmap.scaledToHeight(20, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            # Add logo to the bar
            title_bar.addWidget(self.logo_label)
        except Exception:
            # Fallback if logo file cannot be loaded/found at runtime
            pass

            # 2. Title Label (Emoji removed, increased font size)
        title_label = QLabel("K-Space Frequency Domain Analysis")
        title_label.setObjectName("DisplayTitleLabel")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_bar.addWidget(title_label)

        main_layout.addLayout(title_bar)

        # Main Display Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Row 0: Original Image and Reconstructed Image
        self.original_display = ImageDisplayWidget("Original Image (Ground Truth)")
        grid_layout.addWidget(self.original_display, 0, 0)

        self.reconstructed_display = ImageDisplayWidget("Reconstructed Image (Select a Method)")
        grid_layout.addWidget(self.reconstructed_display, 0, 1)

        # Row 1: Difference Map and Metrics Panel

        # 3. Difference Map (now only 1 column)
        self.error_display = ImageDisplayWidget("Difference Map (Absolute Error vs GT)")
        grid_layout.addWidget(self.error_display, 1, 0)

        # 4. Metrics Panel (NEW)
        self.metrics_display = MetricsDisplayWidget()
        grid_layout.addWidget(self.metrics_display, 1, 1)

        # Ensure rows and columns stretch equally to fill space
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        main_layout.addLayout(grid_layout)
        panel.setLayout(main_layout)
        return panel

    def apply_styles(self):
        """Apply modern dark styling to the application."""
        DARK_BG = "#1e1e1e"
        CONTROL_BG = "#2d2d30"
        TEXT_COLOR = "#cccccc"
        ACCENT_COLOR = "#007acc"  # Deep Blue/Teal accent
        BUTTON_HOVER = "#005a99"

        self.setStyleSheet(f"""
            /* Main Window Background */
            QMainWindow {{
                background-color: {DARK_BG};
            }}
            
            /* Left Control Panel Container */
            QWidget#ControlPanel {{
                background-color: {CONTROL_BG};
                padding: 10px;
            }}
            
            QGroupBox {{
                background-color: {CONTROL_BG};
                color: {TEXT_COLOR};
                font-weight: bold;
                border: 1px solid #444444;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {ACCENT_COLOR};
            }}
            
            /* Standard Button Style */
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                padding: 10px 5px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 25px;
                text-align: center;
            }}
            
            QPushButton:hover {{
                background-color: {BUTTON_HOVER};
            }}
            
            QPushButton:pressed {{
                background-color: #004d80;
            }}
            
            QPushButton:disabled {{
                background-color: #444444;
                color: #aaaaaa;
            }}
            
            /* Specific style for Exit Button */
            QPushButton#ExitButton {{
                background-color: #e81123; /* Red color for Exit/Danger */
                margin-top: 10px;
            }}
            
            QPushButton#ExitButton:hover {{
                background-color: #b80d1b;
            }}

            QLabel {{
                color: {TEXT_COLOR};
            }}
            
            QLabel#StatusLabel {{
                font-style: italic;
                padding: 5px;
            }}
            
            QLabel#DisplayTitleLabel {{
                color: {ACCENT_COLOR};
                padding: 5px;
                margin-right: 10px;
            }}
            
            /* Modern QSpinBox Styling */
            QSpinBox {{
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 6px;
                padding-right: 25px; /* Make space for buttons */
                background-color: #3e3e42;
                color: {TEXT_COLOR};
                selection-background-color: {ACCENT_COLOR};
                min-height: 28px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border;
                width: 20px; /* Width of the button area */
                border-left: 1px solid #444444; /* Separator line */
                background-color: #2d2d30; /* Control background color */
            }}
            QSpinBox::up-button {{
                subcontrol-position: top right;
                height: 14px; /* Half of min-height */
                border-top-right-radius: 4px;
                border-bottom-right-radius: 0;
            }}
            QSpinBox::down-button {{
                subcontrol-position: bottom right;
                height: 14px; /* Half of min-height */
                border-top-right-radius: 0;
                border-bottom-right-radius: 4px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #444444; /* Slight hover effect */
            }}

            /* Custom Arrows using borders */
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                width: 0px; 
                height: 0px;
                image: none; 
            }}
            QSpinBox::up-arrow {{
                border-width: 0 4px 4px 4px;
                border-style: solid;
                border-top-color: transparent;
                border-left-color: transparent;
                border-right-color: transparent;
                border-bottom-color: {ACCENT_COLOR}; /* Accent color */
                padding-bottom: 3px;
            }}
            QSpinBox::down-arrow {{
                border-width: 4px 4px 0 4px;
                border-style: solid;
                border-top-color: {ACCENT_COLOR}; /* Accent color */
                border-left-color: transparent;
                border-right-color: transparent;
                border-bottom-color: transparent;
                padding-top: 3px;
            }}

            QProgressBar {{
                border: 1px solid {ACCENT_COLOR};
                border-radius: 4px;
                text-align: center;
                color: white;
                background-color: #3e3e42;
            }}
            
            QProgressBar::chunk {{
                background-color: {ACCENT_COLOR};
            }}

            /* Metrics Display Widget */
            QWidget#MetricsWidget {{
                background-color: #3e3e42; 
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 15px; 
                margin: 0;
            }}
            QLabel#MetricsTitle {{
                color: {ACCENT_COLOR};
                font-size: 18pt; 
                padding-bottom: 10px;
                border-bottom: 1px solid #555555;
            }}
            QLabel#MetricsHeader {{
                color: #ffffff;
                font-size: 12pt; 
                font-weight: bold;
                padding-top: 10px;
                padding-bottom: 5px;
            }}
            QLabel#DataLabel {{
                color: #4CAF50; /* Green/Success color for data */
                font-size: 16pt; 
                font-family: 'Courier New', monospace; /* Monospaced font fix */
                font-weight: bold;
                padding-top: 5px;
                padding-bottom: 5px;
            }}
            /* Standard QLabel for descriptive text within metrics widget */
            QWidget#MetricsWidget QLabel {{
                color: {TEXT_COLOR};
                font-size: 10pt;
                padding-left: 5px;
                padding-right: 5px;
            }}
        """)

    def load_phantom(self):
        """Load Shepp-Logan phantom."""
        try:
            self.status_label.setText("Loading phantom...")
            QApplication.processEvents()

            img = load_phantom()
            self.current_image = np.abs(img)
            self.current_kspace = image_to_kspace(img)

            self.original_display.display_image(self.current_image)
            # Clear other displays
            self.reconstructed_display.title_label.setText("Reconstructed Image (Select a Method)")
            self.reconstructed_display.display_image(None)
            self.error_display.display_image(None)
            self.metrics_display.update_metrics(None, None)  # Clear metrics
            self.reconstructions = {}  # Reset stored reconstructions

            self.enable_processing_buttons()
            self.status_label.setText("Phantom loaded successfully! Ready for processing.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load phantom:\n{str(e)}")
            self.status_label.setText("Error loading phantom")

    def load_mri_file(self):
        """Load MRI H5 file and enable slice selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MRI H5 File", str(H5_FILE.parent), "H5 Files (*.h5 *.hdf5)"
        )

        if file_path:
            try:
                # Check if file has the right structure
                with h5py.File(file_path, 'r') as f:
                    if 'reconstruction_rss' not in f:
                        raise KeyError("'reconstruction_rss' not found in H5 file")
                    num_slices = f['reconstruction_rss'].shape[0]
                    self.slice_spinbox.setMaximum(num_slices - 1)
                    self.slice_spinbox.setValue(0)
                    self.slice_spinbox.setEnabled(True)

                    # Store file path and load first slice
                    self.mri_file_path = file_path
                    self.load_mri_slice(0)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load MRI file:\n{str(e)}")
                self.status_label.setText("Error loading MRI file")

    def load_mri_slice(self, slice_idx):
        """Load a specific MRI slice."""
        if not hasattr(self, 'mri_file_path'):
            return

        try:
            self.status_label.setText(f"Loading MRI slice {slice_idx}...")
            QApplication.processEvents()

            with h5py.File(self.mri_file_path, 'r') as f:
                img_data = f['reconstruction_rss'][slice_idx]

            img = img_data.astype(np.complex64)
            img_max = img.max()
            if img_max > 0:
                img /= img_max

            self.current_image = np.abs(img)
            self.current_kspace = image_to_kspace(img)

            self.original_display.display_image(self.current_image)
            # Clear other displays
            self.reconstructed_display.title_label.setText("Reconstructed Image (Select a Method)")
            self.reconstructed_display.display_image(None)
            self.error_display.display_image(None)
            self.metrics_display.update_metrics(None, None)  # Clear metrics
            self.reconstructions = {}  # Reset stored reconstructions

            self.enable_processing_buttons()
            self.status_label.setText(f"MRI slice {slice_idx} loaded successfully! Ready for processing.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load MRI slice:\n{str(e)}")
            self.status_label.setText("Error loading MRI slice")

    def load_image_file(self):
        """Load image from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.png *.jpg *.jpeg *.tif *.tiff *.npy *.npz);;All Files (*)"
        )

        if file_path:
            try:
                self.status_label.setText("Loading image...")
                QApplication.processEvents()

                path = Path(file_path)
                if path.suffix.lower() in ['.npy', '.npz']:
                    if path.suffix == '.npy':
                        img = np.load(file_path)
                    else:
                        data = np.load(file_path)
                        # Try common keys
                        if 'image' in data:
                            img = data['image']
                        elif 'data' in data:
                            img = data['data']
                        else:
                            img = data[list(data.keys())[0]]
                else:
                    from matplotlib.image import imread
                    img = imread(file_path)
                    if img.ndim == 3:
                        img = np.mean(img[:, :, :3], axis=2)
                    if img.max() > 1.5:
                        img = img / 255.0

                # Convert to complex and normalize
                img = img.astype(np.complex64)
                img_max = np.abs(img).max()
                if img_max > 0:
                    img = img / img_max

                self.current_image = np.abs(img)
                self.current_kspace = image_to_kspace(img)

                self.original_display.display_image(self.current_image)
                # Clear other displays
                self.reconstructed_display.title_label.setText("Reconstructed Image (Select a Method)")
                self.reconstructed_display.display_image(None)
                self.error_display.display_image(None)
                self.metrics_display.update_metrics(None, None)  # Clear metrics
                self.reconstructions = {}  # Reset stored reconstructions

                self.enable_processing_buttons()
                self.status_label.setText("Image loaded successfully! Ready for processing.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image:\n{str(e)}")
                self.status_label.setText("Error loading image")

    def enable_processing_buttons(self):
        """Enable processing buttons when image is loaded."""
        self.btn_process_full.setEnabled(True)
        self.btn_process_partial.setEnabled(True)
        self.btn_process_lowpass.setEnabled(True)
        self.btn_process_highpass.setEnabled(True)

    def process_image(self, processing_type):
        """Process image with specified method."""
        if self.current_image is None or self.current_kspace is None:
            QMessageBox.warning(self, "Warning", "Please load an image first!")
            return

        self.status_label.setText(f"Processing {processing_type}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        QApplication.processEvents()

        # Get parameters from spinboxes
        partial_fraction = self.partial_spinbox.value() / 100.0
        sigma_fraction = self.sigma_spinbox.value() / 1000.0

        # Create and start processing thread, passing the Ground Truth image
        thread = ProcessingThread(
            self.current_image,  # Ground Truth (for MAE)
            self.current_image,
            self.current_kspace,
            processing_type,
            partial_fraction=partial_fraction,
            sigma_fraction=sigma_fraction
        )
        thread.finished.connect(lambda result: self.on_processing_finished(result))
        thread.error.connect(self.on_processing_error)
        thread.start()
        self.processing_threads.append(thread)

    def on_slice_changed(self, value):
        """Handle slice selection change."""
        if hasattr(self, 'mri_file_path'):
            self.load_mri_slice(value)

    def on_processing_finished(self, result):
        """Handle processing completion."""
        processing_type = result['type']
        image = result['image']
        mae = result['mae']
        metrics = {
            'sharpness': result['sharpness'],
            'noise': result['noise'],
            'error': mae
        }

        # Store processed image
        self.reconstructions[processing_type] = image

        # Determine display name
        if processing_type == 'full':
            display_name = 'Full K-Space (Ideal Reconstruction)'
        elif processing_type == 'partial':
            display_name = 'Partial K-Space Reconstruction'
        elif processing_type == 'lowpass':
            display_name = 'Low-Pass Filtered Reconstruction'
        elif processing_type == 'highpass':
            display_name = 'High-Pass Filtered Reconstruction'
        else:
            display_name = processing_type.capitalize()

        # 1. Update the reconstructed display
        self.reconstructed_display.title_label.setText(f"Reconstructed Image ({display_name})")
        self.reconstructed_display.display_image(image)

        # 2. Update error display (Absolute difference between Ground Truth and Reconstructed Image)
        diff = np.abs(self.current_image - image)
        self.error_display.display_image(diff)

        # 3. Update the dedicated metrics display
        self.metrics_display.update_metrics(processing_type, metrics)

        self.progress_bar.setVisible(False)
        self.status_label.setText(f"{display_name} processing completed!")

    def on_processing_error(self, error_msg):
        """Handle processing error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Processing Error", f"An error occurred:\n{error_msg}")
        self.status_label.setText("Processing error occurred")

    def closeEvent(self, event):
        """Clean up threads on close."""
        for thread in self.processing_threads:
            if thread.isRunning():
                thread.terminate()
                thread.wait()
        event.accept()
