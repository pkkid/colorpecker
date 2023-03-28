# -*- coding: utf-8 -*-
import re
import colorsys
from colorpecker import log  # noqa

# Color modes
RGB = 'rgb'
HSL = 'hsl'
HSV = 'hsv'
CMYK = 'cmyk'

# Regex to try parsing string to colors
_DELIM = r' *[, ]'
_R,_G,_B = (rf'(?: *(?:{c[0]}|{c})? *[:= ])?' for c in ('red','green','blue'))
_NUM,_DEG = (rf' *((?:\.\d+|\d+\.?\d*){c}?)' for c in '%°')
REGEX_ARGB = re.compile(rf'argb\({_NUM}{_DELIM}{_R}{_NUM}{_DELIM}{_G}{_NUM}{_DELIM}{_B}{_NUM} *\)', re.I)
REGEX_RGB = re.compile(rf'rgba?\(?{_R}{_NUM}{_DELIM}{_G}{_NUM}{_DELIM}{_B}{_NUM}(?:{_DELIM}{_NUM})? *\)?', re.I)
REGEX_HSL = re.compile(rf'hsla?\({_DEG}{_DELIM}{_NUM}{_DELIM}{_NUM}(?:{_DELIM}{_NUM})? *\)', re.I)
REGEX_HSV = re.compile(rf'hsva?\({_DEG}{_DELIM}{_NUM}{_DELIM}{_NUM}(?:{_DELIM}{_NUM})? *\)', re.I)
REGEX_HEX = re.compile(r'((?:\#|0x)[a-f\d]{3,8})', re.I)

# Color Formats
COLORFORMATS = [{
    'opaque': lambda color: color.hex.upper(),
    'alpha': lambda color: color.hexa.upper(),
},{
    'opaque': lambda color: f'rgb({color.r}, {color.g}, {color.b})',
    'alpha': lambda color: f'rgba({color.r}, {color.g}, {color.b}, {color.a})',
},{
    'opaque': lambda color: f'rgb({round(color.r*100)}%, {round(color.g*100)}%, {round(color.b*100)}%)',
    'alpha': lambda color: f'rgba({round(color.r*100)}%, {round(color.g*100)}%, {round(color.b*100)}%, {color.a})',
},{
    'opaque': lambda color: f'rgb({round(color.r*255)}, {round(color.g*255)}, {round(color.b*255)})',
    'alpha': lambda color: f'rgba({round(color.r*255)}, {round(color.g*255)}, {round(color.b*255)}, {color.a})',
},{
    'opaque': lambda color: f'hsl({round(color.h*360)}, {round(color.s*100)}%, {round(color.l*100)}%)',
    'alpha': lambda color: f'hsla({round(color.h*360)}, {round(color.s*100)}%, {round(color.l*100)}%, {color.a})',
},{
    'opaque': lambda color: f'hsv({round(color.h*360)}, {round(color.s*100)}%, {round(color.v*100)}%)',
    'alpha': lambda color: f'hsva({round(color.h*360)}, {round(color.s*100)}%, {round(color.v*100)}%, {color.a})',
}]


class RgbColor:
    """ RGB color object. Externally the rgba are used on a 0-255 scale by
        default. Howeever, they are internally stored on a 0-1 scale.
    """
    def __init__(self, r,g,b,a=1):
        self.r = round(r, 3)  # 0-1
        self.g = round(g, 3)  # 0-1
        self.b = round(b, 3)  # 0-1
        self.a = round(a, 3)  # 0-1
    
    cmyka = property(lambda self: self.cmyk + (self.a,))
    hex = property(lambda self: '#'+''.join(f'{int(x*255):02x}' for x in self.rgb))
    hexa = property(lambda self: '#'+''.join(f'{int(x*255):02x}' for x in self.rgba))
    hsla = property(lambda self: self.hsl + (self.a,))
    hsv = property(lambda self: colorsys.rgb_to_hsv(*self.rgb))
    hsva = property(lambda self: self.hsv + (self.a,))
    rgb = property(lambda self: (self.r, self.g, self.b))
    rgba = property(lambda self: (self.r, self.g, self.b, self.a))

    h = property(lambda self: self.hsl[0])
    s = property(lambda self: self.hsl[1])
    l = property(lambda self: self.hsl[2])
    v = property(lambda self: self.hsv[2])
    c = property(lambda self: self.cmyk[0])
    m = property(lambda self: self.cmyk[1])
    y = property(lambda self: self.cmyk[2])
    k = property(lambda self: self.cmyk[3])

    def __str__(self):
        return f'rgba{self.rgba}'

    @property
    def cmyk(self):
        k = 1-max(self.rgb)
        if k == 1: return 0,0,0,1
        c = (1-self.r-k)/(1-float(k))
        m = (1-self.g-k)/(1-float(k))
        y = (1-self.b-k)/(1-float(k))
        return c,m,y,k

    @property
    def hsl(self):
        h,l,s = colorsys.rgb_to_hls(*self.rgb)
        return h,s,l

    def format(self, cformat):
        """ Return a color formatted with the specified color format. """
        return cformat['opaque'](self) if self.a == 1 else cformat['alpha'](self)

    def swap(self, id, value):
        """ Returns a copy of the current color with id value swapped. """
        if id in 'rgba': mode = 'rgba'
        elif id in 'hsv': mode = 'hsva'
        elif id in 'hsl': mode = 'hsla'
        elif id in 'cmyk': mode = 'cmyka'
        i = mode.index(id)
        xcolor = list(getattr(self, mode))
        xcolor[i] = value
        funcname = f'from{mode.title()[:-1]}'
        return getattr(RgbColor, funcname)(*xcolor)

    @classmethod
    def fromCmyk(cls, c,m,y,k,a=1):
        """ Creates an RgbColor from cmyk values. """
        r = round((1-c)*(1-k), 3)
        g = round((1-m)*(1-k), 3)
        b = round((1-y)*(1-k), 3)
        return cls(r,g,b,a)
            
    @classmethod
    def fromHsl(cls, h,s,l,a=1):
        """ Creates an RgbColor from hsl values. Note: The swapped s & l
            arguments, colorsys did things backwards from normal.
        """
        return cls(*colorsys.hls_to_rgb(h,l,s)+(a,))

    @classmethod
    def fromHsv(cls, h,s,v,a=1):
        """ Creates an RgbColor from hsv values. """
        return cls(*colorsys.hsv_to_rgb(h,s,v)+(a,))
    
    @classmethod
    def fromRgb(cls, r,g,b,a=1):
        """ Convenience function to create an RgbColor. """
        return cls(r,g,b,a)
    
    @classmethod
    def fromHex(cls, text):
        """ Create an RgbColor from a hex string. """
        if matches := re.findall(REGEX_HEX, text):
            hexa = matches[0].lower()
            log.info(f'Parsing hex color {hexa}')
            if hexa.startswith('#'): hexa = hexa[1:]
            if hexa.startswith('0x'): hexa = hexa[2:]
            match len(hexa):
                case 3: hexa = f'{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}ff'
                case 4: hexa = f'{hexa[0]*2}{hexa[1]*2}{hexa[2]*2}{hexa[3]*2}'
                case 5: hexa = f'{hexa}0ff'
                case 6: hexa = f'{hexa}ff'
                case 7: hexa = f'{hexa}f'
                case 8: hexa = f'{hexa}'
            rgba = (int(hexa[i:i+2], 16) for i in (0,2,4,6))
            return cls(*(round(x/255.0,3) for x in rgba))
        raise Exception(f'Invalid hex string: {text}')
    
    @classmethod
    def fromHslText(cls, text):
        """ Creates an RgbColor from an hsl string. """
        if matches := re.findall(REGEX_HSL, text):
            log.info(f'Parsing hsl color {text}')
            h = text2num(matches[0][0], scale=360, default=0)
            s = text2num(matches[0][1], scale=100, default=0)
            l = text2num(matches[0][2], scale=100, default=0)
            a = text2num(matches[0][3], scale=1, default=1)
            return RgbColor.fromHsl(h,s,l,a)
        raise Exception(f'Invalid hsl string: {text}')
    
    @classmethod
    def fromHsvText(cls, text):
        """ Creates an RgbColor from an hsv string. """
        if matches := re.findall(REGEX_HSV, text):
            log.info(f'Parsing hsv color {text}')
            h = text2num(matches[0][0], scale=360, default=0)
            s = text2num(matches[0][1], scale=100, default=0)
            v = text2num(matches[0][2], scale=100, default=0)
            a = text2num(matches[0][3], scale=1, default=1)
            return RgbColor.fromHsv(h,s,v,a)
        raise Exception(f'Invalid hsv string: {text}')
    
    @classmethod
    def fromRgbText(cls, text):
        """ Creates an RgbColor from an rgb string. """
        if matches := re.findall(REGEX_RGB, text):
            log.info(f'Parsing rgb color {text}')
            rgb = (text2num(x,255) for x in matches[0][0:3])
            a = text2num(matches[0][3], scale=1, default=1)
            return RgbColor(*rgb, a=a)
        raise Exception(f'Invalid rgb string: {text}')

    @classmethod
    def fromText(cls, text):
        """ Creates an RgbColor from a string. """
        # Order matters here! We are specifically checking color profiles
        # that are harder to match first, then getting more leanient in what
        # we allow as we make it futher to the end.
        funcs = (cls.fromHslText, cls.fromHsvText, cls.fromRgbText, cls.fromHex)
        for func in funcs:
            try:
                return func(text)
            except Exception:
                pass  # try the next method
        raise Exception(f'Invalid color string: {text}')


def text2num(text, scale=None, default=0):
    """ Converts a simple text string to number. For example:
        Percent examples: 100%=1; 59%=.59; 9%=0.09
        Degree examples: 360°=1; 180°=0.5; 12°=0.03
    """
    if text == '': return default
    # Check we can extract the scale from a suffix
    if text.endswith('%'): text, scale = text[:-1], 100
    if text.endswith('°'): text, scale = text[:-1], 360
    # Convert text to float guess the scale if not set
    value = float(text)
    if scale is None and value > 100: scale = 255
    elif scale is None and value > 1: scale = 100
    elif scale is None: scale = 1
    # Return value 0-1
    return round(value / float(scale), 3)


if __name__ == '__main__':
    cmyk = (0.2,0.3,0.4,0.2)
    color = RgbColor.fromCmyk(*cmyk)
    print(list(cmyk))
    print([round(x*255) for x in color.rgb])
    print([x for x in color.cmyk])
