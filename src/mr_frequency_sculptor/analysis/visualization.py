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


def _save_report(prefix: str, metrics_data: list, report_path: Path,
                 full_img: np.ndarray, partial_img: np.ndarray,
                 lowpass_img: np.ndarray, highpass_img: np.ndarray):
    """
    Save analysis report to a text file.
    
    Args:
        prefix: Dataset prefix.
        metrics_data: List of dictionaries with metric data.
        report_path: Path to save the report.
        full_img: Full k-space reconstruction image.
        partial_img: Partial k-space reconstruction image.
        lowpass_img: Low-pass filtered reconstruction image.
        highpass_img: High-pass filtered reconstruction image.
    """
    from datetime import datetime
    
    # Calculate additional metrics
    diff_partial = np.abs(full_img - partial_img)
    diff_lowpass = np.abs(full_img - lowpass_img)
    diff_highpass = np.abs(full_img - highpass_img)
    
    mae_partial = np.mean(diff_partial)
    mae_lowpass = np.mean(diff_lowpass)
    mae_highpass = np.mean(diff_highpass)
    
    max_diff_partial = np.max(diff_partial)
    max_diff_lowpass = np.max(diff_lowpass)
    max_diff_highpass = np.max(diff_highpass)
    
    # Generate report
    report_lines = [
        "=" * 70,
        f"K-SPACE RECONSTRUCTION ANALYSIS REPORT",
        f"Dataset: {prefix}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        "IMAGE QUALITY METRICS",
        "-" * 70,
        f"{'Version':<20} {'Sharpness':<15} {'Noise':<15} {'MAE':<15}",
        "-" * 70,
    ]
    
    for metric in metrics_data:
        report_lines.append(
            f"{metric['name']:<20} {metric['sharpness']:<15.6f} "
            f"{metric['noise']:<15.6f} {metric['error']:<15.6f}"
        )
    
    report_lines.extend([
        "",
        "DIFFERENCE ANALYSIS",
        "-" * 70,
        f"{'Comparison':<20} {'Mean Absolute Error':<25} {'Max Difference':<20}",
        "-" * 70,
        f"{'Partial vs Full':<20} {mae_partial:<25.6f} {max_diff_partial:<20.6f}",
        f"{'Low-pass vs Full':<20} {mae_lowpass:<25.6f} {max_diff_lowpass:<20.6f}",
        f"{'High-pass vs Full':<20} {mae_highpass:<25.6f} {max_diff_highpass:<20.6f}",
        "",
        "IMAGE STATISTICS",
        "-" * 70,
        f"{'Version':<20} {'Min':<15} {'Max':<15} {'Mean':<15} {'Std':<15}",
        "-" * 70,
        f"{'Full k-space':<20} {full_img.min():<15.6f} {full_img.max():<15.6f} "
        f"{full_img.mean():<15.6f} {full_img.std():<15.6f}",
        f"{'Partial (50%)':<20} {partial_img.min():<15.6f} {partial_img.max():<15.6f} "
        f"{partial_img.mean():<15.6f} {partial_img.std():<15.6f}",
        f"{'Low-pass':<20} {lowpass_img.min():<15.6f} {lowpass_img.max():<15.6f} "
        f"{lowpass_img.mean():<15.6f} {lowpass_img.std():<15.6f}",
        f"{'High-pass':<20} {highpass_img.min():<15.6f} {highpass_img.max():<15.6f} "
        f"{highpass_img.mean():<15.6f} {highpass_img.std():<15.6f}",
        "",
        "METRIC DESCRIPTIONS",
        "-" * 70,
        "Sharpness: Mean gradient magnitude using Sobel operator (higher = sharper)",
        "Noise: Standard deviation in corner region (higher = more noise)",
        "MAE: Mean Absolute Error compared to full k-space reconstruction",
        "",
        "=" * 70,
    ])
    
    # Write report to file
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))


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
        full_path = RESULTS_RAW_DIR / f"{prefix}_recon_full.png"
        if not full_path.exists():
            print(f"Error: Required files not found for '{prefix}'.")
            print(f"Expected file: {full_path}")
            print(f"Please run 'python scripts/process_kspace.py' first to generate the data.\n")
            return
        
        full_img = load_image(full_path)
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

    # Collect metrics data
    metrics_data = []
    for name, img in images.items():
        sharpness = calculate_sharpness(img)
        noise = calculate_noise(img)
        error = calculate_mae(full_img, img) if name != 'Full k-space' else 0.0
        metrics_data.append({
            'name': name,
            'sharpness': sharpness,
            'noise': noise,
            'error': error
        })

    # Print to console
    print(f"{'Version':<20} {'Sharpness':<12} {'Noise':<12} {'Error':<12}")
    print("-" * 56)

    for metric in metrics_data:
        print(f"{metric['name']:<20} {metric['sharpness']:<12.4f} {metric['noise']:<12.4f} {metric['error']:<12.4f}")

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

    # Save text report
    report_path = RESULTS_ANALYSIS_DIR / f"{prefix}_report.txt"
    _save_report(prefix, metrics_data, report_path, full_img, partial_img, lowpass_img, highpass_img)

    print(f"Saved: {prefix}_comparison.png")
    print(f"Saved: {prefix}_report.txt\n")

