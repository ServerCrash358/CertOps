def detect_pod_failures(pod_output):

    failures = []

    lines = pod_output.strip().split("\n")

    for line in lines[1:]:

        parts = line.split()

        if len(parts) < 4:
            continue

        namespace = parts[0]
        pod = parts[1]
        status = parts[3]

        if status in [
            "CrashLoopBackOff",
            "ImagePullBackOff",
            "Error",
            "OOMKilled"
        ]:

            failures.append({
                "namespace": namespace,
                "pod": pod,
                "status": status
            })

    return failures