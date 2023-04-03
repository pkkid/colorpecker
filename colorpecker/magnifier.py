# -*- coding: utf-8 -*-
from colorpecker import log  # noqa
from os.path import dirname
from PySide6 import QtCore, QtGui, QtWidgets
from qtemplate import QTemplateWidget


class Magnifier(QTemplateWidget):
    TMPLSTR = f"""
      <QWidget id='magnifierwrap' layout='QVBoxLayout()' padding='0'>
        <set windowFlags='Qt.WindowStaysOnTopHint'/>
        <StyleSheet args='{dirname(__file__)}/resources/colorpicker.sass'/>
        <Set attribute='Qt.WA_TranslucentBackground'/>
        <Set windowFlags='Qt.Dialog | Qt.FramelessWindowHint'/>
        <QWidget id='magnifier'>
          <DropShadow args='(0,5,20,128)'/>
          <set cursor='Qt.BlankCursor'/>
          <QWidget id='bsquare'/>
          <QWidget id='wsquare'/>
        </QWidget>
      </QWidget>
    """
    colorChanged = QtCore.Signal(QtGui.QColor)      # Called when moving the mouse
    colorSelected = QtCore.Signal(QtGui.QColor)     # Called when selecting a color
    cancelled = QtCore.Signal()                     # Called when cancelling selection

    def __init__(self, size=21, zoom=8, border=5, radius=20, parent=None):
        super(Magnifier, self).__init__(parent=parent)
        self.size = size                            # Size of magnifier before zoom
        self.zoom = zoom                            # Amount to magnify
        self.border = border                        # Magnifier border-width
        self.radius = radius                        # Magnifier border-radius
        self.qcolor = None                          # Current qcolor
        self._zsize = size*zoom                     # Size of zoomed in screenshot
        self._fsize = self._zsize+self.border*2     # Fill size of magnifier
        self._screenshots = None                    # Holds desktop screenshots
        self._timer = None                          # QTimer used to update the data
        self._lastpos = None                        # Last position we updated
        self._fadein = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self._fadeout = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.setWindowOpacity(0.0)
    
    def show(self):
        """ Initialize the magnifier when first displayed. """
        self._grabScreenshots()
        self._setMagnifierSize()
        self._updateTargets()
        super(Magnifier, self).show()
        self._startTrackingTimer()
        self._updateDisplay()
    
    def showEvent(self, event):
        self._fadein.setDuration(200)
        self._fadein.setStartValue(0.0)
        self._fadein.setEndValue(1.0)
        self._fadein.start()
    
    def close(self):
        self._timer.stop()
        self._fadeout.setDuration(200)
        self._fadeout.setStartValue(1.0)
        self._fadeout.setEndValue(0.0)
        self._fadeout.finished.connect(super(Magnifier, self).close)
        self._fadeout.start()
    
    def _startTrackingTimer(self):
        """ Start the update timer. """
        if self._timer is None:
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self._updateDisplay)
        log.info('Tracking mouse position..')
        self._timer.start(15)  # 60 fps
    
    def keyPressEvent(self, event):
        """ When shift is pressed, we save the color to help with calculating
            a full brightness color change. When ctrl+v is pressed, we read the
            clipboard and attempt to load the specified color from text.
        """
        pos = QtGui.QCursor.pos()
        match event.key():
            case QtCore.Qt.Key_Left:
                QtGui.QCursor.setPos(pos.x()-1, pos.y())
            case QtCore.Qt.Key_Right:
                QtGui.QCursor.setPos(pos.x()+1, pos.y())
            case QtCore.Qt.Key_Up:
                QtGui.QCursor.setPos(pos.x(), pos.y()-1)
            case QtCore.Qt.Key_Down:
                QtGui.QCursor.setPos(pos.x(), pos.y()+1)
            case QtCore.Qt.Key_Return:
                self.colorChanged.emit(self.qcolor)
                self.close()
            case QtCore.Qt.Key_Escape:
                self.cancelled.emit()
                self.close()
    
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
        self.ids.magnifier.setFixedSize(self._fsize, self._fsize)
    
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
        # Exit early is not changed
        gpos = QtGui.QCursor.pos()
        if gpos == self._lastpos:
            return
        self._lastpos = gpos
        # Get screenshot for the current display
        for i, screen in enumerate(QtWidgets.QApplication.screens()):
            geometry = screen.geometry()
            if geometry.contains(gpos):
                spos = gpos - screen.geometry().topLeft()
                screenshot = self._screenshots[i]
                break
        # Get the portion of the screenshot we care about
        screenx = spos.x() - int(self.size/2)
        screeny = spos.y() - int(self.size/2)
        cropped = screenshot.copy(screenx, screeny, self.size, self.size)
        zoomed = cropped.scaled(self.size*self.zoom, self.size*self.zoom)
        # Crop zoomed pixmap to have rounded corners
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.border, self.border, self._zsize, self._zsize)
        path.addRoundedRect(rect, self.radius*0.6, self.radius*0.6)
        rounded = QtGui.QPixmap(self._fsize, self._fsize)
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
        x = gpos.x() - round(self.width()/2.0)
        y = gpos.y() - round(self.height()/2.0)
        self.move(x, y)
        # Get the current color and emit the colorChanged signal
        center = (self.size/2, self.size/2)
        self.qcolor = cropped.toImage().pixelColor(*center)
        self.colorChanged.emit(self.qcolor)
