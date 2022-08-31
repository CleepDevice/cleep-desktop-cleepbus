# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_submodules

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
             cipher=block_cipher,
             info_plist={
               'NSPrincipalClass': 'NSApplication',
               'NSAppleScriptEnabled': False,
               'CFBundleIdentifier': 'com.cleep.cleepdesktopcleepbus',
               'CFBundleInfoDictionaryVersion': '6.0',
               'CFBundleName': 'CleepDesktopCleepbus',
               'CFBundlePackageType': 'APPL',
               'CFBundleDocumentTypes': [
                  {
                     'CFBundleTypeName': 'CleepDesktopCleepbus',
                     'CFBundleTypeRole': 'Shell',
                     'CFBundleTypeIconFile': 'icon.icns',
                     'LSItemContentTypes': ['com.example.myformat'],
                     'LSHandlerRank': 'Owner'
                  }
               ]
             })
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='cleepbus',
          debug=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='cleepbus')
