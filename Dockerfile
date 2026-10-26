# Production Dockerfile for Beauty Commerce Intelligence Dashboard
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure data and models exist; cold-start generation runs if needed
RUN python -c "from data_generator import generate_beauty_ecommerce_data; generate_beauty_ecommerce_data()" && \
    python -c "from ml_models import train_customer_segmentation_and_purchase_model; train_customer_segmentation_and_purchase_model()"

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to verify app is serving traffic
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
