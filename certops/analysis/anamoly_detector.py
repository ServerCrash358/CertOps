def detect_high_cpu(metrics_text):

    lines = metrics_text.strip().split("\n")

    alerts = []

    for line in lines[1:]:
        parts = line.split()

        node = parts[0]
        cpu_percent = parts[2].replace("%", "")

        cpu_percent = int(cpu_percent)

        if cpu_percent > 80:
            alerts.append({
                "node": node,
                "cpu": cpu_percent
            })

    return alerts