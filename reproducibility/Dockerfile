FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file and install Python dependencies
COPY environment.yml .
RUN pip install --no-cache-dir conda && \
    conda env create -f environment.yml && \
    echo "conda activate superconductor" >> ~/.bashrc

# Copy the rest of the code
COPY . .

# Default command
CMD ["python", "run_pipeline.py", "--help"]
