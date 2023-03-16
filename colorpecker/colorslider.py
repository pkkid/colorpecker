# -*- coding: utf-8 -*-
from colorpecker import log, utils  # noqa
from qtemplate import QTemplateWidget
from PySide6.QtCore import Signal


class ColorSlider(QTemplateWidget):
    TMPLSTR = """
      <QWidget class='colorslider' layout='QHBoxLayout()' padding='0' spacing='15'>
        <QWidget id='sliderbg' layout='QHBoxLayout()' padding='0'>
          <QSlider id='slider' args='(Qt.Horizontal)'>
            <Connect valueChanged='setValue'/>
          </QSlider>
        </QWidget>
        <QSpinBox id='spinbox' fixedWidth='60'>
          <Connect valueChanged='setValue'/>
        </QSpinBox>
      </QWidget>
    """
    valueChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super(ColorSlider, self).__init__(*args, **kwargs)
        self._value = None
    
    @property
    def value(self):
        return self.ids.spinbox.value()

    def setRange(self, minValue, maxValue):
        self.ids.slider.setMinimum(minValue)
        self.ids.slider.setMaximum(maxValue)
        self.ids.spinbox.setRange(minValue, maxValue)

    def setValue(self, value):
        if value != self._value:
            self._value = value
            self.ids.slider.setValue(value)
            self.ids.spinbox.setValue(value)
            self.valueChanged.emit(value)
