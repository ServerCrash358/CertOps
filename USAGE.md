# CertOps Usage Guide

This guide provides detailed instructions for using CertOps in various scenarios.

## Table of Contents

- [Quick Start](#quick-start)
- [Running CertOps](#running-certops)
  - [Main Pipeline](#main-pipeline)
  - [Dashboard](#dashboard)
  - [Tests](#tests)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Files](#configuration-files)
- [Commands Reference](#commands-reference)
  - [Pipeline Commands](#pipeline-commands)
  - [ML Model Commands](#ml-model-commands)
  - [RL Agent Commands](#rl-agent-commands)
  - [Simulation Commands](#simulation-commands)
  - [Safety Verification Commands](#safety-verification-commands)
- [Docker Commands](#docker-commands)
- [Kubernetes Commands](#kubernetes-commands)
- [Monitoring Commands](#monitoring-commands)
- [Development Commands](#development-commands)
- [Troubleshooting Commands](#troubleshooting-commands)
- [Examples](#examples)

## Quick Start

```bash
# 1. Navigate to CertOps directory
cd /f/Projects/CertOps

# 2. Start monitoring stack
docker-compose up -d

# 3. Run CertOps pipeline
python -m certops.main

# 4. Access dashboard
open http://localhost:8000

# 5. Access Prometheus
open http://localhost:9090

# 6. Access Grafana
open http://localhost:3000
```

## Running CertOps

### Main Pipeline

The main pipeline implements the 8-stage safety-certified remediation workflow.

```bash
# Run the main pipeline
python -m certops.main

# Run with verbose logging
python -m certops.main -v

# Run in development mode
DEBUG=1 python -m certops.main
```

**What happens when you run this command:**

1. **Telemetry Collection**: Gathers pod status via kubectl
2. **Incident Detection**: Detects failures (CrashLoopBackOff, OOMKilled, Error)
3. **Causal Analysis**: Builds causal graph to identify root causes
4. **ML Prediction**: Predicts best action using RandomForest classifier
5. **RL Policy**: Generates policy using Q-learning agent
6. **Simulation**: Tests scale(5), scale(8), restart scenarios
7. **Safety Verification**: Verifies constraints with Z3 solver
8. **Certificate Generation**: Generates SHA256-signed certificate
9. **Execution**: Executes certified action (dry-run by default)
10. **Learning**: Records outcome for future training

### Dashboard

The dashboard provides a web interface for monitoring CertOps operations.

```bash
# Run the dashboard
python -m certops.dashboard.app

# Run with uvicorn (recommended for production)
uvicorn certops.dashboard.app:app --host 0.0.0.0 --port 8000

# Run with auto-reload (development)
uvicorn certops.dashboard.app:app --reload --host 0.0.0.0 --port 8000

# Access dashboard
open http://localhost:8000
```

**Dashboard Features:**
- View current incidents
- Monitor remediation status
- Review certificates
- Track ML model performance
- View system metrics

### Tests

CertOps includes comprehensive tests for all components.

```bash
# Run all tests
python test_pipeline.py

# Run verification script
python verify_implementation.py

# Run specific component tests
python -m pytest test/cases/test_ml_model.py -v

# Run integration tests
python -m pytest test/cases/test_integration.py -v
```

## Configuration

### Environment Variables

CertOps uses environment variables for configuration.

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMETHEUS_URL` | `http://localhost:9090` | Prometheus endpoint |
| `DRY_RUN` | `true` | Set to `false` to enable actual kubectl execution |
| `DEBUG` | `0` | Set to `1` for verbose logging |

**Setting environment variables:**

```bash
# Temporary (current session only)
export PROMETHEUS_URL="http://prometheus:9090"
export DRY_RUN="false"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo "export PROMETHEUS_URL='http://prometheus:9090'" >> ~/.bashrc
echo "export DRY_RUN='false'" >> ~/.bashrc
source ~/.bashrc
```

### Configuration Files

CertOps configuration files are in the `config/` directory:

```
config/
├── prometheus.yml          # Prometheus scraping configuration
├── loki.yml                # Loki logging configuration
└── grafana/provisioning/  # Grafana dashboards and data sources
    ├── dashboards/
    │   └── certops.json     # CertOps dashboard
    └── datasources/
        └── prometheus.yml   # Prometheus data source
```

## Commands Reference

### Pipeline Commands

```bash
# Run main pipeline
python -m certops.main

# Run specific pipeline version
python -c "from certops.main import run_certops_v04; run_certops_v04()"

# Run with custom configuration
PROMETHEUS_URL="http://custom-prom:9090" python -m certops.main
```

### ML Model Commands

```bash
# Get ML model instance
python -c "from certops.ml_remediation import get_ml_model; print(get_ml_model().get_stats())"

# Train ML model
python -c "from certops.main import train_ml_model; train_ml_model()"

# Check model statistics
python -c "from certops.ml_remediation import get_ml_model; print(get_ml_model().get_stats())"

# Record outcome manually
python -c "
from certops.ml_remediation import get_ml_model
ml = get_ml_model()
ml.record_outcome(
    {'status': 'OOMKilled', 'namespace': 'default', 'pod': 'test'},
    {'cpu': 80, 'memory': 90, 'latency': 500, 'traffic': 150, 'errors': 0.05},
    'scale_5',
    success=True,
    latency_improvement=30.0
)
"
```

### RL Agent Commands

```bash
# Get RL agent instance
python -c "from certops.rl_agent import get_rl_agent; print(get_rl_agent().get_policy({'cpu': 80, 'memory': 70, 'latency': 500, 'pods': 3, 'incident_type': 'cpu_high'}))"

# Train RL agent
python -c "from certops.rl_agent import get_rl_agent; agent = get_rl_agent(); agent.train(episodes=100)"

# Get policy for specific state
python -c "
from certops.rl_agent import get_rl_agent
agent = get_rl_agent()
policy = agent.get_policy({
    'cpu': 85,
    'memory': 80,
    'latency': 600,
    'pods': 3,
    'incident_type': 'memory_high'
})
print(f'Action: {policy[\"action\"]}, Confidence: {policy[\"confidence\"]}')
"
```

### Simulation Commands

```bash
# Run simulation
python -c "
from certops.simulator import RemediationSimulator, select_best_plan
sim = RemediationSimulator(current_pods=3, current_cpu=80, current_latency=500)
candidates = [{'type': 'scale', 'replicas': 5}, {'type': 'restart'}]
results = sim.run_counterfactuals(candidates)
best = select_best_plan(results)
print(f'Best plan: {best}')
"

# Simulate specific action
python -c "
from certops.simulator import RemediationSimulator
sim = RemediationSimulator(current_pods=3, current_cpu=80, current_latency=500)
result = sim.simulate_scale(5)
print(f'Scale to 5: {result}')
"
```

### Safety Verification Commands

```bash
# Verify scaling
python -c "from certops.policies.safety_verifier import verify_scaling; print(verify_scaling(5, max_pods=10))"

# Verify with custom constraints
python -c "
from certops.policies.safety_verifier import verify_scaling
print('Safe:', verify_scaling(15, max_pods=10))
print('Unsafe:', verify_scaling(15, max_pods=12))
"
```

## Docker Commands

### Starting Services

```bash
# Start all services (Prometheus, Grafana, Loki, CertOps)
docker-compose up -d

# Start specific service
docker-compose up -d prometheus
docker-compose up -d grafana

# Start in foreground (show logs)
docker-compose up
```

### Managing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View logs
docker logs prometheus
docker logs grafana

# Restart service
docker-compose restart prometheus

# Stop service
docker-compose stop prometheus

# Stop all services
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Accessing Services

```bash
# Access Prometheus
docker exec -it prometheus bash

# Access Grafana
docker exec -it grafana bash

# Access CertOps container
docker exec -it certops bash

# Run command in container
docker exec certops python -m certops.main
```

## Kubernetes Commands

### Pod Management

```bash
# Get pod status (used by CertOps)
kubectl get pods -A

# Get pod details
kubectl get pods -n <namespace> -o wide

# Describe pod
kubectl describe pod <pod-name> -n <namespace>

# Get pod logs
kubectl logs <pod-name> -n <namespace>
```

### Deployment Management

```bash
# Scale deployment (what CertOps does)
kubectl scale deployment <deployment> -n <namespace> --replicas=5

# Rollout status
kubectl rollout status deployment/<deployment> -n <namespace>

# Restart deployment
kubectl rollout restart deployment/<deployment> -n <namespace>
```

### Node Management

```bash
# Get node status
kubectl get nodes

# Describe node
kubectl describe node <node-name>

# Get node metrics
kubectl top nodes
```

## Monitoring Commands

### Prometheus Queries

```bash
# Query CPU usage
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=container_cpu_usage_seconds_total'

# Query memory usage
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=container_memory_usage_bytes'

# Query latency
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))'
```

### Grafana Commands

```bash
# Restart Grafana
docker-compose restart grafana

# Reset Grafana admin password
docker exec -it grafana grafana-cli admin reset-admin-password newpassword

# Backup Grafana database
docker exec -it grafana grafana-cli admin backup /var/lib/grafana/grafana.db
```

### Loki Commands

```bash
# Query logs
curl -G http://localhost:3100/loki/api/v1/query_range --data-urlencode 'query={namespace="default"}'

# View Loki logs
docker logs loki
```

## Development Commands

### Code Quality

```bash
# Run linter
flake8 certops/

# Run type checker
mypy certops/

# Format code
autopep8 --in-place --recursive certops/
```

### Testing

```bash
# Run all tests
python -m pytest test/cases/ -v

# Run specific test
python -m pytest test/cases/test_ml_model.py -v

# Run with coverage
python -m pytest test/cases/ --cov=certops --cov-report=html

# Run doctests
python -m doctest certops/*.py -v
```

### Debugging

```bash
# Run with debug logging
DEBUG=1 python -m certops.main

# Run with pdb
python -m pytest test/cases/test_ml_model.py -v --pdb

# Profile performance
python -m cProfile -o profile.stats -m certops.main

# View profile results
python -m pstats profile.stats
```

## Troubleshooting Commands

### Common Issues

```bash
# Docker not starting
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Prometheus not accessible
curl -v http://localhost:9090

# Grafana login issues
docker exec -it grafana grafana-cli admin reset-admin-password newpassword

# Python module not found
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Permission denied
# Linux: sudo usermod -aG docker $USER
# Then log out and back in
```

### Diagnostic Commands

```bash
# Check Python environment
python --version
pip list | grep -E "(numpy|scikit|z3|requests|fastapi)"

# Check Docker version
docker --version
docker-compose --version

# Check kubectl version
kubectl version --client

# Check network connections
netstat -tuln | grep 9090
netstat -tuln | grep 3000

# Check running processes
ps aux | grep python
```

## Examples

### Example 1: Full Pipeline Execution

```bash
#!/bin/bash
# full_pipeline.sh

# Set environment
cd /f/Projects/CertOps
source venv/bin/activate

# Start monitoring stack
docker-compose up -d

# Wait for services to start
sleep 10

# Run CertOps pipeline
echo "Running CertOps pipeline..."
python -m certops.main

# Check results
echo "Pipeline completed. Check dashboard at http://localhost:8000"
```

### Example 2: ML Model Training

```bash
#!/bin/bash
# train_ml_model.sh

# Set environment
cd /f/Projects/CertOps
source venv/bin/activate

# Run pipeline to collect data
echo "Running pipeline to collect training data..."
python -m certops.main

# Train ML model
echo "Training ML model..."
python -c "from certops.main import train_ml_model; train_ml_model()"

# Check model stats
echo "Model statistics:"
python -c "from certops.ml_remediation import get_ml_model; print(get_ml_model().get_stats())"
```

### Example 3: Safety Verification

```bash
#!/bin/bash
# verify_safety.sh

# Set environment
cd /f/Projects/CertOps
source venv/bin/activate

# Test various scaling scenarios
echo "Testing safety verification..."

# Safe scenario
python -c "from certops.policies.safety_verifier import verify_scaling; print('Safe:', verify_scaling(5, max_pods=10))"

# Unsafe scenario
python -c "from certops.policies.safety_verifier import verify_scaling; print('Unsafe:', verify_scaling(15, max_pods=10))"
```

### Example 4: Simulation Analysis

```bash
#!/bin/bash
# analyze_simulation.sh

# Set environment
cd /f/Projects/CertOps
source venv/bin/activate

# Analyze different remediation options
echo "Analyzing remediation options..."

python -c "
from certops.simulator import RemediationSimulator, select_best_plan

# High CPU scenario
print('High CPU scenario:')
sim = RemediationSimulator(current_pods=3, current_cpu=90, current_latency=800)
candidates = [
    {'type': 'scale', 'replicas': 5},
    {'type': 'scale', 'replicas': 8},
    {'type': 'restart'}
]
results = sim.run_counterfactuals(candidates)
best = select_best_plan(results)
print(f'Best: {best[\"action\"]} ({best[\"latency_improvement\"]}% improvement)')

# Memory pressure scenario
print('\nMemory pressure scenario:')
sim = RemediationSimulator(current_pods=3, current_cpu=60, current_latency=600)
results = sim.run_counterfactuals(candidates)
best = select_best_plan(results)
print(f'Best: {best[\"action\"]} ({best[\"latency_improvement\"]}% improvement)')
"
```

## Summary

This usage guide provides comprehensive commands for:

✅ **Running CertOps** (main pipeline, dashboard, tests)
✅ **Configuration** (environment variables, config files)
✅ **Docker management** (starting, stopping, logging)
✅ **Kubernetes operations** (pods, deployments, nodes)
✅ **Monitoring** (Prometheus, Grafana, Loki)
✅ **Development** (testing, debugging, code quality)
✅ **Troubleshooting** (diagnostic commands, common issues)
✅ **Examples** (ready-to-use scripts)

For more information, see:
- [README.md](README.md) - Project overview
- [CLAUDE.md](CLAUDE.md) - Development guide
- [INSTALLATION.md](INSTALLATION.md) - Installation instructions
- [PROMETHEUS_GRAFANA_GUIDE.md](PROMETHEUS_GRAFANA_GUIDE.md) - Monitoring guide
