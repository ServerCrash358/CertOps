import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

class MLRemediationModel:
    """ML model that learns from past incident outcomes to predict best remediation."""

    def __init__(self, model_path: str = "certops/models/remediation_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.action_encoder = LabelEncoder()
        self.status_encoder = LabelEncoder()
        self.is_trained = False

        # Training data storage
        self.training_data: List[Dict] = []
        self.data_path = self.model_path.parent / "training_data.json"

        # Try to load existing model
        self._load_model()

    def _extract_features(self, incident: Dict, metrics: Dict) -> np.ndarray:
        """Convert incident + metrics into feature vector."""
        features = [
            # Incident features
            hash(incident.get('status', 'unknown')) % 1000,  # Encode status as number
            len(incident.get('pod', '')),
            hash(incident.get('namespace', 'default')) % 100,

            # Metrics features
            metrics.get('cpu', 50),
            metrics.get('memory', 60),
            metrics.get('latency', 200),
            metrics.get('traffic', 100),
            metrics.get('errors', 0.01) * 100,  # Scale up errors

            # Time-based feature
            datetime.now().hour,
        ]
        return np.array(features).reshape(1, -1)

    def predict(self, incident: Dict, metrics: Dict) -> Dict[str, Any]:
        """Predict the best remediation action for given incident."""
        if not self.is_trained:
            logger.warning("Model not trained, using fallback strategy")
            return self._fallback_prediction(incident, metrics)

        features = self._extract_features(incident, metrics)
        action_idx = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        action = self.action_encoder.inverse_transform([action_idx])[0]
        confidence = float(probabilities[action_idx])

        logger.info(f"ML prediction: {action} (confidence: {confidence:.2f})")

        return {
            "action": action,
            "confidence": confidence,
            "all_probabilities": {
                self.action_encoder.inverse_transform([i])[0]: float(p)
                for i, p in enumerate(probabilities)
            }
        }

    def _fallback_prediction(self, incident: Dict, metrics: Dict) -> Dict[str, Any]:
        """Rule-based fallback when model isn't trained."""
        status = incident.get('status', '')
        cpu = metrics.get('cpu', 50)

        if status == 'OOMKilled':
            action = "scale_memory"
        elif status == 'CrashLoopBackOff' and cpu > 80:
            action = "scale_5"
        elif cpu > 70:
            action = "scale_5"
        else:
            action = "restart"

        return {
            "action": action,
            "confidence": 0.5,
            "fallback": True
        }

    def record_outcome(self, incident: Dict, metrics: Dict,
                       action: str, success: bool, latency_improvement: float):
        """Record the outcome of a remediation for future training."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "incident_status": incident.get('status'),
            "namespace": incident.get('namespace'),
            "metrics": metrics,
            "action_taken": action,
            "success": success,
            "latency_improvement": latency_improvement
        }
        self.training_data.append(record)
        self._save_training_data()
        logger.info(f"Recorded outcome: {action} -> {'success' if success else 'failure'}")

    def train(self) -> bool:
        """Train model on collected training data."""
        if len(self.training_data) < 5:
            logger.warning(f"Need at least 5 samples, have {len(self.training_data)}")
            return False

        # Prepare training data
        X = []
        y = []

        for record in self.training_data:
            features = [
                hash(record['incident_status']) % 1000,
                hash(record['namespace']) % 100,
                record['metrics']['cpu'],
                record['metrics']['memory'],
                record['metrics']['latency'],
                record['metrics']['traffic'],
                record['latency_improvement'],
            ]
            X.append(features)
            y.append(record['action_taken'])

        X = np.array(X)
        y = self.action_encoder.fit_transform(y)

        # Train model
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.model.fit(X, y)
        self.is_trained = True

        self._save_model()
        logger.info(f"Model trained on {len(X)} samples")
        return True

    def _save_model(self):
        """Save trained model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'action_encoder': self.action_encoder,
                'status_encoder': self.status_encoder
            }, f)

    def _load_model(self):
        """Load trained model from disk."""
        if self.model_path.exists():
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.action_encoder = data['action_encoder']
                self.status_encoder = data['status_encoder']
                self.is_trained = True
                logger.info("Loaded existing model")

        # Load training data
        if self.data_path.exists():
            with open(self.data_path) as f:
                self.training_data = json.load(f)

    def _save_training_data(self):
        """Save training data to JSON."""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, 'w') as f:
            json.dump(self.training_data, f, indent=2)

    def get_stats(self) -> Dict:
        """Get model statistics."""
        return {
            "trained": self.is_trained,
            "training_samples": len(self.training_data),
            "actions": list(self.action_encoder.classes_) if self.is_trained else [],
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self) -> float:
        """Calculate success rate from training data."""
        if not self.training_data:
            return 0.0
        successes = sum(1 for r in self.training_data if r['success'])
        return successes / len(self.training_data)


# Global model instance
_ml_model: Optional[MLRemediationModel] = None

def get_ml_model() -> MLRemediationModel:
    """Get or create singleton ML model."""
    global _ml_model
    if _ml_model is None:
        _ml_model = MLRemediationModel()
    return _ml_model
