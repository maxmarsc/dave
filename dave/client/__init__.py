import sys
import subprocess

sys.path = (
    subprocess.check_output(
        'python -c "import os,sys;print(os.linesep.join(sys.path).strip())"', shell=True
    )
    .decode("utf-8")
    .split()
)

from .gui import DaveGUI