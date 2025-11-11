# MR Frequency Sculptor

**MR Frequency Sculptor** is a Python tool for exploring k-space (frequency domain) manipulations in MRI image reconstruction.
It allows users to see how different k-space filtering strategies affect image quality, sharpness, and artifacts.

![Project Overview](https://github.com/user-attachments/assets/1379a938-ab7e-4788-99de-fb53e9e042e4)

---

## Features

### Core Functionality

* **K-space Processing**: Convert MRI images to k-space using 2D FFT.
* **Reconstruction Methods**:

    * Full k-space (reference/gold standard)
    * Partial k-space (simulates undersampling)
    * Low-pass filtering (preserves low frequencies)
    * High-pass filtering (preserves high frequencies)
* **Quantitative Analysis**: Compute metrics like sharpness, noise, and mean absolute error (MAE).
* **Support for Multiple Data Sources**: Synthetic phantoms (Shepp-Logan) and real MRI slices.
* **Automated Reports**: Generate text reports and visual comparison plots.

---

## Physics Behind the Project

MRI image formation relies on the **Fourier Relationship** between k-space and the spatial domain.

* **Slice Theorem**: Each 1D acquisition corresponds to a projection in the spatial domain.
* **2D Fourier Transform**: The complete image is reconstructed from its frequency components:

$$I(x, y) = |\mathcal{F}^{-1}(K(k_x, k_y))|$$

* **Low Frequencies**: Represent the overall contrast and main image structures.
* **High Frequencies**: Contain edges, fine details, and textures.
* **Partial K-space Sampling**: Demonstrates undersampling effects, which reduce acquisition time but introduce artifacts.

<div align="center">
  <img src="https://github.com/user-attachments/assets/37f5e3e9-bd5b-4f6f-9e2b-846ef6f725b0" width="400">
</div>

---

## Equations Used

### 1. K-space to Image Reconstruction

* Forward Transform:
  $$K(k_x, k_y) = \mathcal{F}(I(x, y))$$
* Inverse Transform:
  $$I(x, y) = |\mathcal{F}^{-1}(K(k_x, k_y))|$$

### 2. Gaussian Filtering

* Low-pass mask:
  $$Mask(u, v) = e^{-(u^2 + v^2)/(2\sigma^2)}$$
* High-pass mask:
  $$Mask_{HP} = 1 - Mask_{LP}$$

### 3. Partial K-space Mask

* Binary rectangular mask applied to central k-space lines to simulate undersampling.

---

## Scenarios

### 1. Full K-space

* **Objective**: Serve as a reference for comparison.
* **Visual**:
  <table>
  <tr>
  <td><img src="https://github.com/user-attachments/assets/1f479e1b-b546-43d9-8045-4c722b8383ff" width="250"></td>
  </tr>
  </table>

### 2. Low-Pass Filtering

* **Objective**: Remove high frequencies for a smoother image.
* **Visual**:
  <table>
  <tr>
  <td><img src="https://github.com/user-attachments/assets/3bc740dd-581a-442d-a294-92a845010f82" width="250"></td>
  </tr>
  </table>

### 3. High-Pass Filtering

* **Objective**: Remove low frequencies to highlight edges.
* **Visual**:
  <table>
  <tr>
  <td><img src="https://github.com/user-attachments/assets/fc85dd96-a4bd-4216-951f-dca9e0ae2587" width="250"></td>
  </tr>
  </table>

### 4. Partial K-space

* **Objective**: Simulate undersampling effects.
* **Visual**:
  <table>
  <tr>
  <td><img src="https://github.com/user-attachments/assets/c01bc262-6924-4eed-8c87-8564137e281d" width="250"></td>
  </tr>
  </table>

---

## How to Run the Project

1. Clone the repository:

```
git clone https://github.com/<username>/MR-Frequency-Sculptor.git
cd MR-Frequency-Sculptor
```

2. Install dependencies:

```
pip install -r requirements.txt
```

### GUI Application (Recommended)

Launch the interactive GUI application:

```
python scripts/launch_gui.py
```

**GUI Features:**

- **Image Selection**:
    - Load Shepp-Logan phantom
    - Load MRI slices from H5 files with slice selector
    - Load custom images from files (PNG, JPG, NPY, NPZ)
- **K-Space Processing**:
    - Process individual methods (Full, Partial, Low-pass, High-pass)
    - Process all methods at once
    - Adjustable parameters (partial fraction, filter sigma)
- **Real-time Visualization**:
    - View original and processed images side-by-side
    - See quality metrics (sharpness, noise, MAE) for each reconstruction
    - Difference maps comparing processed images to reference
- **Responsive Design**: Modern, user-friendly interface with progress indicators

### Command Line Scripts

3. Run the main script:

```
python scripts/process_kspace.py
```

4. Generate analysis reports:

```
python scripts/analyze_results.py
```

---

## Contributors

<div>
<table align="center">
  <tr>
        <td align="center">
      <a href="https://github.com/YassienTawfikk" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="150px;" alt="Yassien Tawfik"/>
        <br />
        <sub><b>Yassien Tawfik</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/madonna-mosaad" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/127048836?v=4" width="150px;" alt="Madonna Mosaad"/>
        <br />
        <sub><b>Madonna Mosaad</b></sub>
      </a>
    </td>
        <td align="center">
      <a href="https://github.com/nancymahmoud1" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/125357872?v=4" width="150px;" alt="Nancy Mahmoud"/>
        <br />
        <sub><b>Nancy Mahmoud</b></sub>
      </a>
    </td>
        <td align="center">
      <a href="https://github.com/RawanAhmed444" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/94761201?v=4" width="150px;" alt="Rawan Ahmed"/>
        <br />
        <sub><b>Rawan Ahmed</b></sub>
      </a>
    </td> 
        <td align="center">
      <a href="https://github.com/NadaMohamedElBasel" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/110432081?v=4" width="150px;" alt="Nada Mohamed"/>
        <br />
        <sub><b>Nada Mohamed</b></sub>
      </a>
    </td>        
  </tr>
</table>
</div>
