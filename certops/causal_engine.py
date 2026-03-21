from typing import Dict, List, Tuple
import re


class CausalGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, name: str, metric_type: str, value: float):
        self.nodes[name] = {"type": metric_type, "value": value}

    def add_edge(self, cause: str, effect: str, strength: float = 1.0):
        self.edges.append({"cause": cause, "effect": effect, "strength": strength})

    def find_root_cause(self, symptom: str) -> List[Tuple[str, float]]:
        causes = []
        for edge in self.edges:
            if edge["effect"] == symptom:
                causes.append((edge["cause"], edge["strength"]))
        return sorted(causes, key=lambda x: x[1], reverse=True)

    def to_dict(self) -> Dict:
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }


def build_causal_model(metrics: Dict) -> CausalGraph:
    graph = CausalGraph()

    graph.add_node("traffic", "input", metrics.get("traffic", 100))
    graph.add_node("cpu", "resource", metrics.get("cpu", 50))
    graph.add_node("memory", "resource", metrics.get("memory", 60))
    graph.add_node("latency", "output", metrics.get("latency", 200))
    graph.add_node("errors", "output", metrics.get("errors", 0.01))

    graph.add_edge("traffic", "cpu", 0.9)
    graph.add_edge("traffic", "memory", 0.6)
    graph.add_edge("cpu", "latency", 0.8)
    graph.add_edge("memory", "latency", 0.5)
    graph.add_edge("cpu", "errors", 0.4)

    return graph


def analyze_root_cause(failure: Dict, metrics: Dict) -> Dict:
    graph = build_causal_model(metrics)

    root_causes = []
    if failure["status"] in ["CrashLoopBackOff", "OOMKilled"]:
        root_causes = graph.find_root_cause("memory")
    elif failure["status"] == "Error":
        root_causes = graph.find_root_cause("cpu")

    return {
        "failure": failure,
        "causal_graph": graph.to_dict(),
        "root_causes": root_causes,
        "primary_cause": root_causes[0][0] if root_causes else "unknown"
    }
