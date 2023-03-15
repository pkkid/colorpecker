# -*- coding: utf-8 -*-
import colorsys
from os.path import dirname, normpath
from colorpicker import log, utils  # noqa
from qtemplate import QTemplateWidget


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def __init__(self, *args, **kwargs):
        super(ColorPicker, self).__init__()
        self.rgb = (0,0,0)                                  # Current color in RGB
        self.a = 100                                        # Current opacity (0-100)
        if 'rgb' in kwargs: self.setRGB(kwargs['rgb'])      # RGB (0-255, 0-255, 0-255)
        elif 'hsv' in kwargs: self.setHSV(kwargs['hsv'])    # HSV (0-360, 0-100, 0-100)
        elif 'hex' in kwargs: self.setHex(kwargs['hex'])    # HEX (00-FF, 00-FF, 00-FF)
        else: self.setRGB(self.rgb)                         # Default to Black

    @property
    def hex(self):
        r,g,b = (int(x) for x in self.rgb)
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

    def setRGB(self, rgb, opacity=100):
        self.rgb = rgb
        self.opacity = opacity

    def setHSV(self, hsv, opacity=100):
        self.rgb = self.hsv2rgb(hsv)
        self.opacity = opacity

    def setHex(self, hex, opacity=100):
        self.rgb = self.hex2rgb(hex)
        self.opacity = opacity

    def hex2rgb(self, hex):
        hex = hex.lstrip('#')
        if len(hex) == 3: hex = f'{hex[0]*2}{hex[1]*2}{hex[2]*2}'
        if len(hex) < 6: hex += '0'*(6-len(hex))
        if len(hex) > 6: hex = hex[0:6]
        return tuple(int(hex[i:i+2], 16) for i in (0,2,4))
    
    def hsv2hex(self, hsv):
        h,s,v = hsv
        r,g,b = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        r,g,b = tuple(int(min(max(x*255,0),255)) for x in (r,g,b))
        return f'{r:02x}{g:02x}{b:02x}'.upper()

    def hsv2rgb(self, h, s, v):
        rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
        return tuple(round(min(max(x*255,0),255),3) for x in rgb)
    
    def redChanged(self, r):
        self.rgb = (r, self.rgb[1], self.rgb[2])

    def greenChanged(self, g):
        self.rgb = (self.rgb[0], g, self.rgb[2])

    def blueChanged(self, b):
        self.rgb = (self.rgb[0], self.rgb[1], b)

    def hueChanged(self, h):
        s = self.ids.saturation.value or 0
        v = self.ids.brightness.value or 0
        self._updateColor(hsv=(h,s,v))
        self._updateSaturationSlider(hsv=(h,s,v))
        self._updateBrightnessSlider(hsv=(h,s,v))
        self._updateOpacitySlider(hsv=(h,s,v))

    def saturationChanged(self, s):
        h = self.ids.hue.value or 0
        v = self.ids.brightness.value or 0
        self._updateColor(hsv=(h,s,v))
        self._updateHueSlider(hsv=(h,s,v))
        self._updateBrightnessSlider(hsv=(h,s,v))
        self._updateOpacitySlider(hsv=(h,s,v))

    def brightnessChanged(self, v):
        h = self.ids.hue.value or 0
        s = self.ids.saturation.value or 0
        self._updateColor(hsv=(h,s,v))
        self._updateHueSlider(hsv=(h,s,v))
        self._updateSaturationSlider(hsv=(h,s,v))
        self._updateOpacitySlider(hsv=(h,s,v))

    def opacityChanged(self, opacity):
        self.opacity = round(opacity/100.0, 2)
        h = self.ids.hue.value or 0
        s = self.ids.saturation.value or 0
        v = self.ids.brightness.value or 0
        self._updateHueSlider(hsv=(h,s,v))
        self._updateSaturationSlider(hsv=(h,s,v))
        self._updateBrightnessSlider(hsv=(h,s,v))
        self._updateColor(hsv=(h,s,v), opacity=opacity)

    def _updateColor(self, rgb=None, hsv=None, opacity=None):
        self.rgb = rgb if rgb else self.hsv2rgb(*hsv)
        r,g,b = self.rgb
        style = f'background-color: rgba({r},{g},{b},{self.opacity});'
        self.ids.currentcolor.setStyleSheet(style)
        self.ids.hex.setText(self.hex)
    
    def _updateHueSlider(self, hsv):
        h,s,v = hsv
        gradient = f"""#hue QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((0.0,s,v))},
            stop:0.17 #{self.hsv2hex((61.2,s,v))},
            stop:0.33 #{self.hsv2hex((118.8,s,v))},
            stop:0.5 #{self.hsv2hex((180.0,s,v))},
            stop:0.67 #{self.hsv2hex((241.2,s,v))},
            stop:0.83 #{self.hsv2hex((298.8,s,v))},
            stop:1 #{self.hsv2hex((360.0,s,v))});
        }}"""
        self.ids.hue.setStyleSheet(gradient)

    def _updateSaturationSlider(self, hsv):
        h,s,v = hsv
        gradient = f"""#saturation QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((h,0,v))},
            stop:1 #{self.hsv2hex((h,100,v))});
        }}"""
        self.ids.saturation.setStyleSheet(gradient)

    def _updateBrightnessSlider(self, hsv):
        h,s,v = hsv
        gradient = f"""#brightness QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 #{self.hsv2hex((h,s,0))},
            stop:1 #{self.hsv2hex((h,s,100))});
        }}"""
        self.ids.brightness.setStyleSheet(gradient)

    def _updateOpacitySlider(self, rgb=None, hsv=None):
        r,g,b = rgb if rgb else self.hsv2rgb(*hsv)
        gradient = f"""#opacity QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.opacity.setStyleSheet(gradient)
