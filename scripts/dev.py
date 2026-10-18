import os
import signal
import subprocess
import sys
import time

def main():
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"], cwd="backend")
    time.sleep(2)
    # Use shell=True for cross-platform npm invocation on Windows/Linux/macOS
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend", shell=(sys.platform == "win32"))
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