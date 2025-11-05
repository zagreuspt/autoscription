# -*- mode: python ; coding: utf-8 -*-
import sysconfig
from os import path

from PyInstaller.building.api import PYZ, COLLECT, EXE
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None
site_packages = sysconfig.get_paths()["purelib"]

datas = [
    (path.join(site_packages, "azure"), "azure"),
    (path.join(site_packages, "torch"), "torch"),
    (path.join(site_packages, "pyzbar"), "pyzbar"),
    (path.join(site_packages, "stamp_processing"), "stamp_processing"),
    (path.join(site_packages, "easyocr"), "easyocr"),
    (path.join(site_packages, "signature_detect"), "signature_detect"),
    (path.join('.', "resources"), "resources"),
    (path.join('.', "tmp"), "tmp")
]
datas += copy_metadata("opentelemetry_api", recursive=True)
datas += copy_metadata("opentelemetry_sdk", recursive=True)

hidden_imports = [
                      'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
                      'sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
                      'tinycss2',
                      'babel.numbers',
                      'bidi',
                      'ttkthemes',
                      'tkcalendar',
                      'cv2',
                      'torchvision',
                      'skimage',
                      'skimage.io',
                      'skimage.measure',
                      'yaml',
                      'pdfplumber',
                      'PyPDF2',
                      'craft_text_detector',
                      'fastai',
                      'fastai.vision',
                      'fastai.vision.all',
                      'weasyprint',
                      'selenium',
                      'pyi_splash',
                      'diskcache',
                      'cryptography',
                      'tkinter.scrolledtext',
                      'xmltodict',
                      'certifi_win32',
                      'pyarrow',
                      'fastparquet'
                  ]
hidden_imports += collect_submodules('opentelemetry')
hidden_imports += collect_submodules('azure')
hidden_imports += collect_submodules('azure.monitor')
hidden_imports += collect_submodules('selenium.webdriver')
hidden_imports += collect_submodules('seleniumpagefactory')
hidden_imports += collect_submodules('wsgiref')
hidden_imports += collect_submodules('cryptography')
hidden_imports += collect_submodules('pyarrow')
hidden_imports += collect_submodules('fastparquet')

a = Analysis(
    [r'run.py'],
    pathex=[site_packages],
    binaries=[
        ('nuitka_build/autoscription_main.cp38-win_amd64.pyd', '.')
    ],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["gui",
              "core",
              "selenium_components",
              "stamp_detection",
              "signature_detection",
              "dosage_extractor",
              "coupons_detection",
              "autoscription_main.py"],
    win_no_prefer_redirects=False,
    win_private_assemblies=True,
    cipher=block_cipher,
    noarchive=True,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
splash = Splash(
    'resources/logos/splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    name='autoscription_main',
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
    icon='resources/logos/logo.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='autoscription_main',
)
