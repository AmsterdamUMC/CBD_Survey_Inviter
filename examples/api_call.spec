# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['api_call.py', 'get_API_access_token.py', 'get_site_list.py', 'get_survey_list.py', 'get_survey_package_list.py', 'GUI_helper_functions.py', 'GUI_module.py', 'helper_functions.py', 'log_handling.py', 'send_survey_invite.py'],
    pathex=[],
    binaries=[],
    datas=[('help_icon.png', '.')],
    hiddenimports=[],
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
    name='CDB_Survey_Inviter',
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
