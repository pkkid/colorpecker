# -*- coding: utf-8 -*-
# Simple test will load colors each second
from colorpecker import log
from functools import partial
from PySide6 import QtCore

TESTCOLORS = [
    '#2cc',
    '#f50',
    '#2c88',
    '#25c9c8',
    '#f85800',
    '#88f868',
    '#25c9c888',
    'argb(10%, 0.146, 0.787, 0.785)',
    'MyColor(0x25c9c8)',
    # 'Color(red: 0.146, green: 0.787, blue: 0.785, opacity: 1.0)',
    # 'NSColor(red: 0.146, green: 0.787, blue: 0.785, alpha: 1.0)',
    # 'UIColor(red: 0.146, green: 0.787, blue: 0.785, alpha: 1.0)',
    # 'Color.rgb(37, 201, 200)',
    # 'Color.FromArgb(255, 37, 201, 200)',
    # 'new Color(37, 201, 200, 255)',
]


def initTests():
    log.info(f'Initilizing {len(TESTCOLORS)} tests..')
    for i, color in enumerate(TESTCOLORS):
        QtCore.QTimer.singleShot((i+1)*1000, partial(runTest, i))


def runTest(i):
    app = QtCore.QCoreApplication.instance()
    app.colorpecker.setColor(TESTCOLORS[i])
