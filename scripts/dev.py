import subprocess, sys, os

def main():
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd="backend")
    frontend = subprocess.Popen([sys.executable, "-m", "http.server", "5173"], cwd="frontend")
    try:
        backend.wait(); frontend.wait()
    except KeyboardInterrupt:
        backend.terminate(); frontend.terminate()

if __name__ == "__main__":
    main()
EOF