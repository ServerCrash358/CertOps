import logging
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RemediationSimulator:
    def __init__(self, current_pods: int, current_cpu: float, current_latency: float):
        self.current_pods = current_pods
        self.current_cpu = current_cpu
        self.current_latency = current_latency

    def simulate_scale(self, new_replicas: int) -> Dict[str, Any]:
        cpu_reduction = min(0.7, (new_replicas - self.current_pods) * 0.15)
        predicted_cpu = self.current_cpu * (1 - cpu_reduction)
        predicted_latency = self.current_latency * (1 - cpu_reduction * 0.8)

        return {
            "action": f"scale_pods_{self.current_pods}_to_{new_replicas}",
            "predicted_cpu": round(predicted_cpu, 2),
            "predicted_latency": round(predicted_latency, 2),
            "latency_improvement": round((self.current_latency - predicted_latency) / self.current_latency * 100, 1),
            "cost_increase": round((new_replicas - self.current_pods) / self.current_pods * 100, 1) if self.current_pods > 0 else 0
        }

    def simulate_restart(self) -> Dict[str, Any]:
        return {
            "action": "restart_pods",
            "predicted_cpu": round(self.current_cpu * 0.8, 2),
            "predicted_latency": self.current_latency * 1.2,
            "latency_improvement": -20,
            "risk": "temporary_downtime",
            "downtime_seconds": 30
        }

    def run_counterfactuals(self, candidates: List[Dict]) -> List[Dict]:
        results = []
        for candidate in candidates:
            if candidate["type"] == "scale":
                result = self.simulate_scale(candidate["replicas"])
            elif candidate["type"] == "restart":
                result = self.simulate_restart()
            else:
                result = {"action": candidate["type"], "unknown": True}
            results.append(result)
        return results


def select_best_plan(results: List[Dict]) -> Dict:
    if not results:
        raise ValueError("No simulation results provided")
    valid = [r for r in results if r.get("latency_improvement", 0) > 0 and "risk" not in r]
    if not valid:
        best = min(results, key=lambda x: x.get("predicted_latency", float('inf')))
        logger.warning(f"No safe plans found, selecting lowest latency: {best['action']}")
        return best
    best = max(valid, key=lambda x: x["latency_improvement"])
    logger.info(f"Selected plan: {best['action']} with {best['latency_improvement']}% improvement")
    return best
