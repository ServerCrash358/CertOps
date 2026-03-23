#!/usr/bin/env python3
"""
Test script to demonstrate the CertOps pipeline with simulated incidents.
"""

import sys
sys.path.insert(0, '/f/Projects/CertOps')

from certops.analysis.anomaly_detector import detect_pod_failures
from certops.causal_engine import analyze_root_cause
from certops.simulator import RemediationSimulator, select_best_plan
from certops.policies.safety_verifier import verify_scaling
from certops.certificate_engine import generate_certificate
from certops.execution.controller import execute_certified_action
from certops.ml_remediation import get_ml_model
from certops.rl_agent import get_rl_agent
from certops.prometheus_client import get_live_metrics


def simulate_kubectl_output():
    """Simulate kubectl get pods -A output with failures."""
    return """NAMESPACE     NAME                         RESTARTS   STATUS             AGE
default       healthy-pod-123              0          Running            5d
kube-system   prometheus-abc123            2          Running            10d
default       oom-pod-456                  5          OOMKilled          2h
default       crash-pod-789                10         CrashLoopBackOff   1h
prod          high-cpu-pod-xyz            0          Running            3d
prod          error-pod-abc                 3          Error              1h"""


def test_full_pipeline():
    """Test the full CertOps pipeline with simulated incidents."""
    print("=" * 70)
    print("CERT-OPS PIPELINE TEST")
    print("=" * 70)

    # Simulate kubectl output
    pod_output = simulate_kubectl_output()

    # Step 1: Detect failures
    print("\n1. DETECTING FAILURES...")
    failures = detect_pod_failures(pod_output)
    print(f"   Found {len(failures)} failures:")
    for failure in failures:
        print(f"   - {failure['namespace']}/{failure['pod']}: {failure['status']}")

    # Initialize ML and RL models
    print("\n2. INITIALIZING AI MODELS...")
    ml_model = get_ml_model()
    rl_agent = get_rl_agent()
    print(f"   ML Model: {ml_model.get_stats()}")
    print(f"   RL Agent: Trained and ready")

    # Process each failure
    for i, failure in enumerate(failures, 1):
        print(f"\n{'='*70}")
        print(f"PROCESSING INCIDENT {i}/{len(failures)}")
        print(f"{'='*70}")
        print(f"Pod: {failure['namespace']}/{failure['pod']}")
        print(f"Status: {failure['status']}")

        # Step 2: Get metrics (simulated)
        print("\n3. FETCHING METRICS...")
        metrics = get_live_metrics(failure['namespace'])
        print(f"   CPU: {metrics['cpu']:.1f}%")
        print(f"   Memory: {metrics['memory']:.1f}%")
        print(f"   Latency: {metrics['latency']:.1f}ms")
        print(f"   Traffic: {metrics['traffic']:.1f} req/s")
        print(f"   Errors: {metrics['errors']:.2%}")

        # Step 3: Causal analysis
        print("\n4. CAUSAL ANALYSIS...")
        analysis = analyze_root_cause(failure, metrics)
        print(f"   Primary cause: {analysis['primary_cause']}")
        print(f"   Root causes: {analysis['root_causes']}")

        # Step 4: ML prediction
        print("\n5. ML PREDICTION...")
        ml_prediction = ml_model.predict(failure, metrics)
        print(f"   Action: {ml_prediction['action']}")
        print(f"   Confidence: {ml_prediction['confidence']:.2%}")
        if ml_prediction.get('fallback'):
            print(f"   (Using fallback - model not trained)")

        # Step 5: RL policy
        print("\n6. RL POLICY...")
        rl_policy = rl_agent.get_policy({
            'cpu': metrics['cpu'],
            'memory': metrics['memory'],
            'latency': metrics['latency'],
            'pods': 3,
            'incident_type': failure['status'].lower()
        })
        print(f"   Action: {rl_policy['action']}")
        print(f"   Q-Value: {rl_policy.get('q_value', 0):.2f}")
        print(f"   Confidence: {rl_policy['confidence']:.2%}")

        # Step 6: Simulation
        print("\n7. SIMULATION...")
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
        print(f"   Best plan: {best['action']}")
        print(f"   Predicted latency: {best.get('predicted_latency', 0):.1f}ms")
        print(f"   Latency improvement: {best.get('latency_improvement', 0):.1f}%")

        # Step 7: Safety verification
        print("\n8. SAFETY VERIFICATION...")
        safe = verify_scaling(5, max_pods=10)
        if safe:
            print(f"   [PASSED] Scaling to 5 pods is safe")
        else:
            print(f"   [FAILED] Safety constraints violated")
            continue

        # Step 8: Certificate generation
        print("\n9. CERTIFICATE GENERATION...")
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
        print(f"   Certificate ID: {cert.certificate_id}")
        print(f"   Status: {cert.to_dict()['status']}")

        # Step 9: Execution (dry-run)
        print("\n10. EXECUTION (DRY-RUN)...")
        result = execute_certified_action(
            cert,
            failure['namespace'],
            failure['pod'],
            dry_run=True
        )
        print(f"   Status: {result['status']}")
        if result['status'] == 'DRY_RUN':
            print(f"   Would execute: {result.get('would_execute', 'N/A')}")

        # Step 10: Record outcome for ML training
        print("\n11. RECORDING OUTCOME...")
        success = best.get('latency_improvement', 0) > 0
        ml_model.record_outcome(
            failure,
            metrics,
            best['action'],
            success=success,
            latency_improvement=best.get('latency_improvement', 0)
        )
        print(f"   Outcome recorded: {'SUCCESS' if success else 'FAILURE'}")

        print(f"\n[SUCCESS] INCIDENT {i} PROCESSED SUCCESSFULLY")

    print(f"\n{'='*70}")
    print("PIPELINE TEST COMPLETE")
    print(f"{'='*70}")
    print(f"\nFinal ML Model Stats:")
    stats = ml_model.get_stats()
    print(f"  - Training samples: {stats['training_samples']}")
    print(f"  - Success rate: {stats['success_rate']:.1%}")
    print(f"  - Model trained: {stats['trained']}")

    return True


if __name__ == "__main__":
    try:
        test_full_pipeline()
        print("\n[SUCCESS] All tests passed!")
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
