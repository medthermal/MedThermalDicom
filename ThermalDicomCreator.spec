# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\thx_dcm\\steja-private-cursor-create-thermal-dicom-python-package-02b5\\steja-private-cursor-create-thermal-dicom-python-package-02b5\\simple_dicom_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\thx_dcm\\steja-private-cursor-create-thermal-dicom-python-package-02b5\\steja-private-cursor-create-thermal-dicom-python-package-02b5\\thermal_dicom', 'thermal_dicom')],
    hiddenimports=['pydicom', 'numpy', 'PIL', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
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
    name='ThermalDicomCreator',
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
)
