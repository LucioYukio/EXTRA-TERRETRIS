import os
import sys
import PyInstaller.__main__

NAME = "ExtraTerretris"

icon = "assets/nave.ico" if sys.platform == "win32" else "assets/nave.png"
args = [
    "main.py",
    "--name", NAME,
    "--onefile",
    "--add-data", f"assets{os.pathsep}assets",
    "--clean",
    "--noconfirm",
    "--icon", icon,
]
if sys.platform == "win32":
    args.insert(3, "--noconsole")

PyInstaller.__main__.run(args)
