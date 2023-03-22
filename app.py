#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
from argparse import ArgumentParser
from colorpecker import APPNAME, STORAGEDIR, log, testing
from colorpecker.colorpicker import ColorPicker
from inkwell import inkwell
from os.path import normpath
from PySide6 import QtWidgets
from PySide6.QtCore import QSettings
from qtemplate import QTemplateWidget


class Application(QtWidgets.QApplication):

    def __init__(self, opts):
        super(Application, self).__init__()
        inkwell.addApplicationFonts()                   # Add Inkwell fonts
        inkwell.applyStyleSheet(self)                   # Apply Inkwell styles
        self.opts = opts                                # Command line options
        self.storage = self._initStorage()              # Setup settings storage
        self.colorpecker = ColorPicker()                # Main window
        self.colorpecker.show()                         # Show the main window
        if opts.test: testing.initTests()               # Init tests if requested

    def _initStorage(self):
        """ Create the storage object to get and save settings. """
        appname = APPNAME.lower().replace(' ','')
        filepath = f'{STORAGEDIR}/{APPNAME}/{appname}.ini'
        self.storage = QSettings(filepath, QSettings.IniFormat)
        log.info(f'Settings: {normpath(self.storage.fileName())}')
        return self.storage

    @classmethod
    def start(cls, opts):
        """ Start the application. """
        QtWidgets.QApplication.setStyle('windows')
        cls(opts).exec()
        log.info('Quitting.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--test', action='store_true', help='Run color tests')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--verbose', action='store_true', help='Even more verbose logging')
    parser.add_argument('--outline', action='store_true', help='Add outline to QWidgets')
    opts = parser.parse_args()
    if opts.debug: log.setLevel('DEBUG')
    if opts.verbose: QTemplateWidget.verbose = True
    app = Application.start(opts)
