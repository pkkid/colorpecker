# -*- coding: utf-8 -*-
import colorsys

RGB = 'rgb'
HSV = 'hsv'


class RgbColor:
    """ RGB color object. Externally the rgba are used on a 0-255 scale by
        default. Howeever, they are internally stored on a 0-1 scale.
    """
    def __init__(self, r,g,b,a=1):
        self.r = round(r, 3)  # 0-1
        self.g = round(g, 3)  # 0-1
        self.b = round(b, 3)  # 0-1
        self.a = round(a, 3)  # 0-1
    
    hex = property(lambda self: '#'+''.join(f'{int(x*255):02x}' for x in self.rgb))
    hexa = property(lambda self: '#'+''.join(f'{int(x*255):02x}' for x in self.rgba))
    hsv = property(lambda self: colorsys.rgb_to_hsv(*self.rgb))
    hsva = property(lambda self: colorsys.rgb_to_hsv(*self.rgb) + (self.a,))
    rgb = property(lambda self: (self.r, self.g, self.b))
    rgba = property(lambda self: (self.r, self.g, self.b, self.a))
    h = property(lambda self: self.hsv[0])
    s = property(lambda self: self.hsv[1])
    v = property(lambda self: self.hsv[2])

    def __str__(self):
        return f'rgba{self.rgba}'
            
    def swap(self, id, value):
        """ Returns a copy of the current color with the id value swapped. """
        if id in 'rgba': mode = 'rgba'
        if id in 'hsv': mode = 'hsva'
        i = mode.index(id)
        xcolor = list(getattr(self, mode))
        xcolor[i] = value
        funcname = f'from{mode.title()[:-1]}'
        return getattr(RgbColor, funcname)(*xcolor)

    def multiply(self, pct=1):
        r = round(self.r * pct, 3)
        g = round(self.g * pct, 3)
        b = round(self.b * pct, 3)
        return RgbColor(r,g,b,self.a)

    @classmethod
    def fromRgb(cls, r,g,b,a=1):
        return cls(r,g,b,a)

    @classmethod
    def fromHsv(cls, h,s,v,a=1):
        return cls(*colorsys.hsv_to_rgb(h,s,v)+(a,))


if __name__ == '__main__':
    assert RgbColor.fromHsv(120/360.0,1,1).hex == '#00ff00'
