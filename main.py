import os
import numpy as np
import matplotlib.pyplot as plt
import h5py
from skimage.data import shepp_logan_phantom
from scipy.fft import fft2, fftshift, ifftshift, ifft2
from scipy.ndimage import gaussian_filter

H5_FILE = "mri.h5"  # from "https://github.com/mylyu/M4Raw"
MRI_SLICE_IDX = 0  # 0 to 17
OUT_DIR = "kspace_results"
os.makedirs(OUT_DIR, exist_ok=True)


def reconstruct_image_from_kspace(kspace: np.ndarray) -> np.ndarray:
    # kspace is expected to be FFTSHIFTed (zero-frequency at center).
    # To invert: first ifftshift, then ifft2.
    return np.abs(ifft2(ifftshift(kspace)))


def normalize_by_reference(img: np.ndarray, ref_max: float) -> np.ndarray:
    if ref_max == 0:
        return img.copy()
    return img / ref_max


def save_reconstructed_image(name: str, image: np.ndarray):
    plt.figure(figsize=(5, 5))
    plt.imshow(image, cmap='gray', vmin=0, vmax=1)
    plt.title(f"{name}")
    plt.axis('off')
    plt.colorbar(fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, f"{name}.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {name}.png")


def simulate_partial_kspace(kspace: np.ndarray, fraction: float = 0.5) -> np.ndarray:
    rows, cols = kspace.shape
    center_r, center_c = rows // 2, cols // 2
    half_r, half_c = int(rows * fraction / 2), int(cols * fraction / 2)
    mask = np.zeros_like(kspace, dtype=bool)
    mask[center_r - half_r:center_r + half_r, center_c - half_c:center_c + half_c] = True
    return kspace * mask


def gaussian_kspace_mask(shape, sigma_fraction=0.1):
    # sigma_fraction is relative to image size; create centered Gaussian mask
    rows, cols = shape
    u = np.arange(-rows // 2, rows // 2)
    v = np.arange(-cols // 2, cols // 2)
    V, U = np.meshgrid(v, u)  # note: meshgrid(v,u) matches array ordering
    d2 = U ** 2 + V ** 2
    # scale sigma with the smaller dimension
    sigma = sigma_fraction * max(rows, cols)
    mask = np.exp(-d2 / (2.0 * (sigma ** 2)))
    return mask


def apply_lowpass_filter(kspace: np.ndarray, sigma_fraction: float = 0.05) -> np.ndarray:
    mask = gaussian_kspace_mask(kspace.shape, sigma_fraction=sigma_fraction)
    # mask is real; preserve complex kspace by multiplying
    return kspace * mask


def apply_highpass_filter(kspace: np.ndarray, sigma_fraction: float = 0.05) -> np.ndarray:
    mask = gaussian_kspace_mask(kspace.shape, sigma_fraction=sigma_fraction)
    return kspace * (1.0 - mask)


def reconstruct_all_versions(kspace: np.ndarray, prefix: str):
    # Raw full reconstruction (not shifted/normalized)
    full_raw = reconstruct_image_from_kspace(kspace)  # absolute magnitude
    full_max = full_raw.max() if full_raw.size > 0 else 1.0

    # Normalize everyone by the same reference maximum (full image)
    full_img = normalize_by_reference(full_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_full", full_img)

    partial_kspace = simulate_partial_kspace(kspace, fraction=0.5)
    partial_raw = reconstruct_image_from_kspace(partial_kspace)
    partial_img = normalize_by_reference(partial_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_partial", partial_img)

    lowpass_kspace = apply_lowpass_filter(kspace, sigma_fraction=0.05)
    lowpass_raw = reconstruct_image_from_kspace(lowpass_kspace)
    lowpass_img = normalize_by_reference(lowpass_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_lowpass", lowpass_img)

    highpass_kspace = apply_highpass_filter(kspace, sigma_fraction=0.05)
    highpass_raw = reconstruct_image_from_kspace(highpass_kspace)
    highpass_img = normalize_by_reference(highpass_raw, full_max)
    save_reconstructed_image(f"{prefix}_recon_highpass", highpass_img)

    # Save raw arrays into an npz for precise analysis later
    np.savez(os.path.join(OUT_DIR, f"{prefix}_recons.npz"),
             full_raw=full_raw,
             partial_raw=partial_raw,
             lowpass_raw=lowpass_raw,
             highpass_raw=highpass_raw)

    print(f"Saved raw reconstructions to: {prefix}_recons.npz")
    print(f"\n{prefix}_recon_full serves as the gold standard for comparison.")
    print("It uses the complete k-space data, representing the highest fidelity reconstruction.\n")


def save_kspace(name: str, kspace: np.ndarray, original_image=None):
    """Save k-space as 3 PNGs + .npz file."""
    mag = np.abs(kspace)
    mag_log = np.log(mag + 1)  # avoid log(0)

    phase = np.angle(kspace)
    real_part = np.real(kspace)

    # Magnitude
    plt.figure(figsize=(5, 5))
    plt.imshow(mag_log, cmap='gray')
    plt.title(f"{name} – log|magnitude|")
    plt.axis('off')
    plt.savefig(os.path.join(OUT_DIR, f"{name}_mag.png"), dpi=150, bbox_inches='tight')
    plt.close()

    # Phase
    plt.figure(figsize=(5, 5))
    im = plt.imshow(phase, cmap='gray')
    plt.title(f"{name} – phase")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, f"{name}_phase.png"), dpi=150, bbox_inches='tight')
    plt.close()

    # Real part
    plt.figure(figsize=(5, 5))
    im = plt.imshow(real_part, cmap='gray')
    plt.title(f"{name} – real(k-space)")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, f"{name}_kspace.png"), dpi=150, bbox_inches='tight')
    plt.close()

    save_dict = {'kspace': kspace, 'magnitude': mag, 'phase': phase, 'real': real_part}
    if original_image is not None:
        save_dict['image'] = original_image
    np.savez(os.path.join(OUT_DIR, f"{name}_kspace.npz"), **save_dict)

    print(f"Saved: {name} → _mag.png, _phase.png, _kspace.png, _kspace.npz")


# 1) using Shepp-Logan phantom:
def process_phantom():
    img = shepp_logan_phantom().astype(np.complex64)

    plt.figure(figsize=(5, 5))
    im = plt.imshow(np.abs(img), cmap='gray')
    plt.title(f"original Phantom")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, "original_phantom.png"), dpi=150, bbox_inches='tight')
    plt.close()

    kspace = fftshift(fft2(img))
    save_kspace("shepp_logan", kspace, original_image=img.real)
    reconstruct_all_versions(kspace, "shepp_logan")


# 2) using  Real MRI slice :
def process_mri_image():
    if not os.path.exists(H5_FILE):
        print(f"Warning: {H5_FILE} not found.")
        return

    with h5py.File(H5_FILE, "r") as f:
        if 'reconstruction_rss' not in f:
            print("Error: 'reconstruction_rss' not found in file.")
            return
        img_data = f['reconstruction_rss'][MRI_SLICE_IDX]  # (256, 256) float32

    img = img_data.astype(np.complex64)
    img_max = img.max()
    if img_max > 0:
        img /= img_max
    else:
        print("Warning: Image is all zero!")

    plt.figure(figsize=(5, 5))
    im = plt.imshow(np.abs(img), cmap='gray')
    plt.title(f"original MRI slice")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, "original_mri_slice.png"), dpi=150, bbox_inches='tight')
    plt.close()

    kspace = fftshift(fft2(img))

    name = f"mri_image_slice{MRI_SLICE_IDX:03d}"
    save_kspace(name, kspace, original_image=img.real)
    reconstruct_all_versions(kspace, name)


if __name__ == "__main__":
    print("Task 4 – Generate k-space from MRI SLICE using 2D FFT\n")
    process_phantom()
    process_mri_image()
    print(f"\nAll results in: ./{OUT_DIR}/")
    print("   *_mag.png      → log-magnitude of k-space")
    print("   *_phase.png    → phase")
    print("   *_kspace.png   → real part")
    print("   *_recons.npz   → raw reconstructions (full, partial, lowpass, highpass)")