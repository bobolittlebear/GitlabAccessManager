# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Files', '(x86)\\Lib\\site-packages', 'mainWindow.py'],
             pathex=['D:\\Program', 'D:\\工作\\GitlabAccess2.0\\GitlabAccess 2.0'],
             binaries=[],
             datas=[('./data/', './data')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Files',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Files')
