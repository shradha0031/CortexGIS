# CortexGIS Docker Image
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels for all dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Optional: Add geospatial wheels (GeoPandas, Rasterio, etc.)
# Uncomment if you want full geospatial support
# RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels \
#     geopandas rasterio whitebox faiss-cpu sentence-transformers

---

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /cortexgis

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev libgeos-c1v5 libproj25 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Copy requirements from builder
COPY --from=builder /build/requirements.txt .

# Install wheels
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --no-index \
    --find-links=/wheels \
    -r requirements.txt && \
    rm -rf /wheels

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 cortexgis && \
    chown -R cortexgis:cortexgis /cortexgis
USER cortexgis

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

# Create output directory
RUN mkdir -p outputs benchmark_results

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import streamlit" || exit 1

# Expose Streamlit port
EXPOSE 8501

# Default command: Run Streamlit app
CMD ["streamlit", "run", "ui/app.py"]

# To run:
# docker build -t cortexgis:latest .
# docker run -p 8501:8501 \
#   -v $(pwd)/outputs:/cortexgis/outputs \
#   -v $(pwd)/benchmark_results:/cortexgis/benchmark_results \
#   cortexgis:latest
