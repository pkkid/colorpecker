# -*- coding: utf-8 -*-
import logging
import sys
from os.path import dirname
from PySide6.QtCore import QStandardPaths

APPNAME = 'Color Picker'
ROOT = dirname(dirname(__file__))
STORAGEDIR = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
VERSION = '1.0.0'


# Custom logging formatter
class MyFormatter(logging.Formatter):
    def format(self, record):
        if 'module' in record.__dict__.keys():
            record.module = record.module[:10]
        return super(MyFormatter, self).format(record)


# Logging configuration
log = logging.getLogger(__name__)
logformat = MyFormatter('%(asctime)s %(module)10s:%(lineno)-4s %(levelname)-7s %(message)s')
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logformat)
log.addHandler(streamhandler)
log.setLevel(logging.INFO)


# Add ColorSlider to QTemplate.GLOBALCONTEXT
from .colorslider import ColorSlider  # noqa
from qtemplate import QTemplateWidget  # noqa
QTemplateWidget.globalcontext.update({'ColorSlider': ColorSlider})
