# -*- mode: python ; coding: utf-8 -*-
import sys
from webdriver_manager.microsoft import EdgeChromiumDriverManager

driver_path = EdgeChromiumDriverManager().install()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[(driver_path, '.')],
    datas=[],
    hiddenimports=['spacy.lang.ru_core_news_sm', 'spacy.lang.ru', 'sklearn.feature_extraction.text', 'dateparser', 'multiprocessing', 'openpyxl.cell._writer', 'openpyxl.utils', 'openpyxl.cell', 'openpyxl.cell.text', 'openpyxl.worksheet._writer', 'selenium', 'selenium.webdriver.edge.service'],
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
    name='PhotoDNA',
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