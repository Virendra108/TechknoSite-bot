import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
python = ROOT / ".venv" / "Scripts" / "python.exe"
bot = ROOT / "bot.py"
stdout = (ROOT / "outputs" / "bot_stdout.log").open("ab")
stderr = (ROOT / "outputs" / "bot_stderr.log").open("ab")

proc = subprocess.Popen(
    [str(python), str(bot)],
    cwd=ROOT,
    stdout=stdout,
    stderr=stderr,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
)
(ROOT / "outputs" / "bot.pid").write_text(str(proc.pid), encoding="utf-8")
print(f"Started bot.py with PID {proc.pid}")
