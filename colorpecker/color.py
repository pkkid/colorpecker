# -*- coding: utf-8 -*-
import colorsys

RGB = 'rgb'
HSL = 'hsl'
HSV = 'hsv'
CMYK = 'cmyk'


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
        c = (1-self.r-k)/(1-float(k))
        m = (1-self.g-k)/(1-float(k))
        y = (1-self.b-k)/(1-float(k))
        return c,m,y,k

    @property
    def hsl(self):
        h,l,s = colorsys.rgb_to_hls(*self.rgb)
        return h,s,l

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


if __name__ == '__main__':
    cmyk = (0.2,0.3,0.4,0.2)
    color = RgbColor.fromCmyk(*cmyk)
    print(list(cmyk))
    print([round(x*255) for x in color.rgb])
    print([x for x in color.cmyk])
