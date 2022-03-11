# -*- mode: python ; coding: utf-8 -*-
import os
import platform

block_cipher = None

def get_resources():
    data_files = []
    for file_name in os.listdir('resources'):
        data_files.append((os.path.join('resources', file_name), 'resources'))
    return data_files

a = Analysis(['main.py'],
             binaries=[],
             datas=get_resources(),
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
          name='Basilisk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon="icon.ico" )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Basilisk')

if platform.system() == 'Darwin':
      app = BUNDLE(coll,
                   name='Basilisk.app',
                   icon='resources/icon.png',
                   bundle_identifier=None)
