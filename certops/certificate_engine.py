import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Certificate:
    def __init__(self, incident_id: str, action: str, safety_proofs: Dict[str, Any]):
        self.incident_id = incident_id
        self.action = action
        self.safety_proofs = safety_proofs
        self.timestamp = datetime.utcnow().isoformat()
        self.certificate_id = self._generate_id()

    def _generate_id(self) -> str:
        data = f"{self.incident_id}{self.action}{self.timestamp}"
        cert_id = hashlib.sha256(data.encode()).hexdigest()[:16]
        logger.debug(f"Generated certificate ID: {cert_id}")
        return cert_id

    def to_dict(self) -> Dict:
        return {
            "certificate_id": self.certificate_id,
            "incident_id": self.incident_id,
            "action": self.action,
            "timestamp": self.timestamp,
            "safety_proofs": self.safety_proofs,
            "status": "CERTIFIED"
        }

    def sign(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def generate_certificate(incident_id: str, action: str, safety_proofs: Dict) -> Certificate:
    if not incident_id or not action:
        raise ValueError("incident_id and action are required")
    cert = Certificate(incident_id, action, safety_proofs)
    logger.info(f"Generated certificate {cert.certificate_id} for incident {incident_id}")
    return cert
