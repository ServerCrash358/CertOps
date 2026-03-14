import subprocess
import json

def check_policy(action, cpu):

    data = {
        "action": action,
        "cpu": cpu
    }

    result = subprocess.run(
        [
            "opa",
            "eval",
            "-i",
            "-",
            "-d",
            "certops/policies/remediation_policy.rego",
            "data.certops.allow"
        ],
        input=json.dumps(data),
        capture_output=True,
        text=True
    )

    return result.stdout