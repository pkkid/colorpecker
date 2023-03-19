# -*- coding: utf-8 -*-
import re
from colorpecker import log, utils  # noqa
from os.path import dirname, normpath
from PySide6 import QtCore, QtGui
from qtemplate import QTemplateWidget

RGB,HSV,HEX = 'RGB','HSV','HEX'
REGEX_DEG = r'\s*(\d+)(?:\.\d+)?°?\s*'
REGEX_NUM = r'\s*(\d+(?:\.\d+)?|%)(?:\s*%)?\s*'
REGEX_H = r'[a-fA-F\d]'
REGEX_RGB = re.compile(rf'rgba?\({REGEX_NUM},{REGEX_NUM},{REGEX_NUM}(?:,{REGEX_NUM})?\)')
REGEX_HSV = re.compile(rf'hsva?\({REGEX_DEG},{REGEX_NUM},{REGEX_NUM}(?:,{REGEX_NUM})?\)')
REGEX_HEX = re.compile(rf'(?:#|0x)?({REGEX_H}{{8}}|{REGEX_H}{{6}}|{REGEX_H}{{3,8}})')


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def __init__(self, colorStr=None):
        super(ColorPicker, self).__init__()
        self.mode = HSV                         # Current slider mode
        self.color = (0,100,100,1)              # Current color in self.mode format
        self._shiftcolor = None                 # color value when shift pressed
        self._updating = False                  # Ignore other slider changes
        if colorStr: self.setColor(colorStr)    # Set the specfied color
        else: self._updateUi(self.color)        # Update UI with default color

    hex = property(lambda self: self.hexa[:7])
    hexa = property(lambda self: utils.convert(self.color, self.mode, HEX))
    hsv = property(lambda self: self.hsva[:3])
    hsva = property(lambda self: utils.convert(self.color, self.mode, HSV))
    rgb = property(lambda self: self.rgba[:3])
    rgba = property(lambda self: utils.convert(self.color, self.mode, RGB))
    
    setHex = lambda self, hex: self.setHexa(hex+'FF')
    setHexa = lambda self, hexa: self._updateUi(utils.convert(hexa, HEX, self.mode))
    setHsv = lambda self, hsv: self.setHsva(hsv+(1,))
    setHsva = lambda self, hsva: self._updateUi(utils.convert(hsva, HSV, self.mode))
    setRgb = lambda self, rgb: self.setRgba(rgb+(1,))
    setRgba = lambda self, rgba: self._updateUi(utils.convert(rgba, RGB, self.mode))

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setColor(self, text):
        """ Try really hard to read the text format and set the color. """
        if matches := re.match(REGEX_HEX, text):
            self.setHex(matches[0])
        elif matches := re.match(REGEX_HSV, text):
            self.setHex(matches[0])
        elif matches := re.match(REGEX_RGB, text):
            self.setRGB(matches[0])
    
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
            self._shiftcolor = self.color
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftcolor = None
        super().keyReleaseEvent(event)

    def _modeChanged(self, index):
        if self.loading: return
        # Update sef.color format and self.mode
        mode = self.ids.mode.itemText(index)
        self.color = utils.convert(self.color, self.mode, mode)
        self.mode = mode
        # Display the correct sliders
        if self.mode == RGB:
            self.ids.HSV.setVisible(False)
            self.ids.RGB.setVisible(True)
        if self.mode == HSV:
            self.ids.RGB.setVisible(False)
            self.ids.HSV.setVisible(True)
        self._updateUi(self.color)

    def _rgbChanged(self, value):
        i = 'rgb'.index(self.sender().objectName())
        rgb = self.color[:i] + (value,) + self.color[i+1:-1]
        srgb = self._shiftcolor
        if srgb and srgb[i] != 0:
            pct = round(1-((srgb[i]-rgb[i])/float(srgb[i])), 3)
            print(pct)
            rgb = tuple(min(max(x*pct, 0), 255) for x in rgb)
        self._updateUi(rgb + (self.color[-1],))

    def _rChanged(self, r):
        _,g,b,a = self.color
        if self._shiftcolor:
            sr,sg,sb = self._shiftcolor[:3]
            if sr != 0:
                pct = round(1-((sr-r)/float(sr)), 3)
                g = min(max(sg*pct, 0), 255)
                b = min(max(sb*pct, 0), 255)
        self._updateUi((r,g,b,a))

    def _gChanged(self, g):
        r,_,b,a = self.color
        if self._shiftcolor:
            sr,sg,sb = self._shiftcolor[:3]
            if sg != 0:
                pct = round(1-((sg-g)/float(sg)), 3)
                r = min(max(sr*pct, 0), 255)
                b = min(max(sb*pct, 0), 255)
        self._updateUi((r,g,b,a))

    def _bChanged(self, b):
        r,g,_,a = self.color
        if self._shiftcolor:
            sr,sg,sb = self._shiftcolor[:3]
            if sb != 0:
                pct = round(1-((sb-b)/float(sb)), 3)
                r = min(max(sr*pct, 0), 255)
                g = min(max(sg*pct, 0), 255)
        self._updateUi((r,g,b,a))

    def _hChanged(self, h):
        print(self.sender().objectName())
        _,s,v,a = self.color
        self._updateUi((h,s,v,a))

    def _sChanged(self, s):
        h,_,v,a = self.color
        self._updateUi((h,s,v,a))

    def _vChanged(self, v):
        h,s,_,a = self.color
        self._updateUi((h,s,v,a))

    def _aChanged(self, a):
        a = round(a / 100, 3)
        if self.mode in (RGB, HSV):
            self._updateUi(self.color[:3]+(a,))

    def _updateUi(self, color):
        if not self._updating:
            self._updating = True
            getattr(self, f'_update{self.mode}')(color)
            self._updating = False
    
    def _updateRGB(self, color):
        if self.mode != RGB:  # TODO: Can this be deleted?
            convertor = f'{self.mode.lower()}2rgb'
            color = getattr(self, convertor)(color)
        self._updateSwatch(color)
        self._updateSlider('r', color)
        self._updateSlider('g', color)
        self._updateSlider('b', color)
        self._updateOpacity(color)
    
    def _updateHSV(self, color):
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
        self.ids.hex.setText(self.hexa)
    
    def _updateSlider(self, id, color):
        """ Update the slider id given current rgba or hsva selection. """
        slider = self.ids[id]
        getColor = lambda c,i,v: c[:i]+(v,)+c[i+1:]
        if self.mode != RGB:
            convertor = getattr(utils, f'{self.mode.lower()}a2rgba')
            getColor = lambda c,i,v: convertor(c[:i]+(v,)+c[i+1:])
        i = self.mode.lower().index(id.lower())
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
