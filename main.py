import os
import numpy as np
import matplotlib.pyplot as plt
import h5py
from skimage.data import shepp_logan_phantom
from scipy.fft import fft2, fftshift, ifftshift
from scipy.fft import ifft2
from scipy.ndimage import gaussian_filter

H5_FILE       = "mri.h5" # from "https://github.com/mylyu/M4Raw"
MRI_SLICE_IDX = 0               # 0 to 17
OUT_DIR       = "kspace_results"
os.makedirs(OUT_DIR, exist_ok=True)

def reconstruct_image_from_kspace(kspace: np.ndarray) -> np.ndarray:
    return np.abs(ifft2(fftshift(kspace)))

def normalize_image(img: np.ndarray) -> np.ndarray:
    img_min, img_max = img.min(), img.max()
    return (img - img_min) / (img_max - img_min + 1e-8)

def save_reconstructed_image(name: str, image: np.ndarray):
    plt.figure(figsize=(5,5))
    plt.imshow(image, cmap='gray')
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

def apply_lowpass_filter(kspace: np.ndarray, sigma: float = 0.5) -> np.ndarray:
    return gaussian_filter(kspace, sigma=sigma)

def apply_highpass_filter(kspace: np.ndarray, sigma: float = 0.5) -> np.ndarray:
    return kspace - gaussian_filter(kspace, sigma=sigma)

def reconstruct_all_versions(kspace: np.ndarray, prefix: str):
    full_img = normalize_image(reconstruct_image_from_kspace(kspace))
    save_reconstructed_image(f"{prefix}_recon_full", full_img)

    partial_kspace = simulate_partial_kspace(kspace, fraction=0.5)
    partial_img = normalize_image(reconstruct_image_from_kspace(partial_kspace))
    save_reconstructed_image(f"{prefix}_recon_partial", partial_img)

    lowpass_kspace = apply_lowpass_filter(kspace)
    lowpass_img = normalize_image(reconstruct_image_from_kspace(lowpass_kspace))
    save_reconstructed_image(f"{prefix}_recon_lowpass", lowpass_img)

    highpass_kspace = apply_highpass_filter(kspace)
    highpass_img = normalize_image(reconstruct_image_from_kspace(highpass_kspace))
    save_reconstructed_image(f"{prefix}_recon_highpass", highpass_img)

    print(f"\n{prefix}_recon_full serves as the gold standard for comparison.")
    print("It uses the complete k-space data, representing the highest fidelity reconstruction.\n")


def save_kspace(name: str, kspace: np.ndarray, original_image=None):
    """Save k-space as 3 PNGs + .npz file."""
    mag = np.abs(kspace)
    mag_log = np.log(mag + 1) # avoid log(0) because k-space has zeros

    phase = np.angle(kspace)
    real_part = np.real(kspace)

    # Magnitude
    plt.figure(figsize=(5,5))
    plt.imshow(mag_log, cmap='gray')
    plt.title(f"{name} – log|magnitude|")
    plt.axis('off')
    plt.savefig(os.path.join(OUT_DIR, f"{name}_mag.png"), dpi=150, bbox_inches='tight')
    plt.close()

    # Phase 
    plt.figure(figsize=(5,5))
    im = plt.imshow(phase, cmap='gray')
    plt.title(f"{name} – phase")
    plt.axis('off')
    plt.colorbar(im, fraction=0.046)
    plt.savefig(os.path.join(OUT_DIR, f"{name}_phase.png"), dpi=150, bbox_inches='tight')
    plt.close()

    # Real part
    plt.figure(figsize=(5,5))
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

    plt.figure(figsize=(5,5))
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

    # Normalize to [0,1] if needed for consistency with previous shepp logan results 
    img = img_data.astype(np.complex64)
    img_max = img.max()
    if img_max > 0:
        img /= img_max
    else:
        print("Warning: Image is all zero!")

    plt.figure(figsize=(5,5))
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
    print("   *.npz          → full data to be processed further")
