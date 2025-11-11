"""
Main script for processing k-space data from MRI images.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.mr_frequency_sculptor.data import load_phantom, load_mri_slice
from src.mr_frequency_sculptor.kspace import image_to_kspace
from src.mr_frequency_sculptor.kspace.processing import reconstruct_all_versions
from src.mr_frequency_sculptor.kspace.io import save_kspace
from src.mr_frequency_sculptor.config import RESULTS_RAW_DIR, MRI_SLICE_IDX, get_dataset_raw_dir


def process_phantom():
    """Process Shepp-Logan phantom."""
    print("Processing Shepp-Logan phantom...")
    prefix = "shepp_logan"
    img = load_phantom()
    kspace = image_to_kspace(img)
    dataset_dir = get_dataset_raw_dir(prefix)
    save_kspace(prefix, kspace, original_image=img.real, output_dir=dataset_dir)
    reconstruct_all_versions(kspace, prefix)


def process_mri_image():
    """Process real MRI slice."""
    print(f"Processing MRI slice {MRI_SLICE_IDX}...")
    try:
        img = load_mri_slice()
        kspace = image_to_kspace(img)
        prefix = f"mri_image_slice{MRI_SLICE_IDX:03d}"
        dataset_dir = get_dataset_raw_dir(prefix)
        save_kspace(prefix, kspace, original_image=img.real, output_dir=dataset_dir)
        reconstruct_all_versions(kspace, prefix)
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Skipping MRI processing.")
    except KeyError as e:
        print(f"Error: {e}")
        print("Skipping MRI processing.")


if __name__ == "__main__":
    print("=" * 60)
    print("MR Frequency Sculptor - K-Space Processing")
    print("=" * 60)
    print()

    process_phantom()
    process_mri_image()

    print(f"\nAll results saved to: {RESULTS_RAW_DIR}")
    print("   Organized by dataset in subdirectories:")
    print("   - results/raw/shepp_logan/")
    print("   - results/raw/mri_image_slice000/")
    print("\n   Each dataset contains subdirectories:")
    print("   - originals/            → Original images")
    print("   - kspace/               → K-space visualizations (magnitude, phase, real)")
    print("   - reconstructions/      → Reconstruction images (full, partial, lowpass, highpass)")
    print("   - data/                 → NPZ files (kspace data and reconstruction arrays)")
