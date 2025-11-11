"""Image quality metrics."""

import numpy as np
from scipy import ndimage


def calculate_sharpness(image):
    """
    Measure edge sharpness using Sobel gradient.
    
    Args:
        image: Image array.
        
    Returns:
        Mean gradient magnitude (sharpness metric).
    """
    gx = ndimage.sobel(image, axis=0, mode='nearest')
    gy = ndimage.sobel(image, axis=1, mode='nearest')
    return np.mean(np.sqrt(gx ** 2 + gy ** 2))


def calculate_noise(image, corner_frac=0.08):
    """
    Estimate noise from corner region.
    
    Args:
        image: Image array.
        corner_frac: Fraction of image size to use for corner region.
        
    Returns:
        Standard deviation of corner region (noise estimate).
    """
    h, w = image.shape
    corner_size_h = max(1, int(h * corner_frac))
    corner_size_w = max(1, int(w * corner_frac))
    corner = image[0:corner_size_h, 0:corner_size_w]
    return np.std(corner)


def calculate_mae(img1, img2):
    """
    Calculate Mean Absolute Error between two images.

    Args:
        img1: First image array.
        img2: Second image array.

    Returns:
        Mean absolute error.
    """
    return np.mean(np.abs(img1 - img2))
