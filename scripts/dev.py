import subprocess, sys, os, signal, time

def main():
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd="backend")
    time.sleep(2)
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()

if __name__ == "__main__":
    main()
EOF