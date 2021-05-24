# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['freeform_minesweeper.py'],
             pathex=['C:\\Users\\Nyxian\\github\\FreeForm-Minesweeper'],
             binaries=[],
             datas=[('assets', 'assets'), ('presets', 'presets')],
             hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
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
          name='Freeform-Minesweeper',
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
               name='Freeform-Minesweeper')
