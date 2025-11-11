"""Setup configuration for MR Frequency Sculptor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=2.1.2",
        "matplotlib>=3.9.2",
        "scipy>=1.14.1",
        "h5py>=3.12.1",
        "scikit-image>=0.24.0",
    ]

setup(
    name="mr-frequency-sculptor",
    version="0.1.0",
    description="A tool for exploring k-space manipulations in MRI reconstruction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/MR-Frequency-Sculptor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "process-kspace=mr_frequency_sculptor.scripts.process_kspace:main",
            "analyze-results=mr_frequency_sculptor.scripts.analyze_results:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
