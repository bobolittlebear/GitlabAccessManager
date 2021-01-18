# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['mainWindow.py'],
             pathex=['D:\\工作\\GitlabAccess2.0\\GitlabAccess 2.0'],
             binaries=[],
             datas=[('./data/projects', './data/projects'), ('./data/token', './data/token'), ('./data/exec.log', './data/exec.log')],
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
          name='oconsole',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='oconsole')
