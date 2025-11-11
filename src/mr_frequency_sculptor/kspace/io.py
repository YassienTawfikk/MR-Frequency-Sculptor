"""K-space I/O functions."""

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from ..config import RESULTS_RAW_DIR, FIGURE_SIZE, DPI, COLORMAP


def save_reconstructed_image(name, image, output_dir=None):
    """
    Save reconstructed image as PNG.
    
    Args:
        name: Name for the saved file (without extension).
        image: Image array to save.
        output_dir: Output directory (defaults to RESULTS_RAW_DIR/reconstructions).
    """
    if output_dir is None:
        output_dir = RESULTS_RAW_DIR / "reconstructions"
    else:
        output_dir = output_dir / "reconstructions"

    plt.figure(figsize=FIGURE_SIZE)
    plt.imshow(image, cmap=COLORMAP, vmin=0, vmax=1)
    plt.title(f"{name}")
    plt.axis('off')
    plt.colorbar(fraction=0.046)
    plt.savefig(output_dir / f"{name}.png", dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"Saved: {name}.png")


def save_kspace(prefix, kspace, original_image=None, output_dir=None):
    """
    Save k-space as 3 PNGs (magnitude, phase, real) + .npz file.
    
    Args:
        prefix: Dataset prefix for file naming (e.g., "shepp_logan").
        kspace: K-space data to save.
        original_image: Original image array (optional, saved in npz).
        output_dir: Output directory (defaults to RESULTS_RAW_DIR/kspace).
    """
    if output_dir is None:
        kspace_dir = RESULTS_RAW_DIR / "kspace"
        data_dir = RESULTS_RAW_DIR / "data"
    else:
        kspace_dir = output_dir / "kspace"
        data_dir = output_dir / "data"

    mag = np.abs(kspace)
    mag_log = np.log(mag + 1)  # avoid log(0)
    phase = np.angle(kspace)
    real_part = np.real(kspace)

    # Magnitude
    plt.figure(figsize=FIGURE_SIZE)
    plt.imshow(mag_log, cmap='gray')
    plt.title(f"{prefix} – log|magnitude|")
    plt.axis('off')
    plt.savefig(kspace_dir / f"{prefix}_magnitude.png", dpi=DPI, bbox_inches='tight')
    plt.close()

    # Phase
    plt.figure(figsize=FIGURE_SIZE)
    im = plt.imshow(phase, cmap='gray')
    plt.title(f"{prefix} – phase")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(kspace_dir / f"{prefix}_phase.png", dpi=DPI, bbox_inches='tight')
    plt.close()

    # Real part
    plt.figure(figsize=FIGURE_SIZE)
    im = plt.imshow(real_part, cmap='gray')
    plt.title(f"{prefix} – real(k-space)")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(kspace_dir / f"{prefix}_real.png", dpi=DPI, bbox_inches='tight')
    plt.close()

    # Save as npz
    save_dict = {'kspace': kspace, 'magnitude': mag, 'phase': phase, 'real': real_part}
    if original_image is not None:
        save_dict['image'] = original_image
    np.savez(data_dir / f"{prefix}_kspace.npz", **save_dict)

    print(f"Saved: {prefix}_magnitude.png, {prefix}_phase.png, {prefix}_real.png, {prefix}_kspace.npz")


def save_reconstructions(prefix, full_raw, partial_raw, lowpass_raw, highpass_raw, output_dir=None):
    """
    Save all reconstruction arrays to npz file.
    
    Args:
        prefix: Dataset prefix for the saved file.
        full_raw: Full reconstruction array.
        partial_raw: Partial k-space reconstruction array.
        lowpass_raw: Low-pass filtered reconstruction array.
        highpass_raw: High-pass filtered reconstruction array.
        output_dir: Output directory (defaults to RESULTS_RAW_DIR/data).
    """
    if output_dir is None:
        data_dir = RESULTS_RAW_DIR / "data"
    else:
        data_dir = output_dir / "data"

    np.savez(
        data_dir / f"{prefix}_reconstructions.npz",
        full_raw=full_raw,
        partial_raw=partial_raw,
        lowpass_raw=lowpass_raw,
        highpass_raw=highpass_raw
    )
    print(f"Saved raw reconstructions to: {prefix}_reconstructions.npz")
