from pathlib import Path
import os
import signal
import subprocess
import time


ROOT = Path(__file__).resolve().parent
pid_file = ROOT / "outputs" / "bot.pid"

if not pid_file.exists():
    print("No bot PID file found.")
    raise SystemExit(0)

pid = int(pid_file.read_text(encoding="utf-8").strip())
try:
    os.kill(pid, signal.SIGTERM)
except ProcessLookupError:
    print(f"Bot process {pid} is not running.")
    raise SystemExit(0)

for _ in range(10):
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if str(pid) not in result.stdout:
        break
    time.sleep(0.5)
else:
    subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=False)

print(f"Stopped bot.py PID {pid}")
