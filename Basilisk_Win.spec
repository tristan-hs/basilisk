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
             pathex=['C:\\Users\\taq\\Desktop\\basilisk'],
             binaries=[],
             datas=get_resources(),
             hiddenimports=['tcod','numpy'],
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
          icon="C:\\Users\\taq\\Desktop\\basilisk\\resources\\icon.ico" )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Basilisk')


"""

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
             pathex=['/Applications/MAMP/htdocs/basilisk'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Basilisk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )


    info_plist = {}
    app = BUNDLE(exe,
                 name='Basilisk.app',
                 bundle_identifier=None,
                 icon=None,
                 info_plist=info_plist
                )
"""
