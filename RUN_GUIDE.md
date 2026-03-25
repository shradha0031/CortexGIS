# 🚀 Complete CortexGIS Setup & Run Guide

**Step-by-step instructions to get CortexGIS running on your Windows system.**

---

## 📋 **Prerequisites Check**

### 1. **Python 3.9+**
```powershell
python --version
```
- If not installed: Download from [python.org](https://www.python.org/downloads/)
- Make sure `python` and `pip` are in your PATH

### 2. **Git**
```powershell
git --version
```
- If not installed: Download from [git-scm.com](https://git-scm.com/)

### 3. **Optional: Docker** (for containerized deployment)
- Download from [docker.com](https://www.docker.com/products/docker-desktop)
- Install and restart your computer

---

## 📥 **Step 1: Get the Project**

### Option A: Clone from GitHub (Recommended)
```powershell
cd C:\projects
git clone https://github.com/shradha0031/CortexGIS.git
cd CortexGIS
```

### Option B: If you already have it locally
```powershell
cd C:\projects\cortexgis
```

---

## 🐍 **Step 2: Set Up Python Environment**

### Create Virtual Environment
```powershell
# Navigate to project folder
cd C:\projects\cortexgis

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**You should see `(venv)` in your PowerShell prompt.**

---

## 📦 **Step 3: Install Dependencies**

### Install Core Dependencies
```powershell
# Make sure venv is activated (you should see (venv))
venv\Scripts\activate

# Install minimal requirements
pip install streamlit
```

### Optional: Install Full Geospatial Stack
```powershell
# For actual geospatial processing
pip install geopandas rasterio whitebox faiss-cpu sentence-transformers
```

---

## ✅ **Step 4: Verify Installation**

### Check Core Modules
```powershell
python -c "import streamlit; print('✓ Streamlit OK')"
python -c "from planner.geospatial_planner import GeospatialPlanner; print('✓ Planner OK')"
python -c "from executor.executor import WorkflowExecutor; print('✓ Executor OK')"
```

### Validate Workflows
```powershell
python scripts/validate_workflows.py
```
**Expected output:**
```
✓ flood_mapping.json (10 steps, confidence: 0.85)
✓ site_suitability.json (14 steps, confidence: 0.8)
Summary: 2/2 workflows valid
```

---

## 🚀 **Step 5: Run the Application**

### Method 1: Streamlit UI (Recommended)
```powershell
# Make sure you're in project root
cd C:\projects\cortexgis

# Activate venv
venv\Scripts\activate

# Run the app
streamlit run ui/app.py
```

**Expected output:**
```
Streamlit app is running!

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Method 2: Docker (If Docker is installed)
```powershell
# Build and run
docker-compose up -d

# Check status
docker ps
```

---

## 🌐 **Step 6: Access the Application**

1. **Open your web browser**
2. **Navigate to:** `http://localhost:8501`
3. **You should see the CortexGIS interface with 4 tabs:**
   - **Query Input** — Enter natural language queries
   - **Workflow Review** — See generated workflows
   - **Execute** — Run the workflow
   - **Results** — View outputs and metrics

---

## 🧪 **Step 7: Test the Application**

### Try a Sample Query
1. In the **Query Input** tab, enter:
   ```
   Map flood extent from Sentinel-1 data in Bangladesh for August 2024
   ```

2. Click **Generate Workflow**
3. Review the generated workflow in the **Workflow Review** tab
4. Click **Execute** to run it
5. View results in the **Results** tab

### Run Demo Scripts
```powershell
# Test planner
python scripts/demo_planner.py

# Test integrated workflow
python scripts/demo_integrated.py

# Test benchmarking
python scripts/demo_benchmarking.py
```

---

## 🔧 **Step 8: Optional Enhancements**

### Add Real LLM Integration
```powershell
# Install OpenAI SDK
pip install openai

# Set API key
$env:OPENAI_API_KEY = "sk-your-key-here"

# Edit planner/geospatial_planner.py to use real LLM
```

### Enable RAG (Vector Search)
```powershell
# Install ML dependencies
pip install sentence-transformers faiss-cpu

# Build RAG index
python scripts/init_rag_index.py
```

### Connect to Cloud Data
```powershell
# Set environment variables for data sources
$env:COPERNICUS_USER = "your_username"
$env:COPERNICUS_PASS = "your_password"
$env:BHOONIDHI_API_KEY = "your_api_key"
```

---

## 🐛 **Troubleshooting**

### Issue: "streamlit not recognized"
```powershell
# Activate venv first
venv\Scripts\activate

# Install streamlit
pip install streamlit

# Try again
streamlit run ui/app.py
```

### Issue: "docker-compose not recognized"
- Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- Restart your computer
- Try: `docker compose up -d` (with space)

### Issue: "ModuleNotFoundError"
```powershell
# Install missing modules
pip install -r requirements.txt

# Or install specific module
pip install geopandas rasterio
```

### Issue: Wrong Directory
```powershell
# Always run from project root
cd C:\projects\cortexgis
ls docker-compose.yml  # Should show the file
```

### Issue: Port 8501 Already in Use
```powershell
# Use different port
streamlit run ui/app.py --server.port=8502
```

---

## 📚 **Documentation**

Once running, read these files for more info:
- **[README.md](README.md)** — Project overview and features
- **[SETUP.md](SETUP.md)** — Detailed installation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Cloud deployment options
- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute quick start

---

## 🎯 **Success Checklist**

- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] Project cloned to `C:\projects\cortexgis`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install streamlit`)
- [ ] Core modules import successfully
- [ ] Workflows validate (`python scripts/validate_workflows.py`)
- [ ] Streamlit app runs (`streamlit run ui/app.py`)
- [ ] Browser opens to `http://localhost:8501`
- [ ] Can enter queries and generate workflows

---

## 🚀 **Next Steps**

1. **Explore the UI** — Try different queries
2. **Read documentation** — Understand the architecture
3. **Add custom tools** — Extend the system
4. **Deploy to cloud** — See [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Contribute** — See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**🎉 Congratulations! CortexGIS is now running on your system.**

*Questions? Check the troubleshooting section above or open an issue on GitHub.*
