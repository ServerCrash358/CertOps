import subprocess
from typing import Dict, Any

from certops.certificate_engine import Certificate


class ExecutionController:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.executed = []

    def execute(self, certificate: Certificate, namespace: str, deployment: str) -> Dict[str, Any]:
        if certificate.to_dict()["status"] != "CERTIFIED":
            return {"error": "Certificate not valid", "executed": False}

        action = certificate.action

        if self.dry_run:
            return {
                "certificate_id": certificate.certificate_id,
                "action": action,
                "status": "DRY_RUN",
                "would_execute": f"kubectl scale deployment {deployment} -n {namespace} --replicas=5"
            }

        if "scale" in action.lower():
            replicas = self._extract_replicas(action)
            result = subprocess.run(
                ["kubectl", "scale", "deployment", deployment, "-n", namespace, f"--replicas={replicas}"],
                capture_output=True, text=True
            )

            self.executed.append(certificate.certificate_id)
            return {
                "certificate_id": certificate.certificate_id,
                "action": action,
                "status": "EXECUTED",
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        return {"error": "Unknown action", "executed": False}

    def _extract_replicas(self, action: str) -> int:
        parts = action.split("_")
        for p in parts:
            if p.isdigit():
                return int(p)
        return 3


def execute_certified_action(certificate: Certificate, namespace: str, deployment: str, dry_run: bool = True) -> Dict:
    controller = ExecutionController(dry_run=dry_run)
    return controller.execute(certificate, namespace, deployment)
