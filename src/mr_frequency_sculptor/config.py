"""Configuration settings for MR Frequency Sculptor."""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_RAW_DIR = RESULTS_DIR / "raw"
RESULTS_ANALYSIS_DIR = RESULTS_DIR / "analysis"

# Data files
H5_FILE = DATA_DIR / "mri.h5"  # from `https://github.com/mylyu/M4Raw`
MRI_SLICE_IDX = 0  # 0 to 17

# Processing parameters
PARTIAL_KSpace_FRACTION = 0.5
LOWPASS_SIGMA_FRACTION = 0.05
HIGHPASS_SIGMA_FRACTION = 0.05

# Visualization settings
FIGURE_SIZE = (5, 5)
DPI = 150
COLORMAP = 'gray'

# Create directories if they don't exist
for directory in [DATA_DIR, RESULTS_DIR, RESULTS_RAW_DIR, RESULTS_ANALYSIS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
