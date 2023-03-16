# -*- coding: utf-8 -*-
import colorsys
from os.path import dirname, normpath
from colorpecker import log, utils  # noqa
from qtemplate import QTemplateWidget

RGB, HSV = 'rgb', 'hsv'     # Current slider mode


class ColorPecker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpecker.tmpl')

    def __init__(self, rgb=None, hsv=None, hex=None):
        super(ColorPecker, self).__init__()
        self.rgba = (0,0,0,1.0)             # Current color in RGB
        self.mode = HSV                     # Current slider mode
        self._rgba = None                   # Last displayed rgba value
        self._hsva = None                   # Last displayed hsva value
        if rgb: self.setRGB(rgb)            # RGB (0-255, 0-255, 0-255, {0-1})
        elif hsv: self.setHSV(hsv)          # HSV (0-360, 0-100, 0-100, {0-1})
        elif hex: self.setHex(hex)          # HEX #000000{00}-#FFFFFF{FF}
        else: self.setRGB(self.rgba)        # Set default color

    @property
    def hex(self):
        return self.hexa[:7]
    
    @property
    def hsv(self):
        return self.hsva[:3]
    
    @property
    def rgb(self):
        return self.rgba[:3]
    
    @property
    def hexa(self):
        r,g,b,a = (int(x) for x in self.rgba)
        a = int(round(a * 255))
        return f'#{r:02x}{g:02x}{b:02x}{b:02x}'.upper()
    
    @property
    def hsva(self):
        r,g,b,a = self._rgba
        h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        return (round(h*360), round(s*100), round(v*100), a)

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPecker, self).show()

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
        log.info(f'setHex({hexa})')
        rgba = self.hexa2rgba(hexa)
        self._updateUi(rgba=rgba)
    
    def setOpacity(self, opacity):
        """ Set the opacity from 0-1. """
        rgba = self.rgba[:3] + (1.0,)
        self._updateUi(rgba=rgba)
    
    def _rChanged(self, r):
        _,g,b,a = self._rgba
        self._updateUi(rgba=(r,g,b,a))

    def _gChanged(self, g):
        r,_,b,a = self._rgba
        self._updateUi(rgba=(r,g,b,a))

    def _bChanged(self, b):
        r,g,_,a = self._rgba
        self._updateUi(rgba=(r,g,b,a))

    def _hChanged(self, h):
        _,s,v,a = self._hsva
        self._updateUi(hsva=(h,s,v,a))

    def _sChanged(self, s):
        h,_,v,a = self._hsva
        self._updateUi(hsva=(h,s,v,a))

    def _vChanged(self, v):
        h,s,_,a = self._hsva
        self._updateUi(hsva=(h,s,v,a))

    def _aChanged(self, a):
        h,s,v,_ = self._hsva
        a = round(a / 100, 3)
        self._updateUi(hsva=(h,s,v,a))

    def _updateUi(self, rgba=None, hsva=None):
        if self.mode == RGB:
            self._updateRGB(rgba, hsva)
        if self.mode == HSV:
            self._updateHSV(rgba, hsva)
    
    def _updateRGB(self, rgba=None, hsva=None):
        raise Exception('not implemented yet')
        r,g,b,a = rgba if rgba else self.hsva2rgba(hsva)
        if self._rgba != (r,g,b,a):
            self._rgba = (r,g,b,a)
            self._updateCurrentColor(rgba=(r,g,b,a))
            self._updateRed(rgba=(r,g,b,a))
            self._updateGreen(rgba=(r,g,b,a))
            self._updateBlue(rgba=(r,g,b,a))
            self._updateOpacity(rgba=(r,g,b,a))

    def _updateHSV(self, rgba=None, hsva=None):
        h,s,v,a = hsva if hsva else self.rgba2hsva(rgba)
        if self._hsva != (h,s,v,a):
            self._hsva = (h,s,v,a)
            self._updateSwatch(hsva=(h,s,v,a))
            self._updateHue(hsva=(h,s,v,a))
            self._updateSaturation(hsva=(h,s,v,a))
            self._updateBrightness(hsva=(h,s,v,a))
            self._updateOpacity(hsva=(h,s,v,a))

    def _updateSwatch(self, rgba=None, hsva=None):
        self.rgba = rgba if rgba else self.hsva2rgba(hsva)
        r,g,b,a = self.rgba
        style = f'background-color: rgba({r},{g},{b},{a});'
        self.ids.swatch.setStyleSheet(style)
        self.ids.hex.setText(self.hex)
    
    def _updateHue(self, hsva):
        h,s,v,a = hsva
        self.ids.h.setValue(h)
        gradient = f"""#h QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsva2hex((0.0,s,v,a))},
            stop:0.17 #{self.hsva2hex((61.2,s,v,a))},
            stop:0.33 #{self.hsva2hex((118.8,s,v,a))},
            stop:0.5 #{self.hsva2hex((180.0,s,v,a))},
            stop:0.67 #{self.hsva2hex((241.2,s,v,a))},
            stop:0.83 #{self.hsva2hex((298.8,s,v,a))},
            stop:1 #{self.hsva2hex((360.0,s,v,a))});
        }}"""
        self.ids.h.setStyleSheet(gradient)

    def _updateSaturation(self, hsva):
        h,s,v,a = hsva
        self.ids.s.setValue(s)
        gradient = f"""#s QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsva2hex((h,0,v,a))},
            stop:1 #{self.hsva2hex((h,100,v,a))});
        }}"""
        self.ids.s.setStyleSheet(gradient)

    def _updateBrightness(self, hsva):
        h,s,v,a = hsva
        self.ids.v.setValue(v)
        gradient = f"""#v QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsva2hex((h,s,0,a))},
            stop:1 #{self.hsva2hex((h,s,100,a))});
        }}"""
        self.ids.v.setStyleSheet(gradient)

    def _updateOpacity(self, rgba=None, hsva=None):
        r,g,b,a = rgba if rgba else self.hsva2rgba(hsva)
        self.ids.a.setValue(round(a*100))
        gradient = f"""#a QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.a.setStyleSheet(gradient)
    
    @classmethod
    def hexa2rgba(cls, hexa):
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
    def hsva2hex(cls, hsva):
        """ Convert hsva to hex (without the alpha channel). """
        h,s,v,a = hsva
        _rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = (int(x*255) for x in _rgb)
        return f'{r:02x}{g:02x}{b:02x}'.upper()

    @classmethod
    def hsva2rgba(cls, hsva):
        """ Convert hsva to rgba. """
        h,s,v,a = hsva
        _rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = (round(x*255) for x in _rgb)
        return (r,g,b,a)
    
    @classmethod
    def rgba2hsva(cls, rgba):
        """ Convert rgba to hsva. """
        r,g,b,a = rgba
        h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        h,s,v = (round(h*360), round(s*100), round(v*100))
        return (h,s,v,a)
