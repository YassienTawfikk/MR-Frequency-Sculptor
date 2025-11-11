"""K-space reconstruction functions."""

import numpy as np
from scipy.fft import ifft2, ifftshift


def reconstruct_image_from_kspace(kspace: np.ndarray) -> np.ndarray:
    """
    Reconstruct image from k-space data.
    
    Args:
        kspace: K-space data expected to be FFTSHIFTed (zero-frequency at center).
        
    Returns:
        Reconstructed image as absolute magnitude.
    """
    # kspace is expected to be FFTSHIFTed (zero-frequency at center).
    # To invert: first ifftshift, then ifft2.
    return np.abs(ifft2(ifftshift(kspace)))


def normalize_by_reference(img: np.ndarray, ref_max: float) -> np.ndarray:
    """
    Normalize image by reference maximum value.
    
    Args:
        img: Image array to normalize.
        ref_max: Reference maximum value for normalization.
        
    Returns:
        Normalized image array.
    """
    if ref_max == 0:
        return img.copy()
    return img / ref_max

