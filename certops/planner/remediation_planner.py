import ollama


def suggest_pod_remediation(failure):

    prompt = f"""
Pod {failure['pod']} in namespace {failure['namespace']} is in state {failure['status']}.

Suggest possible remediation steps.
"""

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]