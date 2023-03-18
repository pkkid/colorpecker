# -*- coding: utf-8 -*-
import colorsys
from colorpecker import log, utils  # noqa
from colorpecker.utils import minmax
from os.path import dirname, normpath
from PySide6 import QtCore
from qtemplate import QTemplateWidget

RGB, HSV = 'RGB', 'HSV'  # Current slider mode


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def __init__(self, rgb=None, hsv=None, hex=None):
        super(ColorPicker, self).__init__()
        self.mode = HSV                     # Current slider mode
        self.rgba = (0,0,0,1.0)             # Current color in RGB mode
        self.hsva = (0,0,0,1.0)             # Current color in HSV mode
        self._shiftrgba = None              # rgba value when shift pressed
        self._updating = False                # Ignore other slider changes
        if rgb: self.setRGB(rgb)            # RGB (0-255, 0-255, 0-255, {0-1})
        elif hsv: self.setHSV(hsv)          # HSV (0-360, 0-100, 0-100, {0-1})
        elif hex: self.setHex(hex)          # HEX #000000{00}-#FFFFFF{FF}
        else: self.setRGB(self.rgba)        # Set default color
    
    @property
    def hex(self):
        return self.rgb2hex(self.rgba)[:7]
    
    @property
    def hexa(self):
        return self.rgb2hex(self.rgba)
    
    @property
    def hsv(self):
        return self.hsva[:3]

    @property
    def rgb(self):
        return self.rgba[:3]
    
    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setRGB(self, rgba):
        """ Set the current rgb(a) value. """
        if len(rgba) == 3:
            rgba = rgba + (1.0,)
        self._updateUi(rgba=rgba)

    def setHSV(self, hsva):
        """ Set the current hsv(a) value. """
        if len(hsva) == 3:
            hsva = hsva + (1.0,)
        self._updateUi(hsva=hsva)

    def setHex(self, hexa):
        """ Set the current hex(a) value. """
        rgba = self.hex2rgb(hexa)
        self._updateUi(rgba=rgba)
    
    def setOpacity(self, opacity):
        """ Set the opacity from 0-1. """
        rgba = self.rgba[:3] + (1.0,)
        self._updateUi(rgba=rgba)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftrgba = self.rgba
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftrgba = None
        super().keyReleaseEvent(event)

    def _modeChanged(self, index):
        if self.loading: return
        self.mode = self.ids.mode.itemText(index)
        if self.mode == RGB:
            self.ids.HSV.setVisible(False)
            self.ids.RGB.setVisible(True)
        if self.mode == HSV:
            self.ids.RGB.setVisible(False)
            self.ids.HSV.setVisible(True)
        self._updateUi(rgba=self.rgba)

    def _rChanged(self, r):
        _,g,b,a = self.rgba
        if self._shiftrgba:
            sr,sg,sb = self._shiftrgba[:3]
            pct = round(1-((sr-r)/float(sr)), 3)
            g = utils.minmax(sg*pct, 0, 255)
            b = utils.minmax(sb*pct, 0, 255)
        self._updateUi(rgba=(r,g,b,a))

    def _gChanged(self, g):
        r,_,b,a = self.rgba
        if self._shiftrgba:
            sr,sg,sb = self._shiftrgba[:3]
            pct = round(1-((sg-g)/float(sg)), 3)
            r = utils.minmax(sr*pct, 0, 255)
            b = utils.minmax(sb*pct, 0, 255)
        self._updateUi(rgba=(r,g,b,a))

    def _bChanged(self, b):
        r,g,_,a = self.rgba
        if self._shiftrgba:
            sr,sg,sb = self._shiftrgba[:3]
            pct = round(1-((sb-b)/float(sb)), 3)
            r = utils.minmax(sr*pct, 0, 255)
            g = utils.minmax(sg*pct, 0, 255)
        self._updateUi(rgba=(r,g,b,a))

    def _hChanged(self, h):
        _,s,v,a = self.hsva
        self._updateUi(hsva=(h,s,v,a))

    def _sChanged(self, s):
        h,_,v,a = self.hsva
        self._updateUi(hsva=(h,s,v,a))

    def _vChanged(self, v):
        h,s,_,a = self.hsva
        self._updateUi(hsva=(h,s,v,a))

    def _aChanged(self, a):
        a = round(a / 100, 3)
        if self.mode == RGB:
            r,g,b,_ = self.rgba
            self._updateUi(rgba=(r,g,b,a))
        if self.mode == HSV:
            h,s,v,_ = self.hsva
            self._updateUi(hsva=(h,s,v,a))

    def _updateUi(self, rgba=None, hsva=None):
        if not self._updating:
            self._updating = True
            update = getattr(self, f'_update{self.mode}')
            update(rgba, hsva)
            self._updating = False
    
    def _updateRGB(self, rgba=None, hsva=None):
        self.rgba = rgba if rgba else self.hsv2rgb(hsva)
        # log.debug(f'_updateRGB{self.rgba}')
        self._updateSwatch(rgba=self.rgba)
        self._updateSlider('r', rgba=self.rgba)
        self._updateSlider('g', rgba=self.rgba)
        self._updateSlider('b', rgba=self.rgba)
        self._updateOpacity(rgba=self.rgba)

    def _updateHSV(self, rgba=None, hsva=None):
        self.hsva = hsva if hsva else self.rgb2hsv(rgba)
        # log.debug(f'_updateHSV{self.hsva}')
        self._updateSwatch(hsva=self.hsva)
        self._updateHue(hsva=self.hsva)
        self._updateSlider('s', hsva=self.hsva)
        self._updateSlider('v', hsva=self.hsva)
        self._updateOpacity(hsva=self.hsva)

    def _updateSwatch(self, rgba=None, hsva=None):
        self.rgba = rgba if rgba else self.hsv2rgb(hsva)
        style = f'background-color: rgba{self.rgba};'
        self.ids.swatch.setStyleSheet(style)
        self.ids.hex.setText(self.hex)
    
    def _updateSlider(self, id, rgba=None, hsva=None):
        """ Update the slider id given current rgba or hsva selection. """
        slider = self.ids[id]
        getColor = lambda c,i,v: c[:i]+(v,)+c[i+1:]
        if hsva is not None:
            getColor = lambda c,i,v: self.hsv2rgb(c[:i]+(v,)+c[i+1:])
        c = rgba or hsva
        i = 'rgb'.index(id) if rgba else 'hsv'.index(id)
        slider.setValue(rgba[i] if rgba else hsva[i])
        gradient = f"""#{id} QSlider {{
            background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgb{getColor(c, i, slider.minValue)[:3]},
            stop:1 rgb{getColor(c, i, slider.maxValue)[:3]});
        }}"""
        slider.setStyleSheet(gradient)

    def _updateHue(self, hsva):
        h,s,v,a = hsva
        self.ids.h.setValue(h)
        gradient = f"""#h QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((0.0,s,v,a))},
            stop:0.17 #{self.hsv2hex((61.2,s,v,a))},
            stop:0.33 #{self.hsv2hex((118.8,s,v,a))},
            stop:0.5 #{self.hsv2hex((180.0,s,v,a))},
            stop:0.67 #{self.hsv2hex((241.2,s,v,a))},
            stop:0.83 #{self.hsv2hex((298.8,s,v,a))},
            stop:1 #{self.hsv2hex((360.0,s,v,a))});
        }}"""
        self.ids.h.setStyleSheet(gradient)

    def _updateOpacity(self, rgba=None, hsva=None):
        r,g,b,a = rgba if rgba else self.hsv2rgb(hsva)
        self.ids.a.setValue(round(a*100))
        gradient = f"""#a QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.a.setStyleSheet(gradient)
    
    @classmethod
    def hex2rgb(cls, hexa):
        """ Converts hexa to rgba. """
        hexa = hexa.lstrip('#').upper()
        if len(hexa) <= 2: hexa = f'{hexa}{"0"*(6-len(hexa))}FF'
        if len(hexa) == 3: hexa = f'{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}FF'
        if len(hexa) == 4: hexa = f'{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}{hexa[3]*2}'
        if len(hexa) == 6: hexa = f'{hexa}FF'
        if len(hexa) == 7: hexa = f'{hexa}F'
        try:
            r,g,b = (int(hexa[i:i+2], 16) for i in (0,2,4))
            a = int(hexa[6:8], 16) / 255.0
            return (r,g,b,a)
        except Exception:
            return (0,0,0,1.0)
    
    @classmethod
    def hsv2hex(cls, hsva):
        """ Convert hsva to hex (without the alpha channel). """
        h,s,v,a = hsva
        _rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = (int(x*255) for x in _rgb)
        return f'{r:02x}{g:02x}{b:02x}'.upper()

    @classmethod
    def hsv2rgb(cls, hsva):
        """ Convert hsva to rgba. """
        h,s,v,a = hsva
        _rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = (round(x*255,3) for x in _rgb)
        return (r,g,b,a)
    
    @classmethod
    def rgb2hex(cls, rgba):
        """ Convert rgba to hsva. """
        r,g,b,a = (int(x) for x in rgba)
        a = int(round(a * 255))
        return f'#{r:02x}{g:02x}{b:02x}{b:02x}'.upper()

    @classmethod
    def rgb2hsv(cls, rgba):
        """ Convert rgba to hsva. """
        r,g,b,a = rgba
        h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        h,s,v = (round(h*360,3), round(s*100,3), round(v*100,3))
        return (h,s,v,a)
