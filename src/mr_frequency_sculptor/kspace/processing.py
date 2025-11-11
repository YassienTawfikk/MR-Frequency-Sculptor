"""K-space processing pipeline functions."""

import numpy as np
from scipy.fft import fft2, fftshift

from .reconstruction import reconstruct_image_from_kspace, normalize_by_reference
from .filters import simulate_partial_kspace, apply_lowpass_filter, apply_highpass_filter
from .io import save_reconstructed_image, save_kspace, save_reconstructions
from ..config import (
    PARTIAL_KSpace_FRACTION,
    LOWPASS_SIGMA_FRACTION,
    HIGHPASS_SIGMA_FRACTION,
    RESULTS_RAW_DIR
)


def image_to_kspace(image):
    """
    Convert image to k-space using 2D FFT.
    
    Args:
        image: Image array (can be complex or real).
        
    Returns:
        K-space array (FFTSHIFTed, zero-frequency at center).
    """
    return fftshift(fft2(image))


def reconstruct_all_versions(kspace, prefix):
    """
    Reconstruct images from k-space using multiple methods and save results.
    
    Args:
        kspace: Full k-space data.
        prefix: Prefix for saved files.
    """
    # Raw full reconstruction (not shifted/normalized)
    full_raw = reconstruct_image_from_kspace(kspace)  # absolute magnitude
    full_max = full_raw.max() if full_raw.size > 0 else 1.0

    # Normalize everyone by the same reference maximum (full image)
    full_img = normalize_by_reference(full_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_full", full_img, RESULTS_RAW_DIR)

    # Partial k-space reconstruction
    partial_kspace = simulate_partial_kspace(kspace, fraction=PARTIAL_KSpace_FRACTION)
    partial_raw = reconstruct_image_from_kspace(partial_kspace)
    partial_img = normalize_by_reference(partial_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_partial", partial_img, RESULTS_RAW_DIR)

    # Low-pass filtered reconstruction
    lowpass_kspace = apply_lowpass_filter(kspace, sigma_fraction=LOWPASS_SIGMA_FRACTION)
    lowpass_raw = reconstruct_image_from_kspace(lowpass_kspace)
    lowpass_img = normalize_by_reference(lowpass_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_lowpass", lowpass_img, RESULTS_RAW_DIR)

    # High-pass filtered reconstruction
    highpass_kspace = apply_highpass_filter(kspace, sigma_fraction=HIGHPASS_SIGMA_FRACTION)
    highpass_raw = reconstruct_image_from_kspace(highpass_kspace)
    highpass_img = normalize_by_reference(highpass_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_highpass", highpass_img, RESULTS_RAW_DIR)

    # Save raw arrays into an npz for precise analysis later
    save_reconstructions(prefix, full_raw, partial_raw, lowpass_raw, highpass_raw, RESULTS_RAW_DIR)

    print(f"\n{prefix}_recon_full serves as the gold standard for comparison.")
    print("It uses the complete k-space data, representing the highest fidelity reconstruction.\n")
