"""K-space filtering functions."""

import numpy as np


def gaussian_kspace_mask(shape, sigma_fraction=0.1):
    """
    Create a centered Gaussian mask for k-space filtering.
    
    Args:
        shape: Shape of the k-space array (rows, cols).
        sigma_fraction: Fraction of image size to use for sigma (relative to max dimension).
        
    Returns:
        Gaussian mask array.
    """
    rows, cols = shape
    u = np.arange(-rows // 2, rows // 2)
    v = np.arange(-cols // 2, cols // 2)
    V, U = np.meshgrid(v, u)  # note: meshgrid(v,u) matches array ordering
    d2 = U ** 2 + V ** 2
    # scale sigma with the smaller dimension
    sigma = sigma_fraction * max(rows, cols)
    mask = np.exp(-d2 / (2.0 * (sigma ** 2)))
    return mask


def simulate_partial_kspace(kspace: np.ndarray, fraction: float = 0.5) -> np.ndarray:
    """
    Simulate partial k-space acquisition by masking center region.
    
    Args:
        kspace: Full k-space data.
        fraction: Fraction of k-space to retain (0.0 to 1.0).
        
    Returns:
        Masked k-space array.
    """
    rows, cols = kspace.shape
    center_r, center_c = rows // 2, cols // 2
    half_r, half_c = int(rows * fraction / 2), int(cols * fraction / 2)
    mask = np.zeros_like(kspace, dtype=bool)
    mask[center_r - half_r:center_r + half_r, center_c - half_c:center_c + half_c] = True
    return kspace * mask


def apply_lowpass_filter(kspace: np.ndarray, sigma_fraction: float = 0.05) -> np.ndarray:
    """
    Apply low-pass filter to k-space (preserves low frequencies).
    
    Args:
        kspace: K-space data to filter.
        sigma_fraction: Fraction of image size for Gaussian sigma.
        
    Returns:
        Filtered k-space array.
    """
    mask = gaussian_kspace_mask(kspace.shape, sigma_fraction=sigma_fraction)
    # mask is real; preserve complex kspace by multiplying
    return kspace * mask


def apply_highpass_filter(kspace: np.ndarray, sigma_fraction: float = 0.05) -> np.ndarray:
    """
    Apply high-pass filter to k-space (preserves high frequencies).
    
    Args:
        kspace: K-space data to filter.
        sigma_fraction: Fraction of image size for Gaussian sigma.
        
    Returns:
        Filtered k-space array.
    """
    mask = gaussian_kspace_mask(kspace.shape, sigma_fraction=sigma_fraction)
    return kspace * (1.0 - mask)

