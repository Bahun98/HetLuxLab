# HetLuxLab.spec
# No need for __file__ or project_dir

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],  # Leave blank or add a hardcoded path if needed
    binaries=[],
    datas=[
        ('real_data.xlsx', '.'),               # Excel file in root
        ('icons/luxlabicon.png', 'icons'),     # Icon
    ],
    hiddenimports=[],
    hookspath=[],
    excludes=['PowerBI'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LuxLabApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LuxLabApp'
)
