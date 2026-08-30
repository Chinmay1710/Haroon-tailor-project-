# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/assets', 'assets')],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineCore', 'PySide6.QtWebChannel', 
        'sqlalchemy', 'sqlite3', 'reportlab',
        'app.models.customer', 'app.models.measurement', 'app.models.order',
        'app.models.payment', 'app.models.expense', 'app.models.settings',
        'app.models.worker', 'app.models.stock',
        'app.services.stock_service', 'app.services.worker_service', 'app.services.dictation_service',
        'app.services.order_service', 'app.services.customer_service', 'app.services.whatsapp_service',
        'app.services.backup_service', 'app.services.pdf_service',
        'app.web.tunnel', 'app.web.server', 'app.printing.receipt_printer',
        'pyngrok', 'fastapi', 'uvicorn', 'pydantic', 'qrcode', 'speech_recognition'
    ],
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
    name='Haroon Tailor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/assets/www/img/logo.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Haroon Tailor',
)
