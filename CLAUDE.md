# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CertOps is an experimental safety-verified autonomous infrastructure remediation system. It simulates and verifies remediation actions before executing them in production, reducing the risk of automated fixes making outages worse.

## Development Commands

### Running the Application

```bash
# Run the main pipeline (CLI mode)
cd certops
python main.py

# Run the dashboard (FastAPI web interface)
cd certops
python dashboard/app.py
# Or directly: uvicorn dashboard.app:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Start the full stack (Prometheus, Grafana, Loki, CertOps)
docker-compose up -d

# Access services:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - Loki: http://localhost:3100
# - CertOps Dashboard: http://localhost:8000
```

### ML Model Training

```bash
cd certops
python -c "from main import train_ml_model; train_ml_model()"
```

### Virtual Environment

```bash
# Activate existing venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Architecture Overview

CertOps implements an 8-stage safety-certified remediation pipeline:

```
Telemetry Collection
    ↓
Incident Detection (anomaly_detector.py)
    ↓
Causal Analysis (causal_engine.py - builds causal graph of root causes)
    ↓
ML Prediction (ml_remediation.py - RandomForestClassifier)
    ↓
RL Policy (rl_agent.py - Q-learning agent)
    ↓
Counterfactual Simulation (simulator.py - predicts outcomes)
    ↓
Safety Verification (policies/safety_verifier.py - Z3 SMT solver)
    ↓
Certificate Generation (certificate_engine.py)
    ↓
Execution Controller (execution/controller.py - kubectl via dry-run default)
```

## Key Components

### Core Pipeline (main.py)
- `run_certops_v04()` - Main entry point implementing v0.4 of the pipeline
- Live Prometheus metrics → ML prediction → RL policy → Simulation → Safety check → Certificate → Execution

### ML Remediation (ml_remediation.py)
- `MLRemediationModel` - RandomForest classifier that learns from past incident outcomes
- Training data stored in `certops/models/training_data.json`
- Model persisted to `certops/models/remediation_model.pkl`
- Falls back to rule-based strategy when untrained

### RL Agent (rl_agent.py)
- `RemediationRLAgent` - Q-learning agent with epsilon-greedy exploration
- `RemediationEnv` - Simulated environment for training
- Pre-trains 500 episodes on initialization
- State discretized into buckets (CPU/Memory/Latency)

### Simulator (simulator.py)
- `RemediationSimulator` - Predicts outcomes of candidate actions
- `run_counterfactuals()` - Runs "what-if" scenarios for scale/restart actions
- `select_best_plan()` - Chooses plan with highest latency improvement, no risk flags

### Safety Verification (policies/safety_verifier.py)
- Uses Z3 SMT solver for formal verification
- Currently implements: `verify_scaling(pods, max_pods)`

### Certificate Engine (certificate_engine.py)
- Generates SHA256-signed certificates containing all safety proofs
- Certificate ID is first 16 chars of hash(incident_id + action + timestamp)

### Execution Controller (execution/controller.py)
- `ExecutionController` - Only executes actions with "CERTIFIED" status
- **Dry-run mode is default** - set `dry_run=False` for actual kubectl execution
- Supports: `scale` actions via kubectl

### Prometheus Client (prometheus_client.py)
- `PrometheusClient` - Queries live metrics from Prometheus
- Returns CPU, memory, latency (p95), traffic, error rate
- Falls back to default metrics if Prometheus unreachable

## Module Structure

```
certops/
├── main.py                    # Pipeline entry point
├── causal_engine.py           # Causal graph builder for root cause analysis
├── simulator.py               # Counterfactual simulation
├── certificate_engine.py      # Safety certificate generation
├── ml_remediation.py          # ML model for remediation prediction
├── rl_agent.py                # Q-learning RL agent
├── prometheus_client.py       # Prometheus metrics client
├── telemetry/
│   └── k8s_metrics_collector.py   # kubectl pod status
├── analysis/
│   └── anomaly_detector.py      # Parse kubectl output for failures
├── planner/
│   └── remediation_planner.py     # Ollama/Phi3 LLM integration
├── policies/
│   ├── safety_verifier.py         # Z3 formal verification
│   └── policy_engine.py           # OPA (Open Policy Agent) integration
├── execution/
│   └── controller.py              # kubectl execution
├── chaos/
│   └── failure_generator.py       # Chaos engineering (creates crashloop)
└── dashboard/
    └── app.py                     # FastAPI web UI
    └── templates/index.html       # Jinja2 templates
```

## Configuration

- `config/prometheus.yml` - Prometheus scraping configuration
- `config/loki.yml` - Loki logging configuration
- `config/grafana/provisioning/` - Grafana datasources/dashboards

## Environment Variables

- `PROMETHEUS_URL` - Prometheus endpoint (default: http://prometheus:9090)
- `DRY_RUN` - Set to `false` to enable actual kubectl execution

## Data Flow

1. **Detection**: `kubectl get pods` parsed for CrashLoopBackOff/OOMKilled/Error states
2. **Metrics**: Prometheus queried for CPU%, memory%, latency, traffic, errors
3. **Causal Analysis**: Hardcoded causal graph maps traffic→CPU/memory→latency/errors
4. **ML/RL**: Both models provide action recommendations with confidence scores
5. **Simulation**: Tests scale(5), scale(8), restart options
6. **Safety**: Z3 verifies constraints (e.g., pods ≤ max_pods)
7. **Certificate**: All proofs bundled into signed certificate
8. **Execution**: Only certified actions execute via kubectl (dry-run by default)

## Notes for Development

- **Default mode is dry-run** - actual infrastructure changes require explicitly setting `dry_run=False`
- ML model needs 5+ training samples before it will train
- RL agent auto-trains 500 episodes on first import
- Prometheus connectivity is optional - system falls back to default metrics
- Dashboard uses in-memory storage for incidents/certificates (no persistence)
