# CortexGIS Setup Guide

Complete installation and environment setup instructions for **Windows**, **macOS**, and **Linux**.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start (All Platforms)](#quick-start-all-platforms)
3. [Windows Setup](#windows-setup)
4. [macOS Setup](#macos-setup)
5. [Linux Setup](#linux-setup)
6. [Verify Installation](#verify-installation)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum (Stub/Demo Mode)

- **Python:** 3.9 or later (3.12+ recommended)
- **RAM:** 4 GB
- **Disk Space:** 500 MB
- **Dependencies:** Streamlit only

### Recommended (Full Geospatial Processing)

- **Python:** 3.11 or later
- **RAM:** 8 GB or more (16 GB for large rasters)
- **Disk Space:** 2 GB (includes GDAL, geospatial libraries)
- **Dependencies:** All packages in `requirements_full.txt`

---

## Quick Start (All Platforms)

### 1. Clone/Download CortexGIS

```bash
cd /path/to/projects
git clone https://github.com/yourusername/cortexgis.git
cd cortexgis
```

Or if you have it locally:

```bash
cd c:\projects\cortexgis  # Windows
cd ~/projects/cortexgis   # macOS/Linux
```

### 2. Create Python Virtual Environment

**Option A: Using `venv` (Built-in)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Option B: Using `conda` (Recommended for Geospatial)**

```bash
# Install conda first from: https://docs.conda.io/en/latest/miniconda.html
conda create -n cortexgis python=3.11
conda activate cortexgis
```

### 3. Install Minimal Dependencies

```bash
pip install streamlit
```

This is enough to run the Streamlit UI in stub/demo mode.

### 4. Run the UI

```bash
streamlit run ui/app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install the Taichi backend...
```

Open http://localhost:8501 in your browser.

---

## Windows Setup

### Prerequisites

Ensure Python 3.9+ is installed:

```powershell
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/).

### Step 1: Activate Virtual Environment

```powershell
# PowerShell or CMD
cd c:\projects\cortexgis
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 3: Install Minimal Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Install Full Dependencies (Optional, for Real Geospatial Processing)

⚠️ **Note:** Some packages require pre-built wheels or GDAL dev libraries. Follow these steps:

**Option A: Using Pre-built Wheels (Easiest)**

```powershell
# Install dependencies that have wheels available on PyPI
pip install -r requirements_full.txt
```

If any package fails (e.g., Rasterio), try pre-built wheels from:
- [Unofficial Windows Binaries by Christoph Gohlke](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

```powershell
# Example: Install rasterio wheel manually
pip install C:\Downloads\rasterio-1.3.0-cp311-cp311-win_amd64.whl
```

**Option B: Using OSGeo4W (Alternative, More Involved)**

1. Download [OSGeo4W installer](https://trac.osgeo.org/osgeo4w/)
2. Select `GDAL`, `GEOS`, `PROJ` during installation
3. Use OSGeo4W Python directly or configure environment variables

### Step 5: Verify Installation

```powershell
python -m py_compile planner/geospatial_planner.py
python -m py_compile executor/executor.py
python -m py_compile ui/app.py
```

All should print nothing (no errors).

### Step 6: Run Tests

```powershell
python scripts/validate_workflows.py
python scripts/demo_planner.py
python scripts/demo_integrated.py
```

### Troubleshooting Windows

**Error: `ModuleNotFoundError: No module named 'geopandas'`**

- This is expected if you only installed `requirements.txt`
- Install full stack: `pip install -r requirements_full.txt`
- Or ignore and run in stub mode (all demos still work)

**Error: `gdal not found` during geopandas install**

- Use pre-built wheels (Option A above)
- Or install OSGeo4W with GDAL dev libraries (Option B)

---

## macOS Setup

### Prerequisites

Ensure Python 3.9+ and Xcode command-line tools are installed:

```bash
python3 --version
xcode-select --install  # If not already installed
```

### Step 1: Activate Virtual Environment

```bash
cd ~/projects/cortexgis
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install Homebrew Dependencies (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install geospatial dev libraries
brew install gdal geos proj
```

### Step 3: Install Python Packages

```bash
# Upgrade pip
pip install --upgrade pip

# Minimal install
pip install -r requirements.txt

# Full install (includes geospatial)
pip install -r requirements_full.txt
```

If `pip install geopandas` fails, try:

```bash
conda install -c conda-forge geopandas rasterio
```

(Requires conda; easier than managing brew + pip together)

### Step 4: Verify Installation

```bash
python -m py_compile planner/geospatial_planner.py
python -m py_compile executor/executor.py
python -m py_compile ui/app.py
```

All should print nothing (no errors).

### Step 5: Run Tests

```bash
python scripts/validate_workflows.py
python scripts/demo_planner.py
python scripts/demo_integrated.py
```

### Troubleshooting macOS

**Error: `fatal error: 'gdal.h' file not found`**

```bash
brew install gdal
export CPLUS_INCLUDE_PATH=/usr/local/include
export LD_LIBRARY_PATH=/usr/local/lib
pip install geopandas --no-cache-dir
```

**Error: Rasterio wheel not found**

```bash
conda install -c conda-forge rasterio
```

Or use conda for all geospatial packages (simplest for macOS).

---

## Linux Setup

### Prerequisites

Ensure Python 3.9+ and development tools are installed:

```bash
python3 --version
apt-get update && apt-get install -y python3-dev python3-pip build-essential
```

### Step 1: Install Geospatial Dev Libraries

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install -y \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin
```

**Fedora/RHEL:**

```bash
sudo dnf install gdal-devel geos-devel proj-devel gdal
```

**Arch Linux:**

```bash
sudo pacman -S gdal geos proj
```

### Step 2: Set Environment Variables (If Needed)

```bash
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
```

Add to `~/.bashrc` or `~/.zshrc` to persist:

```bash
echo 'export CPLUS_INCLUDE_PATH=/usr/include/gdal' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Activate Virtual Environment

```bash
cd ~/projects/cortexgis
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Packages

```bash
# Upgrade pip
pip install --upgrade pip

# Minimal install
pip install -r requirements.txt

# Full install
pip install -r requirements_full.txt
```

### Step 5: Verify Installation

```bash
python -m py_compile planner/geospatial_planner.py
python -m py_compile executor/executor.py
python -m py_compile ui/app.py
python -c "import geopandas; print('✓ GeoPandas OK')"
python -c "import rasterio; print('✓ Rasterio OK')"
```

### Step 6: Run Tests

```bash
python scripts/validate_workflows.py
python scripts/demo_planner.py
python scripts/demo_integrated.py
```

### Troubleshooting Linux

**Error: `gdal.h: No such file or directory`**

```bash
apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
pip install geopandas --no-cache-dir
```

**Error: `libgdal.so.X not found`**

```bash
sudo ldconfig
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

---

## Verify Installation

### Quick Check

Run all validation scripts:

```bash
# Validate workflow JSON schemas
python scripts/validate_workflows.py
```

Expected output:
```
Workflow Validation Report:
✓ flood_mapping.json (10 steps, confidence: 0.85)
✓ site_suitability.json (14 steps, confidence: 0.80)
Summary: 2/2 workflows valid
```

### Start the Web UI

```bash
streamlit run ui/app.py
```

Navigate to http://localhost:8501 and verify:
- ✓ Query Input tab loads
- ✓ Workflow Review tab accessible
- ✓ Tool Registry sidebar visible

### Run Demo Scripts

```bash
# End-to-end planner → executor
python scripts/demo_integrated.py

# Benchmark suite
python scripts/demo_benchmarking.py

# Data ingestion demo
python scripts/demo_data_ingestion.py
```

All should complete without fatal errors (warnings about missing geospatial libs are OK in stub mode).

---

## Environment Variables (Optional)

For cloud data access, set these in your shell or `.env` file:

```bash
# Copernicus Scihub (Sentinel-1/2)
export SCIHUB_USERNAME="your_username"
export SCIHUB_PASSWORD="your_password"

# Google Earth Engine
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google_credentials.json"

# USGS API Key (for SRTM, Landsat)
export USGS_API_KEY="your_api_key"
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Requires python-dotenv
scihub_user = os.getenv("SCIHUB_USERNAME")
```

---

## Performance Tuning

### For Large Rasters (>1 GB)

```bash
# Increase heap memory for Java-based tools (Whitebox)
export JAVACMD="java -Xmx4g"

# Optimize GDAL settings
export GDAL_CACHEMAX=512
export GDAL_NUM_THREADS=ALL_CPUS
```

### For Faster Processing

```bash
# Use GPU if available (FAISS)
pip uninstall faiss-cpu
pip install faiss-gpu

# Or use approximate search (FAISS IVF index)
# See rag/rag_index.py for index_type parameter
```

---

## Deactivate Environment

When finished, deactivate the virtual environment:

```bash
deactivate  # All platforms
```

---

## Next Steps

1. **Run the Streamlit UI:** `streamlit run ui/app.py`
2. **Explore Example Workflows:** Open `/workflows/flood_mapping.json` and `/workflows/site_suitability.json`
3. **Read Documentation:** See [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Integrate Real LLM:** Edit `planner/geospatial_planner.py` to use OpenAI/local LLMs
5. **Add Custom Tools:** Extend `GeoTool` in `executor/tool_adapters.py`

---

## Need Help?

- Check [Troubleshooting](#troubleshooting) section above
- Review script output: `python scripts/demo_integrated.py` shows detailed error messages
- Consult [README.md](README.md) for architecture overview
- Refer to module docstrings for API details

---

**Last Updated:** 2025  
**Tested On:** Python 3.9–3.12 on Win10, macOS 12+, Ubuntu 20.04+
