# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_submodules
from src.version import VERSION
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--identity")
options = parser.parse_args()

block_cipher = None
sentry_sdk_submodules = collect_submodules('sentry_sdk')
hidden_imports = sentry_sdk_submodules
hidden_imports.append('pkg_resources.py2_warn')

a = Analysis(['src/app.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('src', 'src'),
             ],
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if options.identity:
   print(f" ==> Signing binaries")
   exe = EXE(pyz,
            a.scripts,
            exclude_binaries=True,
            name='cleepbus',
            debug=False,
            strip=False,
            upx=False,
            console=True,
            icon='icon.icns',
            target_arch='arm64',
            entitlements_file='entitlements.plist',
            codesign_identity=options.identity)
else:
   print(f" ==> No signing")
   exe = EXE(pyz,
            a.scripts,
            exclude_binaries=True,
            name='cleepbus',
            debug=False,
            strip=False,
            upx=False,
            console=True,
            icon='icon.icns',
            target_arch='arm64',
            entitlements_file='entitlements.plist')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='cleepbus')
