import os
import sys
import PyInstaller.__main__

NAME = "ExtraTerretris"

icon = "assets/nave.ico" if sys.platform == "win32" else "assets/nave.png"
hidden = [
    "entities.enemy", "entities.bullets", "entities.nave",
    "entities.fades", "entities.asteroid", "entities.background",
    "entities.body", "entities.effect", "entities.powers",
    "entities.powerstack", "entities.powerstores", "entities.projectile",
    "entities.winlosescreens",
    "gameplay", "gameplay.config", "gameplay.game", "gameplay.setup",
    "tetris", "tetris.grid", "tetris.tetris",
    "ui", "ui.button", "ui.text", "ui.persondisplay",
    "config", "config.sounds", "config.tabs", "config.preload",
    "engine", "engine.const", "engine.object", "engine.screen",
    "engine.vector2", "engine.mouse", "engine.imagecache",
    "pplay", "pplay.window", "pplay.keyboard", "pplay.mouse",
    "pplay.sound", "pplay.gameimage", "pplay.gameobject",
    "pplay.sprite", "pplay.collision", "pplay.point", "pplay.animation",
]
args = [
    "main.py",
    "--name", NAME,
    "--onefile",
    "--add-data", f"assets{os.pathsep}assets",
    "--clean",
    "--noconfirm",
    "--icon", icon,
    "--collect-all", "entities",
    "--collect-all", "pplay",
]
for h in hidden:
    args += ["--hidden-import", h]
if sys.platform == "win32":
    args.insert(3, "--noconsole")

PyInstaller.__main__.run(args)
