import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)

class PrometheusClient:
    """Client to fetch real metrics from Prometheus."""

    def __init__(self, url: str = "http://localhost:9090"):
        self.url = url.rstrip('/')
        self.session = requests.Session()

    def query(self, promql: str) -> Optional[float]:
        """Execute Prometheus query and return scalar value."""
        try:
            resp = self.session.get(
                f"{self.url}/api/v1/query",
                params={"query": promql},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "success":
                logger.warning(f"Query failed: {data.get('error')}")
                return None

            result = data.get("data", {}).get("result", [])
            if not result:
                return None

            value = result[0].get("value", [])
            if len(value) >= 2:
                return float(value[1])

        except Exception as e:
            logger.error(f"Failed to query Prometheus: {e}")
            return None

    def get_pod_metrics(self, namespace: str = "default") -> Dict[str, float]:
        """Get key metrics for pods in namespace."""
        metrics = {}

        # CPU usage percentage
        cpu_query = f'''
            avg(
                rate(container_cpu_usage_seconds_total{{
                    namespace="{namespace}",
                    container!=""
                }}[5m])
            ) * 100
        '''
        metrics["cpu"] = self.query(cpu_query) or 50.0

        # Memory usage percentage
        mem_query = f'''
            avg(
                container_memory_usage_bytes{{
                    namespace="{namespace}",
                    container!=""
                }} /
                container_spec_memory_limit_bytes{{
                    namespace="{namespace}",
                    container!=""
                }} * 100
            )
        '''
        metrics["memory"] = self.query(mem_query) or 60.0

        # Request latency (p95)
        latency_query = f'''
            histogram_quantile(0.95,
                sum(rate(http_request_duration_seconds_bucket{{
                    namespace="{namespace}"
                }}[5m])) by (le)
            ) * 1000
        '''
        latency = self.query(latency_query) or 200.0
        metrics["latency"] = latency

        # Request rate (traffic)
        traffic_query = f'''
            sum(rate(http_requests_total{{
                namespace="{namespace}"
            }}[5m]))
        '''
        traffic = self.query(traffic_query)
        metrics["traffic"] = traffic if traffic else 100.0

        # Error rate
        error_query = f'''
            sum(rate(http_requests_total{{
                namespace="{namespace}",
                status=~"5.."
            }}[5m])) /
            sum(rate(http_requests_total{{
                namespace="{namespace}"
            }}[5m])) * 100
        '''
        error_rate = self.query(error_query)
        metrics["errors"] = error_rate if error_rate is not None else 0.1

        logger.info(f"Fetched metrics for {namespace}: {metrics}")
        return metrics

    def is_healthy(self) -> bool:
        """Check if Prometheus is reachable."""
        try:
            resp = self.session.get(f"{self.url}/-/healthy", timeout=5)
            return resp.status_code == 200
        except:
            return False


# Global client
_prom_client: Optional[PrometheusClient] = None

def get_prometheus_client(url: str = "http://localhost:9090") -> PrometheusClient:
    """Get or create Prometheus client."""
    global _prom_client
    if _prom_client is None:
        _prom_client = PrometheusClient(url)
    return _prom_client


def get_live_metrics(namespace: str = "default") -> Dict[str, float]:
    """Get live metrics from Prometheus or fallback to defaults."""
    client = get_prometheus_client()

    if client.is_healthy():
        return client.get_pod_metrics(namespace)

    logger.warning("Prometheus not available, using fallback metrics")
    return {
        "cpu": 75.0,
        "memory": 65.0,
        "latency": 300.0,
        "traffic": 120.0,
        "errors": 0.05
    }
