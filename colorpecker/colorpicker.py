# -*- coding: utf-8 -*-
from colorpecker import log, utils  # noqa
from colorpecker.color import RgbColor, RGB, HSV
from os.path import dirname, normpath
from PySide6 import QtCore, QtGui
from qtemplate import QTemplateWidget


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/resources/colorpicker.tmpl')

    def __init__(self, color=None):
        super(ColorPicker, self).__init__()
        self.mode = HSV                 # Current slider mode
        self.color = None               # Current color in self.mode format
        self._shiftColor = None         # color value when shift pressed
        self._updating = False          # Ignore other slider changes
        self.setColor(color)            # Set the specfied color

    def __str__(self):
        return f'{self.mode}{self.color}'

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()

    def setColor(self, color):
        """ Try really hard to read the text format and set the color. """
        try:
            if isinstance(color, str):
                mode, color = utils.text2color(color)
                color = utils.convert(color, mode, self.mode)
            self.color = color or RgbColor(1,0,0)
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
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftColor = self.color
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """ When shift is released, no longer store the color. """
        if event.key() == QtCore.Qt.Key_Shift:
            self._shiftColor = None
        super().keyReleaseEvent(event)

    def _modeChanged(self, index):
        """ Called when the color mode has changed. """
        if not self.loading:
            self.mode = self.ids.mode.itemText(index).lower()
            self.ids.rgb.setVisible(False)
            self.ids.hsv.setVisible(False)
            self.ids[self.mode].setVisible(True)
            self._updateSliderValues()
            self._updateDisplay()

    def _rgbChanged(self, value):
        """ Called when an rgb slider value has changed. """
        if not self._updating:
            r = self.ids.r.value / float(self.ids.r.max)
            g = self.ids.g.value / float(self.ids.g.max)
            b = self.ids.b.value / float(self.ids.b.max)
            a = self.ids.a.value / float(self.ids.a.max)
            # If shift pressed, change the brightness
            if self._shiftColor:
                slider = self.sender()
                id = slider.objectName().lower()
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

    def _hsvChanged(self, value):
        """ Called when an hsv slider value has changed. """
        if not self._updating:
            h = self.ids.h.value / float(self.ids.h.max)
            s = self.ids.s.value / float(self.ids.s.max)
            v = self.ids.v.value / float(self.ids.v.max)
            a = self.ids.a.value / float(self.ids.a.max)
            self.color = RgbColor.fromHsv(h,s,v,a)
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
            log.debug(f'_updateSliderValues({self.color})')
            self._updating = True
            if self.mode == RGB:
                self.ids.r.setValue(round(self.color.r*255))
                self.ids.g.setValue(round(self.color.g*255))
                self.ids.b.setValue(round(self.color.b*255))
            if self.mode == HSV:
                self.ids.h.setValue(round(self.color.h*360))
                self.ids.s.setValue(round(self.color.s*255))
                self.ids.v.setValue(round(self.color.v*255))
            self.ids.a.setValue(round(self.color.a*100))
            self._updating = False

    def _updateDisplay(self):
        """ Update the swatch, text display, and slider background gradients. """
        if not self._updating:
            log.debug(f'_updateDisplay({self.color})')
            self._updateSwatchDisplay()
            self._updateTextDisplay()
            self._updateOpacityDisplay()
            if self.mode == RGB:
                self._updateSliderDisplay('r', mode=RGB)
                self._updateSliderDisplay('g', mode=RGB)
                self._updateSliderDisplay('b', mode=RGB)
            if self.mode == HSV:
                self._updateHueDisplay()
                self._updateSliderDisplay('s', mode=HSV)
                self._updateSliderDisplay('v', mode=HSV)

    def _updateSwatchDisplay(self):
        """ Update the swatch display. """
        r,g,b = (x*255 for x in self.color.rgb)
        style = f'background-color: rgba({r},{g},{b},{self.color.a});'
        self.ids.swatch.setStyleSheet(style)
    
    def _updateTextDisplay(self):
        """ Update the text color display. """
        match self.color.a:
            case 1: self.ids.hex.setText(self.color.hex)
            case _: self.ids.hex.setText(self.color.hexa)
    
    def _updateSliderDisplay(self, id, mode=RGB):
        """ Update the slider id given current rgba or hsva selection. """
        gradient = f"""#{id} QSlider {{
            background-color: qlineargradient(x1:0, x2:1,
            stop:0 {self.color.swap(id, 0).hex},
            stop:1 {self.color.swap(id, 1).hex});
        }}"""
        self.ids[id].setStyleSheet(gradient)

    def _updateHueDisplay(self):
        """ Update the hue background gradient. """
        gradient = f"""#h QSlider {{
          background-color: qlineargradient(x1:0, x2:1,
            stop:0 {self.color.swap('h',0).hex},
            stop:0.17 {self.color.swap('h',0.166).hex},
            stop:0.33 {self.color.swap('h',0.333).hex},
            stop:0.5 {self.color.swap('h',0.5).hex},
            stop:0.67 {self.color.swap('h',0.666).hex},
            stop:0.83 {self.color.swap('h',0.833).hex},
            stop:1 {self.color.swap('h',1).hex});
        }}"""
        self.ids.h.setStyleSheet(gradient)
    
    def _updateOpacityDisplay(self):
        """ Update the opacity background gradient. """
        r,g,b = (x*255 for x in self.color.rgb)
        gradient = f"""#a QSlider {{
        background-color: qlineargradient(x1:0, x2:1,
            stop:0 rgba({r},{g},{b},0),
            stop:1 rgba({r},{g},{b},1));
        }}"""
        self.ids.a.setStyleSheet(gradient)
