import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from certops.certificate_engine import generate_certificate
from certops.causal_engine import analyze_root_cause
from certops.simulator import RemediationSimulator, select_best_plan
from certops.policies.safety_verifier import verify_scaling
from certops.ml_remediation import get_ml_model
from certops.rl_agent import get_rl_agent
from certops.prometheus_client import get_live_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CertOps Dashboard", version="0.4.0")

app.mount("/static", StaticFiles(directory="certops/dashboard/static"), name="static")
templates = Jinja2Templates(directory="certops/dashboard/templates")


class Incident(BaseModel):
    id: str
    pod: str
    namespace: str
    status: str
    timestamp: str


INCIDENTS: List[Incident] = []
CERTIFICATES: List[Dict] = []
ML_STATS: Dict[str, Any] = {}


@app.get("/")
async def dashboard(request: Request):
    ml_model = get_ml_model()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "incidents": INCIDENTS,
        "certificates": CERTIFICATES,
        "ml_stats": ml_model.get_stats(),
        "version": "0.4.0"
    })


@app.get("/api/incidents")
async def get_incidents() -> List[Incident]:
    return INCIDENTS


@app.post("/api/incidents")
async def create_incident(incident: Incident):
    INCIDENTS.append(incident)
    logger.info(f"New incident: {incident.id}")
    return incident


@app.post("/api/remediate/{incident_id}")
async def remediate(incident_id: str) -> Dict[str, Any]:
    incident = next((i for i in INCIDENTS if i.id == incident_id), None)
    if not incident:
        return {"error": "Incident not found"}

    # v0.4: Get LIVE metrics from Prometheus
    metrics = get_live_metrics(incident.namespace)

    # Causal analysis
    analysis = analyze_root_cause(
        {"pod": incident.pod, "namespace": incident.namespace, "status": incident.status},
        metrics
    )

    # v0.4: ML Prediction
    ml_model = get_ml_model()
    ml_pred = ml_model.predict(
        {"pod": incident.pod, "namespace": incident.namespace, "status": incident.status},
        metrics
    )

    # v0.4: RL Policy
    rl_agent = get_rl_agent()
    rl_policy = rl_agent.get_policy({
        'cpu': metrics['cpu'],
        'memory': metrics['memory'],
        'latency': metrics['latency'],
        'pods': 3,
        'incident_type': incident.status
    })

    # Simulate
    sim = RemediationSimulator(3, metrics['cpu'], metrics['latency'])
    candidates = [{"type": "scale", "replicas": 5}, {"type": "scale", "replicas": 8}]
    results = sim.run_counterfactuals(candidates)
    best = select_best_plan(results)

    # Verify
    safe = verify_scaling(5, max_pods=10)

    # Certificate
    cert = generate_certificate(incident_id, best["action"], {
        "simulation": best,
        "safety": safe,
        "root_cause": analysis["primary_cause"],
        "ml_prediction": ml_pred,
        "rl_policy": rl_policy,
        "live_metrics": metrics
    })

    cert_data = cert.to_dict()
    CERTIFICATES.append(cert_data)

    # Record for ML training
    ml_model.record_outcome(
        {"pod": incident.pod, "namespace": incident.namespace, "status": incident.status},
        metrics,
        best["action"],
        success=best.get("latency_improvement", 0) > 0,
        latency_improvement=best.get("latency_improvement", 0)
    )

    return {
        "incident": incident_id,
        "root_cause": analysis["primary_cause"],
        "action": best["action"],
        "improvement": best.get("latency_improvement", 0),
        "certificate": cert.certificate_id,
        "safety_passed": safe,
        "ml_prediction": ml_pred,
        "rl_policy": rl_policy,
        "live_metrics": metrics
    }


@app.get("/api/certificates")
async def get_certificates() -> List[Dict]:
    return CERTIFICATES


@app.get("/api/ml/stats")
async def get_ml_stats() -> Dict:
    ml_model = get_ml_model()
    return ml_model.get_stats()


@app.post("/api/ml/train")
async def train_ml() -> Dict:
    ml_model = get_ml_model()
    success = ml_model.train()
    return {"trained": success, "stats": ml_model.get_stats()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
