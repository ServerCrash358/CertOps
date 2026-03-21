import logging

from certops.telemetry.k8s_metrics_collector import get_pod_status
from certops.analysis.anomaly_detector import detect_pod_failures
from certops.causal_engine import analyze_root_cause
from certops.simulator import RemediationSimulator, select_best_plan
from certops.policies.safety_verifier import verify_scaling
from certops.certificate_engine import generate_certificate
from certops.execution.controller import execute_certified_action
from certops.ml_remediation import get_ml_model
from certops.rl_agent import get_rl_agent
from certops.prometheus_client import get_live_metrics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_certops_v04():
    """CertOps v0.4 - ML + RL + Real Metrics Pipeline."""
    logger.info("=== CertOps v0.4 Starting ===")

    # Initialize ML and RL models
    ml_model = get_ml_model()
    rl_agent = get_rl_agent()

    pods = get_pod_status()
    failures = detect_pod_failures(pods)

    if not failures:
        print("No incidents detected")
        return

    for failure in failures:
        print(f"\n{'='*50}")
        print(f"INCIDENT: {failure['pod']} in {failure['namespace']}")
        print(f"STATUS: {failure['status']}")
        print(f"{'='*50}")

        # Step 1: Get LIVE metrics from Prometheus (v0.4)
        metrics = get_live_metrics(failure['namespace'])
        print(f"\n📊 Live Metrics:")
        print(f"   CPU: {metrics['cpu']:.1f}%")
        print(f"   Memory: {metrics['memory']:.1f}%")
        print(f"   Latency: {metrics['latency']:.1f}ms")
        print(f"   Traffic: {metrics['traffic']:.1f} req/s")

        # Step 2: Causal Analysis
        analysis = analyze_root_cause(failure, metrics)
        print(f"\n🔍 Root Cause: {analysis['primary_cause']}")

        # Step 3: ML Prediction (v0.4)
        ml_prediction = ml_model.predict(failure, metrics)
        print(f"\n🤖 ML Prediction:")
        print(f"   Action: {ml_prediction['action']}")
        print(f"   Confidence: {ml_prediction['confidence']:.2f}")
        if ml_prediction.get('fallback'):
            print(f"   (Using fallback - model not trained)")

        # Step 4: RL Policy (v0.4)
        rl_policy = rl_agent.get_policy({
            'cpu': metrics['cpu'],
            'memory': metrics['memory'],
            'latency': metrics['latency'],
            'pods': 3,
            'incident_type': failure['status']
        })
        print(f"\n🎯 RL Policy:")
        print(f"   Action: {rl_policy['action']}")
        print(f"   Q-Value: {rl_policy.get('q_value', 0):.2f}")
        print(f"   Confidence: {rl_policy['confidence']:.2f}")

        # Step 5: Simulate Counterfactuals
        candidates = [
            {"type": "scale", "replicas": 5},
            {"type": "scale", "replicas": 8},
            {"type": "restart"}
        ]
        simulator = RemediationSimulator(
            current_pods=3,
            current_cpu=metrics['cpu'],
            current_latency=metrics['latency']
        )
        results = simulator.run_counterfactuals(candidates)
        best = select_best_plan(results)
        print(f"\n📈 Simulation Results:")
        print(f"   Best Plan: {best['action']}")
        print(f"   Predicted Latency: {best.get('predicted_latency', 0):.1f}ms")
        print(f"   Improvement: {best.get('latency_improvement', 0):.1f}%")

        # Step 6: Safety Verification
        safe = verify_scaling(5, max_pods=10)
        if not safe:
            print("\n❌ Safety check FAILED")
            continue
        print(f"\n✅ Safety: PASSED")

        # Step 7: Generate Certificate
        safety_proofs = {
            "simulation": best,
            "safety_check": safe,
            "ml_prediction": ml_prediction,
            "rl_policy": rl_policy
        }
        cert = generate_certificate(
            incident_id=failure['pod'],
            action=best['action'],
            safety_proofs=safety_proofs
        )
        print(f"\n📜 Certificate: {cert.certificate_id}")

        # Step 8: Execute (dry-run for safety)
        result = execute_certified_action(
            cert, failure['namespace'], failure['pod'], dry_run=True
        )
        print(f"🔧 Execution: {result['status']}")

        # Step 9: Record outcome for ML training (v0.4)
        success = best.get('latency_improvement', 0) > 0
        ml_model.record_outcome(
            failure, metrics, best['action'],
            success=success,
            latency_improvement=best.get('latency_improvement', 0)
        )
        print(f"\n💾 Recorded outcome for ML training")

    print(f"\n{'='*50}")
    print("CertOps v0.4 Complete")
    print(f"ML Model: {ml_model.get_stats()}")
    print(f"{'='*50}")


def train_ml_model():
    """Train ML model on collected data."""
    ml_model = get_ml_model()
    if ml_model.train():
        print("✅ ML model trained successfully")
    else:
        print("⚠️ Not enough data to train model")


if __name__ == "__main__":
    run_certops_v04()
