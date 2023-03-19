# -*- coding: utf-8 -*-
import colorsys
import sys
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication


def centerWindow(qobj):
    """ Move the specified widget to the center of the screen. """
    geometry = qobj.frameGeometry()
    screen = QApplication.screenAt(QtGui.QCursor.pos())
    centerpos = screen.geometry().center()
    geometry.moveCenter(centerpos)
    qobj.move(geometry.topLeft())


def convert(color, modeFrom, modeTo):
    """ Return the correct conversion function for the specified modes. """
    modeFrom, modeTo = modeFrom.lower(), modeTo.lower()
    modeFrom += 'a' if not modeFrom.endswith('a') else ''
    modeTo += 'a' if not modeTo.endswith('a') else ''
    if modeFrom == modeTo: return color
    funcname = f'{modeFrom}2{modeTo}'
    return getattr(sys.modules[__name__], funcname)(color)


def hexa2rgba(hexa):
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


def hsva2hexa(hsva):
    """ Convert hsva to hexa. """
    return rgba2hexa(hsva2rgba(hsva))


def hsva2rgba(hsva):
    """ Convert hsva to rgba. """
    h,s,v,a = hsva
    r,g,b = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
    r,g,b = (round(x*255,3) for x in (r,g,b))
    return (r,g,b,a)


def rgba2hexa(rgba):
    """ Convert rgba to hsva. """
    r,g,b,a = (int(x) for x in rgba)
    a = int(round(a * 255))
    return f'#{r:02x}{g:02x}{b:02x}{b:02x}'.upper()


def rgba2hsva(rgba):
    """ Convert rgba to hsva. """
    r,g,b,a = rgba
    h,s,v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    h,s,v = (round(h*360,3), round(s*100,3), round(v*100,3))
    return (h,s,v,a)
