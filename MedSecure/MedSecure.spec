# MedSecure.spec — PyInstaller build specification
# ===================================================
# Build command: pyinstaller MedSecure.spec
#
# This produces a single-folder dist/MedSecure/ with MedSecure.exe
# For a single-file exe use onefile=True (slower startup, larger file)

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect all hidden imports needed by cryptography and PyQt5
hiddenimports = (
    collect_submodules('cryptography') +
    collect_submodules('PyQt5') +
    ['PIL', 'PIL.Image', 'numpy', 'app', 'app.core', 'app.ui', 'app.controllers']
)

datas = collect_data_files('cryptography') + collect_data_files('PyQt5')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MedSecure',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No console window (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Add icon path here: icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MedSecure',
)
