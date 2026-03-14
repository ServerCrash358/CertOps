import subprocess

def create_crashloop():

    subprocess.run([
        "kubectl",
        "run",
        "crash-test",
        "--image=busybox",
        "--restart=Always",
        "--",
        "sh",
        "-c",
        "while true; do exit 1; done"
    ])

    print("CrashLoopBackOff scenario created")


if __name__ == "__main__":
    create_crashloop()