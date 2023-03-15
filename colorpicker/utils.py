# -*- coding: utf-8 -*-
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication


def centerWindow(qobj):
    """ Move the specified widget to the center of the screen. """
    geometry = qobj.frameGeometry()
    screen = QApplication.screenAt(QtGui.QCursor.pos())
    centerpos = screen.geometry().center()
    geometry.moveCenter(centerpos)
    qobj.move(geometry.topLeft())
