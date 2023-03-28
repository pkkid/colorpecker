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
            try:
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
            except Exception:
                log.error(f'Unable to parse HEX string: {text}')
                raise
    
    @classmethod
    def fromHslText(cls, text):
        """ Creates an RgbColor from an hsl string. """
        if matches := re.findall(REGEX_HSL, text):
            try:
                log.info(f'Parsing hsl color {text}')
                h = text2num(matches[0][0], scale=360)
                s = text2num(matches[0][1], scale=100)
                l = text2num(matches[0][2], scale=100)
                a = text2num(matches[0][3], scale=1, default=1)
                return RgbColor.fromHsl(h,s,l,a)
            except Exception:
                log.error(f'Unable to parse HSL string: {text}')
                raise
    
    @classmethod
    def fromHsvText(cls, text):
        """ Creates an RgbColor from an hsv string. """
        if matches := re.findall(REGEX_HSV, text):
            try:
                log.info(f'Parsing hsv color {text}')
                h = text2num(matches[0][0], scale=360)
                s = text2num(matches[0][1], scale=100)
                v = text2num(matches[0][2], scale=100)
                a = text2num(matches[0][3], scale=1, default=1)
                return RgbColor.fromHsv(h,s,v,a)
            except Exception:
                log.error(f'Unable to parse HSV string: {text}')
                raise
    
    @classmethod
    def fromRgbText(cls, text):
        """ Creates an RgbColor from an rgb string. """
        if matches := re.findall(REGEX_RGB, text):
            try:
                log.info(f'Parsing rgb color {text}')
                rgb = text2num(matches[0][0:3])
                a = text2num(matches[0][3], scale=1, default=1)
                return RgbColor(*rgb, a=a)
            except Exception:
                log.error(f'Unable to parse RGB string: {text}')
                raise

    @classmethod
    def fromText(cls, text):
        """ Creates an RgbColor from a string. """
        # Order matters here! We are specifically checking color profiles
        # that are harder to match first, then getting more leanient in what
        # we allow as we make it futher to the end.
        funcs = (cls.fromHslText, cls.fromHsvText, cls.fromRgbText, cls.fromHex)
        for func in funcs:
            value = func(text)
            if value is not None:
                return value
        raise Exception(f'Unknown color format: {text}')


def text2num(values, scale=None, default=0):
    """ Converts a list of text strings to a list of numbers. We assume the
        same scale and suffix applies to all values in the list.
        Percent example: (100%, 59%, 9%) => (1, .59, .09)
        Degree example: 360° => 1
    """
    # Quick exit and make sure we're always dealing with a list
    if values in ('', None): return default
    if isinstance(values, str): values = (values,)
    # First pass, look for clues in any of the values
    if all(v.endswith('%') for v in values):
        values = tuple(v.replace('%','') for v in values)
        scale = 100
    if all(v.endswith('°') for v in values):
        values = tuple(v.replace('°','') for v in values)
        scale = 360
    values = tuple(float(v) for v in values)
    # Check all values are under 1
    if not scale and all(v <= 1 for v in values): scale = 1
    if not scale and any(v > 255 for v in values): scale = 360
    if not scale: scale = 255  # Could be 100, but 255 is more popular
    # Return values 0-1
    values = tuple(round(v / float(scale), 3) for v in values)
    return values[0] if len(values) == 1 else tuple(values)


if __name__ == '__main__':
    cmyk = (0.2,0.3,0.4,0.2)
    color = RgbColor.fromCmyk(*cmyk)
    print(list(cmyk))
    print([round(x*255) for x in color.rgb])
    print([x for x in color.cmyk])
