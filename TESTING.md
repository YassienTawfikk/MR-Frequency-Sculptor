# Testing Guide

## Quick Start

### 1. Install Dependencies

First, make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### 2. Run K-Space Processing

Process MRI images and generate k-space reconstructions:

```bash
python scripts/process_kspace.py
```

This will:
- ✅ Process the Shepp-Logan phantom (always works)
- ✅ Process real MRI slice (if `data/mri.h5` exists)
- ✅ Generate k-space visualizations
- ✅ Create all reconstruction types
- ✅ Save results to `results/raw/`

**Expected output:**
- `results/raw/shepp_logan_*.png` - K-space visualizations
- `results/raw/shepp_logan_recon_*.png` - Reconstructions
- `results/raw/shepp_logan_recons.npz` - Raw data arrays
- `results/raw/mri_image_slice000_*.png` - (if MRI data available)

### 3. Run Analysis

Analyze the reconstruction quality:

```bash
python scripts/analyze_results.py
```

This will:
- ✅ Calculate quality metrics (sharpness, noise, MAE)
- ✅ Generate comparison plots
- ✅ Create difference maps
- ✅ Save results to `results/analysis/`

**Expected output:**
- `results/analysis/shepp_logan_comparison.png`
- `results/analysis/mri_image_slice000_comparison.png` (if MRI data available)

## Full Test Workflow

```bash
# Step 1: Process k-space
python scripts/process_kspace.py

# Step 2: Analyze results
python scripts/analyze_results.py
```

## Verify Installation

Test that the package can be imported:

```bash
python -c "import sys; sys.path.insert(0, 'src'); from mr_frequency_sculptor import config; print('✓ Package works!')"
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

## Expected Results

After running both scripts, you should have:

```
results/
├── raw/
│   ├── original_phantom.png
│   ├── shepp_logan_mag.png
│   ├── shepp_logan_phase.png
│   ├── shepp_logan_kspace.png
│   ├── shepp_logan_recon_full.png
│   ├── shepp_logan_recon_partial.png
│   ├── shepp_logan_recon_lowpass.png
│   ├── shepp_logan_recon_highpass.png
│   └── shepp_logan_recons.npz
└── analysis/
    └── shepp_logan_comparison.png
```

