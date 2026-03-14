import ollama

def suggest_remediation(alert):

    prompt = f"""
Kubernetes node {alert['node']} has CPU usage of {alert['cpu']}%.

Suggest possible remediation steps.
"""

    response = ollama.chat(
        model="phi3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    alert = {
        "node": "minikube",
        "cpu": 92
    }

    result = suggest_remediation(alert)

    print("\nSuggested remediation:\n")
    print(result)