# -*- coding: utf-8 -*-
import colorsys
import re
import sys
from colorpecker import log
from PySide6 import QtGui
from PySide6.QtWidgets import QApplication

TEXT, RGB, HEX, HSV = 'text', 'rgb', 'hex', 'hsv'
START, END, DELIM = r'^\s*', r'\s*$', r' *[, ]'
R,G,B = (rf'(?: *(?:{c[0]}|{c})? *[:= ])?' for c in ('red','green','blue'))
NUM, DEG = (rf' *(\d+(?:\.\d+)? ?{c}?)' for c in '%°')
REGEX_ARGB = re.compile(rf'{START}argb\({NUM}{DELIM}{R}{NUM}{DELIM}{G}{NUM}{DELIM}{B}{NUM} *\){END}', re.I)
REGEX_RGBA = re.compile(rf'{START}rgba?\(?{R}{NUM}{DELIM}{G}{NUM}{DELIM}{B}{NUM}(?:{DELIM}{NUM})? *\)?{END}', re.I)
REGEX_HSVA = re.compile(rf'{START}hsva?\({DEG}{DELIM}{NUM}{DELIM}{NUM}(?:{DELIM}{NUM})? *\){END}', re.I)
REGEX_HEXA = re.compile(rf'{START}(?:#|0x)?([a-f\d]{1,8}){END}', re.I)


def centerWindow(qobj):
    """ Move the specified widget to the center of the screen. """
    geometry = qobj.frameGeometry()
    screen = QApplication.screenAt(QtGui.QCursor.pos())
    centerpos = screen.geometry().center()
    geometry.moveCenter(centerpos)
    qobj.move(geometry.topLeft())


def convert(color, modeFrom, modeTo):
    """ Return the correct conversion function for the specified modes. """
    if modeFrom == modeTo:
        return color
    funcname = f'{modeFrom}a2{modeTo}a'
    return getattr(sys.modules[__name__], funcname)(color)


def text2color(text):
    """ Tries to convert the text to a mode and color. Raise exception if unable. """
    if color := text2hexa(text):
        log.info(f'HEX {color}')
        return HEX, color
    if color := text2hsva(text):
        log.info(f'HSV {color}')
        return HSV, color
    if color := text2rgba(text):
        log.info(f'RGB {color}')
        return RGB, color
    raise Exception(f'Unknown color format {text}')


def text2hexa(text):
    """ Convert a text string to a proper hexa string 8 characters long. This method
        is very liberal in what it allows as a proper hex string, and will auto-fill
        any missing characters for improper hex colors 1,2,5 & 7 characters long.
    """
    if not re.match(REGEX_HEXA, text):
        return False
    # Strip the leading junk
    log.info(f'Parsing hexa value: {text}')
    hexa = text.lower()
    if hexa.startswith('#'): hexa = hexa[1:]
    if hexa.startswith('0x'): hexa = hexa[2:]
    # Clean string to be 8 characters long
    match len(hexa):
        case 1: hexa = f'#{hexa[0]*2}0000ff'
        case 2: hexa = f'#{hexa[0]*2}{hexa[1]*2}00ff'
        case 3: hexa = f'#{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}ff'
        case 4: hexa = f'#{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}{hexa[3]*2}'
        case 5: hexa = f'#{hexa}0ff'
        case 6: hexa = f'#{hexa}ff'
        case 7: hexa = f'#{hexa}f'
        case 8: hexa = f'#{hexa}'
    return hexa


def text2rgba(text):
    # Check argb and rgba regex patterns
    if matches := re.findall(REGEX_ARGB, text):
        log.info(f'Parsing argb value: {text}')
        a,r,g,b = matches[0]
        rgba = [r,g,b,a]
    if matches := re.findall(REGEX_RGBA, text):
        log.info(f'Parsing rgba value: {text}')
        rgba = matches[0]
        if len(rgba) == 3: rgba += [1]
    if not rgba:
        return False
    # Convert the individual strings to numbers. This part is super tricky because we don't
    # know if the rgb color format is going to be from 0-1, 0-100, or 0-255. Additionally,
    # we don't know if the alpha channel is from 0-1, 0-100, or 0-255. We attempt to use
    # the variables below to determine if any values are a percent, greater than 1, or
    # greater than 100.
    pct = False      # True is any rgb values use %
    gt1 = False      # True if any rgb values > 1
    gt100 = False    # True if any rgb values > 100
    for i in range(3):
        rgba[i] = rgba[i].replace(' ','')
        if '%' in rgba[i]: pct = True
        rgba[i] = float(rgba[i].rstrip('%'))
        if rgba[i] > 1: gt1 = True
        if rgba[i] > 100: gt100 = True
    rgba[3] = float(rgba[3].rstrip('%'))
    # At this point all rgba values are floats. We make a best guess at the number range
    # used for rgba values. Unfortunatly for the alpha value, we have less data to go by.
    # This application uses the color range from 0-255.
    for i in range(3):
        if gt100: pass                                           # rgb 0-255
        elif pct: rgba[i] = round((rgba[i] / 100.0) * 255, 3)    # rgb 0-100
        elif gt1: rgba[i] = round((rgba[i] / 100.0) * 255, 3)    # rgb 0-100
        else: rgba[i] = round(rgba[i] * 255, 3)                  # rgb 0-1
    # For the alpha channel we use 0-1 and we can't use the hints above.
    if rgba[3] > 100: rgba[3] = round(rgba[3] / 255.0, 3)   # alpha 0-255
    if rgba[3] > 1: rgba[3] = round(rgba[3] / 100, 3)       # alpha 0-1
    log.info(f'  result: rgba{tuple(rgba)}')
    return tuple(rgba)


def text2hsva(text):
    pass


def hexa2rgba(hexa):
    """ Converts hexa to rgba. """
    if hexa.startswith('#'): hexa = hexa[1:]
    if hexa.startswith('0x'): hexa = hexa[2:]
    if len(hexa) == 6: hexa += 'ff'
    r,g,b,a = (int(hexa[i:i+2], 16) for i in (0,2,4,6))
    a = round(a / 255.0, 3)
    return (r,g,b,a)


def hexa2hsva(hexa):
    """ Converts hexa to hsva. """
    return rgba2hsva(hexa2rgba(hexa))


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
