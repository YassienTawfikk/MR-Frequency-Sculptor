import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

# Configuration
OUT_DIR = "kspace_results"
RESULTS_DIR = "kspace_analysis"
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_image_for_analysis(filepath, crop_title=True):
    """Load image for analysis, optionally cropping title region."""
    img = plt.imread(filepath)
    if img.ndim == 3:
        img = np.mean(img[:, :, :3], axis=2)  # drop alpha if any
    img = img.astype(np.float32)

    # If PNG saved as 8-bit, convert to [0,1]
    if img.max() > 1.5:
        img /= 255.0

    # Normalize globally to [0,1]
    img = (img - img.min()) / (img.max() - img.min() + 1e-8)

    # Crop title region (approximately 30 pixels from top)
    if crop_title:
        img = img[35:, :]  # Remove top 30 pixels where title is located

    return img

def calculate_sharpness(image):
    """Measure edge sharpness using gradient."""
    gx = ndimage.sobel(image, axis=0)
    gy = ndimage.sobel(image, axis=1)
    return np.mean(np.sqrt(gx ** 2 + gy ** 2))

def calculate_noise(image):
    """Estimate noise from corner region."""
    corner = image[0:50, 0:50]
    return np.std(corner)

def calculate_mae(img1, img2):
    """Mean Absolute Error."""
    return np.mean(np.abs(img1 - img2))

def analyze_dataset(prefix):
    """Load images and calculate metrics."""

    print(f"\n{'=' * 60}")
    print(f"Analyzing: {prefix}")
    print(f"{'=' * 60}\n")

    # Load all four versions (crop titles for clean analysis)
    full_img = load_image_for_analysis(f"{OUT_DIR}/{prefix}_recon_full.png", crop_title=True)
    partial_img = load_image_for_analysis(f"{OUT_DIR}/{prefix}_recon_partial.png", crop_title=True)
    lowpass_img = load_image_for_analysis(f"{OUT_DIR}/{prefix}_recon_lowpass.png", crop_title=True)
    highpass_img = load_image_for_analysis(f"{OUT_DIR}/{prefix}_recon_highpass.png", crop_title=True)

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
    axes[1, 0].text(0.5, 0.5, 'Reference', ha='center', va='center',
                    fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')

    diff1 = np.abs(full_img - partial_img)
    im1 = axes[1, 1].imshow(diff1, cmap='hot')
    axes[1, 1].set_title(f'Difference\nMAE: {np.mean(diff1):.4f}', fontsize=10, pad=10)
    axes[1, 1].axis('off')
    plt.colorbar(im1, ax=axes[1, 1], fraction=0.046, pad=0.04)

    diff2 = np.abs(full_img - lowpass_img)
    im2 = axes[1, 2].imshow(diff2, cmap='hot')
    axes[1, 2].set_title(f'Difference\nMAE: {np.mean(diff2):.4f}', fontsize=10, pad=10)
    axes[1, 2].axis('off')
    plt.colorbar(im2, ax=axes[1, 2], fraction=0.046, pad=0.04)

    diff3 = np.abs(full_img - highpass_img)
    im3 = axes[1, 3].imshow(diff3, cmap='hot')
    axes[1, 3].set_title(f'Difference\nMAE: {np.mean(diff3):.4f}', fontsize=10, pad=10)
    axes[1, 3].axis('off')
    plt.colorbar(im3, ax=axes[1, 3], fraction=0.046, pad=0.04)

    plt.suptitle(f'Comparison: {prefix}', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for suptitle
    plt.savefig(f"{RESULTS_DIR}/{prefix}_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {prefix}_comparison.png\n")

if __name__ == "__main__":
    print("\nK-SPACE IMAGE QUALITY ANALYSIS")
    print("=" * 60)

    # Analyze datasets
    analyze_dataset("shepp_logan")
    analyze_dataset("mri_image_slice000")

    print(f"Results saved in: ./{RESULTS_DIR}/\n")