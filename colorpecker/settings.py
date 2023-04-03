# -*- coding: utf-8 -*-
from os.path import normpath
from colorpecker import STORAGEDIR, log
from colorpecker.color import COLORFORMATS
from functools import partial
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class Settings:
    """ Settings all contained within a context menu. """

    def __init__(self, parent):
        self.parent = parent        # Qobj menu is applied to
        self.menu = None            # Conext menu object
        self._initStorage()         # Settings storage
        self._initMainMenu()        # Initialize the menu

    @property
    def alwaysOnTop(self):
        """ Get the Always On Top value. """
        try:
            value = self.storage.value('alwaysOnTop', 'false')
            return value.lower() == 'true'
        except Exception:
            return False

    @property
    def showOpacity(self):
        """ Get the Show Opacity value. """
        try:
            value = self.storage.value('showOpacity', 'true')
            return value.lower() == 'true'
        except Exception:
            return True
        
    @property
    def colorFormat(self):
        """ Get the Color Format. """
        try:
            cformat = self.storage.value('colorFormat', 'hex').lower()
            return COLORFORMATS[cformat]
        except Exception:
            return COLORFORMATS['hex']

    def _initStorage(self):
        """ Initialize settings storage. """
        filepath = f'{STORAGEDIR}/ColorPecker/colorpecker.ini'
        self.storage = QtCore.QSettings(filepath, QtCore.QSettings.IniFormat)
        log.info(f'ColorPecker Settings: {normpath(self.storage.fileName())}')

    def _initMainMenu(self):
        """ Initialize the main menu. """
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
        # Color Format
        self.menu.formats = QtWidgets.QMenu('Color Format')
        for cformat in COLORFORMATS.values():
            text = self.parent.color.format(cformat)
            action = QtGui.QAction(text, self.parent)
            action.setCheckable(True)
            action.triggered.connect(partial(self.setColorFormat, cformat.name))
            action.setProperty('cformat', cformat.name)
            self.menu.formats.addAction(action)
        self.menu.addMenu(self.menu.formats)
        self.setColorFormat(self.colorFormat)
        # Link main menu to parent widget
        self.parent.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.parent.customContextMenuRequested.connect(self.show)
    
    def show(self, pos):
        self.menu.exec_(self.parent.mapToGlobal(pos))

    def setAlwaysOnTop(self, value=None):
        """ Set always on top value. Toggles value if None. """
        log.info(f'setAlwaysOnTop({value})')
        if value is None:
            value = self.alwaysOnTop
        # Update Window flag
        pos = self.parent.pos()
        flags = self.parent.windowFlags()
        if value:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        self.parent.setWindowFlags(flags)
        self.parent.show(pos)
        # Update menu display and save setting
        self.menu.alwaysOnTop.setChecked(value)
        self.storage.setValue('alwaysOnTop', value)
        self.storage.sync()

    def setShowOpacity(self, value=None):
        """ Toggle show opacity value. """
        log.info(f'setShowOpacity({value})')
        if value is None:
            value = not self.showOpacity
        # Update alpha visibility
        self.parent.ids.a.setValue(100)
        self.parent.ids.a.setVisible(value)
        # Update menu display and save setting
        self.menu.showOpacity.setChecked(value)
        self.storage.setValue('showOpacity', value)
        self.storage.sync()
    
    def setColorFormat(self, cformat=None):
        """ Set the format action. """
        log.info(f'setColorFormat({cformat})')
        if isinstance(cformat, str):
            cformat = COLORFORMATS[cformat]
        # Update parent color format
        self.parent.cformat = cformat
        self.parent._updateTextDisplay()
        # Update menu display and save setting
        for action in self.menu.formats.actions():
            checked = cformat.name == action.property('cformat')
            action.setChecked(checked)
        self.storage.setValue('colorFormat', cformat.name)
        self.storage.sync()

    def updateColorFormats(self, color):
        """ Update the color format choices to match current color. """
        for action in self.menu.formats.actions():
            cformat = COLORFORMATS[action.property('cformat')]
            action.setText(color.format(cformat))
