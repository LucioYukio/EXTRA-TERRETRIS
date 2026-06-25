import os
import PyInstaller.__main__

NAME = "ExtraTerretris"

PyInstaller.__main__.run([
    "main.py",
    "--name", NAME,
    "--noconsole",
    "--onefile",
    "--add-data", f"assets{os.pathsep}assets",
    "--clean",
    "--noconfirm",
])
