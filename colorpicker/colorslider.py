# -*- coding: utf-8 -*-
from colorpicker import log, utils  # noqa
from qtemplate import QTemplateWidget
from PySide6.QtCore import Signal


class ColorSlider(QTemplateWidget):
    TMPLSTR = """
      <QWidget class='colorslider' layout='QHBoxLayout()' padding='0' spacing='15'>
        <QWidget id='sliderbg' layout='QHBoxLayout()' padding='0'>
          <QSlider id='slider' args='(Qt.Horizontal)'>
            <Connect valueChanged='_valueChanged'/>
          </QSlider>
        </QWidget>
        <QSpinBox id='spinbox' fixedWidth='60'>
          <Connect valueChanged='_valueChanged'/>
        </QSpinBox>
      </QWidget>
    """
    valueChanged = Signal(int)

    def __init__(self, *args, **kwargs):
        super(ColorSlider, self).__init__(*args, **kwargs)
        self.value = None
    
    def setRange(self, minValue, maxValue):
        self.ids.slider.setMinimum(minValue)
        self.ids.slider.setMaximum(maxValue)
        self.ids.spinbox.setRange(minValue, maxValue)
        if self.value is None: self.setValue(minValue)
        if self.value > maxValue: self.setValue(maxValue)
        if self.value < minValue: self.setValue(minValue)

    def setValue(self, value):
        self.ids.slider.setValue(value)
        self.ids.spinbox.setValue(value)
        self.value = value
    
    def _valueChanged(self, value):
        if value != self.value:
            self.value = value
            self.setValue(value)
            self.valueChanged.emit(value)
