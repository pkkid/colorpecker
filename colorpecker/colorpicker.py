# -*- coding: utf-8 -*-
from colorpecker import log, utils  # noqa
from colorpecker.color import RgbColor
from colorpecker.color import RGB, HSL, HSV, CMYK
from colorpecker.magnifier import Magnifier
from os.path import dirname, normpath
from PySide6 import QtCore, QtGui
from qtemplate import QTemplateWidget

COLORFORMATS = [
    lambda c: (c.hex.upper() if c.a == 1 else c.hexa.upper()),
    lambda c: (f'rgb({c.r}, {c.g}, {c.b})' if c.a == 1 else
               f'rgba({c.r}, {c.g}, {c.b}, {c.a})'),
    lambda c: (f'rgb({round(c.r*100)}%, {round(c.g*100)}%, {round(c.b*100)}%)' if c.a == 1 else
               f'rgba({round(c.r*100)}%, {round(c.g*100)}%, {round(c.b*100)}%, {c.a})'),
    lambda c: (f'rgb({round(c.r*255)}, {round(c.g*255)}, {round(c.b*255)})' if c.a == 1 else
               f'rgba({round(c.r*255)}, {round(c.g*255)}, {round(c.b*255)}, {c.a})'),
    lambda c: (f'hsl({round(c.h*360)}, {round(c.s*100)}%, {round(c.l*100)}%)' if c.a == 1 else
               f'hsla({round(c.h*360)}, {round(c.s*100)}%, {round(c.l*100)}%, {c.a})'),
    lambda c: (f'hsv({round(c.h*360)}, {round(c.s*100)}%, {round(c.v*100)}%)' if c.a == 1 else
               f'hsva({round(c.h*360)}, {round(c.s*100)}%, {round(c.v*100)}%, {c.a})'),
]


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/resources/colorpicker.tmpl')

    def __init__(self, color=None):
        super(ColorPicker, self).__init__()
        self.mode = RGB                 # Current slider mode
        self.color = RgbColor(0,0,0)    # Current color in self.mode format
        self._magnifier = None          # Magnifier window
        self._shiftColor = None         # color value when shift pressed
        self._eyedropColor = None       # color value when eyedrop opened
        self._updating = False          # Ignore other slider changes
        self._initTextMenu()            # Init text display choices
        self.setColor(color)            # Set the specfied color

    def __str__(self):
        return f'{self.mode}{self.color}'
    
    def _initTextMenu(self):
        """ Init the text display menu. """
        parent = self.ids.text
        # Allow custom menu and remove all default actions
        parent.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.textmenu = parent.createStandardContextMenu()
        self.textmenu.clear()
        # Build the new actions
        actions = []
        for i, cformat in enumerate(COLORFORMATS):
            actions.append(QtGui.QAction(cformat(self.color), parent))
            self.textmenu.addAction(actions[-1])
        # Show the custom menu when requested
        showmenu = lambda pos: self.textmenu.exec_(parent.mapToGlobal(pos))
        parent.customContextMenuRequested.connect(showmenu)

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setColor(self, color):
        """ Try really hard to read the text format and set the color. """
        try:
            if isinstance(color, str):
                color = RgbColor.fromText(color)
            if isinstance(color, (tuple, list)):
                color = RgbColor(*color)
            self.color = color
            self._updateSliderValues()
            self._updateDisplay()
        except Exception:
            raise Exception(f'Unable to parse color {color}')
    
    def keyPressEvent(self, event):
        """ When shift is pressed, we save the color to help with calculating
            a full brightness color change. When ctrl+v is pressed, we read the
            clipboard and attempt to load the specified color from text.
        """
        if event.matches(QtGui.QKeySequence.Paste):
            clipboard = QtGui.QClipboard()
            mimedata = clipboard.mimeData()
            if mimedata.hasText():
                self.setColor(mimedata.text())
        match event.key():
            case QtCore.Qt.Key_Shift:
                self._shiftColor = self.color
            case QtCore.Qt.Key_Escape:
                self.setFocus()
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """ When shift is released, no longer store the color. """
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftColor = None
        super().keyReleaseEvent(event)

    def _eyedropClicked(self):
        """ Show the eyedropper manginfier. """
        if not self._magnifier:
            self._magnifier = Magnifier()
            self._magnifier.colorChanged.connect(self._eyedropColorChanged)
            self._magnifier.cancelled.connect(self._eyedropCancelled)
        self._eyedropColor = self.color
        self._magnifier.show()
    
    def _eyedropColorChanged(self, qcolor):
        rgb = tuple(round(x/255.0,3) for x in qcolor.getRgb())
        self.color = RgbColor(*rgb)
        self._updateSliderValues()
        self._updateDisplay()
    
    def _eyedropCancelled(self):
        """ Called when the eyedrop color selection was cancelled. """
        self.color = self._eyedropColor
        self._updateSliderValues()
        self._updateDisplay()

    def _textEditingFinished(self):
        self.setColor(self.ids.text.text())

    def _modeChanged(self, index):
        """ Called when the color mode has changed. """
        if not self.loading:
            self.mode = self.ids.mode.itemText(index).lower()
            self.ids.rgb.setVisible(False)
            self.ids.hsl.setVisible(False)
            self.ids.hsv.setVisible(False)
            self.ids.cmyk.setVisible(False)
            self.ids[self.mode].setVisible(True)
            self.updateGeometry()
            self.adjustSize()
            self._updateSliderValues()
            self._updateDisplay()

    def _rgbChanged(self, value):
        """ Called when an rgb slider value has changed. """
        if not self._updating:
            r = self.ids.rgb_r.value / float(self.ids.rgb_r.max)
            g = self.ids.rgb_g.value / float(self.ids.rgb_g.max)
            b = self.ids.rgb_b.value / float(self.ids.rgb_b.max)
            a = self.ids.a.value / float(self.ids.a.max)
            # If shift pressed, change the brightness
            if self._shiftColor:
                slider = self.sender()
                id = slider.objectName().lower()[-1]
                value = round(value / float(slider.max), 3)
                svalue = getattr(self._shiftColor, id)
                if svalue > 0:
                    pct = round(1-((svalue-value) / float(svalue)), 3)
                    r,g,b = [min(max(sc*pct,0),1) for sc in self._shiftColor.rgb]
            # Update the ui
            self.color = RgbColor.fromRgb(r,g,b,a)
            if self._shiftColor:
                self._updateSliderValues()
            self._updateDisplay()

    def _hslChanged(self, value):
        """ Called when an hsl slider value has changed. """
        if not self._updating:
            h = self.ids.hsl_h.value / float(self.ids.hsl_h.max)
            s = self.ids.hsl_s.value / float(self.ids.hsl_s.max)
            l = self.ids.hsl_l.value / float(self.ids.hsl_l.max)
            a = self.ids.a.value / float(self.ids.a.max)
            self.color = RgbColor.fromHsl(h,s,l,a)
            self._updateDisplay()

    def _hsvChanged(self, value):
        """ Called when an hsv slider value has changed. """
        if not self._updating:
            h = self.ids.hsv_h.value / float(self.ids.hsv_h.max)
            s = self.ids.hsv_s.value / float(self.ids.hsv_s.max)
            v = self.ids.hsv_v.value / float(self.ids.hsv_v.max)
            a = self.ids.a.value / float(self.ids.a.max)
            self.color = RgbColor.fromHsv(h,s,v,a)
            self._updateDisplay()
        
    def _cmykChanged(self, value):
        """ Called when an hsv slider value has changed. """
        if not self._updating:
            c = self.ids.cmyk_c.value / float(self.ids.cmyk_c.max)
            m = self.ids.cmyk_m.value / float(self.ids.cmyk_m.max)
            y = self.ids.cmyk_y.value / float(self.ids.cmyk_y.max)
            k = self.ids.cmyk_k.value / float(self.ids.cmyk_k.max)
            a = self.ids.a.value / float(self.ids.a.max)
            self.color = RgbColor.fromCmyk(c,m,y,k,a)
            self._updateDisplay()

    def _aChanged(self, a):
        """ Called when the opacity slider value has changed. """
        if not self._updating:
            self.color.a = self.ids.a.value / float(self.ids.a.max)
            self._updateDisplay()

    def _updateSliderValues(self):
        """ Update the slider values, only needed if we change the
            color outside of using the sliders.
        """
        if not self._updating:
            self._updating = True
            for id in self.mode:
                slider = self.ids[f'{self.mode}_{id}']
                slider.setValue(round(getattr(self.color, id)*slider.max))
            self.ids.a.setValue(round(self.color.a*100))
            self._updating = False

    def _updateDisplay(self):
        """ Update the swatch, text display, and slider background gradients. """
        if not self._updating:
            self._updateSwatchDisplay()
            self._updateTextDisplay()
            self._updateOpacityDisplay()
            if self.mode == RGB:
                self._updateSliderDisplay('r')
                self._updateSliderDisplay('g')
                self._updateSliderDisplay('b')
            if self.mode == HSL:
                self._updateHueDisplay()
                self._updateSliderDisplay('s')
                self._updateLightnessDisplay()
            if self.mode == HSV:
                self._updateHueDisplay()
                self._updateSliderDisplay('s')
                self._updateSliderDisplay('v')
            if self.mode == CMYK:
                self._updateSliderDisplay('c')
                self._updateSliderDisplay('m')
                self._updateSliderDisplay('y')
                self._updateSliderDisplay('k')

    def _updateSwatchDisplay(self):
        """ Update the swatch display. """
        r,g,b = (round(x*255) for x in self.color.rgb)
        style = f'background-color: rgba({r},{g},{b},{self.color.a});'
        self.ids.swatch.setStyleSheet(style)
    
    def _updateTextDisplay(self):
        """ Update the text color display. """
        # Update the main text display
        match self.color.a:
            case 1: self.ids.text.setText(self.color.hex.upper())
            case _: self.ids.text.setText(self.color.hexa.upper())
        # Update test menu options
        for i, action in enumerate(self.textmenu.actions()):
            action.setText(COLORFORMATS[i](self.color))
    
    def _updateSliderDisplay(self, id):
        """ Update the slider id given current rgba or hsva selection. """
        gradient = f"""#{self.mode}_{id} QSlider {{
            background-color: qlineargradient(x1:0, x2:1,
            stop:0 {self.color.swap(id, 0).hex},
            stop:1 {self.color.swap(id, 1).hex});
        }}"""
        slider = self.ids[f'{self.mode}_{id}']
        slider.setStyleSheet(gradient)

    def _updateHueDisplay(self):
        """ Update the hue background gradient. """
        gradient = f"""#{self.mode}_h QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 {self.color.swap('h',0).hex},
            stop:0.17 {self.color.swap('h',0.166).hex},
            stop:0.33 {self.color.swap('h',0.333).hex},
            stop:0.5 {self.color.swap('h',0.5).hex},
            stop:0.67 {self.color.swap('h',0.666).hex},
            stop:0.83 {self.color.swap('h',0.833).hex},
            stop:1 {self.color.swap('h',1).hex});
        }}"""
        slider = self.ids[f'{self.mode}_h']
        slider.setStyleSheet(gradient)
    
    def _updateLightnessDisplay(self):
        gradient = f"""#hsl_l QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 {self.color.swap('l',0).hex},
            stop:0.5 {self.color.swap('l',0.5).hex},
            stop:1 {self.color.swap('l',1).hex});
        }}"""
        self.ids.hsl_l.setStyleSheet(gradient)
    
    def _updateOpacityDisplay(self):
        """ Update the opacity background gradient. """
        r,g,b = (round(x*255) for x in self.color.rgb)
        gradient = f"""#a QSlider {{
        background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.a.setStyleSheet(gradient)
