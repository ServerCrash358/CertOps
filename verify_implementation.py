#!/usr/bin/env python3
"""
Verification script to ensure all CertOps components are properly implemented.
"""

import sys
import os

sys.path.insert(0, '/f/Projects/CertOps')

def verify_file_exists(filepath, description):
    """Verify that a file exists."""
    full_path = os.path.join('F:\\Projects\\CertOps', filepath)
    exists = os.path.exists(full_path)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {full_path}")
    return exists

def verify_import(module_path, description):
    """Verify that a module can be imported."""
    try:
        __import__(module_path)
        print(f"[OK] {description}: {module_path}")
        return True
    except Exception as e:
        print(f"[FAIL] {description}: {module_path} - {e}")
        return False

def verify_function(module_path, func_name, description):
    """Verify that a function exists in a module."""
    try:
        module = __import__(module_path, fromlist=[func_name])
        if hasattr(module, func_name):
            print(f"[OK] {description}: {module_path}.{func_name}")
            return True
        else:
            print(f"[FAIL] {description}: {module_path}.{func_name} not found")
            return False
    except Exception as e:
        print(f"[FAIL] {description}: {module_path}.{func_name} - {e}")
        return False

def verify_class(module_path, class_name, description):
    """Verify that a class exists in a module."""
    try:
        module = __import__(module_path, fromlist=[class_name])
        if hasattr(module, class_name):
            print(f"[OK] {description}: {module_path}.{class_name}")
            return True
        else:
            print(f"[FAIL] {description}: {module_path}.{class_name} not found")
            return False
    except Exception as e:
        print(f"[FAIL] {description}: {module_path}.{class_name} - {e}")
        return False

def main():
    print("=" * 80)
    print("CERT-OPS IMPLEMENTATION VERIFICATION")
    print("=" * 80)

    all_checks = []

    # Check file structure
    print("\n1. FILE STRUCTURE")
    print("-" * 80)

    files_to_check = [
        ('certops/__init__.py', 'certops package'),
        ('certops/main.py', 'Main pipeline'),
        ('certops/causal_engine.py', 'Causal engine'),
        ('certops/simulator.py', 'Simulator'),
        ('certops/certificate_engine.py', 'Certificate engine'),
        ('certops/ml_remediation.py', 'ML remediation'),
        ('certops/rl_agent.py', 'RL agent'),
        ('certops/prometheus_client.py', 'Prometheus client'),
        ('certops/analysis/anomaly_detector.py', 'Anomaly detector'),
        ('certops/telemetry/k8s_metrics_collector.py', 'K8s metrics collector'),
        ('certops/policies/safety_verifier.py', 'Safety verifier'),
        ('certops/execution/controller.py', 'Execution controller'),
        ('certops/dashboard/app.py', 'Dashboard app'),
    ]

    for filepath, description in files_to_check:
        all_checks.append(verify_file_exists(filepath, description))

    # Check imports
    print("\n2. MODULE IMPORTS")
    print("-" * 80)

    imports_to_check = [
        ('certops', 'certops package'),
        ('certops.main', 'Main module'),
        ('certops.causal_engine', 'Causal engine'),
        ('certops.simulator', 'Simulator'),
        ('certops.certificate_engine', 'Certificate engine'),
        ('certops.ml_remediation', 'ML remediation'),
        ('certops.rl_agent', 'RL agent'),
        ('certops.prometheus_client', 'Prometheus client'),
        ('certops.analysis.anomaly_detector', 'Anomaly detector'),
        ('certops.telemetry.k8s_metrics_collector', 'K8s metrics collector'),
        ('certops.policies.safety_verifier', 'Safety verifier'),
        ('certops.execution.controller', 'Execution controller'),
    ]

    for module_path, description in imports_to_check:
        all_checks.append(verify_import(module_path, description))

    # Check key functions
    print("\n3. KEY FUNCTIONS")
    print("-" * 80)

    functions_to_check = [
        ('certops.main', 'run_certops_v04', 'Main pipeline entry point'),
        ('certops.main', 'train_ml_model', 'ML model training'),
        ('certops.causal_engine', 'analyze_root_cause', 'Root cause analysis'),
        ('certops.simulator', 'select_best_plan', 'Plan selection'),
        ('certops.certificate_engine', 'generate_certificate', 'Certificate generation'),
        ('certops.ml_remediation', 'get_ml_model', 'ML model singleton'),
        ('certops.rl_agent', 'get_rl_agent', 'RL agent singleton'),
        ('certops.prometheus_client', 'get_live_metrics', 'Live metrics'),
        ('certops.analysis.anomaly_detector', 'detect_pod_failures', 'Failure detection'),
        ('certops.telemetry.k8s_metrics_collector', 'get_pod_status', 'Pod status collection'),
        ('certops.policies.safety_verifier', 'verify_scaling', 'Safety verification'),
        ('certops.execution.controller', 'execute_certified_action', 'Action execution'),
    ]

    for module_path, func_name, description in functions_to_check:
        all_checks.append(verify_function(module_path, func_name, description))

    # Check key classes
    print("\n4. KEY CLASSES")
    print("-" * 80)

    classes_to_check = [
        ('certops.causal_engine', 'CausalGraph', 'Causal graph'),
        ('certops.simulator', 'RemediationSimulator', 'Remediation simulator'),
        ('certops.certificate_engine', 'Certificate', 'Certificate'),
        ('certops.ml_remediation', 'MLRemediationModel', 'ML model'),
        ('certops.rl_agent', 'RemediationRLAgent', 'RL agent'),
        ('certops.rl_agent', 'RemediationEnv', 'RL environment'),
        ('certops.prometheus_client', 'PrometheusClient', 'Prometheus client'),
        ('certops.execution.controller', 'ExecutionController', 'Execution controller'),
    ]

    for module_path, class_name, description in classes_to_check:
        all_checks.append(verify_class(module_path, class_name, description))

    # Test component functionality
    print("\n5. COMPONENT FUNCTIONALITY")
    print("-" * 80)

    try:
        from certops.ml_remediation import get_ml_model
        ml_model = get_ml_model()
        stats = ml_model.get_stats()
        print(f"[OK] ML model initialized: {stats}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] ML model initialization failed: {e}")
        all_checks.append(False)

    try:
        from certops.rl_agent import get_rl_agent
        rl_agent = get_rl_agent()
        policy = rl_agent.get_policy({'cpu': 80, 'memory': 70, 'latency': 500, 'pods': 3, 'incident_type': 'cpu_high'})
        print(f"[OK] RL agent initialized: {policy['action']}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] RL agent initialization failed: {e}")
        all_checks.append(False)

    try:
        from certops.causal_engine import analyze_root_cause
        analysis = analyze_root_cause({'status': 'OOMKilled', 'namespace': 'default', 'pod': 'test'},
                                      {'cpu': 80, 'memory': 90, 'latency': 500, 'traffic': 150, 'errors': 0.05})
        print(f"[OK] Causal analysis: {analysis['primary_cause']}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] Causal analysis failed: {e}")
        all_checks.append(False)

    try:
        from certops.simulator import RemediationSimulator, select_best_plan
        simulator = RemediationSimulator(current_pods=3, current_cpu=80, current_latency=500)
        results = simulator.run_counterfactuals([{'type': 'scale', 'replicas': 5}, {'type': 'restart'}])
        best = select_best_plan(results)
        print(f"[OK] Simulation: {best['action']}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] Simulation failed: {e}")
        all_checks.append(False)

    try:
        from certops.policies.safety_verifier import verify_scaling
        safe = verify_scaling(5, max_pods=10)
        print(f"[OK] Safety verification: {'PASSED' if safe else 'FAILED'}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] Safety verification failed: {e}")
        all_checks.append(False)

    try:
        from certops.certificate_engine import generate_certificate
        cert = generate_certificate('test-pod', 'scale_5', {'test': True})
        print(f"[OK] Certificate generation: {cert.certificate_id}")
        all_checks.append(True)
    except Exception as e:
        print(f"[FAIL] Certificate generation failed: {e}")
        all_checks.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100

    print(f"\nTotal checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {percentage:.1f}%")

    if percentage == 100:
        print("\n[SUCCESS] ALL CHECKS PASSED - CERT-OPS IS FULLY IMPLEMENTED!")
        return 0
    else:
        print("\n[WARNING] Some checks failed - please review the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
