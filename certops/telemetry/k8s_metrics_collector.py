import subprocess

def get_node_metrics():
    try:
        result = subprocess.run(
            ["kubectl", "top", "nodes"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Error retrieving metrics")
            return None

        return result.stdout

    except Exception as e:
        print("Telemetry error:", e)
        return None


if __name__ == "__main__":
    metrics = get_node_metrics()
    print(metrics)