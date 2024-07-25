# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

# Collect metadata for pyvisa, pyvisa-py, and zeroconf
datas = copy_metadata('pyvisa')
datas += copy_metadata('pyvisa-py')
datas += copy_metadata('zeroconf')

# Add pyvisa, pyvisa-py, and zeroconf to hidden imports
hiddenimports = ['pyvisa', 'pyvisa_py', 'zeroconf']

a = Analysis(
    ['VB_AVA_Python.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],  # Ensure this points to where hook-pyvisa.py is located
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VB_AVA_Python',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VB_AVA_Python'
)
