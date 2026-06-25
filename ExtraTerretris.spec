# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'entities.enemy', 'entities.bullets', 'entities.nave',
        'entities.fades', 'entities.asteroid', 'entities.background',
        'entities.body', 'entities.effect', 'entities.powers',
        'entities.powerstack', 'entities.powerstores', 'entities.projectile',
        'entities.winlosescreens',
        'gameplay', 'gameplay.config', 'gameplay.game', 'gameplay.setup',
        'tetris', 'tetris.grid', 'tetris.tetris',
        'ui', 'ui.button', 'ui.text', 'ui.persondisplay',
        'config', 'config.sounds', 'config.tabs', 'config.preload',
        'engine', 'engine.const', 'engine.object', 'engine.screen',
        'engine.vector2', 'engine.mouse', 'engine.imagecache',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ExtraTerretris',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/nave.ico',
)
