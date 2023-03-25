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

    def __init__(self, size=21, zoom=8, border=5, radius=20):
        super(Magnifier, self).__init__()
        self.size = size                            # Size of magnifier before zoom
        self.zoom = zoom                            # Amount to magnify
        self.border = border                        # Magnifier border-width
        self.radius = radius                        # Magnifier border-radius
        self.qcolor = None                          # Current qcolor
        self.zsize = size*zoom                      # Size of zoomed in screenshot
        self.fsize = self.zsize+self.border*2       # Fill size of magnifier
        self._screenshots = None                    # Holds desktop screenshots
    
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
            self.cancelled.emit()
            self.close()
    
    def mouseMoveEvent(self, event):
        # Take a screenshot of what's under the QWidget
        self._updateDisplay()
    
    def mouseReleaseEvent(self, event):
        """ Grab the color or cancel. """
        if event.button() == QtCore.Qt.LeftButton:
            self.colorChanged.emit(self.qcolor)
        elif event.button() == QtCore.Qt.RightButton:
            self.cancelled.emit()
        self.close()
    
    def _grabScreenshots(self):
        """ Take a screenshot of all displays. """
        self._screenshots = []
        for screen in QtWidgets.QApplication.screens():
            self._screenshots.append(screen.grabWindow(0))
    
    def _setMagnifierSize(self):
        """ Set the magnifier size based on self.size, and self.width. """
        self.ids.magnifier.setFixedSize(self.fsize, self.fsize)
    
    def _updateTargets(self):
        """ Move and resize the target squares in the center of the magnifier. """
        bpos = round((self.size*self.zoom)/2.0)
        self.ids.bsquare.move(bpos+1, bpos+1)
        self.ids.bsquare.resize(self.zoom, self.zoom)
        self.ids.wsquare.move(bpos, bpos)
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
        # Crop zoomed pixmap to have rounded corners
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.border, self.border, self.zsize, self.zsize)
        path.addRoundedRect(rect, self.radius*0.6, self.radius*0.6)
        rounded = QtGui.QPixmap(self.fsize, self.fsize)
        rounded.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(rounded)
        painter.setClipPath(path)
        painter.drawPixmap(self.border, self.border, zoomed)
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
        # Get the current color and emit the colorChanged signal
        center = (self.size/2, self.size/2)
        self.qcolor = cropped.toImage().pixelColor(*center)
        self.colorChanged.emit(self.qcolor)
        
