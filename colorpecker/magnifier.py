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
          <QWidget id='bsquare'><set mouseTracking='True'/></QWidget>
          <QWidget id='wsquare'><set mouseTracking='True'/></QWidget>
        </QWidget>
      </QWidget>
    """
    colorChanged = QtCore.Signal(QtGui.QColor)      # Called when moving the mouse
    colorSelected = QtCore.Signal(QtGui.QColor)     # Called when selecting a color
    cancelled = QtCore.Signal()                     # Called when cancelling selection

    def __init__(self, size=22, zoom=8):
        super(Magnifier, self).__init__()
        self.size = size                # Size of magnifier before zoom
        self.zoom = zoom                # Amount to magnify
        self.borderWidth = 5            # Magnifier border-width
        self.borderRadius = 20          # Magnifier border-radius
        self._screenshots = None        # Holds desktop screenshots
    
    def show(self):
        """ Initialize the magnifier when first displayed. """
        self._grabScreenshots()
        self._setMagnifierSize()
        self._updateTargets()
        super(Magnifier, self).show()
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
    
    def mouseReleaseEvent(self, event):
        """ Grab the color or cancel. """
        if event.button() == QtCore.Qt.LeftButton:
            pass
        self.close()
    
    def _grabScreenshots(self):
        """ Take a screenshot of all displays. """
        self._screenshots = []
        for screen in QtWidgets.QApplication.screens():
            self._screenshots.append(screen.grabWindow(0))
    
    def _setMagnifierSize(self):
        """ Set the magnifier size based on self.size, and self.borderWidth. """
        magsize = (self.size*self.zoom) + self.borderWidth  # Only add borderWidth once?
        self.ids.magnifier.setFixedSize(magsize, magsize)
    
    def _updateTargets(self):
        """ Move and resize the target squares in the center of the magnifier. """
        bpos = round((self.size * self.zoom) / 2.0)
        self.ids.bsquare.move(bpos, bpos)
        self.ids.bsquare.resize(self.zoom, self.zoom)
        self.ids.wsquare.move(bpos-1, bpos-1)
        self.ids.wsquare.resize(self.zoom+2, self.zoom+2)

    def _updateDisplay(self):
        """ Updates the magnifier display. """
        # Grab the global mouse position
        pos = QtGui.QCursor.pos()
        # Get screenshot for the current display
        for i, screen in enumerate(QtWidgets.QApplication.screens()):
            geometry = screen.geometry()
            if geometry.contains(pos):
                screenshot = self._screenshots[i]
                break
        # Get the portion of the screenshot we care about
        screenx = pos.x() - int(self.size/2)
        screeny = pos.y() - int(self.size/2)
        cropped = screenshot.copy(screenx, screeny, self.size, self.size)
        zoomed = cropped.scaled(cropped.width()*self.zoom, cropped.height()*self.zoom)
        # Set rounded corners on the screenshot
        rounded = QtGui.QPixmap(zoomed.size())
        rounded.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setBrush(QtGui.QBrush(zoomed))
        painter.setPen(QtCore.Qt.NoPen)
        drawrect = rounded.rect().adjusted(self.borderWidth, self.borderWidth, 0,0)
        painter.drawRoundedRect(drawrect, self.borderRadius*0.6, self.borderRadius*0.6)
        painter.end()
        # Set zoomed screenshot as the background
        brush = QtGui.QBrush(rounded)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, brush)
        self.ids.magnifier.setAutoFillBackground(True)
        self.ids.magnifier.setPalette(palette)
        # Move the window to the correct location
        x = pos.x() - round(self.width() / 2.0)
        y = pos.y() - round(self.height() / 2.0)
        self.move(x, y)
        # Get the current color and emit the colorChanged signal
        center = (self.size/2, self.size/2)
        self.colorChanged.emit(cropped.toImage().pixelColor(*center))
        
