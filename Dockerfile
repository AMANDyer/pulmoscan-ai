# ─────────────────────────────────────────────
# Stage 1 – base image with Python 3.10
# ─────────────────────────────────────────────
FROM python:3.10-slim

# System dependencies for Pillow / TF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (Docker cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY streamlit_app.py .

# Copy your trained model (place my_model.keras in the same folder before building)
COPY my_model.keras .

# Expose both service ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit via a small shell script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
