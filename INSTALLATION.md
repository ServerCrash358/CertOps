# CertOps Installation Guide

This guide provides step-by-step instructions for installing and setting up CertOps and its dependencies.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install Python Dependencies](#install-python-dependencies)
- [Install Docker and Docker Compose](#install-docker-and-docker-compose)
- [Install kubectl](#install-kubectl)
- [Install Prometheus and Grafana](#install-prometheus-and-grafana)
- [Configure Environment Variables](#configure-environment-variables)
- [Run CertOps](#run-certops)
- [Verify Installation](#verify-installation)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **CPU**: 2+ cores
- **RAM**: 8GB+ recommended
- **Disk Space**: 5GB+ available
- **Internet**: Required for downloading dependencies

### Required Software

1. Python 3.8 or higher
2. pip (Python package manager)
3. Docker (for containerized deployment)
4. Docker Compose
5. kubectl (for Kubernetes integration)
6. Git (for source code management)

## Install Python Dependencies

### Install Python

#### Windows

Download and install Python from [python.org](https://www.python.org/downloads/):

```powershell
# Check if Python is installed
python --version

# If not installed, download and install from python.org
# Make sure to check "Add Python to PATH" during installation
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

#### macOS

```bash
brew install python
```

### Install pip packages

```bash
# Navigate to CertOps directory
cd /f/Projects/CertOps

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(numpy|scikit|z3|requests|fastapi)"
```

### Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Install Docker and Docker Compose

Docker is required for running Prometheus, Grafana, and other monitoring components.

### Windows

Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop):

```powershell
# Install Docker Desktop (GUI installer)
# Start Docker Desktop after installation

# Verify installation
docker --version
docker-compose --version
```

### Linux (Ubuntu/Debian)

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
```

### macOS

```bash
brew install --cask docker

# Start Docker Desktop
open -a Docker

# Verify installation
docker --version
docker-compose --version
```

## Install kubectl

kubectl is required for interacting with Kubernetes clusters.

### Windows

```powershell
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/windows/amd64/kubectl.exe"

# Add to PATH
Move-Item .\kubectl.exe C:\Windows\System32\kubectl.exe

# Verify installation
kubectl version --client
```

### Linux (Ubuntu/Debian)

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

### macOS

```bash
brew install kubectl

# Verify installation
kubectl version --client
```

## Install Prometheus and Grafana

Prometheus and Grafana are used for monitoring and metrics collection.

### What Prometheus Contributes

Prometheus provides:
- **Real-time metrics collection** from Kubernetes pods
- **Time-series database** for storing metrics
- **Query language (PromQL)** for analyzing metrics
- **Alerting** based on metric thresholds

CertOps uses Prometheus to:
1. Query CPU usage of pods
2. Query memory usage of pods
3. Query request latency (p95)
4. Query traffic (requests per second)
5. Query error rates

### What Grafana Contributes

Grafana provides:
- **Visualization dashboard** for metrics
- **Customizable dashboards** for different use cases
- **Alerting UI** for managing alerts
- **Data source integration** with Prometheus

CertOps uses Grafana to:
1. Visualize system metrics
2. Monitor incident detection
3. Track remediation actions
4. Analyze system health over time

### Running Prometheus and Grafana with Docker

```bash
# Navigate to CertOps directory
cd /f/Projects/CertOps

# Start Prometheus, Grafana, and Loki
docker-compose up -d

# Verify containers are running
docker ps

# You should see:
# - prometheus
# - grafana
# - loki
# - certops (optional)
```

### Access Prometheus

- **URL**: http://localhost:9090
- **Username**: (none)
- **Password**: (none)

### Access Grafana

- **URL**: http://localhost:3000
- **Username**: admin
- **Password**: admin

### Access Loki

- **URL**: http://localhost:3100
- **Username**: (none)
- **Password**: (none)

### Configure Grafana Data Sources

After logging into Grafana (admin/admin):

1. Click "Configuration" (gear icon) → "Data Sources"
2. Click "Add data source"
3. Select "Prometheus"
4. Set URL to: `http://prometheus:9090`
5. Click "Save & Test"

### Import Grafana Dashboards

Grafana dashboards are configured in `config/grafana/provisioning/dashboards/`.

## Configure Environment Variables

CertOps uses environment variables for configuration.

### Set Environment Variables

#### Windows (PowerShell)

```powershell
# Set Prometheus URL
$env:PROMETHEUS_URL = "http://localhost:9090"

# Disable dry-run mode (for production)
$env:DRY_RUN = "false"
```

#### Linux/macOS (Bash)

```bash
# Set Prometheus URL
export PROMETHEUS_URL="http://localhost:9090"

# Disable dry-run mode (for production)
export DRY_RUN="false"
```

### Permanent Configuration

To make environment variables persistent:

#### Windows

```powershell
# Edit system environment variables
[System.Environment]::SetEnvironmentVariable('PROMETHEUS_URL', 'http://localhost:9090', 'User')
[System.Environment]::SetEnvironmentVariable('DRY_RUN', 'true', 'User')
```

#### Linux/macOS

```bash
# Add to ~/.bashrc or ~/.zshrc
echo "export PROMETHEUS_URL='http://localhost:9090'" >> ~/.bashrc
echo "export DRY_RUN='true'" >> ~/.bashrc

# Reload source file
source ~/.bashrc
```

## Run CertOps

### Run the Main Pipeline

```bash
# Navigate to CertOps directory
cd /f/Projects/CertOps

# Run the main pipeline
python -m certops.main

# Expected output:
# - RL agent training (500 episodes)
# - Incident detection
# - Metrics collection
# - Root cause analysis
# - ML and RL predictions
# - Simulation
# - Safety verification
# - Certificate generation
# - Execution (dry-run)
```

### Run the Dashboard

```bash
# Run the FastAPI dashboard
python -m certops.dashboard.app

# Or with uvicorn:
uvicorn certops.dashboard.app:app --host 0.0.0.0 --port 8000

# Access dashboard at: http://localhost:8000
```

### Run Tests

```bash
# Run comprehensive pipeline test
python test_pipeline.py

# Run verification script
python verify_implementation.py

# Train ML model
python -c "from certops.main import train_ml_model; train_ml_model()"
```

## Verify Installation

### Check Python Environment

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(numpy|scikit|z3|requests|fastapi)"

# Expected packages:
# numpy
# scikit-learn
# z3-solver
# requests
# fastapi
```

### Check Docker Containers

```bash
# List running containers
docker ps

# Expected containers:
# - prometheus
# - grafana
# - loki
```

### Check kubectl

```bash
# Check kubectl version
kubectl version --client
```

### Run Verification Script

```bash
python verify_implementation.py

# Expected result: 51/51 checks passed
```

## Troubleshooting

### Common Issues

#### Docker not starting

```bash
# Restart Docker service
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker
```

#### Prometheus not accessible

```bash
# Check if Prometheus is running
docker ps | grep prometheus

# Restart Prometheus
docker-compose restart prometheus
```

#### Grafana login issues

```bash
# Default credentials: admin/admin
# If you forgot password, reset with:
docker exec -it grafana grafana-cli admin reset-admin-password newpassword
```

#### Python module not found

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Permission denied

```bash
# On Linux, add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Next Steps

After successful installation:

1. ✅ Run `python verify_implementation.py` to verify all components
2. ✅ Run `python test_pipeline.py` to test the full pipeline
3. ✅ Connect to real Prometheus (if available)
4. ✅ Test with real Kubernetes cluster (if available)
5. ✅ Collect more training data for ML model
6. ✅ Disable dry-run mode for production use

## Uninstallation

To completely remove CertOps and its dependencies:

```bash
# Stop and remove containers
docker-compose down

# Remove virtual environment
rm -rf venv

# Uninstall Python packages
pip uninstall numpy scikit-learn z3-solver requests fastapi uvicorn

# Remove CertOps directory
rm -rf /f/Projects/CertOps
```

## Support

For issues or questions:
- Check the [README.md](README.md) for project overview
- Check [CLAUDE.md](CLAUDE.md) for development guide
- Check [COMPLETION_REPORT.md](COMPLETION_REPORT.md) for verification details

## Summary

You have successfully installed CertOps with:
- ✅ Python dependencies
- ✅ Docker and Docker Compose
- ✅ kubectl
- ✅ Prometheus (metrics collection)
- ✅ Grafana (visualization)
- ✅ Loki (logging)

The system is ready for testing and deployment!
