# -*- coding: utf-8 -*-
from os.path import normpath
from colorpecker import STORAGEDIR, log
from colorpecker.color import COLORFORMATS
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class Settings:
    """ Settings all contained within a context menu. """

    def __init__(self, parent):
        self.parent = parent        # Qobj menu is applied to
        self.menu = None            # Conext menu object
        self._initStorage()         # Settings storage
        self._initMenu()            # Initialize the menu

    @property
    def alwaysOnTop(self):
        """ Get the Always On Top value. """
        return self.storage.value('alwaysOnTop', 'true').lower() == 'true'

    @property
    def showOpacity(self):
        """ Get the Show Opacity value. """
        return self.storage.value('showOpacity', 'true').lower() == 'true'

    def _initStorage(self):
        """ Initialize settings storage. """
        filepath = f'{STORAGEDIR}/ColorPecker/colorpecker.ini'
        self.storage = QtCore.QSettings(filepath, QtCore.QSettings.IniFormat)
        log.info(f'ColorPecker Settings: {normpath(self.storage.fileName())}')

    def _initMenu(self):
        """ Initialize the menu. """
        self.menu = QtWidgets.QMenu()
        # Always on Top
        self.menu.alwaysOnTop = QtGui.QAction('Always on Top', self.parent)
        self.menu.alwaysOnTop.setCheckable(True)
        self.menu.alwaysOnTop.triggered.connect(self.setAlwaysOnTop)
        self.menu.addAction(self.menu.alwaysOnTop)
        self.setAlwaysOnTop(self.alwaysOnTop)
        # Show Opacity
        self.menu.showOpacity = QtGui.QAction('Show Opacity', self.parent)
        self.menu.showOpacity.setCheckable(True)
        self.menu.showOpacity.triggered.connect(self.setShowOpacity)
        self.menu.addAction(self.menu.showOpacity)
        self.setShowOpacity(self.showOpacity)
        # TODO: INIT VALUE
        # Color Formats
        self.menu.formats = QtWidgets.QMenu('Color Format')
        for cformat in COLORFORMATS:
            text = self.parent.color.format(cformat)
            faction = QtGui.QAction(text, self.parent)
            self.menu.formats.addAction(faction)
        self.menu.addMenu(self.menu.formats)
        # Link menu to parent widget
        self.parent.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.parent.customContextMenuRequested.connect(self.show)
    
    def show(self, pos):
        self.menu.exec_(self.parent.mapToGlobal(pos))

    def setAlwaysOnTop(self, value=None):
        """ Set always on top value. Toggles value if None. """
        log.info(f'setAlwaysOnTop({value})')
        value = value if value is not None else not self.alwaysOnTop
        pos = self.parent.pos()
        flags = self.parent.windowFlags()
        log.info(flags)
        if value: flags |= Qt.WindowStaysOnTopHint
        else: flags &= ~Qt.WindowStaysOnTopHint
        log.info(flags)
        self.parent.setWindowFlags(flags)
        self.parent.show(pos)
        self.menu.alwaysOnTop.setChecked(value)
        self.storage.setValue('alwaysOnTop', value)
        self.storage.sync()

    def setShowOpacity(self, value=None):
        """ Toggle show opacity value. """
        log.info(f'setShowOpacity({value})')
        value = not self.showOpacity if value is None else value
        self.parent.ids.a.setValue(100)
        self.parent.ids.a.setVisible(value)
        self.menu.showOpacity.setChecked(value)
        self.storage.setValue('showOpacity', value)
        self.storage.sync()

    def updateColorFormats(self, color):
        """ Update the color format choices to match current color. """
        for i, action in enumerate(self.menu.formats.actions()):
            cformat = COLORFORMATS[i]
            action.setText(color.format(cformat))
