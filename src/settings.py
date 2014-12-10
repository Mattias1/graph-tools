from . import colors
import tkinter.font
import math


class Settings():
    """The settings class"""

    def __init__(self):
        self.pos = Pos(50, 0)
        self.size = Size(1050, 700)
        self.offset = Pos(40, 20)
        self.font = ('Consolas', 10)
        self.drawsmall = False
        self.drawtext = True
        self.vertexradiussmall = 4      #px
        self.vertexradiusbig = 20       #px
        self.selectradius = 30          #px
        self.bagfactor = 3
        self.scrollbars = 'none'
        self.fps_inv = 1/30             # seconds per frame
        self.colors = colors.Colors()
        self.calcFontWidths()

    def calcFontWidths(self):
        fonts = [tkinter.font.Font(family=fam, size=pt) for fam, pt in [self.font]]
        self.fontsize = Size(fonts[0].measure('a'), fonts[0].metrics("linespace"))


class Pos():
    """A position class just to make things a bit easier."""
    def __init__(self, x, y=None):
        if y == None:
            self.x, self.y = x[0], x[1]
        else:
            self.x, self.y = x, y

    @property
    def t(self):
        return (self.x, self.y)

    def __getitem__(self, i):
        if i==0:
            return self.x
        return self.y

    def __add__(self, other):
        return Pos(self.x + other[0], self.y + other[1])
    def __radd__(self, other):
        return other + self
    def __sub__(self, other):
        return self + (-other[0], -other[1])

    def __mul__(self, constant):
        return Size(constant * self.x, constant * self.y)
    def __rmul__(self, constant):
        return self * constant

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other[0] and self.y == other[1]
    def __neq__(self, other):
        return not self == other

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def distanceTo(self, other):
        return math.sqrt(self.distanceSqTo(other))
    def distanceSqTo(self, other):
        diff = self - other
        return diff.x * diff.x + diff.y * diff.y

class Size():
    """A size class just to make things a bit easier."""
    def __init__(self, w, h=None):
        if h == None:
            self.w, self.h = w[0], w[1]
        else:
            self.w, self.h = w, h

    @property
    def t(self):
        return (self.w, self.h)

    def __getitem__(self, i):
        if i==0:
            return self.w
        return self.h

    def __add__(self, other):
        return Size(self.w + other[0], self.h + other[1])
    def __radd__(self, other):
        return other + self
    def __sub__(self, other):
        return self + (-other[0], -other[1])

    def __mul__(self, constant):
        return Size(constant * self.w, constant * self.h)
    def __rmul__(self, constant):
        return self * constant

    def __eq__(self, other):
        if other is None:
            return False
        return self.w == other[0] and self.h == other[1]
    def __neq__(self, other):
        return not a == other

    def __str__(self):
        return '{}x{}'.format(self.w, self.h)

