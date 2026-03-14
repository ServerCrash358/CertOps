import subprocess


def get_pod_status():

    result = subprocess.run(
        ["kubectl", "get", "pods", "-A"],
        capture_output=True,
        text=True
    )

    return result.stdout