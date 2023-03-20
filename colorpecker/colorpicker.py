# -*- coding: utf-8 -*-
from colorpecker import log, utils  # noqa
from colorpecker.utils import HEX, HSV, RGB
from os.path import dirname, normpath
from PySide6 import QtCore, QtGui
from qtemplate import QTemplateWidget


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def __init__(self, color=None):
        super(ColorPicker, self).__init__()
        self.mode = HSV                         # Current slider mode
        self.color = (0,100,100,1)              # Current color in self.mode format
        self._shiftColor = None                 # color value when shift pressed
        self._updating = False                  # Ignore other slider changes
        if color: self.setColor(color)          # Set the specfied color
        else: self._updateUi(self.color)        # Update UI with default color

    hex = property(lambda self: self.hexa[:7])
    hexa = property(lambda self: utils.convert(self.color, self.mode, HEX))
    hsv = property(lambda self: self.hsva[:3])
    hsva = property(lambda self: utils.convert(self.color, self.mode, HSV))
    rgb = property(lambda self: self.rgba[:3])
    rgba = property(lambda self: utils.convert(self.color, self.mode, RGB))
    opacity = property(lambda self: self.color[-1])
    
    # setHex = lambda self, hex: self.setHexa(hex)
    # setHsv = lambda self, hsv: self.setHsva(hsv)
    # setRgb = lambda self, rgb: self.setRgba(rgb)

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setColor(self, text):
        """ Try really hard to read the text format and set the color. """
        try:
            mode, color = utils.text2color(text)
            color = utils.convert(color, mode, self.mode)
            self._updateUi(color)
        except Exception:
            raise Exception(f'Unable to parse color {text}')

    def setOpacity(self, a):
        """ Set the opacity from 0-1. """
        self._updateUi(self.color[:-1] + (a,))
    
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            clipboard = QtGui.QClipboard()
            mimedata = clipboard.mimeData()
            if mimedata.hasText():
                self.setColor(mimedata.text())
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftColor = self.color
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftColor = None
        super().keyReleaseEvent(event)

    def _modeChanged(self, index):
        if self.loading: return
        # Update sef.color format and self.mode
        mode = self.ids.mode.itemText(index).lower()
        self.color = utils.convert(self.color, self.mode, mode)
        self.mode = mode
        # Display the correct sliders
        if self.mode == RGB:
            self.ids.hsv.setVisible(False)
            self.ids.rgb.setVisible(True)
        if self.mode == HSV:
            self.ids.rgb.setVisible(False)
            self.ids.hsv.setVisible(True)
        self._updateUi(self.color)

    def _rgbChanged(self, value):
        id = self.sender().objectName().lower()
        index = RGB.index(id)
        color = list(self.color)
        color[index] = value
        if self._shiftColor:
            scolor = self._shiftColor
            svalue = scolor[index]
            if svalue != 0:
                pct = round(1-((svalue-value)/float(svalue)), 3)
                color = [min(max(sc*pct, 0), 255) for sc in scolor[:-1]] + [color[-1]]
                color[index] = value
        self._updateUi(tuple(color))

    def _hsvChanged(self, value):
        id = self.sender().objectName().lower()
        index = HSV.index(id)
        color = list(self.color)
        color[index] = value
        self._updateUi(tuple(color))

    def _aChanged(self, a):
        a = round(a / 100, 3)
        if self.mode in (RGB, HSV):
            self._updateUi(self.color[:-1]+(a,))

    def _updateUi(self, color):
        if not self._updating:
            self._updating = True
            funcname = f'_update{self.mode.title()}'
            getattr(self, funcname)(color)
            self._updating = False
    
    def _updateRgb(self, color):
        if self.mode != RGB:  # TODO: Can this be deleted?
            convertor = f'{self.mode.lower()}2rgb'
            color = getattr(self, convertor)(color)
        self._updateSwatch(color)
        self._updateSlider('r', color)
        self._updateSlider('g', color)
        self._updateSlider('b', color)
        self._updateOpacity(color)
    
    def _updateHsv(self, color):
        if self.mode != HSV:  # TODO: Can this be deleted?
            convertor = f'{self.mode.lower()}2hsv'
            color = getattr(self, convertor)(color)
        self._updateSwatch(color)
        self._updateHue(color)
        self._updateSlider('s', color)
        self._updateSlider('v', color)
        self._updateOpacity(color)

    def _updateSwatch(self, color):
        self.color = color
        self.ids.swatch.setStyleSheet(f'background-color: rgba{self.rgba};')
        if self.opacity == 1: self.ids.hex.setText(self.hex)
        else: self.ids.hex.setText(self.hexa)
    
    def _updateSlider(self, id, color):
        """ Update the slider id given current rgba or hsva selection. """
        slider = self.ids[id]
        getColor = lambda c,i,v: c[:i]+(v,)+c[i+1:]
        if self.mode != RGB:
            convert = getattr(utils, f'{self.mode.lower()}a2rgba')
            getColor = lambda c,i,v: convert(c[:i]+(v,)+c[i+1:])
        i = self.mode.index(id.lower())
        slider.setValue(color[i])
        gradient = f"""#{id} QSlider {{
            background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgb{getColor(color, i, slider.minValue)[:3]},
            stop:1 rgb{getColor(color, i, slider.maxValue)[:3]});
        }}"""
        slider.setStyleSheet(gradient)

    def _updateHue(self, color):
        h,s,v,a = color
        self.ids.h.setValue(h)
        gradient = f"""#h QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 {utils.convert((0.0,s,v,a), self.mode, HEX)[:7]},
            stop:0.17 {utils.convert((61.2,s,v,a), self.mode, HEX)[:7]},
            stop:0.33 {utils.convert((118.8,s,v,a), self.mode, HEX)[:7]},
            stop:0.5 {utils.convert((180.0,s,v,a), self.mode, HEX)[:7]},
            stop:0.67 {utils.convert((241.2,s,v,a), self.mode, HEX)[:7]},
            stop:0.83 {utils.convert((298.8,s,v,a), self.mode, HEX)[:7]},
            stop:1 {utils.convert((360.0,s,v,a), self.mode, HEX)[:7]});
        }}"""
        self.ids.h.setStyleSheet(gradient)
    
    def _updateOpacity(self, color):
        r,g,b,a = utils.convert(color, self.mode, RGB)
        self.ids.a.setValue(round(a*100))
        gradient = f"""#a QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.a.setStyleSheet(gradient)
