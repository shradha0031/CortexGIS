# 🚀 Quick Start Guide

Get CortexGIS running in 5 minutes.

---

## 1️⃣ Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/))
- **VS Code** (optional, for editing)

---

## 2️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cortexgis.git
cd cortexgis

# Create virtual environment (REQUIRED)
python -m venv venv
source venv/bin/activate          # macOS/Linux
# OR
venv\Scripts\activate             # Windows

# Install minimal dependencies
pip install streamlit
```

**Done!** You can now run the Streamlit UI.

---

## 3️⃣ Run the Application

```bash
streamlit run ui/app.py
```

Opens automatically at `http://localhost:8501`

---

## 4️⃣ Use the Web Interface

1. **Query Tab** — Type your geospatial question
   - Example: *"Map flood extent from Sentinel-1 data in Bangladesh"*

2. **Workflow Tab** — Review generated workflow
   - Shows Chain-of-Thought reasoning
   - Lists all steps and data requirements

3. **Execute Tab** — Run the workflow
   - Monitor progress
   - View step outputs

4. **Results Tab** — See results
   - Download maps (GeoTIFF)
   - View metrics and performance stats

---

## 5️⃣ (Optional) Install Full Stack

For actual geospatial processing:

```bash
pip install -r requirements_full.txt
```

Includes: GeoPandas, Rasterio, WhiteboxTools, FAISS, sentence-transformers

**Note:** First run takes ~1 min (downloads ML models).

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview & features |
| [SETUP.md](SETUP.md) | Detailed installation guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & components |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Cloud deployment (AWS/GCP/Azure) |
| [API_GUIDE.md](API_GUIDE.md) | Python API reference |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## 🧪 Validate Installation

```bash
# Quick test
python -c "import streamlit; print('✓ OK')"

# Run validation script
python scripts/validate_workflows.py

# Run example
python scripts/demo_integrated.py
```

---

## 🐳 Using Docker (Optional)

```bash
# Build image
docker build -t cortexgis:latest .

# Run container
docker run -p 8501:8501 cortexgis:latest

# Using docker-compose (includes PostGIS)
docker-compose up -d
```

Access at `http://localhost:8501`

---

## 🔑 Integrate Real LLM (Optional)

To use actual LLM reasoning instead of stubs:

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# OR for Google VertexAI
gcloud auth application-default login
```

Then edit `planner/geospatial_planner.py` to use your LLM client.

---

## 📁 Project Structure

```
cortexgis/
├── ui/app.py              ← Run this to start UI
├── planner/               ← Workflow planning (CoT)
├── executor/              ← Tool execution & registry
├── rag/                   ← Vector search (FAISS)
├── data/                  ← Data ingestion
├── workflows/             ← Example workflows (JSON)
├── scripts/               ← Demo & validation scripts
├── evaluation/            ← Benchmarking & metrics
└── docs/                  ← Documentation
```

---

## ⚡ Common Tasks

### Run Demo Workflows

```bash
python scripts/demo_planner.py          # Generate workflows
python scripts/demo_integrated.py       # Plan + Execute
python scripts/demo_benchmarking.py     # Run benchmarks
```

### Validate Workflows

```bash
python scripts/validate_workflows.py
```

### Add Custom Workflow

1. Create `workflows/my_workflow.json`
2. Follow schema in `workflows/flood_mapping.json`
3. Run: `python scripts/validate_workflows.py`

### Add Custom Tool

1. Extend `GeoTool` in `executor/tool_adapters.py`
2. Register in `ToolRegistry`
3. Add to `gis_functions_schema.json`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: streamlit` | `pip install streamlit` |
| `Port 8501 already in use` | Change port: `streamlit run ui/app.py --server.port=8502` |
| Geospatial tools fail | Install full stack: `pip install -r requirements_full.txt` |
| Slow startup | First run is slow (ML model download); subsequent runs are fast |
| `GDAL not found` (Windows) | Use pre-built wheels: See [SETUP.md](SETUP.md) |

---

## 📞 Need Help?

- **Documentation:** See [README.md](README.md)
- **API Reference:** See [API_GUIDE.md](API_GUIDE.md)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/cortexgis/issues)
- **Discussion:** [GitHub Discussions](https://github.com/yourusername/cortexgis/discussions)

---

## 🎯 Next Steps

1. ✅ Run the UI (`streamlit run ui/app.py`)
2. 📖 Read [README.md](README.md) for features
3. 🏗️ Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand design
4. 🔗 Integrate LLM (optional)
5. ☁️ Deploy to cloud (see [DEPLOYMENT.md](DEPLOYMENT.md))
6. 🛠️ Extend with custom tools (see [CONTRIBUTING.md](CONTRIBUTING.md))

---

**Welcome to CortexGIS! 🌍**

*Autonomous geospatial workflow orchestration powered by Chain-of-Thought reasoning.*
