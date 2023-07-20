# Use the official PyTorch image as the parent image
FROM python:3.9-slim-buster

ARG PROJECT_DIR
ARG VIRTUAL_PORT
WORKDIR ${PROJECT_DIR}

# Copy the local model files to the image
COPY ./models/v1-2-0/ ./models/v1-2-0/

COPY requirements.txt .

# Install build dependencies, build the Python packages, and remove build dependencies to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    netcat \
    info \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc python3-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

EXPOSE ${VIRTUAL_PORT}
