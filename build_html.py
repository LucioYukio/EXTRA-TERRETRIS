import subprocess
import sys

subprocess.run(
    [sys.executable, "-m", "pygbag", "--build", "--disable-sound-format-error", "."],
    check=True,
)
