from certops.telemetry.k8s_metrics_collector import get_pod_status
from certops.analysis.anomaly_detector import detect_pod_failures
from certops.planner.remediation_planner import suggest_pod_remediation


def run_certops():

    pods = get_pod_status()

    failures = detect_pod_failures(pods)

    if not failures:
        print("No incidents detected")
        return

    for failure in failures:

        print("\nIncident detected:")
        print(failure)

        suggestion = suggest_pod_remediation(failure)

        print("\nSuggested remediation:\n")
        print(suggestion)


if __name__ == "__main__":
    run_certops()