# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files =[
    ('betaalmail/templates/*.*', 'betaalmail/templates'),
    ('betaalmail/templates/pages/*.*', 'betaalmail/templates/pages'),
    ('betaalmail/content/*.*', 'betaalmail/content'),
    ('static/betaalmail/*.*', 'static/betaalmail'),
    ('instance/output/*.*', 'instance/output'),
    ('config.ini', '.'),
    ('venv/Lib/site-packages/pandas/io/formats/templates/html.tpl', '.'),
]

a = Analysis(
    ['app.py'],
    pathex=['C:\\Users\\lcvri\\projects_lc\\mailing_betaling'],
    binaries=[],
    datas=added_files,
    hiddenimports=['jinja2.ext'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='betaalmail',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon='static\\betaalmail\\favicon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
