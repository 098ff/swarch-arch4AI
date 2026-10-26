"""Start all three services on this machine. Stop them with Ctrl+C.

    python run_all.py

gateway            http://127.0.0.1:8000   (clients call this)
review service     http://127.0.0.1:8001
inference service  http://127.0.0.1:8002

Each service also has interactive API docs at /docs.
After you change any code, stop with Ctrl+C and start again.
"""
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx

from common import settings

ROOT = Path(__file__).resolve().parent
SERVICES = [("inference service", "inference_service.app:app", settings.INFERENCE_PORT),
            ("review service", "review_service.app:app", settings.REVIEW_PORT),
            ("gateway", "gateway.app:app", settings.GATEWAY_PORT)]


def wait_healthy(port, proc, seconds=60):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        try:
            if httpx.get(f"http://{settings.HOST}:{port}/health", timeout=1).status_code == 200:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(0.3)
    return False


def _stop(signum, frame):
    raise KeyboardInterrupt


def main():
    # stop the services too when this script is killed or its terminal is closed
    for sig in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if sig is not None:
            signal.signal(sig, _stop)
    procs = []
    try:
        for name, target, port in SERVICES:
            p = subprocess.Popen([sys.executable, "-m", "uvicorn", target, "--host", settings.HOST,
                                  "--port", str(port), "--log-level", "warning"], cwd=ROOT)
            procs.append(p)
            if not wait_healthy(port, p):
                print(f"{name} did not start on port {port}. See the error above. If it says the address\n"
                      "is already in use, an earlier run is still going: stop it, or close that terminal.")
                return 1
            print(f"{name:18} http://{settings.HOST}:{port}   (docs: /docs)")
        print("\nAll services are up. Open a second terminal for tools/loadtest.py. Ctrl+C stops everything.")
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
        print("A service stopped unexpectedly. See the error above.")
        return 1
    except KeyboardInterrupt:
        print("\nStopping...")
        return 0
    finally:
        for p in procs:
            p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    sys.exit(main())
