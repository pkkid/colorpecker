# -*- coding: utf-8 -*-
import colorsys
from os.path import dirname, normpath
from colorpicker import log, utils  # noqa
from qtemplate import QTemplateWidget


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def __init__(self, *args, **kwargs):
        super(ColorPicker, self).__init__()
        self.rgba = (255,0,0,100)                           # Current color in RGB
        self.mode = 'hsva'                                  # Current slider mode
        if 'rgb' in kwargs: self.setRGB(kwargs['rgb'])      # RGB (0-255, 0-255, 0-255)
        elif 'hsv' in kwargs: self.setHSV(kwargs['hsv'])    # HSV (0-360, 0-100, 0-100)
        elif 'hex' in kwargs: self.setHex(kwargs['hex'])    # HEX (00-FF, 00-FF, 00-FF)
        else: self.setRGB(self.rgba)                        # Default to Black

    @property
    def hex(self):
        r,g,b,a = (int(x) for x in self.rgba)
        return f'#{r:02x}{g:02x}{b:02x}'.upper()
    
    @property
    def hsv(self):
        r,g,b = self.rgb
        h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        return (round(h*360,3), round(s*100,3), round(v*100,3))

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setRGB(self, rgba):
        if len(rgba) == 3:
            rgba = tuple(list(rgba).append(100))
        self._updateUi(rgba=rgba)

    def setHSV(self, hsva):
        if len(hsva) == 3:
            hsva = tuple(list(hsva).append(100))
        self._updateUi(hsva=hsva)

    def setHex(self, hex):
        rgba = self.hex2rgb(hex)
        self._updateUi(rgba=rgba)

    def hex2rgb(self, hex):
        hex = hex.lstrip('#')
        if len(hex) == 3: hex = f'{hex[0]*2}{hex[1]*2}{hex[2]*2}'
        if len(hex) < 6: hex += '0'*(6-len(hex))
        if len(hex) > 6: hex = hex[0:6]
        r,g,b = (int(hex[i:i+2], 16) for i in (0,2,4))
        return (r,g,b,100)
    
    def hsv2hex(self, hsva):
        h,s,v,a = hsva
        r,g,b = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = tuple(int(min(max(x*255,0),255)) for x in (r,g,b))
        return f'{r:02x}{g:02x}{b:02x}'.upper()

    def hsv2rgb(self, hsva):
        h,s,v,a = hsva
        r,g,b = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = (round(min(max(x*255,0),255),3) for x in (r,g,b))
        return (r,g,b,a)
    
    def rgb2hsv(self, rgba):
        r,g,b,a = rgba
        h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        h,s,v = (round(h*360,3), round(s*100,3), round(v*100,3))
        return (h,s,v,a)
    
    def redChanged(self, r):
        self.rgb = (r, self.rgb[1], self.rgb[2])

    def greenChanged(self, g):
        self.rgb = (self.rgb[0], g, self.rgb[2])

    def blueChanged(self, b):
        self.rgb = (self.rgb[0], self.rgb[1], b)

    def hueChanged(self, h):
        s = self.ids.saturation.value
        v = self.ids.brightness.value
        a = round(self.ids.opacity.value / 100, 2)
        self._updateUi(hsva=(h,s,v,a), skip='h')

    def saturationChanged(self, s):
        h = self.ids.hue.value
        v = self.ids.brightness.value
        a = round(self.ids.opacity.value / 100, 2)
        self._updateUi(hsva=(h,s,v,a), skip='s')

    def brightnessChanged(self, v):
        h = self.ids.hue.value
        s = self.ids.saturation.value
        a = round((self.ids.opacity.value or 0) / 100, 2)
        self._updateUi(hsva=(h,s,v,a), skip='v')

    def opacityChanged(self, a):
        h = self.ids.hue.value
        s = self.ids.saturation.value
        v = self.ids.brightness.value
        a = round(a / 100, 2)
        self._updateUi(hsva=(h,s,v,a), skip='a')

    def _updateUi(self, rgba=None, hsva=None, skip=None):
        if self.mode == 'hsva':
            h,s,v,a = hsva if hsva else self.rgb2hsv(rgba)
            self._updateColor(hsva=(h,s,v,a))
            if skip != 'h': self._updateHueSlider(hsva=(h,s,v,a))
            if skip != 's': self._updateSaturationSlider(hsva=(h,s,v,a))
            if skip != 'v': self._updateBrightnessSlider(hsva=(h,s,v,a))
            if skip != 'a': self._updateOpacitySlider(hsva=(h,s,v,a))
            if skip is None:
                print('SET')
                self.ids.hue.setValue(h)
                self.ids.saturation.setValue(s)
                self.ids.brightness.setValue(v)
                self.ids.opacity.setValue(a)
    
    def _updateColor(self, rgba=None, hsva=None):
        self.rgba = rgba if rgba else self.hsv2rgb(hsva)
        r,g,b,a = self.rgba
        style = f'background-color: rgba({r},{g},{b},{a});'
        self.ids.currentcolor.setStyleSheet(style)
        self.ids.hex.setText(self.hex)
    
    def _updateHueSlider(self, hsva):
        h,s,v,a = hsva
        gradient = f"""#hue QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((0.0,s,v,a))},
            stop:0.17 #{self.hsv2hex((61.2,s,v,a))},
            stop:0.33 #{self.hsv2hex((118.8,s,v,a))},
            stop:0.5 #{self.hsv2hex((180.0,s,v,a))},
            stop:0.67 #{self.hsv2hex((241.2,s,v,a))},
            stop:0.83 #{self.hsv2hex((298.8,s,v,a))},
            stop:1 #{self.hsv2hex((360.0,s,v,a))});
        }}"""
        self.ids.hue.setStyleSheet(gradient)

    def _updateSaturationSlider(self, hsva):
        h,s,v,a = hsva
        gradient = f"""#saturation QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((h,0,v,a))},
            stop:1 #{self.hsv2hex((h,100,v,a))});
        }}"""
        self.ids.saturation.setStyleSheet(gradient)

    def _updateBrightnessSlider(self, hsva):
        h,s,v,a = hsva
        gradient = f"""#brightness QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((h,s,0,a))},
            stop:1 #{self.hsv2hex((h,s,100,a))});
        }}"""
        self.ids.brightness.setStyleSheet(gradient)

    def _updateOpacitySlider(self, rgba=None, hsva=None):
        r,g,b,a = rgba if rgba else self.hsv2rgb(hsva)
        gradient = f"""#opacity QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.opacity.setStyleSheet(gradient)
