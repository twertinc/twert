# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static'), ('flask_admin', 'flask_admin'), (r"C:\Users\Nam Anh\twert\env\Lib\site-packages\en_core_web_sm", "en_core_web_sm")],
    hiddenimports=[r"C:\Users\Nam Anh\twert\Classify\Classify.py",'scikit-learn', 'sklearn', 'sklearn.calibration', 'sklearn.metrics._pairwise_distances_reduction._datasets_pair', 'sklearn.metrics._pairwise_distances_reduction._middle_term_computer'],
    hookspath=[],   
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='run',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
