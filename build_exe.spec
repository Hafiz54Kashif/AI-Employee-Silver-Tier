# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

BASE = Path(r'D:\Agentic AI\Assignments\AI_Employee_Project\AI_Employee_Project')

a = Analysis(
    [str(BASE / 'dashboard' / 'app.py')],
    pathex=[str(BASE)],
    binaries=[],
    datas=[
        (str(BASE / 'dashboard' / 'templates'), 'dashboard/templates'),
        (str(BASE / 'dashboard' / '_app_secrets.py'), 'dashboard'),
        (str(BASE / 'watchers'), 'watchers'),
        (str(BASE / 'vault' / 'Company_Handbook.md'), 'vault'),
        (str(BASE / 'vault' / 'Business_Goals.md'), 'vault'),
        (str(BASE / 'vault' / 'Dashboard.md'), 'vault'),
        (str(BASE / 'settings.json'), '.'),
    ],
    hiddenimports=[
        'flask', 'jinja2', 'werkzeug', 'click',
        'anthropic', 'imaplib', 'smtplib', 'email',
        'requests', 'pathlib', 'json', 'subprocess',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Employee',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Employee',
)
