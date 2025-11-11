"""Visualization functions for analysis results."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from .metrics import calculate_sharpness, calculate_noise, calculate_mae
from ..config import RESULTS_RAW_DIR, RESULTS_ANALYSIS_DIR


def load_image(filepath: Path) -> np.ndarray:
    """
    Load grayscale image without re-normalizing to [0,1] automatically.
    
    Args:
        filepath: Path to image file.
        
    Returns:
        Image array as float32.
    """
    img = plt.imread(filepath)
    if img.ndim == 3:
        img = np.mean(img[:, :, :3], axis=2)  # drop alpha if any
    img = img.astype(np.float32)
    # If PNG saved as 8-bit, convert to [0,1]
    if img.max() > 1.5:
        img /= 255.0
    return img


def _hide_ticks_and_spines(ax):
    """Hide ticks and spines but keep axis labels visible."""
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def analyze_dataset(prefix: str):
    """
    Load images, calculate metrics, and create comparison visualization.
    
    Args:
        prefix: Prefix for dataset files (e.g., "shepp_logan", "mri_image_slice000").
    """
    print(f"\n{'=' * 60}")
    print(f"Analyzing: {prefix}")
    print(f"{'=' * 60}\n")

    # Prefer raw npz reconstructions if available
    npz_path = RESULTS_RAW_DIR / f"{prefix}_recons.npz"
    if npz_path.exists():
        data = np.load(npz_path)
        full_raw = data['full_raw']
        partial_raw = data['partial_raw']
        lowpass_raw = data['lowpass_raw']
        highpass_raw = data['highpass_raw']

        # Normalize all by the reference full image max so metrics are comparable
        ref_max = full_raw.max() if full_raw.max() != 0 else 1.0
        full_img = full_raw / ref_max
        partial_img = partial_raw / ref_max
        lowpass_img = lowpass_raw / ref_max
        highpass_img = highpass_raw / ref_max
    else:
        # Fallback to PNG images (assumes the main script saved a consistent scale)
        full_img = load_image(RESULTS_RAW_DIR / f"{prefix}_recon_full.png")
        partial_img = load_image(RESULTS_RAW_DIR / f"{prefix}_recon_partial.png")
        lowpass_img = load_image(RESULTS_RAW_DIR / f"{prefix}_recon_lowpass.png")
        highpass_img = load_image(RESULTS_RAW_DIR / f"{prefix}_recon_highpass.png")

    # Calculate metrics
    images = {
        'Full k-space': full_img,
        'Partial (50%)': partial_img,
        'Low-pass': lowpass_img,
        'High-pass': highpass_img
    }

    print(f"{'Version':<20} {'Sharpness':<12} {'Noise':<12} {'Error':<12}")
    print("-" * 56)

    for name, img in images.items():
        sharpness = calculate_sharpness(img)
        noise = calculate_noise(img)
        error = calculate_mae(full_img, img) if name != 'Full k-space' else 0.0
        print(f"{name:<20} {sharpness:<12.4f} {noise:<12.4f} {error:<12.4f}")

    # Create comparison plot
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    # Top row: Images
    axes[0, 0].imshow(full_img, cmap='gray', vmin=0, vmax=1)
    axes[0, 0].set_title('Full k-space\n(Reference)', fontsize=11, pad=10)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(partial_img, cmap='gray', vmin=0, vmax=1)
    axes[0, 1].set_title('Partial k-space\n(50% center)', fontsize=11, pad=10)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(lowpass_img, cmap='gray', vmin=0, vmax=1)
    axes[0, 2].set_title('Low-pass filtered', fontsize=11, pad=10)
    axes[0, 2].axis('off')

    axes[0, 3].imshow(highpass_img, cmap='gray', vmin=0, vmax=1)
    axes[0, 3].set_title('High-pass filtered', fontsize=11, pad=10)
    axes[0, 3].axis('off')

    # Bottom row: Difference maps
    axes[1, 0].text(0.5, 0.5, 'Reference\n(no difference)', ha='center', va='center',
                    fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')

    # Partial - Full difference
    diff1 = np.abs(full_img - partial_img)
    im1 = axes[1, 1].imshow(diff1, cmap='hot')
    _hide_ticks_and_spines(axes[1, 1])
    axes[1, 1].set_xlabel(f'Partial - Full\nMAE: {np.mean(diff1):.4f}', fontsize=10, labelpad=10)
    plt.colorbar(im1, ax=axes[1, 1], fraction=0.046, pad=0.04)

    # Low-pass - Full difference
    diff2 = np.abs(full_img - lowpass_img)
    im2 = axes[1, 2].imshow(diff2, cmap='hot')
    _hide_ticks_and_spines(axes[1, 2])
    axes[1, 2].set_xlabel(f'Low-pass - Full\nMAE: {np.mean(diff2):.4f}', fontsize=10, labelpad=10)
    plt.colorbar(im2, ax=axes[1, 2], fraction=0.046, pad=0.04)

    # High-pass - Full difference
    diff3 = np.abs(full_img - highpass_img)
    im3 = axes[1, 3].imshow(diff3, cmap='hot')
    _hide_ticks_and_spines(axes[1, 3])
    axes[1, 3].set_xlabel(f'High-pass - Full\nMAE: {np.mean(diff3):.4f}', fontsize=10, labelpad=10)
    plt.colorbar(im3, ax=axes[1, 3], fraction=0.046, pad=0.04)

    plt.suptitle(f'Comparison: {prefix}', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for suptitle
    plt.savefig(RESULTS_ANALYSIS_DIR / f"{prefix}_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {prefix}_comparison.png\n")

