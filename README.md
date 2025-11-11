# MR Frequency Sculptor

A Python tool for exploring k-space (frequency domain) manipulations in MRI image reconstruction. This project demonstrates how different k-space filtering strategies affect image quality, sharpness, and artifacts.

## Features

- **K-space Processing**: Convert MRI images to k-space using 2D FFT
- **Multiple Reconstruction Methods**:
  - Full k-space (reference/gold standard)
  - Partial k-space (simulates undersampling)
  - Low-pass filtering (preserves low frequencies)
  - High-pass filtering (preserves high frequencies)
- **Quality Analysis**: Quantitative metrics (sharpness, noise, MAE) and visual comparisons
- **Support for Multiple Data Sources**: Synthetic phantoms (Shepp-Logan) and real MRI data
- **Automated Reports**: Text reports with detailed metrics and statistics

## Project Structure

```
MR-Frequency-Sculptor/
├── src/
│   └── mr_frequency_sculptor/
│       ├── __init__.py
│       ├── config.py              # Configuration settings
│       ├── kspace/                 # K-space processing module
│       │   ├── __init__.py
│       │   ├── reconstruction.py  # Image reconstruction functions
│       │   ├── filters.py          # K-space filtering functions
│       │   ├── io.py               # I/O operations
│       │   └── processing.py       # Processing pipeline
│       ├── data/                   # Data loading module
│       │   ├── __init__.py
│       │   └── loaders.py          # Data loading functions
│       └── analysis/               # Analysis module
│           ├── __init__.py
│           ├── metrics.py          # Quality metrics
│           └── visualization.py   # Visualization functions
├── scripts/
│   ├── process_kspace.py          # Main processing script
│   └── analyze_results.py          # Analysis script
├── data/                           # Data files directory
│   └── mri.h5                      # MRI data (from M4Raw dataset)
├── results/                        # Output directory
│   ├── raw/                        # Raw k-space and reconstructions
│   └── analysis/                   # Analysis results and comparisons
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MR-Frequency-Sculptor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download MRI data (optional):
   - The project expects `mri.h5` in the `data/` directory
   - Data source: [M4Raw dataset](https://github.com/mylyu/M4Raw)
   - If not available, the script will process only the Shepp-Logan phantom

## Usage

### Quick Start

**Step 1: Process K-space Data**

Process MRI images and generate k-space reconstructions:

```bash
python scripts/process_kspace.py
```

This will:
- Process the Shepp-Logan phantom (always works)
- Process real MRI slice (if `data/mri.h5` exists)
- Generate k-space visualizations (magnitude, phase, real part)
- Create reconstructions using all methods
- Save results to `results/raw/`

**Step 2: Analyze Results**

Analyze reconstruction quality and generate comparison plots:

```bash
python scripts/analyze_results.py
```

This will:
- Calculate quality metrics (sharpness, noise, MAE)
- Generate side-by-side comparison plots
- Create difference maps showing artifacts
- Generate text reports with detailed metrics
- Save results to `results/analysis/`

### Full Workflow

```bash
# Step 1: Process k-space
python scripts/process_kspace.py

# Step 2: Analyze results
python scripts/analyze_results.py
```

## Configuration

Edit `src/mr_frequency_sculptor/config.py` to customize:

- `MRI_SLICE_IDX`: Which MRI slice to process (0-17)
- `PARTIAL_KSpace_FRACTION`: Fraction of k-space to retain (default: 0.5)
- `LOWPASS_SIGMA_FRACTION`: Low-pass filter sigma (default: 0.05)
- `HIGHPASS_SIGMA_FRACTION`: High-pass filter sigma (default: 0.05)

## Output Files

### Raw Results (`results/raw/`)

Results are organized by dataset with subdirectories for better structure:

```
results/raw/
├── shepp_logan/
│   ├── originals/
│   │   └── shepp_logan_phantom.png
│   ├── kspace/
│   │   ├── shepp_logan_magnitude.png
│   │   ├── shepp_logan_phase.png
│   │   └── shepp_logan_real.png
│   ├── reconstructions/
│   │   ├── shepp_logan_full.png
│   │   ├── shepp_logan_partial.png
│   │   ├── shepp_logan_lowpass.png
│   │   └── shepp_logan_highpass.png
│   └── data/
│       ├── shepp_logan_kspace.npz
│       └── shepp_logan_reconstructions.npz
└── mri_image_slice000/
    └── (same structure)
```

### Analysis Results (`results/analysis/`)
- `*_comparison.png`: Side-by-side comparison with difference maps
- `*_report.txt`: Detailed text report with metrics and statistics

The report files include:
- Image quality metrics (Sharpness, Noise, MAE)
- Difference analysis (comparing each method to full k-space)
- Image statistics (min, max, mean, std)
- Timestamp and metric descriptions

## Testing

### Verify Installation

Test that the package can be imported:

```bash
python -c "import sys; sys.path.insert(0, 'src'); from src.mr_frequency_sculptor import config; print('✓ Package works!')"
```

### Expected Results

After running both scripts, you should have:

```
results/
├── raw/
│   ├── shepp_logan/
│   │   ├── originals/
│   │   ├── kspace/
│   │   ├── reconstructions/
│   │   └── data/
│   └── mri_image_slice000/
│       └── (same structure)
└── analysis/
    ├── shepp_logan_comparison.png
    ├── shepp_logan_report.txt
    └── mri_image_slice000_*.png (if MRI data available)
```

## Troubleshooting

### Missing Dependencies
If you get `ModuleNotFoundError`, install requirements:
```bash
pip install -r requirements.txt
```

### Missing MRI Data
If `data/mri.h5` is missing, the script will:
- ✅ Still process the Shepp-Logan phantom
- ⚠️ Skip MRI processing with a warning
- ✅ Continue normally

### Import Errors
If you get import errors, make sure you're running from the project root:
```bash
cd /path/to/MR-Frequency-Sculptor
python scripts/process_kspace.py
```

### Missing Files Error
If you run the analysis script before processing, you'll get a helpful error message:
```
Error: Required files not found for 'shepp_logan'.
Please run 'python scripts/process_kspace.py' first to generate the data.
```

## Project History / Migration Notes

This project was restructured for better organization and maintainability.

### Old vs New Structure

**Old files (removed):**
- `main.py` → Replaced by `scripts/process_kspace.py`
- `kspace_analysis.py` → Replaced by `scripts/analyze_results.py`

**Old output directories (removed):**
- `kspace_results/` → Replaced by `results/raw/`
- `kspace_analysis/` → Replaced by `results/analysis/`

**New structure:**
- Source code: `src/mr_frequency_sculptor/`
- Scripts: `scripts/`
- Data: `data/`
- Results: `results/raw/` and `results/analysis/`

All configuration is now centralized in `src/mr_frequency_sculptor/config.py`.

## Dependencies

- numpy >= 2.1.2
- matplotlib >= 3.9.2
- scipy >= 1.14.1
- h5py >= 3.12.1
- scikit-image >= 0.24.0

## License

[Add your license here]

## Acknowledgments

- MRI data from [M4Raw dataset](https://github.com/mylyu/M4Raw)
- Shepp-Logan phantom from scikit-image
