"""
Analysis script for k-space reconstruction results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.mr_frequency_sculptor.analysis import analyze_dataset
from src.mr_frequency_sculptor.config import RESULTS_ANALYSIS_DIR, MRI_SLICE_IDX

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("K-SPACE IMAGE QUALITY ANALYSIS")
    print("=" * 60)

    # Analyze datasets
    analyze_dataset("shepp_logan")
    analyze_dataset(f"mri_image_slice{MRI_SLICE_IDX:03d}")

    print(f"Results saved in: {RESULTS_ANALYSIS_DIR}\n")
