# -*- coding: utf-8 -*-
from colorpecker import log
from os.path import dirname
from PySide6 import QtCore, QtGui, QtWidgets
from qtemplate import QTemplateWidget


class Magnifier(QTemplateWidget):
    TMPLSTR = f"""
      <QWidget id='magnifierwrap' layout='QVBoxLayout()' padding='0'>
        <set mouseTracking='True'/>
        <set windowFlags='Qt.WindowStaysOnTopHint'/>
        <StyleSheet args='{dirname(__file__)}/resources/colorpicker.sass'/>
        <Set attribute='Qt.WA_TranslucentBackground'/>
        <Set windowFlags='Qt.Dialog | Qt.FramelessWindowHint'/>
        <QWidget id='magnifier'>
          <DropShadow args='(0,5,20,128)'/>
          <set mouseTracking='True'/>
          <set cursor='Qt.BlankCursor'/>
          <QWidget id='square'>
            <set mouseTracking='True'/>
          </QWidget>
        </QWidget>
      </QWidget>
    """

    def __init__(self):
        super(Magnifier, self).__init__()
        self._screenshots = None
    
    def show(self):
        """ Initialize the magnifier when first displayed. """
        super(Magnifier, self).show()
        # Get a screenshot of all displays
        self._screenshots = []
        for screen in QtWidgets.QApplication.screens():
            self._screenshots.append(screen.grabWindow(0))
        # Display the magnifier
        self.ids.square.move(100,100)
        self._updateDisplay()
    
    def keyPressEvent(self, event):
        """ When shift is pressed, we save the color to help with calculating
            a full brightness color change. When ctrl+v is pressed, we read the
            clipboard and attempt to load the specified color from text.
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
    
    def mouseMoveEvent(self, event):
        # Take a screenshot of what's under the QWidget
        self._updateDisplay()
    
    def _updateDisplay(self):
        pos = QtGui.QCursor.pos()

        # Get screenshot for the current display
        for i, screen in enumerate(QtWidgets.QApplication.screens()):
            geometry = screen.geometry()
            if geometry.contains(pos):
                screenshot = self._screenshots[i]
                break
        
        # Get the portion of the screenshot we care about
        screenshot = screenshot.copy(pos.x()-20, pos.y()-20, 42, 42)
        screenshot = screenshot.scaled(screenshot.width()*5, screenshot.height()*5)

        # Set rounded corners on the screenshot
        rounded = QtGui.QPixmap(screenshot.size())
        rounded.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setBrush(QtGui.QBrush(screenshot))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rounded.rect(), 23, 23)
        painter.end()

        # Set zoomed screenshot as the background
        brush = QtGui.QBrush(rounded)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, brush)
        self.ids.magnifier.setAutoFillBackground(True)
        self.ids.magnifier.setPalette(palette)

        # Move the window to the correct location
        x = pos.x() - round(self.width()/2.0)
        y = pos.y() - round(self.height()/2.0)
        self.move(x, y)
        
