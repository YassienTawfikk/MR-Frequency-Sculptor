# Migration Guide

This project has been restructured for better organization and maintainability.

## New Structure

The project now uses a proper package structure:

- **Source code**: `src/mr_frequency_sculptor/`
- **Scripts**: `scripts/`
- **Data**: `data/`
- **Results**: `results/raw/` and `results/analysis/`

## Old vs New

### Old Files (Deprecated)

- `main.py` → Replaced by `scripts/process_kspace.py`
- `kspace_analysis.py` → Replaced by `scripts/analyze_results.py`

### New Usage

**Old way:**

```bash
python main.py
python kspace_analysis.py
```

**New way:**

```bash
python scripts/process_kspace.py
python scripts/analyze_results.py
```

## Output Directories

- Old: `kspace_results/` and `kspace_analysis/`
- New: `results/raw/` and `results/analysis/`

The old directories are still in `.gitignore` for backward compatibility, but new runs will use the new structure.

## Configuration

All configuration is now centralized in `src/mr_frequency_sculptor/config.py`. You can modify:

- Data file paths
- Processing parameters
- Output directories
- Visualization settings

## Package Installation (Optional)

You can now install the package in development mode:

```
pip install -e .
```

This allows importing from anywhere:

```
from mr_frequency_sculptor import

...
```

