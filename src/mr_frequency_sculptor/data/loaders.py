"""Data loading functions."""

import numpy as np
import h5py
import matplotlib.pyplot as plt
from pathlib import Path
from skimage.data import shepp_logan_phantom

from ..config import H5_FILE, MRI_SLICE_IDX, RESULTS_RAW_DIR, FIGURE_SIZE, DPI, get_dataset_raw_dir


def load_phantom():
    """
    Load Shepp-Logan phantom image.
    
    Returns:
        Phantom image as complex64 array.
    """
    img = shepp_logan_phantom().astype(np.complex64)

    # Save original phantom to dataset-specific directory
    dataset_dir = get_dataset_raw_dir("shepp_logan")
    plt.figure(figsize=FIGURE_SIZE)
    im = plt.imshow(np.abs(img), cmap='gray')
    plt.title("Original Phantom")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(dataset_dir / "originals" / "shepp_logan_phantom.png", dpi=DPI, bbox_inches='tight')
    plt.close()

    return img


def load_mri_slice(slice_idx=None, h5_file=None):
    """
    Load MRI slice from H5 file.
    
    Args:
        slice_idx: Slice index (defaults to config value).
        h5_file: Path to H5 file (defaults to config value).
        
    Returns:
        MRI slice image as complex64 array, normalized to [0, 1].
        
    Raises:
        FileNotFoundError: If H5 file doesn't exist.
        KeyError: If required dataset not found in file.
    """
    if slice_idx is None:
        slice_idx = MRI_SLICE_IDX
    if h5_file is None:
        h5_file = H5_FILE

    if not h5_file.exists():
        raise FileNotFoundError(f"MRI data file not found: {h5_file}")

    with h5py.File(h5_file, "r") as f:
        if 'reconstruction_rss' not in f:
            raise KeyError("'reconstruction_rss' not found in H5 file.")
        img_data = f['reconstruction_rss'][slice_idx]  # (256, 256) float32

    img = img_data.astype(np.complex64)
    img_max = img.max()
    if img_max > 0:
        img /= img_max
    else:
        print("Warning: Image is all zero!")

    # Save original MRI slice to dataset-specific directory
    prefix = f"mri_image_slice{slice_idx:03d}"
    dataset_dir = get_dataset_raw_dir(prefix)
    plt.figure(figsize=FIGURE_SIZE)
    im = plt.imshow(np.abs(img), cmap='gray')
    plt.title(f"Original MRI Slice {slice_idx}")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(dataset_dir / "originals" / f"{prefix}_original.png", dpi=DPI, bbox_inches='tight')
    plt.close()

    return img
